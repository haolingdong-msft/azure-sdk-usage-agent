"""
Simple test to show what the AI prompt looks like
"""
import asyncio
import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.schema_loader import SchemaLoader
from src.mcp_tools import MCPTools

async def show_ai_prompt_example():
    """Show an example of the AI prompt generated"""
    
    # Initialize components
    schema_file = 'reference/schemas/AMEAnalytics_Schema.json'
    schema_loader = SchemaLoader(schema_file)
    mcp_tools = MCPTools(schema_loader)
    
    # Read the sample KQL file
    with open('reference/samples/sample.kql', 'r') as f:
        original_kql = f.read()
    
    # Test with the user's original question
    user_question = "show me the js request count this month"
    
    print("🤖 AI-Powered KQL Modification")
    print("=" * 60)
    print(f"User Question: {user_question}")
    print("=" * 60)
    
    result = await mcp_tools.modify_kusto_query(original_kql, user_question)
    
    if result.get("success"):
        ai_prompt = result.get("ai_prompt", "")
        print("Generated AI Prompt:")
        print("-" * 40)
        print(ai_prompt)
        print("-" * 40)
        print("\n✅ This prompt can now be sent to any AI model (ChatGPT, Claude, etc.)")
        print("The AI will return a modified KQL query based on the user's request.")
        
        # Show the expected response format
        expected = result.get("expected_response_format", {})
        print(f"\n📋 Expected AI Response Format:")
        print(f"- modified_kql: {expected.get('modified_kql', 'The modified KQL query')}")
        print(f"- explanation: {expected.get('explanation', 'Explanation of changes')}")
        print(f"- modifications_applied: {expected.get('modifications_applied', ['List of changes'])}")
    else:
        print(f"❌ Error: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(show_ai_prompt_example())
