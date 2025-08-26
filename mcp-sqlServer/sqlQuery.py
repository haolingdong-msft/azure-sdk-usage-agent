import os
import sys
import json
import re
from typing import Any, Dict, List, Optional

import pyodbc
from mcp.server.fastmcp import FastMCP
from azure.identity import DefaultAzureCredential

# Initialize FastMCP server
mcp_port = int(os.environ.get("FUNCTIONS_CUSTOMHANDLER_PORT", 8080))
mcp = FastMCP("sqlQuery", stateless_http=True, port=mcp_port)

# Constants
server = os.getenv('SQL_SERVER', 'azuresdkbi-server.database.windows.net')
database = os.getenv('SQL_DATABASE', 'azuresdkbi') 
driver = '{ODBC Driver 17 for SQL Server}'

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
PROVIDER_ENUM = TABLE_SCHEMA['definitions'].get('Provider', {}).get('enum', [])
RESOURCE_ENUM = TABLE_SCHEMA['definitions'].get('Resource', {}).get('enum', [])
HTTP_METHOD_ENUM = TABLE_SCHEMA['definitions'].get('HttpMethod', {}).get('enum', [])
OS_ENUM = TABLE_SCHEMA['definitions'].get('OS', {}).get('enum', [])

def get_database_connection():
    """Establish connection to SQL Server with Azure AD authentication."""
    try:
        credential = DefaultAzureCredential()
        token = credential.get_token("https://database.windows.net/.default")
        
        conn = pyodbc.connect(
            f"Driver={driver};Server={server};Database={database};Authentication=ActiveDirectoryMsi;",
            attrs={'AccessToken': token.token}
        )
        return conn
    except Exception as e:
        raise Exception(f"Failed to connect to database: {str(e)}")

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
    
    # Enhanced filtering with enum support
    
    # Month filtering (improved pattern matching)
    month_patterns = re.findall(r'(\d{4}-\d{2}-\d{2}|\d{4}-\d{2}|\d{4}/\d{2})', query_lower)
    if month_patterns and 'Month' in available_columns:
        for month in month_patterns:
            if len(month) == 7:  # YYYY-MM format
                conditions.append(f"Month LIKE '{month}%'")
            else:
                conditions.append(f"Month = '{month}'")
    
    # Product filtering with enum support
    if 'Product' in available_columns:
        for product in PRODUCT_ENUM:
            if product.lower() in query_lower:
                conditions.append(f"Product = '{product}'")
                break
        # Generic product filtering
        if not any(product.lower() in query_lower for product in PRODUCT_ENUM):
            product_match = re.search(r'product[s]?\s+(?:is|equals?|named?|called?)\s+["\']?([^"\']+)["\']?', query_lower)
            if product_match:
                product_name = product_match.group(1).strip()
                conditions.append(f"Product LIKE '%{product_name}%'")
    
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
    
    # Provider filtering with enum support
    if 'Provider' in available_columns:
        for provider in PROVIDER_ENUM:
            if provider.lower() in query_lower or provider.replace('Microsoft.', '').lower() in query_lower:
                conditions.append(f"Provider = '{provider}'")
                break
    
    # Resource filtering with enum support
    if 'Resource' in available_columns:
        for resource in RESOURCE_ENUM:
            if resource.lower() in query_lower:
                conditions.append(f"Resource = '{resource}'")
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
    
    # API Version filtering
    if 'ApiVersion' in available_columns:
        api_version_match = re.search(r'(\d{4}-\d{2}-\d{2}(?:-preview)?)', query_lower)
        if api_version_match:
            api_version = api_version_match.group(1)
            conditions.append(f"ApiVersion = '{api_version}'")
    
    # Subscription ID filtering (UUID pattern)
    if any(col in available_columns for col in ['SubscriptionId', 'SubscriptionID']):
        uuid_pattern = re.search(r'([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})', query_text)
        if uuid_pattern:
            uuid_val = uuid_pattern.group(1)
            if 'SubscriptionId' in available_columns:
                conditions.append(f"SubscriptionId = '{uuid_val}'")
            elif 'SubscriptionID' in available_columns:
                conditions.append(f"SubscriptionID = '{uuid_val}'")
    
    # Request/Subscription count filtering (enhanced)
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
    
    # Boolean filtering for IsTrack2
    if 'IsTrack2' in available_columns:
        if any(phrase in query_lower for phrase in ['track 2', 'track2', 'is track 2']):
            conditions.append("IsTrack2 = 1")
        elif any(phrase in query_lower for phrase in ['track 1', 'track1', 'is track 1', 'not track 2']):
            conditions.append("IsTrack2 = 0")
    
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

@mcp.tool()
async def sqlQuery(request: str) -> Dict[str, Any]:
    """
    Execute a SQL query based on a natural language question about SQL Server data.

    Args:
        request: A natural language question about the data (e.g., "Show me the top 10 customers by request count", 
                "What products were used in 2024-01?", "Which customers have more than 1000 requests?")

    Returns:
        A JSON object containing the query results, generated SQL, or error information.
    """
    
    try:
        print(f"Received question: {request}")
        
        # Parse the user question into SQL components
        query_info = parse_user_query(request)
        
        if 'error' in query_info:
            return {"error": query_info['error']}
        
        # Build the SQL query
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
        
        print(f"Generated SQL: {sql_query}")
        
        # Execute the query
        conn = get_database_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            
            # Format query results
            columns = [column[0] for column in cursor.description]
            result_data = []
            
            for row in rows:
                row_dict = {}
                for i, value in enumerate(row):
                    # Handle different data types
                    if value is None:
                        row_dict[columns[i]] = None
                    elif isinstance(value, (int, float, str, bool)):
                        row_dict[columns[i]] = value
                    else:
                        row_dict[columns[i]] = str(value)
                result_data.append(row_dict)
            
            return {
                "success": True,
                "query": sql_query,
                "data": result_data,
                "row_count": len(result_data),
                "table_used": query_info['table_name']
            }
            
        except pyodbc.Error as db_error:
            return {
                "error": f"Database error: {str(db_error)}",
                "query": sql_query
            }
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        return {
            "error": f"Error processing your question: {str(e)}",
            "suggestion": "Try asking questions like: 'Show me top 10 customers', 'What products were used this month?', 'Which customers have high request counts?'"
        }

@mcp.tool() 
async def listTables() -> Dict[str, Any]:
    """
    List all available tables and their columns that can be queried with enhanced metadata.
    
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
            "available_providers": PROVIDER_ENUM,
            "available_http_methods": HTTP_METHOD_ENUM,
            "available_os": OS_ENUM
        }
    except Exception as e:
        return {"error": f"Error retrieving table information: {str(e)}"}

@mcp.tool()
async def executeCustomSQL(sql_query: str) -> Dict[str, Any]:
    """
    Execute a custom SQL query directly (for advanced users).
    
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
        
        print(f"Executing custom SQL: {sql_query}")
        
        conn = get_database_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            
            # Format results
            columns = [column[0] for column in cursor.description]
            result_data = []
            
            for row in rows:
                row_dict = {}
                for i, value in enumerate(row):
                    if value is None:
                        row_dict[columns[i]] = None
                    elif isinstance(value, (int, float, str, bool)):
                        row_dict[columns[i]] = value
                    else:
                        row_dict[columns[i]] = str(value)
                result_data.append(row_dict)
            
            return {
                "success": True,
                "query": sql_query,
                "data": result_data,
                "row_count": len(result_data)
            }
            
        except pyodbc.Error as db_error:
            return {
                "error": f"Database error: {str(db_error)}",
                "query": sql_query
            }
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        return {"error": f"Error executing custom SQL: {str(e)}"}

@mcp.tool()
async def getEnumValues(field_name: str) -> Dict[str, Any]:
    """
    Get available enum values for a specific field to help with query construction.
    
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
            'provider': PROVIDER_ENUM,
            'resource': RESOURCE_ENUM,
            'httpmethod': HTTP_METHOD_ENUM,
            'method': HTTP_METHOD_ENUM,
            'os': OS_ENUM,
            'operatingsystem': OS_ENUM
        }
        
        field_lower = field_name.lower()
        
        if field_lower in enum_mappings:
            return {
                "success": True,
                "field_name": field_name,
                "enum_values": enum_mappings[field_lower],
                "count": len(enum_mappings[field_lower])
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
                    "description": def_info.get('description', '')
                }
        
        return {
            "error": f"No enum values found for field '{field_name}'",
            "available_fields": list(enum_mappings.keys())
        }
        
    except Exception as e:
        return {"error": f"Error retrieving enum values: {str(e)}"}

@mcp.tool()
async def validateQuery(user_question: str) -> Dict[str, Any]:
    """
    Validate a user question and show what SQL would be generated without executing it.
    
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
                ]
            }
        
        # Build the SQL query (same logic as sqlQuery but don't execute)
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
            "limit": query_info['limit_clause'] if query_info['limit_clause'] else "None"
        }
        
    except Exception as e:
        return {
            "valid": False,
            "error": f"Error validating query: {str(e)}"
        }


if __name__ == "__main__":
    try:
        # Initialize and run the server
        print("Starting MCP server...")
        mcp.run(transport="streamable-http")
    except Exception as e:
        print(f"Error while running MCP server: {e}", file=sys.stderr)
