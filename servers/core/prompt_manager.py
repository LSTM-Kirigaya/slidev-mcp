from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from typing import Dict, Any

from servers.models.prompt import PromptName

class PromptManager:
    def __init__(self, prompt_dir: str = None):
        if prompt_dir is None:
            prompt_dir = str(Path(__file__).parent / "prompts")

        self.env = Environment(
            loader=FileSystemLoader(prompt_dir),
            autoescape=select_autoescape(["j2"])
        )
        
    def render(self, template_name: PromptName, context: Dict[str, Any]) -> str:
        template = self.env.get_template(template_name)
        return template.render(context)
