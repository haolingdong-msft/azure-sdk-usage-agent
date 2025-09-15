"""
Main entry point for the MCP SQL Server with AI Query Helper
Includes executeSQLQuery, aiQueryHelper, generateSQLQuery, and executeAIGeneratedQuery tools
"""
import sys
from mcp.server.fastmcp import FastMCP
from ..config.config import MCP_PORT, SCHEMA_FILE_PATH
from ..data.schema_loader import SchemaLoader
from ..services.sql_mcp_tools import MCPTools

def create_mcp_server():
    """Create and configure the MCP server with AI helper and execute tools"""
    # Initialize FastMCP server
    mcp = FastMCP("mssqlQueryAI", stateless_http=True, port=MCP_PORT)
    
    # Initialize components
    schema_loader = SchemaLoader(SCHEMA_FILE_PATH)
    mcp_tools = MCPTools(schema_loader)
    
    # Register executeSQLQuery tool (unchanged)
    @mcp.tool()
    async def executeSQLQuery(table_name: str, columns: list, where_clause: str = "", order_clause: str = "", limit_clause: str = ""):
        """
        Execute a SQL query using the parsed components from parseUserQuery for MS SQL Server.
        Includes Azure AD authentication validation.

        Args:
            table_name: The name of the table to query
            columns: List of column names to select
            where_clause: SQL WHERE conditions (optional)
            order_clause: SQL ORDER BY clause (optional)  
            limit_clause: SQL LIMIT/TOP clause (optional)

        Returns:
            A JSON object containing the query results, or error information if authentication fails.
        """
        return await mcp_tools.execute_sql_with_auth(table_name, columns, where_clause, order_clause, limit_clause)
    
    # Register AI Query Helper tool 
    @mcp.tool()
    async def aiQueryHelper(user_question: str):
        """
        Helper function for AI agents to generate correct column names, table names, and conditions
        based on user questions and available database schema.

        Args:
            user_question: A natural language question about the data

        Returns:
            A JSON object containing schema and suggestions for AI query generation
        """
        return await mcp_tools.ai_query_helper(user_question)
    
    # Register new prompt-based SQL Query Generator tool
    @mcp.tool()
    async def generateSQLQuery(user_question: str, schema_hint: str = ""):
        """
        Generate AI prompt based on user question and SQL schema for intelligent SQL query generation.

        Args:
            user_question: A natural language question about the data
            schema_hint: Optional hint about which table or schema to focus on

        Returns:
            A JSON object containing AI prompt and schema context
        """
        try:
            print(f"🚀 Generating AI prompt for: {user_question}")
            if schema_hint:
                print(f"📋 Schema hint: {schema_hint}")

            # Get available tables
            enabled_tables = schema_loader.get_enabled_tables()
            
            # Format schema information
            schema_context = "# Available Database Tables and Schema\n\n"
            
            for table_key, table_info in enabled_tables.items():
                schema_context += f"## Table: {table_info.name}\n"
                schema_context += f"**Description**: {table_info.description}\n"
                schema_context += f"**Columns**: {', '.join(table_info.columns)}\n\n"
            
            # Build complete AI prompt
            prompt = f"""You are an expert SQL query generator. Based on the user's natural language question and the provided database schema, generate the appropriate SQL query parameters.

## User Question
{user_question}

## Schema Hint
{schema_hint if schema_hint else "No specific hint provided"}

## Database Schema
{schema_context}

## Task
Analyze the user question and generate a JSON response with the following structure:

```json
{{
    "table_name": "selected_table_name",
    "columns": ["column1", "column2", "column3"],
    "where_clause": "optional WHERE conditions",
    "order_clause": "optional ORDER BY clause", 
    "limit_clause": "optional TOP N or LIMIT N",
    "confidence": 0.85,
    "explanation": "Detailed explanation of the query logic and reasoning"
}}
```

## Guidelines
1. **Table Selection**: Choose the most appropriate table based on the user question and schema hint
2. **Column Selection**: Select relevant columns that answer the user's question
3. **WHERE Conditions**: Generate appropriate filters based on the question context
4. **Sorting**: Add ORDER BY if the question implies ranking or ordering
5. **Limiting**: Add TOP/LIMIT if the question asks for specific number of results
6. **Confidence**: Rate your confidence in the query accuracy (0.0 to 1.0)
7. **Explanation**: Provide clear reasoning for your choices

## Examples of Question Patterns
- "Show me the top 10..." → Add LIMIT and ORDER BY DESC
- "Find customers with..." → Focus on Customer columns and WHERE conditions
- "What happened this month?" → Add Month/Date filters
- "Most popular products" → Focus on Product columns with COUNT/SUM aggregation

Please analyze the question carefully and provide an accurate, executable SQL query structure."""

            # Return prompt and related info
            result = {
                "success": True,
                "prompt": prompt,
                "schema_context": schema_context,
                "user_question": user_question,
                "schema_hint": schema_hint,
                "instructions": {
                    "next_steps": [
                        "Send the 'prompt' to your AI service (OpenAI, Claude, etc.)",
                        "Parse the JSON response from AI",
                        "Use the parsed parameters with executeSQLQuery tool",
                        "Return the query results to user"
                    ],
                    "expected_ai_response": {
                        "format": "JSON object with table_name, columns, where_clause, order_clause, limit_clause, confidence, explanation"
                    },
                    "error_handling": "If AI response is malformed, use default values or ask user to rephrase question"
                },
                "available_tables": [
                    {
                        "name": table_info.name,
                        "description": table_info.description,
                        "columns": table_info.columns
                    }
                    for table_info in enabled_tables.values()
                ]
            }
            
            print(f"✅ Generated prompt with {len(enabled_tables)} available tables")
            return result
            
        except Exception as e:
            print(f"❌ Error generating prompt: {str(e)}")
            return {
                "success": False,
                "error": f"Error generating AI prompt: {str(e)}",
                "user_question": user_question,
                "schema_hint": schema_hint
            }

    # Register AI Response Processor and Query Executor tool
    @mcp.tool()
    async def executeAIGeneratedQuery(ai_response: str, user_question: str = ""):
        """
        Parse AI-generated SQL parameters and execute the query.

        Args:
            ai_response: JSON response from AI service containing SQL parameters
            user_question: Original user question (for context)

        Returns:
            A JSON object containing query results or error information
        """
        try:
            print(f"🤖 Processing AI response for query execution")
            
            # Parse AI response
            import json
            try:
                if isinstance(ai_response, str):
                    # Try to extract JSON from AI response
                    # Handle responses that might contain code blocks
                    if "```json" in ai_response:
                        json_start = ai_response.find("```json") + 7
                        json_end = ai_response.find("```", json_start)
                        ai_response = ai_response[json_start:json_end].strip()
                    elif "```" in ai_response:
                        json_start = ai_response.find("```") + 3
                        json_end = ai_response.rfind("```")
                        ai_response = ai_response[json_start:json_end].strip()
                    
                    ai_params = json.loads(ai_response)
                else:
                    ai_params = ai_response
                    
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"Failed to parse AI response as JSON: {str(e)}",
                    "ai_response": ai_response,
                    "user_question": user_question
                }
            
            # Validate required parameters
            required_fields = ["table_name", "columns"]
            for field in required_fields:
                if field not in ai_params:
                    return {
                        "success": False,
                        "error": f"Missing required field '{field}' in AI response",
                        "ai_response": ai_response,
                        "user_question": user_question
                    }
            
            # Extract parameters
            table_name = ai_params.get("table_name", "")
            columns = ai_params.get("columns", [])
            where_clause = ai_params.get("where_clause", "")
            order_clause = ai_params.get("order_clause", "")
            limit_clause = ai_params.get("limit_clause", "")
            confidence = ai_params.get("confidence", 0.5)
            explanation = ai_params.get("explanation", "")
            
            print(f"�� Parsed AI parameters:")
            print(f"  Table: {table_name}")
            print(f"  Columns: {columns}")
            print(f"  Confidence: {confidence}")
            
            # Build complete SQL for display
            sql_parts = []
            if limit_clause:
                sql_parts.append(f"SELECT {limit_clause} {', '.join(columns) if columns else '*'}")
            else:
                sql_parts.append(f"SELECT {', '.join(columns) if columns else '*'}")
            
            sql_parts.append(f"FROM {table_name}")
            
            if where_clause and where_clause.strip():
                sql_parts.append(f"WHERE {where_clause}")
            
            if order_clause and order_clause.strip():
                sql_parts.append(order_clause)
            
            generated_sql = ' '.join(sql_parts)
            print(f"📜 Generated SQL: {generated_sql}")
            
            # Execute query
            execution_result = await mcp_tools.execute_sql_with_auth(
                table_name=table_name,
                columns=columns,
                where_clause=where_clause,
                order_clause=order_clause,
                limit_clause=limit_clause
            )
            
            # Build return result
            if execution_result.get('success'):
                return {
                    "success": True,
                    "data": execution_result.get('data', []),
                    "generated_sql": generated_sql,
                    "ai_parameters": ai_params,
                    "row_count": len(execution_result.get('data', [])),
                    "confidence": confidence,
                    "explanation": explanation,
                    "user_question": user_question,
                    "execution_time": execution_result.get('execution_time', 'N/A')
                }
            else:
                return {
                    "success": False,
                    "error": execution_result.get('error', 'Query execution failed'),
                    "generated_sql": generated_sql,
                    "ai_parameters": ai_params,
                    "user_question": user_question
                }
                
        except Exception as e:
            print(f"❌ Error executing AI-generated query: {str(e)}")
            return {
                "success": False,
                "error": f"Error executing AI-generated query: {str(e)}",
                "ai_response": ai_response,
                "user_question": user_question
            }
    
    return mcp


def main():
    """Main entry point"""
    try:
        # Initialize and run the server
        print("Starting MCP MS SQL Server with AI Query Helper (executeSQLQuery + aiQueryHelper + generateSQLQuery + executeAIGeneratedQuery)...")
        mcp = create_mcp_server()
        mcp.run(transport="streamable-http")
    except Exception as e:
        print(f"Error while running MCP server: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
