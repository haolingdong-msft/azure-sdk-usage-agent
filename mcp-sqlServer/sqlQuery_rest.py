import os
import sys
import json
import asyncio
from typing import Any, Dict, List, Optional

import httpx
from mcp.server.fastmcp import FastMCP
from azure.identity import DefaultAzureCredential

# Initialize FastMCP server
mcp_port = int(os.environ.get("FUNCTIONS_CUSTOMHANDLER_PORT", 8080))
mcp = FastMCP("sqlQuery", stateless_http=True, port=mcp_port)

# Constants
server = os.getenv('SQL_SERVER', 'azuresdkbi-server.database.windows.net')
database = os.getenv('SQL_DATABASE', 'azuresdkbi')

class AzureSQLRestClient:
    """使用 Azure SQL Database REST API 连接数据库"""
    
    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.base_url = f"https://{server}/rest/v1"
        self._token = None
        self._token_expires = None
    
    async def _get_access_token(self):
        """获取Azure SQL的访问令牌"""
        try:
            token = self.credential.get_token("https://database.windows.net/.default")
            return token.token
        except Exception as e:
            raise Exception(f"Failed to get access token: {str(e)}")
    
    async def execute_query(self, sql_query: str) -> Dict[str, Any]:
        """执行SQL查询并返回结果"""
        try:
            token = await self._get_access_token()
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "query": sql_query,
                "database": database
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/query",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    raise Exception(f"SQL API request failed: {response.status_code} - {response.text}")
                    
        except Exception as e:
            raise Exception(f"Failed to execute query via REST API: {str(e)}")

# Global SQL client
sql_client = AzureSQLRestClient()

# Load table schema information (same as before)
def load_table_schema() -> Dict[str, Any]:
    """Load table schema from fixture file with enhanced structure support."""
    try:
        schema_file = os.path.join(os.path.dirname(__file__), 'fixture', 'tables_and_columns.json')
        with open(schema_file, 'r') as f:
            schema_data = json.load(f)
        
        # Convert to dict for easier lookup with enhanced metadata
        schema_dict = {}
        definitions = schema_data.get('definitions', {})
        
        for table in schema_data.get('Tables', []):
            table_name = table['TableName']
            enabled = table.get('enabled', 'true') == 'true'
            description = table.get('Description', '')
            
            columns = []
            column_metadata = {}
            
            for col in table.get('Columns', []):
                col_name = col['ColumnName']
                columns.append(col_name)
                
                # Extract column metadata from definitions
                ref = col.get('$ref', '').replace('#/definitions/', '')
                if ref in definitions:
                    def_info = definitions[ref]
                    column_metadata[col_name] = {
                        'title': def_info.get('title', col_name),
                        'description': def_info.get('description', ''),
                        'type': def_info.get('type', 'string'),
                        'enum': def_info.get('enum'),
                        'pattern': def_info.get('pattern'),
                        'format': def_info.get('format'),
                        'minimum': def_info.get('minimum')
                    }
            
            schema_dict[table_name.lower()] = {
                'name': table_name,
                'enabled': enabled,
                'description': description,
                'columns': columns,
                'column_metadata': column_metadata
            }
        
        return {
            'tables': schema_dict,
            'definitions': definitions
        }
    except Exception as e:
        print(f"Error loading table schema: {e}")
        return {'tables': {}, 'definitions': {}}

# Global schema cache
TABLE_SCHEMA = load_table_schema()

@mcp.tool()
async def sqlQueryREST(request: str) -> Dict[str, Any]:
    """
    Execute a SQL query using Azure SQL REST API based on a natural language question.

    Args:
        request: A natural language question about the data

    Returns:
        A JSON object containing the query results, generated SQL, or error information.
    """
    
    try:
        print(f"Received question: {request}")
        
        # 简化的查询解析（这里可以重用原来的解析逻辑）
        if "python-sdk" in request.lower() and "this month" in request.lower():
            sql_query = """
                SELECT Month, Product, RequestCount, SubscriptionCount 
                FROM AMEConciseSubReqCCIDCountByMonthProduct 
                WHERE Product = 'Python-SDK' AND Month LIKE '2025-08%' 
                ORDER BY RequestCount DESC
            """
        elif "list tables" in request.lower() or "available tables" in request.lower():
            # 返回schema信息而不是查询数据库
            enabled_tables = [
                {
                    "table_name": info['name'],
                    "description": info['description'],
                    "enabled": info['enabled']
                }
                for info in TABLE_SCHEMA['tables'].values() 
                if info['enabled']
            ]
            return {
                "success": True,
                "message": "Available tables (from schema)",
                "data": enabled_tables,
                "row_count": len(enabled_tables)
            }
        else:
            return {
                "error": "Query not supported in REST mode. Try 'Show Python-SDK usage this month' or 'List available tables'"
            }
        
        print(f"Generated SQL: {sql_query}")
        
        # 执行查询 (注意：Azure SQL 可能没有直接的REST API)
        # 这里我们模拟一个响应
        mock_result = {
            "columns": ["Month", "Product", "RequestCount", "SubscriptionCount"],
            "rows": [
                ["2025-08-01", "Python-SDK", 15420, 892],
                ["2025-08-15", "Python-SDK", 12850, 756]
            ]
        }
        
        # 格式化结果
        result_data = []
        for row in mock_result["rows"]:
            row_dict = {}
            for i, col in enumerate(mock_result["columns"]):
                row_dict[col] = row[i]
            result_data.append(row_dict)
        
        return {
            "success": True,
            "query": sql_query,
            "data": result_data,
            "row_count": len(result_data),
            "method": "REST API (Mock)",
            "note": "This is a mock response. Real implementation would use Azure SQL REST API."
        }
        
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        return {
            "error": f"Error processing your question: {str(e)}",
            "suggestion": "Try asking: 'Show Python-SDK usage this month' or 'List available tables'"
        }

@mcp.tool()
async def testConnection() -> Dict[str, Any]:
    """
    Test Azure AD authentication without connecting to database.
    
    Returns:
        A JSON object containing authentication test results.
    """
    try:
        credential = DefaultAzureCredential()
        token = credential.get_token("https://database.windows.net/.default")
        
        return {
            "success": True,
            "message": "Azure AD authentication successful",
            "token_type": "Bearer",
            "token_length": len(token.token),
            "expires_on": token.expires_on,
            "note": "Token can be used for Azure SQL authentication"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Azure AD authentication failed: {str(e)}",
            "suggestion": "Check Azure credentials and permissions"
        }

if __name__ == "__main__":
    try:
        print("Starting MCP server with REST API support...")
        mcp.run(transport="streamable-http")
    except Exception as e:
        print(f"Error while running MCP server: {e}", file=sys.stderr)
