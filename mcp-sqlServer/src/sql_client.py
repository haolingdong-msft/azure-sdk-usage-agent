"""
MS SQL Server Client using pyodbc with Managed Service Identity (MSI)
"""
import pyodbc
import os
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from typing import Any, Dict, List, Optional
from azure.identity import DefaultAzureCredential
from .config import (
    SQL_SERVER, SQL_DATABASE
)


class MSSQLMSIClient:
    """
    MS SQL Server Client using pyodbc with Managed Service Identity (MSI)
    
    This client provides passwordless connectivity to Azure SQL Database using pyodbc
    with Managed Service Identity authentication. This approach is more secure and
    eliminates the need to manage access tokens manually.
    
    Features:
    - Passwordless authentication using MSI
    - Automatic credential handling via DefaultAzureCredential
    - Connection pooling support
    - Proper error handling and resource cleanup
    """
    
    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.connection_string = self._build_msi_connection_string()
        self._executor = ThreadPoolExecutor(max_workers=2)
    
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
            # Create connection using MSI
            connection = pyodbc.connect(self.connection_string)
            elapsed_time = time.time() - start_time
            print(f"✅ Successfully connected to SQL Server using MSI (took {elapsed_time:.2f}s)")
            return connection
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"❌ Connection failed after {elapsed_time:.2f}s: {str(e)}")
            raise
    
    
    def _build_msi_connection_string(self) -> str:
        """
        Build ODBC connection string with MSI authentication
        
        This uses ActiveDirectoryMSI authentication which automatically handles
        both system-assigned and user-assigned managed identities.
        
        Returns:
            str: ODBC connection string for MSI authentication
        """
        # Check if AZURE_CLIENT_ID is set for user-assigned managed identity
        client_id = os.getenv('AZURE_CLIENT_ID')
        
        base_connection_string = (
            f"Driver={{ODBC Driver 18 for SQL Server}};"
            f"Server=tcp:{SQL_SERVER},1433;"
            f"Database={SQL_DATABASE};"
            f"Encrypt=yes;"
            f"TrustServerCertificate=no;"
            f"Connection Timeout=3;"
            f"Login Timeout=3;"
            f"Authentication=ActiveDirectoryMSI"
        )
        
        # Add client ID for user-assigned managed identity if specified
        if client_id:
            connection_string = f"{base_connection_string};UID={client_id}"
            print(f"🔑 Using user-assigned managed identity: {client_id}")
        else:
            connection_string = base_connection_string
            print("🔑 Using system-assigned managed identity")
            
        return connection_string
    
    async def _get_connection(self, timeout: int = 30) -> pyodbc.Connection:
        """
        Get or create a database connection with MSI authentication
        
        Args:
            timeout: Connection timeout in seconds
            
        Returns:
            pyodbc.Connection: Database connection
        """
        try:
            print("🔄 Starting connection process...")
            
            # Create a progress task to show connection is in progress
            progress_task = asyncio.create_task(self._show_connection_progress())
            
            try:
                # Run the blocking connection operation in a thread pool with timeout
                loop = asyncio.get_event_loop()
                connection_future = loop.run_in_executor(
                    self._executor, 
                    lambda: self._connect_sync(timeout)
                )
                
                # Wait for connection with timeout
                connection = await asyncio.wait_for(connection_future, timeout=timeout)
                
                # Cancel progress indicator
                progress_task.cancel()
                try:
                    await progress_task
                except asyncio.CancelledError:
                    pass
                
                return connection
                
            except asyncio.TimeoutError:
                # Cancel progress indicator
                progress_task.cancel()
                try:
                    await progress_task
                except asyncio.CancelledError:
                    pass
                
                error_msg = f"Connection timed out after {timeout} seconds"
                print(f"⏰ {error_msg}")
                raise Exception(error_msg)
                
        except pyodbc.Error as e:
            error_msg = f"MSI database connection failed: {str(e)}"
            print(f"💥 {error_msg}")
            # Provide helpful troubleshooting information
            print("🔍 Troubleshooting tips:")
            print("   - Ensure the managed identity is assigned to this resource")
            print("   - Verify the managed identity has appropriate SQL database permissions")
            print("   - Check if AZURE_CLIENT_ID is correctly set for user-assigned identity")
            print("   - Verify network connectivity to the SQL server")
            print("   - Check if the SQL server allows connections from this IP/region")
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Connection error: {str(e)}"
            print(f"💥 {error_msg}")
            raise Exception(error_msg)
    
    async def _show_connection_progress(self):
        """Show connection progress indicators"""
        try:
            dots = 0
            while True:
                dots = (dots + 1) % 4
                progress_indicator = "🔄 Connecting" + "." * dots + " " * (3 - dots)
                print(f"\r{progress_indicator}", end="", flush=True)
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            print("\r" + " " * 20 + "\r", end="", flush=True)  # Clear the progress line
            raise
    
    
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
        try:
            # Get database connection with timeout
            connection = await self._get_connection(timeout)
            
            # Execute query in thread pool to prevent blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self._executor, 
                self._execute_query_sync, 
                connection, 
                sql_query
            )
            
            return result
            
        except Exception as e:
            error_msg = f"Query execution error: {str(e)}"
            print(f"💥 {error_msg}")
            return {
                "columns": [],
                "rows": [],
                "row_count": 0,
                "status": "error", 
                "error": error_msg
            }
        finally:
            # Clean up connection
            if connection:
                try:
                    connection.close()
                    print("🔌 Database connection closed")
                except:
                    pass
    
    def _execute_query_sync(self, connection: pyodbc.Connection, sql_query: str) -> Dict[str, Any]:
        """
        Synchronous query execution to be run in thread pool
        
        Args:
            connection: Database connection
            sql_query: SQL query to execute
            
        Returns:
            Dict[str, Any]: Query results
        """
        try:
            # Create cursor and execute query
            cursor = connection.cursor()
            print("📡 Executing SQL query...")
            
            start_time = time.time()
            cursor.execute(sql_query)
            execution_time = time.time() - start_time
            
            # Get column information
            columns = [column[0] for column in cursor.description] if cursor.description else []
            
            # Fetch all rows
            rows = cursor.fetchall()
            
            # Convert rows to list of dictionaries
            result_rows = []
            for row in rows:
                row_dict = {}
                for i, value in enumerate(row):
                    column_name = columns[i] if i < len(columns) else f"column_{i}"
                    # Handle different data types
                    if hasattr(value, 'isoformat'):  # datetime objects
                        row_dict[column_name] = value.isoformat()
                    elif isinstance(value, bytes):  # binary data
                        row_dict[column_name] = value.decode('utf-8', errors='ignore')
                    else:
                        row_dict[column_name] = value
                result_rows.append(row_dict)

            result = {
                "columns": columns,
                "rows": result_rows,
                "row_count": len(result_rows),
                "status": "success",
                "execution_time": execution_time
            }
            
            print(f"✅ Query executed successfully. Returned {len(result_rows)} rows in {execution_time:.2f}s")
            return result
            
        except pyodbc.Error as e:
            error_msg = f"SQL execution failed: {str(e)}"
            print(f"💥 {error_msg}")
            return {
                "columns": [],
                "rows": [],
                "row_count": 0,
                "status": "error",
                "error": error_msg
            }
    
    def test_connection(self, timeout: int = 30) -> Dict[str, Any]:
        """
        Test the MSI database connection
        
        Args:
            timeout: Connection timeout in seconds
            
        Returns:
            Dict[str, Any]: Connection test result
        """
        import asyncio
        import sys
        
        async def _test():
            try:
                print(f"🧪 Testing connection with {timeout}s timeout...")
                start_time = time.time()
                connection = await self._get_connection(timeout)
                connection_time = time.time() - start_time
                connection.close()
                return {
                    "status": "success",
                    "message": f"MSI connection test successful (took {connection_time:.2f}s)",
                    "server": SQL_SERVER,
                    "database": SQL_DATABASE,
                    "authentication": "ActiveDirectoryMSI",
                    "connection_time": connection_time
                }
            except Exception as e:
                connection_time = time.time() - start_time
                return {
                    "status": "error", 
                    "message": f"MSI connection test failed after {connection_time:.2f}s: {str(e)}",
                    "server": SQL_SERVER,
                    "database": SQL_DATABASE,
                    "authentication": "ActiveDirectoryMSI",
                    "connection_time": connection_time
                }
        
        # Handle cases where event loop is already running
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
            
        if loop is not None:
            # If we're in an event loop, create a task
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, _test())
                return future.result()
        else:
            # If no event loop is running, use asyncio.run
            return asyncio.run(_test())
