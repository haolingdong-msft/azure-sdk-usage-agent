import os
import sys
import json
import re
from typing import Any, Dict, List, Optional

import httpx
from mcp.server.fastmcp import FastMCP
from azure.identity import DefaultAzureCredential

# Initialize FastMCP server
mcp_port = int(os.environ.get("FUNCTIONS_CUSTOMHANDLER_PORT", 8080))
mcp = FastMCP("mssqlQuery", stateless_http=True, port=mcp_port)

# Constants
server = os.getenv('SQL_SERVER', 'azuresdkbi-server.database.windows.net')
database = os.getenv('SQL_DATABASE', 'azuresdkbi')
subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID', 'your-subscription-id')
resource_group = os.getenv('AZURE_RESOURCE_GROUP', 'your-resource-group')

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
        self.management_url = "https://management.azure.com"
        self.sql_scope = "https://database.windows.net/.default"
        self.management_scope = "https://management.azure.com/.default"
    
    async def get_access_token(self, scope: str = None):
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
                print("�🔄 Direct API failed, attempting Azure Management API fallback...")
            
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
            url = f"https://{server}/api/sql/v1/query"
            print(f"🌐 Attempting connection to: {url}")
            
            payload = {
                "database": database,
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
            server_name = server.split('.')[0]  # Extract server name from FQDN
            url = f"{self.management_url}/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Sql/servers/{server_name}/databases/{database}/query"
            print(f"🌐 Attempting connection to Management API: {url}")
            print(f"📊 Target: Server={server_name}, Database={database}, ResourceGroup={resource_group}")
            
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
                    print(f"   Check if server '{server_name}' exists in resource group '{resource_group}'")
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

# Global SQL client
sql_client = MSSQLRestClient()

# Load table schema information
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

# Extract enum values for enhanced query parsing
PRODUCT_ENUM = TABLE_SCHEMA['definitions'].get('Product', {}).get('enum', [])
TRACK_ENUM = TABLE_SCHEMA['definitions'].get('TrackInfo', {}).get('enum', [])
HTTP_METHOD_ENUM = TABLE_SCHEMA['definitions'].get('HttpMethod', {}).get('enum', [])
OS_ENUM = TABLE_SCHEMA['definitions'].get('OS', {}).get('enum', [])

def find_table_by_name(query_text: str) -> Optional[str]:
    """Find the most likely table name from user query with enhanced matching."""
    query_lower = query_text.lower()
    
    # Get enabled tables only
    enabled_tables = {k: v for k, v in TABLE_SCHEMA['tables'].items() if v['enabled']}
    
    # Direct table name matches
    for table_key, table_info in enabled_tables.items():
        if table_key in query_lower or table_info['name'].lower() in query_lower:
            return table_info['name']
    
    # Enhanced keyword-based matching with scoring
    table_scores = {}
    
    for table_key, table_info in enabled_tables.items():
        score = 0
        table_name = table_info['name'].lower()
        description = table_info['description'].lower()
        
        # Score based on table name components
        if 'product' in query_lower and 'product' in table_name:
            score += 2
        if 'customer' in query_lower and 'customer' in table_name:
            score += 2
        if 'subscription' in query_lower and 'subscription' in table_name:
            score += 2
        if 'go' in query_lower and 'gosdk' in table_name:
            score += 3
        if 'request' in query_lower and ('req' in table_name or 'request' in description):
            score += 1
        if 'count' in query_lower and 'count' in table_name:
            score += 1
        if 'track' in query_lower and 'track' in table_name:
            score += 1
        if 'api' in query_lower and 'api' in table_name:
            score += 1
        if 'version' in query_lower and 'version' in table_name:
            score += 1
        if 'language' in query_lower and 'language' in table_name:
            score += 1
        if 'os' in query_lower and 'os' in table_name:
            score += 1
        if 'provider' in query_lower and 'provider' in table_name:
            score += 1
        
        # Score based on column availability
        columns = table_info['columns']
        if 'provider' in query_lower and 'Provider' in columns:
            score += 1
        if 'resource' in query_lower and 'Resource' in columns:
            score += 1
        if 'http' in query_lower and 'HttpMethod' in columns:
            score += 1
        if 'method' in query_lower and 'HttpMethod' in columns:
            score += 1
        if 'os' in query_lower and 'OS' in columns:
            score += 1
        
        if score > 0:
            table_scores[table_info['name']] = score
    
    # Return the highest scoring table
    if table_scores:
        return max(table_scores.items(), key=lambda x: x[1])[0]
    
    # Fallback to first enabled table
    if enabled_tables:
        return list(enabled_tables.values())[0]['name']
    
    return None

def extract_columns_from_query(query_text: str, table_name: str) -> List[str]:
    """Extract relevant columns based on user query and enhanced table schema."""
    if not table_name or table_name.lower() not in TABLE_SCHEMA['tables']:
        return ['*']
    
    table_info = TABLE_SCHEMA['tables'][table_name.lower()]
    available_columns = table_info['columns']
    column_metadata = table_info.get('column_metadata', {})
    query_lower = query_text.lower()
    
    # Check for specific column mentions
    mentioned_columns = []
    for col in available_columns:
        col_lower = col.lower()
        # Check column name and aliases
        if col_lower in query_lower:
            mentioned_columns.append(col)
        # Check column title/description for better matching
        elif col in column_metadata:
            meta = column_metadata[col]
            title_lower = meta.get('title', '').lower()
            desc_lower = meta.get('description', '').lower()
            if title_lower in query_lower or any(word in desc_lower for word in query_lower.split()):
                mentioned_columns.append(col)
    
    # Enhanced column selection based on query intent
    if not mentioned_columns:
        intent_columns = []
        
        # Product-related queries
        if any(word in query_lower for word in ['product', 'sdk', 'tool']):
            if 'Product' in available_columns:
                intent_columns.append('Product')
        
        # Track-related queries
        if any(word in query_lower for word in ['track', 'version']):
            if 'TrackInfo' in available_columns:
                intent_columns.append('TrackInfo')
        
        # Provider/Resource queries
        if any(word in query_lower for word in ['provider', 'service']):
            if 'Provider' in available_columns:
                intent_columns.append('Provider')
        if any(word in query_lower for word in ['resource', 'type']):
            if 'Resource' in available_columns:
                intent_columns.append('Resource')
        
        # HTTP method queries
        if any(word in query_lower for word in ['method', 'http', 'get', 'post', 'put', 'delete']):
            if 'HttpMethod' in available_columns:
                intent_columns.append('HttpMethod')
        
        # OS queries
        if any(word in query_lower for word in ['os', 'operating', 'system', 'windows', 'linux', 'mac']):
            if 'OS' in available_columns:
                intent_columns.append('OS')
        
        # Always include key columns for context
        key_columns = ['Month', 'RequestCount', 'SubscriptionCount']
        for col in key_columns:
            if col in available_columns and col not in intent_columns:
                intent_columns.append(col)
        
        if intent_columns:
            return intent_columns
        else:
            # Return most important columns
            priority_columns = ['Month', 'Product', 'RequestCount', 'SubscriptionCount', 'TrackInfo']
            result = []
            for col in priority_columns:
                if col in available_columns:
                    result.append(col)
            return result[:5]  # Limit to 5 columns
    
    return mentioned_columns

def build_where_clause(query_text: str, table_name: str) -> str:
    """Build WHERE clause based on user query intent with enhanced enum support."""
    if not table_name or table_name.lower() not in TABLE_SCHEMA['tables']:
        return "1=1"  # Return all records if no specific filtering
    
    table_info = TABLE_SCHEMA['tables'][table_name.lower()]
    available_columns = table_info['columns']
    query_lower = query_text.lower()
    conditions = []
    
    # Month filtering (improved pattern matching)
    month_patterns = re.findall(r'(\d{4}-\d{2}-\d{2}|\d{4}-\d{2}|\d{4}/\d{2})', query_lower)
    if month_patterns and 'Month' in available_columns:
        for month in month_patterns:
            if len(month) == 7:  # YYYY-MM format
                conditions.append(f"Month LIKE '{month}%'")
            else:
                conditions.append(f"Month = '{month}'")
    
    # This month filtering
    if 'this month' in query_lower and 'Month' in available_columns:
        conditions.append("Month LIKE '2025-08%'")
    
    # Product filtering with enum support
    if 'Product' in available_columns:
        for product in PRODUCT_ENUM:
            if product.lower() in query_lower:
                conditions.append(f"Product = '{product}'")
                break
    
    # Track filtering with enum support
    if 'TrackInfo' in available_columns:
        for track in TRACK_ENUM:
            if track.lower() in query_lower:
                conditions.append(f"TrackInfo = '{track}'")
                break
        # Also check for track1/track2 patterns
        if 'track 1' in query_lower or 'track1' in query_lower:
            conditions.append("TrackInfo = 'Track1'")
        elif 'track 2' in query_lower or 'track2' in query_lower:
            conditions.append("TrackInfo = 'Track2'")
    
    # Provider filtering - now uses text matching instead of enum
    if 'Provider' in available_columns:
        # Look for common provider patterns in the query
        provider_patterns = [
            r'microsoft\.(\w+)',  # Microsoft.Compute, Microsoft.Storage, etc.
            r'microsoft\s+(\w+)',  # Microsoft Compute, Microsoft Storage, etc.
            r'compute|storage|network|web|sql|keyvault|resources|container|documentdb|authorization'
        ]
        
        for pattern in provider_patterns:
            matches = re.findall(pattern, query_lower)
            if matches:
                if pattern.startswith('microsoft'):
                    # Construct Microsoft.ServiceName format
                    service_name = matches[0].capitalize()
                    conditions.append(f"Provider LIKE '%Microsoft.{service_name}%'")
                else:
                    # General service name matching
                    conditions.append(f"Provider LIKE '%{matches[0]}%'")
                break
    
    # Resource filtering - now uses text matching instead of enum
    if 'Resource' in available_columns:
        # Look for common resource type patterns
        resource_keywords = [
            'virtualmachines', 'vm', 'virtual machines',
            'storageaccounts', 'storage accounts', 'storage',
            'virtualnetworks', 'vnet', 'virtual networks', 'network',
            'webapps', 'web apps', 'webapp',
            'sqlservers', 'sql servers', 'sql',
            'keyvaults', 'key vaults', 'keyvault',
            'resourcegroups', 'resource groups',
            'kubernetesclusters', 'kubernetes', 'aks',
            'cosmosdbaccounts', 'cosmos', 'cosmosdb',
            'roleassignments', 'role assignments'
        ]
        
        for keyword in resource_keywords:
            if keyword in query_lower:
                # Convert keyword to likely resource name format
                if keyword in ['vm', 'virtual machines']:
                    conditions.append("Resource LIKE '%virtualMachines%'")
                elif keyword in ['storage accounts', 'storage']:
                    conditions.append("Resource LIKE '%storageAccounts%'")
                elif keyword in ['vnet', 'virtual networks', 'network']:
                    conditions.append("Resource LIKE '%virtualNetworks%'")
                elif keyword in ['web apps', 'webapp']:
                    conditions.append("Resource LIKE '%webApps%'")
                elif keyword in ['sql servers', 'sql']:
                    conditions.append("Resource LIKE '%sqlServers%'")
                elif keyword in ['key vaults', 'keyvault']:
                    conditions.append("Resource LIKE '%keyVaults%'")
                elif keyword in ['resource groups']:
                    conditions.append("Resource LIKE '%resourceGroups%'")
                elif keyword in ['kubernetes', 'aks']:
                    conditions.append("Resource LIKE '%kubernetesClusters%'")
                elif keyword in ['cosmos', 'cosmosdb']:
                    conditions.append("Resource LIKE '%cosmosDbAccounts%'")
                elif keyword in ['role assignments']:
                    conditions.append("Resource LIKE '%roleAssignments%'")
                else:
                    # Direct match for exact resource names
                    conditions.append(f"Resource LIKE '%{keyword}%'")
                break
    
    # HTTP Method filtering with enum support
    if 'HttpMethod' in available_columns:
        for method in HTTP_METHOD_ENUM:
            if method.lower() in query_lower:
                conditions.append(f"HttpMethod = '{method}'")
                break
    
    # OS filtering with enum support
    if 'OS' in available_columns:
        for os_name in OS_ENUM:
            if os_name.lower() in query_lower:
                conditions.append(f"OS = '{os_name}'")
                break
    
    # Request/Subscription count filtering
    count_columns = ['RequestCount', 'SubscriptionCount', 'RequestCounts', 'CCIDCount']
    for count_col in count_columns:
        if count_col in available_columns:
            # Extract numeric comparisons
            patterns = [
                (r'(?:more than|greater than|above)\s+(\d+)', lambda x: f"{count_col} > {x}"),
                (r'(?:less than|below|under)\s+(\d+)', lambda x: f"{count_col} < {x}"),
                (r'(?:at least|minimum of)\s+(\d+)', lambda x: f"{count_col} >= {x}"),
                (r'(?:at most|maximum of)\s+(\d+)', lambda x: f"{count_col} <= {x}"),
                (r'(?:exactly|equal to)\s+(\d+)', lambda x: f"{count_col} = {x}"),
            ]
            
            for pattern, formatter in patterns:
                match = re.search(pattern, query_lower)
                if match:
                    conditions.append(formatter(match.group(1)))
                    break
    
    return ' AND '.join(conditions) if conditions else "1=1"

def parse_user_query(user_question: str) -> Dict[str, Any]:
    """Parse user question into SQL query components."""
    table_name = find_table_by_name(user_question)
    
    if not table_name:
        return {
            'error': 'Could not identify a relevant table from your question. Available topics: customer data, product usage, subscription information.'
        }
    
    columns = extract_columns_from_query(user_question, table_name)
    where_clause = build_where_clause(user_question, table_name)
    
    # Handle TOP N queries
    limit_clause = ""
    top_match = re.search(r'top\s+(\d+)', user_question.lower())
    if top_match:
        limit_clause = f"TOP {top_match.group(1)}"
    
    # Handle ORDER BY (enhanced)
    order_clause = ""
    order_column = None
    order_direction = "DESC"
    
    # Determine sort column
    if any(word in user_question.lower() for word in ['count', 'request', 'usage']):
        if 'RequestCount' in TABLE_SCHEMA['tables'][table_name.lower()]['columns']:
            order_column = 'RequestCount'
        elif 'SubscriptionCount' in TABLE_SCHEMA['tables'][table_name.lower()]['columns']:
            order_column = 'SubscriptionCount'
    elif 'date' in user_question.lower() or 'time' in user_question.lower():
        if 'Month' in TABLE_SCHEMA['tables'][table_name.lower()]['columns']:
            order_column = 'Month'
        elif 'RequestsDate' in TABLE_SCHEMA['tables'][table_name.lower()]['columns']:
            order_column = 'RequestsDate'
    
    # Determine sort direction
    if any(word in user_question.lower() for word in ['lowest', 'least', 'minimum', 'asc', 'ascending', 'oldest']):
        order_direction = "ASC"
    elif any(word in user_question.lower() for word in ['highest', 'most', 'maximum', 'desc', 'descending', 'latest', 'newest']):
        order_direction = "DESC"
    
    if order_column:
        order_clause = f"ORDER BY {order_column} {order_direction}"
    
    return {
        'table_name': table_name,
        'columns': columns,
        'where_clause': where_clause,
        'limit_clause': limit_clause,
        'order_clause': order_clause
    }

# MCP Tools Implementation
@mcp.tool()
async def mssqlQuery(request: str) -> Dict[str, Any]:
    """
    Execute a SQL query based on a natural language question using REST API for MS SQL Server.

    Args:
        request: A natural language question about the data (e.g., "Show me the top 10 customers by request count", 
                "What products were used in 2024-01?", "Which customers have more than 1000 requests?")

    Returns:
        A JSON object containing the query results, generated SQL, or error information.
    """
    
    try:
        print(f"Received question: {request}")
        
        # Step 1: Validate and generate SQL query first (without connecting to database)
        print("🔍 Step 1: Validating query and generating SQL...")
        validation_result = await validateQueryMSSQL(request)
        
        if not validation_result.get('valid', False):
            print("❌ Query validation failed")
            return {
                "error": "Query validation failed",
                "validation_error": validation_result.get('error', 'Unknown validation error'),
                "suggestions": validation_result.get('suggestions', []),
                "connection_method": "REST API"
            }
        
        sql_query = validation_result['generated_sql']
        query_info = validation_result
        
        print(f"✅ SQL validation successful: {sql_query}")
        
        # Step 2: Now that SQL is validated, attempt database connection and execution
        print("🔗 Step 2: Connecting to database and executing query...")
        
        # Execute the query via REST API
        try:
            query_result = await sql_client.execute_query_via_rest(sql_query)
        except Exception as api_error:
            return {
                "error": f"Failed to execute query via REST API: {str(api_error)}",
                "query": sql_query,
                "connection_method": "REST API",
                "troubleshooting": [
                    "Check Azure AD authentication with validateAzureAuthMSSQL",
                    "Verify SQL server and database names are correct",
                    "Ensure your account has access to the SQL database",
                    "Check network connectivity to Azure SQL Database",
                    "Verify subscription ID and resource group settings"
                ]
            }
        
        # Format query results
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
            "table_used": query_info.get('table_used', 'unknown'),
            "connection_method": "REST API",
            "data_source": metadata.get("source", "mssql_server"),
            "query_type": metadata.get("query_type", "general"),
            "server": server,
            "database": database,
            "validation_info": {
                "pre_validated": True,
                "columns_selected": query_info.get('columns_selected', []),
                "filters_applied": query_info.get('filters_applied', ''),
                "ordering": query_info.get('ordering', ''),
                "limit": query_info.get('limit', '')
            }
        }
        
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        return {
            "error": f"Error processing your question: {str(e)}",
            "suggestion": "Try asking questions like: 'Show me top 10 customers', 'What products were used this month?', 'Which customers have high request counts?'"
        }

@mcp.tool() 
async def listTablesMSSQL() -> Dict[str, Any]:
    """
    List all available tables and their columns that can be queried via REST API for MS SQL Server.
    
    Returns:
        A JSON object containing all available tables, their column information, and metadata.
    """
    try:
        tables_info = []
        for table_key, table_info in TABLE_SCHEMA['tables'].items():
            column_details = []
            column_metadata = table_info.get('column_metadata', {})
            
            for col in table_info['columns']:
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
                "table_name": table_info['name'],
                "enabled": table_info['enabled'],
                "description": table_info['description'],
                "columns": column_details,
                "column_count": len(table_info['columns'])
            })
        
        # Filter to show only enabled tables by default
        enabled_tables = [t for t in tables_info if t['enabled']]
        
        return {
            "success": True,
            "enabled_tables": enabled_tables,
            "all_tables": tables_info,
            "total_tables": len(tables_info),
            "enabled_count": len(enabled_tables),
            "available_products": PRODUCT_ENUM,
            "available_track_info": TRACK_ENUM,
            "available_http_methods": HTTP_METHOD_ENUM,
            "available_os": OS_ENUM,
            "note": "Provider, Resource, and ApiVersion fields no longer have enum restrictions and accept any valid database values",
            "connection_method": "REST API",
            "data_source": "MS SQL Server Schema Cache"
        }
    except Exception as e:
        return {"error": f"Error retrieving table information: {str(e)}"}

@mcp.tool()
async def validateAzureAuthMSSQL() -> Dict[str, Any]:
    """
    Validate Azure AD authentication for MS SQL Server using REST approach.
    
    Returns:
        A JSON object containing authentication test results.
    """
    try:
        # Test SQL database token
        sql_token = await sql_client.get_access_token(sql_client.sql_scope)
        
        # Test management API token
        mgmt_token = await sql_client.get_access_token(sql_client.management_scope)
        
        return {
            "success": True,
            "message": "Azure AD authentication successful for MS SQL Server REST API",
            "server": server,
            "database": database,
            "subscription_id": subscription_id,
            "resource_group": resource_group,
            "sql_token_prefix": sql_token[:30] + "...",
            "sql_token_length": len(sql_token),
            "mgmt_token_prefix": mgmt_token[:30] + "...",
            "mgmt_token_length": len(mgmt_token),
            "authentication_method": "DefaultAzureCredential",
            "sql_scope": sql_client.sql_scope,
            "management_scope": sql_client.management_scope,
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

@mcp.tool()
async def executeCustomSQLMSSQL(sql_query: str) -> Dict[str, Any]:
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
            query_result = await sql_client.execute_query_via_rest(sql_query)
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

@mcp.tool()
async def getEnumValuesMSSQL(field_name: str) -> Dict[str, Any]:
    """
    Get available enum values for a specific field to help with query construction for MS SQL Server.
    
    Args:
        field_name: The name of the field to get enum values for (e.g., 'Product', 'TrackInfo', 'Provider')
        
    Returns:
        A JSON object containing the available enum values for the specified field.
    """
    try:
        enum_mappings = {
            'product': PRODUCT_ENUM,
            'trackinfo': TRACK_ENUM,
            'track': TRACK_ENUM,
            'httpmethod': HTTP_METHOD_ENUM,
            'method': HTTP_METHOD_ENUM,
            'os': OS_ENUM,
            'operatingsystem': OS_ENUM
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
            enum_values = enum_mappings[field_lower]
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
        definitions = TABLE_SCHEMA.get('definitions', {})
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

@mcp.tool()
async def validateQueryMSSQL(user_question: str) -> Dict[str, Any]:
    """
    Validate a user question and show what SQL would be generated without executing it for MS SQL Server.
    
    Args:
        user_question: The natural language question to validate
        
    Returns:
        A JSON object containing the validation results and planned SQL query.
    """
    try:
        # Parse the user question
        query_info = parse_user_query(user_question)
        
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
        
        # Build the SQL query (same logic as mssqlQuery but don't execute)
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

if __name__ == "__main__":
    try:
        # Initialize and run the server
        print("Starting MCP MS SQL Server with REST API support (No ODBC required)...")
        mcp.run(transport="streamable-http")
    except Exception as e:
        print(f"Error while running MCP server: {e}", file=sys.stderr)
