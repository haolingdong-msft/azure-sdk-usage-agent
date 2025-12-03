"""
MCP Tools - Collection of tools for the MCP server
"""

from .kusto import execute_kusto_query, query_kusto_with_natural_language

__all__ = [
    "execute_kusto_query",
    "query_kusto_with_natural_language",
]
