"""
Unified MCP Server that provides a single unified_query tool
Decides between SQL Server and Kusto based on the user question
"""
import sys
from mcp.server.fastmcp import FastMCP
from src.config import MCP_PORT, SCHEMA_FILE_PATH
from src.services.sql_mcp_tools import SQLServerMCPTools
from src.services.kusto_mcp_tools import KQLGeneratorMCP
from src.utils.file_utils import read_file_content
from src.utils.schema_utils import getSQLSchemaDefinitions

def sdkdataQueryMCP():
    """Create and configure the MCP server with unified query tool"""
    mcp = FastMCP("sdkdataQueryServer", stateless_http=True, port=MCP_PORT)

    mcpSqltools = SQLServerMCPTools()
    mcpKustoTools = KQLGeneratorMCP()

    @mcp.tool()
    async def queryTypeDecision(user_question: str):
        """
        queryTypeDecision MCP tool that decides between SQL Server and Kusto based on user question.
        
        Args:
            user_question: A natural language question about the data
            
        Returns:
            A string only "sql" OR "kusto"
        """
        try:
            print(f"Processing unified query: {user_question}")
            
            prompt_template = read_file_content('templates/prompts/QueryTypeDecision.md', relative_to_file=__file__)
            
            prompt = prompt_template.replace("{USER_QUESTION}", user_question)
            
            schema_definitions = await getSQLSchemaDefinitions(["Month", "Product", "TrackInfo", "HttpMethod", "OS", "RequestCount", "SubscriptionCount", "SubscriptionId", "Provider", "ApiVersion", "HttpMethod", "OS", "PackageName", "PackageVersion", "IsTrack2"])
            prompt = prompt.replace("{SQL_SCHEMA_FIELD}", str(schema_definitions))

            return prompt
            
        except Exception as e:
            print(f"Error in unified_query tool: {str(e)}")
            return {
                "type": "error",
                "message": f"Error processing unified query: {str(e)}"
            }

    @mcp.tool()
    async def generateSQLQuery(user_question: str):
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

        return await mcpSqltools.generate_sql_from_template(user_question)

    @mcp.tool()
    async def executeSQLQuery(sql_query: str):
        """
        Execute a SQL query from generateSQLQuery for MS SQL Server.

        Args:
            sql_query: The SQL query string to execute

        Returns:
            A JSON object containing the query results
        """
        return await mcpSqltools.execute_sql_query(sql_query)
    
    @mcp.tool()
    async def generateKQLFromTemplate(user_question: str):
        """
        Generate KQL query based on Azure SDK usage query template and user question
        
        This tool will:
        1. Read src/templates/queries/azure_sdk_usage_query.kql as template
        2. Return user question and template together to AI
        3. Let AI generate new KQL query based on template and question
        
        Args:
            user_question: User's query requirement (e.g.: "Show percentage analysis of Go SDK resource providers last month")
            
        Returns:
            Structured data containing template and user question for AI to generate new KQL query
        """
        return await mcpKustoTools.generate_kql_from_template(user_question)

    
    return mcp


def main():
    """Main entry point for the unified MCP server"""
    try:
        print("Starting Unified MCP Server with comprehensive query tools...")
        print("Available tools:")
        print("  - queryTypeDecision: Decides between SQL/KQL based on user question")
        print("  - generateSQLQuery: Generates SQL queries from natural language")
        print("  - executeSQLQuery: Executes SQL queries")
        print("  - generateKQLFromTemplate: Generates KQL queries from templates")
        
        # Initialize and run the server
        mcp = sdkdataQueryMCP()
        mcp.run(transport="streamable-http")
        
    except Exception as e:
        print(f"Error while running MCP server: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()