"""
High-level client for Azure Data Factory operations.
"""

from typing import Dict, Any, Optional, List
from azure.identity import DefaultAzureCredential

from .auth import get_token
from .pipeline import trigger_pipeline, wait_for_pipeline, get_pipeline_run_status
from .activity import get_activity_runs
from .config import DEFAULT_POLL_INTERVAL, DEFAULT_TIMEOUT


class ADFClient:
    """
    High-level client for Azure Data Factory operations.
    
    This client encapsulates authentication and common ADF operations,
    providing a convenient interface for pipeline management.
    """
    
    def __init__(
        self,
        subscription_id: str,
        resource_group_name: str,
        factory_name: str,
        credential: Optional[DefaultAzureCredential] = None
    ):
        """
        Initialize the ADF client.
        
        Args:
            subscription_id: Azure subscription ID
            resource_group_name: Resource group name
            factory_name: Data Factory name
            credential: Azure credential instance. If None, creates a new DefaultAzureCredential.
        """
        self.subscription_id = subscription_id
        self.resource_group_name = resource_group_name
        self.factory_name = factory_name
        self.credential = credential or DefaultAzureCredential()
        self._token = None
    
    def _get_token(self) -> str:
        """Get or refresh the access token."""
        if self._token is None:
            self._token = get_token(self.credential)
        return self._token
    
    def refresh_token(self) -> str:
        """Force refresh the access token."""
        self._token = get_token(self.credential)
        return self._token
    
    def trigger_pipeline(
        self,
        pipeline_name: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Trigger a pipeline run.
        
        Args:
            pipeline_name: Pipeline name to trigger
            parameters: Optional dictionary of pipeline parameters
        
        Returns:
            str: Run ID of the triggered pipeline
        """
        token = self._get_token()
        return trigger_pipeline(
            subscription_id=self.subscription_id,
            resource_group_name=self.resource_group_name,
            factory_name=self.factory_name,
            pipeline_name=pipeline_name,
            token=token,
            parameters=parameters
        )
    
    def get_pipeline_run_status(self, run_id: str) -> Dict[str, Any]:
        """
        Get the status of a pipeline run.
        
        Args:
            run_id: Pipeline run ID
        
        Returns:
            dict: Pipeline run status information
        """
        token = self._get_token()
        return get_pipeline_run_status(
            subscription_id=self.subscription_id,
            resource_group_name=self.resource_group_name,
            factory_name=self.factory_name,
            run_id=run_id,
            token=token
        )
    
    def wait_for_pipeline(
        self,
        run_id: str,
        poll_interval: int = DEFAULT_POLL_INTERVAL,
        timeout: int = DEFAULT_TIMEOUT
    ) -> Dict[str, Any]:
        """
        Wait for a pipeline run to complete.
        
        Args:
            run_id: Pipeline run ID
            poll_interval: Seconds between status checks
            timeout: Maximum seconds to wait
        
        Returns:
            dict: Final pipeline run status information
        """
        token = self._get_token()
        return wait_for_pipeline(
            subscription_id=self.subscription_id,
            resource_group_name=self.resource_group_name,
            factory_name=self.factory_name,
            run_id=run_id,
            token=token,
            poll_interval=poll_interval,
            timeout=timeout
        )
    
    def get_activity_runs(
        self,
        run_id: str,
        start_time: str,
        end_time: str
    ) -> List[Dict[str, Any]]:
        """
        Get activity runs for a pipeline run.
        
        Args:
            run_id: Pipeline run ID
            start_time: Start time in ISO 8601 format
            end_time: End time in ISO 8601 format
        
        Returns:
            list: List of activity run information dictionaries
        """
        token = self._get_token()
        return get_activity_runs(
            subscription_id=self.subscription_id,
            resource_group_name=self.resource_group_name,
            factory_name=self.factory_name,
            run_id=run_id,
            token=token,
            start_time=start_time,
            end_time=end_time
        )
    
    def run_pipeline(
        self,
        pipeline_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        wait: bool = True,
        poll_interval: int = DEFAULT_POLL_INTERVAL,
        timeout: int = DEFAULT_TIMEOUT
    ) -> Dict[str, Any]:
        """
        Trigger a pipeline and optionally wait for completion.
        
        This is a convenience method that combines trigger and wait operations.
        
        Args:
            pipeline_name: Pipeline name to trigger
            parameters: Optional dictionary of pipeline parameters
            wait: Whether to wait for pipeline completion
            poll_interval: Seconds between status checks
            timeout: Maximum seconds to wait
        
        Returns:
            dict: Pipeline run status information
        """
        run_id = self.trigger_pipeline(pipeline_name, parameters)
        
        if wait:
            return self.wait_for_pipeline(run_id, poll_interval, timeout)
        else:
            return {"runId": run_id, "status": "InProgress"}
