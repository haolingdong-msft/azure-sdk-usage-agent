"""Exception hierarchy for ADF SDK."""

from typing import Optional, Any


class ADFError(Exception):
    """Base exception for all ADF SDK errors."""
    
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        """
        Initialize ADF error.
        
        Args:
            message: Error message
            details: Optional dictionary with additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class PipelineError(ADFError):
    """Base exception for pipeline-related errors."""
    pass


class PipelineNotFoundError(PipelineError):
    """Exception raised when a pipeline is not found."""
    
    def __init__(self, pipeline_name: str):
        """
        Initialize PipelineNotFoundError.
        
        Args:
            pipeline_name: Name of the pipeline that was not found
        """
        self.pipeline_name = pipeline_name
        super().__init__(
            f"Pipeline '{pipeline_name}' not found",
            {"pipeline_name": pipeline_name}
        )


class PipelineTimeoutError(PipelineError):
    """Exception raised when a pipeline run times out."""
    
    def __init__(self, run_id: str, elapsed: int, timeout: int):
        """
        Initialize PipelineTimeoutError.
        
        Args:
            run_id: Pipeline run ID
            elapsed: Elapsed time in seconds
            timeout: Timeout limit in seconds
        """
        self.run_id = run_id
        self.elapsed = elapsed
        self.timeout = timeout
        super().__init__(
            f"Pipeline run '{run_id}' timed out after {elapsed}s (limit: {timeout}s)",
            {
                "run_id": run_id,
                "elapsed": elapsed,
                "timeout": timeout
            }
        )


class PipelineTriggerError(PipelineError):
    """Exception raised when pipeline trigger fails."""
    
    def __init__(self, pipeline_name: str, reason: Optional[str] = None):
        """
        Initialize PipelineTriggerError.
        
        Args:
            pipeline_name: Name of the pipeline
            reason: Optional reason for the failure
        """
        self.pipeline_name = pipeline_name
        self.reason = reason
        message = f"Failed to trigger pipeline '{pipeline_name}'"
        if reason:
            message += f": {reason}"
        super().__init__(message, {"pipeline_name": pipeline_name, "reason": reason})


class PipelineExecutionError(PipelineError):
    """Exception raised when a pipeline execution fails."""
    
    def __init__(self, run_id: str, status: str, message: Optional[str] = None):
        """
        Initialize PipelineExecutionError.
        
        Args:
            run_id: Pipeline run ID
            status: Final status of the pipeline run
            message: Optional error message from the pipeline
        """
        self.run_id = run_id
        self.status = status
        error_msg = f"Pipeline run '{run_id}' failed with status: {status}"
        if message:
            error_msg += f" - {message}"
        super().__init__(
            error_msg,
            {"run_id": run_id, "status": status, "message": message}
        )


class ActivityError(ADFError):
    """Base exception for activity-related errors."""
    pass


class ActivityRunNotFoundError(ActivityError):
    """Exception raised when activity runs are not found."""
    
    def __init__(self, run_id: str):
        """
        Initialize ActivityRunNotFoundError.
        
        Args:
            run_id: Pipeline run ID
        """
        self.run_id = run_id
        super().__init__(
            f"No activity runs found for pipeline run '{run_id}'",
            {"run_id": run_id}
        )


class ActivityQueryError(ActivityError):
    """Exception raised when querying activity runs fails."""
    
    def __init__(self, run_id: str, reason: Optional[str] = None):
        """
        Initialize ActivityQueryError.
        
        Args:
            run_id: Pipeline run ID
            reason: Optional reason for the failure
        """
        self.run_id = run_id
        self.reason = reason
        message = f"Failed to query activity runs for pipeline run '{run_id}'"
        if reason:
            message += f": {reason}"
        super().__init__(message, {"run_id": run_id, "reason": reason})


class AuthenticationError(ADFError):
    """Exception raised for authentication failures."""
    
    def __init__(self, message: str = "Authentication failed"):
        """
        Initialize AuthenticationError.
        
        Args:
            message: Error message
        """
        super().__init__(message)


class ConfigurationError(ADFError):
    """Exception raised for configuration errors."""
    
    def __init__(self, message: str, missing_fields: Optional[list[str]] = None):
        """
        Initialize ConfigurationError.
        
        Args:
            message: Error message
            missing_fields: Optional list of missing configuration fields
        """
        self.missing_fields = missing_fields or []
        details = {}
        if missing_fields:
            details["missing_fields"] = missing_fields
        super().__init__(message, details)
