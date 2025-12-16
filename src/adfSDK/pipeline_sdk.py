"""
Pipeline operations for Azure Data Factory using Azure SDK.
"""

import time
from typing import Dict, Any, Optional

from azure.identity import DefaultAzureCredential
from azure.mgmt.datafactory import DataFactoryManagementClient
from datetime import datetime, timedelta

from .config import DEFAULT_POLL_INTERVAL, DEFAULT_TIMEOUT


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
        Exception: If the pipeline trigger fails
    """
    if credential is None:
        credential = DefaultAzureCredential()
    
    # Create ADF client
    adf_client = DataFactoryManagementClient(credential, subscription_id)
    
    # Trigger pipeline
    run_response = adf_client.pipelines.create_run(
        resource_group_name=resource_group_name,
        factory_name=factory_name,
        pipeline_name=pipeline_name,
        parameters=parameters
    )
    
    run_id = run_response.run_id
    print(f"Pipeline triggered successfully. Run ID: {run_id}")
    
    return run_id


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
        dict: Pipeline run status information
    
    Raises:
        Exception: If fetching the status fails
    """
    if credential is None:
        credential = DefaultAzureCredential()
    
    # Create ADF client
    adf_client = DataFactoryManagementClient(credential, subscription_id)
    
    # Get pipeline run
    pipeline_run = adf_client.pipeline_runs.get(
        resource_group_name=resource_group_name,
        factory_name=factory_name,
        run_id=run_id
    )
    
    # Convert to dictionary using SDK's as_dict() method
    # This automatically handles datetime serialization and returns snake_case keys
    return pipeline_run.as_dict()


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
        TimeoutError: If pipeline doesn't complete within timeout
    """
    if credential is None:
        credential = DefaultAzureCredential()
    
    start_time = time.time()
    terminal_statuses = {"Succeeded", "Failed", "Cancelled"}
    
    print(f"Waiting for pipeline run {run_id} to complete...")
    
    while True:
        elapsed = time.time() - start_time
        if elapsed > timeout:
            raise TimeoutError(
                f"Pipeline run {run_id} did not complete within {timeout} seconds"
            )
        
        status_info = get_pipeline_run_status(
            subscription_id,
            resource_group_name,
            factory_name,
            run_id,
            credential
        )
        
        status = status_info.get("status")
        print(f"Current status: {status}")
        
        if status in terminal_statuses:
            print(f"Pipeline completed with status: {status}")
            return status_info
        
        time.sleep(poll_interval)
