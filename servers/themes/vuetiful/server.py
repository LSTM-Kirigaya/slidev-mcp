import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
current_path = Path(__file__).parent
theme = current_path.name

sys.path.insert(0, str(project_root))

from mcp.server.fastmcp import FastMCP
from servers.core.base_server import SlidevBaseServer

mcp = FastMCP(f'slidev-mcp-{theme}')
server = SlidevBaseServer(
    mcp=mcp,
    theme=theme,
    prompt_dir=current_path / 'prompts',
    template_dir=current_path / 'templates'
)

mcp.run(transport='stdio')