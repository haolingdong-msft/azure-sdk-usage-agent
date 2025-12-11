import sys
import warnings
import logging

from mcp.server.fastmcp import FastMCP

from src.tools import (
    execute_kusto_query,
    generate_kql_from_question,
    get_kusto_helper_functions,
)

# Reduce MCP SDK, uvicorn, and httpx logging verbosity
logging.getLogger("mcp").setLevel(logging.WARNING)
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

# Suppress websockets deprecation warnings from uvicorn (not using WebSockets anyways)
warnings.filterwarnings("ignore", category=DeprecationWarning, module="websockets.legacy")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="uvicorn.protocols.websockets")

# Initialize FastMCP server
mcp = FastMCP("sdk-usage-kusto", stateless_http=True)

# Register tools using decorator syntax
@mcp.tool()
async def generate_kql_query_tool(user_query: str, execute: bool = False, export_to_file: str = None) -> str:
    """
    Purpose:
        Convert a natural-language question into a valid KQL query.

    When to Use:
        Use this tool when the user asks a question requiring the creation of a KQL query.

    Inputs:
      - user_query: The natural-language question to convert.
      - execute: If True, the model must run the generated query.
      - export_to_file: Optional CSV export path when executing the query.

    Model Behavior:
      - Call this tool to obtain schema and context.
      - Generate a valid KQL query using the returned schema.
      - If execute=True, immediately call execute_kusto_query_tool with
        the generated query and optional export_to_file.

    Limitations:
      - Do not call this tool when the user already supplies a complete KQL query.
      - Do not invent parameters that are not part of the input schema.
    """
    result = generate_kql_from_question(user_query)
    
    if execute:
        result += "\n\n" + "=" * 80
        result += "\nNOTE: execute=True was specified."
        result += "\nAfter generating the KQL query based on the schema above, "
        result += "you MUST call execute_kusto_query_tool() with the generated query to return results."
        if export_to_file:
            result += f"\nExport results to: {export_to_file}"
        result += "\n" + "=" * 80
    
    return result


@mcp.tool()
async def execute_kusto_query_tool(kusto_query: str, timeout: int = 3600, poll_interval: int = 30, export_to_file: str = None) -> str:
    """
    Purpose:
        Execute a KQL query and retrieve results from Azure SDK usage data.

    When to Use:
        Use this tool after you have generated a valid KQL query string (either from 
        generate_kql_query_tool or constructed manually following the schema).

    Inputs:
      - kusto_query: The complete KQL query string to execute
      - timeout: Maximum seconds to wait for completion (default: 3600)
      - poll_interval: Seconds between status checks (default: 30)
      - export_to_file: Optional CSV file path to save all results

    Output:
        Returns formatted query results including:
        - Row count summary
        - Data table (displays up to 100 rows)
        - Billing and runtime information
        
        Note: The response displays up to 100 rows. Only use export_to_file parameter 
        when the user explicitly requests to save results to a file, or when you need 
        to preserve all rows from large result sets.

    Limitations:
      - Do not call this tool without a valid KQL query string.
      - Query must follow the schema requirements (Unionizer table, TaskName filter, TIMESTAMP filter).
    """
    return await execute_kusto_query(kusto_query, timeout, poll_interval, export_to_file)


@mcp.tool()
async def get_kusto_helper_functions_tool() -> str:
    """
    Purpose:
        Retrieve KQL helper function definitions for advanced SDK usage analysis.

    When to Use:
        Call this tool when the user's query requires analyzing SDK-specific information:
        - SDK/tool identification (Python, Java, .NET, Terraform, etc.)
        - SDK version tracking (Track1 vs Track2)
        - Operating system detection (Windows, Linux, MacOS)
        - Resource type extraction from operation names
        - Programming language version parsing

    Output:
        Returns 5 complete KQL function definitions:
        - GetProduct(userAgent): Extract SDK/product name
        - GetTrackInfo(userAgent): Determine Track1 or Track2
        - GetOSInfo(userAgent): Extract operating system
        - GetResource(operationName): Extract resource type
        - GetLanguageVersion(userAgent, Product, Track): Extract language version

    Model Behavior:
      - Include these function definitions at the START of your KQL query
      - Place them BEFORE the main Unionizer query
      - Use `let FunctionName = ...` syntax for each function
      - Then extend your query results using these functions (e.g., | extend Product = GetProduct(userAgent))

    Limitations:
      - Only call this tool when SDK analysis is actually needed for the user's question.
      - Do not call this for simple queries that don't involve SDK/tool analysis.
    """
    return get_kusto_helper_functions()


def main():
    """Main entry point for the MCP server."""
    try:
        print("Starting MCP server...")
        mcp.run(transport="streamable-http")
    except Exception as e:
        print(f"Error while running MCP server: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
