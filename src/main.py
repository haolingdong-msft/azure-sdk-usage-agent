"""
Azure SDK Usage Data Query Server

This module provides table-specific SQL MCP tools for querying Azure SDK usage data.
Supports both SQL queries for structured data and KQL queries for broader telemetry analysis.

🔍 CRITICAL DATA SCOPE UNDERSTANDING:
- SQL Tools: Query pre-aggregated tables containing ONLY SDK request data
- KQL Tool: Query raw HttpIncomingRequests containing ALL ARM requests (SDK + non-SDK)

USAGE STRATEGY:
1. FIRST: Call analyzeUserIntent(user_question) to get tool recommendation
2. For SDK vs TOTAL ARM analysis → MUST use generateKQLFromTemplate (only tool with all data)
3. For SDK-only analysis → use generateSQLBy... tools (faster, structured)
4. For fallback scenarios → use generateKQLFromTemplate when SQL lacks required dimensions

CRITICAL DECISION KEYWORDS:
- "total ARM", "vs total", "SDK percentage", "non-SDK" → KQL REQUIRED
- "SDK adoption", "SDK comparison", "Track1 vs Track2" → SQL APPROPRIATE

SQL TOOLS: Best for SDK adoption, SDK comparisons, SDK performance within SDK ecosystem
KQL TOOL: Required for SDK vs total traffic, complete ARM telemetry, non-SDK data inclusion
"""
import sys
from src.config import MCP_PORT
from src.mcp_server import ServerConfigurator

def create_sdk_usage_mcp_server():
    """Create and configure the MCP server with table-specific SQL generation tools"""
    configurator = ServerConfigurator()
    return configurator.create_mcp_server(__file__)


def start_sdk_usage_query_server():
    """Main entry point for the table-specific SQL MCP server"""
    try:
        print("Starting Azure SDK Usage Data Query Server...")
        print(f"Server running on port {MCP_PORT}")
        
        # Initialize and run the server
        mcp = create_sdk_usage_mcp_server()
        mcp.run(transport="streamable-http")
        
    except Exception as e:
        print(f"Error while running Table-Specific SQL MCP server: {e}", file=sys.stderr)
