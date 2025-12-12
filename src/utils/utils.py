"""
Utility functions for formatting ADF pipeline results
"""

from typing import Dict, Any, List


def format_pipeline_status_failed(final_status: Dict[str, Any]) -> str:
    """Format failed pipeline status into a readable error message for LLM processing.
    
    Args:
        final_status: The final status dictionary from ADF pipeline run
        
    Returns:
        str: Formatted error message with pipeline failure details in a structured format
    """
    result_parts = []
    
    # Add error header
    pipeline_name = final_status.get('pipelineName', 'Unknown')
    result_parts.append(f"❌ Pipeline Failed - {pipeline_name}")
    
    # Add error message if available
    message = final_status.get("message")
    if message:
        result_parts.append(f"Error: {message}")
    
    return "\n".join(result_parts)


def format_table(data: List[Dict[str, Any]], max_rows: int = 100) -> str:
    """Format a list of dictionaries as a readable table.
    
    Args:
        data: List of dictionaries to format
        max_rows: Maximum number of rows to display (default: 100)
    
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
    
    # Add summary
    if max_rows and total_rows > max_rows:
        result += f"\n\n... {total_rows - max_rows} more rows (showing {max_rows} of {total_rows})"
    else:
        result += f"\n\nTotal rows: {total_rows}"
    
    return result


def format_activity_runs(activity_runs: List[Dict[str, Any]], pipeline_duration_ms: int, run_id: str) -> tuple[str, List[Dict[str, Any]]]:
    """Format activity runs results into a readable message.
    
    Args:
        activity_runs: List of activity run dictionaries from ADF
        pipeline_duration_ms: Pipeline execution duration in milliseconds
        run_id: Pipeline run ID
        
    Returns:
        tuple: (formatted_message, full_data_list)
            - formatted_message: Formatted string with activity results
            - full_data_list: List of all data records for export
    """
    result_parts = []
    
    # Extract output from Kusto activity
    full_data = []  # Store all data for export
    has_error = False
    
    for activity in activity_runs:
        activity_status = activity.get('status', 'Unknown')
        
        if activity_status == 'Succeeded':
            output = activity.get('output', {})
            if output:
                # Store full data for export
                value = output.get('value', [])
                if isinstance(value, list):
                    full_data.extend(value)
        elif activity_status == 'Failed':
            has_error = True
            activity_name = activity.get('activityName', 'Unknown')
            error = activity.get('error', {})
            
            result_parts.append(f"❌ Query Failed - Activity: {activity_name}")
            result_parts.append(f"Error: {error.get('message', 'Unknown error')}")

    
    # Display results based on data availability
    if not has_error:
        if len(full_data) > 0:
            # Show data table
            total_rows = len(full_data)
            if total_rows > 100:
                result_parts.append(f"Note: Displaying first 100 of {total_rows} rows. Full results exported to CSV.\n")
            result_parts.append(format_table(full_data, max_rows=100))
        else:
            result_parts.append("Query executed successfully but returned no data.")
    
    return "\n".join(result_parts), full_data
