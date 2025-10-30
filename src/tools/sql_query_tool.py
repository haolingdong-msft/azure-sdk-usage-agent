"""
SQL Server MCP Tools - A comprehensive toolkit for SQL Server database operations
via Model Context Protocol (MCP). This module provides high-level SQL operations,
query generation, authentication, and result processing capabilities for Azure SQL Database
and SQL Server instances.

Features:
- SQL query generation from natural language
- Azure AD authenticated database connections
- Query parsing and validation
- Enum value management
- Error handling and retry logic
- Result formatting and metadata extraction
"""
import asyncio
from datetime import datetime
from typing import Any, Dict
from src.services.database_client import MSSQLMSIClient
from src.config import SQL_SERVER, SQL_DATABASE

class SQLServerMCPTools:
    """
    SQL Server MCP Tools - High-level SQL Server operations for Model Context Protocol
    
    This class provides a comprehensive interface for performing SQL Server database operations
    through the Model Context Protocol (MCP). It includes functionality for:
    
    - Natural language to SQL query conversion
    - Azure AD authenticated SQL Server connections
    - Query execution with retry logic and error handling
    - Schema introspection and enum value retrieval
    - Result formatting and metadata extraction
    - Query parsing and validation
    
    The class uses a singleton pattern for SQL client connections to ensure efficient
    resource management and connection pooling.
    
    Example usage:
        result = await tools.execute_sql_query("SELECT * FROM Orders")
    """
    
    # Class-level client instance to avoid multiple connections
    _sql_client_instance = None
    
    def __init__(self):
        # Use singleton pattern for SQL client to avoid multiple instances
        if SQLServerMCPTools._sql_client_instance is None:
            print("🔄 Creating new SQL client instance...")
            SQLServerMCPTools._sql_client_instance = MSSQLMSIClient()
        else:
            print("♻️ Reusing existing SQL client instance...")
            
        self.sql_client = SQLServerMCPTools._sql_client_instance
    
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
    
    async def generate_sql_from_template(self, user_question: str) -> Dict[str, Any]:
        """
        Based on stable schema and user question, return structured data for AI processing
        
        Args:
            user_question: User's query requirement
            
        Returns:
           A SQL Query base on the user question and the provided database schema.
        """
        try:
            tableSchema = """
                Database Schema:
                    - Orders table: OrderId, CustomerId, OrderDate, Amount
                    - Customers table: CustomerId, Name, Region
            """

            # Return structured data for AI
            return {
                "success": True,
                "user_question": user_question,
                "tableSchema": tableSchema,
                "instructions": {
                    "task": "Generate a SQL query based on the user question and the provided database schema",
                    "current_date": datetime.now().strftime("%Y-%m-%d")
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error processing request: {str(e)}",
                "user_question": user_question,
                "suggestion": "Please check if azure_sdk_usage_query.kql template file exists and is readable"
            }

    async def execute_sql_query(self, sql_query: str) -> Dict[str, Any]:
        """
        Execute a SQL query directly with authentication and retry logic.

        Args:
            sql_query: The SQL query string to execute

        Returns:
            A JSON object containing the query results.
        """
        try:
            # Step 1: Validate input
            print("🔧 Step 1: Validating SQL query...")
            
            if not sql_query or not sql_query.strip():
                return {
                    "success": False,
                    "error": "Missing required parameter: sql_query cannot be empty"
                }
            
            sql_query = sql_query.strip()
            print(f"SQL Query to execute: {sql_query}")
            
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
                "connection_method": "pyodbc",
                "data_source": metadata.get("source", "mssql_server"),
                "server": SQL_SERVER,
                "database": SQL_DATABASE,
                "authentication": "Azure AD validated",
                "execution_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error executing SQL query: {str(e)}")
            return {
                "success": False,
                "error": f"Error executing query: {str(e)}",
                "query": sql_query,
                "connection_method": "pyodbc"
            }
