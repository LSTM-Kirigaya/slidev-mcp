from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from typing import Dict, Any

from servers.models.template import TemplateName

class TemplateManager:
    def __init__(self, template_dir: str = None):
        if template_dir is None:
            template_dir = str(Path(__file__).parent / "templates")

        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(["md", "j2"])
        )

    def render(self, template_name: TemplateName, context: Dict[str, Any]) -> str:
        template = self.env.get_template(template_name)
        return template.render(**context)
