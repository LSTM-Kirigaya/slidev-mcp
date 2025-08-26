from mcp.server.fastmcp import FastMCP
# user profile mcp: https://github.com/LSTM-Kirigaya/usermcp
from usermcp import register_user_profile_mcp

from servers.core.common import websearch, check_environment
from servers.core.base import SlidevBase
from servers.models.slidev import SlidevResult, SlidevMakeCoverParam, SlidevAddPageParam, SlidevSetPageParam, SlidevLoadParam, SlidevGetPageParam

class SlidevBaseServer:
    def __init__(self, mcp: FastMCP, slidev: SlidevBase):
        self.mcp = mcp
        self.slidev = slidev

        self.install_usermcp_tools()
        self.install_crawl4ai_tools()
        self.install_slidev_necessary_tools()

    def install_usermcp_tools(self):
        register_user_profile_mcp(self.mcp)
    
    def install_crawl4ai_tools(self):
        self.mcp.add_tool(
            fn=websearch,
            name='websearch',
            description='search the given https url and get the markdown text of the website'
        )
    
    def install_slidev_necessary_tools(self):
        slidev = self.slidev
        mcp = self.mcp

        @mcp.tool()
        def slidev_check_environment() -> SlidevResult:
            """check if nodejs and slidev-cli is ready"""
            return check_environment()


        @mcp.tool()
        def slidev_create(name: str) -> SlidevResult:
            """create slidev, you need to ask user to get title and author to continue the task. you don't know title and author at beginning."""
            return slidev.create(name)


        @mcp.tool()
        def slidev_make_cover(param: SlidevMakeCoverParam) -> SlidevResult:
            """Create or update slidev cover."""
            return slidev.make_cover(param)
        

        @mcp.tool()
