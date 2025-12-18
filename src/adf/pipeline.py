"""
Pipeline operations for Azure Data Factory using Azure SDK.

This module contains the implementation of pipeline-related operations.
These functions are used by the ADFClientSDK class.
"""

import time
from pathlib import Path
from typing import Optional
from datetime import datetime

from azure.mgmt.datafactory import DataFactoryManagementClient
from azure.mgmt.datafactory.models import PipelineRun

from .models import (
    is_terminal_status,
    KustoQueryPipelineParameters,
)
from .exceptions import (
    PipelineTriggerError,
    PipelineTimeoutError
)
from .utils import get_logger, save_to_json, sdk_object_to_dict, validate_run_id
from .config import DEFAULT_POLL_INTERVAL, DEFAULT_TIMEOUT


logger = get_logger(__name__)


# ==================== Pipeline Operations ====================

def trigger_pipeline(
    adf_client: DataFactoryManagementClient,
    resource_group_name: str,
    factory_name: str,
    pipeline_name: str,
    parameters: Optional[KustoQueryPipelineParameters] = None
) -> str:
    """
    Trigger an Azure Data Factory pipeline run using SDK.
    
    Args:
        adf_client: Azure Data Factory Management Client instance
        resource_group_name: Resource group name
        factory_name: Data Factory name
        pipeline_name: Pipeline name to trigger
        parameters: Optional dictionary of pipeline parameters
    
    Returns:
        str: Run ID of the triggered pipeline
    
    Raises:
        PipelineTriggerError: If the pipeline trigger fails
    """
    try:
        logger.info(f"Triggering pipeline: {pipeline_name}")
        
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
    adf_client: DataFactoryManagementClient,
    resource_group_name: str,
    factory_name: str,
    run_id: str
) -> PipelineRun:
    """
    Get the current status of a pipeline run using SDK.
    
    Args:
        adf_client: Azure Data Factory Management Client instance
        resource_group_name: Resource group name
        factory_name: Data Factory name
        run_id: Pipeline run ID to check status for
    
    Returns:
        PipelineRun: Azure SDK PipelineRun object with run status information
    
    Raises:
        Exception: If fetching the status fails
    """
    # Validate run_id format
    validate_run_id(run_id)
    
    logger.debug(f"Getting status for run: {run_id}")
    
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
    adf_client: DataFactoryManagementClient,
    resource_group_name: str,
    factory_name: str,
    run_id: str,
    poll_interval: int = DEFAULT_POLL_INTERVAL,
    timeout: int = DEFAULT_TIMEOUT,
    save_to_file: bool = False
) -> PipelineRun:
    """
    Wait for a pipeline run to complete by polling its status using SDK.
    
    Args:
        adf_client: Azure Data Factory Management Client instance
        resource_group_name: Resource group name
        factory_name: Data Factory name
        run_id: Pipeline run ID
        poll_interval: Seconds between status checks (default: 30)
        timeout: Maximum seconds to wait (default: 3600)
        save_to_file: Whether to save final status to JSON file (default: False)
    
    Returns:
        dict: Final pipeline run status information
    
    Raises:
        PipelineTimeoutError: If pipeline doesn't complete within timeout
    """
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
            adf_client,
            resource_group_name,
            factory_name,
            run_id
        )
        
        status = status_info.get("status")
        logger.debug(f"Current status: {status} (elapsed: {elapsed}s)")
        
        # Check if terminal status
        if is_terminal_status(status):
            logger.info(f"Pipeline completed with status: {status}")
            
            # Save to file if requested
            if save_to_file:
                _save_pipeline_status(status_info, run_id)
            
            return status_info
        
        # Wait before next poll
        time.sleep(poll_interval)


def _save_pipeline_status(
    pipeline_status: PipelineRun,
    run_id: str
) -> Path:
    """
    Save pipeline status to JSON file.
    
    Args:
        pipeline_status: Pipeline status dictionary
        run_id: Pipeline run ID
        
    Returns:
        Path to saved file
    """
    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"pipeline_status_{timestamp}_{run_id}.json"
    
    # Save to file
    save_to_json(pipeline_status, output_file)
    
    logger.info(f"Pipeline status saved to: {output_file}")
    
    return output_file
