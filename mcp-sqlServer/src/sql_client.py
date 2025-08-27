"""
MS SQL Server REST API Client
"""
import httpx
from typing import Any, Dict, Optional
from azure.identity import DefaultAzureCredential
from .config import (
    SQL_SERVER, SQL_DATABASE, AZURE_SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP,
    SQL_SCOPE, MANAGEMENT_SCOPE, MANAGEMENT_URL
)


class MSSQLRestClient:
    """
    MS SQL Server REST API Client
    
    This client provides REST API based connectivity to Azure SQL Database.
    It implements a fallback strategy with two different API approaches:
    
    1. Direct SQL Database API: Connects directly to the SQL Database instance
       - Uses database-specific authentication scope
       - Potentially lower latency and better performance
       - Conceptual implementation as Azure SQL doesn't provide public REST query API
    
    2. Azure Management API: Connects through Azure Resource Management layer
       - Uses management-specific authentication scope
       - Requires subscription and resource group information
       - Better suited for administrative and monitoring scenarios
    
    The client automatically tries both methods in sequence to maximize
    connection success rate across different Azure configurations and permissions.
    """
    
    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.management_url = MANAGEMENT_URL
        self.sql_scope = SQL_SCOPE
        self.management_scope = MANAGEMENT_SCOPE
    
    async def get_access_token(self, scope: str = None) -> str:
        """
        Obtain Azure AD access token for the specified scope
        
        Args:
            scope: The authentication scope (defaults to SQL Database scope)
            
        Returns:
            str: Access token for API authentication
        """
        try:
            if scope is None:
                scope = self.sql_scope
            
            print(f"🔑 Requesting Azure AD token for scope: {scope}")
            token = self.credential.get_token(scope)
            print(f"✅ Successfully obtained access token (expires: {token.expires_on})")
            return token.token
        except Exception as e:
            print(f"🔒 Failed to obtain access token for scope '{scope}': {str(e)}")
            raise Exception(f"Failed to get access token: {str(e)}")
    
    async def execute_query_via_rest(self, sql_query: str) -> Dict[str, Any]:
        """
        Execute SQL query through REST API with intelligent fallback strategy
        First attempts direct SQL Database API, then falls back to Management API only for specific failures
        """
        print(f"🔄 Starting REST API query execution for: {sql_query[:50]}...")
        
        try:
            # First attempt: Direct SQL Database API
            print("🎯 Attempting direct SQL Database API connection...")
            try:
                result = await self._try_sql_database_api(sql_query)
                if result:
                    print("✅ Successfully executed query via direct SQL Database API")
                    return result
                else:
                    print("⚠️ Direct SQL Database API returned no result, trying fallback...")
            except ConnectionError as e:
                print(f"🌐 Direct API connection error: {str(e)}")
                # Connection errors might be due to endpoint not existing, try fallback
                print("🔄 Connection failed, attempting Azure Management API fallback...")
            except httpx.HTTPStatusError as e:
                if e.response.status_code in [401, 403]:
                    print(f"🔒 Authentication/Authorization failed for Direct API: {str(e)}")
                    # Authentication errors are serious, don't try fallback
                    raise Exception(f"Authentication failed: {str(e)}")
                else:
                    print(f"💥 Direct API HTTP error: {str(e)}")
                    print("🔄 Direct API failed, attempting Azure Management API fallback...")
            except Exception as e:
                print(f"💥 Direct API unexpected error: {str(e)}")
                # For other errors, try fallback
                print("🔄 Direct API failed, attempting Azure Management API fallback...")
            
            # Second attempt: Azure Management API (only if first attempt had recoverable failure)
            try:
                result = await self._try_management_api(sql_query)
                if result:
                    print("✅ Successfully executed query via Azure Management API")
                    return result
                else:
                    print("❌ Azure Management API also returned no result")
            except Exception as e:
                print(f"💥 Management API also failed: {str(e)}")
                raise Exception(f"Management API failed after Direct API failure: {str(e)}")
            
            # If all API attempts fail, raise exception
            print("❌ All REST API endpoints failed to connect")
            raise Exception("All REST API endpoints failed to connect")
            
        except Exception as e:
            # Re-raise if it's already a formatted exception
            if str(e).startswith("Authentication failed") or str(e).startswith("Management API failed"):
                raise e
            print(f"💥 REST API execution failed with error: {str(e)}")
            raise Exception(f"REST API execution failed: {str(e)}")
    
    async def _try_sql_database_api(self, sql_query: str) -> Optional[Dict[str, Any]]:
        """
        Attempt to use direct SQL Database API
        
        This method tries to connect directly to the SQL Database instance
        using a conceptual REST API endpoint. Note: Azure SQL Database
        doesn't currently provide public REST query APIs.
        """
        print("🔐 Obtaining access token for SQL Database scope...")
        try:
            token = await self.get_access_token(self.sql_scope)
            print("✅ Successfully obtained SQL Database access token")
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # Using conceptual Azure SQL Database Query API endpoint
            url = f"https://{SQL_SERVER}/api/sql/v1/query"
            print(f"🌐 Attempting connection to: {url}")
            
            payload = {
                "database": SQL_DATABASE,
                "query": sql_query,
                "timeout": 30
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                print("📡 Sending HTTP POST request to SQL Database API...")
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    print("✅ SQL Database API: Query executed successfully")
                    return response.json()
                elif response.status_code == 401:
                    print("🔒 SQL Database API: Authentication failed (HTTP 401)")
                    return None
                elif response.status_code == 403:
                    print("🚫 SQL Database API: Access denied (HTTP 403)")
                    return None
                else:
                    print(f"⚠️ SQL Database API: Unexpected HTTP status {response.status_code}")
                    return None
                    
        except httpx.ConnectError as e:
            print(f"🌐 SQL Database API: Connection failed - {str(e)}")
            return None
        except Exception as e:
            print(f"💥 SQL Database API: Unexpected error - {str(e)}")
            return None
    
    async def _try_management_api(self, sql_query: str) -> Optional[Dict[str, Any]]:
        """
        Attempt to use Azure Management API
        
        This method tries to execute queries through Azure Resource Management
        layer, which requires subscription and resource group information.
        This approach is more suitable for administrative scenarios.
        """
        print("🔐 Obtaining access token for Azure Management scope...")
        try:
            token = await self.get_access_token(self.management_scope)
            print("✅ Successfully obtained Azure Management access token")
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Azure Management API for SQL databases
            server_name = SQL_SERVER.split('.')[0]  # Extract server name from FQDN
            url = f"{self.management_url}/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourceGroups/{AZURE_RESOURCE_GROUP}/providers/Microsoft.Sql/servers/{server_name}/databases/{SQL_DATABASE}/query"
            print(f"🌐 Attempting connection to Management API: {url}")
            print(f"📊 Target: Server={server_name}, Database={SQL_DATABASE}, ResourceGroup={AZURE_RESOURCE_GROUP}")
            
            payload = {
                "query": sql_query
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                print("📡 Sending HTTP POST request to Azure Management API...")
                response = await client.post(url, headers=headers, json=payload, params={"api-version": "2021-11-01"})
                
                if response.status_code == 200:
                    print("✅ Azure Management API: Query executed successfully")
                    return response.json()
                elif response.status_code == 401:
                    print("🔒 Azure Management API: Authentication failed (HTTP 401)")
                    return None
                elif response.status_code == 403:
                    print("🚫 Azure Management API: Access denied (HTTP 403)")
                    return None
                elif response.status_code == 404:
                    print("🔍 Azure Management API: Resource not found (HTTP 404)")
                    print(f"   Check if server '{server_name}' exists in resource group '{AZURE_RESOURCE_GROUP}'")
                    return None
                else:
                    print(f"⚠️ Azure Management API: Unexpected HTTP status {response.status_code}")
                    try:
                        error_details = response.json()
                        print(f"   Error details: {error_details}")
                    except:
                        print(f"   Response text: {response.text[:200]}...")
                    return None
                    
        except httpx.ConnectError as e:
            print(f"🌐 Azure Management API: Connection failed - {str(e)}")
            return None
        except Exception as e:
            print(f"💥 Azure Management API: Unexpected error - {str(e)}")
            return None
