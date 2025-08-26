from mcp.server.fastmcp import FastMCP
from typing import Optional, Union, List, Dict
from pydantic import BaseModel
import subprocess
import sys
import shutil
from pathlib import Path
import os
from crawl4ai import AsyncWebCrawler
import datetime
from usermcp import register_user_profile_mcp
import argparse
import json

mcp = FastMCP('slidev-mcp-academic')

register_user_profile_mcp(mcp)

# 全局变量存储当前活动的Slidev项目
ACTIVE_SLIDEV_PROJECT: Optional[Dict] = None
SLIDEV_CONTENT: List[str] = []
ACADEMIC_THEME = 'academic'

"""根目录配置说明
SLIDEV_MCP_ROOT 环境变量：
    * 若设置且为绝对路径 -> 使用该绝对路径作为所有项目的根目录
    * 若未设置或不是绝对路径 -> 回退到默认相对目录 .slidev-mcp （相对于仓库根 / 运行目录）
默认行为保持向后兼容。
"""
DEFAULT_SLIDEV_MCP_ROOT = '.slidev-mcp'
_env_root = os.environ.get('SLIDEV_MCP_ROOT')
if _env_root and os.path.isabs(_env_root):
    SLIDEV_MCP_ROOT = _env_root
else:
    SLIDEV_MCP_ROOT = DEFAULT_SLIDEV_MCP_ROOT

def ensure_root_dir():
    try:
        os.makedirs(SLIDEV_MCP_ROOT, exist_ok=True)
    except Exception:
        pass
ensure_root_dir()

def get_project_home(name: str) -> str:
    """根据项目名称返回项目存储目录（相对路径）。"""
    return os.path.join(SLIDEV_MCP_ROOT, name)


class SlidevResult(BaseModel):
    success: bool
    message: str
    output: Optional[Union[str, int, List[str]]] = None


class OutlineItem(BaseModel):
    group: str
    content: str

class SaveOutlineParam(BaseModel):
    outlines: List[OutlineItem]

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


def load_slidev_content(name: str) -> bool:
    global SLIDEV_CONTENT, ACTIVE_SLIDEV_PROJECT
    home = get_project_home(name)
    
    slides_path = Path(home) / "slides.md"
    # if not slides_path.exists():
    #     return True
    
    with open(slides_path.absolute(), 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 初始化全局变量
    ACTIVE_SLIDEV_PROJECT = {
        "name": name,
        "home": home,
        "slides_path": str(slides_path)
    }
    
    slides = parse_markdown_slides(content)
    SLIDEV_CONTENT = [slide.strip() for slide in slides if slide.strip()]
    return True


def save_slidev_content() -> bool:
    global ACTIVE_SLIDEV_PROJECT, SLIDEV_CONTENT
    
    if not ACTIVE_SLIDEV_PROJECT:
        return False
    
    with open(ACTIVE_SLIDEV_PROJECT["slides_path"], 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(SLIDEV_CONTENT))
    
    return True


def save_outline_content(outline: SaveOutlineParam) -> bool:
    """
    保存大纲到 outline.json 文件
    """
    global ACTIVE_SLIDEV_PROJECT
    
    if not ACTIVE_SLIDEV_PROJECT:
        return False
    
    outline_path = os.path.join(ACTIVE_SLIDEV_PROJECT["home"], "outline.json")
        
    with open(outline_path, 'w', encoding='utf-8') as f:
        f.write(outline.model_dump_json(indent=2))

    return True


def transform_parameters_to_frontmatter(parameters: dict):
    frontmatter = ''
    for key in parameters.keys():
        value = parameters.get(key, '')
        frontmatter += f'{key}: {value}\n'
    return frontmatter.strip()


@mcp.prompt()
def slidev_generate_prompt():
    """guide the ai to use slidev"""
    return f"""
你是一个擅长使用 slidev 进行讲演生成的 agent，如果用户给你输入超链接，你需要调用 websearch 工具来获取对应的文本。对于返回的文本，如果你看到了验证码，网络异常等等代表访问失败的信息，你需要提醒用户本地网络访问受阻，请手动填入需要生成讲演的文本。
当你生成讲演的每一页时，一定要严格按照用户输入的文本内容或者你通过 websearch 获取到的文本内容来。请记住，在获取用户输入之前，你一无所知，请不要自己编造不存在的事实，扭曲文章的原本含义，或者是不经过用户允许的情况下扩充本文的内容。
请一定要尽可能使用爬取到的文章中的图片，它们往往是以 ![](https://adwadaaw.png) 的形式存在的。

如果当前页面仅仅存在一个图片，而且文字数量超过了三行，你应该使用 figure-side 作为 layout
你必须参考的资料，下面的资料你需要使用爬虫进行爬取并得到内容：
- academic 主题的 frontmatter: https://raw.githubusercontent.com/alexanderdavide/slidev-theme-academic/refs/heads/master/README.md

遇到 `:` 开头的话语，这是命令，目前的命令有如下的：
- `:sum {{url}}`: 使用 `websearch` 爬取目标网页内容并整理，如果爬取失败，你需要停下来让用户手动输入网页内容的总结。
- `:mermaid {{description}}`: 根据 description 生成符合描述的 mermaid 流程图代码，使用 ```mermaid ``` 进行包裹。

如果用户要求你生成大纲或者摘要，那么一定要调用 `slidev_save_outline` 这个函数来保存你总结好的大纲结果。

请爬取如下链接来获取 academic 基本的使用方法
https://raw.githubusercontent.com/alexanderdavide/slidev-theme-academic/refs/heads/master/README.md
"""

@mcp.prompt()
def slidev_generate_with_specific_outlines_prompt(title: str, content: str, outlines: str, path:str):
    """generate slidev with specific outlines"""

    return f"""
{slidev_generate_prompt()}

<OUTLINES> 标签中包裹的是整理好的大纲内容；<CONTENT> 标签中包裹的是用户输入的素材和内容,。在开始之前，你需要先使用slidev_create工具创建讲演，并以{path}作为参数传入。

<OUTLINES>
{outlines}
</OUTLINES>

<CONTENT title="{title}">
{content}
</CONTENT>

请严格根据大纲中的内容调用工具来生成 slidev，outlines中的每一个元素，都对应一页 slidev 的页，你需要使用 `slidev_add_page` 来创建它。

所有步骤结束后，你需要调用 `slidev_export_project` 来导出项目。
"""

@mcp.prompt()
def outline_generate_prompt(title: str, content: str):
    """generate outline for slidev"""
    return f"""
你是一个擅长使用 slidev 进行讲演生成的 agent，如果用户让你生成给定素材的大纲，从而在后续生成 slidev，那么你应该先根据用户输入的素材，生成一个大纲。
生成大纲后，你需要调用 `slidev_save_outline` 来保存这次的结果。

你不被允许在生成大纲时，执行任何关于 slidev 项目生成，创建，修改和添加页面的操作。

如果遇到用户给定的素材中 http 或者 https 链接，你应该积极地使用 `websearch` 来爬去网页内容。

如果遇到 `:` 开头的话语，这是命令，目前的命令有如下的：
- `:sum {{url}}`: 使用 `websearch` 爬取目标网页内容并整理，如果爬取失败，你需要停下来让用户手动输入网页内容的总结。
- `:mermaid {{description}}`: 根据 description 生成符合描述的 mermaid 流程图代码，使用 ```mermaid ``` 进行包裹。

下面是用户的输入：

<CONTENT title="{title}">
{content}
</CONTENT>

请帮我制作 slidev ppt 的大纲。
    """


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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Slidev MCP Server')
    parser.add_argument('--transport', 
                       choices=['stdio', 'streamable-http'], 
                       default='stdio',
                       help='Transport method (default: stdio)')
    
    args = parser.parse_args()
    
    mcp.run(transport=args.transport)