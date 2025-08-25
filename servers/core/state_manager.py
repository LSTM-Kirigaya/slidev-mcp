import os
from pathlib import Path
from typing import Optional, Dict, List

from servers.models.slidev import SaveOutlineParam
from servers.core.common import parse_markdown_slides

class SlidevStateManager:
    def __init__(self, root_env_var: str = "SLIDEV_MCP_ROOT", default_root: str = ".slidev-mcp", theme: str = "academic"):
        # 设置根目录
        _env_root = os.environ.get(root_env_var)
        if _env_root and os.path.isabs(_env_root):
            self.root_dir = _env_root
        else:
            self.root_dir = default_root
        os.makedirs(self.root_dir, exist_ok=True)

        self.active_project: Optional[Dict] = None
        self.slidev_content: List[str] = []
        self.theme = theme

    def get_project_home(self, name: str) -> str:
        return os.path.join(self.root_dir, name)

    def set_active_project(self, name: str, slides_path: str):
        self.active_project = {
            "name": name,
            "home": self.get_project_home(name),
            "slides_path": slides_path
        }

    def clear_active_project(self):
        self.active_project = None
        self.slidev_content = []

    def set_slidev_content(self, slides: List[str]):
        self.slidev_content = slides

    def get_slidev_content(self) -> List[str]:
        return self.slidev_content

    def is_project_loaded(self) -> bool:
        return self.active_project is not None

    def load_slidev_content(self, name: str) -> bool:
        """加载指定项目的 slides.md，并设置为 active project"""
        home = self.get_project_home(name)
        slides_path = Path(home) / "slides.md"

        if not slides_path.exists():
            return False

        with open(slides_path.absolute(), "r", encoding="utf-8") as f:
            content = f.read()

        # 更新状态
        self.set_active_project(name, str(slides_path))
        slides = parse_markdown_slides(content)
        self.set_slidev_content([s.strip() for s in slides if s.strip()])
        return True

    def save_slidev_content(self) -> bool:
        """保存当前项目的 slides 内容到 slides.md"""
        if not self.is_project_loaded():
            return False
        with open(self.active_project["slides_path"], "w", encoding="utf-8") as f:
            f.write("\n\n".join(self.get_slidev_content()))
        return True

    def save_outline_content(self, outline: "SaveOutlineParam") -> bool:
        """保存 outline.json"""
        if not self.is_project_loaded():
            return False
        outline_path = os.path.join(self.active_project["home"], "outline.json")
        with open(outline_path, "w", encoding="utf-8") as f:
            f.write(outline.model_dump_json(indent=2))
        return True
