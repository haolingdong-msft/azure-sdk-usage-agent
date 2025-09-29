"""
Azure SDK Usage Data Query Server - Main Entry Point

This module serves as the main entry point for the Azure SDK usage data query server,
providing MCP (Model Context Protocol) based SQL/KQL query capabilities for SDK release data.

"""

def start_sdk_query_server():
    """Start Azure SDK usage data query MCP server"""
    print("Starting Azure SDK Usage Data Query Server...")
    from src.sdkDataQuery import start_sdk_usage_query_server
    start_sdk_usage_query_server()

if __name__ == "__main__":
    start_sdk_query_server()