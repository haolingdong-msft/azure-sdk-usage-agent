"""
Data models and type definitions
"""
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class TableInfo:
    """Information about a database table"""
    name: str
    enabled: bool
    description: str
    columns: List[str]
    column_metadata: Dict[str, Any]


@dataclass
class QueryInfo:
    """Information about a parsed query"""
    table_name: str
    columns: List[str]
    where_clause: str
    limit_clause: str
    order_clause: str


@dataclass
class QueryResult:
    """Result of a SQL query execution"""
    success: bool
    query: str
    data: List[Dict[str, Any]]
    row_count: int
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
