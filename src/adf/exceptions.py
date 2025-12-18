"""Exception hierarchy for ADF SDK."""

from typing import Optional


class ADFError(Exception):
    """Base exception for all ADF SDK errors."""
    
    def __init__(self, message: str, details: Optional[dict[str, object]] = None):
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


class ActivityError(ADFError):
    """Base exception for activity-related errors."""
    pass


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
