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
    async def parseUserQuery(user_question: str):
        """
        Parse a natural language question and extract table names, column names, and conditions for MS SQL Server.

        Args:
            user_question: A natural language question about the data (e.g., "Show me the top 10 customers by request count", 
                         "What products were used in 2024-01?", "Which customers have more than 1000 requests?")

        Returns:
            A JSON object containing the parsed query components: table name, columns, conditions, ordering, and limit.
        """
        return await mcp_tools.parse_user_query(user_question)

    @mcp.tool()
    async def executeSQLQuery(table_name: str, columns: list, where_clause: str = "", order_clause: str = "", limit_clause: str = ""):
        """
        Execute a SQL query using the parsed components from parseUserQuery for MS SQL Server.
        Includes Azure AD authentication validation.

        Args:
            table_name: The name of the table to query
            columns: List of column names to select
            where_clause: SQL WHERE conditions (optional)
            order_clause: SQL ORDER BY clause (optional)  
            limit_clause: SQL LIMIT/TOP clause (optional)

        Returns:
            A JSON object containing the query results, or error information if authentication fails.
        """
        return await mcp_tools.execute_sql_with_auth(table_name, columns, where_clause, order_clause, limit_clause)
    
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
