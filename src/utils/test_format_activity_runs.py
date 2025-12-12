"""
Test script for format_activity_runs function

Usage:
    uv run python src/utils/test_format_activity_runs.py

Description:
    This script tests the format_activity_runs function with real JSON data from
    Azure Data Factory activity runs. It loads activity run snapshots and formats
    them to verify the output formatting is correct.

Test Files:
    - activity_runs_succeeded.json: Contains a successful Kusto query activity
    - activity_runs_failed.json: Contains a failed activity with timeout error
"""

import json
import os
from pathlib import Path
from utils import format_activity_runs


def load_json_file(file_path: str):
    """Load JSON file and return the data"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def test_format_activity_runs():
    """Test format_activity_runs with both succeeded and failed activity runs"""
    
    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent
    
    # Load the test data
    # test_file = project_root / "src/adf/test/snapshots/activity_runs_succeeded.json"
    test_file = project_root / "src/adf/test/snapshots/activity_runs_failed.json"
    
    # Test: activity runs
    print(f"Testing with ${test_file} activity runs")
    
    print("Start" + "*" * 100)
    
    data = load_json_file(test_file)
    activity_runs = data.get("value", [])
    
    formatted_message, full_data = format_activity_runs(
        activity_runs=activity_runs,
        pipeline_duration_ms=25601,
        run_id="test-run-id-succeeded-12345"
    )
    
    print("End" + "*" * 100)
    
    print(f"message:\n {formatted_message}")
    print(f"\n\nTotal data records extracted: {len(full_data)}")
    if full_data:
        print(f"\nShowing first 10 records (out of {len(full_data)} total):")
        print(json.dumps(full_data[:10], indent=2))
    

if __name__ == "__main__":
    test_format_activity_runs()
