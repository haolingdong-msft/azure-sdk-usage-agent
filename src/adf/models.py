"""Data models and type definitions for ADF SDK."""

from typing import TypedDict, Any, Optional
from enum import Enum


class RunStatus(str, Enum):
    """Pipeline and Activity run status."""
    QUEUED = "Queued"
    IN_PROGRESS = "InProgress"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    CANCELLED = "Cancelled"
    CANCELING = "Canceling"


class ActivityType(str, Enum):
    """Activity types in Azure Data Factory."""
    COPY = "Copy"
    EXECUTE_PIPELINE = "ExecutePipeline"
    WEB = "Web"
    LOOKUP = "Lookup"
    GET_METADATA = "GetMetadata"
    DELETE = "Delete"
    SQL_SERVER_STORED_PROCEDURE = "SqlServerStoredProcedure"
    CUSTOM = "Custom"
    DATABRICKS_NOTEBOOK = "DatabricksNotebook"
    DATABRICKS_SPARK_JAR = "DatabricksSparkJar"
    DATABRICKS_SPARK_PYTHON = "DatabricksSparkPython"
    AZURE_ML_BATCH_EXECUTION = "AzureMLBatchExecution"
    AZURE_ML_UPDATE_RESOURCE = "AzureMLUpdateResource"
    HDI_SPARK = "HDInsightSpark"
    HDI_HIVE = "HDInsightHive"
    HDI_PIG = "HDInsightPig"
    HDI_MAP_REDUCE = "HDInsightMapReduce"
    HDI_STREAMING = "HDInsightStreaming"


class PipelineRunInfo(TypedDict, total=False):
    """Type definition for pipeline run information."""
    run_id: str
    pipeline_name: str
    status: str
    run_start: Optional[str]
    run_end: Optional[str]
    duration_in_ms: Optional[int]
    parameters: Optional[dict[str, Any]]
    message: Optional[str]
    run_group_id: Optional[str]
    is_latest: Optional[bool]
    invoked_by: Optional[dict[str, Any]]


class ActivityRunInfo(TypedDict, total=False):
    """Type definition for activity run information."""
    pipeline_name: str
    pipeline_run_id: str
    activity_name: str
    activity_type: str
    activity_run_id: str
    linked_service_name: Optional[str]
    status: str
    activity_run_start: Optional[str]
    activity_run_end: Optional[str]
    duration_in_ms: Optional[int]
    input: Optional[dict[str, Any]]
    output: Optional[dict[str, Any]]
    error: Optional[dict[str, Any]]


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
