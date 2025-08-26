#!/usr/bin/env python3
"""
Test script for the refactored SQL Query MCP server.
This script demonstrates how to use the new natural language query capabilities.
"""

import asyncio
import json
from sqlQuery import sqlQuery, listTables, executeCustomSQL

async def test_natural_language_queries():
    """Test various natural language queries."""
    
    print("=== Testing Natural Language SQL Queries ===\n")
    
    # Test questions
    test_questions = [
        "Show me the top 10 customers by request count",
        "What are all the available tables?",
        "List customers with more than 1000 requests", 
        "Show me product usage data for 2024-01",
        "Which customers use the most products?",
        "Get all customer information",
        "Show me subscription data"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"Test {i}: {question}")
        print("-" * 50)
        
        try:
            if "available tables" in question.lower():
                result = await listTables()
            else:
                result = await sqlQuery(question)
            
            print(f"Result: {json.dumps(result, indent=2)}")
            
            if result.get('success'):
                print(f"✅ Query executed successfully")
                print(f"📊 Returned {result.get('row_count', 0)} rows")
                if 'query' in result:
                    print(f"🔍 Generated SQL: {result['query']}")
            else:
                print(f"❌ Query failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Exception occurred: {str(e)}")
        
        print("\n" + "="*70 + "\n")

async def test_custom_sql():
    """Test custom SQL execution."""
    
    print("=== Testing Custom SQL Queries ===\n")
    
    # Test custom SQL queries
    custom_queries = [
        "SELECT TOP 5 CustomerName, RequestCount FROM AMEConciseFiteredNewProductCCIDCustomer ORDER BY RequestCount DESC",
        "SELECT DISTINCT Product FROM AMEConciseFiteredNewProductCCIDCustomer",
        "SELECT Month, COUNT(*) as RecordCount FROM AMEConciseFiteredNewProductCCIDCustomer GROUP BY Month"
    ]
    
    for i, query in enumerate(custom_queries, 1):
        print(f"Custom Query {i}:")
        print(f"SQL: {query}")
        print("-" * 50)
        
        try:
            result = await executeCustomSQL(query)
            print(f"Result: {json.dumps(result, indent=2)}")
            
            if result.get('success'):
                print(f"✅ Custom query executed successfully")
                print(f"📊 Returned {result.get('row_count', 0)} rows")
            else:
                print(f"❌ Custom query failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Exception occurred: {str(e)}")
        
        print("\n" + "="*70 + "\n")

async def main():
    """Main test function."""
    print("🚀 Starting SQL Query MCP Server Tests\n")
    
    # Test natural language queries
    await test_natural_language_queries()
    
    # Test custom SQL
    await test_custom_sql()
    
    print("🏁 All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
