from mcp.server.fastmcp import FastMCP
from pathlib import Path

from servers.core.base_server import SlidevBaseServer

mcp = FastMCP('slidev-mcp-academic')
current_path = Path(__file__).parent
print(current_path)
# server = SlidevBaseServer(mcp, 'academic', 'prompts', 'templates')

# mcp.run(transport='stdio')