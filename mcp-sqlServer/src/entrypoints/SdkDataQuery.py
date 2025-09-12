"""
Unified MCP Server that provides a single unified_query tool
Decides between SQL Server and Kusto based on the user question
"""
import resource
import sys
import os
import json
from mcp.server.fastmcp import FastMCP
# from mcp.server.fastmcp import MCP, Prompt, Resource, Tool, Run
from ..config.config import MCP_PORT, SCHEMA_FILE_PATH
from ..data.schema_loader import SchemaLoader
from ..services.sql_mcp_tools import MCPTools
from ..services.kusto_mcp_tools import KQLGeneratorMCP
from ..utils.file_reader import read_file_content

def sdkdataQueryMCP():
    """Create and configure the MCP server with unified query tool"""
    # Initialize FastMCP server
    mcp = FastMCP("sdkdataQueryServer", stateless_http=True, port=MCP_PORT)

    @mcp.resource(name="kusto_schema_resource", uri="http://localhost:7071/mcp/load_kusto_schema")
    def load_kusto_schema():
        """Load Kusto schema from reference/schemas/KQL_Schema.json"""
        try:
            schema_content = read_file_content('../../reference/schemas/KQL_Schema.json', relative_to_file=__file__)
            kusto_schema = json.loads(schema_content)
            return kusto_schema
        except Exception as e:
            return {"error": f"Failed to load Kusto schema: {str(e)}"}

    @mcp.resource(name="sql_schema_resource", uri="http://localhost:7071/mcp/load_sql_schema")
    def load_sql_schema():
        """Load SQL schema from reference/schemas/AMEAnalytics_Schema.json"""
        try:
            schema_content = read_file_content('../../reference/schemas/AMEAnalytics_Schema.json', relative_to_file=__file__)
            sql_schema = json.loads(schema_content)
            return sql_schema
        except Exception as e:
            return {"error": f"Failed to load SQL schema: {str(e)}"}

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
            
            # Read prompt template from file
            prompt_template = read_file_content('../../reference/prompt/QueryTypeDecision2.md', relative_to_file=__file__)
            
            # Replace placeholder with actual user question
            prompt = prompt_template.replace("{user_question_here}", user_question)
            
            return prompt
            
        except Exception as e:
            print(f"Error in unified_query tool: {str(e)}")
            return {
                "type": "error",
                "message": f"Error processing unified query: {str(e)}"
            }
    
    # Register executeSQLQuery tool with fallback to KQL (enhanced version)
    # This allows users to execute SQL queries, with automatic fallback to KQL generation if SQL fails
    @mcp.tool()
    async def executeSQLQuery(table_name: str, columns: list, where_clause: str = "", order_clause: str = "", limit_clause: str = "", original_question: str = ""):
        """
        Execute a SQL query using the parsed components from parseUserQuery for MS SQL Server.
        Includes Azure AD authentication validation. If SQL execution fails, automatically attempts 
        to generate a KQL query as fallback.

        Args:
            table_name: The name of the table to query
            columns: List of column names to select
            where_clause: SQL WHERE conditions (optional)
            order_clause: SQL ORDER BY clause (optional)  
            limit_clause: SQL LIMIT/TOP clause (optional)
            original_question: The original user question (optional, used for KQL fallback)

        Returns:
            A JSON object containing the query results, or KQL generation if SQL fails.
        """
        print(f"Executing SQL query")
        return "SQL query result placeholder"

    # Register generateKQLFromTemplate tool (adapted from kusto_server.py)
    # This allows users to generate KQL queries from templates
    @mcp.tool()
    async def executeKQLQuery(user_question: str):
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
        print(f"Executing KQL query")
        return "KQL query result placeholder"
    
    return mcp


def main():
    """Main entry point for the unified MCP server"""
    try:
        print("Starting Unified MCP Server with comprehensive query tools...")
        print("Available tools:")
        print("  - unified_query: Decides between SQL/KQL and generates queries")
        print("  - smart_query_execution: Automatically tries SQL first, falls back to KQL")
        print("  - executeSQLQuery: Executes SQL queries with automatic KQL fallback")
        print("  - generateKQLFromTemplate: Generates KQL queries from templates")
        
        # Initialize and run the server
        mcp = sdkdataQueryMCP()
        mcp.run(transport="streamable-http")
        
    except Exception as e:
        print(f"Error while running MCP server: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()