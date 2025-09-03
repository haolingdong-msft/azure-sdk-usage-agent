#!/usr/bin/env python3
"""
Simple test to verify Kusto query modification works with sample.kql
Only returns the final modified query
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.schema_loader import SchemaLoader
from src.mcp_tools import MCPTools
from src.config import SCHEMA_FILE_PATH


async def simple_kql_test():
    """Simple test of KQL modification"""
    
    # Read the actual sample.kql file
    sample_kql_file = os.path.join(os.path.dirname(__file__), '..', 'reference', 'samples', 'sample.kql')
    
    with open(sample_kql_file, 'r', encoding='utf-8') as f:
        original_kql = f.read()
    
    # Initialize components (suppress initialization output)
    schema_loader = SchemaLoader(SCHEMA_FILE_PATH)
    mcp_tools = MCPTools(schema_loader)
    
    # Test case: Filter for Python SDK only
    user_question = "只显示Python SDK的数据"
    
    result = await mcp_tools.modify_kusto_query(original_kql, user_question)
    
    if result.get('success'):
        # Return only the modified query
        return result.get('modified_kql', '')
    else:
        return f"Error: {result.get('error', 'Unknown error')}"


if __name__ == "__main__":
    # Suppress all debug output 
    import logging
    logging.getLogger().setLevel(logging.CRITICAL)
    
    # Capture and suppress print statements during initialization
    import io
    from contextlib import redirect_stdout, redirect_stderr
    
    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        result = asyncio.run(simple_kql_test())
    
    print(result)
