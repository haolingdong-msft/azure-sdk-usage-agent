"""
Kusto query execution tool via Azure Data Factory
"""

import logging
import csv
from pathlib import Path
from typing import Any, Optional, Dict, List
from datetime import datetime
from azure.identity import DefaultAzureCredential

from ..adf import ADFClient
from ..adf.config import config
from ..utils.utils import format_pipeline_status_failed, format_activity_runs


def export_to_csv(data: List[Dict[str, Any]], output_file: Optional[str] = None) -> str:
    """Export data to CSV file.
    
    Args:
        data: List of dictionaries to export
        output_file: Optional path to output CSV file. If not provided, generates a default filename
                     in the format 'output/kusto_query_results_YYYYMMDD_HHMMSS.csv'
    
    Returns:
        str: Status message with file path
    """
    if not data:
        return "No data to export."
    
    # Get all unique keys from all dictionaries
    keys = []
    for item in data:
        for key in item.keys():
            if key not in keys:
                keys.append(key)
    
    if not keys:
        return "No data to export."
    
    # Generate default filename if not provided
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"output/kusto_query_results_{timestamp}.csv"
    
    # Write to CSV
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    
    return f"Exported {len(data)} rows to: {output_path.absolute()}"


def get_kusto_schema() -> str:
    """Get the Kusto schema with essential query patterns.
    
    Returns core schema, fields, and basic examples. For SDK analysis queries,
    the AI should call get_kusto_helper_functions() to get complete function definitions.
    
    Returns:
        str: Schema context
    """
    return """
Kusto Query Language (KQL) Base Schema:

REQUIRED:
- Table: Unionizer("Requests", "HttpIncomingRequests")
- Filter: where TaskName == "HttpIncomingRequestEndWithSuccess"
- Time filter: where TIMESTAMP > ago(Xd) [ALWAYS required]

KEY FIELDS:
- TIMESTAMP, operationName, httpMethod, userAgent, apiVersion, subscriptionId
- targetResourceProvider, targetResourceType, tenantId, principalOid, RoleLocation

QUERY PATTERNS:
- Time: `where TIMESTAMP > ago(24h)` or `ago(7d)`
- Provider: `where tolower(targetResourceProvider) == "microsoft.compute"`
- Aggregate: `summarize count() by field` or `dcount(subscriptionId)`
- Sort: `order by count_ desc` or `top 10 by count_ desc`

AVAILABLE HELPER FUNCTIONS (call get_kusto_helper_functions() tool if needed):
- GetProduct(userAgent) - Extract SDK name (Python-SDK, Java-SDK, .NET-SDK, etc.)
- GetTrackInfo(userAgent) - Extract Track1/Track2
- GetOSInfo(userAgent) - Extract OS (Windows, Linux, MacOS)
- GetResource(operationName) - Extract resource type
- GetLanguageVersion(userAgent, Product, Track) - Extract language version

NOTE: If your query needs SDK analysis, OS detection, or resource type extraction,
call get_kusto_helper_functions() to get the complete function definitions.

BASIC EXAMPLES:


1. Total API calls for a resource provider:
```kql
Unionizer("Requests", "HttpIncomingRequests")
| where TaskName == "HttpIncomingRequestEndWithSuccess"
| where TIMESTAMP > ago(24h)
| where tolower(targetResourceProvider) == "microsoft.compute"
| summarize TotalCalls = count()
```

2. Top 10 operations by subscription count:
```kql
Unionizer("Requests", "HttpIncomingRequests")
| where TaskName == "HttpIncomingRequestEndWithSuccess"
| where TIMESTAMP > ago(7d)
| where tolower(targetResourceProvider) == "microsoft.compute"
| summarize UniqueSubscriptions = dcount(subscriptionId) by operationName
| top 10 by UniqueSubscriptions desc
```

3. API calls by HTTP method:
```kql
Unionizer("Requests", "HttpIncomingRequests")
| where TaskName == "HttpIncomingRequestEndWithSuccess"
| where TIMESTAMP > ago(24h)
| where tolower(targetResourceProvider) == "microsoft.compute"
| summarize count() by httpMethod
| order by count_ desc
```
"""


def get_kusto_helper_functions() -> str:
    """Get complete KQL helper function definitions for SDK analysis.
    
    Returns all 5 helper functions with full implementation including:
    - GetProduct() - Extract SDK/product name from UserAgent
    - GetTrackInfo() - Extract Track1/Track2 from UserAgent
    - GetOSInfo() - Extract operating system from UserAgent
    - GetResource() - Extract resource type from operationName
    - GetLanguageVersion() - Extract language version from UserAgent
    
    Returns:
        str: Complete function definitions
    """
    return r"""
KQL Helper Functions - Complete Definitions:

USAGE: Copy these function definitions to the start of your query (before Unionizer).
Define with `let FunctionName = ...` syntax.

```kql
let GetProduct = (UAString: string) {
    let userAgent = tolower(trim(" ", UAString));
    let goSdkException = dynamic(["kubernetes-cloudprovider", "custer-api-provider-azure", "cilium", "azure-metrics-exporter", "azure_prometheus_exporter", "cluster-image-registry-operator", "aad-pod-identity", "azure-service-operator"]);
    let netReg = extract(@"(microsoft\.windowsazure\.management|microsoft\.azure\.management)", 1, userAgent);
    let jsRlcReg = "azsdk-js-arm-[a-z0-9]+-rest";
    case(
        isempty(UAString), "",
        userAgent has "terraform", "Terraform",
        userAgent has "ansible", "Ansible",
        (userAgent has "azure-sdk-for-java" or userAgent has "azsdk-java") and userAgent has "auto-generated", "Java Fluent Lite",
        userAgent has "azure-sdk-for-java" or userAgent has "azsdk-java", "Java Fluent Premium",
        netReg != "" and userAgent has "fluent", ".Net Fluent",
        netReg != "" or userAgent has "azsdk-net", ".Net Code-gen",
        userAgent has "azure-sdk-for-python" or userAgent has "azsdk-python", "Python-SDK",
        userAgent has "azure-sdk-for-node", "JavaScript (Node.JS)",
        userAgent matches regex jsRlcReg, "JavaScript RLC",
        (userAgent has "ms-rest-js" and userAgent startswith "@azure/arm") or userAgent has "azsdk-js-arm", "JavaScript",
        userAgent has "azure-sdk-for-ruby", "Ruby-SDK",
        (userAgent has "azure-sdk-for-go" or userAgent has "azsdk-go") and array_index_of(goSdkException, userAgent) == -1, "Go-SDK",
        userAgent has "azure-sdk-for-php", "PHP-SDK",
        userAgent has "azsdk-rust-", "Rust",
        ""
    )
};
let GetTrackInfo = (UAString: string) {
    let userAgent = tolower(trim(" ", UAString));
    case(
        userAgent has "azsdk-net", "Track2",
        userAgent has "azsdk-python", "Track2",
        userAgent has "azsdk-java", "Track2",
        userAgent has "azsdk-go", "Track2",
        userAgent has "azsdk-js", "Track2",
        "Track1"
    )
};
let GetOSInfo = (UAString: string) {
    let userAgent = tolower(trim(" ", UAString));
    case(
        userAgent has "windows", "Windows",
        userAgent has "linux", "Linux",
        userAgent has "macos", "MacOS",
        userAgent has "mac os", "MacOS",
        "Unknown"
    )
};
let GetResource = (operationName: string) {
    let lowerOperationName = tolower(operationName);
    let resourceMatch = extract("/providers/microsoft.([a-z]+)/([a-z]+)/", 2, lowerOperationName);
    let entityName = iff(resourceMatch != "", resourceMatch, "");
    let elements = split(lowerOperationName, "/");
    let entityName2 = iif(entityName == "", elements[-1], entityName);
    tolower(entityName2)
};
let GetLanguageVersion = (UAString: string, Product: string, Track: string) {
    let userAgent = tolower(trim(" ", UAString));
    case(
        isempty(userAgent), '',
        (Product == '.Net Fluent' or Product == '.Net Code-gen') and Track == "Track1", extract("(?i)FxVersion/(\\d+.\\d+)", 1, userAgent),
        (Product == '.Net Fluent' or Product == '.Net Code-gen') and Track == "Track2", extract("(?i).NET\\s(\\d+.\\d+.\\d+)", 1, userAgent),
        (Product == 'Java Fluent Lite' or Product == 'Java Fluent Premium') and Track == "Track1", extract("java:(\\d+.\\d+.\\d+(_\\d+)?)", 1, userAgent),
        (Product == 'Java Fluent Lite' or Product == 'Java Fluent Premium') and Track == "Track2", extract("\\((\\d+.\\d+.\\d+(_\\d+)?)", 1, userAgent),
        Product == 'Python-SDK', extract("(Python|python)/(\\d+.\\d+.\\d+)", 2, userAgent),
        Product == 'Go-SDK', extract("go(\\d+.\\d+.\\d+)", 1, userAgent),
        Product == 'JavaScript (Node.JS)' or Product == 'JavaScript RLC' or Product == 'JavaScript', extract("(?i)Node/(?:v)?(\\d+\\.\\d+\\.\\d+)", 1, userAgent),
        Product == 'Rust', extract("\\((\\d+.\\d+.[^\\;]+);", 1, userAgent),
        ''
    )
};
```

EXAMPLE: SDK usage analysis with Product, Track, and OS
```kql
let GetProduct = (UAString: string) { /* definition above */ };
let GetTrackInfo = (UAString: string) { /* definition above */ };
let GetOSInfo = (UAString: string) { /* definition above */ };

Unionizer("Requests", "HttpIncomingRequests")
| where TaskName == "HttpIncomingRequestEndWithSuccess"
| where TIMESTAMP > ago(7d)
| where tolower(targetResourceProvider) == "microsoft.compute"
| extend Product = GetProduct(userAgent), Track = GetTrackInfo(userAgent), OS = GetOSInfo(userAgent)
| where isnotempty(Product)
| summarize count() by Product, Track, OS, RoleLocation
| order by count_ desc
```
"""


def generate_kql_from_question(user_query: str) -> str:
    """Generate KQL query based on natural language question.
    
    This function provides schema, patterns, and context needed for generating
    a valid KQL query. The calling AI agent will use this context to generate
    the actual KQL query based on the user's question.
    
    Workflow:
    1. AI calls this function with user's natural language question
    2. Function returns schema and context
    3. AI generates KQL query using the context
    4. AI can then call execute_kusto_query_tool to run the generated query
    
    Args:
        user_query: Natural language question or request
    
    Returns:
        str: Schema context, patterns, and instructions for KQL generation
    """
    base_schema = get_kusto_schema()
    
    return f"""User Query: {user_query}

Generate a KQL query based on the schema below.

{base_schema}

IMPORTANT:
- If your query needs SDK analysis, OS detection, resource type extraction, or language versions,
  call get_kusto_helper_functions() to get complete function definitions.
"""


async def execute_kusto_query(
    kusto_query: str,
    timeout: Optional[int] = None,
    poll_interval: Optional[int] = None,
    export_to_file: Optional[str] = None
) -> str:
    """Execute a Kusto query via Azure Data Factory pipeline.
    
    This tool triggers an ADF pipeline that executes a Kusto query and returns the results.
    The pipeline is pre-configured with Azure subscription and Data Factory settings.
    
    Args:
        kusto_query: The Kusto query to execute
        timeout: Maximum wait time in seconds (default: uses config.timeout)
        poll_interval: Status check interval in seconds (default: uses config.poll_interval)
        export_to_file: Optional file path to export full results (CSV format)
    
    Returns:
        str: Formatted query results or error message
    """
    # Use config defaults if not provided
    timeout = timeout if timeout is not None else config.timeout
    poll_interval = poll_interval if poll_interval is not None else config.poll_interval
    
    try:
        # Create ADF client using context manager
        with ADFClient(
            subscription_id=config.subscription_id,
            resource_group_name=config.resource_group_name,
            factory_name=config.factory_name,
            credential=DefaultAzureCredential()
        ) as client:
            # Prepare pipeline parameters
            parameters: Dict[str, Any] = {
                config.pipeline_parameter_key: kusto_query
            }
            
            # Trigger and wait for pipeline completion
            final_status = client.run_pipeline(
                pipeline_name=config.pipeline_name,
                parameters=parameters,
                wait=True,
                poll_interval=poll_interval,
                timeout=timeout,
                save_to_file=True
            )
            
            # Extract results
            run_id = final_status.get("run_id")
            status = final_status.get("status")
            duration_ms = final_status.get("duration_in_ms", 0)
            
            if status != "Succeeded":
                error_output = format_pipeline_status_failed(final_status)
                logging.error(f"Pipeline execution failed for run_id {run_id}")
                return error_output
            
            # Get activity runs to extract query results
            start_time = final_status.get("run_start")
            end_time = final_status.get("run_end")
            
            if not (run_id and start_time and end_time):
                return f"Pipeline succeeded but missing timing information.\nStatus: {status}\nRun ID: {run_id}"
            
            activity_runs = client.get_activity_runs(
                run_id=run_id,
                start_time=start_time,
                end_time=end_time,
                save_to_file=True
            )
            
            # Format activity results and extract data
            result_message, full_data = format_activity_runs(activity_runs, duration_ms, run_id)
            
            # Export to CSV if user requested or if result set is large (> 100 rows)
            if full_data and (export_to_file or len(full_data) > 100):
                export_msg = export_to_csv(full_data, export_to_file)
                result_message += f"\n\n{'=' * 80}\n{export_msg}"
            
            return result_message
        
    except Exception as e:
        error_msg = f"Error executing Kusto query via ADF: {str(e)}"
        logging.error(error_msg, exc_info=True)
        return f"Error: {error_msg}"
