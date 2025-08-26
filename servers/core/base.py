from pathlib import Path
from typing import Dict, Any
import os

from servers.models.slidev import SlidevResult, SaveOutlineParam, SlidevCreateParam, SlidevMakeCoverParam, SlidevAddPageParam, SlidevSetPageParam, SlidevGetPageParam, SlidevLoadParam
from servers.models.template import TemplateName
from servers.core.common import transform_parameters_to_frontmatter
from servers.core.state_manager import SlidevStateManager
from servers.core.template_manager import TemplateManager

class SlidevBase:
    def __init__(
            self,
            theme: str,
            state_manager: SlidevStateManager,
            template_manager: TemplateManager,
        ):
        """
        Base class for slidev MCP tools
        - state_manager: SlidevStateManager 实例
        - theme: 默认主题
        """
        self.state_manager = state_manager
        self.template_manager = template_manager
        self.theme = theme

    def create(self, param: SlidevCreateParam) -> SlidevResult:
        """创建 slidev 项目"""
        name = param.name
        home = self.state_manager.get_project_home(name)

        os.makedirs(home, exist_ok=True)
        slides_path = os.path.join(home, 'slides.md')

        if os.path.exists(slides_path):
            return self.load(name)
        else:
            template = self.template_manager.render(TemplateName.cover, {
                "title": name
            })

            with open(slides_path, 'w', encoding="utf-8") as f:
                f.write(template)
            
            if not self.state_manager.load_slidev_content(name):
                return SlidevResult(success=False, message="项目创建成功但加载失败", data=name)

        return SlidevResult(success=True, message=f"成功创建并加载项目 {name}", data=name)

    def load(self, param: SlidevLoadParam) -> SlidevResult:
        """加载已有项目"""
        
        name = param.name
        slides_path = Path(self.state_manager.get_project_home(name)) / "slides.md"
        if self.state_manager.load_slidev_content(name):
            return SlidevResult(
                success=True,
                message=f"项目加载成功: {slides_path.absolute()}",
                data=self.state_manager.get_slidev_content()
            )
        return SlidevResult(success=False, message=f"加载失败: {slides_path.absolute()}")

    def make_cover(self, param: SlidevMakeCoverParam) -> SlidevResult:
        """创建/更新封面"""
        if not self.state_manager.is_project_loaded():
            return SlidevResult(success=False, message="没有激活的项目")

        template = self.template_manager.render(
            template_name=TemplateName.cover,
            context=param.model_dump()
        )

        self.state_manager.set_slidev_page(0, template)
        self.state_manager.save_slidev_content()

        return SlidevResult(success=True, message="封面已更新")

    def add_page(self, param: SlidevAddPageParam) -> SlidevResult:
        """添加页面"""
        if not self.state_manager.is_project_loaded():
            return SlidevResult(success=False, message="没有激活的项目")

        template = self.template_manager.render(TemplateName.page, {
            "content": param.content,
            "layout": param.layout,
            "parameters": param.parameters
        })

        new_index = self.state_manager.add_page_content(template)
        self.state_manager.save_slidev_content()

        return SlidevResult(success=True, message=f"新页面添加完成，添加到第 {new_index} 页")

    def set_page(self, param: SlidevSetPageParam) -> SlidevResult:
        """更新页面"""
        if not self.state_manager.is_project_loaded():
            return SlidevResult(success=False, message="没有激活的项目")

        slides = self.state_manager.get_slidev_content()
        index = param.index

        if index < 0 or index >= len(slides):
            return SlidevResult(success=False, message=f"无效的页码 {index}")

        template = self.template_manager.render(TemplateName.page, {
            "content": param.content,
            "layout": param.layout,
            "parameters": param.parameters
        })

        self.state_manager.set_slidev_page(index, template)
        self.state_manager.save_slidev_content()

        return SlidevResult(success=True, message=f"第 {index} 页更新完成")

    def get_page(self, param: SlidevGetPageParam) -> SlidevResult:
        """获取页面内容"""

        index = param.index
        if not self.state_manager.is_project_loaded():
            return SlidevResult(success=False, message="没有激活的项目")

        slides = self.state_manager.get_slidev_content()
        if index < 0 or index >= len(slides):
            return SlidevResult(success=False, message=f"无效的页码 {index}")

        return SlidevResult(success=True, message=f"第 {index} 页内容")

    def save_outline(self, outline: SaveOutlineParam) -> SlidevResult:
        """保存 outline.json"""
        if self.state_manager.save_outline_content(outline):
            return SlidevResult(success=True, message="大纲保存成功")
        return SlidevResult(success=False, message="保存失败，没有激活的项目")

    def export_project(self, path: str):
        """导出项目元信息"""
        return self.state_manager.active_project
