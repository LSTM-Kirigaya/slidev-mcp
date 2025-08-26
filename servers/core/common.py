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

def run_command(command: Union[str, List[str]]) -> SlidevResult:
    try:
        result = subprocess.run(
            command,
            cwd='./',
            capture_output=True,
            text=True,
            shell=isinstance(command, str),
            timeout=10,
            stdin=subprocess.DEVNULL
        )
        if result.returncode == 0:
            return SlidevResult(success=True, message="Command executed successfully", output=result.stdout)
        else:
            return SlidevResult(success=False, message=f"Command failed: {result.stderr}")
    except Exception as e:
        return SlidevResult(success=False, message=f"Error executing command: {str(e)}")



async def websearch(url: str) -> SlidevResult:
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url)
        return SlidevResult(success=True, message="success", output=result.markdown)

def check_environment() -> SlidevResult:
    if not check_nodejs_installed():
        return SlidevResult(success=False, message="Node.js is not installed. Please install Node.js first.")
    
    result = run_command("slidev --version")
    if not result.success:
        return run_command("npm install -g @slidev/cli")
    return SlidevResult(success=True, message="环境就绪，slidev 可以使用", output=result.output)


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