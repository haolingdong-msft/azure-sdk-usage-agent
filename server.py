import sys
import warnings
import logging

from mcp.server.fastmcp import FastMCP

from src.tools import execute_kusto_query, query_kusto_with_natural_language

# Reduce MCP SDK, uvicorn, and httpx logging verbosity
logging.getLogger("mcp").setLevel(logging.WARNING)
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

# Suppress websockets deprecation warnings from uvicorn (not using WebSockets anyways)
warnings.filterwarnings("ignore", category=DeprecationWarning, module="websockets.legacy")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="uvicorn.protocols.websockets")

# Initialize FastMCP server
mcp = FastMCP("kusto", stateless_http=True)

# Register tools using decorator syntax
@mcp.tool()
async def query_kusto_with_natural_language_tool(user_query: str, database: str = None, timeout: int = 3600, poll_interval: int = 30) -> str:
    """Execute a Kusto query using natural language."""
    return await query_kusto_with_natural_language(user_query, database, timeout, poll_interval)

@mcp.tool()
async def execute_kusto_query_tool(kusto_query: str, timeout: int = 3600, poll_interval: int = 30, export_to_file: str = None) -> str:
    """Execute a Kusto query via Azure Data Factory pipeline.
    
    Args:
        kusto_query: The Kusto query to execute
        timeout: Maximum wait time in seconds (default: 3600)
        poll_interval: Status check interval in seconds (default: 30)
        export_to_file: Optional file path to export full results in CSV format
    """
    return await execute_kusto_query(kusto_query, timeout, poll_interval, export_to_file)

def main():
    """Main entry point for the MCP server."""
    try:
        print("Starting MCP server...")
        mcp.run(transport="streamable-http")
    except Exception as e:
        print(f"Error while running MCP server: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
