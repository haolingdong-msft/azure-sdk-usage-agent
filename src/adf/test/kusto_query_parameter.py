"""
Compute usage query example for Azure Data Factory pipeline runner.

Run this script using UV (as a module to support relative imports):
    uv run python -m src.adf.test.kusto_query_parameter
"""

import json
import os
from pathlib import Path
from ..auth import get_token
from ..pipeline import trigger_pipeline, wait_for_pipeline
from ..activity import get_activity_runs
from ..config import (
    SUBSCRIPTION_ID,
    RESOURCE_GROUP_NAME,
    FACTORY_NAME,
    PIPELINE_NAME,
    KUSTO_QUERY_PARAM_KEY
)


def main():
    """
    Example: Triggering and monitoring an Azure Data Factory pipeline with KustoQuery parameter.
    
    This example demonstrates how to:
    1. Read KQL query from a file
    2. Authenticate with Azure
    3. Trigger a pipeline execution with KustoQuery parameter
    4. Monitor the pipeline run status
    5. Retrieve activity run details
    """
    
    # Read KQL query from file
    # query_file = Path(__file__).parent / "example_query_failed.kql"
    query_file = Path(__file__).parent / "example_query.kql"
    print(f"Reading KQL query from: {query_file}")
    
    with open(query_file, 'r', encoding='utf-8') as f:
        kusto_query = f.read()
    
    print(f"Query content:\n{kusto_query}\n")
    
    # Pipeline parameters with KustoQuery
    pipeline_parameters = {
        KUSTO_QUERY_PARAM_KEY: kusto_query
    }
    
    try:
        # Step 1: Get authentication token
        print("Authenticating with Azure...")
        token = get_token()
        print("Authentication successful")
        print(f"{'=' * 40}\n")
        
        # Step 2: Trigger the pipeline
        print(f"\nTriggering pipeline: {PIPELINE_NAME}")
        run_id = trigger_pipeline(
            subscription_id=SUBSCRIPTION_ID,
            resource_group_name=RESOURCE_GROUP_NAME,
            factory_name=FACTORY_NAME,
            pipeline_name=PIPELINE_NAME,
            token=token,
            parameters=pipeline_parameters
        )
        print(f"{'=' * 40}\n")
        
        # Step 3: Wait for pipeline completion
        print(f"\nMonitoring pipeline run: {run_id}")
        final_status = wait_for_pipeline(
            subscription_id=SUBSCRIPTION_ID,
            resource_group_name=RESOURCE_GROUP_NAME,
            factory_name=FACTORY_NAME,
            run_id=run_id,
            token=token,
            poll_interval=30,
            timeout=3600
        )
        
        print(f"\nFinal pipeline status: {final_status.get('status')}")
        # print(json.dumps(final_status, indent=2))
        print(f"{'=' * 40}\n")
        
        # Step 4: Get activity runs
        print(f"\nRetrieving activity runs for pipeline run: {run_id}")
        
        # Use pipeline start and end times from the status
        start_time = final_status.get("runStart")
        end_time = final_status.get("runEnd")
        
        if start_time and end_time:
            activity_runs = get_activity_runs(
                subscription_id=SUBSCRIPTION_ID,
                resource_group_name=RESOURCE_GROUP_NAME,
                factory_name=FACTORY_NAME,
                run_id=run_id,
                token=token,
                start_time=start_time,
                end_time=end_time
            )
            
            print("\nActivity runs:")
            for activity in activity_runs:
                print(f"  - {activity.get('activityName')}: {activity.get('status')}")
                if activity.get('status') == 'Failed':
                    print(f"    Error: {activity.get('error', {}).get('message', 'Unknown error')}")
        
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
