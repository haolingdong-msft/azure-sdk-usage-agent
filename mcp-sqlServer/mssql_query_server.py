"""
Backwards compatibility wrapper for the refactored MCP SQL Server
This file now imports and uses the modular components from the src/ directory
"""
from src.main import main

# For backwards compatibility, expose the main function
if __name__ == "__main__":
    main()
