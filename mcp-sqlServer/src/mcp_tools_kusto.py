"""
MCP Tools implementation for Kusto Query operations
Specialized tools for KQL query modification, validation, and explanation
"""
import re
import json
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta


class MCPToolsKusto:
    """MCP Tools for Kusto Query operations"""
    
    def __init__(self):
        # Common KQL operators and functions for syntax validation
        self.kql_operators = {
            'logical': ['and', 'or', 'not'],
            'comparison': ['==', '!=', '<', '>', '<=', '>=', '=~', '!~', 'contains', 'startswith', 'endswith'],
            'aggregation': ['count', 'sum', 'avg', 'min', 'max', 'dcount', 'percentile'],
            'datetime': ['ago', 'now', 'datetime', 'timespan', 'between'],
            'string': ['extract', 'split', 'strcat', 'strlen', 'tolower', 'toupper'],
            'array': ['mvexpand', 'array_length', 'array_slice']
        }
        
        # Common KQL table operators
        self.table_operators = [
            'where', 'project', 'extend', 'summarize', 'sort', 'order', 'top', 'take',
            'limit', 'distinct', 'join', 'union', 'render', 'let', 'datatable'
        ]
        
        # Sample Azure service data for context
        self.azure_services = [
            'Microsoft.Compute', 'Microsoft.Storage', 'Microsoft.Network', 'Microsoft.Web',
            'Microsoft.KeyVault', 'Microsoft.Sql', 'Microsoft.DocumentDB', 'Microsoft.ServiceBus'
        ]
        
        # Common product patterns for Azure SDK usage analytics
        self.product_patterns = [
            'Python-SDK', 'Java-SDK', 'JavaScript-SDK', 'DotNet-SDK', 'Go-SDK',
            'CLI', 'PowerShell', 'REST-API', 'Portal', 'ARM-Template'
        ]

    async def modify_kusto_query(self, original_kql: str, user_question: str) -> Dict[str, Any]:
        """
        Generate a modified Kusto Query based on the user's existing query and requirements.
        
        Args:
            original_kql: Original Kusto Query (.kql file content)
            user_question: User's question or modification requirements
            
        Returns:
            Modified Kusto Query with explanation of changes
        """
        try:
            print(f"Modifying KQL query based on: {user_question}")
            
            # Analyze the original query structure
            query_analysis = self._analyze_kql_structure(original_kql)
            
            # Parse user requirements
            modifications = self._parse_modification_requirements(user_question)
            
            # Apply modifications to the query
            modified_kql = self._apply_modifications(original_kql, modifications, query_analysis)
            
            # Generate explanation
            explanation = self._generate_modification_explanation(modifications, query_analysis)
            
            return {
                "success": True,
                "original_kql": original_kql,
                "modified_kql": modified_kql,
                "user_request": user_question,
                "modifications_applied": modifications,
                "explanation": explanation,
                "query_analysis": query_analysis,
                "performance_tips": self._get_performance_tips(modified_kql)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error modifying KQL query: {str(e)}",
                "original_kql": original_kql,
                "user_request": user_question,
                "suggestions": [
                    "Ensure the original KQL query is syntactically correct",
                    "Be specific about what you want to modify",
                    "Common modifications: add time filters, change aggregations, filter by products"
                ]
            }

    def _analyze_kql_structure(self, kql: str) -> Dict[str, Any]:
        """Analyze the structure of a KQL query"""
        lines = [line.strip() for line in kql.split('\n') if line.strip() and not line.strip().startswith('//')]
        
        analysis = {
            "has_let_statements": False,
            "has_functions": False,
            "data_sources": [],
            "table_operators": [],
            "aggregations": [],
            "time_filters": [],
            "variables": [],
            "functions": [],
            "main_query_start": 0
        }
        
        for i, line in enumerate(lines):
            # Check for let statements
            if line.startswith('let '):
                analysis["has_let_statements"] = True
                if '(' in line and ')' in line:
                    # Function definition
                    func_name = line.split(' ')[1].split('(')[0]
                    analysis["functions"].append(func_name)
                    analysis["has_functions"] = True
                else:
                    # Variable definition
                    var_name = line.split(' ')[1].split('=')[0].strip()
                    analysis["variables"].append(var_name)
            
            # Check for data sources
            elif any(source in line for source in ['Unionizer(', 'Events', 'Requests', 'HttpIncomingRequests']):
                if 'Unionizer(' in line:
                    analysis["data_sources"].append("Unionizer")
                else:
                    for source in ['Events', 'Requests', 'HttpIncomingRequests']:
                        if source in line:
                            analysis["data_sources"].append(source)
                if not analysis["has_let_statements"]:
                    analysis["main_query_start"] = i
            
            # Check for table operators
            elif line.startswith('|'):
                operator = line.split('|')[1].strip().split(' ')[0]
                analysis["table_operators"].append(operator)
                
                # Check for aggregations
                if operator == 'summarize':
                    agg_functions = []
                    for agg in self.kql_operators['aggregation']:
                        if agg in line:
                            agg_functions.append(agg)
                    analysis["aggregations"].extend(agg_functions)
                
                # Check for time filters
                if operator == 'where' and any(time_func in line for time_func in ['ago(', 'datetime(', 'between(']):
                    analysis["time_filters"].append(line)
        
        return analysis

    def _parse_modification_requirements(self, user_question: str) -> Dict[str, Any]:
        """Parse user requirements for query modification"""
        question_lower = user_question.lower()
        modifications = {
            "add_time_filter": None,
            "change_aggregation": None,
            "add_product_filter": None,
            "change_grouping": None,
            "add_ordering": None,
            "change_limit": None,
            "add_fields": [],
            "filter_conditions": []
        }
        
        # Time filter modifications
        if any(phrase in question_lower for phrase in ['past 7 days', 'last 7 days', 'past week']):
            modifications["add_time_filter"] = "ago(7d)"
        elif any(phrase in question_lower for phrase in ['past 30 days', 'last 30 days', 'past month']):
            modifications["add_time_filter"] = "ago(30d)"
        elif any(phrase in question_lower for phrase in ['today', 'past 24 hours']):
            modifications["add_time_filter"] = "ago(1d)"
        elif any(phrase in question_lower for phrase in ['this year', '2025']):
            modifications["add_time_filter"] = "datetime(2025-01-01)"
        
        # Product filtering
        for product in self.product_patterns:
            if product.lower() in question_lower:
                modifications["add_product_filter"] = product
                break
        
        if any(phrase in question_lower for phrase in ['python sdk', 'python']):
            modifications["add_product_filter"] = "Python-SDK"
        elif any(phrase in question_lower for phrase in ['java sdk', 'java']):
            modifications["add_product_filter"] = "Java-SDK"
        elif any(phrase in question_lower for phrase in ['javascript sdk', 'js sdk', 'node']):
            modifications["add_product_filter"] = "JavaScript-SDK"
        elif any(phrase in question_lower for phrase in ['.net sdk', 'dotnet sdk', 'c#']):
            modifications["add_product_filter"] = "DotNet-SDK"
        
        # Aggregation changes
        if any(phrase in question_lower for phrase in ['top 10', 'top ten']):
            modifications["change_limit"] = "10"
            modifications["add_ordering"] = "desc"
        elif any(phrase in question_lower for phrase in ['top 5', 'top five']):
            modifications["change_limit"] = "5"
            modifications["add_ordering"] = "desc"
        elif 'count' in question_lower:
            modifications["change_aggregation"] = "count()"
        elif 'sum' in question_lower:
            modifications["change_aggregation"] = "sum(RequestCount)"
        
        # Grouping changes
        if 'group by product' in question_lower:
            modifications["change_grouping"] = "Product"
        elif 'group by customer' in question_lower:
            modifications["change_grouping"] = "Customer"
        elif 'group by month' in question_lower:
            modifications["change_grouping"] = "Month"
        
        return modifications

    def _apply_modifications(self, original_kql: str, modifications: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Apply modifications to the KQL query"""
        lines = original_kql.split('\n')
        modified_lines = []
        
        # Track if we've added modifications
        added_time_filter = False
        added_product_filter = False
        modified_summarize = False
        
        for i, line in enumerate(lines):
            current_line = line
            
            # Add time filter to where clause
            if (line.strip().startswith('| where') and 
                modifications["add_time_filter"] and 
                not added_time_filter):
                
                if 'ago(' not in line and 'datetime(' not in line:
                    if modifications["add_time_filter"].startswith("ago("):
                        current_line = f"{line} and TIMESTAMP >= {modifications['add_time_filter']}"
                    else:
                        current_line = f"{line} and TIMESTAMP >= {modifications['add_time_filter']}"
                    added_time_filter = True
            
            # Add product filter
            if (line.strip().startswith('| where') and 
                modifications["add_product_filter"] and 
                not added_product_filter):
                
                if 'Product' not in line:
                    current_line = f"{current_line} and Product == \"{modifications['add_product_filter']}\""
                    added_product_filter = True
            
            # Modify summarize clause
            if (line.strip().startswith('| summarize') and 
                (modifications["change_aggregation"] or modifications["change_grouping"]) and
                not modified_summarize):
                
                if modifications["change_aggregation"]:
                    # Replace aggregation function
                    if 'count()' in line and modifications["change_aggregation"] != "count()":
                        current_line = line.replace('count()', modifications["change_aggregation"])
                    elif modifications["change_aggregation"] == "count()" and 'sum(' in line:
                        current_line = re.sub(r'sum\([^)]+\)', 'count()', current_line)
                
                if modifications["change_grouping"]:
                    # Add or modify grouping
                    if ' by ' not in line:
                        current_line = f"{current_line} by {modifications['change_grouping']}"
                    else:
                        # Replace existing grouping
                        parts = current_line.split(' by ')
                        current_line = f"{parts[0]} by {modifications['change_grouping']}"
                
                modified_summarize = True
            
            # Add top/take clause
            if (line.strip().startswith('| summarize') and 
                modifications["change_limit"] and 
                i + 1 < len(lines) and 
                not lines[i + 1].strip().startswith('| top') and
                not lines[i + 1].strip().startswith('| take')):
                
                modified_lines.append(current_line)
                modified_lines.append(f"| top {modifications['change_limit']} by RequestCount desc")
                continue
            
            modified_lines.append(current_line)
        
        # Add time filter if no where clause exists
        if (modifications["add_time_filter"] and not added_time_filter and 
            not any('| where' in line for line in modified_lines)):
            
            # Insert after data source
            for i, line in enumerate(modified_lines):
                if any(source in line for source in analysis.get("data_sources", [])):
                    time_filter = f"| where TIMESTAMP >= {modifications['add_time_filter']}"
                    modified_lines.insert(i + 1, time_filter)
                    break
        
        # Add product filter if no where clause exists
        if (modifications["add_product_filter"] and not added_product_filter and 
            not any('Product' in line for line in modified_lines)):
            
            # Insert after time filter or data source
            insert_index = -1
            for i, line in enumerate(modified_lines):
                if '| where' in line or any(source in line for source in analysis.get("data_sources", [])):
                    insert_index = i
            
            if insert_index >= 0:
                product_filter = f"| where Product == \"{modifications['add_product_filter']}\""
                if '| where' in modified_lines[insert_index]:
                    modified_lines[insert_index] = f"{modified_lines[insert_index]} and Product == \"{modifications['add_product_filter']}\""
                else:
                    modified_lines.insert(insert_index + 1, product_filter)
        
        return '\n'.join(modified_lines)

    def _generate_modification_explanation(self, modifications: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Generate explanation of what was modified"""
        explanations = []
        
        if modifications["add_time_filter"]:
            explanations.append(f"Added time filter: {modifications['add_time_filter']}")
        
        if modifications["add_product_filter"]:
            explanations.append(f"Added product filter: {modifications['add_product_filter']}")
        
        if modifications["change_aggregation"]:
            explanations.append(f"Changed aggregation to: {modifications['change_aggregation']}")
        
        if modifications["change_grouping"]:
            explanations.append(f"Changed grouping to: {modifications['change_grouping']}")
        
        if modifications["change_limit"]:
            explanations.append(f"Limited results to top {modifications['change_limit']}")
        
        if not explanations:
            explanations.append("No modifications were applied - query structure maintained")
        
        return "; ".join(explanations)

    def _get_performance_tips(self, kql: str) -> List[str]:
        """Generate performance tips for the KQL query"""
        tips = []
        
        # Check for time filters early in query
        lines = [line.strip() for line in kql.split('\n') if line.strip()]
        has_early_time_filter = False
        
        for i, line in enumerate(lines[:5]):  # Check first 5 lines
            if '| where' in line and ('ago(' in line or 'datetime(' in line):
                has_early_time_filter = True
                break
        
        if not has_early_time_filter:
            tips.append("Consider adding time filters early in the query to improve performance")
        
        # Check for specific column selection
        has_project = any('| project' in line for line in lines)
        if not has_project:
            tips.append("Use '| project' to select only needed columns")
        
        # Check for limit/top
        has_limit = any(op in kql for op in ['| top', '| take', '| limit'])
        if not has_limit and '| summarize' not in kql:
            tips.append("Consider adding '| top N' or '| take N' to limit results")
        
        if not tips:
            tips.append("Query structure looks optimized for performance")
        
        return tips

    async def validate_kusto_syntax(self, kql_query: str) -> Dict[str, Any]:
        """
        Validate the basic syntax correctness of a Kusto Query
        
        Args:
            kql_query: Kusto Query to validate
            
        Returns:
            Validation result containing syntax error information
        """
        try:
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
                    # Check if this is the first non-comment, non-let line
                    prev_lines = [l.strip() for l in lines[:i-1] if l.strip() and not l.strip().startswith('//')]
                    if not any(l.startswith('let ') or any(source in l for source in ['Unionizer(', 'Events']) for l in prev_lines):
                        errors.append(f"Line {i}: Query cannot start with pipe operator without a data source")
                
                # Check for let statement syntax
                if line_stripped.startswith('let '):
                    if not ('=' in line and (line.endswith(';') or line.endswith('{') or line.endswith('('))):
                        warnings.append(f"Line {i}: Let statement should end with semicolon, opening brace, or parenthesis")
                
                # Check for function definition syntax
                if '= (' in line and line.startswith('let ') and not (line.strip().endswith('{') or '};' in line):
                    warnings.append(f"Line {i}: Function definition should be properly closed")
                
                # Check for common operator mistakes
                if '| where' in line:
                    # Check for single = instead of ==
                    if re.search(r'\w\s*=\s*\w', line) and '==' not in line:
                        warnings.append(f"Line {i}: Use '==' for comparison, not '='")
                
                # Check for proper string quotes
                if 'where' in line and '"' in line:
                    # Count quotes to ensure they're balanced
                    quote_count = line.count('"')
                    if quote_count % 2 != 0:
                        errors.append(f"Line {i}: Unbalanced quotes in string literals")
            
            return {
                "success": True,
                "is_valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "line_count": len([l for l in lines if l.strip() and not l.strip().startswith('//')]),
                "syntax_check": "completed"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Validation error: {str(e)}",
                "is_valid": False
            }

    async def explain_kusto_query(self, kql_query: str) -> Dict[str, Any]:
        """
        Explain the main components and functionality of a Kusto Query
        
        Args:
            kql_query: Kusto Query to explain
            
        Returns:
            Query explanation including main steps and functional descriptions
        """
        try:
            lines = kql_query.split('\n')
            explanation = {
                "query_type": "Kusto Query Language (KQL)",
                "main_steps": [],
                "variables_defined": [],
                "functions_defined": [],
                "data_operations": [],
                "output_columns": [],
                "data_flow": []
            }
            
            current_function = None
            data_source_found = False
            
            for i, line in enumerate(lines):
                line_stripped = line.strip()
                if not line_stripped or line_stripped.startswith('//'):
                    continue
                
                # Identify let statements (variables and functions)
                if line_stripped.startswith('let '):
                    var_name = line_stripped.split(' ')[1].split('=')[0].strip()
                    if '(' in line:  # Function definition
                        explanation["functions_defined"].append({
                            "name": var_name,
                            "description": "User-defined function",
                            "line": i + 1
                        })
                        current_function = var_name
                    else:  # Variable definition
                        explanation["variables_defined"].append({
                            "name": var_name,
                            "description": "Variable definition",
                            "line": i + 1
                        })
                
                # Identify data sources
                elif any(source in line_stripped for source in ['Unionizer(', 'Events', 'Requests', 'HttpIncomingRequests']):
                    if not data_source_found:
                        explanation["main_steps"].append("Data source identification")
                        explanation["data_flow"].append("Start: Load data from source")
                        data_source_found = True
                
                # Identify main query operations
                elif line_stripped.startswith('|'):
                    operation = line_stripped.split('|')[1].strip().split(' ')[0]
                    explanation["data_operations"].append({
                        "operation": operation,
                        "description": line_stripped,
                        "line": i + 1
                    })
                    
                    # Add to data flow
                    if operation == 'where':
                        explanation["data_flow"].append("Filter: Apply WHERE conditions")
                    elif operation == 'project':
                        explanation["data_flow"].append("Select: Choose specific columns")
                        # Extract projected columns
                        cols = line_stripped.replace('| project', '').strip()
                        if cols:
                            explanation["output_columns"] = [col.strip() for col in cols.split(',')]
                    elif operation == 'summarize':
                        explanation["data_flow"].append("Aggregate: Group and summarize data")
                    elif operation in ['sort', 'order']:
                        explanation["data_flow"].append("Sort: Order results")
                    elif operation in ['top', 'take']:
                        explanation["data_flow"].append("Limit: Restrict number of results")
                    elif operation == 'extend':
                        explanation["data_flow"].append("Extend: Add calculated columns")
            
            # Generate summary
            summary_parts = []
            if explanation['variables_defined']:
                summary_parts.append(f"{len(explanation['variables_defined'])} variables")
            if explanation['functions_defined']:
                summary_parts.append(f"{len(explanation['functions_defined'])} functions")
            if explanation['data_operations']:
                summary_parts.append(f"{len(explanation['data_operations'])} data operations")
            
            explanation["summary"] = f"Query defines {', '.join(summary_parts) if summary_parts else 'no variables/functions'} and processes data through {len(explanation['data_flow'])} steps"
            
            return {
                "success": True,
                "explanation": explanation,
                "complexity": "Low" if len(explanation['data_operations']) < 5 else "Medium" if len(explanation['data_operations']) < 10 else "High"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Explanation error: {str(e)}"
            }

    def get_kql_examples(self) -> Dict[str, Any]:
        """Get example KQL queries for common scenarios"""
        examples = {
            "basic_filtering": {
                "title": "Basic Time and Product Filtering",
                "query": """Events
| where TIMESTAMP >= ago(7d)
| where Product == "Python-SDK"
| project TIMESTAMP, Product, Customer, RequestCount""",
                "description": "Filter data from past 7 days for Python SDK usage"
            },
            "aggregation": {
                "title": "Aggregation and Grouping",
                "query": """Events
| where TIMESTAMP >= ago(30d)
| summarize TotalRequests = sum(RequestCount) by Product, Customer
| top 10 by TotalRequests desc""",
                "description": "Get top 10 customers by total requests per product in the last 30 days"
            },
            "time_series": {
                "title": "Time Series Analysis",
                "query": """Events
| where TIMESTAMP >= ago(90d)
| summarize RequestCount = sum(RequestCount) by bin(TIMESTAMP, 1d), Product
| sort by TIMESTAMP asc""",
                "description": "Daily request counts by product over the last 90 days"
            },
            "complex_filtering": {
                "title": "Complex Filtering with Multiple Conditions",
                "query": """Events
| where TIMESTAMP between(datetime(2025-01-01) .. datetime(2025-01-31))
| where Product in ("Python-SDK", "Java-SDK", "JavaScript-SDK")
| where RequestCount > 100
| summarize AvgRequests = avg(RequestCount), MaxRequests = max(RequestCount) by Product
| order by AvgRequests desc""",
                "description": "January 2025 statistics for multiple SDKs with high usage"
            }
        }
        
        return {
            "success": True,
            "examples": examples,
            "tips": [
                "Use 'ago()' for relative time ranges",
                "Use 'between()' for specific date ranges",
                "Always filter by time early in the query for better performance",
                "Use 'summarize' for aggregations and grouping",
                "Use 'top' or 'take' to limit results"
            ]
        }
