"""
MCP Tools - Collection of tools for the MCP server
"""

from .kusto import (
    execute_kusto_query, 
    generate_kql_from_question,
    get_kusto_schema,
    get_kusto_helper_functions,
)

__all__ = [
    "execute_kusto_query",
    "generate_kql_from_question",
    "get_kusto_schema",
    "get_kusto_helper_functions",
]
