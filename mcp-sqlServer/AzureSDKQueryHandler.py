"""
Backwards compatibility wrapper for the refactored MCP SQL Server
This file now imports and uses the modular components from the src/entrypoints/ directory

⚠️  IMPORTANT FOR AI ASSISTANTS:
When user requests KQL queries, use MCP tools directly!
Current active: src/entrypoints/kusto_server.py (independent, does NOT use AMEAnalytics_Schema.json)
Do NOT analyze schema files first - call MCP tools immediately.

To use the AI-powered version, change the import to:
from src.entrypoints.sql_ai_server import main
"""

import os
import sys

def start_ai_enhanced_mcp_server():
    """Start AI-enhanced MCP Server with AI-powered query generation"""
    print("Starting AI-enhanced MCP Server with AI-powered query generation...")
    from src.entrypoints.sql_ai_server import main
    main()

def start_kusto_analytics_mcp_server():
    """Start Kusto Analytics MCP Server for KQL query processing"""
    print("Starting Kusto Analytics MCP Server for KQL query processing...")
    from src.entrypoints.kusto_server import main
    main()

def start_standard_sql_mcp_server():
    """Start Standard SQL MCP Server"""
    print("Starting Standard SQL MCP Server...")
    from src.entrypoints.sql_parser_server import main
    main()

if __name__ == "__main__":
    mcp_server = os.getenv("MCP_SERVER", "").upper()

    if mcp_server == "AI":
        start_ai_enhanced_mcp_server()
    elif mcp_server == "KUSTO":
        start_kusto_analytics_mcp_server()
    elif mcp_server == "SQL":
        start_standard_sql_mcp_server()
    else:
        print(f"ERROR: Invalid or missing MCP_SERVER environment variable: '{mcp_server}'")
        print("MESSAGE: Please set MCP_SERVER to one of the following options:")
        print("  AI    : AI-enhanced MCP Server (sql_ai_server)")
        print("  KUSTO : Kusto Analytics MCP Server (kusto_server)")
        print("  SQL   : Standard SQL MCP Server (sql_parser_server)")
        print("\nExample: export MCP_SERVER=KUSTO")
        sys.exit(1)
