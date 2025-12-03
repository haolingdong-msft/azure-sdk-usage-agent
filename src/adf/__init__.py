"""
Azure Data Factory Pipeline Runner

This package provides utilities to interact with Azure Data Factory pipelines
using the REST API (api-version=2018-06-01) with DefaultAzureCredential authentication.
"""

from .auth import get_token
from .pipeline import trigger_pipeline, wait_for_pipeline, get_pipeline_run_status
from .activity import get_activity_runs, print_activity_details
from .client import ADFClient

__all__ = [
    "get_token",
    "trigger_pipeline",
    "wait_for_pipeline",
    "get_pipeline_run_status",
    "get_activity_runs",
    "print_activity_details",
    "ADFClient",
]

__version__ = "0.1.0"
