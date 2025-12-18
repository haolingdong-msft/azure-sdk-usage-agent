"""Data models and type definitions for ADF SDK."""

from enum import Enum


# Type aliases for KQL/Kusto queries
KustoQuery = str  # KQL query string
KustoQueryFile = str  # Path to .kql file


# Specific type for Kusto query pipeline parameters
# Usage: {parameter_name: kusto_query_string}
KustoQueryPipelineParameters = dict[str, KustoQuery]


class RunStatus(str, Enum):
    """Pipeline and Activity run status."""
    QUEUED = "Queued"
    IN_PROGRESS = "InProgress"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    CANCELLED = "Cancelled"
    CANCELING = "Canceling"


def is_terminal_status(status: str) -> bool:
    """
    Check if a status is terminal (completed, failed, or cancelled).
    
    Args:
        status: Status string to check
        
    Returns:
        True if status is terminal, False otherwise
    """
    try:
        status_enum = RunStatus(status)
        return status_enum in {
            RunStatus.SUCCEEDED,
            RunStatus.FAILED,
            RunStatus.CANCELLED
        }
    except ValueError:
        # If status is not recognized, assume it's not terminal
        return False


def is_successful_status(status: str) -> bool:
    """
    Check if a status indicates success.
    
    Args:
        status: Status string to check
        
    Returns:
        True if status is Succeeded, False otherwise
    """
    try:
        return RunStatus(status) == RunStatus.SUCCEEDED
    except ValueError:
        return False
