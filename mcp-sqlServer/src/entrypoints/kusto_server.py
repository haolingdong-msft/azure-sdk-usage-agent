"""
Main entry point for the MCP KQL Generator Server
Template-based KQL query generation through MCP protocol
"""
import sys
from mcp.server.fastmcp import FastMCP
from ..config.config import MCP_PORT_KUSTO
from ..services.kusto_mcp_tools import KQLGeneratorMCP

def create_kusto_mcp_server():
    """Create and configure the MCP server for KQL query generation"""
    mcp = FastMCP("kqlGenerator", stateless_http=True, port=MCP_PORT_KUSTO)
    
    # Initialize components
    mcp_tools = KQLGeneratorMCP()
    
    # Register Kusto-specific MCP tools
    @mcp.tool()
    async def generateKQLFromTemplate(user_question: str):
        """
        Generate KQL query based on sample.kql template and user question
        
        This tool will:
        1. Read reference/samples/sample.kql as template
        2. Return user question and template together to AI
        3. Let AI generate new KQL query based on template and question
        
        Args:
            user_question: User's query requirement (e.g.: "Show percentage analysis of Go SDK resource providers last month")
            
        Returns:
            Structured data containing template and user question for AI to generate new KQL query
        """
        return await mcp_tools.generate_kql_from_template(user_question)
    
    return mcp

def main():
    """Main entry point for KQL Generator MCP server"""
    try:
        # Initialize and run the server
        print("Starting MCP KQL Generator Server...")
        mcp = create_kusto_mcp_server()
        mcp.run(transport="streamable-http")
    except Exception as e:
        print(f"Error while running KQL Generator MCP server: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
