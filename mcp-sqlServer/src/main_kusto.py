"""
Main entry point for the MCP Kusto Query Server
Simplified version: Only responsible for passing data to AI, letting AI handle query generation logic
"""
import sys
from mcp.server.fastmcp import FastMCP
from .config import MCP_PORT_KUSTO
from .simple_kusto_mcp import SimpleKustoMCP

def create_kusto_mcp_server():
    """Create and configure the MCP server for Kusto query operations"""
    mcp = FastMCP("kustoQueryModifier", stateless_http=True, port=MCP_PORT_KUSTO)
    
    # Initialize components
    mcp_tools = SimpleKustoMCP()
    
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

    @mcp.tool()
    async def modifyKustoQuery(original_kql: str, user_question: str):
        """
        Compatibility tool: Forward request to generateKQLFromTemplate
        
        Args:
            original_kql: Original KQL query (might not be used)
            user_question: User's modification requirement
            
        Returns:
            Structured data based on template and user question
        """
        return await mcp_tools.generate_kql_from_template(user_question)

    @mcp.tool()
    async def validateKustoSyntax(kql_query: str):
        """
        Validate basic syntax of KQL query
        
        Args:
            kql_query: KQL query to validate
            
        Returns:
            Basic syntax validation result
        """
        return await mcp_tools.validate_kusto_syntax(kql_query)

    @mcp.tool()
    async def explainKustoQuery(kql_query: str):
        """
        Explain main components of KQL query
        
        Args:
            kql_query: KQL query to explain
            
        Returns:
            Explanation of query structure and operations
        """
        return await mcp_tools.explain_kusto_query(kql_query)
    
    return mcp

    # @mcp.tool()
    # async def getKqlExamples():
    #     """
    #     Get example KQL queries for common scenarios
        
    #     Returns:
    #         Collection of example KQL queries with descriptions and usage tips
    #     """
    #     return mcp_tools.get_kql_examples()
    
    return mcp


def main():
    """Main entry point for Kusto MCP server"""
    try:
        # Initialize and run the server
        print("Starting MCP Kusto Query Modifier Server...")
        mcp = create_kusto_mcp_server()
        mcp.run(transport="streamable-http")
    except Exception as e:
        print(f"Error while running Kusto MCP server: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()