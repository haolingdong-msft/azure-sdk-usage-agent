"""
High-level client for Azure Data Factory operations using Azure SDK.
"""

from typing import Dict, Any, Optional, List
from azure.identity import DefaultAzureCredential
from azure.mgmt.datafactory import DataFactoryManagementClient

from .pipeline_sdk import trigger_pipeline, wait_for_pipeline, get_pipeline_run_status
from .activity_sdk import get_activity_runs
from .config import DEFAULT_POLL_INTERVAL, DEFAULT_TIMEOUT


class ADFClientSDK:
    """
    High-level client for Azure Data Factory operations using Azure SDK.
    
    This client encapsulates authentication and common ADF operations,
    providing a convenient interface for pipeline management using the official SDK.
    """
    
    def __init__(
        self,
        subscription_id: str,
        resource_group_name: str,
        factory_name: str,
        credential: Optional[DefaultAzureCredential] = None
    ):
        """
        Initialize the ADF SDK client.
        
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
        self._adf_client = None
    
    @property
    def adf_client(self) -> DataFactoryManagementClient:
        """Get or create the Data Factory Management Client."""
        if self._adf_client is None:
            self._adf_client = DataFactoryManagementClient(
                self.credential,
                self.subscription_id
            )
        return self._adf_client
    
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
        return trigger_pipeline(
            subscription_id=self.subscription_id,
            resource_group_name=self.resource_group_name,
            factory_name=self.factory_name,
            pipeline_name=pipeline_name,
            credential=self.credential,
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
        return get_pipeline_run_status(
            subscription_id=self.subscription_id,
            resource_group_name=self.resource_group_name,
            factory_name=self.factory_name,
            run_id=run_id,
            credential=self.credential
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
        return wait_for_pipeline(
            subscription_id=self.subscription_id,
            resource_group_name=self.resource_group_name,
            factory_name=self.factory_name,
            run_id=run_id,
            credential=self.credential,
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
        return get_activity_runs(
            subscription_id=self.subscription_id,
            resource_group_name=self.resource_group_name,
            factory_name=self.factory_name,
            run_id=run_id,
            start_time=start_time,
            end_time=end_time,
            credential=self.credential
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
            return {"run_id": run_id, "status": "InProgress"}
    
    def list_pipelines(self) -> List[str]:
        """
        List all pipelines in the Data Factory.
        
        Returns:
            list: List of pipeline names
        """
        pipelines = self.adf_client.pipelines.list_by_factory(
            resource_group_name=self.resource_group_name,
            factory_name=self.factory_name
        )
        return [pipeline.name for pipeline in pipelines]
    
    def get_pipeline(self, pipeline_name: str) -> Dict[str, Any]:
        """
        Get pipeline details.
        
        Args:
            pipeline_name: Pipeline name
        
        Returns:
            dict: Pipeline resource details
        """
        pipeline = self.adf_client.pipelines.get(
            resource_group_name=self.resource_group_name,
            factory_name=self.factory_name,
            pipeline_name=pipeline_name
        )
        
        # Convert to dictionary using SDK's as_dict() method
        # Returns snake_case keys like 'activity_name', 'pipeline_name', etc.
        return pipeline.as_dict()
