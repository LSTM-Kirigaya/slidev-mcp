from mcp.server.fastmcp import FastMCP
from typing import Optional, Union, List, Dict
from pydantic import BaseModel
import subprocess
import sys
import shutil
from pathlib import Path
import os
import datetime
from crawl4ai import AsyncWebCrawler
from usermcp import register_user_profile_mcp

from servers.core.state_manager import SlidevStateManager
from servers.models.slidev import SlidevResult, SaveOutlineParam
from utils import parse_markdown_slides

mcp = FastMCP("slidev-mcp-academic")
register_user_profile_mcp(mcp)

# 状态管理器
state = SlidevStateManager()

# ----------------- Utils -----------------

def check_nodejs_installed() -> bool:
    return shutil.which("node") is not None


def run_command(command: Union[str, List[str]]) -> SlidevResult:
    try:
        result = subprocess.run(
            command,
            cwd="./",
            capture_output=True,
            text=True,
            shell=isinstance(command, str),
            timeout=10,
            stdin=subprocess.DEVNULL,
        )
        if result.returncode == 0:
            return SlidevResult(success=True, message="Command executed successfully", output=result.stdout)
        else:
            return SlidevResult(success=False, message=f"Command failed: {result.stderr}")
    except Exception as e:
        return SlidevResult(success=False, message=f"Error executing command: {str(e)}")





# ----------------- MCP Tools & Prompts -----------------
# （这里只展示修改过的几个函数，其他 prompt 保持原样）

@mcp.tool(
    name='websearch',
    description='search the given https url and get the markdown text of the website'
)
async def websearch(url: str) -> SlidevResult:
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url)
        return SlidevResult(success=True, message="success", output=result.markdown)


@mcp.tool()
def slidev_check_environment() -> SlidevResult:
    """check if nodejs and slidev-cli is ready"""
    if not check_nodejs_installed():
        return SlidevResult(success=False, message="Node.js is not installed. Please install Node.js first.")
    
    result = run_command("slidev --version")
    if not result.success:
        return run_command("npm install -g @slidev/cli")
    return SlidevResult(success=True, message="环境就绪，slidev 可以使用", output=result.output)


@mcp.tool()
def slidev_create(name: str) -> SlidevResult:
    """create slidev project"""
    env_check = slidev_check_environment()
    if not env_check.success:
        return env_check
    
    home = state.get_project_home(name)
    
    try:
        os.makedirs(home, exist_ok=True)
        slides_path = os.path.join(home, 'slides.md')

        if os.path.exists(slides_path):
            if state.load_slidev_content(name):
                return SlidevResult(
                    success=True, 
                    message=f"项目已经存在于 {home}/slides.md 中", 
                    output=state.get_slidev_content()
                )
        else:
            with open(slides_path, 'w', encoding="utf-8") as f:
                f.write(f"""
---
theme: {state.theme}
layout: cover
transition: slide-left
---

# Your title
## sub title
""".strip())

            if not state.load_slidev_content(name):
                return SlidevResult(success=False, message="项目创建成功但加载失败", output=name)

        return SlidevResult(success=True, message=f"成功创建并加载项目 {name}", output=name)
        
    except Exception as e:
        return SlidevResult(success=False, message=f"创建失败: {str(e)}", output=name)


@mcp.tool()
def slidev_load(name: str) -> SlidevResult:
    """load exist slidev project"""
    slides_path = Path(state.get_project_home(name)) / "slides.md"
    if state.load_slidev_content(name):
        return SlidevResult(
            success=True,
            message=f"项目加载成功: {slides_path.absolute()}",
            output=state.get_slidev_content()
        )
    return SlidevResult(success=False, message=f"加载失败: {slides_path.absolute()}")


@mcp.tool()
def slidev_make_cover(title: str, subtitle: str = "", author: str = "", background: str = "", python_string_template: str = "") -> SlidevResult:
    """Create or update slidev cover page"""
    if not state.is_project_loaded():
        return SlidevResult(success=False, message="没有激活的项目")

    if python_string_template:
        template = f"""
---
theme: {state.theme}
layout: cover
transition: slide-left
coverAuthor: {author}
coverBackgroundUrl: {background}
---

{python_string_template.format(title=title, subtitle=subtitle)}
""".strip()
    else:
        template = f"""
---
theme: {state.theme}
layout: cover
transition: slide-left
coverAuthor: {author}
background: {background}
---

# {title}
## {subtitle}
""".strip()

    slides = state.get_slidev_content()
    if slides:
        slides[0] = template
    else:
        slides.append(template)
    state.set_slidev_content(slides)
    state.save_slidev_content()

    return SlidevResult(success=True, message="封面更新完成", output=0)


@mcp.tool()
def slidev_add_page(content: str, layout: str = "default", parameters: dict = {}) -> SlidevResult:
    """Add new page"""
    if not state.is_project_loaded():
        return SlidevResult(success=False, message="没有激活的项目")

    parameters['layout'] = layout
    parameters['transition'] = 'slide-left'
    frontmatter = transform_parameters_to_frontmatter(parameters)

    template = f"""
---
{frontmatter}
---

{content}
""".strip()

    slides = state.get_slidev_content()
    slides.append(template)
    state.set_slidev_content(slides)
    state.save_slidev_content()

    return SlidevResult(success=True, message="新页面添加完成", output=len(slides) - 1)


@mcp.tool()
def slidev_set_page(index: int, content: str, layout: str = "", parameters: dict = {}) -> SlidevResult:
    """Update a page"""
    if not state.is_project_loaded():
        return SlidevResult(success=False, message="没有激活的项目")

    slides = state.get_slidev_content()
    if index < 0 or index >= len(slides):
        return SlidevResult(success=False, message=f"无效的页码 {index}")

    parameters['layout'] = layout
    parameters['transition'] = 'slide-left'
    frontmatter = transform_parameters_to_frontmatter(parameters)

    template = f"""
---
{frontmatter}
---

{content}
""".strip()

    slides[index] = template
    state.set_slidev_content(slides)
    state.save_slidev_content()

    return SlidevResult(success=True, message=f"第 {index} 页已更新", output=index)


@mcp.tool()
def slidev_get_page(index: int) -> SlidevResult:
    """Get page content"""
    if not state.is_project_loaded():
        return SlidevResult(success=False, message="没有激活的项目")

    slides = state.get_slidev_content()
    if index < 0 or index >= len(slides):
        return SlidevResult(success=False, message=f"无效的页码 {index}")

    return SlidevResult(success=True, message=f"第 {index} 页内容", output=slides[index])


@mcp.tool()
def slidev_save_outline(outline: SaveOutlineParam) -> SlidevResult:
    """Save outline.json"""
    if state.save_outline_content(outline):
        return SlidevResult(success=True, message="大纲保存成功")
    return SlidevResult(success=False, message="保存失败，没有激活的项目")


@mcp.tool()
def slidev_export_project(path: str):
    return state.active_project
