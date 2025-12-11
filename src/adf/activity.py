"""
Activity run operations for Azure Data Factory.
"""

from typing import Dict, Any, List
import json
from pathlib import Path
from datetime import datetime

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
    
    # Save result to JSON file
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"activity_runs_{timestamp}_{run_id}.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"Activity runs result saved to: {output_file}")
    
    activity_runs = result.get("value", [])
    
    print(f"Retrieved {len(activity_runs)} activity runs")
    return activity_runs
