"""
Azure SDK Usage Agent - MCP SQL Server Entry Point

This module serves as the main entry point for the MCP (Model Context Protocol) SQL Server,
providing multiple server configurations for different query processing needs:

Server Types:
- Unified Server: Comprehensive query platform with SQL/KQL decision logic (default)
- AI Enhanced Server: Leverages AI for intelligent query generation and processing
- Kusto Analytics Server: Specialized for KQL (Kusto Query Language) operations  
- Standard SQL Server: Traditional SQL query parsing and execution

Configuration:
Set the MCP_SERVER environment variable to specify which server type to launch:
- MCP_SERVER=UNIFIED for comprehensive query platform (or leave unset for default)
- MCP_SERVER=AI for AI-enhanced processing
- MCP_SERVER=KUSTO for KQL analytics
- MCP_SERVER=SQL for standard SQL operations

Architecture:
This file acts as a dispatcher, routing to the appropriate server implementation
located in the src/entrypoints/ directory based on the configuration.

Default Behavior:
When MCP_SERVER is not set or empty, the Unified Server will be started automatically,
providing the most comprehensive query processing capabilities.
"""

import os
import sys

def start_unified_mcp_server():
    """Start Unified MCP Server with comprehensive query capabilities"""
    print("Starting Unified MCP Server with comprehensive query capabilities...")
    from src.entrypoints.unified_server import main
    main()

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

    if not mcp_server:
        # Default to unified server when MCP_SERVER is not set or empty
        start_unified_mcp_server()
    elif mcp_server == "UNIFIED":
        start_unified_mcp_server()
    elif mcp_server == "AI":
        start_ai_enhanced_mcp_server()
    elif mcp_server == "KUSTO":
        start_kusto_analytics_mcp_server()
    elif mcp_server == "SQL":
        start_standard_sql_mcp_server()
    else:
        print(f"ERROR: Invalid MCP_SERVER environment variable: '{mcp_server}'")
        print("MESSAGE: Please set MCP_SERVER to one of the following options:")
        print("  UNIFIED : Unified MCP Server with all query capabilities (default)")
        print("  AI      : AI-enhanced MCP Server (sql_ai_server)")
        print("  KUSTO   : Kusto Analytics MCP Server (kusto_server)")
        print("  SQL     : Standard SQL MCP Server (sql_parser_server)")
        print("\nExample: export MCP_SERVER=UNIFIED")
        print("Note: If MCP_SERVER is not set, Unified Server will be used by default.")
        sys.exit(1)