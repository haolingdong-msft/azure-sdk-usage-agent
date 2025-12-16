"""
Configuration constants for Azure Data Factory SDK.
Reuses configuration from the REST API version.
"""

import sys
from pathlib import Path

# Add parent directory to path to import from adf package
sys.path.insert(0, str(Path(__file__).parent.parent))

from adf.config import (
    API_VERSION,
    MANAGEMENT_SCOPE,
    MANAGEMENT_BASE_URL,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_TIMEOUT,
    SUBSCRIPTION_ID,
    RESOURCE_GROUP_NAME,
    FACTORY_NAME,
    PIPELINE_NAME,
    PIPELINE_NAME_NO_PARAMS,
    KUSTO_QUERY_PARAM_KEY
)

__all__ = [
    "API_VERSION",
    "MANAGEMENT_SCOPE",
    "MANAGEMENT_BASE_URL",
    "DEFAULT_POLL_INTERVAL",
    "DEFAULT_TIMEOUT",
    "SUBSCRIPTION_ID",
    "RESOURCE_GROUP_NAME",
    "FACTORY_NAME",
    "PIPELINE_NAME",
    "PIPELINE_NAME_NO_PARAMS",
    "KUSTO_QUERY_PARAM_KEY",
]
