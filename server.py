import sys
import warnings
import logging
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

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

# Register tools
mcp.tool()(query_kusto_with_natural_language)
mcp.tool()(execute_kusto_query)

def main():
    """Main entry point for the MCP server."""
    try:
        print("Starting MCP server...")
        mcp.run(transport="streamable-http")
    except Exception as e:
        print(f"Error while running MCP server: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
