"""
Main entry point for the MCP SQL Server with AI Query Helper
Includes executeSQLQuery, aiQueryHelper, generateSQLQuery, and executeAIGeneratedQuery tools
"""
import sys
from mcp.server.fastmcp import FastMCP
from ..config.config import MCP_PORT, SCHEMA_FILE_PATH
from ..data.schema_loader import SchemaLoader
from ..services.sql_mcp_tools import SQLServerMCPTools

def create_mcp_server():
    """Create and configure the MCP server with AI helper and execute tools"""
    # Initialize FastMCP server
    mcp = FastMCP("mssqlQueryAI", stateless_http=True, port=MCP_PORT)
    
    # Initialize components
    schema_loader = SchemaLoader(SCHEMA_FILE_PATH)
    mcp_tools = SQLServerMCPTools(schema_loader)

    @mcp.tool()
    async def generate_sql_query(user_question: str):
        """
        Generate SQL query from user question and SQL schema.

        This tool will:
        1. Read table schema as reference
        2. Return user question and schema together to AI
        3. Let AI generate a new SQL query and question

        Args:
            user_question: A natural language question about the data

        Returns:
            A SQL Query
        """

        return await mcp_tools.generate_sql_from_template(user_question)

    @mcp.tool()
    async def execute_sql_query(sql_query: str):
        """
        Execute a SQL query from generate_sql_query for MS SQL Server.

        Args:
            sql_query: The SQL query string to execute

        Returns:
            A JSON object containing the query results
        """
        return await mcp_tools.execute_sql_query(sql_query)
        # return 'finished execute_sql_query'
    
    return mcp


def main():
    """Main entry point"""
    try:
        # Initialize and run the server
        print("Starting MCP MS SQL Server with AI Query Helper (executeSQLQuery + aiQueryHelper + generateSQLQuery + executeAIGeneratedQuery)...")
        mcp = create_mcp_server()
        mcp.run(transport="streamable-http")
    except Exception as e:
        print(f"Error while running MCP server: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
