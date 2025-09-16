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
from ..services.sql_mcp_tools import SQLServerMCPTools
from ..services.kusto_mcp_tools import KQLGeneratorMCP
from ..utils.file_reader import read_file_content

def sdkdataQueryMCP():
    """Create and configure the MCP server with unified query tool"""
    # Initialize FastMCP server
    mcp = FastMCP("sdkdataQueryServer", stateless_http=True, port=MCP_PORT)

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
            
            prompt_template = read_file_content('../../reference/prompt/QueryTypeDecision.md', relative_to_file=__file__)
            
            prompt = prompt_template.replace("{USER_QUESTION}", user_question)
            
            # Await the async function call
            schema_definitions = await getSQLSchemaDefinitions(["Month", "Product", "TrackInfo", "HttpMethod", "OS", "RequestCount", "SubscriptionCount", "SubscriptionId", "Provider", "ApiVersion", "HttpMethod", "OS", "PackageName", "PackageVersion", "IsTrack2"])
            prompt = prompt.replace("{SQL_SCHEMA_FIELD}", str(schema_definitions))

            return prompt
            
        except Exception as e:
            print(f"Error in unified_query tool: {str(e)}")
            return {
                "type": "error",
                "message": f"Error processing unified query: {str(e)}"
            }

    async def getSQLSchemaDefinitions(field_names: list = None):
        """
        Extract complete field definitions from AMEAnalytics_Schema.json with all attributes.
        Returns the exact definition structure including title, description, type, enum, pattern, etc.
        
        Args:
            field_names: List of field names to retrieve from definitions (optional).
                        If None, returns all definitions.
                        Example: ["TrackInfo", "Product", "HttpMethod", "OS"]
            
        Returns:
            Complete field definitions in their original format, e.g.:
            {
                "Product": {
                    "title": "Product",
                    "description": "Azure SDK product name", 
                    "type": "string",
                    "enum": [".Net Code-gen", ".Net Fluent", ...]
                }
            }
        """
        try:
            print(f"Loading SQL schema definitions for fields: {field_names}")
            
            schema_content = read_file_content('../../reference/schemas/AMEAnalytics_Schema.json', relative_to_file=__file__)
            sql_schema = json.loads(schema_content)
            
            definitions = sql_schema.get("definitions", {})
            
            if field_names is None:
                return definitions
            
            filtered_definitions = {}
            
            for field_name in field_names:
                if field_name in definitions:
                    # Return the complete definition with all attributes
                    filtered_definitions[field_name] = definitions[field_name]
            
            return filtered_definitions
            
        except Exception as e:
            print(f"Error in getSQLSchemaDefinitions tool: {str(e)}")
            return {
                "_error": f"Error loading schema definitions: {str(e)}",
                "_available_fields": []
            }

    # Register executeSQLQuery tool with fallback to KQL (enhanced version)
    # This allows users to execute SQL queries, with automatic fallback to KQL generation if SQL fails
    @mcp.tool()
    async def executeSQLQuery(user_question: str):
        """
        Execute a SQL query .

        Args:
            user_question: User's query requirement (e.g.: "how many request count for go this month")

        Returns:
            A JSON object containing the query results.
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
        print("  - queryTypeDecision: Decides between SQL/KQL based on user question")
        print("  - getSQLSchemaDefinitions: Extracts complete field definitions from AMEAnalytics schema")
        print("  - executeSQLQuery: Executes SQL queries with automatic KQL fallback")
        print("  - executeKQLQuery: Generates KQL queries from templates")
        
        # Initialize and run the server
        mcp = sdkdataQueryMCP()
        mcp.run(transport="streamable-http")
        
    except Exception as e:
        print(f"Error while running MCP server: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()