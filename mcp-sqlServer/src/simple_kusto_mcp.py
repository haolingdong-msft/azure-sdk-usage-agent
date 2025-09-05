"""
Simplified Kusto MCP tool
Only responsible for reading sample.kql template and passing user questions, letting AI handle query generation
"""
import os
from typing import Any, Dict


class SimpleKustoMCP:
    """Simplified Kusto MCP tool class"""
    
    def __init__(self):
        self.sample_kql_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "reference", "samples", "sample.kql"
        )
    
    async def generate_kql_from_template(self, user_question: str) -> Dict[str, Any]:
        """
        Based on sample.kql template and user question, return structured data for AI processing
        
        Args:
            user_question: User's query requirement
            
        Returns:
            Structured data containing template and user question for AI processing
        """
        try:
            # Read sample.kql template
            sample_kql = self._read_sample_kql()
            
            # Return structured data for AI
            return {
                "success": True,
                "user_question": user_question,
                "sample_kql_template": sample_kql,
                "instructions": {
                    "task": "Generate a new KQL query based on the user question and sample template",
                    "requirements": [
                        "Use Unionizer('Requests', 'HttpIncomingRequests') as the data source",
                        "Include all necessary user-defined functions (GetProduct, GetProvider, etc.)",
                        "Maintain the overall structure of the sample query",
                        "Modify filters, aggregations, and output based on user question",
                        "Ensure proper time range filtering"
                    ],
                    "current_date": "2025-09-04"
                },
                "query_context": {
                    "data_source": "Kusto cluster",
                    "table": "Unionizer('Requests', 'HttpIncomingRequests')",
                    "available_fields": [
                        "TIMESTAMP", "userAgent", "subscriptionId", "operationName", 
                        "apiVersion", "targetResourceProvider", "httpMethod", 
                        "TaskName", "RoleLocation"
                    ],
                    "user_defined_functions": [
                        "GetProduct(userAgent) -> identifies SDK type",
                        "GetProvider(operationName) -> extracts resource provider", 
                        "GetTrackInfo(userAgent) -> identifies Track1/Track2",
                        "GetOSInfo(userAgent) -> identifies operating system",
                        "GetResource(operationName) -> extracts resource type"
                    ]
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error processing request: {str(e)}",
                "user_question": user_question,
                "suggestion": "Please check if sample.kql file exists and is readable"
            }
    
    def _read_sample_kql(self) -> str:
        """Read content of sample.kql file"""
        try:
            with open(self.sample_kql_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise Exception(f"Sample KQL file not found: {self.sample_kql_path}")
        except Exception as e:
            raise Exception(f"Error reading sample KQL file: {str(e)}")
    
    async def validate_kusto_syntax(self, kql_query: str) -> Dict[str, Any]:
        """
        Simple KQL syntax validation
        
        Args:
            kql_query: KQL query to validate
            
        Returns:
            Validation result
        """
        try:
            # Basic syntax check
            errors = []
            lines = kql_query.split('\n')
            
            # Check basic structure
            if not any('Unionizer' in line for line in lines):
                errors.append("Missing Unionizer data source")
            
            # Check necessary filter conditions
            if not any('where TIMESTAMP' in line for line in lines):
                errors.append("Missing timestamp filter")
            
            # Check syntax errors
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if line and not line.startswith('//') and not line.startswith('let'):
                    if line.endswith(','):
                        errors.append(f"Line {i}: Unexpected comma at end of line")
            
            return {
                "success": len(errors) == 0,
                "errors": errors,
                "query_length": len(kql_query),
                "line_count": len(lines),
                "validation_note": "Basic syntax validation only"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Validation error: {str(e)}"
            }
    
    async def explain_kusto_query(self, kql_query: str) -> Dict[str, Any]:
        """
        Explain basic components of KQL query
        
        Args:
            kql_query: KQL query to explain
            
        Returns:
            Query explanation
        """
        try:
            lines = [line.strip() for line in kql_query.split('\n') if line.strip()]
            
            analysis = {
                "query_structure": {
                    "total_lines": len(lines),
                    "has_let_statements": any(line.startswith('let ') for line in lines),
                    "has_functions": any('= (' in line for line in lines),
                    "data_source": "Unionizer" if any('Unionizer' in line for line in lines) else "Unknown",
                    "has_time_filter": any('TIMESTAMP' in line for line in lines),
                    "has_aggregation": any('summarize' in line.lower() for line in lines)
                },
                "operations": [],
                "functions_used": []
            }
            
            # Analyze query operations
            for line in lines:
                if line.startswith('let '):
                    analysis["operations"].append(f"Function definition: {line[:50]}...")
                elif line.startswith('| where'):
                    analysis["operations"].append(f"Filter: {line}")
                elif line.startswith('| extend'):
                    analysis["operations"].append(f"Extend: {line}")
                elif line.startswith('| summarize'):
                    analysis["operations"].append(f"Aggregation: {line}")
                elif line.startswith('| project'):
                    analysis["operations"].append(f"Projection: {line}")
                elif line.startswith('| order'):
                    analysis["operations"].append(f"Ordering: {line}")
            
            return {
                "success": True,
                "analysis": analysis,
                "explanation": "Query structure and operations identified"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error explaining query: {str(e)}"
            }
