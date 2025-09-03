"""
Test script for the new AI-powered KQL modification approach
"""
import asyncio
import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.schema_loader import SchemaLoader
from src.mcp_tools import MCPTools

async def test_ai_kql_modification():
    """Test the new AI-powered KQL modification"""
    
    # Initialize components
    schema_file = 'reference/schemas/AMEAnalytics_Schema.json'
    schema_loader = SchemaLoader(schema_file)
    mcp_tools = MCPTools(schema_loader)
    
    # Read the sample KQL file
    with open('reference/samples/sample.kql', 'r') as f:
        original_kql = f.read()
    
    # Test different user questions
    test_questions = [
        "show me the js request count this month",
        "filter for JavaScript requests only",
        "show top 10 results",
        "change time range to last 7 days", 
        "group by OS and provider",
        "只显示Python SDK的请求",
        "last 30 days data only"
    ]
    
    print("🧪 Testing AI-powered KQL modification approach")
    print("=" * 60)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Testing question: {question}")
        print("-" * 40)
        
        try:
            result = await mcp_tools.modify_kusto_query(original_kql, question)
            
            if result.get("success"):
                print("✅ Success!")
                print(f"Request type: {result.get('request_type')}")
                print(f"AI prompt length: {len(result.get('ai_prompt', ''))} characters")
                print(f"Schema context provided: {len(result.get('schema_context', {}))} items")
                
                # Show a snippet of the AI prompt
                ai_prompt = result.get('ai_prompt', '')
                if ai_prompt:
                    snippet = ai_prompt[:200] + "..." if len(ai_prompt) > 200 else ai_prompt
                    print(f"AI prompt preview: {snippet}")
                
            else:
                print(f"❌ Error: {result.get('error')}")
                
        except Exception as e:
            print(f"💥 Exception: {str(e)}")
    
    print("\n" + "=" * 60)
    print("Test completed! The method now prepares requests for AI processing.")
    print("Next step: Send the ai_prompt to your AI model (ChatGPT, Claude, etc.)")

if __name__ == "__main__":
    asyncio.run(test_ai_kql_modification())
