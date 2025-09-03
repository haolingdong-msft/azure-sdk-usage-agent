#!/usr/bin/env python3
"""
Demo script for Kusto Query modification functionality
Shows the final modified query output only
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.schema_loader import SchemaLoader
from src.mcp_tools import MCPTools
from src.config import SCHEMA_FILE_PATH


async def demo_kusto_modification():
    """Demo the Kusto query modification with clean output"""
    
    # Read the sample KQL from file
    sample_kql_file = os.path.join(os.path.dirname(__file__), '..', 'reference', 'samples', 'sample.kql')
    
    try:
        with open(sample_kql_file, 'r', encoding='utf-8') as f:
            original_kql = f.read()
    except FileNotFoundError:
        # Fallback to simplified version
        original_kql = """let currentDateTime = datetime({startDateTime});  
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
    
    # Test cases for demo
    test_cases = [
        "只显示Python SDK的数据",
        "过去7天的数据", 
        "显示前10个结果按计数排序",
        "只要Java相关的数据"
    ]
    
    print("🚀 Kusto Query Modification Demo")
    print("=" * 50)
    
    for i, user_question in enumerate(test_cases, 1):
        print(f"\n📝 Demo {i}: {user_question}")
        print("-" * 30)
        
        try:
            result = await mcp_tools.modify_kusto_query(original_kql, user_question)
            
            if result.get('success'):
                # Output only the final modified query
                print(result.get('modified_kql', ''))
            else:
                print(f"Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print("\n" + "=" * 50)


if __name__ == "__main__":
    # Suppress debug output for clean demo
    import logging
    logging.getLogger().setLevel(logging.ERROR)
    
    asyncio.run(demo_kusto_modification())
