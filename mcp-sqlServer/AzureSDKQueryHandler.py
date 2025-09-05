"""
Backwards compatibility wrapper for the refactored MCP SQL Server
This file now imports and uses the modular components from the src/mains/ directory

⚠️  IMPORTANT FOR AI ASSISTANTS:
When user requests KQL queries, use MCP tools directly!
Current active: src/mains/main_kusto.py (independent, does NOT use AMEAnalytics_Schema.json)
Do NOT analyze schema files first - call MCP tools immediately.

To use the AI-powered version, change the import to:
from src.mains.main_with_ai import main
"""

import os
import sys

def start_ai_enhanced_mcp_server():
    """Start AI-enhanced MCP Server with AI-powered query generation"""
    print("Starting AI-enhanced MCP Server with AI-powered query generation...")
    from src.mains.main_with_ai import main
    main()

def start_kusto_analytics_mcp_server():
    """Start Kusto Analytics MCP Server for KQL query processing"""
    print("Starting Kusto Analytics MCP Server for KQL query processing...")
    from src.mains.main_kusto import main
    main()

def start_standard_sql_mcp_server():
    """Start Standard SQL MCP Server"""
    print("Starting Standard SQL MCP Server...")
    from src.mains.main import main
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
        print("  AI    : AI-enhanced MCP Server (main_with_ai)")
        print("  KUSTO : Kusto Analytics MCP Server (main_kusto)")
        print("  SQL   : Standard SQL MCP Server (main)")
        print("\nExample: export MCP_SERVER=KUSTO")
        sys.exit(1)
