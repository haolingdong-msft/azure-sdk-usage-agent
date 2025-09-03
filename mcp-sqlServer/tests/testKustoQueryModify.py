#!/usr/bin/env python3
"""
Test script for Kusto Query modification functionality
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.schema_loader import SchemaLoader
from src.mcp_tools import MCPTools
from src.config import SCHEMA_FILE_PATH


async def test_kusto_query_modification():
    """Test the Kusto query modification functionality"""
    
    # Sample KQL query (simplified version of sample.kql)
    sample_kql = """let currentDateTime = datetime({startDateTime});  
let startDateTime = datetime_add("day", -15, currentDateTime); 
let endDateTime = datetime_add("minute", 30, startDateTime); 

let GetProduct = (UAString: string)  
{  
    let userAgent = tolower(trim(" ", UAString));  
    case(
        isempty(UAString), "",
        userAgent has "terraform", "Terraform",  
        userAgent has "ansible", "Ansible",  
        userAgent has "azure-sdk-for-python" or userAgent has "azsdk-python", "Python-SDK",  
        userAgent has "azure-sdk-for-java" or userAgent has  "azsdk-java", "Java Fluent Premium",  
        ""  
    )
};

Unionizer("Requests", "HttpIncomingRequests")
| where TIMESTAMP >= startDateTime and TIMESTAMP < endDateTime
| where TaskName == "HttpIncomingRequestEndWithSuccess"
| where isnotempty(subscriptionId)
| extend Product = GetProduct(userAgent)
| where isnotnull(Product) and isnotempty(Product)
| summarize counts = count() by subscriptionId, Product
| project subscriptionId, Product, counts
| extend startDateTime"""

    # Initialize components
    schema_loader = SchemaLoader(SCHEMA_FILE_PATH)
    mcp_tools = MCPTools(schema_loader)
    
    # Test cases
    test_cases = [
        {
            "description": "Filter for Python SDK only",
            "user_question": "只显示Python SDK的数据",
            "expected_contains": ['| where Product == "Python-SDK"']
        },
        {
            "description": "Change to last 7 days",
            "user_question": "过去7天的数据",
            "expected_contains": ['datetime_add("day", -7, currentDateTime)']
        },
        {
            "description": "Add top 10 limit",
            "user_question": "显示前10个结果",
            "expected_contains": ['| top 10 by counts desc']
        },
        {
            "description": "Filter for Java SDK",
            "user_question": "只要Java相关的数据",
            "expected_contains": ['| where Product == "Java Fluent Premium"']
        }
    ]
    
    print("🧪 Testing Kusto Query Modification Functionality")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['description']}")
        print(f"❓ User Question: {test_case['user_question']}")
        
        try:
            # Call the modify_kusto_query function
            result = await mcp_tools.modify_kusto_query(sample_kql, test_case['user_question'])
            
            if result.get('success'):
                print("✅ Modification successful")
                modified_kql = result.get('modified_kql', '')
                
                # Check if expected content is present
                found_expected = []
                for expected in test_case['expected_contains']:
                    if expected in modified_kql:
                        found_expected.append(expected)
                        print(f"   ✓ Found expected content: {expected}")
                    else:
                        print(f"   ✗ Missing expected content: {expected}")
                
                # Show modifications applied
                modifications = result.get('modifications_applied', [])
                print(f"   📊 Modifications applied: {', '.join(modifications)}")
                
                # Show a snippet of the modified query
                print("   📄 Modified query snippet:")
                lines = modified_kql.split('\n')
                for line in lines:
                    if any(exp in line for exp in test_case['expected_contains']):
                        print(f"      >>> {line.strip()}")
                
            else:
                print(f"❌ Modification failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🏁 Kusto Query Modification Tests Completed")


async def test_validation_functionality():
    """Test the Kusto query validation functionality"""
    print("\n🔍 Testing Kusto Query Validation Functionality")
    print("=" * 60)
    
    # Initialize components
    schema_loader = SchemaLoader(SCHEMA_FILE_PATH)
    mcp_tools = MCPTools(schema_loader)
    
    valid_kql = """let currentDateTime = now();
let startDateTime = datetime_add("day", -7, currentDateTime);
Unionizer("Requests")
| where TIMESTAMP >= startDateTime
| summarize count() by Product"""
    
    invalid_kql = """| where TIMESTAMP >= startDateTime
let currentDateTime = now()
| summarize count() by Product"""
    
    test_cases = [
        {
            "description": "Valid KQL query",
            "kql": valid_kql,
            "should_be_valid": True
        },
        {
            "description": "Invalid KQL query (starts with pipe)",
            "kql": invalid_kql,
            "should_be_valid": False
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Validation Test {i}: {test_case['description']}")
        
        try:
            # Create a temporary function for validation (since it's not in mcp_tools yet)
            lines = test_case['kql'].split('\n')
            errors = []
            
            for i, line in enumerate(lines, 1):
                line_stripped = line.strip()
                if not line_stripped or line_stripped.startswith('//'):
                    continue
                    
                if line_stripped.startswith('|') and i == 1:
                    errors.append(f"Line {i}: Query cannot start with pipe operator")
            
            is_valid = len(errors) == 0
            
            if is_valid == test_case['should_be_valid']:
                print("✅ Validation result as expected")
            else:
                print("❌ Validation result unexpected")
            
            if errors:
                print(f"   ⚠️ Errors found: {errors}")
            else:
                print("   ✓ No syntax errors detected")
                
        except Exception as e:
            print(f"❌ Validation test failed: {str(e)}")


if __name__ == "__main__":
    async def main():
        await test_kusto_query_modification()
        await test_validation_functionality()
    
    # Run the tests
    asyncio.run(main())
