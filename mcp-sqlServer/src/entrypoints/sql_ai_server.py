"""
Main entry point for the MCP SQL Server with AI Query Helper
Only includes executeSQLQuery and AI helper tools (no parseUserQuery)
"""
import sys
from mcp.server.fastmcp import FastMCP
from ..config.config import MCP_PORT, SCHEMA_FILE_PATH
from ..data.schema_loader import SchemaLoader
from ..services.mcp_tools import MCPTools

def create_mcp_server():
    """Create and configure the MCP server with AI helper and execute tools only"""
    # Initialize FastMCP server
    mcp = FastMCP("mssqlQueryAI", stateless_http=True, port=MCP_PORT)
    
    # Initialize components
    schema_loader = SchemaLoader(SCHEMA_FILE_PATH)
    mcp_tools = MCPTools(schema_loader)
    
    # Register executeSQLQuery tool (unchanged)
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
    
    # Register AI Query Helper tool
    @mcp.tool()
    async def aiQueryHelper(user_question: str):
        """
        Helper function for AI agents to generate correct column names, table names, and conditions
        based on user questions and available database schema.

        Args:
            user_question: A natural language question about the data

        Returns:
            A JSON object containing:
            - available_tables: List of all available tables with descriptions
            - suggested_table: Most relevant table for the question
            - available_columns: All columns for the suggested table  
            - column_metadata: Detailed information about each column
            - enum_values: Valid values for enum columns
            - example_conditions: Example WHERE clause conditions
            - example_columns: Suggested columns based on question intent
        """
        return await mcp_tools.ai_query_helper(user_question)
    
    return mcp


def main():
    """Main entry point"""
    try:
        # Initialize and run the server
        print("Starting MCP MS SQL Server with AI Query Helper (executeSQLQuery + aiQueryHelper only)...")
        mcp = create_mcp_server()
        mcp.run(transport="streamable-http")
    except Exception as e:
        print(f"Error while running MCP server: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
