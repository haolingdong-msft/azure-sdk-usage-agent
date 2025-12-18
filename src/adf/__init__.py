"""
Azure Data Factory SDK - Modern Python SDK for Azure Data Factory operations.

This package provides a high-level interface for interacting with Azure Data Factory
using the official Azure SDK, with enhanced type safety, logging, and error handling.

Example:
    Basic usage:
    >>> from adfSDK import ADFClient
    >>> client = ADFClient(
    ...     subscription_id="your-subscription-id",
    ...     resource_group_name="your-rg",
    ...     factory_name="your-factory"
    ... )
    >>> run_id = client.trigger_pipeline("my-pipeline")
    
    Using environment variables:
    >>> client = ADFClient.new()
    >>> result = client.run_pipeline("my-pipeline", wait=True)
    
    Using context manager:
    >>> with ADFClient.new() as client:
    ...     activities = client.get_activity_runs(run_id, start_time, end_time)
"""

from .__version__ import __version__, __author__, __license__, __description__
from .client import ADFClient
from .models import (
    RunStatus,

    KustoQuery,
    KustoQueryFile,
    KustoQueryPipelineParameters,
    is_terminal_status,
    is_successful_status
)
# Re-export Azure SDK types for convenience
from azure.mgmt.datafactory.models import PipelineRun, ActivityRun
from .exceptions import (
    ADFError,
    PipelineError,
    PipelineTimeoutError,
    PipelineTriggerError,
    ActivityError,
    ConfigurationError
)
from .config import Config, DEFAULT_POLL_INTERVAL, DEFAULT_TIMEOUT

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__license__",
    "__description__",
    
    # Main client
    "ADFClient",
    
    # Configuration
    "Config",
    "DEFAULT_POLL_INTERVAL",
    "DEFAULT_TIMEOUT",
    
    # Models and types
    "RunStatus",
    "KustoQuery",
    "KustoQueryFile",
    "KustoQueryPipelineParameters",
    "is_terminal_status",
    "is_successful_status",
    
    # Azure SDK types (re-exported for convenience)
    "PipelineRun",
    "ActivityRun",
    
    # Exceptions
    "ADFError",
    "PipelineError",
    "PipelineTimeoutError",
    "PipelineTriggerError",
    "ActivityError",
    "ConfigurationError",
]

