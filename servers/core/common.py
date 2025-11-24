import os
import shutil
import subprocess
from typing import Optional, Union, List, Dict

from crawl4ai import AsyncWebCrawler
from colorama import Fore, Style

from servers.models.slidev import SlidevResult

def parse_markdown_slides(content: str) -> list:
    """
    解析markdown内容，按YAML front matter切分幻灯片
    """
    slides = []
    current_slide = []
    in_yaml = False
    
    for line in content.splitlines():
        if line.strip() == '---' and not in_yaml:
            # 开始YAML front matter
            if not current_slide:
                in_yaml = True
                current_slide.append(line)
            else:
                # 遇到新的幻灯片分隔符
                slides.append('\n'.join(current_slide))
                current_slide = [line]
                in_yaml = True
        elif line.strip() == '---' and in_yaml:
            # 结束YAML front matter
            current_slide.append(line)
            in_yaml = False
        else:
            current_slide.append(line)
    
    # 添加最后一个幻灯片
    if current_slide:
        slides.append('\n'.join(current_slide))
    
    return slides

def transform_parameters_to_frontmatter(parameters: dict):
    frontmatter = ""
    for key in parameters.keys():
        value = parameters.get(key, "")
        frontmatter += f"{key}: {value}\n"
    return frontmatter.strip()

def check_nodejs_installed() -> bool:
    return shutil.which("node") is not None


def get_node_major_version(env: Optional[Dict[str, str]] = None) -> Optional[int]:
    """获取当前 Node.js 主版本号，例如 20.x 返回 20。

    参数:
        env: 可选的环境变量，用于在指定 PATH 下解析 node 版本
    """
    try:
        result = subprocess.run(
            ["node", "-v"],
            capture_output=True,
            text=True,
            timeout=5,
            stdin=subprocess.DEVNULL,
            env=env if env is not None else os.environ.copy(),
        )
        if result.returncode != 0:
            return None
        ver = result.stdout.strip() or result.stderr.strip()
        # 版本通常形如 v20.11.1
        if ver.startswith("v"):
            ver = ver[1:]
        major = ver.split(".")[0]
        return int(major)
    except Exception:
        return None


def prepare_env_with_nvm_node20_plus() -> Optional[Dict[str, str]]:
    """
    使用 nvm 检查是否已安装任意 >=20 的 Node 版本：
    - 若存在，选择最高版本并返回包含该版本 bin 路径优先的 env；
    - 若 nvm 不存在或未安装 >=20 版本，返回 None（由上层决定是否提示安装）。
    """
    nvm_dir = os.environ.get("NVM_DIR", os.path.expanduser("~/.nvm"))
    nvm_sh = os.path.join(nvm_dir, "nvm.sh")

    if not os.path.exists(nvm_sh):
        return None

    # 列出已安装版本并解析出 >=20 的最高版本
    list_cmd = f"source '{nvm_sh}' >/dev/null 2>&1 && nvm ls --no-colors"
    try:
        proc = subprocess.run(
            ["bash", "-lc", list_cmd],
            capture_output=True,
            text=True,
            timeout=20,
            stdin=subprocess.DEVNULL,
        )
        if proc.returncode != 0:
            return None

        output = (proc.stdout or proc.stderr or "")

        # 提取所有形如 vX.Y.Z 或 X.Y.Z 的版本字符串
        import re

        versions = []
        for m in re.finditer(r"v?(\d+)\.(\d+)\.(\d+)", output):
            major, minor, patch = map(int, m.groups())
            versions.append((major, minor, patch))

        # 过滤出 >=20 的版本并选择最高版本
        versions_20_plus = [v for v in versions if v[0] >= 20]
        if not versions_20_plus:
            return None

        versions_20_plus.sort(reverse=True)
        top = versions_20_plus[0]
        version_str = f"v{top[0]}.{top[1]}.{top[2]}"

        # 定位该版本的 node 绝对路径
        which_cmd = (
            f"source '{nvm_sh}' >/dev/null 2>&1 && "
            f"nvm which {version_str}"
        )
        which_proc = subprocess.run(
            ["bash", "-lc", which_cmd],
            capture_output=True,
            text=True,
            timeout=20,
            stdin=subprocess.DEVNULL,
        )
        if which_proc.returncode != 0:
            return None
        node_path = (which_proc.stdout or which_proc.stderr).strip()
        if not node_path:
            return None
        bin_dir = os.path.dirname(node_path)

        # 构造新的 PATH，确保选定版本优先
        new_env = os.environ.copy()
        old_path = new_env.get("PATH", "")
        new_env["PATH"] = f"{bin_dir}:{old_path}" if old_path else bin_dir
        return new_env
    except Exception:
        return None

def run_command(command: Union[str, List[str]], env: Optional[Dict[str, str]] = None) -> SlidevResult:
    try:
        result = subprocess.run(
            command,
            cwd='./',
            capture_output=True,
            text=True,
            shell=isinstance(command, str),
            timeout=10,
            stdin=subprocess.DEVNULL,
            env=env if env is not None else os.environ.copy(),
        )
        if result.returncode == 0:
            return SlidevResult(success=True, message="Command executed successfully", data=result.stdout)
        else:
            return SlidevResult(success=False, message=f"Command failed: {result.stderr}")
    except Exception as e:
        return SlidevResult(success=False, message=f"Error executing command: {str(e)}")



async def websearch(url: str) -> SlidevResult:
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url)
        return SlidevResult(success=True, message="success", data=result.markdown)

def check_environment() -> SlidevResult:
    """
    检查运行环境：
    - 必须存在 Node.js 且主版本 >= 20；
      若当前未满足且 nvm 中存在 >=20 的已安装版本，优先切换至该版本；
      若 nvm 中不存在 >=20 的版本，则提示安装（不自动安装）。
    - 确认 slidev CLI 可用，不可用则尝试安装。
    """
    desired_major_min = 20
    env_override: Optional[Dict[str, str]] = None

    node_installed = check_nodejs_installed()
    node_major = get_node_major_version() if node_installed else None

    # 若未安装或版本 < 20，优先尝试从 nvm 切换到 >=20 的已安装版本
    if (not node_installed) or (node_major is None) or (node_major < desired_major_min):
        env_override = prepare_env_with_nvm_node20_plus()
        # 在切换后的环境下再检测版本
        node_major_after = get_node_major_version(env_override) if env_override else None
        if env_override and node_major_after is not None and node_major_after >= desired_major_min:
            node_major = node_major_after
        else:
            # 无法从 nvm 切换成功，给出明确提示
            if not node_installed:
                return SlidevResult(
                    success=False,
                    message="未检测到 Node.js。请安装 Node >=20（建议使用 nvm: nvm install 20）后重试。",
                )
            else:
                return SlidevResult(
                    success=False,
                    message=f"当前 Node 主版本为 {node_major or '未知'}，需要 >=20。"
                            "请使用 nvm 安装并切换到 >=20 版本（例如: nvm install 20 && nvm use 20）后重试。",
                )

    # 使用（可能的）env_override 检查 slidev
    result = run_command("slidev --version", env=env_override)
    if not result.success:
        # 这里依然使用 Node >=20 环境执行安装
        install_result = run_command("npm install -g @slidev/cli", env=env_override)
        if not install_result.success:
            return install_result
        # 安装成功后再试一次
        result = run_command("slidev --version", env=env_override)

    if result.success:
        return SlidevResult(success=True, message="环境就绪，已使用 Node >=20，slidev 可用", data=result.data)
    return SlidevResult(success=False, message="无法确认 slidev 可用性，请检查 Node >=20 与 slidev 安装。")


def print_tools(tools):
    if not tools:
        print(Fore.YELLOW + "No tools registered.")
        return
    print(Fore.CYAN + "\nRegistered Tools:")
    for tool in tools:
        print(
            f"  {Fore.GREEN}{tool.name:<30}"
            f"{Fore.MAGENTA}{tool.description.strip().split('\n')[0] or ''}"
        )


def print_prompts(prompts):
    if not prompts:
        print(Fore.YELLOW + "No prompts registered.")
        return
    print(Fore.CYAN + "\nRegistered Prompts:")
    for prompt in prompts:
        args = ", ".join(arg.name for arg in prompt.arguments) if prompt.arguments else "-"
        print(
            f"  {Fore.GREEN}{prompt.name:<40}"
            f"{Fore.BLUE}args=[{args}]  "
            f"{Fore.MAGENTA}{prompt.description or ''}"
        )


def print_resources(resources):
    if not resources:
        print(Fore.YELLOW + "No resources registered.")
        return
    print(Fore.CYAN + "\nRegistered Resources:")
    for res in resources:
        print(f"  {Fore.GREEN}{res}")


def print_resource_templates(templates):
    if not templates:
        print(Fore.YELLOW + "No resource templates registered.")
        return
    print(Fore.CYAN + "\nRegistered Resource Templates:")
    for tmpl in templates:
        print(f"  {Fore.GREEN}{tmpl}")