"""
Unified MCP Server that provides a single unified_query tool
Decides between SQL Server and Kusto based on the user question
"""
import sys
from mcp.server.fastmcp import FastMCP
from ..config.config import MCP_PORT, SCHEMA_FILE_PATH
from ..data.schema_loader import SchemaLoader
from ..services.sql_mcp_tools import MCPTools
from ..services.kusto_mcp_tools import KQLGeneratorMCP

def create_mcp_server():
    """Create and configure the MCP server with unified query tool"""
    # Initialize FastMCP server
    mcp = FastMCP("unifiedQueryServer", stateless_http=True, port=MCP_PORT)
    
    # Initialize components
    schema_loader = SchemaLoader(SCHEMA_FILE_PATH)
    mcp_tools = MCPTools(schema_loader)
    kusto_tools = KQLGeneratorMCP()
    
    # Register the unified query tool
    @mcp.tool()
    async def unified_query(user_question: str):
        """
        Unified MCP tool that decides between SQL Server and Kusto based on user question.
        
        Args:
            user_question: A natural language question about the data
            
        Returns:
            A JSON object containing:
            - type: "sql" | "kusto" | "error"
            - query: the generated query string (only if type is sql or kusto)
            - message: error message if type=error
            - reasoning: explanation of why this query type was chosen (optional)
        """
        try:
            print(f"Processing unified query: {user_question}")
            
            # Call the decision and query generation function
            # The function will handle schema loading internally
            result = await mcp_tools.decide_and_generate_query(user_question)
            
            return result
            
        except Exception as e:
            print(f"Error in unified_query tool: {str(e)}")
            return {
                "type": "error",
                "message": f"Error processing unified query: {str(e)}"
            }
    
    # Register smart query execution tool that tries SQL first, then KQL
    @mcp.tool()
    async def smart_query_execution(user_question: str):
        """
        Smart query execution that automatically tries SQL first, then falls back to KQL if SQL fails.
        This is a higher-level tool that combines unified_query decision making with automatic fallback.
        
        Args:
            user_question: A natural language question about the data
            
        Returns:
            A JSON object containing the execution results, with details about which method was used
        """
        try:
            print(f"🧠 Smart query execution for: {user_question}")
            
            # Step 1: Get the unified query decision
            decision_result = await mcp_tools.decide_and_generate_query(user_question)
            
            if decision_result.get("type") == "sql":
                print("📊 Decision: SQL query recommended")
                
                # Extract SQL components from the decision
                mcp_params = decision_result.get("mcp_tool_params", {})
                table_name = mcp_params.get("table_name", "")
                columns = mcp_params.get("columns", [])
                where_clause = mcp_params.get("where_clause", "")
                order_clause = mcp_params.get("order_clause", "")
                limit_clause = mcp_params.get("limit_clause", "")
                
                if table_name and columns:
                    # Try SQL execution with automatic KQL fallback
                    sql_result = await mcp_tools.execute_sql_with_auth(table_name, columns, where_clause, order_clause, limit_clause)
                    
                    if sql_result.get("success", False):
                        return {
                            "method_used": "sql",
                            "execution_result": sql_result,
                            "decision_details": decision_result,
                            "message": "Successfully executed SQL query"
                        }
                    else:
                        print("❌ SQL execution failed, trying KQL fallback...")
                        # SQL failed, try KQL
                        kql_result = await kusto_tools.generate_kql_from_template(user_question)
                        return {
                            "method_used": "kql_fallback",
                            "sql_failure": sql_result,
                            "kql_result": kql_result,
                            "decision_details": decision_result,
                            "message": "SQL execution failed, generated KQL query as alternative"
                        }
                else:
                    print("⚠️ SQL decision made but missing components, trying KQL...")
                    # Missing SQL components, try KQL
                    kql_result = await kusto_tools.generate_kql_from_template(user_question)
                    return {
                        "method_used": "kql_fallback",
                        "reason": "Incomplete SQL components",
                        "kql_result": kql_result,
                        "decision_details": decision_result,
                        "message": "SQL components incomplete, generated KQL query instead"
                    }
                    
            elif decision_result.get("type") == "kusto":
                print("📈 Decision: KQL query recommended")
                # Direct KQL generation
                kql_result = await kusto_tools.generate_kql_from_template(user_question)
                return {
                    "method_used": "kql_direct",
                    "kql_result": kql_result,
                    "decision_details": decision_result,
                    "message": "Generated KQL query as recommended by decision engine"
                }
            else:
                print("❓ Decision unclear, trying both approaches...")
                # Decision was unclear, try SQL first, then KQL
                # Attempt a generic SQL approach
                try:
                    # Parse the question to extract potential SQL components
                    parse_result = await mcp_tools.parse_user_query(user_question)
                    if parse_result.get("success") and parse_result.get("table_name"):
                        sql_result = await mcp_tools.execute_sql_with_auth(
                            parse_result["table_name"],
                            parse_result.get("columns", ["*"]),
                            parse_result.get("where_clause", ""),
                            parse_result.get("order_clause", ""),
                            parse_result.get("limit_clause", "")
                        )
                        if sql_result.get("success", False):
                            return {
                                "method_used": "sql_parsed",
                                "execution_result": sql_result,
                                "parse_result": parse_result,
                                "decision_details": decision_result,
                                "message": "Used SQL query parsing as fallback"
                            }
                except Exception as parse_e:
                    print(f"SQL parsing failed: {parse_e}")
                
                # If all else fails, use KQL
                kql_result = await kusto_tools.generate_kql_from_template(user_question)
                return {
                    "method_used": "kql_final_fallback",
                    "kql_result": kql_result,
                    "decision_details": decision_result,
                    "message": "All SQL approaches failed, using KQL as final option"
                }
                
        except Exception as e:
            print(f"❌ Error in smart_query_execution: {str(e)}")
            return {
                "method_used": "error",
                "error": f"Smart query execution failed: {str(e)}",
                "message": "Both SQL and KQL approaches encountered errors"
            }
    
    # Register executeSQLQuery tool with fallback to KQL (enhanced version)
    # This allows users to execute SQL queries, with automatic fallback to KQL generation if SQL fails
    @mcp.tool()
    async def executeSQLQuery(table_name: str, columns: list, where_clause: str = "", order_clause: str = "", limit_clause: str = "", original_question: str = ""):
        """
        Execute a SQL query using the parsed components from parseUserQuery for MS SQL Server.
        Includes Azure AD authentication validation. If SQL execution fails, automatically attempts 
        to generate a KQL query as fallback.

        Args:
            table_name: The name of the table to query
            columns: List of column names to select
            where_clause: SQL WHERE conditions (optional)
            order_clause: SQL ORDER BY clause (optional)  
            limit_clause: SQL LIMIT/TOP clause (optional)
            original_question: The original user question (optional, used for KQL fallback)

        Returns:
            A JSON object containing the query results, or KQL generation if SQL fails.
        """
        try:
            # First attempt: Execute SQL query
            print(f"🔍 Attempting SQL query execution...")
            sql_result = await mcp_tools.execute_sql_with_auth(table_name, columns, where_clause, order_clause, limit_clause)
            
            # Check if SQL query was successful
            if sql_result.get("success", False):
                print("✅ SQL query executed successfully")
                return sql_result
            else:
                print(f"❌ SQL query failed: {sql_result.get('error', 'Unknown error')}")
                
                # Fallback: Try KQL generation if we have the original question
                if original_question:
                    print("🔄 Falling back to KQL generation...")
                    kql_result = await kusto_tools.generate_kql_from_template(original_question)
                    
                    # Return combined result showing SQL failure and KQL fallback
                    return {
                        "sql_execution": sql_result,
                        "fallback_method": "kql_generation",
                        "kql_result": kql_result,
                        "message": "SQL query failed, generated KQL query as alternative",
                        "recommendation": "Use the generated KQL query in your Kusto/Azure Data Explorer environment"
                    }
                else:
                    # No original question provided, construct one from SQL components
                    constructed_question = f"Show {', '.join(columns)} from {table_name}"
                    if where_clause:
                        constructed_question += f" where {where_clause}"
                    
                    print(f"🔄 Falling back to KQL generation with constructed question: {constructed_question}")
                    kql_result = await kusto_tools.generate_kql_from_template(constructed_question)
                    
                    return {
                        "sql_execution": sql_result,
                        "fallback_method": "kql_generation",
                        "kql_result": kql_result,
                        "constructed_question": constructed_question,
                        "message": "SQL query failed, generated KQL query as alternative based on SQL components",
                        "recommendation": "Use the generated KQL query in your Kusto/Azure Data Explorer environment"
                    }
                    
        except Exception as e:
            print(f"❌ Error in executeSQLQuery with fallback: {str(e)}")
            
            # Even in case of exception, try KQL fallback if possible
            if original_question:
                try:
                    print("🔄 Exception occurred, attempting KQL fallback...")
                    kql_result = await kusto_tools.generate_kql_from_template(original_question)
                    return {
                        "sql_execution": {"success": False, "error": f"Exception: {str(e)}"},
                        "fallback_method": "kql_generation", 
                        "kql_result": kql_result,
                        "message": "SQL execution threw exception, generated KQL query as alternative",
                        "recommendation": "Use the generated KQL query in your Kusto/Azure Data Explorer environment"
                    }
                except Exception as kql_e:
                    print(f"❌ KQL fallback also failed: {str(kql_e)}")
            
            return {
                "success": False,
                "error": f"Both SQL execution and KQL fallback failed: {str(e)}",
                "sql_attempted": True,
                "kql_fallback_attempted": bool(original_question)
            }
    
    # Register generateKQLFromTemplate tool (adapted from kusto_server.py)
    # This allows users to generate KQL queries from templates
    @mcp.tool()
    async def generateKQLFromTemplate(user_question: str):
        """
        Generate KQL query based on sample.kql template and user question
        
        This tool will:
        1. Read reference/samples/sample.kql as template
        2. Return user question and template together to AI
        3. Let AI generate new KQL query based on template and question
        
        Args:
            user_question: User's query requirement (e.g.: "Show percentage analysis of Go SDK resource providers last month")
            
        Returns:
            Structured data containing template and user question for AI to generate new KQL query
        """
        return await kusto_tools.generate_kql_from_template(user_question)
    
    return mcp


def main():
    """Main entry point for the unified MCP server"""
    try:
        print("Starting Unified MCP Server with comprehensive query tools...")
        print("Available tools:")
        print("  - unified_query: Decides between SQL/KQL and generates queries")
        print("  - smart_query_execution: Automatically tries SQL first, falls back to KQL")
        print("  - executeSQLQuery: Executes SQL queries with automatic KQL fallback")
        print("  - generateKQLFromTemplate: Generates KQL queries from templates")
        
        # Initialize and run the server
        mcp = create_mcp_server()
        mcp.run(transport="streamable-http")
        
    except KeyboardInterrupt:
        print("\nShutting down Unified MCP Server...")
        # Clean up SQL client if needed
        MCPTools.cleanup_sql_client()
        
    except Exception as e:
        print(f"Error while running Unified MCP server: {e}", file=sys.stderr)
        # Clean up SQL client if needed
        MCPTools.cleanup_sql_client()


if __name__ == "__main__":
    main()