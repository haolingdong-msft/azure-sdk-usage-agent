"""
MCP Tools implementation for SQL Server operations
"""
import asyncio
from typing import Any, Dict, List
from .sql_client import MSSQLMSIClient
from ..data.schema_loader import SchemaLoader
from ..parsers.query_parser import QueryParser
from ..config.config import SQL_SERVER, SQL_DATABASE

class MCPTools:
    """MCP Tools for SQL Server operations"""
    
    # Class-level client instance to avoid multiple connections
    _sql_client_instance = None
    
    def __init__(self, schema_loader: SchemaLoader):
        # Use singleton pattern for SQL client to avoid multiple instances
        if MCPTools._sql_client_instance is None:
            print("🔄 Creating new SQL client instance...")
            MCPTools._sql_client_instance = MSSQLMSIClient()
        else:
            print("♻️ Reusing existing SQL client instance...")
            
        self.sql_client = MCPTools._sql_client_instance
        self.schema_loader = schema_loader
        self.query_parser = QueryParser(schema_loader)
    
    @classmethod
    def cleanup_sql_client(cls):
        """Clean up the shared SQL client instance"""
        if cls._sql_client_instance:
            print("🧹 Cleaning up shared SQL client instance...")
            try:
                cls._sql_client_instance.close()
                cls._sql_client_instance = None
                print("✅ SQL client instance cleaned up")
            except Exception as e:
                print(f"⚠️ Error cleaning up SQL client: {e}")
    
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
        Execute a SQL query using parsed components.

        Args:
            table_name: The name of the table to query
            columns: List of column names to select
            where_clause: SQL WHERE conditions (optional)
            order_clause: SQL ORDER BY clause (optional)
            limit_clause: SQL LIMIT/TOP clause (optional)

        Returns:
            A JSON object containing the query results.
        """
        try:
            # Step 1: Build SQL query from components
            print("🔧 Step 1: Building SQL query from components...")
            
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
            
            # Step 2: Execute the query with retry logic
            print("🚀 Step 2: Executing SQL query with retry logic...")
            
            max_retries = 3
            retry_delay = 1  # seconds
            
            for attempt in range(max_retries):
                try:
                    print(f"🔄 Attempt {attempt + 1}/{max_retries}")
                    query_result = await self.sql_client.execute_query(sql_query)
                    
                    # If successful, break out of retry loop
                    if query_result.get("status") != "error":
                        print(f"✅ Query executed successfully on attempt {attempt + 1}")
                        break
                    else:
                        # If it's an error, check if it's retryable
                        error_msg = query_result.get("error", "").lower()
                        if any(retryable_error in error_msg for retryable_error in [
                            "timeout", "connection", "network", "transient", "temporary"
                        ]):
                            if attempt < max_retries - 1:
                                print(f"⚠️ Retryable error on attempt {attempt + 1}: {query_result.get('error')}")
                                print(f"⏳ Waiting {retry_delay} seconds before retry...")
                                await asyncio.sleep(retry_delay)
                                retry_delay *= 2  # Exponential backoff
                                continue
                        
                        # If not retryable or last attempt, return the error
                        print(f"💥 Non-retryable error or final attempt: {query_result.get('error')}")
                        break
                        
                except Exception as api_error:
                    error_str = str(api_error).lower()
                    is_retryable = any(retryable_error in error_str for retryable_error in [
                        "timeout", "connection", "network", "transient", "temporary", "reset"
                    ])
                    
                    if is_retryable and attempt < max_retries - 1:
                        print(f"⚠️ Retryable exception on attempt {attempt + 1}: {api_error}")
                        print(f"⏳ Waiting {retry_delay} seconds before retry...")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    else:
                        print(f"💥 Non-retryable exception or final attempt: {api_error}")
                        return {
                            "success": False,
                            "error": f"Failed to execute query via pyodbc after {max_retries} attempts: {str(api_error)}",
                            "query": sql_query,
                            "connection_method": "pyodbc",
                            "attempts": attempt + 1,
                            "troubleshooting": [
                                "Check network connectivity to Azure SQL Database",
                                "Ensure ODBC Driver 18 for SQL Server is installed",
                                "Verify your account has proper database permissions",
                                "Check if the database server is accessible",
                                "Verify firewall rules allow your connection"
                            ]
                        }
            
            # Step 3: Check query execution status and format results
            if query_result.get("status") == "error":
                return {
                    "success": False,
                    "error": f"SQL execution failed: {query_result.get('error', 'Unknown error')}",
                    "query": sql_query,
                    "connection_method": "pyodbc"
                }
            
            # New sql_client returns rows as list of dictionaries already
            result_data = query_result.get("rows", [])
            
            metadata = query_result.get("metadata", {})
            
            return {
                "success": True,
                "query": sql_query,
                "data": result_data,
                "row_count": len(result_data),
                "table_used": table_name,
                "connection_method": "pyodbc",
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
                "connection_method": "pyodbc"
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
                        "connection_method": "pyodbc"
                    }
            
            # Check if it's a field without enum restrictions
            if field_lower in open_fields:
                return {
                    "success": True,
                    "field_name": field_name,
                    "message": f"No enum restriction for {field_name}",
                    "description": open_fields[field_lower],
                    "note": "This field accepts any valid value from the database",
                    "connection_method": "pyodbc"
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
                        "connection_method": "pyodbc"
                    }
            
            # Combine available fields
            all_available_fields = list(enum_mappings.keys()) + list(open_fields.keys())
            
            return {
                "error": f"No enum information found for field '{field_name}'",
                "available_fields": all_available_fields,
                "note": "Fields like 'provider', 'resource', and 'apiversion' no longer have enum restrictions",
                "connection_method": "pyodbc"
            }
            
        except Exception as e:
            return {"error": f"Error retrieving enum values: {str(e)}"}

    async def ai_query_helper(self, user_question: str) -> Dict[str, Any]:
        """
        Helper function for AI agents to generate correct column names, table names, and conditions
        based on user questions and available database schema.

        Args:
            user_question: A natural language question about the data

        Returns:
            A JSON object containing:
            - available_tables: List of all available tables with descriptions
            - suggested_table: Most relevant table for the question  
            - available_columns: All columns for the suggested table
            - column_metadata: Detailed information about each column
            - enum_values: Valid values for enum columns
            - example_conditions: Example WHERE clause conditions
            - example_columns: Suggested columns based on question intent
        """
        try:
            print(f"AI Query Helper analyzing: {user_question}")
            
            # Get all available tables
            enabled_tables = self.schema_loader.get_enabled_tables()
            
            # Find the most relevant table using existing logic
            suggested_table_name = self.query_parser.find_table_by_name(user_question)
            
            if not suggested_table_name and enabled_tables:
                # Fallback to first available table
                suggested_table_name = list(enabled_tables.values())[0].name
            
            # Prepare response structure
            result = {
                "success": True,
                "user_question": user_question,
                "available_tables": [],
                "suggested_table": None,
                "available_columns": [],
                "column_metadata": {},
                "enum_values": {},
                "example_conditions": [],
                "example_columns": []
            }
            
            # Add all available tables info
            for table_key, table_info in enabled_tables.items():
                result["available_tables"].append({
                    "name": table_info.name,
                    "description": table_info.description,
                    "key": table_key
                })
            
            # Add detailed info for suggested table
            if suggested_table_name:
                table_info = self.schema_loader.get_table_info(suggested_table_name)
                if table_info:
                    result["suggested_table"] = {
                        "name": table_info.name,
                        "description": table_info.description
                    }
                    
                    result["available_columns"] = table_info.columns
                    result["column_metadata"] = table_info.column_metadata
                    
                    # Get enum values for columns that have them
                    for column in table_info.columns:
                        if column in table_info.column_metadata:
                            meta = table_info.column_metadata[column]
                            if meta.get('type') == 'enum':
                                enum_name = meta.get('enum_name', column)
                                enum_values = self.schema_loader.get_enum_values(enum_name)
                                if enum_values:
                                    result["enum_values"][column] = enum_values
                    
                    # Generate example conditions and suggested columns based on question
                    query_lower = user_question.lower()
                    
                    # Suggest columns based on question intent
                    if any(word in query_lower for word in ['count', 'number', 'requests']):
                        if 'RequestCount' in table_info.columns:
                            result["example_columns"].append('RequestCount')
                    
                    if any(word in query_lower for word in ['product', 'tool', 'sdk']):
                        if 'Product' in table_info.columns:
                            result["example_columns"].append('Product')
                    
                    if any(word in query_lower for word in ['customer', 'user']):
                        if 'Customer' in table_info.columns:
                            result["example_columns"].append('Customer')
                    
                    if any(word in query_lower for word in ['month', 'time', 'date', 'when']):
                        if 'Month' in table_info.columns:
                            result["example_columns"].append('Month')
                    
                    # If no specific columns identified, suggest key columns
                    if not result["example_columns"]:
                        # Add common important columns
                        for col in ['Customer', 'Product', 'RequestCount', 'Month']:
                            if col in table_info.columns:
                                result["example_columns"].append(col)
                    
                    # Generate example conditions
                    if 'this month' in query_lower and 'Month' in table_info.columns:
                        result["example_conditions"].append("Month LIKE '2025-08%'")
                    
                    if any(word in query_lower for word in ['top', 'highest', 'most']) and 'RequestCount' in table_info.columns:
                        result["example_conditions"].append("RequestCount > 100")
                    
                    if any(word in query_lower for word in ['recent', 'latest']) and 'Month' in table_info.columns:
                        result["example_conditions"].append("Month >= '2025-01'")
                    
                    # Add enum-based example conditions
                    for column, enum_values in result["enum_values"].items():
                        if enum_values and len(enum_values) > 0:
                            result["example_conditions"].append(f"{column} = '{enum_values[0]}'")
                            if len(enum_values) > 1:
                                result["example_conditions"].append(f"{column} IN ('{enum_values[0]}', '{enum_values[1]}')")
            
            return result
            
        except Exception as e:
            print(f"Error in AI query helper: {str(e)}")
            return {
                "success": False,
                "error": f"Error in AI helper: {str(e)}",
                "user_question": user_question
            }
