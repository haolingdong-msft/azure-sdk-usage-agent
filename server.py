import warnings
import logging
import asyncio
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

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

# Initialize MCP server
server = Server("sdk-usage-kusto")


# ============================================================================
# TOOL DEFINITIONS
# ============================================================================

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return [
        Tool(
            name="generate_kql_query_tool",
            description="Convert a natural-language question into a valid KQL query for Azure SDK usage data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_query": {
                        "type": "string",
                        "description": "The natural-language question to convert into a KQL query",
                    },
                    "execute": {
                        "type": "boolean",
                        "description": "If True, the model must run the generated query",
                        "default": False,
                    },
                    "export_to_file": {
                        "type": "string",
                        "description": "Optional CSV export path when executing the query",
                    },
                },
                "required": ["user_query"],
            },
        ),
        Tool(
            name="execute_kusto_query_tool",
            description="Execute a KQL query and retrieve results from Azure SDK usage data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "kusto_query": {
                        "type": "string",
                        "description": "The complete KQL query string to execute",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Maximum seconds to wait for completion",
                        "default": 3600,
                    },
                    "poll_interval": {
                        "type": "integer",
                        "description": "Seconds between status checks",
                        "default": 30,
                    },
                    "export_to_file": {
                        "type": "string",
                        "description": "Optional CSV file path to save all results",
                    },
                },
                "required": ["kusto_query"],
            },
        ),
        Tool(
            name="get_kusto_helper_functions_tool",
            description="Retrieve KQL helper function definitions for advanced SDK usage analysis (SDK identification, version tracking, OS detection, etc.).",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls."""
    logger = logging.getLogger("sdk-usage-kusto")
    logger.info(f"Tool called: {name} with arguments: {arguments}")
    
    if name == "generate_kql_query_tool":
        user_query = arguments.get("user_query")
        execute = arguments.get("execute", False)
        export_to_file = arguments.get("export_to_file")
        
        result = generate_kql_from_question(user_query)
        
        if execute:
            result += "\n\n" + "=" * 80
            result += "\nNOTE: execute=True was specified."
            result += "\nAfter generating the KQL query based on the schema above, "
            result += "you MUST call execute_kusto_query_tool() with the generated query to return results."
            if export_to_file:
                result += f"\nExport results to: {export_to_file}"
            result += "\n" + "=" * 80
        
        return [TextContent(type="text", text=result)]
    
    elif name == "execute_kusto_query_tool":
        kusto_query = arguments.get("kusto_query")
        timeout = arguments.get("timeout", 3600)
        poll_interval = arguments.get("poll_interval", 30)
        export_to_file = arguments.get("export_to_file")
        
        result = await execute_kusto_query(kusto_query, timeout, poll_interval, export_to_file)
        return [TextContent(type="text", text=result)]
    
    elif name == "get_kusto_helper_functions_tool":
        result = get_kusto_helper_functions()
        return [TextContent(type="text", text=result)]
    
    else:
        raise ValueError(f"Unknown tool: {name}")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main():
    """Main entry point for the MCP server."""
    logger = logging.getLogger("sdk-usage-kusto")
    logger.info("Starting MCP STDIO Server...")
    
    async with stdio_server() as (read_stream, write_stream):
        logger.info("Server initialized, waiting for requests...")
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
