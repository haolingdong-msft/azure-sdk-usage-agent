"""
MCP Server Configuration Service

Handles MCP server creation, configuration, and tool registration.
"""
from mcp.server.fastmcp import FastMCP
from src.config import MCP_PORT
from src.tools.sql_query_tool import SQLServerMCPTools
from src.tools.kql_generator_tool import KQLGeneratorMCP
from src.tools.query_selection_tool import QueryToolSelector
from src.tools.sql_generator_tool import SQLGeneratorTool
from src.utils.file_utils import read_relative_file, load_description

class ServerConfigurator:
    """Configures and creates the MCP server with all required tools"""
    
    def __init__(self):
        self.query_tool_selector = QueryToolSelector()
        self.sql_generator = SQLGeneratorTool()
        self.sql_tools = SQLServerMCPTools()
        self.kusto_tools = KQLGeneratorMCP()
    
    def create_mcp_server(self, file_context) -> FastMCP:
        """Create and configure the MCP server with all tools"""
        mcp = FastMCP(
            "create_sdk_usage_mcp_server", 
            stateless_http=True, 
            port=MCP_PORT,
            instructions=read_relative_file("instructions/MCP_Instructions.md", file_context)
        )
        
        # Register core analysis tool
        @mcp.tool(description=load_description("analyzeUserIntent", file_context))
        async def analyzeUserIntent(user_question: str):
            return self.query_tool_selector.analyze_user_intent(user_question)
        
        # Register SQL execution tool
        @mcp.tool(description=load_description("executeSQLQuery", file_context))
        async def executeSQLQuery(sql_query: str):
            return await self.sql_tools.execute_sql_query(sql_query)
        
        # Register KQL generation tool
        @mcp.tool(description=load_description("generateKQLFromTemplate", file_context))
        async def generateKQLFromTemplate(user_question: str):
            return await self.kusto_tools.generate_kql_from_template(user_question)
        
        # Register all SQL generation tools
        self.sql_generator.register_sql_tools(mcp, file_context)
        
        return mcp