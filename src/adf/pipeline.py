"""
Pipeline operations for Azure Data Factory.
"""

import time
from typing import Dict, Any, Optional

import requests

from .config import API_VERSION, DEFAULT_POLL_INTERVAL, DEFAULT_TIMEOUT


def trigger_pipeline(
    subscription_id: str,
    resource_group_name: str,
    factory_name: str,
    pipeline_name: str,
    token: str,
    parameters: Optional[Dict[str, Any]] = None
) -> str:
    """
    Trigger an Azure Data Factory pipeline run.
    
    Args:
        subscription_id: Azure subscription ID
        resource_group_name: Resource group name
        factory_name: Data Factory name
        pipeline_name: Pipeline name to trigger
        token: Bearer token for authentication
        parameters: Optional dictionary of pipeline parameters
    
    Returns:
        str: Run ID of the triggered pipeline
    
    Raises:
        requests.HTTPError: If the API request fails
    """
    url = (
        f"https://management.azure.com/subscriptions/{subscription_id}"
        f"/resourceGroups/{resource_group_name}"
        f"/providers/Microsoft.DataFactory/factories/{factory_name}"
        f"/pipelines/{pipeline_name}/createRun"
        f"?api-version={API_VERSION}"
    )
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    body = parameters if parameters else {}
    
    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()
    
    result = response.json()
    run_id = result.get("runId")
    
    print(f"Pipeline triggered successfully. Run ID: {run_id}")
    return run_id


def get_pipeline_run_status(
    subscription_id: str,
    resource_group_name: str,
    factory_name: str,
    run_id: str,
    token: str
) -> Dict[str, Any]:
    """
    Get the status of a pipeline run.
    
    Args:
        subscription_id: Azure subscription ID
        resource_group_name: Resource group name
        factory_name: Data Factory name
        run_id: Pipeline run ID
        token: Bearer token for authentication
    
    Returns:
        dict: Pipeline run status information
    
    Raises:
        requests.HTTPError: If the API request fails
    """
    url = (
        f"https://management.azure.com/subscriptions/{subscription_id}"
        f"/resourceGroups/{resource_group_name}"
        f"/providers/Microsoft.DataFactory/factories/{factory_name}"
        f"/pipelineruns/{run_id}"
        f"?api-version={API_VERSION}"
    )
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    return response.json()


def wait_for_pipeline(
    subscription_id: str,
    resource_group_name: str,
    factory_name: str,
    run_id: str,
    token: str,
    poll_interval: int = DEFAULT_POLL_INTERVAL,
    timeout: int = DEFAULT_TIMEOUT
) -> Dict[str, Any]:
    """
    Wait for a pipeline run to complete by polling its status.
    
    Args:
        subscription_id: Azure subscription ID
        resource_group_name: Resource group name
        factory_name: Data Factory name
        run_id: Pipeline run ID
        token: Bearer token for authentication
        poll_interval: Seconds between status checks (default: 30)
        timeout: Maximum seconds to wait (default: 3600)
    
    Returns:
        dict: Final pipeline run status information
    
    Raises:
        TimeoutError: If pipeline doesn't complete within timeout
        requests.HTTPError: If the API request fails
    """
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
            token
        )
        
        status = status_info.get("status")
        print(f"Current status: {status}")
        
        if status in terminal_statuses:
            print(f"Pipeline completed with status: {status}")
            return status_info
        
        time.sleep(poll_interval)
