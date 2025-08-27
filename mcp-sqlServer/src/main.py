"""
Main entry point for the MCP SQL Server
"""
import sys
from mcp.server.fastmcp import FastMCP
from .config import MCP_PORT, SCHEMA_FILE_PATH
from .schema_loader import SchemaLoader
from .mcp_tools import MCPTools


def create_mcp_server():
    """Create and configure the MCP server with all tools"""
    # Initialize FastMCP server
    mcp = FastMCP("mssqlQuery", stateless_http=True, port=MCP_PORT)
    
    # Initialize components
    schema_loader = SchemaLoader(SCHEMA_FILE_PATH)
    mcp_tools = MCPTools(schema_loader)
    
    # Register MCP tools
    @mcp.tool()
    async def mssqlQuery(request: str):
        """
        Execute a SQL query based on a natural language question using REST API for MS SQL Server.

        Args:
            request: A natural language question about the data (e.g., "Show me the top 10 customers by request count", 
                    "What products were used in 2024-01?", "Which customers have more than 1000 requests?")

        Returns:
            A JSON object containing the query results, generated SQL, or error information.
        """
        return await mcp_tools.execute_sql_query(request)

    @mcp.tool() 
    async def listTablesMSSQL():
        """
        List all available tables and their columns that can be queried via REST API for MS SQL Server.
        
        Returns:
            A JSON object containing all available tables, their column information, and metadata.
        """
        return await mcp_tools.list_tables()

    @mcp.tool()
    async def validateAzureAuthMSSQL():
        """
        Validate Azure AD authentication for MS SQL Server using REST approach.
        
        Returns:
            A JSON object containing authentication test results.
        """
        return await mcp_tools.validate_azure_auth()

    @mcp.tool()
    async def executeCustomSQLMSSQL(sql_query: str):
        """
        Execute a custom SQL query directly via REST API for MS SQL Server (for advanced users).
        
        Args:
            sql_query: A valid SQL SELECT statement to execute.
            
        Returns:
            A JSON object containing the query results.
        """
        return await mcp_tools.execute_custom_sql(sql_query)

    @mcp.tool()
    async def getEnumValuesMSSQL(field_name: str):
        """
        Get available enum values for a specific field to help with query construction for MS SQL Server.
        
        Args:
            field_name: The name of the field to get enum values for (e.g., 'Product', 'TrackInfo', 'Provider')
            
        Returns:
            A JSON object containing the available enum values for the specified field.
        """
        return await mcp_tools.get_enum_values(field_name)

    @mcp.tool()
    async def validateQueryMSSQL(user_question: str):
        """
        Validate a user question and show what SQL would be generated without executing it for MS SQL Server.
        
        Args:
            user_question: The natural language question to validate
            
        Returns:
            A JSON object containing the validation results and planned SQL query.
        """
        return await mcp_tools.validate_query(user_question)
    
    return mcp


def main():
    """Main entry point"""
    try:
        # Initialize and run the server
        print("Starting MCP MS SQL Server with REST API support (No ODBC required)...")
        mcp = create_mcp_server()
        mcp.run(transport="streamable-http")
    except Exception as e:
        print(f"Error while running MCP server: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
