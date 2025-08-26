import os
import sys
import json
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp_port = int(os.environ.get("FUNCTIONS_CUSTOMHANDLER_PORT", 8080))
mcp = FastMCP("sqlQuery", stateless_http=True, port=mcp_port)

@mcp.tool()
async def testQuery(request: str) -> dict:
    """
    Test query function that doesn't require database connection.
    
    Args:
        request: A test query string
        
    Returns:
        A JSON object with test results
    """
    return {
        "success": True,
        "message": f"Test query received: {request}",
        "timestamp": "2025-08-27",
        "server_status": "running",
        "python_version": sys.version,
        "working_directory": os.getcwd()
    }

@mcp.tool()
async def listTables() -> dict:
    """
    Test function to list available tables without database connection.
    
    Returns:
        A JSON object containing mock table information.
    """
    try:
        # Load schema from fixture file
        schema_file = os.path.join(os.path.dirname(__file__), 'fixture', 'tables_and_columns.json')
        with open(schema_file, 'r') as f:
            schema_data = json.load(f)
        
        # Extract enabled tables
        enabled_tables = []
        for table in schema_data.get('Tables', []):
            if table.get('enabled', 'true') == 'true':
                enabled_tables.append({
                    "table_name": table['TableName'],
                    "description": table.get('Description', ''),
                    "column_count": len(table.get('Columns', []))
                })
        
        return {
            "success": True,
            "enabled_tables": enabled_tables,
            "total_count": len(enabled_tables),
            "note": "This is a test version without database connection"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error loading schema: {str(e)}"
        }

if __name__ == "__main__":
    try:
        print("Starting MCP server (test version)...")
        mcp.run(transport="streamable-http")
    except Exception as e:
        print(f"Error while running MCP server: {e}", file=sys.stderr)
