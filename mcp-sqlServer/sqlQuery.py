import os
import sys
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

from azure.identity import DefaultAzureCredential

# Initialize FastMCP server
mcp_port = int(os.environ.get("FUNCTIONS_CUSTOMHANDLER_PORT", 8080))
mcp = FastMCP("sqlQuery", stateless_http=True, port=mcp_port)

# Constants
server = os.getenv('SQL_SERVER', 'azuresdkbi-server.database.windows.net')
database = os.getenv('SQL_DATABASE', 'azuresdkbi') 
driver = '{ODBC Driver 17 for SQL Server}'

@mcp.tool()
async def sqlQuery(request):
    """
    Execute a SQL query on a specified SQL Server table.

    Args:
        tableName: Name of the table to query.
        columns: Comma-separated list of columns to select (e.g. "column1, column2").
        conditions: SQL WHERE clause with conditions (e.g. "column1 = 'value' AND column2 > 100").

    Returns:
        A JSON object containing the query results.
    """
    
    table_name = request.args.get("tableName")
    columns = request.args.get("columns")
    conditions = request.args.get("conditions") 

    print(f"Received request with tableName={table_name}, columns={columns}, conditions={conditions}")

    if not table_name or not columns or not conditions:
        return {"error": "Missing required parameters (tableName, columns, or conditions)"}

    query = f"SELECT {columns} FROM {table_name} WHERE {conditions}"

    credential = DefaultAzureCredential()
    token = credential.get_token("https://database.windows.net/.default")
    
    conn = pyodbc.connect(f"Driver={driver};Server={server};Database={database};Authentication=ActiveDirectoryMsi;", attrs={'AccessToken': token.token})
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    
    # 格式化查询结果
    result = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
    
    # 返回查询结果
    return {"data": result}


if __name__ == "__main__":
    try:
        # Initialize and run the server
        print("Starting MCP server...")
        mcp.run(transport="streamable-http")
    except Exception as e:
        print(f"Error while running MCP server: {e}", file=sys.stderr)
