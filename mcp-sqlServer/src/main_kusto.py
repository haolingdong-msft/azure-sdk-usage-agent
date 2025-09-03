"""
Main entry point for the MCP Kusto Query Server
"""
import sys
from mcp.server.fastmcp import FastMCP
from .config import MCP_PORT, SCHEMA_FILE_PATH
from .schema_loader import SchemaLoader
from .mcp_tools import MCPTools


def create_kusto_mcp_server():
    """Create and configure the MCP server for Kusto query operations"""
    # Initialize FastMCP server with different port for Kusto
    kusto_port = MCP_PORT + 1  # Use a different port
    mcp = FastMCP("kustoQueryModifier", stateless_http=True, port=kusto_port)
    
    # Initialize components
    schema_loader = SchemaLoader(SCHEMA_FILE_PATH)
    mcp_tools = MCPTools(schema_loader)
    
    # Register Kusto-specific MCP tools
    @mcp.tool()
    async def modifyKustoQuery(original_kql: str, user_question: str):
        """
        根据用户提供的已有 Kusto Query 和用户问题，生成一个修改后的 Kusto Query，满足用户问题的要求。
        
        Args:
            original_kql: 原始的 Kusto Query (.kql 文件内容)
            user_question: 用户的问题或修改要求 (例如: "只显示Python SDK的数据", "过去7天的数据", "按产品分组显示前10个结果")
            
        Returns:
            修改后的 Kusto Query，保持原始查询结构尽量完整，只修改必要部分
        """
        return await mcp_tools.modify_kusto_query(original_kql, user_question)

    @mcp.tool()
    async def validateKustoSyntax(kql_query: str):
        """
        验证 Kusto Query 语法的基本正确性
        
        Args:
            kql_query: 要验证的 Kusto Query
            
        Returns:
            验证结果，包含语法错误信息（如果有）
        """
        try:
            # Basic syntax validation
            lines = kql_query.split('\n')
            errors = []
            warnings = []
            
            # Check for common syntax issues
            for i, line in enumerate(lines, 1):
                line_stripped = line.strip()
                if not line_stripped or line_stripped.startswith('//'):
                    continue
                    
                # Check for proper pipe operator usage
                if line_stripped.startswith('|') and i == 1:
                    errors.append(f"Line {i}: Query cannot start with pipe operator")
                
                # Check for let statement syntax
                if line_stripped.startswith('let ') and not ('=' in line and line.endswith(';')):
                    if not line.endswith('{') and not line.endswith('('):
                        warnings.append(f"Line {i}: Let statement should end with semicolon")
                
                # Check for function definition syntax
                if '= (' in line and not line.strip().endswith('{'):
                    warnings.append(f"Line {i}: Function definition should end with opening brace")
            
            return {
                "success": True,
                "is_valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "line_count": len([l for l in lines if l.strip() and not l.strip().startswith('//')])
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Validation error: {str(e)}",
                "is_valid": False
            }

    @mcp.tool()
    async def explainKustoQuery(kql_query: str):
        """
        解释 Kusto Query 的主要组成部分和功能
        
        Args:
            kql_query: 要解释的 Kusto Query
            
        Returns:
            查询解释，包含主要步骤和功能说明
        """
        try:
            lines = kql_query.split('\n')
            explanation = {
                "query_type": "Kusto Query Language (KQL)",
                "main_steps": [],
                "variables_defined": [],
                "functions_defined": [],
                "data_operations": [],
                "output_columns": []
            }
            
            current_function = None
            
            for line in lines:
                line_stripped = line.strip()
                if not line_stripped or line_stripped.startswith('//'):
                    continue
                
                # Identify let statements (variables)
                if line_stripped.startswith('let ') and '=' in line:
                    var_name = line_stripped.split(' ')[1].split('=')[0].strip()
                    if '(' in line:  # Function definition
                        explanation["functions_defined"].append({
                            "name": var_name,
                            "description": "User-defined function"
                        })
                        current_function = var_name
                    else:  # Variable definition
                        explanation["variables_defined"].append({
                            "name": var_name,
                            "description": "Variable definition"
                        })
                
                # Identify main query operations
                elif line_stripped.startswith('|'):
                    operation = line_stripped.split('|')[1].strip().split(' ')[0]
                    explanation["data_operations"].append({
                        "operation": operation,
                        "description": line_stripped
                    })
                
                # Identify data source
                elif 'Unionizer(' in line_stripped or any(table in line_stripped for table in ['Events', 'Requests', 'HttpIncomingRequests']):
                    explanation["main_steps"].append("Data source identification")
                
                # Identify project operations (output columns)
                elif '| project' in line_stripped:
                    cols = line_stripped.replace('| project', '').strip()
                    explanation["output_columns"] = [col.strip() for col in cols.split(',')]
            
            return {
                "success": True,
                "explanation": explanation,
                "summary": f"Query defines {len(explanation['variables_defined'])} variables, {len(explanation['functions_defined'])} functions, and performs {len(explanation['data_operations'])} data operations"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Explanation error: {str(e)}"
            }
    
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