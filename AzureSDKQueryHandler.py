"""
Azure SDK Usage Agent - MCP SQL Server Entry Point

This module serves as the main entry point for the MCP (Model Context Protocol) SQL Server,
providing a unified query platform with SQL/KQL capabilities.

"""

def start_SdkDataQuery_mcp_server():
    """Start SdkDataQuery MCP Server with comprehensive query capabilities"""
    print("Starting SdkDataQuery MCP Server...")
    from src.SdkDataQuery import main
    main()

if __name__ == "__main__":
    start_SdkDataQuery_mcp_server()