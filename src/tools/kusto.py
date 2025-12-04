"""
Kusto query execution tool via Azure Data Factory
"""

import logging
import json
import csv
from pathlib import Path
from typing import Any, Optional, Dict, List
from azure.identity import DefaultAzureCredential

from ..adf import ADFClient
from .config import (
    SUBSCRIPTION_ID,
    RESOURCE_GROUP_NAME,
    FACTORY_NAME,
    PIPELINE_NAME
)


def export_to_csv(data: List[Dict[str, Any]], output_file: str) -> str:
    """Export data to CSV file.
    
    Args:
        data: List of dictionaries to export
        output_file: Path to output CSV file
    
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
    
    # Write to CSV
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    
    return f"Exported {len(data)} rows to: {output_path.absolute()}"


def format_table(data: List[Dict[str, Any]], max_rows: Optional[int] = None) -> str:
    """Format a list of dictionaries as a readable table.
    
    Args:
        data: List of dictionaries to format
        max_rows: Maximum number of rows to display (None for all)
    
    Returns:
        str: Formatted table as string
    """
    if not data:
        return "No data to display."
    
    # Limit rows if specified
    display_data = data[:max_rows] if max_rows else data
    total_rows = len(data)
    
    # Get all unique keys from all dictionaries
    keys = []
    for item in display_data:
        for key in item.keys():
            if key not in keys:
                keys.append(key)
    
    if not keys:
        return "No data to display."
    
    # Calculate column widths
    col_widths = {}
    for key in keys:
        col_widths[key] = len(str(key))
    
    for item in display_data:
        for key in keys:
            value = str(item.get(key, ''))
            col_widths[key] = max(col_widths[key], len(value))
    
    # Build table
    lines = []
    
    # Header
    header = " | ".join(str(key).ljust(col_widths[key]) for key in keys)
    lines.append(header)
    
    # Separator
    separator = "-+-".join("-" * col_widths[key] for key in keys)
    lines.append(separator)
    
    # Data rows
    for item in display_data:
        row = " | ".join(str(item.get(key, '')).ljust(col_widths[key]) for key in keys)
        lines.append(row)
    
    result = "\n".join(lines)
    
    # Add summary if truncated
    if max_rows and total_rows > max_rows:
        result += f"\n\n... {total_rows - max_rows} more rows (showing {max_rows} of {total_rows})"
    else:
        result += f"\n\nTotal rows: {total_rows}"
    
    return result


def format_query_results(output: Dict[str, Any], show_raw: bool = False) -> str:
    """Format Kusto query results for display.
    
    Args:
        output: Activity output containing query results
        show_raw: Whether to show raw JSON output
    
    Returns:
        str: Formatted results
    """
    parts = []
    
    # Extract result count and data
    count = output.get('count', 0)
    value = output.get('value', [])
    
    parts.append(f"Result count: {count}")
    
    if isinstance(value, list) and value:
        # Format as table
        parts.append("\nResults:\n")
        parts.append(format_table(value, max_rows=100))
    elif value:
        parts.append(f"\nResults:\n{json.dumps(value, indent=2)}")
    else:
        parts.append("\nNo results returned.")
    
    # Add billing and runtime info if available
    if 'effectiveIntegrationRuntime' in output:
        parts.append(f"\nIntegration Runtime: {output['effectiveIntegrationRuntime']}")
    
    if 'billingReference' in output:
        billing = output['billingReference']
        if 'billableDuration' in billing:
            for duration in billing['billableDuration']:
                meter = duration.get('meterType', 'Unknown')
                time = duration.get('duration', 0)
                unit = duration.get('unit', 'Hours')
                parts.append(f"Billing: {meter} - {time} {unit}")
    
    if 'durationInQueue' in output:
        queue_time = output['durationInQueue'].get('integrationRuntimeQueue', 0)
        parts.append(f"Queue time: {queue_time}s")
    
    # Optionally show raw JSON
    if show_raw:
        parts.append(f"\n{'=' * 80}")
        parts.append("RAW OUTPUT")
        parts.append(f"{'=' * 80}")
        parts.append(json.dumps(output, indent=2))
    
    return "\n".join(parts)

async def generate_kql_from_query(user_query: str) -> str:
    """Generate KQL (Kusto Query Language) from a natural language query.
    
    This function converts a user's natural language question into a valid KQL query.
    
    Args:
        user_query: Natural language question or request
    
    Returns:
        str: Generated KQL query
    
    Examples:
        >>> await generate_kql_from_query("Show me the top 10 errors from the last hour")
        "Logs | where Level == 'Error' and Timestamp > ago(1h) | top 10 by Timestamp desc"
        
        >>> await generate_kql_from_query("Count users by country")
        "Users | summarize count() by Country"
    """
    # TODO: Implement KQL generation logic
    # This could use an LLM (like GPT-4) to convert natural language to KQL
    
    logging.info(f"Generating KQL for query: {user_query}")
    
    # For now, return a simple example query
    # In production, integrate with an LLM service here
    return f"// Generated from: {user_query}\n// TODO: Implement LLM-based KQL generation"


async def execute_kusto_query(
    kusto_query: str,
    timeout: int = 3600,
    poll_interval: int = 30,
    export_to_file: Optional[str] = None
) -> str:
    """Execute a Kusto query via Azure Data Factory pipeline.
    
    This tool triggers an ADF pipeline that executes a Kusto query and returns the results.
    The pipeline is pre-configured with Azure subscription and Data Factory settings.
    
    Args:
        kusto_query: The Kusto query to execute
        timeout: Maximum wait time in seconds (default: 3600)
        poll_interval: Status check interval in seconds (default: 30)
        export_to_file: Optional file path to export full results (CSV format)
    
    Returns:
        str: Formatted query results or error message
    """
    try:
        # Create ADF client with DefaultAzureCredential
        logging.info(f"Creating ADF client for factory: {FACTORY_NAME}")
        client = ADFClient(
            subscription_id=SUBSCRIPTION_ID,
            resource_group_name=RESOURCE_GROUP_NAME,
            factory_name=FACTORY_NAME,
            credential=DefaultAzureCredential()
        )
        
        # Prepare pipeline parameters
        parameters: Dict[str, Any] = {
            "KustoQuery": kusto_query
        }
        
        logging.info(f"Triggering pipeline: {PIPELINE_NAME} with query: {kusto_query[:100]}...")
        
        # Trigger and wait for pipeline completion
        final_status = client.run_pipeline(
            pipeline_name=PIPELINE_NAME,
            parameters=parameters,
            wait=True,
            poll_interval=poll_interval,
            timeout=timeout
        )
        
        # Extract results
        run_id = final_status.get("runId")
        status = final_status.get("status")
        duration_ms = final_status.get("durationInMs", 0)
        
        if status != "Succeeded":
            error_msg = f"Pipeline execution failed with status: {status}"
            logging.error(error_msg)
            return f"Error: {error_msg}\nRun ID: {run_id}"
        
        # Get activity runs to extract query results
        start_time = final_status.get("runStart")
        end_time = final_status.get("runEnd")
        
        if not (run_id and start_time and end_time):
            return f"Pipeline succeeded but missing timing information.\nStatus: {status}\nRun ID: {run_id}"
        
        logging.info(f"Fetching activity runs for run_id: {run_id}")
        activity_runs = client.get_activity_runs(
            run_id=run_id,
            start_time=start_time,
            end_time=end_time
        )
        
        # Format results
        result_parts = [
            f"Query executed successfully in {duration_ms}ms",
            f"Run ID: {run_id}",
            f"\n{'=' * 80}",
            "QUERY RESULTS",
            f"{'=' * 80}\n"
        ]
        
        # Extract output from Kusto activity
        full_data = []  # Store all data for export
        
        for activity in activity_runs:
            activity_type = activity.get('activityType', '')
            activity_name = activity.get('activityName', 'Unknown')
            activity_status = activity.get('status', 'Unknown')
            
            result_parts.append(f"\nActivity: {activity_name} ({activity_type})")
            result_parts.append(f"Status: {activity_status}")
            
            if activity_status == 'Succeeded':
                output = activity.get('output', {})
                if output:
                    # Store full data for export
                    value = output.get('value', [])
                    if isinstance(value, list):
                        full_data.extend(value)
                    
                    result_parts.append("\n" + format_query_results(output, show_raw=False))
            elif activity_status == 'Failed':
                error = activity.get('error', {})
                result_parts.append(f"\n❌ Error: {error.get('message', 'Unknown error')}")
                result_parts.append(f"Error Code: {error.get('errorCode', 'Unknown')}")
        
        # Export to file if requested
        if export_to_file and full_data:
            export_msg = export_to_csv(full_data, export_to_file)
            result_parts.append(f"\n{'=' * 80}")
            result_parts.append(export_msg)
        
        return "\n".join(result_parts)
        
    except Exception as e:
        error_msg = f"Error executing Kusto query via ADF: {str(e)}"
        logging.error(error_msg, exc_info=True)
        return f"Error: {error_msg}"


async def query_kusto_with_natural_language(
    user_query: str,
    database: Optional[str] = None,
    timeout: int = 3600,
    poll_interval: int = 30
) -> str:
    """Execute a Kusto query using natural language.
    
    This is a convenience function that combines KQL generation from natural language
    and query execution into a single operation.
    
    Args:
        user_query: Natural language question or request
        database: Optional Kusto database name (if required by pipeline)
        timeout: Maximum wait time in seconds (default: 3600)
        poll_interval: Status check interval in seconds (default: 30)
    
    Returns:
        str: Query results or error message
    
    Examples:
        >>> await query_kusto_with_natural_language(
        ...     user_query="Show me errors from the last hour"
        ... )
    """
    try:
        # Step 1: Generate KQL from natural language
        logging.info(f"Generating KQL from user query: {user_query}")
        kusto_query = await generate_kql_from_query(user_query=user_query)
        
        logging.info(f"Generated KQL: {kusto_query}")
        
        # Step 2: Execute the generated KQL
        result = await execute_kusto_query(
            kusto_query=kusto_query,
            database=database,
            timeout=timeout,
            poll_interval=poll_interval
        )
        
        return f"Natural Language Query: {user_query}\n\nGenerated KQL:\n{kusto_query}\n\n{result}"
        
    except Exception as e:
        error_msg = f"Error processing natural language query: {str(e)}"
        logging.error(error_msg, exc_info=True)
        return f"Error: {error_msg}"
