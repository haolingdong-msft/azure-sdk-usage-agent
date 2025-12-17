"""
High-level client for Azure Data Factory operations using Azure SDK.
"""

from typing import Dict, Any, Optional, List
from azure.identity import DefaultAzureCredential
from azure.mgmt.datafactory import DataFactoryManagementClient

from .operations import (
    trigger_pipeline,
    get_pipeline_run_status,
    wait_for_pipeline,
    get_activity_runs
)
from .models import PipelineRunInfo, ActivityRunInfo, RunStatus
from .exceptions import ConfigurationError
from .utils import get_logger, setup_logging
from .config import ADFConfig, DEFAULT_POLL_INTERVAL, DEFAULT_TIMEOUT


logger = get_logger(__name__)


class ADFClient:
    """
    High-level client for Azure Data Factory operations.
    
    Example:
        >>> client = ADFClientSDK.new()
        >>> run_id = client.trigger_pipeline("my-pipeline")
        >>> status = client.wait_for_pipeline(run_id)
    """
    
    def __init__(
        self,
        subscription_id: str,
        resource_group_name: str,
        factory_name: str,
        credential: Optional[DefaultAzureCredential] = None,
        config: Optional[ADFConfig] = None
    ):
        """
        Initialize the ADF SDK client.
        
        Args:
            subscription_id: Azure subscription ID
            resource_group_name: Resource group name
            factory_name: Data Factory name
            credential: Azure credential instance. If None, creates a new DefaultAzureCredential
            config: Optional ADFConfig instance for business defaults (pipeline_name, poll_interval, etc.)
                   Config is NOT required - it only provides default values for runtime parameters.
        
        Raises:
            ConfigurationError: If required parameters are missing
        """
        # Validate required parameters
        if not subscription_id:
            raise ConfigurationError("subscription_id is required")
        if not resource_group_name:
            raise ConfigurationError("resource_group_name is required")
        if not factory_name:
            raise ConfigurationError("factory_name is required")
        
        self.subscription_id = subscription_id
        self.resource_group_name = resource_group_name
        self.factory_name = factory_name
        self.credential = credential or DefaultAzureCredential()
        
        # Config is optional - only used for business defaults
        self.config = config
        
        # Setup logging
        log_level = config.log_level if config else "INFO"
        log_format = config.log_format if config else "%(levelname)s - %(message)s"
        setup_logging(level=log_level, log_format=log_format)
        
        # Lazy-loaded ADF client
        self._adf_client = None
        
        logger.info(
            f"Initialized ADFClient for factory: {factory_name} "
            f"in resource group: {resource_group_name}"
        )
    
    @classmethod
    def new(cls, config: Optional[ADFConfig] = None, credential: Optional[DefaultAzureCredential] = None) -> "ADFClient":
        """
        Create a new ADF client from environment variables or custom configuration.
        
        This unified method can work in multiple ways:
        1. No config: Read core Azure settings from env vars, use built-in defaults for runtime params
        2. Partial config: Override specific settings (e.g., pipeline_name), others from env/defaults
        3. Full config: Complete custom configuration
        
        Required environment variables (for core Azure resources):
            - AZURE_SUBSCRIPTION_ID: Azure subscription ID
            - AZURE_RESOURCE_GROUP: Resource group name
            - AZURE_FACTORY_NAME: Data Factory name
        
        Optional environment variables (for business defaults):
            - ADF_PIPELINE_NAME: Default pipeline name
            - ADF_POLL_INTERVAL: Default poll interval in seconds
            - ADF_TIMEOUT: Default timeout in seconds
            - ADF_LOG_LEVEL: Log level
            - ADF_LOG_FORMAT: Log format
            - ADF_AUTO_SAVE: Auto save results
            - ADF_OUTPUT_DIR: Output directory
        
        Args:
            config: Optional ADFConfig for business defaults (pipeline_name, poll_interval, etc.).
                    If None, only core Azure settings are loaded from env vars.
                    Runtime parameters will use built-in defaults unless overridden in method calls.
            credential: Optional Azure credential instance
            
        Returns:
            ADFClient instance
            
        Raises:
            ConfigurationError: If required environment variables are missing
            
        Examples:
            >>> # Simple: Only core Azure settings from env, no config needed
            >>> client = ADFClient.new()
            >>> client.run_pipeline(pipeline_name="MyPipeline")  # Pass params when calling
            
            >>> # With defaults: Config provides business defaults
            >>> config = ADFConfig(pipeline_name="MyPipeline", poll_interval=15)
            >>> client = ADFClient.new(config=config)
            >>> client.run_pipeline()  # Uses config defaults
        """
        # Always read core Azure settings from environment
        base_config = ADFConfig.from_env()
        
        # If user provided config, it takes precedence for business defaults
        # Otherwise, use the base_config (which has env vars + built-in defaults)
        final_config = config if config else base_config
        
        return cls(
            subscription_id=base_config.subscription_id,
            resource_group_name=base_config.resource_group_name,
            factory_name=base_config.factory_name,
            credential=credential,
            config=final_config if config else None  # Pass None if no custom config provided
        )
    
    @property
    def adf_client(self) -> DataFactoryManagementClient:
        """
        Get or create the Data Factory Management Client (lazy-loaded).
        
        Returns:
            DataFactoryManagementClient instance
        """
        if self._adf_client is None:
            self._adf_client = DataFactoryManagementClient(
                self.credential,
                self.subscription_id
            )
            logger.debug("Created DataFactoryManagementClient")
        return self._adf_client
    
    def trigger_pipeline(
        self,
        pipeline_name: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Trigger a pipeline run.
        
        Args:
            pipeline_name: Pipeline name to trigger. If None, uses config.pipeline_name
            parameters: Optional dictionary of pipeline parameters
        
        Returns:
            str: Run ID of the triggered pipeline
            
        Raises:
            PipelineTriggerError: If triggering fails
            ConfigurationError: If pipeline_name is not provided and not in config
        """
        # Priority: parameter > config > error
        if pipeline_name is None:
            if self.config and self.config.pipeline_name:
                pipeline_name = self.config.pipeline_name
            else:
                raise ConfigurationError(
                    "pipeline_name is required. Either pass it as parameter or set it in config."
                )
        
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
            dict: Pipeline run status information (PipelineRunInfo compatible)
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
        poll_interval: Optional[int] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Wait for a pipeline run to complete.
        
        Args:
            run_id: Pipeline run ID
            poll_interval: Seconds between status checks. Priority: parameter > config > 30 (default)
            timeout: Maximum seconds to wait. Priority: parameter > config > 3600 (default)
        
        Returns:
            dict: Final pipeline run status information
            
        Raises:
            PipelineTimeoutError: If timeout is exceeded
        """
        # Priority: parameter > config > built-in default
        if poll_interval is None:
            poll_interval = self.config.poll_interval if self.config else DEFAULT_POLL_INTERVAL
        if timeout is None:
            timeout = self.config.timeout if self.config else DEFAULT_TIMEOUT
        
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
        end_time: str,
        save_to_file: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """
        Get activity runs for a pipeline run.
        
        Args:
            run_id: Pipeline run ID
            start_time: Start time in ISO 8601 format
            end_time: End time in ISO 8601 format
            save_to_file: Whether to save to file. Priority: parameter > config > False (default)
        
        Returns:
            list: List of activity run information dictionaries (ActivityRunInfo compatible)
            
        Raises:
            ActivityQueryError: If query fails
        """
        # Priority: parameter > config > built-in default (False)
        if save_to_file is None:
            save_to_file = self.config.auto_save_results if self.config else False
        
        return get_activity_runs(
            subscription_id=self.subscription_id,
            resource_group_name=self.resource_group_name,
            factory_name=self.factory_name,
            run_id=run_id,
            start_time=start_time,
            end_time=end_time,
            credential=self.credential,
            save_to_file=save_to_file
        )
    
    def run_pipeline(
        self,
        pipeline_name: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        wait: bool = True,
        poll_interval: Optional[int] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Trigger a pipeline and optionally wait for completion.
        
        This is a convenience method that combines trigger and wait operations.
        
        Args:
            pipeline_name: Pipeline name to trigger. Priority: parameter > config > error
            parameters: Optional dictionary of pipeline parameters
            wait: Whether to wait for pipeline completion (default: True)
            poll_interval: Seconds between status checks. Priority: parameter > config > 30
            timeout: Maximum seconds to wait. Priority: parameter > config > 3600
        
        Returns:
            dict: Pipeline run status information
            
        Raises:
            PipelineTriggerError: If triggering fails
            PipelineTimeoutError: If timeout is exceeded (when wait=True)
            ConfigurationError: If pipeline_name is not provided and not in config
        """
        run_id = self.trigger_pipeline(pipeline_name, parameters)
        
        if wait:
            return self.wait_for_pipeline(run_id, poll_interval, timeout)
        else:
            return {
                "run_id": run_id,
                "status": RunStatus.IN_PROGRESS.value,
                "message": "Pipeline triggered, not waiting for completion"
            }
    
    def list_pipelines(self) -> List[str]:
        """
        List all pipelines in the Data Factory.
        
        Returns:
            list: List of pipeline names
        """
        logger.debug("Listing pipelines")
        pipelines = self.adf_client.pipelines.list_by_factory(
            resource_group_name=self.resource_group_name,
            factory_name=self.factory_name
        )
        pipeline_names = [pipeline.name for pipeline in pipelines]
        logger.info(f"Found {len(pipeline_names)} pipelines")
        return pipeline_names
    
    def get_pipeline(self, pipeline_name: str) -> Dict[str, Any]:
        """
        Get pipeline details.
        
        Args:
            pipeline_name: Pipeline name
        
        Returns:
            dict: Pipeline resource details
        """
        logger.debug(f"Getting pipeline: {pipeline_name}")
        pipeline = self.adf_client.pipelines.get(
            resource_group_name=self.resource_group_name,
            factory_name=self.factory_name,
            pipeline_name=pipeline_name
        )
        
        # Convert to dictionary using SDK's as_dict() method
        return pipeline.as_dict()
    
    def __enter__(self) -> "ADFClient":
        """Context manager entry."""
        logger.debug("Entering ADFClient context")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        logger.debug("Exiting ADFClient context")
        self.close()
    
    def close(self) -> None:
        """
        Clean up resources.
        
        Closes the underlying Azure SDK client if it was created.
        """
        if self._adf_client is not None:
            self._adf_client.close()
            self._adf_client = None
            logger.info("Closed ADFClient")
    
    def __repr__(self) -> str:
        """String representation of the client."""
        return (
            f"ADFClient(factory_name='{self.factory_name}', "
            f"resource_group='{self.resource_group_name}', "
            f"subscription_id='{self.subscription_id[:8]}...')"
        )
