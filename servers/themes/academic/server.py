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


def transform_parameters_to_frontmatter(parameters: dict):
    frontmatter = ""
    for key in parameters.keys():
        value = parameters.get(key, "")
        frontmatter += f"{key}: {value}\n"
    return frontmatter.strip()


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
    """
    create slidev, you need to ask user to get title and author to continue the task.
    you don't know title and author at beginning.
    `name`: name of the project
    """
    global ACTIVE_SLIDEV_PROJECT, SLIDEV_CONTENT

    # clear global var
    ACTIVE_SLIDEV_PROJECT = None
    SLIDEV_CONTENT = []
    
    env_check = slidev_check_environment()
    if not env_check.success:
        return env_check
    
    home = get_project_home(name)
    
    try:
        # 创建目标文件夹
        os.makedirs(home, exist_ok=True)
        
        # 在文件夹内创建slides.md文件
        slides_path = os.path.join(home, 'slides.md')

        # 如果已经存在 slides.md，则读入内容，初始化
        if os.path.exists(slides_path):
            load_slidev_content(name)
            return SlidevResult(success=True, message=f"项目已经存在于 {home}/slides.md 中", output=SLIDEV_CONTENT)
        else:
            SLIDEV_CONTENT = []

        with open(slides_path, 'w') as f:
            f.write(f"""
---
theme: {ACADEMIC_THEME}
layout: cover
transition: slide-left
---

# Your title
## sub title

""".strip())
        
        # 尝试加载内容
        if not load_slidev_content(name):
            return SlidevResult(success=False, message="successfully create project but fail to load file", output=name)
            
        return SlidevResult(success=True, message=f"successfully load slidev project {name}", output=name)
        
    except OSError as e:
        return SlidevResult(success=False, message=f"fail to create file: {str(e)}", output=name)
    except IOError as e:
        return SlidevResult(success=False, message=f"fail to create file: {str(e)}", output=name)
    except Exception as e:
        return SlidevResult(success=False, message=f"unknown error: {str(e)}", output=name)


@mcp.tool()
def slidev_load(name: str) -> SlidevResult:
    """load exist slidev project and get the current slidev markdown content"""
    # 兼容：传入的 name 视为项目名，而不是完整路径
    slides_path = Path(get_project_home(name)) / "slides.md"

    if load_slidev_content(name):
        return SlidevResult(success=True, message=f"Slidev project loaded from {slides_path.absolute()}", output=SLIDEV_CONTENT) 
    return SlidevResult(success=False, message=f"Failed to load Slidev project from {slides_path.absolute()}")


@mcp.tool()
def slidev_make_cover(title: str, subtitle: str = "", author: str = "", background: str = "", python_string_template: str = "") -> SlidevResult:
    """
    Create or update slidev cover.
    `python_string_template` is python string template, you can use {title}, {subtitle} to format the string.
    If user give enough information, you can use it to update cover page, otherwise you must ask the lacking information. `background` must be a valid url of image
    """
    global SLIDEV_CONTENT
    
    if not ACTIVE_SLIDEV_PROJECT:
        return SlidevResult(success=False, message="No active Slidev project. Please create or load one first.")
    
    date = datetime.datetime.now().strftime("%Y-%m-%d")

    if python_string_template:
        template = f"""
---
theme: {ACADEMIC_THEME}
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
theme: {ACADEMIC_THEME}
layout: cover
transition: slide-left
coverAuthor: {author}
background: {background}
---

# {title}
## {subtitle}
""".strip()

    # 更新或添加封面页
    SLIDEV_CONTENT[0] = template
    
    save_slidev_content()
    return SlidevResult(success=True, message="Cover page updated", output=0)


@mcp.tool()
def slidev_add_page(content: str, layout: str = "default", parameters: dict = {}) -> SlidevResult:
    """
    Add new page.
    - `content` is markdown format text to describe page content.
    - `layout`: layout of the page
    - `parameters`: frontmatter parameters of the page
    """
    global SLIDEV_CONTENT
    
    if not ACTIVE_SLIDEV_PROJECT:
        return SlidevResult(success=False, message="No active Slidev project. Please create or load one first.")
    
    parameters['layout'] = layout
    parameters['transition'] = 'slide-left'
    frontmatter_string = transform_parameters_to_frontmatter(parameters)

    template = f"""
---
{frontmatter_string}
---

{content}

""".strip()

    SLIDEV_CONTENT.append(template)
    page_index = len(SLIDEV_CONTENT) - 1
    save_slidev_content()
    
    return SlidevResult(success=True, message=f"Page added at index {page_index}", output=page_index)


@mcp.tool()
def slidev_set_page(index: int, content: str, layout: str = "", parameters: dict = {}) -> SlidevResult:
    """
    `index`: the index of the page to set. 0 is cover, so you should use index in [1, {len(SLIDEV_CONTENT) - 1}]
    `content`: the markdown content to set.
    - You can use ```code ```, latex or mermaid to represent more complex idea or concept. 
    - Too long or short content is forbidden.
    `layout`: the layout of the page.
    `parameters`: frontmatter parameters.
    """
    global SLIDEV_CONTENT
    
    if not ACTIVE_SLIDEV_PROJECT:
        return SlidevResult(success=False, message="No active Slidev project. Please create or load one first.")
    
    if index < 0 or index >= len(SLIDEV_CONTENT):
        return SlidevResult(success=False, message=f"Invalid page index: {index}")
    
    parameters['layout'] = layout
    parameters['transition'] = 'slide-left'
    frontmatter_string = transform_parameters_to_frontmatter(parameters)
    
    template = f"""
---
{frontmatter_string}
---

{content}

""".strip()
    
    SLIDEV_CONTENT[index] = template
    save_slidev_content()
    
    return SlidevResult(success=True, message=f"Page {index} updated", output=index)


@mcp.tool()
def slidev_get_page(index: int) -> SlidevResult:
    """get the content of the `index` th page"""
    if not ACTIVE_SLIDEV_PROJECT:
        return SlidevResult(success=False, message="No active Slidev project. Please create or load one first.")
    
    if index < 0 or index >= len(SLIDEV_CONTENT):
        return SlidevResult(success=False, message=f"Invalid page index: {index}")
    
    return SlidevResult(success=True, message=f"Content of page {index}", output=SLIDEV_CONTENT[index])


@mcp.tool()
def slidev_save_outline(outline: SaveOutlineParam) -> SlidevResult:
    """
    保存大纲到项目的 outline.json 文件中
    `outline`: 大纲项目列表，每个项目包含 group 和 content 字段
    """
    if save_outline_content(outline):
        return SlidevResult(success=True, message="Outline saved successfully", output=None)
    return SlidevResult(success=False, message="Failed to save outline. No active project.", output=None)

@mcp.tool()
def slidev_export_project(path: str):
    return ACTIVE_SLIDEV_PROJECT
