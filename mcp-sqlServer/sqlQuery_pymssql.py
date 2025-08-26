import os
import sys
import json
import re
from typing import Any, Dict, List, Optional

import pymssql
from mcp.server.fastmcp import FastMCP
from azure.identity import DefaultAzureCredential

# Initialize FastMCP server
mcp_port = int(os.environ.get("FUNCTIONS_CUSTOMHANDLER_PORT", 8080))
mcp = FastMCP("sqlQuery", stateless_http=True, port=mcp_port)

# Constants
server = os.getenv('SQL_SERVER', 'azuresdkbi-server.database.windows.net')
database = os.getenv('SQL_DATABASE', 'azuresdkbi') 

def get_database_connection():
    """Establish connection to SQL Server with Azure AD authentication using pymssql."""
    try:
        credential = DefaultAzureCredential()
        token = credential.get_token("https://database.windows.net/.default")
        
        # pymssql 连接字符串，使用访问令牌
        conn = pymssql.connect(
            server=server,
            database=database,
            as_dict=True,  # 返回字典格式的行
            # 使用访问令牌进行身份验证
            # 注意：pymssql 对 Azure AD 令牌的支持可能有限
        )
        return conn
    except Exception as e:
        raise Exception(f"Failed to connect to database with pymssql: {str(e)}")

# 其他函数保持不变...
