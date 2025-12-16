"""
Activity run operations for Azure Data Factory using Azure SDK.
"""

from typing import Dict, Any, List, Optional
import json
from pathlib import Path
from datetime import datetime

from azure.identity import DefaultAzureCredential
from azure.mgmt.datafactory import DataFactoryManagementClient
from azure.mgmt.datafactory.models import RunFilterParameters


def get_activity_runs(
    subscription_id: str,
    resource_group_name: str,
    factory_name: str,
    run_id: str,
    start_time: str,
    end_time: str,
    credential: Optional[DefaultAzureCredential] = None
) -> List[Dict[str, Any]]:
    """
    Get activity runs for a pipeline run using SDK.
    
    Args:
        subscription_id: Azure subscription ID
        resource_group_name: Resource group name
        factory_name: Data Factory name
        run_id: Pipeline run ID
        start_time: Start time in ISO 8601 format (e.g., "2024-01-01T00:00:00Z")
        end_time: End time in ISO 8601 format (e.g., "2024-01-01T23:59:59Z")
        credential: Azure credential instance. If None, creates a new DefaultAzureCredential
    
    Returns:
        list: List of activity run information dictionaries
    
    Raises:
        Exception: If the API request fails
    """
    if credential is None:
        credential = DefaultAzureCredential()
    
    # Create ADF client
    adf_client = DataFactoryManagementClient(credential, subscription_id)
    
    # Parse datetime strings
    last_updated_after = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
    last_updated_before = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
    
    # Create filter parameters
    filter_params = RunFilterParameters(
        last_updated_after=last_updated_after,
        last_updated_before=last_updated_before
    )
    
    # Query activity runs
    activity_runs_response = adf_client.activity_runs.query_by_pipeline_run(
        resource_group_name=resource_group_name,
        factory_name=factory_name,
        run_id=run_id,
        filter_parameters=filter_params
    )
    
    # Convert SDK objects to dictionaries
    # Note: We need to convert because:
    # 1. SDK returns ActivityRun objects, not plain dicts
    # 2. as_dict() automatically handles datetime serialization
    # 3. Maintain consistent format with REST API version
    activity_runs = []
    for activity_run in activity_runs_response.value:
        # Use SDK's as_dict() method - it automatically converts datetime to strings
        activity_dict = activity_run.as_dict()
        activity_runs.append(activity_dict)
    
    # Create result dictionary
    result = {
        "value": activity_runs,
        "continuationToken": activity_runs_response.continuation_token
    }
    
    # Save result to JSON file
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"activity_runs_{timestamp}_{run_id}.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"Activity runs result saved to: {output_file}")
    print(f"Retrieved {len(activity_runs)} activity runs")
    
    return activity_runs
