"""
Example usage of Azure Data Factory SDK client.

This file demonstrates how to use the ADFClientSDK class to interact with
Azure Data Factory using the official Azure SDK instead of REST API.
"""

from datetime import datetime, timedelta
from azure.identity import DefaultAzureCredential

from src.adfSDK.client_sdk import ADFClientSDK
from src.adfSDK.config import (
    SUBSCRIPTION_ID,
    RESOURCE_GROUP_NAME,
    FACTORY_NAME,
    PIPELINE_NAME,
    PIPELINE_NAME_NO_PARAMS,
    KUSTO_QUERY_PARAM_KEY
)


def example_trigger_pipeline_with_params():
    """
    Example: Trigger a pipeline with parameters using SDK.
    """
    # Create credential
    credential = DefaultAzureCredential()
    
    # Create ADF client
    client = ADFClientSDK(
        subscription_id=SUBSCRIPTION_ID,
        resource_group_name=RESOURCE_GROUP_NAME,
        factory_name=FACTORY_NAME,
        credential=credential
    )
    
    # Define pipeline parameters
    kusto_query = """
    HttpRequests
    | where timestamp >= datetime(2024-01-01) and timestamp < datetime(2024-02-01)
    | where sdkName contains "azure-sdk"
    | summarize count() by sdkName, sdkVersion
    | order by count_ desc
    """
    
    parameters = {
        KUSTO_QUERY_PARAM_KEY: kusto_query
    }
    
    # Trigger pipeline
    run_id = client.trigger_pipeline(PIPELINE_NAME, parameters)
    print(f"Pipeline triggered with run ID: {run_id}")
    
    return run_id


def example_trigger_pipeline_no_params():
    """
    Example: Trigger a pipeline without parameters using SDK.
    """
    # Create credential
    credential = DefaultAzureCredential()
    
    # Create ADF client
    client = ADFClientSDK(
        subscription_id=SUBSCRIPTION_ID,
        resource_group_name=RESOURCE_GROUP_NAME,
        factory_name=FACTORY_NAME,
        credential=credential
    )
    
    # Trigger pipeline without parameters
    run_id = client.trigger_pipeline(PIPELINE_NAME_NO_PARAMS)
    print(f"Pipeline triggered with run ID: {run_id}")
    
    return run_id


def example_wait_for_pipeline(run_id: str):
    """
    Example: Wait for a pipeline to complete using SDK.
    
    Args:
        run_id: Pipeline run ID
    """
    # Create credential
    credential = DefaultAzureCredential()
    
    # Create ADF client
    client = ADFClientSDK(
        subscription_id=SUBSCRIPTION_ID,
        resource_group_name=RESOURCE_GROUP_NAME,
        factory_name=FACTORY_NAME,
        credential=credential
    )
    
    # Wait for pipeline completion
    result = client.wait_for_pipeline(run_id)
    print(f"Pipeline completed with status: {result['status']}")
    
    return result


def example_get_pipeline_status(run_id: str):
    """
    Example: Get pipeline status using SDK.
    
    Args:
        run_id: Pipeline run ID
    """
    # Create credential
    credential = DefaultAzureCredential()
    
    # Create ADF client
    client = ADFClientSDK(
        subscription_id=SUBSCRIPTION_ID,
        resource_group_name=RESOURCE_GROUP_NAME,
        factory_name=FACTORY_NAME,
        credential=credential
    )
    
    # Get pipeline status
    status = client.get_pipeline_run_status(run_id)
    print(f"Pipeline status: {status['status']}")
    
    return status


def example_get_activity_runs(run_id: str):
    """
    Example: Get activity runs for a pipeline using SDK.
    
    Args:
        run_id: Pipeline run ID
    """
    # Create credential
    credential = DefaultAzureCredential()
    
    # Create ADF client
    client = ADFClientSDK(
        subscription_id=SUBSCRIPTION_ID,
        resource_group_name=RESOURCE_GROUP_NAME,
        factory_name=FACTORY_NAME,
        credential=credential
    )
    
    # Define time range
    end_time = datetime.now()
    start_time = end_time - timedelta(days=1)
    
    # Get activity runs
    activity_runs = client.get_activity_runs(
        run_id=run_id,
        start_time=start_time.isoformat() + "Z",
        end_time=end_time.isoformat() + "Z"
    )
    
    print(f"Found {len(activity_runs)} activity runs")
    for run in activity_runs:
        print(f"  - {run['activity_name']}: {run['status']}")
    
    return activity_runs


def example_run_pipeline_and_wait():
    """
    Example: Run a pipeline and wait for completion using SDK.
    """
    # Create credential
    credential = DefaultAzureCredential()
    
    # Create ADF client
    client = ADFClientSDK(
        subscription_id=SUBSCRIPTION_ID,
        resource_group_name=RESOURCE_GROUP_NAME,
        factory_name=FACTORY_NAME,
        credential=credential
    )
    
    # Define pipeline parameters
    kusto_query = """
    HttpRequests
    | where timestamp >= ago(7d)
    | where sdkName contains "azure"
    | summarize count() by sdkName
    | top 10 by count_ desc
    """
    
    parameters = {
        KUSTO_QUERY_PARAM_KEY: kusto_query
    }
    
    # Run pipeline and wait
    result = client.run_pipeline(
        pipeline_name=PIPELINE_NAME,
        parameters=parameters,
        wait=True,
        poll_interval=30,
        timeout=1800
    )
    
    print(f"Pipeline completed with status: {result['status']}")
    
    return result


def example_list_pipelines():
    """
    Example: List all pipelines in the Data Factory using SDK.
    """
    # Create credential
    credential = DefaultAzureCredential()
    
    # Create ADF client
    client = ADFClientSDK(
        subscription_id=SUBSCRIPTION_ID,
        resource_group_name=RESOURCE_GROUP_NAME,
        factory_name=FACTORY_NAME,
        credential=credential
    )
    
    # List pipelines
    pipelines = client.list_pipelines()
    print(f"Found {len(pipelines)} pipelines:")
    for pipeline_name in pipelines:
        print(f"  - {pipeline_name}")
    
    return pipelines


def example_get_pipeline_details(pipeline_name: str = PIPELINE_NAME):
    """
    Example: Get pipeline details using SDK.
    
    Args:
        pipeline_name: Pipeline name
    """
    # Create credential
    credential = DefaultAzureCredential()
    
    # Create ADF client
    client = ADFClientSDK(
        subscription_id=SUBSCRIPTION_ID,
        resource_group_name=RESOURCE_GROUP_NAME,
        factory_name=FACTORY_NAME,
        credential=credential
    )
    
    # Get pipeline details
    pipeline = client.get_pipeline(pipeline_name)
    print(f"Pipeline: {pipeline['name']}")
    print(f"Description: {pipeline['description']}")
    print(f"Activities: {pipeline['activities']}")
    print(f"Parameters: {pipeline['parameters']}")
    
    return pipeline


if __name__ == "__main__":
    # Example 1: List pipelines
    print("=" * 80)
    print("Example 1: List all pipelines")
    print("=" * 80)
    example_list_pipelines()
    print()
    
    # Example 2: Get pipeline details
    print("=" * 80)
    print("Example 2: Get pipeline details")
    print("=" * 80)
    example_get_pipeline_details()
    print()
    
    # Example 3: Trigger and wait for pipeline
    print("=" * 80)
    print("Example 3: Trigger pipeline with parameters and wait")
    print("=" * 80)
    result = example_run_pipeline_and_wait()
    run_id = result.get("run_id")
    print()
    
    # Example 4: Get activity runs
    if run_id:
        print("=" * 80)
        print("Example 4: Get activity runs")
        print("=" * 80)
        example_get_activity_runs(run_id)
        print()
