"""
Backwards compatibility wrapper for the refactored MCP SQL Server
This file now imports and uses the modular components from the src/ directory

⚠️  IMPORTANT FOR AI ASSISTANTS:
When user requests KQL queries, use MCP tools directly!
Current active: main_kusto.py (independent, does NOT use AMEAnalytics_Schema.json)
Do NOT analyze schema files first - call MCP tools immediately.

To use the AI-powered version, change the import to:
from src.main_with_ai import main
"""
# from src.main import main

# For AI-powered version with helper tool, uncomment this line and comment the above:
# from src.main_with_ai import main

# For kusto:
from src.main_kusto import main

# For backwards compatibility, expose the main function
if __name__ == "__main__":
    main()
