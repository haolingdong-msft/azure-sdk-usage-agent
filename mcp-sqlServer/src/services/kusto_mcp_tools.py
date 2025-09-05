"""
KQL Generator MCP tool
Generates KQL queries based on sample templates and user questions through MCP protocol
"""
import os
from datetime import datetime
from typing import Any, Dict

class KQLGeneratorMCP:
    """KQL Generator MCP tool for template-based query generation"""
    
    def __init__(self):
        self.sample_kql_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
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
                    "current_date": datetime.now().strftime("%Y-%m-%d")
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
