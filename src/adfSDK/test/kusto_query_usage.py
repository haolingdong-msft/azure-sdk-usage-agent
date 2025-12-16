"""
Advanced usage example for Azure Data Factory pipeline runner using SDK.

Run this script using UV (as a module to support relative imports):
    uv run python -m src.adfSDK.test.kusto_query_usage
"""

import json
from azure.identity import DefaultAzureCredential
from ..client_sdk import ADFClientSDK
from ..config import (
    SUBSCRIPTION_ID,
    RESOURCE_GROUP_NAME,
    FACTORY_NAME,
    PIPELINE_NAME_NO_PARAMS as PIPELINE_NAME
)


def main():
    """
    Example: Triggering and monitoring an Azure Data Factory pipeline using SDK.
    
    This example demonstrates how to:
    1. Create ADF SDK client with Azure authentication
    2. Trigger a pipeline execution
    3. Monitor the pipeline run status
    4. Retrieve activity run details
    """
    
    # Optional pipeline parameters
    pipeline_parameters = {
        # "param1": "value1",
        # "param2": "value2"
    }
    
    try:
        # Step 1: Create ADF SDK client
        print("Authenticating with Azure...")
        credential = DefaultAzureCredential()
        
        client = ADFClientSDK(
            subscription_id=SUBSCRIPTION_ID,
            resource_group_name=RESOURCE_GROUP_NAME,
            factory_name=FACTORY_NAME,
            credential=credential
        )
        print("Authentication successful")
        print(f"{'=' * 40}\n")
        
        # Step 2: Trigger the pipeline
        print(f"\nTriggering pipeline: {PIPELINE_NAME}")
        run_id = client.trigger_pipeline(
            pipeline_name=PIPELINE_NAME,
            parameters=pipeline_parameters
        )
        print(f"{'=' * 40}\n")
        
        # Step 3: Wait for pipeline completion
        print(f"\nMonitoring pipeline run: {run_id}")
        final_status = client.wait_for_pipeline(
            run_id=run_id,
            poll_interval=30,
            timeout=3600
        )
        
        print(f"\nFinal pipeline status: {final_status.get('status')}")
        # print(json.dumps(final_status, indent=2))
        print(f"{'=' * 40}\n")
        
        # Step 4: Get activity runs
        print(f"\nRetrieving activity runs for pipeline run: {run_id}")
        
        # Use pipeline start and end times from the status
        start_time = final_status.get("run_start")
        end_time = final_status.get("run_end")
        
        if start_time and end_time:
            activity_runs = client.get_activity_runs(
                run_id=run_id,
                start_time=start_time,
                end_time=end_time
            )
            
            print("\nActivity runs:")
            for activity in activity_runs:
                print(f"  - {activity.get('activity_name')}: {activity.get('status')}")
                if activity.get('status') == 'Failed':
                    error = activity.get('error', {})
                    error_msg = error.get('message', 'Unknown error') if isinstance(error, dict) else str(error)
                    print(f"    Error: {error_msg}")
        
        # Check if pipeline succeeded
        if final_status.get("status") == "Succeeded":
            print("\n✓ Pipeline completed successfully!")
        else:
            print(f"\n✗ Pipeline finished with status: {final_status.get('status')}")
            
    except Exception as e:
        print(f"\nError: {str(e)}")
        raise


if __name__ == "__main__":
    main()
