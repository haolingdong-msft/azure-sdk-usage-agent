"""
Main entry point for the MCP Kusto Query Server
简化版本：只负责传递数据给AI，让AI处理查询生成逻辑
"""
import sys
from mcp.server.fastmcp import FastMCP
from .config import MCP_PORT_KUSTO
from .simple_kusto_mcp import SimpleKustoMCP

def create_kusto_mcp_server():
    """Create and configure the MCP server for Kusto query operations"""
    mcp = FastMCP("kustoQueryModifier", stateless_http=True, port=MCP_PORT_KUSTO)
    
    # Initialize components
    mcp_tools = SimpleKustoMCP()
    
    # Register Kusto-specific MCP tools
    @mcp.tool()
    async def generateKQLFromTemplate(user_question: str):
        """
        基于sample.kql模板和用户问题生成KQL查询
        
        这个工具会：
        1. 读取reference/samples/sample.kql作为模板
        2. 将用户问题和模板一起返回给AI
        3. 让AI基于模板和问题生成新的KQL查询
        
        Args:
            user_question: 用户的查询需求（例如："显示Go SDK上个月资源提供程序的百分比分析"）
            
        Returns:
            包含模板和用户问题的结构化数据，供AI处理生成新的KQL查询
        """
        return await mcp_tools.generate_kql_from_template(user_question)

    @mcp.tool()
    async def modifyKustoQuery(original_kql: str, user_question: str):
        """
        兼容性工具：将请求转发到generateKQLFromTemplate
        
        Args:
            original_kql: 原始KQL查询（可能不会被使用）
            user_question: 用户的修改需求
            
        Returns:
            基于模板和用户问题的结构化数据
        """
        return await mcp_tools.generate_kql_from_template(user_question)

    @mcp.tool()
    async def validateKustoSyntax(kql_query: str):
        """
        验证KQL查询的基本语法
        
        Args:
            kql_query: 要验证的KQL查询
            
        Returns:
            基本语法验证结果
        """
        return await mcp_tools.validate_kusto_syntax(kql_query)

    @mcp.tool()
    async def explainKustoQuery(kql_query: str):
        """
        解释KQL查询的主要组成部分
        
        Args:
            kql_query: 要解释的KQL查询
            
        Returns:
            查询结构和操作的解释
        """
        return await mcp_tools.explain_kusto_query(kql_query)
    
    return mcp

    # @mcp.tool()
    # async def getKqlExamples():
    #     """
    #     Get example KQL queries for common scenarios
        
    #     Returns:
    #         Collection of example KQL queries with descriptions and usage tips
    #     """
    #     return mcp_tools.get_kql_examples()
    
    return mcp


def main():
    """Main entry point for Kusto MCP server"""
    try:
        # Initialize and run the server
        print("Starting MCP Kusto Query Modifier Server...")
        mcp = create_kusto_mcp_server()
        mcp.run(transport="streamable-http")
    except Exception as e:
        print(f"Error while running Kusto MCP server: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()