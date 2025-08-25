from pathlib import Path
from typing import Dict, Any
import os

from servers.models.slidev import SlidevResult, SaveOutlineParam
from servers.core.common import transform_parameters_to_frontmatter

class SlidevBase:
    def __init__(self, state, theme: str = "academic"):
        """
        Base class for slidev MCP tools
        - state: SlidevStateManager 实例
        - theme: 默认主题
        """
        self.state = state
        self.theme = theme

    def create(self, name: str) -> SlidevResult:
        """创建 slidev 项目"""
        home = self.state.get_project_home(name)
        try:
            os.makedirs(home, exist_ok=True)
            slides_path = os.path.join(home, 'slides.md')

            if os.path.exists(slides_path):
                if self.state.load_slidev_content(name):
                    return SlidevResult(
                        success=True,
                        message=f"项目已存在 {home}/slides.md",
                        output=self.state.get_slidev_content()
                    )
            else:
                with open(slides_path, 'w', encoding="utf-8") as f:
                    f.write(f"""
---
theme: {self.theme}
layout: cover
transition: slide-left
---

# Your title
## sub title
""".strip())

                if not self.state.load_slidev_content(name):
                    return SlidevResult(success=False, message="项目创建成功但加载失败", output=name)

            return SlidevResult(success=True, message=f"成功创建并加载项目 {name}", output=name)

        except Exception as e:
            return SlidevResult(success=False, message=f"创建失败: {str(e)}", output=name)

    def load(self, name: str) -> SlidevResult:
        """加载已有项目"""
        slides_path = Path(self.state.get_project_home(name)) / "slides.md"
        if self.state.load_slidev_content(name):
            return SlidevResult(
                success=True,
                message=f"项目加载成功: {slides_path.absolute()}",
                output=self.state.get_slidev_content()
            )
        return SlidevResult(success=False, message=f"加载失败: {slides_path.absolute()}")

    def make_cover(self, title: str, subtitle: str = "", author: str = "", background: str = "", python_string_template: str = "") -> SlidevResult:
        """创建/更新封面"""
        if not self.state.is_project_loaded():
            return SlidevResult(success=False, message="没有激活的项目")

        if python_string_template:
            template = f"""
---
theme: {self.theme}
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
theme: {self.theme}
layout: cover
transition: slide-left
coverAuthor: {author}
background: {background}
---

# {title}
## {subtitle}
""".strip()

        slides = self.state.get_slidev_content()
        if slides:
            slides[0] = template
        else:
            slides.append(template)
        self.state.set_slidev_content(slides)
        self.state.save_slidev_content()

        return SlidevResult(success=True, message="封面已更新", output=0)

    def add_page(self, content: str, layout: str = "default", parameters: Dict[str, Any] = None) -> SlidevResult:
        """添加页面"""
        if not self.state.is_project_loaded():
            return SlidevResult(success=False, message="没有激活的项目")

        parameters = parameters or {}
        parameters['layout'] = layout
        parameters['transition'] = 'slide-left'
        frontmatter = transform_parameters_to_frontmatter(parameters)

        template = f"""
---
{frontmatter}
---

{content}
""".strip()

        slides = self.state.get_slidev_content()
        slides.append(template)
        self.state.set_slidev_content(slides)
        self.state.save_slidev_content()

        return SlidevResult(success=True, message="新页面添加完成", output=len(slides) - 1)

    def set_page(self, index: int, content: str, layout: str = "", parameters: Dict[str, Any] = None) -> SlidevResult:
        """更新页面"""
        if not self.state.is_project_loaded():
            return SlidevResult(success=False, message="没有激活的项目")

        slides = self.state.get_slidev_content()
        if index < 0 or index >= len(slides):
            return SlidevResult(success=False, message=f"无效的页码 {index}")

        parameters = parameters or {}
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
        self.state.set_slidev_content(slides)
        self.state.save_slidev_content()

        return SlidevResult(success=True, message=f"第 {index} 页更新完成", output=index)

    def get_page(self, index: int) -> SlidevResult:
        """获取页面内容"""
        if not self.state.is_project_loaded():
            return SlidevResult(success=False, message="没有激活的项目")

        slides = self.state.get_slidev_content()
        if index < 0 or index >= len(slides):
            return SlidevResult(success=False, message=f"无效的页码 {index}")

        return SlidevResult(success=True, message=f"第 {index} 页内容", output=slides[index])

    def save_outline(self, outline: SaveOutlineParam) -> SlidevResult:
        """保存 outline.json"""
        if self.state.save_outline_content(outline):
            return SlidevResult(success=True, message="大纲保存成功")
        return SlidevResult(success=False, message="保存失败，没有激活的项目")

    def export_project(self, path: str):
        """导出项目元信息"""
        return self.state.active_project
