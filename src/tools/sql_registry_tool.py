"""
SQL Generator Tool Service

Handles registration and configuration of SQL generation tools for the MCP server.
"""
from typing import List, Tuple
from mcp.server.fastmcp import FastMCP
from src.utils.file_utils import load_and_format_prompt, load_description

class SQLGeneratorTool:
    """Manages SQL generation tools registration and configuration"""
    
    def __init__(self):
        self.sql_tools_config = [
            ("genSQLByMonthProductSubscriptionId", "AMEConciseFiteredNewProductCCIDCustomerSubscriptionId"),
            ("genSQLByMonthProduct", "AMEConciseSubReqCCIDCountByMonthProduct"),
            ("genSQLByMonthProductHttpMethod", "AMEConciseSubReqCCIDCountByMonthProductHttpMethod"),
            ("genSQLByMonthProductOS", "AMEConciseSubReqCCIDCountByMonthProductOS"),
            ("genSQLByMonthProductProviderTrackInfo", "AMEConciseSubReqCCIDCountByMonthProductProviderTrackInfo"),
            ("genSQLByMonthProductProviderTrackInfoApiVersion", "AMEConciseSubReqCCIDCountByMonthProductProviderTrackInfoApiVersion"),
            ("genSQLByMonthProductProviderTrackInfoPUT", "AMEConciseSubReqCCIDCountByMonthProductProviderTrackInfoPUT"),
            ("genSQLByMonthProductTrackInfo", "AMEConciseSubReqCCIDCountByMonthProductTrackInfo"),
            ("genSQLByMonthProductTrackInfoMinorLanguageVersion", "AMEConciseSubReqCountByMonthProductMinorLanguageVersion"),
            ("genSQLByMonthProductTrackInfoMinorLanguageVersionPatchLanguageVersion", "AMEConciseSubReqCountByMonthProductPatchLanguageVersion"),
            ("genSQLReqCountByMonthTrackInfoPackageNamePackageVersionGoVersionForGo", "AMEGoSDKReqCountCustomerDataByMonth"),
            ("genSQLSubCountByMonthPackageNamePackageVersionForGo", "AMEGoSDKSubCountCustomerDataByMonthPackageName"),
            ("genSQLSubCountByMonthTrackInfoForGo", "AMEGoSDKSubCountCustomerDataByMonthTrackInfo"),
            ("genSQLSubCountByMonthGoVersionForGo", "AMEGoSDKSubCountCustomerDataByMonthVersion"),
        ]
    
    def create_sql_tool(self, prompt_file: str, file_context):
        """Create a SQL generation tool function"""
        async def tool_func(user_question: str):
            return load_and_format_prompt(prompt_file, user_question, file_context)
        return tool_func
    
    def register_sql_tools(self, mcp: FastMCP, file_context):
        """Register all SQL generation tools with the MCP server"""
        for tool_name, prompt_file in self.sql_tools_config:
            tool_func = self.create_sql_tool(prompt_file, file_context)
            tool_func.__name__ = tool_name
            mcp.tool(description=load_description(tool_name, file_context))(tool_func)
    
    def get_sql_tools_config(self) -> List[Tuple[str, str]]:
        """Get the SQL tools configuration"""
        return self.sql_tools_config.copy()