from mcp.server.fastmcp import FastMCP
from typing import Optional, Union, List, Dict
from pydantic import BaseModel
import subprocess
import sys
import shutil
from pathlib import Path
import os
from utils import parse_markdown_slides
from crawl4ai import AsyncWebCrawler
import datetime
from usermcp import register_user_profile_mcp
import argparse
import json

mcp = FastMCP('slidev-mcp-academic')

register_user_profile_mcp(mcp)


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
    pass

@mcp.tool()
def slidev_create(name: str) -> SlidevResult:
    """
    create slidev, you need to ask user to get title and author to continue the task.
    you don't know title and author at beginning.
    `name`: name of the project
    """
    pass

@mcp.tool()
def slidev_load(name: str) -> SlidevResult:
    """load exist slidev project and get the current slidev markdown content"""
    pass

@mcp.tool()
def slidev_make_cover(title: str, subtitle: str = "", author: str = "", background: str = "", python_string_template: str = "") -> SlidevResult:
    """
    Create or update slidev cover.
    `python_string_template` is python string template, you can use {title}, {subtitle} to format the string.
    If user give enough information, you can use it to update cover page, otherwise you must ask the lacking information. `background` must be a valid url of image
    """
    pass


@mcp.tool()
def slidev_add_page(content: str, layout: str = "default", parameters: dict = {}) -> SlidevResult:
    """
    Add new page.
    - `content` is markdown format text to describe page content.
    - `layout`: layout of the page
    - `parameters`: frontmatter parameters of the page
    """
    pass


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
    pass


@mcp.tool()
def slidev_get_page(index: int) -> SlidevResult:
    """get the content of the `index` th page"""
    pass


@mcp.tool()
def slidev_save_outline(outline: SaveOutlineParam) -> SlidevResult:
    """
    保存大纲到项目的 outline.json 文件中
    `outline`: 大纲项目列表，每个项目包含 group 和 content 字段
    """
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Slidev MCP Server')
    parser.add_argument('--transport', 
                       choices=['stdio', 'streamable-http'], 
                       default='stdio',
                       help='Transport method (default: stdio)')
    
    args = parser.parse_args()
    
    mcp.run(transport=args.transport)