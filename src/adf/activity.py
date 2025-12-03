"""
Activity run operations for Azure Data Factory.
"""

from typing import Dict, Any, List

import requests

from .config import API_VERSION


def get_activity_runs(
    subscription_id: str,
    resource_group_name: str,
    factory_name: str,
    run_id: str,
    token: str,
    start_time: str,
    end_time: str
) -> List[Dict[str, Any]]:
    """
    Get activity runs for a pipeline run.
    
    Args:
        subscription_id: Azure subscription ID
        resource_group_name: Resource group name
        factory_name: Data Factory name
        run_id: Pipeline run ID
        token: Bearer token for authentication
        start_time: Start time in ISO 8601 format (e.g., "2024-01-01T00:00:00Z")
        end_time: End time in ISO 8601 format (e.g., "2024-01-01T23:59:59Z")
    
    Returns:
        list: List of activity run information dictionaries
    
    Raises:
        requests.HTTPError: If the API request fails
    """
    url = (
        f"https://management.azure.com/subscriptions/{subscription_id}"
        f"/resourceGroups/{resource_group_name}"
        f"/providers/Microsoft.DataFactory/factories/{factory_name}"
        f"/pipelineruns/{run_id}/queryActivityRuns"
        f"?api-version={API_VERSION}"
    )
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    body = {
        "lastUpdatedAfter": start_time,
        "lastUpdatedBefore": end_time
    }
    
    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()
    
    result = response.json()
    activity_runs = result.get("value", [])
    
    print(f"Retrieved {len(activity_runs)} activity runs")
    return activity_runs


def print_activity_details(activity_runs: List[Dict[str, Any]]) -> None:
    """
    Print detailed information about activity runs including outputs.
    
    Args:
        activity_runs: List of activity run dictionaries
    """
    if not activity_runs:
        print("No activity runs found.")
        return
    
    for idx, activity in enumerate(activity_runs, 1):
        print(f"\n{'=' * 80}")
        print(f"Activity #{idx}: {activity.get('activityName')}")
        print(f"{'=' * 80}")
        print(f"Type:     {activity.get('activityType')}")
        print(f"Status:   {activity.get('status')}")
        print(f"Start:    {activity.get('activityRunStart')}")
        print(f"End:      {activity.get('activityRunEnd')}")
        print(f"Duration: {activity.get('durationInMs')} ms")
        
        # Display output if available
        output = activity.get('output')
        if output:
            print(f"\nOutput:")
            import json
            print(json.dumps(output, indent=2))
        
        # Display error if failed
        if activity.get('status') == 'Failed':
            error = activity.get('error', {})
            print(f"\n❌ Error:")
            print(f"  Code:    {error.get('errorCode', 'Unknown')}")
            print(f"  Message: {error.get('message', 'Unknown error')}")
            if error.get('failureType'):
                print(f"  Type:    {error.get('failureType')}")
        
        # Display input if available
        input_data = activity.get('input')
        if input_data:
            print(f"\nInput:")
            import json
            print(json.dumps(input_data, indent=2))
