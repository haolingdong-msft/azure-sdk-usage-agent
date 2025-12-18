"""
Activity operations for Azure Data Factory using Azure SDK.

This module contains the implementation of activity-related operations.
These functions are used by the ADFClientSDK class.
"""

from pathlib import Path
from typing import Optional
from datetime import datetime

from azure.mgmt.datafactory import DataFactoryManagementClient
from azure.mgmt.datafactory.models import RunFilterParameters, ActivityRun

from .exceptions import ActivityQueryError
from .utils import get_logger, save_to_json, sdk_object_to_dict, validate_run_id


logger = get_logger(__name__)


# ==================== Activity Operations ====================

def get_activity_runs(
    adf_client: DataFactoryManagementClient,
    resource_group_name: str,
    factory_name: str,
    run_id: str,
    start_time: str,
    end_time: str,
    save_to_file: bool = True
) -> list[ActivityRun]:
    """
    Get activity runs for a pipeline run using SDK.
    
    Args:
        adf_client: Azure Data Factory Management Client instance
        resource_group_name: Resource group name
        factory_name: Data Factory name
        run_id: Pipeline run ID
        start_time: Start time in ISO 8601 format (e.g., "2024-01-01T00:00:00Z")
        end_time: End time in ISO 8601 format (e.g., "2024-01-01T23:59:59Z")
        save_to_file: Whether to save results to JSON file (default: True)
    
    Returns:
        list[ActivityRun]: List of Azure SDK ActivityRun objects
    
    Raises:
        ActivityQueryError: If the query fails
    """
    # Validate run_id
    validate_run_id(run_id)
    
    try:
        logger.info(f"Querying activity runs for pipeline run: {run_id}")
        
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
        activity_runs = []
        for activity_run in activity_runs_response.value:
            activity_dict = sdk_object_to_dict(activity_run)
            activity_runs.append(activity_dict)
        
        logger.info(f"Retrieved {len(activity_runs)} activity runs")
        
        # Save to file if requested
        if save_to_file:
            _save_activity_runs(activity_runs, run_id, activity_runs_response.continuation_token)
        
        return activity_runs
        
    except Exception as e:
        logger.error(f"Failed to query activity runs for {run_id}: {e}")
        raise ActivityQueryError(run_id, str(e)) from e


def _save_activity_runs(
    activity_runs: list[ActivityRun],
    run_id: str,
    continuation_token: Optional[str] = None
) -> Path:
    """
    Save activity runs to JSON file.
    
    Args:
        activity_runs: List of activity run dictionaries
        run_id: Pipeline run ID
        continuation_token: Optional continuation token
        
    Returns:
        Path to saved file
    """
    # Create result dictionary
    result = {
        "value": activity_runs,
        "continuationToken": continuation_token
    }
    
    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"activity_runs_{timestamp}_{run_id}.json"
    
    # Save to file
    save_to_json(result, output_file)
    
    logger.info(f"Activity runs saved to: {output_file}")
    
    return output_file
