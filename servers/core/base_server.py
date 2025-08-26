import asyncio

from mcp.server.fastmcp import FastMCP
# user profile mcp: https://github.com/LSTM-Kirigaya/usermcp
from usermcp import register_user_profile_mcp
from colorama import Fore, Style

from servers.core.common import websearch, check_environment
from servers.core.state_manager import SlidevStateManager
from servers.core.prompt_manager import PromptManager
from servers.core.template_manager import TemplateManager
from servers.core.base import SlidevBase
from servers.models.slidev import SlidevResult, SlidevCreateParam, SlidevMakeCoverParam, SlidevAddPageParam, SlidevSetPageParam, SlidevLoadParam, SlidevGetPageParam
from servers.models.prompt import PromptName
from servers.core.common import print_prompts, print_resource_templates, print_resources, print_tools

class SlidevBaseServer:
    def __init__(self,
        mcp: FastMCP,
        theme: str,
        template_dir: str,
        prompt_dir: str
    ):
        self.mcp = mcp
        self.state_manager = SlidevStateManager(theme=theme)
        self.template_manager = TemplateManager(template_dir)
        self.prompt_manager = PromptManager(prompt_dir)

        self.slidev = SlidevBase(theme, self.state_manager, self.template_manager)

        self.install_usermcp_tools()
        self.install_crawl4ai_tools()
        self.install_slidev_tools()
        self.install_slidev_prompts()

        asyncio.run(show_mcp_detail(mcp))

    def install_usermcp_tools(self):
        register_user_profile_mcp(self.mcp)
    
    def install_crawl4ai_tools(self):
        self.mcp.add_tool(
            fn=websearch,
            name='websearch',
            description='search the given https url and get the markdown text of the website'
        )
    
    def install_slidev_tools(self):
        slidev = self.slidev
        mcp = self.mcp

        @mcp.tool()
        def slidev_check_environment() -> SlidevResult:
            """
            Check if nodejs and slidev-cli is ready.
            
            Returns:
                SlidevResult: Result indicating if the environment is properly set up
            """
            return check_environment()


        @mcp.tool()
        def slidev_create(param: SlidevCreateParam) -> SlidevResult:
            """
            Create a new slidev project with the given name.
            
            Args:
                name (str): The name of the slidev project to create
                
            Returns:
                SlidevResult: Result indicating success or failure of the creation process
            """
            return slidev.create(param)


        @mcp.tool()
        def slidev_load(param: SlidevLoadParam) -> SlidevResult:
            """
            Load an existing slidev project.
            
            Args:
                param (SlidevLoadParam): Parameter containing the name of the project to load
                
            Returns:
                SlidevResult: Result containing the loaded project data or error message
            """
            return slidev.load(param)


        @mcp.tool()
        def slidev_make_cover(param: SlidevMakeCoverParam) -> SlidevResult:
            """
            Create or update slidev cover.
            
            Args:
                param (SlidevMakeCoverParam): Parameters for creating/updating the cover
                
            Returns:
                SlidevResult: Result indicating success or failure of the operation
            """
            return slidev.make_cover(param)
        

        @mcp.tool()
        def slidev_add_page(param: SlidevAddPageParam) -> SlidevResult:
            """
            Add a new page to the slidev presentation.
            
            Args:
                param (SlidevAddPageParam): Parameters for the new page including content, layout and parameters
                
            Returns:
                SlidevResult: Result indicating success or failure of the operation
            """
            return slidev.add_page(param)


        @mcp.tool()
        def slidev_set_page(param: SlidevSetPageParam) -> SlidevResult:
            """
            Update an existing page in the slidev presentation.
            
            Args:
                param (SlidevSetPageParam): Parameters for updating the page including index, content, layout and parameters
                
            Returns:
                SlidevResult: Result indicating success or failure of the operation
            """
            return slidev.set_page(param)


        @mcp.tool()
        def slidev_get_page(param: SlidevGetPageParam) -> SlidevResult:
            """
            Get the content of a specific page in the slidev presentation.
            
            Args:
                param (SlidevGetPageParam): Parameter containing the index of the page to retrieve
                
            Returns:
                SlidevResult: Result containing the page content or error message
            """
            return slidev.get_page(param)
        
        @mcp.tool()
        def slidev_export_project():
            return slidev.state_manager.active_project
        

    def install_slidev_prompts(self):
        mcp = self.mcp
        slidev = self.slidev
        prompt_manager = self.prompt_manager

        @mcp.prompt()
        def outline_generate_prompt(title: str, content: str):
            """generate outline for slidev"""
            return prompt_manager.render(
                PromptName.outline_generate,
                {
                    "title": title,
                    "content": content
                }
            )

        @mcp.prompt()
        def slidev_generate_prompt():
            return prompt_manager.render(
                PromptName.slidev_generate,
                {}
            )

        @mcp.prompt()
        def slidev_generate_with_specific_outlines_prompt(title: str, content: str, outlines: str, path: str):
            """generate slidev with specific outlines"""
            return prompt_manager.render(
                PromptName.slidev_generate_with_specific_outlines,
                {
                    "title": title,
                    "content": content,
                    "outlines": outlines,
                    "path": path
                }
            )
        

async def show_mcp_detail(mcp: FastMCP):
    tools = await mcp.list_tools()
    prompts = await mcp.list_prompts()
    resources = await mcp.list_resources()
    templates = await mcp.list_resource_templates()
    
    print(Fore.YELLOW + Style.BRIGHT + f"\n🚀 MCP Server {mcp.name} Registry")
    print_tools(tools)
    print_prompts(prompts)
    print_resources(resources)
    print_resource_templates(templates)