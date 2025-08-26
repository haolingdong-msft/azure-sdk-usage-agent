#!/usr/bin/env python3
"""
Test the core SQL query parsing logic without database dependencies.
This demonstrates the natural language processing capabilities.
"""

import json
import re
import os
from typing import Dict, List, Optional, Any

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

def find_table_by_name(query_text: str, schema: Dict) -> Optional[str]:
    """Find the most likely table name from user query."""
    query_lower = query_text.lower()
    
    # Direct table name matches
    for table_key, table_info in schema.items():
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

def extract_columns_from_query(query_text: str, table_name: str, schema: Dict) -> List[str]:
    """Extract relevant columns based on user query and table schema."""
    if not table_name or table_name.lower() not in schema:
        return ['*']
    
    available_columns = schema[table_name.lower()]['columns']
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

def build_where_clause(query_text: str, table_name: str, schema: Dict) -> str:
    """Build WHERE clause based on user query intent."""
    if not table_name or table_name.lower() not in schema:
        return "1=1"  # Return all records if no specific filtering
    
    available_columns = schema[table_name.lower()]['columns']
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
    
    return ' AND '.join(conditions) if conditions else "1=1"

def parse_user_query(user_question: str, schema: Dict) -> Dict[str, Any]:
    """Parse user question into SQL query components."""
    table_name = find_table_by_name(user_question, schema)
    
    if not table_name:
        return {
            'error': 'Could not identify a relevant table from your question. Available topics: customer data, product usage, subscription information.'
        }
    
    columns = extract_columns_from_query(user_question, table_name, schema)
    where_clause = build_where_clause(user_question, table_name, schema)
    
    # Handle TOP N queries
    limit_clause = ""
    top_match = re.search(r'top\s+(\d+)', user_question.lower())
    if top_match:
        limit_clause = f"TOP {top_match.group(1)}"
    
    # Handle ORDER BY
    order_clause = ""
    if any(word in user_question.lower() for word in ['highest', 'most', 'maximum', 'desc']):
        if 'RequestCount' in schema[table_name.lower()]['columns']:
            order_clause = "ORDER BY RequestCount DESC"
    elif any(word in user_question.lower() for word in ['lowest', 'least', 'minimum', 'asc']):
        if 'RequestCount' in schema[table_name.lower()]['columns']:
            order_clause = "ORDER BY RequestCount ASC"
    
    return {
        'table_name': table_name,
        'columns': columns,
        'where_clause': where_clause,
        'limit_clause': limit_clause,
        'order_clause': order_clause
    }

def generate_sql_query(query_info: Dict[str, Any]) -> str:
    """Generate SQL query from parsed components."""
    if 'error' in query_info:
        return None
    
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
    
    return ' '.join(sql_parts)

def test_queries():
    """Test various natural language queries."""
    print("🚀 Testing Natural Language SQL Query Parser\n")
    
    # Load schema
    schema = load_table_schema()
    print(f"📊 Loaded schema for {len(schema)} tables:")
    for table_name, table_info in schema.items():
        print(f"  • {table_info['name']} ({len(table_info['columns'])} columns)")
    print()
    
    # Test questions
    test_questions = [
        "Show me the top 10 customers by request count",
        "What products were used in 2024-01?", 
        "List customers with more than 1000 requests",
        "Show me product usage data",
        "Which customers use the most products?",
        "Get subscription data for high usage customers",
        "Show me all customer information",
        "Find products that Microsoft uses"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"Test {i}: {question}")
        print("-" * 60)
        
        # Parse the question
        query_info = parse_user_query(question, schema)
        
        if 'error' in query_info:
            print(f"❌ Error: {query_info['error']}")
        else:
            # Generate SQL
            sql_query = generate_sql_query(query_info)
            
            print(f"✅ Successfully parsed query")
            print(f"📊 Table: {query_info['table_name']}")
            print(f"📋 Columns: {', '.join(query_info['columns'])}")
            print(f"🔍 Where: {query_info['where_clause']}")
            if query_info['limit_clause']:
                print(f"🔢 Limit: {query_info['limit_clause']}")
            if query_info['order_clause']:
                print(f"🔄 Order: {query_info['order_clause']}")
            print(f"💻 Generated SQL:")
            print(f"   {sql_query}")
        
        print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    test_queries()
