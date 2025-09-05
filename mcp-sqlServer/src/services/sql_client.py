"""
MS SQL Server Client using pyodbc with Managed Service Identity (MSI)
"""
import pyodbc
import asyncio
import time
import struct
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional
from azure.identity import DefaultAzureCredential
from ..config.config import (
    SQL_SERVER, SQL_DATABASE
)


class MSSQLMSIClient:
    """
    MS SQL Server Client using pyodbc with Managed Service Identity (MSI)
    
    This client provides passwordless connectivity to Azure SQL Database using pyodbc
    with Managed Service Identity authentication through DefaultAzureCredential. 
    This approach is more secure and eliminates the need to manage passwords.
    
    Features:
    - Passwordless authentication using MSI via DefaultAzureCredential
    - Access token-based authentication for enhanced security
    - Dynamic connection timeout configuration
    - Proper error handling and resource cleanup
    - Async/await support with thread pool execution
    """
    
    def __init__(self):
        try:
            print("🚀 Initializing MSSQLMSIClient...")
            self.credential = DefaultAzureCredential()
            
            # Use single worker to avoid threading issues in Azure Functions
            # Azure Functions can have memory constraints and threading issues
            self._executor = ThreadPoolExecutor(
                max_workers=1,  # Conservative approach for Azure Functions
                thread_name_prefix="SQLClient"
            )
            self.sql_scope = "https://database.windows.net/.default"
            print("✅ MSSQLMSIClient initialized successfully")
            
        except Exception as e:
            print(f"💥 Error initializing MSSQLMSIClient: {e}")
            raise
    
    def __del__(self):
        """Cleanup resources when the object is destroyed"""
        print("🧹 Cleaning up MSSQLMSIClient resources...")
        try:
            if hasattr(self, '_executor') and self._executor:
                self._executor.shutdown(wait=True, timeout=5)
                print("✅ Thread pool executor shut down")
        except Exception as e:
            print(f"⚠️ Error during cleanup: {e}")
    
    def close(self):
        """Explicitly close the thread pool executor"""
        print("🔒 Explicitly closing MSSQLMSIClient...")
        try:
            if hasattr(self, '_executor') and self._executor:
                self._executor.shutdown(wait=True, timeout=10)
                print("✅ Thread pool executor closed successfully")
        except Exception as e:
            print(f"⚠️ Error closing thread pool: {e}")
            raise
    
    async def get_access_token(self, scope: str) -> str:
        """
        Get access token for the specified scope
        
        Args:
            scope: The OAuth scope to request token for
            
        Returns:
            str: Access token
        """
        try:
            loop = asyncio.get_event_loop()
            token = await loop.run_in_executor(
                self._executor,
                lambda: self.credential.get_token(scope)
            )
            return token.token
        except Exception as e:
            raise Exception(f"Failed to get access token: {str(e)}")
    
    def _connect_sync(self, timeout: int = 30) -> pyodbc.Connection:
        """
        Synchronous connection method to be run in thread pool
        
        Args:
            timeout: Connection timeout in seconds
            
        Returns:
            pyodbc.Connection: Database connection
        """
        print(f"🌐 Connecting to SQL Server: {SQL_SERVER}")
        print(f"🌐 Database: {SQL_DATABASE}")
        print("🔐 Authentication: Managed Service Identity (MSI)")
        print(f"⏱️  Connection timeout: {timeout} seconds")
        
        start_time = time.time()
        
        try:
            # Get access token using DefaultAzureCredential
            print("🔑 Acquiring access token using MSI...")
            token = self.credential.get_token("https://database.windows.net/.default")
            access_token = token.token
            print("✅ Access token acquired successfully")
            
            # Build connection string with access token
            connection_string = (
                f"Driver={{ODBC Driver 18 for SQL Server}};"
                f"Server=tcp:{SQL_SERVER},1433;"
                f"Database={SQL_DATABASE};"
                f"Encrypt=yes;"
                f"TrustServerCertificate=no;"
                f"Connection Timeout={timeout};"
            )
            
            print("🔑 Using system-assigned managed identity")
            
            # Create connection using access token (following app.py pattern)
            # Encode token as UTF-16-LE and pack it with struct
            token_bytes = access_token.encode("UTF-16-LE")
            token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)
            
            # SQL_COPT_SS_ACCESS_TOKEN = 1256 (SQL Server specific connection attribute)
            SQL_COPT_SS_ACCESS_TOKEN = 1256
            attrs_before = {
                SQL_COPT_SS_ACCESS_TOKEN: token_struct
            }
            
            connection = pyodbc.connect(connection_string, attrs_before=attrs_before)
            elapsed_time = time.time() - start_time
            print(f"✅ Successfully connected to SQL Server using MSI (took {elapsed_time:.2f}s)")
            return connection
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"❌ Connection failed after {elapsed_time:.2f}s: {str(e)}")
            raise

    async def get_connection(self, timeout: int = 30) -> pyodbc.Connection:
        """
        Get a database connection with MSI authentication
        
        Args:
            timeout: Connection timeout in seconds
            
        Returns:
            pyodbc.Connection: Database connection
        """
        try:
            # Run the blocking connection operation in a thread pool
            loop = asyncio.get_event_loop()
            connection = await loop.run_in_executor(
                self._executor, 
                lambda: self._connect_sync(timeout)
            )
            return connection
                
        except Exception as e:
            error_msg = f"Connection error: {str(e)}"
            print(f"💥 {error_msg}")
            raise Exception(error_msg)
    
    async def execute_query(self, sql_query: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Execute SQL query using pyodbc with MSI authentication
        
        Args:
            sql_query: SQL query to execute
            timeout: Connection timeout in seconds
            
        Returns:
            Dict[str, Any]: Query results with columns and rows
        """
        print(f"📊 Executing SQL query: {sql_query[:100]}{'...' if len(sql_query) > 100 else ''}")
        
        connection = None
        cursor = None
        
        try:
            # Validate input
            if not sql_query or not sql_query.strip():
                raise ValueError("SQL query cannot be empty")
            
            # Get database connection with timeout
            print("🔌 Establishing database connection...")
            connection = await self.get_connection(timeout)
            
            if connection is None:
                raise Exception("Failed to establish database connection")
            
            print("✅ Database connection established")
            
            # Execute query in thread pool to prevent blocking
            print("⚡ Executing query in thread pool...")
            loop = asyncio.get_event_loop()
            
            # Add a reasonable timeout for query execution
            try:
                result = await asyncio.wait_for(
                    loop.run_in_executor(
                        self._executor, 
                        self._execute_query_sync, 
                        connection, 
                        sql_query
                    ),
                    timeout=timeout * 2  # Query timeout is 2x connection timeout
                )
            except asyncio.TimeoutError:
                raise Exception(f"Query execution timed out after {timeout * 2} seconds")
            
            print("✅ Query execution completed")
            return result
            
        except Exception as e:
            error_msg = f"Query execution error: {str(e)}"
            print(f"💥 {error_msg}")
            
            # Return a consistent error response
            return {
                "columns": [],
                "rows": [],
                "row_count": 0,
                "status": "error", 
                "error": error_msg,
                "error_type": type(e).__name__
            }
        finally:
            # Clean up resources in proper order
            print("🧹 Cleaning up resources...")
            
            # Close cursor first if it exists
            if cursor:
                try:
                    cursor.close()
                    print("📋 Cursor closed")
                except Exception as e:
                    print(f"⚠️ Error closing cursor: {e}")
            
            # Then close connection
            if connection:
                try:
                    # Check if connection is still valid before closing
                    if hasattr(connection, 'close'):
                        connection.close()
                        print("🔌 Database connection closed")
                except Exception as e:
                    print(f"⚠️ Error closing connection: {e}")
            
            print("✅ Resource cleanup completed")
    
    def _execute_query_sync(self, connection: pyodbc.Connection, sql_query: str) -> Dict[str, Any]:
        """
        Synchronous query execution to be run in thread pool
        
        Args:
            connection: Database connection
            sql_query: SQL query to execute
            
        Returns:
            Dict[str, Any]: Query results
        """
        cursor = None
        
        try:
            # Validate connection
            if connection is None:
                raise Exception("Database connection is None")
            
            # Create cursor with error handling
            print("📋 Creating database cursor...")
            cursor = connection.cursor()
            
            if cursor is None:
                raise Exception("Failed to create database cursor")
            
            print("📡 Executing SQL query...")
            start_time = time.time()
            
            # Execute query with proper error handling
            cursor.execute(sql_query)
            execution_time = time.time() - start_time
            
            print(f"⚡ Query executed in {execution_time:.2f}s, fetching results...")
            
            # Get column information safely
            columns = []
            if cursor.description:
                columns = [column[0] for column in cursor.description]
                print(f"📊 Found {len(columns)} columns: {columns}")
            else:
                print("⚠️ No column description found (possibly non-SELECT query)")
            
            # Fetch all rows with memory consideration
            print("📥 Fetching query results...")
            rows = cursor.fetchall()
            row_count = len(rows)
            
            print(f"📊 Fetched {row_count} rows")
            
            # Check for large result sets
            if row_count > 10000:
                print(f"⚠️ Large result set detected ({row_count} rows). Processing in chunks...")
            
            # Convert rows to list of dictionaries with proper error handling
            result_rows = []
            for row_index, row in enumerate(rows):
                try:
                    row_dict = {}
                    for i, value in enumerate(row):
                        try:
                            column_name = columns[i] if i < len(columns) else f"column_{i}"
                            
                            # Handle different data types safely
                            if value is None:
                                row_dict[column_name] = None
                            elif hasattr(value, 'isoformat'):  # datetime objects
                                row_dict[column_name] = value.isoformat()
                            elif isinstance(value, bytes):  # binary data
                                try:
                                    row_dict[column_name] = value.decode('utf-8', errors='replace')
                                except Exception:
                                    row_dict[column_name] = str(value)
                            elif isinstance(value, (int, float, str, bool)):
                                row_dict[column_name] = value
                            else:
                                # Convert other types to string safely
                                row_dict[column_name] = str(value)
                                
                        except Exception as e:
                            print(f"⚠️ Error processing column {i} in row {row_index}: {e}")
                            row_dict[f"column_{i}"] = f"<Error: {str(e)}>"
                    
                    result_rows.append(row_dict)
                    
                    # Progress indication for large datasets
                    if row_count > 1000 and (row_index + 1) % 1000 == 0:
                        print(f"📊 Processed {row_index + 1}/{row_count} rows...")
                        
                except Exception as e:
                    print(f"⚠️ Error processing row {row_index}: {e}")
                    # Continue with next row instead of failing completely
                    continue

            result = {
                "columns": columns,
                "rows": result_rows,
                "row_count": len(result_rows),
                "status": "success",
                "execution_time": execution_time,
                "processed_rows": len(result_rows),
                "total_fetched_rows": row_count
            }
            
            print(f"✅ Query executed successfully. Processed {len(result_rows)}/{row_count} rows in {execution_time:.2f}s")
            return result
            
        except pyodbc.Error as e:
            error_msg = f"SQL execution failed: {str(e)}"
            print(f"💥 {error_msg}")
            return {
                "columns": [],
                "rows": [],
                "row_count": 0,
                "status": "error",
                "error": error_msg,
                "error_type": "pyodbc.Error"
            }
        except Exception as e:
            error_msg = f"Unexpected error during query execution: {str(e)}"
            print(f"💥 {error_msg}")
            return {
                "columns": [],
                "rows": [],
                "row_count": 0,
                "status": "error",
                "error": error_msg,
                "error_type": type(e).__name__
            }
        finally:
            # Clean up cursor
            if cursor:
                try:
                    cursor.close()
                    print("📋 Cursor closed successfully")
                except Exception as e:
                    print(f"⚠️ Error closing cursor: {e}")
