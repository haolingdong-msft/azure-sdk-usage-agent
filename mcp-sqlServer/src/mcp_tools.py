"""
MCP Tools implementation for SQL Server operations
"""
from typing import Any, Dict, List
from .sql_client import MSSQLRestClient
from .schema_loader import SchemaLoader
from .query_parser import QueryParser
from .config import SQL_SERVER, SQL_DATABASE, AZURE_SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP


class MCPTools:
    """MCP Tools for SQL Server operations"""
    
    def __init__(self, schema_loader: SchemaLoader):
        self.sql_client = MSSQLRestClient()
        self.schema_loader = schema_loader
        self.query_parser = QueryParser(schema_loader)
    
    async def parse_user_query(self, user_question: str) -> Dict[str, Any]:
        """
        Parse a natural language question and extract table names, column names, and conditions.

        Args:
            user_question: A natural language question about the data

        Returns:
            A JSON object containing the parsed query components: table name, columns, conditions, ordering, and limit.
        """
        try:
            print(f"Parsing user question: {user_question}")
            
            # Parse the user question using existing query parser
            query_info = self.query_parser.parse_user_query(user_question)
            
            if 'error' in query_info:
                return {
                    "success": False,
                    "error": query_info['error'],
                    "suggestions": [
                        "Try asking about products, or request counts",
                        "Include specific dates like '2024-01' or time periods",
                        "Mention specific products like 'Python-SDK' or 'Java Fluent Premium'",
                        "Ask for top/bottom N results",
                        "Filter by providers like 'Microsoft.Compute' or OS like 'Windows'"
                    ]
                }
            
            return {
                "success": True,
                "table_name": query_info['table_name'],
                "columns": query_info['columns'],
                "where_clause": query_info['where_clause'] if query_info['where_clause'] != "1=1" else "",
                "order_clause": query_info['order_clause'] if query_info['order_clause'] else "",
                "limit_clause": query_info['limit_clause'] if query_info['limit_clause'] else "",
                "original_question": user_question
            }
            
        except Exception as e:
            print(f"Error parsing query: {str(e)}")
            return {
                "success": False,
                "error": f"Error parsing your question: {str(e)}",
                "suggestion": "Try asking questions like: 'Show me top 10 customers', 'What products were used this month?', 'Which customers have high request counts?'"
            }

    async def execute_sql_with_auth(self, table_name: str, columns: list, where_clause: str = "", order_clause: str = "", limit_clause: str = "") -> Dict[str, Any]:
        """
        Execute a SQL query using parsed components with Azure AD authentication validation.

        Args:
            table_name: The name of the table to query
            columns: List of column names to select
            where_clause: SQL WHERE conditions (optional)
            order_clause: SQL ORDER BY clause (optional)
            limit_clause: SQL LIMIT/TOP clause (optional)

        Returns:
            A JSON object containing the query results, or error information if authentication fails.
        """
        try:
            # Step 1: Validate Azure AD authentication first
            print("🔐 Step 1: Validating Azure AD authentication...")
            auth_result = await self.validate_azure_auth()
            
            if not auth_result.get('success', False):
                print("❌ Azure AD authentication failed")
                return {
                    "success": False,
                    "error": "Azure AD authentication failed",
                    "auth_error": auth_result.get('error', 'Unknown authentication error'),
                    "troubleshooting": auth_result.get('troubleshooting', [])
                }
            
            print("✅ Azure AD authentication successful")
            
            # Step 2: Build SQL query from components
            print("🔧 Step 2: Building SQL query from components...")
            
            # Validate inputs
            if not table_name or not columns:
                return {
                    "success": False,
                    "error": "Missing required parameters: table_name and columns are required"
                }
            
            # Build columns string
            if isinstance(columns, list):
                columns_str = ', '.join(columns) if columns else '*'
            else:
                columns_str = str(columns)
            
            # Build SQL query
            sql_parts = []
            if limit_clause:
                sql_parts.append(f"SELECT {limit_clause} {columns_str}")
            else:
                sql_parts.append(f"SELECT {columns_str}")
            
            sql_parts.append(f"FROM {table_name}")
            
            if where_clause and where_clause.strip():
                sql_parts.append(f"WHERE {where_clause}")
            
            if order_clause and order_clause.strip():
                sql_parts.append(order_clause)
            
            sql_query = ' '.join(sql_parts)
            print(f"Generated SQL: {sql_query}")
            
            # Step 3: Execute the query
            print("🚀 Step 3: Executing SQL query...")
            try:
                query_result = await self.sql_client.execute_query_via_rest(sql_query)
            except Exception as api_error:
                return {
                    "success": False,
                    "error": f"Failed to execute query via REST API: {str(api_error)}",
                    "query": sql_query,
                    "connection_method": "REST API",
                    "troubleshooting": [
                        "Check network connectivity to Azure SQL Database",
                        "Verify subscription ID and resource group settings",
                        "Ensure your account has proper database permissions"
                    ]
                }
            
            # Step 4: Format query results
            result_data = []
            
            for row in query_result.get("rows", []):
                row_dict = {}
                for i, value in enumerate(row):
                    column_name = query_result.get("columns", [])[i] if i < len(query_result.get("columns", [])) else f"column_{i}"
                    # Handle different data types
                    if value is None:
                        row_dict[column_name] = None
                    elif isinstance(value, (int, float, str, bool)):
                        row_dict[column_name] = value
                    else:
                        row_dict[column_name] = str(value)
                result_data.append(row_dict)
            
            metadata = query_result.get("metadata", {})
            
            return {
                "success": True,
                "query": sql_query,
                "data": result_data,
                "row_count": len(result_data),
                "table_used": table_name,
                "connection_method": "REST API",
                "data_source": metadata.get("source", "mssql_server"),
                "server": SQL_SERVER,
                "database": SQL_DATABASE,
                "authentication": "Azure AD validated",
                "query_components": {
                    "table": table_name,
                    "columns": columns,
                    "where": where_clause if where_clause else "None",
                    "order": order_clause if order_clause else "None",
                    "limit": limit_clause if limit_clause else "None"
                }
            }
            
        except Exception as e:
            print(f"Error executing SQL with auth: {str(e)}")
            return {
                "success": False,
                "error": f"Error executing query: {str(e)}",
                "connection_method": "REST API"
            }

    async def list_tables(self) -> Dict[str, Any]:
        """
        List only enabled tables and their columns that can be queried via REST API for MS SQL Server.
        
        Returns:
            A JSON object containing only enabled tables, their column information, and metadata.
        """
        try:
            # Get only enabled tables
            enabled_tables_dict = self.schema_loader.get_enabled_tables()
            tables_info = []
            
            for table_key, table_info in enabled_tables_dict.items():
                column_details = []
                column_metadata = table_info.column_metadata
                
                for col in table_info.columns:
                    col_detail = {'name': col}
                    if col in column_metadata:
                        meta = column_metadata[col]
                        col_detail.update({
                            'title': meta.get('title', col),
                            'description': meta.get('description', ''),
                            'type': meta.get('type', 'string'),
                            'enum': meta.get('enum')
                        })
                    column_details.append(col_detail)
                
                tables_info.append({
                    "table_name": table_info.name,
                    "enabled": table_info.enabled,
                    "description": table_info.description,
                    "columns": column_details,
                    "column_count": len(table_info.columns)
                })
            
            return {
                "success": True,
                "tables": tables_info,
                "total_tables": len(tables_info),
                "available_products": self.schema_loader.get_enum_values('Product'),
                "available_track_info": self.schema_loader.get_enum_values('TrackInfo'),
                "available_http_methods": self.schema_loader.get_enum_values('HttpMethod'),
                "available_os": self.schema_loader.get_enum_values('OS'),
                "note": "Provider, Resource, and ApiVersion fields no longer have enum restrictions and accept any valid database values",
                "connection_method": "REST API",
                "data_source": "MS SQL Server Schema Cache"
            }
        except Exception as e:
            return {"error": f"Error retrieving table information: {str(e)}"}

    async def validate_azure_auth(self) -> Dict[str, Any]:
        """
        Validate Azure AD authentication for MS SQL Server using REST approach.
        
        Returns:
            A JSON object containing authentication test results.
        """
        try:
            # Test SQL database token
            sql_token = await self.sql_client.get_access_token(self.sql_client.sql_scope)
            
            # Test management API token
            mgmt_token = await self.sql_client.get_access_token(self.sql_client.management_scope)
            
            return {
                "success": True,
                "message": "Azure AD authentication successful for MS SQL Server REST API",
                "server": SQL_SERVER,
                "database": SQL_DATABASE,
                "subscription_id": AZURE_SUBSCRIPTION_ID,
                "resource_group": AZURE_RESOURCE_GROUP,
                "sql_token_prefix": sql_token[:30] + "...",
                "sql_token_length": len(sql_token),
                "mgmt_token_prefix": mgmt_token[:30] + "...",
                "mgmt_token_length": len(mgmt_token),
                "authentication_method": "DefaultAzureCredential",
                "sql_scope": self.sql_client.sql_scope,
                "management_scope": self.sql_client.management_scope,
                "connection_method": "REST API"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Azure AD authentication failed: {str(e)}",
                "troubleshooting": [
                    "Ensure you're logged in with 'az login'",
                    "Check if your account has access to the MS SQL Server database",
                    "Verify the SQL server and database names are correct",
                    "Make sure Azure AD authentication is enabled on the SQL server",
                    "Check subscription ID and resource group settings"
                ],
                "connection_method": "REST API"
            }

    async def execute_custom_sql(self, sql_query: str) -> Dict[str, Any]:
        """
        Execute a custom SQL query directly via REST API for MS SQL Server (for advanced users).
        
        Args:
            sql_query: A valid SQL SELECT statement to execute.
            
        Returns:
            A JSON object containing the query results.
        """
        try:
            # Basic SQL injection protection
            sql_lower = sql_query.lower().strip()
            
            # Only allow SELECT statements
            if not sql_lower.startswith('select'):
                return {"error": "Only SELECT queries are allowed"}
            
            # Prevent dangerous operations
            dangerous_keywords = ['drop', 'delete', 'insert', 'update', 'create', 'alter', 'truncate', 'exec', 'execute']
            if any(keyword in sql_lower for keyword in dangerous_keywords):
                return {"error": "Query contains prohibited operations"}
            
            print(f"Executing custom SQL via REST: {sql_query}")
            
            # Execute via REST API
            try:
                query_result = await self.sql_client.execute_query_via_rest(sql_query)
            except Exception as api_error:
                return {
                    "error": f"Failed to execute custom SQL via REST API: {str(api_error)}",
                    "query": sql_query,
                    "connection_method": "REST API",
                    "troubleshooting": [
                        "Check Azure AD authentication with validateAzureAuthMSSQL",
                        "Verify SQL server and database names are correct",
                        "Ensure your account has access to the SQL database",
                        "Check network connectivity to Azure SQL Database"
                    ]
                }
            
            # Format results
            result_data = []
            
            for row in query_result.get("rows", []):
                row_dict = {}
                for i, value in enumerate(row):
                    column_name = query_result.get("columns", [])[i] if i < len(query_result.get("columns", [])) else f"column_{i}"
                    if value is None:
                        row_dict[column_name] = None
                    elif isinstance(value, (int, float, str, bool)):
                        row_dict[column_name] = value
                    else:
                        row_dict[column_name] = str(value)
                result_data.append(row_dict)
            
            metadata = query_result.get("metadata", {})
            
            return {
                "success": True,
                "query": sql_query,
                "data": result_data,
                "row_count": len(result_data),
                "connection_method": "REST API",
                "data_source": metadata.get("source", "mssql_server"),
                "query_type": metadata.get("query_type", "custom")
            }
            
        except Exception as e:
            return {
                "error": f"Error executing custom SQL via REST: {str(e)}",
                "connection_method": "REST API"
            }

    async def get_enum_values(self, field_name: str) -> Dict[str, Any]:
        """
        Get available enum values for a specific field to help with query construction for MS SQL Server.
        
        Args:
            field_name: The name of the field to get enum values for (e.g., 'Product', 'TrackInfo', 'Provider')
            
        Returns:
            A JSON object containing the available enum values for the specified field.
        """
        try:
            enum_mappings = {
                'product': 'Product',
                'trackinfo': 'TrackInfo',
                'track': 'TrackInfo',
                'httpmethod': 'HttpMethod',
                'method': 'HttpMethod',
                'os': 'OS',
                'operatingsystem': 'OS'
            }
            
            # Fields that no longer have enum restrictions
            open_fields = {
                'provider': "Azure resource provider names (e.g., Microsoft.Compute, Microsoft.Storage, etc.)",
                'resource': "Azure resource types (e.g., virtualMachines, storageAccounts, etc.)",
                'apiversion': "Azure API versions (e.g., 2021-04-01, 2020-12-01, etc.)"
            }
            
            field_lower = field_name.lower()
            
            # Check if it's a field with enum values
            if field_lower in enum_mappings:
                enum_name = enum_mappings[field_lower]
                enum_values = self.schema_loader.get_enum_values(enum_name)
                if enum_values:  # Only return if there are actual enum values
                    return {
                        "success": True,
                        "field_name": field_name,
                        "enum_values": enum_values,
                        "count": len(enum_values),
                        "connection_method": "REST API"
                    }
            
            # Check if it's a field without enum restrictions
            if field_lower in open_fields:
                return {
                    "success": True,
                    "field_name": field_name,
                    "message": f"No enum restriction for {field_name}",
                    "description": open_fields[field_lower],
                    "note": "This field accepts any valid value from the database",
                    "connection_method": "REST API"
                }
            
            # If exact match not found, search in definitions
            schema = self.schema_loader.load_table_schema()
            definitions = schema.get('definitions', {})
            for def_name, def_info in definitions.items():
                if def_name.lower() == field_lower and 'enum' in def_info:
                    return {
                        "success": True,
                        "field_name": def_name,
                        "enum_values": def_info['enum'],
                        "count": len(def_info['enum']),
                        "description": def_info.get('description', ''),
                        "connection_method": "REST API"
                    }
            
            # Combine available fields
            all_available_fields = list(enum_mappings.keys()) + list(open_fields.keys())
            
            return {
                "error": f"No enum information found for field '{field_name}'",
                "available_fields": all_available_fields,
                "note": "Fields like 'provider', 'resource', and 'apiversion' no longer have enum restrictions",
                "connection_method": "REST API"
            }
            
        except Exception as e:
            return {"error": f"Error retrieving enum values: {str(e)}"}

    async def validate_query(self, user_question: str) -> Dict[str, Any]:
        """
        Validate a user question and show what SQL would be generated without executing it for MS SQL Server.
        
        Args:
            user_question: The natural language question to validate
            
        Returns:
            A JSON object containing the validation results and planned SQL query.
        """
        try:
            # Parse the user question
            query_info = self.query_parser.parse_user_query(user_question)
            
            if 'error' in query_info:
                return {
                    "valid": False,
                    "error": query_info['error'],
                    "suggestions": [
                        "Try asking about products, customers, or request counts",
                        "Include specific dates like '2024-01' or time periods",
                        "Mention specific products like 'Python-SDK' or 'Java Fluent Premium'",
                        "Ask for top/bottom N results",
                        "Filter by providers like 'Microsoft.Compute' or OS like 'Windows'"
                    ],
                    "connection_method": "REST API"
                }
            
            # Build the SQL query (same logic as execute_sql_query but don't execute)
            columns_str = ', '.join(query_info['columns'])
            
            sql_parts = []
            if query_info['limit_clause']:
                sql_parts.append(f"SELECT {query_info['limit_clause']} {columns_str}")
            else:
                sql_parts.append(f"SELECT {columns_str}")
            
            sql_parts.append(f"FROM {query_info['table_name']}")
            
            if query_info['where_clause'] != "1=1":
                sql_parts.append(f"WHERE {query_info['where_clause']}")
            
            if query_info['order_clause']:
                sql_parts.append(query_info['order_clause'])
            
            sql_query = ' '.join(sql_parts)
            
            return {
                "valid": True,
                "generated_sql": sql_query,
                "table_used": query_info['table_name'],
                "columns_selected": query_info['columns'],
                "filters_applied": query_info['where_clause'] if query_info['where_clause'] != "1=1" else "None",
                "ordering": query_info['order_clause'] if query_info['order_clause'] else "None",
                "limit": query_info['limit_clause'] if query_info['limit_clause'] else "None",
                "connection_method": "REST API"
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Error validating query: {str(e)}",
                "connection_method": "REST API"
            }
