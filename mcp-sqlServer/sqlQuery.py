import os
import sys
import json
import re
from typing import Any, Dict, List, Optional

import httpx
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
def load_table_schema() -> Dict[str, List[Dict]]:
    """Load table schema from fixture file."""
    try:
        schema_file = os.path.join(os.path.dirname(__file__), 'fixture', 'tables_and_columns.json')
        with open(schema_file, 'r') as f:
            schema_data = json.load(f)
        
        # Convert to dict for easier lookup
        schema_dict = {}
        for table in schema_data:
            table_name = table['TableName']
            columns = [col['ColumnName'] for col in table['Columns']]
            schema_dict[table_name.lower()] = {
                'name': table_name,
                'columns': columns
            }
        return schema_dict
    except Exception as e:
        print(f"Error loading table schema: {e}")
        return {}

# Global schema cache
TABLE_SCHEMA = load_table_schema()

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
    """Find the most likely table name from user query."""
    query_lower = query_text.lower()
    
    # Direct table name matches
    for table_key, table_info in TABLE_SCHEMA.items():
        if table_key in query_lower or table_info['name'].lower() in query_lower:
            return table_info['name']
    
    # Keyword-based matching
    table_keywords = {
        'customer': ['AMEConciseFiteredNewProductCCIDCustomer', 'AMEConciseFiteredNewProductCCIDCustomerSubscriptionId'],
        'product': ['AMEConciseFiteredNewProductCCIDCustomer', 'AMEConciseFiteredNewProductCCIDCustomerSubscriptionId'],
        'subscription': ['AMEConciseFiteredNewProductCCIDCustomerSubscriptionId'],
        'request': ['AMEConciseFiteredNewProductCCIDCustomer', 'AMEConciseFiteredNewProductCCIDCustomerSubscriptionId']
    }
    
    for keyword, tables in table_keywords.items():
        if keyword in query_lower:
            return tables[0]  # Return first matching table
    
    return None

def extract_columns_from_query(query_text: str, table_name: str) -> List[str]:
    """Extract relevant columns based on user query and table schema."""
    if not table_name or table_name.lower() not in TABLE_SCHEMA:
        return ['*']
    
    available_columns = TABLE_SCHEMA[table_name.lower()]['columns']
    query_lower = query_text.lower()
    
    # Check for specific column mentions
    mentioned_columns = []
    for col in available_columns:
        if col.lower() in query_lower:
            mentioned_columns.append(col)
    
    # If no specific columns mentioned, use common ones based on query type
    if not mentioned_columns:
        # Default important columns
        default_columns = []
        for col in available_columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['name', 'product', 'count', 'month', 'ccid']):
                default_columns.append(col)
        
        if default_columns:
            return default_columns
        else:
            return available_columns[:5]  # Return first 5 columns if no pattern match
    
    return mentioned_columns

def build_where_clause(query_text: str, table_name: str) -> str:
    """Build WHERE clause based on user query intent."""
    if not table_name or table_name.lower() not in TABLE_SCHEMA:
        return "1=1"  # Return all records if no specific filtering
    
    available_columns = TABLE_SCHEMA[table_name.lower()]['columns']
    query_lower = query_text.lower()
    conditions = []
    
    # Extract common filters
    # Month filtering
    month_patterns = re.findall(r'(\d{4}-\d{2}|\d{4}/\d{2}|january|february|march|april|may|june|july|august|september|october|november|december)', query_lower)
    if month_patterns and 'Month' in available_columns:
        for month in month_patterns:
            conditions.append(f"Month LIKE '%{month}%'")
    
    # Product filtering
    if 'product' in query_lower and 'Product' in available_columns:
        # Look for specific product names in quotes or after keywords
        product_match = re.search(r'product[s]?\s+(?:is|equals?|named?|called?)\s+["\']?([^"\']+)["\']?', query_lower)
        if product_match:
            product_name = product_match.group(1).strip()
            conditions.append(f"Product = '{product_name}'")
    
    # Customer filtering
    if 'customer' in query_lower and 'CustomerName' in available_columns:
        customer_match = re.search(r'customer[s]?\s+(?:is|equals?|named?|called?)\s+["\']?([^"\']+)["\']?', query_lower)
        if customer_match:
            customer_name = customer_match.group(1).strip()
            conditions.append(f"CustomerName = '{customer_name}'")
    
    # Request count filtering
    if any(word in query_lower for word in ['high', 'low', 'more than', 'less than', 'greater', 'minimum', 'maximum']) and 'RequestCount' in available_columns:
        # Extract numeric values
        numbers = re.findall(r'\b(\d+)\b', query_text)
        if numbers:
            num = numbers[0]
            if any(word in query_lower for word in ['more than', 'greater', 'minimum', 'high']):
                conditions.append(f"RequestCount > {num}")
            elif any(word in query_lower for word in ['less than', 'maximum', 'low']):
                conditions.append(f"RequestCount < {num}")
    
    # Top N filtering
    top_match = re.search(r'top\s+(\d+)', query_lower)
    if top_match:
        # This will be handled in the main query logic
        pass
    
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
    
    # Handle ORDER BY
    order_clause = ""
    if any(word in user_question.lower() for word in ['highest', 'most', 'maximum', 'desc']):
        if 'RequestCount' in TABLE_SCHEMA[table_name.lower()]['columns']:
            order_clause = "ORDER BY RequestCount DESC"
    elif any(word in user_question.lower() for word in ['lowest', 'least', 'minimum', 'asc']):
        if 'RequestCount' in TABLE_SCHEMA[table_name.lower()]['columns']:
            order_clause = "ORDER BY RequestCount ASC"
    
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
    List all available tables and their columns that can be queried.
    
    Returns:
        A JSON object containing all available tables and their column information.
    """
    try:
        tables_info = []
        for table_key, table_info in TABLE_SCHEMA.items():
            tables_info.append({
                "table_name": table_info['name'],
                "columns": table_info['columns'],
                "description": f"Table containing {', '.join(table_info['columns'][:3])}..." if len(table_info['columns']) > 3 else f"Table containing {', '.join(table_info['columns'])}"
            })
        
        return {
            "success": True,
            "tables": tables_info,
            "total_tables": len(tables_info)
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


if __name__ == "__main__":
    try:
        # Initialize and run the server
        print("Starting MCP server...")
        mcp.run(transport="streamable-http")
    except Exception as e:
        print(f"Error while running MCP server: {e}", file=sys.stderr)
