"""
Low-level operations for Azure Data Factory using Azure SDK.

This module contains the implementation of pipeline and activity operations.
These functions are used by the ADFClientSDK class.
"""

import time
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from azure.identity import DefaultAzureCredential
from azure.mgmt.datafactory import DataFactoryManagementClient
from azure.mgmt.datafactory.models import RunFilterParameters

from .models import PipelineRunInfo, ActivityRunInfo, is_terminal_status
from .exceptions import (
    PipelineTriggerError,
    PipelineTimeoutError,
    ActivityQueryError
)
from .utils import get_logger, save_to_json, sdk_object_to_dict, validate_run_id
from .config import DEFAULT_POLL_INTERVAL, DEFAULT_TIMEOUT


logger = get_logger(__name__)


# ==================== Helper Functions ====================

def _create_adf_client(
    credential: DefaultAzureCredential,
    subscription_id: str
) -> DataFactoryManagementClient:
    """
    Create Azure Data Factory Management Client.
    
    Args:
        credential: Azure credential instance
        subscription_id: Azure subscription ID
        
    Returns:
        DataFactoryManagementClient instance
    """
    return DataFactoryManagementClient(credential, subscription_id)


# ==================== Pipeline Operations ====================

def trigger_pipeline(
    subscription_id: str,
    resource_group_name: str,
    factory_name: str,
    pipeline_name: str,
    credential: Optional[DefaultAzureCredential] = None,
    parameters: Optional[Dict[str, Any]] = None
) -> str:
    """
    Trigger an Azure Data Factory pipeline run using SDK.
    
    Args:
        subscription_id: Azure subscription ID
        resource_group_name: Resource group name
        factory_name: Data Factory name
        pipeline_name: Pipeline name to trigger
        credential: Azure credential instance. If None, creates a new DefaultAzureCredential
        parameters: Optional dictionary of pipeline parameters
    
    Returns:
        str: Run ID of the triggered pipeline
    
    Raises:
        PipelineTriggerError: If the pipeline trigger fails
    """
    if credential is None:
        credential = DefaultAzureCredential()
    
    try:
        logger.info(f"Triggering pipeline: {pipeline_name}")
        
        # Create ADF client
        adf_client = _create_adf_client(credential, subscription_id)
        
        # Trigger pipeline
        run_response = adf_client.pipelines.create_run(
            resource_group_name=resource_group_name,
            factory_name=factory_name,
            pipeline_name=pipeline_name,
            parameters=parameters
        )
        
        run_id = run_response.run_id
        logger.info(f"Pipeline triggered successfully. Run ID: {run_id}")
        
        return run_id
        
    except Exception as e:
        logger.error(f"Failed to trigger pipeline {pipeline_name}: {e}")
        raise PipelineTriggerError(pipeline_name, str(e)) from e


def get_pipeline_run_status(
    subscription_id: str,
    resource_group_name: str,
    factory_name: str,
    run_id: str,
    credential: Optional[DefaultAzureCredential] = None
) -> Dict[str, Any]:
    """
    Get the status of a pipeline run using SDK.
    
    Args:
        subscription_id: Azure subscription ID
        resource_group_name: Resource group name
        factory_name: Data Factory name
        run_id: Pipeline run ID
        credential: Azure credential instance. If None, creates a new DefaultAzureCredential
    
    Returns:
        dict: Pipeline run status information (PipelineRunInfo compatible)
    
    Raises:
        Exception: If fetching the status fails
    """
    if credential is None:
        credential = DefaultAzureCredential()
    
    # Validate run_id format
    validate_run_id(run_id)
    
    logger.debug(f"Getting status for run: {run_id}")
    
    # Create ADF client
    adf_client = _create_adf_client(credential, subscription_id)
    
    # Get pipeline run
    pipeline_run = adf_client.pipeline_runs.get(
        resource_group_name=resource_group_name,
        factory_name=factory_name,
        run_id=run_id
    )
    
    # Convert to dictionary using SDK's as_dict() method
    # This automatically handles datetime serialization and returns snake_case keys
    status_dict = sdk_object_to_dict(pipeline_run)
    
    logger.debug(f"Run {run_id} status: {status_dict.get('status')}")
    
    return status_dict


def wait_for_pipeline(
    subscription_id: str,
    resource_group_name: str,
    factory_name: str,
    run_id: str,
    credential: Optional[DefaultAzureCredential] = None,
    poll_interval: int = DEFAULT_POLL_INTERVAL,
    timeout: int = DEFAULT_TIMEOUT
) -> Dict[str, Any]:
    """
    Wait for a pipeline run to complete by polling its status using SDK.
    
    Args:
        subscription_id: Azure subscription ID
        resource_group_name: Resource group name
        factory_name: Data Factory name
        run_id: Pipeline run ID
        credential: Azure credential instance. If None, creates a new DefaultAzureCredential
        poll_interval: Seconds between status checks (default: 30)
        timeout: Maximum seconds to wait (default: 3600)
    
    Returns:
        dict: Final pipeline run status information
    
    Raises:
        PipelineTimeoutError: If pipeline doesn't complete within timeout
    """
    if credential is None:
        credential = DefaultAzureCredential()
    
    # Validate run_id
    validate_run_id(run_id)
    
    start_time = time.time()
    
    logger.info(f"Waiting for pipeline run {run_id} to complete (timeout: {timeout}s)...")
    
    while True:
        elapsed = int(time.time() - start_time)
        
        if elapsed > timeout:
            logger.error(f"Pipeline run {run_id} timed out after {elapsed}s")
            raise PipelineTimeoutError(run_id, elapsed, timeout)
        
        # Get current status
        status_info = get_pipeline_run_status(
            subscription_id,
            resource_group_name,
            factory_name,
            run_id,
            credential
        )
        
        status = status_info.get("status")
        logger.debug(f"Current status: {status} (elapsed: {elapsed}s)")
        
        # Check if terminal status
        if is_terminal_status(status):
            logger.info(f"Pipeline completed with status: {status}")
            return status_info
        
        # Wait before next poll
        time.sleep(poll_interval)


# ==================== Activity Operations ====================

def get_activity_runs(
    subscription_id: str,
    resource_group_name: str,
    factory_name: str,
    run_id: str,
    start_time: str,
    end_time: str,
    credential: Optional[DefaultAzureCredential] = None,
    save_to_file: bool = True
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
        save_to_file: Whether to save results to JSON file (default: True)
    
    Returns:
        list: List of activity run information dictionaries (ActivityRunInfo compatible)
    
    Raises:
        ActivityQueryError: If the query fails
    """
    if credential is None:
        credential = DefaultAzureCredential()
    
    # Validate run_id
    validate_run_id(run_id)
    
    try:
        logger.info(f"Querying activity runs for pipeline run: {run_id}")
        
        # Create ADF client
        adf_client = _create_adf_client(credential, subscription_id)
        
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
    activity_runs: List[Dict[str, Any]],
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
