#!/usr/bin/env python3
"""
Test script to verify the new validation-first flow
"""

import asyncio
import sys
import os

# Add the current directory to the path so we can import the mssql_query_server
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the validation function
from mssql_query_server import validateQueryMSSQL

async def test_validation_flow():
    """Test the validation flow with different queries"""
    
    test_queries = [
        "Show me the request count for Go-SDK this month",
        "What are the top 10 products by request count?",
        "Invalid query with nonsense",
        "How many requests for Python-SDK in 2024-01?"
    ]
    
    print("🧪 Testing Query Validation Flow")
    print("=" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing: '{query}'")
        print("-" * 40)
        
        try:
            result = await validateQueryMSSQL(query)
            
            if result.get('valid', False):
                print("✅ Validation PASSED")
                print(f"   Generated SQL: {result.get('generated_sql', 'N/A')}")
                print(f"   Table: {result.get('table_used', 'N/A')}")
                print(f"   Columns: {result.get('columns_selected', 'N/A')}")
                print(f"   Filters: {result.get('filters_applied', 'None')}")
            else:
                print("❌ Validation FAILED")
                print(f"   Error: {result.get('error', 'N/A')}")
                if 'suggestions' in result:
                    print(f"   Suggestions: {result['suggestions']}")
                    
        except Exception as e:
            print(f"💥 Exception during validation: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_validation_flow())
