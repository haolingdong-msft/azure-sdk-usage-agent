"""
简化的 Kusto Query 修改 MCP 工具
正确的MCP设计：返回结构化数据给AI助手处理，而不是直接调用AI API
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
    
    async def generate_kusto_query(self, user_question: str) -> Dict[str, Any]:
        """
        根据用户问题直接生成新的KQL查询
        
        Args:
            user_question: 用户的查询需求
            
        Returns:
            包含生成的KQL查询的结构化数据
        """
        try:
            print(f"生成KQL查询，用户需求: {user_question}")
            
            # 根据用户问题生成KQL查询
            generated_kql = self._generate_kql_for_question(user_question)
            
            result = {
                "success": True,
                "user_question": user_question,
                "generated_kql": generated_kql,
                "explanation": f"根据用户需求生成的KQL查询: {user_question}",
                "query_type": "Kusto Query Language (KQL)",
                "estimated_execution_time": "Fast"
            }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"生成KQL查询时出错: {str(e)}",
                "user_question": user_question,
                "suggestion": "请重新描述查询需求"
            }

    async def modify_kusto_query(self, original_kql: str, user_question: str) -> Dict[str, Any]:
        """
        根据用户问题重新生成KQL查询（不再是修改现有查询）
        
        Args:
            original_kql: 原始 KQL 查询（可能不需要，但保留兼容性）
            user_question: 用户的查询需求
            
        Returns:
            包含重新生成的KQL查询的结构化数据
        """
        try:
            print(f"重新生成KQL查询，用户需求: {user_question}")
            
            # 直接根据用户问题生成新的KQL查询，不依赖原始查询
            generated_kql = self._generate_kql_for_question(user_question)
            
            result = {
                "success": True,
                "user_question": user_question,
                "generated_kql": generated_kql,
                "explanation": f"根据用户需求重新生成的KQL查询: {user_question}",
                "query_type": "Kusto Query Language (KQL)",
                "approach": "complete_regeneration"
            }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"重新生成KQL查询时出错: {str(e)}",
                "user_question": user_question,
                "suggestion": "请重新描述查询需求"
            }
    
    def _generate_kql_for_question(self, user_question: str) -> str:
        """
        Generate a complete KQL query with user-defined functions for user questions
        
        Args:
            user_question: 用户的查询需求
            
        Returns:
            Complete KQL query string with GetProduct, GetProvider, GetResource functions
        """
        # Get time range
        start_time, end_time = self._generate_time_range(user_question)
        
        # Get product filtering  
        product_filter = self._get_product_filter(user_question)
        
        # Determine query type and aggregation
        query_type = self._detect_query_type(user_question.lower())
        
        # Generate complete query with all user-defined functions
        query = f"""// Generated KQL for: {user_question}
let currentDateTime = datetime("{end_time}");  
let startDateTime = datetime("{start_time}");
let endDateTime = currentDateTime;

// User-defined functions for data enrichment
let GetProduct = (UAString: string)  
{{  
    let userAgent = tolower(trim(" ", UAString));  
    let goSdkException = dynamic(["kubernetes-cloudprovider", "cluster-api-provider-azure", "cilium", "azure-metrics-exporter", "azure_prometheus_exporter", "cluster-image-registry-operator", "aad-pod-identity", "azure-service-operator"]);
    let netReg = extract(@"(microsoft\\.windowsazure\\.management|microsoft\\.azure\\.management)", 1, userAgent);  
    let jsRlcReg = "azsdk-js-arm-[a-z0-9]+-rest";  
    case(
        isempty(UAString), "",
        userAgent has "terraform", "Terraform",  
        userAgent has "ansible", "Ansible",  
        (userAgent has "azure-sdk-for-java" or userAgent has "azsdk-java") and userAgent has "auto-generated", "Java Fluent Lite",  
        userAgent has "azure-sdk-for-java" or userAgent has  "azsdk-java", "Java Fluent Premium",  
        netReg != "" and userAgent has "fluent", ".Net Fluent",  
        netReg != "" or userAgent has "azsdk-net", ".Net Code-gen",  
        userAgent has "azure-sdk-for-python" or userAgent has "azsdk-python", "Python-SDK",  
        userAgent has "azure-sdk-for-node", "JavaScript (Node.JS)",  
        userAgent matches regex jsRlcReg, "JavaScript RLC",  
        (userAgent has "ms-rest-js" and userAgent startswith "@azure/arm") or userAgent has "azsdk-js-arm", "JavaScript",  
        userAgent has "azure-sdk-for-ruby", "Ruby-SDK",  
        (userAgent has "azure-sdk-for-go" or userAgent has "azsdk-go") and array_index_of(goSdkException, userAgent) == -1, "Go-SDK",  
        userAgent has "azure-sdk-for-php", "PHP-SDK",  
        ""  
    )
}};

let GetTrackInfo = (UAString: string)   
{{  
    let userAgent = tolower(trim(" ", UAString));  
    let entityName = "Track1";  
    case(  
        userAgent has "azsdk-net", "Track2",  
        userAgent has "azsdk-python", "Track2",  
        userAgent has "azsdk-java", "Track2",  
        userAgent has "azsdk-go", "Track2",  
        userAgent has "azsdk-js", "Track2",  
        entityName  
    );
}};

let GetOSInfo = (UAString: string)   
{{  
    let userAgent = tolower(trim(" ", UAString));  
    let entityName = "Unknown";  
    case(  
        userAgent has "windows", "Windows",  
        userAgent has "linux", "Linux",  
        userAgent has "macos", "MacOS",
        userAgent has "mac os", "MacOS",
        entityName   
    ); 
}};

let GetProvider = (uriString: string)   
{{   
    let entityName = "";  
    let lowerURI = tolower(uriString);  
    let providerMatch = extract("/providers/([^?/]*)", 1, lowerURI);  
    let entityName1 = iff(providerMatch != "", providerMatch, entityName);  
    let containsResourceManager = iif(lowerURI contains "/resource-manager-rest-api/" or lowerURI contains "/providers?" or lowerURI contains "/resourcegroups/", "ResourceManager", entityName1);  
    tolower(containsResourceManager);
}};

let GetResource = (operationName: string)  
{{  
    let lowerOperationName = tolower(operationName);  
    let resourceMatch = extract("/providers/microsoft.([a-z]+)/([a-z]+)/", 2, lowerOperationName);  
    let entityName = iff(resourceMatch != "", resourceMatch, "");  
    let elements = split(lowerOperationName, "/");  
    let entityName2 = iif(entityName == "", elements[-1], entityName);
    tolower(entityName2); 
}};

// Main query with data enrichment
Unionizer("Requests", "HttpIncomingRequests")
| where TIMESTAMP >= startDateTime and TIMESTAMP < endDateTime
| where TaskName == "HttpIncomingRequestEndWithSuccess"
| where isnotempty(subscriptionId)
| extend Product = GetProduct(userAgent)
| extend Track = GetTrackInfo(userAgent)
| extend OS = GetOSInfo(userAgent)
| extend Provider = GetProvider(operationName)
| extend Resource = GetResource(operationName)
| where isnotnull(Product) and isnotempty(Product)
{self._get_product_where_filter(user_question)}
| where isnotempty(apiVersion)
| where isnotempty(Track)
| where isnotempty(targetResourceProvider)
| where isnotempty(Resource)
| where isnotempty(httpMethod)
{self._generate_aggregation_and_output(user_question, query_type)}"""
        
        return query

    def _generate_time_range(self, question: str) -> tuple[str, str]:
        """
        Generate simple start and end time strings based on user question
        
        Args:
            question: User question
            
        Returns:
            Tuple of (start_time, end_time) as ISO datetime strings
        """
        question_lower = question.lower()
        
        # Current time for reference
        current_time = "2025-09-04"
        
        # Parse time expressions
        if 'this month' in question_lower or '本月' in question_lower:
            return "2025-09-01", current_time
        elif 'last month' in question_lower or '上个月' in question_lower:
            return "2025-08-01", "2025-08-31"
        elif 'today' in question_lower or '今天' in question_lower:
            return current_time, current_time
        elif 'yesterday' in question_lower or '昨天' in question_lower:
            return "2025-09-03", "2025-09-03"
        elif 'this year' in question_lower or '今年' in question_lower or '2025' in question_lower:
            return "2025-01-01", current_time
        elif 'last year' in question_lower or '去年' in question_lower or '2024' in question_lower:
            return "2024-01-01", "2024-12-31"
        else:
            # Default: current month
            return "2025-09-01", current_time

    def _get_product_filter(self, question: str) -> dict:
        """
        Generate product filtering based on user question
        
        Args:
            question: User question
            
        Returns:
            Dictionary with product filter information
        """
        question_lower = question.lower()
        
        if 'go' in question_lower and 'sdk' in question_lower:
            return {
                'where_clause': '| where (tolower(userAgent) has "azure-sdk-for-go" or tolower(userAgent) has "azsdk-go")',
                'description': 'Go SDK'
            }
        elif 'python' in question_lower:
            return {
                'where_clause': '| where (tolower(userAgent) has "azure-sdk-for-python" or tolower(userAgent) has "azsdk-python")',
                'description': 'Python SDK'
            }
        elif 'javascript' in question_lower or ('js' in question_lower and 'sdk' in question_lower):
            return {
                'where_clause': '| where (tolower(userAgent) has "azsdk-js" or tolower(userAgent) has "ms-rest-js")',
                'description': 'JavaScript SDK'
            }
        elif 'java' in question_lower and 'javascript' not in question_lower:
            return {
                'where_clause': '| where (tolower(userAgent) has "azure-sdk-for-java" or tolower(userAgent) has "azsdk-java")',
                'description': 'Java SDK'
            }
        elif 'dotnet' in question_lower or '.net' in question_lower or 'c#' in question_lower:
            return {
                'where_clause': '| where tolower(userAgent) has "azsdk-net"',
                'description': '.NET SDK'
            }
        elif 'go' in question_lower:  # Fallback for 'go' without 'sdk'
            return {
                'where_clause': '| where (tolower(userAgent) has "azure-sdk-for-go" or tolower(userAgent) has "azsdk-go")',
                'description': 'Go SDK'
            }
        else:
            return {
                'where_clause': '',
                'description': 'All SDKs'
            }

    def _generate_summarize_project(self, question: str, detected_product: str) -> str:
        """
        根据用户问题生成summarize和project部分
        
        Args:
            question: 用户问题（小写）
            detected_product: 检测到的产品名
            
        Returns:
            summarize和project的KQL语句
        """
        # 如果是请求计数相关的查询
        if any(word in question for word in ['count', 'number', 'how many', '数量', '多少']):
            if detected_product:
                # 特定产品的总请求数
                return """| summarize TotalRequests = sum(counts)
| project TotalRequests"""
            else:
                # 按产品分组的请求数
                return """| summarize TotalRequests = sum(counts) by Product
| project Product, TotalRequests
| order by TotalRequests desc"""
        
        # 如果是订阅相关的查询
        elif any(word in question for word in ['subscription', 'customer', '订阅', '客户']):
            return """| summarize TotalRequests = sum(counts) by subscriptionId, Product
| project subscriptionId, Product, TotalRequests
| order by TotalRequests desc"""
        
        # 如果是API版本相关的查询
        elif any(word in question for word in ['api', 'version', 'endpoint', 'resource']):
            return """| summarize TotalRequests = sum(counts) by Product, apiVersion, targetResourceProvider
| project Product, apiVersion, targetResourceProvider, TotalRequests
| order by TotalRequests desc"""
        
        # 如果是操作系统相关的查询
        elif any(word in question for word in ['os', 'platform', 'windows', 'linux', 'mac']):
            return """| summarize TotalRequests = sum(counts) by Product, OS
| project Product, OS, TotalRequests
| order by TotalRequests desc"""
        
        # 如果是Track相关的查询
        elif any(word in question for word in ['track', 'version']):
            return """| summarize TotalRequests = sum(counts) by Product, Track
| project Product, Track, TotalRequests
| order by TotalRequests desc"""
        
        # 如果是详细分析查询
        elif any(word in question for word in ['detail', 'breakdown', 'analysis', '详细', '分析']):
            return """| summarize TotalRequests = sum(counts) by subscriptionId, Product, apiVersion, Track, OS, targetResourceProvider, Resource, httpMethod
| project subscriptionId, Product, TotalRequests, apiVersion, Track, OS, targetResourceProvider, Resource, httpMethod
| order by TotalRequests desc"""
        
        # 默认情况：简单的总计
        else:
            if detected_product:
                return """| summarize TotalRequests = sum(counts)
| project TotalRequests"""
            else:
                return """| summarize TotalRequests = sum(counts) by Product
| project Product, TotalRequests
| order by TotalRequests desc"""

    def _get_time_condition(self, question: str) -> str:
        """
        根据问题获取时间条件，但保持sample.kql的时间变量结构
        
        Args:
            question: 用户问题（小写）
            
        Returns:
            时间相关的说明（主要用于注释）
        """
        if 'this month' in question or '本月' in question:
            return "current month"
        elif 'last month' in question or '上个月' in question:
            return "last month"
        elif 'today' in question or '今天' in question:
            return "today"
        elif 'week' in question or '周' in question:
            return "this week"
        else:
            return "default range (last 30 days)"

    def _detect_time_range(self, question: str) -> Optional[Dict[str, str]]:
        """检测时间范围"""
        if 'last 3 months' in question:
            return {"start": "2025-06-01", "end": "2025-09-01"}
        elif 'last 6 months' in question:
            return {"start": "2025-03-01", "end": "2025-09-01"}
        elif 'this year' in question or '2025' in question:
            return {"start": "2025-01-01", "end": "2025-12-01"}
        elif 'last year' in question or '2024' in question:
            return {"start": "2024-01-01", "end": "2024-12-01"}
        return None

    def _detect_query_type(self, question: str) -> str:
        """检测查询类型"""
        if any(word in question for word in ['count', 'number', 'how many', '数量', '多少']):
            return 'count'
        elif any(word in question for word in ['trend', 'over time', '趋势', '变化']):
            return 'trend'
        elif any(word in question for word in ['top', 'most', '最多', '排名']):
            return 'ranking'
        elif any(word in question for word in ['percent', 'percentage', '百分比', '占比']):
            return 'percentage'
        return 'summary'

    def _get_product_where_filter(self, user_question: str) -> str:
        """
        基于用户问题生成产品过滤的 where 子句
        
        Args:
            user_question: 用户问题
            
        Returns:
            产品过滤的 where 子句
        """
        question_lower = user_question.lower()
        
        if 'go' in question_lower and 'sdk' in question_lower:
            return '| where Product == "Go-SDK"'
        elif 'python' in question_lower:
            return '| where Product == "Python-SDK"'
        elif 'javascript' in question_lower or ('js' in question_lower and 'sdk' in question_lower):
            return '| where Product == "JavaScript"'
        elif 'java' in question_lower and 'javascript' not in question_lower:
            return '| where Product has "Java"'
        elif 'dotnet' in question_lower or '.net' in question_lower or 'c#' in question_lower:
            return '| where Product has ".Net"'
        else:
            return ''  # 不过滤，显示所有产品

    def _generate_aggregation_and_output(self, user_question: str, query_type: str) -> str:
        """
        基于查询类型生成聚合和输出部分
        
        Args:
            user_question: 用户问题
            query_type: 查询类型
            
        Returns:
            聚合和输出的KQL语句
        """
        question_lower = user_question.lower()
        
        # 百分比相关查询
        if query_type == 'percentage' or any(word in question_lower for word in ['percent', 'percentage', '百分比', '占比']):
            if 'provider' in question_lower or 'resource provider' in question_lower:
                return """| summarize RequestCount = count() by Provider
| extend TotalRequests = toscalar(summarize sum(RequestCount))
| extend Percentage = round(100.0 * RequestCount / TotalRequests, 2)
| project Provider, RequestCount, Percentage
| order by Percentage desc"""
            elif 'resource' in question_lower and 'provider' not in question_lower:
                return """| summarize RequestCount = count() by Resource
| extend TotalRequests = toscalar(summarize sum(RequestCount))
| extend Percentage = round(100.0 * RequestCount / TotalRequests, 2)
| project Resource, RequestCount, Percentage
| order by Percentage desc"""
            else:
                return """| summarize RequestCount = count() by Product
| extend TotalRequests = toscalar(summarize sum(RequestCount))
| extend Percentage = round(100.0 * RequestCount / TotalRequests, 2)
| project Product, RequestCount, Percentage
| order by Percentage desc"""
        
        # 订阅相关查询
        elif any(word in question_lower for word in ['subscription', 'customer', '订阅', '客户']):
            return """| summarize RequestCount = count() by subscriptionId, Product, Provider
| project subscriptionId, Product, Provider, RequestCount
| order by RequestCount desc"""
        
        # API版本相关查询
        elif any(word in question_lower for word in ['api', 'version', 'endpoint']):
            return """| summarize RequestCount = count() by Product, apiVersion, Provider
| project Product, apiVersion, Provider, RequestCount
| order by RequestCount desc"""
        
        # 操作系统相关查询
        elif any(word in question_lower for word in ['os', 'platform', 'windows', 'linux', 'mac']):
            return """| summarize RequestCount = count() by Product, OS, Provider
| project Product, OS, Provider, RequestCount
| order by RequestCount desc"""
        
        # Track相关查询
        elif any(word in question_lower for word in ['track']):
            return """| summarize RequestCount = count() by Product, Track, Provider
| project Product, Track, Provider, RequestCount
| order by RequestCount desc"""
        
        # 详细分析查询
        elif any(word in question_lower for word in ['detail', 'breakdown', 'analysis', '详细', '分析']):
            return """| summarize RequestCount = count() by subscriptionId, Product, apiVersion, Track, OS, Provider, Resource, httpMethod
| project subscriptionId, Product, RequestCount, apiVersion, Track, OS, Provider, Resource, httpMethod
| order by RequestCount desc"""
        
        # 排名相关查询
        elif query_type == 'ranking' or any(word in question_lower for word in ['top', 'most', '最多', '排名']):
            limit_num = 10  # 默认前10
            if 'top 5' in question_lower or '前5' in question_lower:
                limit_num = 5
            elif 'top 20' in question_lower or '前20' in question_lower:
                limit_num = 20
            
            if 'provider' in question_lower:
                return f"""| summarize RequestCount = count() by Provider
| project Provider, RequestCount
| order by RequestCount desc
| take {limit_num}"""
            else:
                return f"""| summarize RequestCount = count() by Product
| project Product, RequestCount
| order by RequestCount desc
| take {limit_num}"""
        
        # 默认情况：基本计数
        else:
            if 'provider' in question_lower or 'resource provider' in question_lower:
                return """| summarize RequestCount = count() by Provider
| project Provider, RequestCount
| order by RequestCount desc"""
            else:
                return """| summarize RequestCount = count() by Product
| project Product, RequestCount
| order by RequestCount desc"""

    def _generate_ai_prompt(self, original_kql: str, user_question: str) -> str:
        """生成 AI 提示"""
        prompt = f"""你是一个Kusto Query Language (KQL)专家。请根据用户需求修改以下KQL查询。

用户需求: {user_question}

原始KQL查询:
```kql
{original_kql}
```

请按以下格式返回JSON响应:
{{
    "success": true,
    "modified_kql": "修改后的完整KQL查询",
    "explanation": "修改说明",
    "changes_made": ["具体修改点1", "具体修改点2"]
}}

修改要求:
1. 保持原查询的核心结构
2. 只修改与用户需求相关的部分
3. 确保修改后的KQL语法正确
4. 提供清晰的修改说明

常见修改类型:
- 时间过滤: 使用 ago(7d), ago(30d), ago(1d) 等
- 产品过滤: 添加或修改 Product == "产品名" 条件
- 结果限制: 添加 | top N by 列名 desc
- 聚合修改: 更改 count(), sum(), avg() 等函数
- 分组修改: 调整 summarize ... by 子句

请确保返回有效的JSON格式。"""
        
        return prompt
    
    async def validate_kusto_syntax(self, kql_query: str) -> Dict[str, Any]:
        """
        Validate the basic syntax correctness of a Kusto Query
        
        Args:
            kql_query: Kusto Query to validate
            
        Returns:
            Validation result containing syntax error information (if any)
        """
        try:
            lines = [line.strip() for line in kql_query.split('\n') if line.strip()]
            errors = []
            warnings = []
            
            for i, line in enumerate(lines, 1):
                # Skip comments
                if line.startswith('//'):
                    continue
                
                # Check for basic syntax issues
                if line.startswith('|') and i == 1:
                    errors.append(f"Line {i}: Query cannot start with pipe operator '|'")
                
                # Check parentheses matching
                if line.count('(') != line.count(')'):
                    errors.append(f"Line {i}: Unmatched parentheses")
                
                # Check for valid operators after pipe
                if line.startswith('|'):
                    operator = line.split('|')[1].strip().split(' ')[0]
                    if operator not in self.table_operators:
                        warnings.append(f"Line {i}: Unknown table operator '{operator}'")
                
                # Check for function definition syntax
                if line.startswith('let') and '(' in line:
                    if not line.rstrip().endswith(';'):
                        warnings.append(f"Line {i}: Function definition should be properly closed")
            
            return {
                "success": len(errors) == 0,
                "query": kql_query,
                "syntax_errors": errors,
                "warnings": warnings,
                "line_count": len(lines),
                "validation_summary": {
                    "total_errors": len(errors),
                    "total_warnings": len(warnings),
                    "is_valid": len(errors) == 0
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Validation error: {str(e)}",
                "query": kql_query
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
            lines = [line.strip() for line in kql_query.split('\n') if line.strip() and not line.strip().startswith('//')]
            
            explanation = {
                "success": True,
                "query": kql_query,
                "overview": "Query explanation",
                "data_sources": [],
                "data_operations": [],
                "variables_defined": [],
                "functions_defined": [],
                "output_description": "",
                "estimated_complexity": "Medium"
            }
            
            for i, line in enumerate(lines):
                if line.startswith('let '):
                    if '(' in line:  # Function definition
                        explanation["functions_defined"].append({
                            "name": line.split(' ')[1].split('(')[0],
                            "description": "User-defined function",
                            "line": i + 1
                        })
                    else:  # Variable definition
                        explanation["variables_defined"].append({
                            "name": line.split(' ')[1].split('=')[0].strip(),
                            "description": "Variable definition",
                            "line": i + 1
                        })
                
                elif any(source in line for source in ['Events', 'Requests', 'HttpIncomingRequests', 'Unionizer']):
                    explanation["data_sources"].append({
                        "source": line.strip(),
                        "description": "Data source query",
                        "line": i + 1
                    })
                
                elif line.startswith('|'):
                    operator = line.split('|')[1].strip().split(' ')[0]
                    explanation["data_operations"].append({
                        "operation": operator,
                        "description": f"Data transformation using '{operator}'",
                        "line": i + 1,
                        "details": line.strip()
                    })
            
            # Set complexity based on operations count
            explanation["estimated_complexity"] = "Low" if len(explanation['data_operations']) < 5 else "Medium" if len(explanation['data_operations']) < 10 else "High"
            
            return explanation
            
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
    
    def get_supported_modifications(self) -> Dict[str, Any]:
        """获取支持的修改类型说明"""
        return {
            "time_filters": {
                "description": "时间过滤修改",
                "examples": [
                    "过去7天的数据",
                    "最近30天",
                    "今天的记录",
                    "2025年的数据"
                ]
            },
            "product_filters": {
                "description": "产品过滤",
                "examples": [
                    "只显示Python SDK",
                    "Java相关数据",
                    "JavaScript SDK使用情况"
                ]
            },
            "result_limits": {
                "description": "结果数量限制",
                "examples": [
                    "前10个结果",
                    "显示前5名",
                    "限制100条记录"
                ]
            },
            "aggregations": {
                "description": "聚合函数修改",
                "examples": [
                    "改为计数统计",
                    "求和而不是计数",
                    "计算平均值"
                ]
            },
            "grouping": {
                "description": "分组方式修改",
                "examples": [
                    "按产品分组",
                    "按客户分组",
                    "按月份汇总"
                ]
            }
        }


# 使用示例
async def example_usage():
    """使用示例"""
    modifier = MCPToolsKusto()
    
    sample_kql = """let currentDateTime = datetime("2025-09-01");  
let startDateTime = datetime_add("day", -15, currentDateTime); 

Unionizer("Requests", "HttpIncomingRequests")
| where TIMESTAMP >= startDateTime 
| where TaskName == "HttpIncomingRequestEndWithSuccess"
| summarize counts = count() by subscriptionId, Product
| project subscriptionId, Product, counts"""
    
    user_question = "只显示Python SDK的数据，限制前10个结果"
    
    result = await modifier.modify_kusto_query(sample_kql, user_question)
    
    print("MCP工具返回结果:")
    print(f"成功: {result['success']}")
    if result['success']:
        print(f"任务类型: {result['instructions']['task']}")
        print(f"用户需求: {result['user_question']}")
        print("AI提示片段:")
        print(result['ai_prompt'][:200] + "...")
        print("\n这个结果应该传递给AI助手来处理AI提示并生成修改后的KQL")
    else:
        print(f"错误: {result['error']}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
