"""
High-level client for Azure Data Factory operations using Azure SDK.
"""

from typing import Optional
from azure.identity import DefaultAzureCredential
from azure.mgmt.datafactory import DataFactoryManagementClient
from azure.mgmt.datafactory.models import PipelineRun, ActivityRun

from .pipeline import (
    trigger_pipeline,
    get_pipeline_run_status,
    wait_for_pipeline,
)
from .activity import get_activity_runs
from .models import (
    RunStatus,
    KustoQueryPipelineParameters,
)
from .exceptions import ConfigurationError
from .utils import get_logger


logger = get_logger(__name__)


class ADFClient:
    """
    High-level client for Azure Data Factory operations.

    Example:
        src/adf/examples/kusto_query_usage.py
    """

    def __init__(
        self,
        subscription_id: str,
        resource_group_name: str,
        factory_name: str,
        credential: Optional[DefaultAzureCredential] = None,
    ):
        """
        Initialize the ADF client.

        Args:
            subscription_id: Azure subscription ID
            resource_group_name: Resource group name
            factory_name: Data Factory name
            credential: Azure credential instance. If None, creates DefaultAzureCredential

        Raises:
            ConfigurationError: If required parameters are missing
        """
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

        # Create ADF client once
        self.adf_client = DataFactoryManagementClient(
            self.credential, self.subscription_id
        )

        logger.info(
            f"Initialized ADFClient for factory: {factory_name} "
            f"in resource group: {resource_group_name}"
        )

    def trigger_pipeline(
        self, pipeline_name: str, parameters: Optional[KustoQueryPipelineParameters] = None
    ) -> str:
        """
        Trigger a pipeline run.

        Args:
            pipeline_name: Pipeline name to trigger
            parameters: Optional dictionary of pipeline parameters

        Returns:
            str: Run ID of the triggered pipeline

        Raises:
            PipelineTriggerError: If triggering fails
        """
        return trigger_pipeline(
            adf_client=self.adf_client,
            resource_group_name=self.resource_group_name,
            factory_name=self.factory_name,
            pipeline_name=pipeline_name,
            parameters=parameters,
        )

    def get_pipeline_run_status(self, run_id: str) -> PipelineRun:
        """
        Get the current status of a pipeline run.

        Args:
            run_id: Pipeline run ID returned from trigger_pipeline

        Returns:
            PipelineRun: Azure SDK PipelineRun object containing:
                - status: Current run status (e.g., 'InProgress', 'Succeeded', 'Failed')
                - run_id: Pipeline run identifier
                - pipeline_name: Name of the pipeline
                - run_start: Run start timestamp
                - run_end: Run end timestamp (if completed)
                - Additional metadata and error details

        Raises:
            Exception: If fetching the status fails
        """
        return get_pipeline_run_status(
            adf_client=self.adf_client,
            resource_group_name=self.resource_group_name,
            factory_name=self.factory_name,
            run_id=run_id,
        )

    def wait_for_pipeline(
        self, run_id: str, poll_interval: int = 30, timeout: int = 3600, save_to_file: bool = False
    ) -> PipelineRun:
        """
        Wait for a pipeline run to complete by polling its status.

        Args:
            run_id: Pipeline run ID to monitor
            poll_interval: Seconds between status checks (default: 30)
            timeout: Maximum seconds to wait before raising timeout error (default: 3600)
            save_to_file: If True, saves final pipeline status to output/pipeline_status_{timestamp}_{run_id}.json (default: False)

        Returns:
            PipelineRun: Final Azure SDK PipelineRun object with completion details

        Raises:
            PipelineTimeoutError: If pipeline doesn't complete within the timeout period
        """
        return wait_for_pipeline(
            adf_client=self.adf_client,
            resource_group_name=self.resource_group_name,
            factory_name=self.factory_name,
            run_id=run_id,
            poll_interval=poll_interval,
            timeout=timeout,
            save_to_file=save_to_file,
        )

    def get_activity_runs(
        self, run_id: str, start_time: str, end_time: str, save_to_file: bool = False
    ) -> list[ActivityRun]:
        """
        Get detailed information about all activity runs within a pipeline run.

        Args:
            run_id: Pipeline run ID to query activities for
            start_time: Query start time in ISO 8601 format (e.g., '2024-01-01T00:00:00Z')
            end_time: Query end time in ISO 8601 format (e.g., '2024-01-01T23:59:59Z')
            save_to_file: If True, saves activity runs to output/{run_id}.json (default: False)

        Returns:
            list[ActivityRun]: List of Azure SDK ActivityRun objects, each containing:
                - activity_name: Name of the activity
                - status: Activity execution status
                - activity_type: Type of activity (Copy, ExecutePipeline, etc.)
                - start/end times, duration, and error details if applicable

        Raises:
            ActivityQueryError: If the query fails or returns invalid data
        """
        return get_activity_runs(
            adf_client=self.adf_client,
            resource_group_name=self.resource_group_name,
            factory_name=self.factory_name,
            run_id=run_id,
            start_time=start_time,
            end_time=end_time,
            save_to_file=save_to_file,
        )

    def run_pipeline(
        self,
        pipeline_name: str,
        parameters: Optional[KustoQueryPipelineParameters] = None,
        wait: bool = True,
        poll_interval: int = 30,
        timeout: int = 3600,
        save_to_file: bool = False,
    ) -> PipelineRun | dict[str, str]:
        """
        Trigger a pipeline and optionally wait for completion (high-level convenience method).

        Args:
            pipeline_name: Name of the pipeline to execute
            parameters: Optional dictionary of pipeline parameters to pass to the run
            wait: If True, waits for completion; if False, returns immediately after trigger (default: True)
            poll_interval: Seconds between status checks when waiting (default: 30)
            timeout: Maximum seconds to wait for completion (default: 3600)
            save_to_file: If True, saves final pipeline status to output/pipeline_status_{timestamp}_{run_id}.json (default: False)

        Returns:
            PipelineRun | dict: When wait=True, returns Azure SDK PipelineRun object;
                  when wait=False, returns dict with run_id and status

        Raises:
            PipelineTriggerError: If triggering the pipeline fails
            PipelineTimeoutError: If timeout is exceeded when wait=True
        """
        run_id = self.trigger_pipeline(pipeline_name, parameters)

        if wait:
            return self.wait_for_pipeline(run_id, poll_interval, timeout, save_to_file)
        else:
            return {
                "run_id": run_id,
                "status": RunStatus.IN_PROGRESS.value,
                "message": "Pipeline triggered, not waiting for completion",
            }

    def __enter__(self) -> "ADFClient":
        """
        Context manager entry.

        Called when entering a 'with' statement block. Returns the client instance.
        Example:
            with ADFClient(...) as client:
                client.trigger_pipeline("my-pipeline")
        """
        logger.debug("Entering ADFClient context")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Context manager exit.

        Automatically called when exiting a 'with' statement block.
        Ensures proper resource cleanup by calling close().
        """
        logger.debug("Exiting ADFClient context")
        self.close()

    def close(self) -> None:
        """
        Clean up resources and close Azure SDK client connections.

        Should be called when the client is no longer needed. Automatically called
        when using the client as a context manager (with statement).

        Note:
            It's safe to call this method multiple times.
        """
        if self.adf_client is not None:
            self.adf_client.close()
            logger.info("Closed ADFClient")

    def __repr__(self) -> str:
        """
        String representation of the client for debugging and logging.

        Returns a string showing key configuration details with subscription_id partially masked.

        Example:
            >>> client = ADFClient(...)
            >>> print(client)
            ADFClient(factory_name='my-factory', resource_group='my-rg', subscription_id='12345678...')
        """
        return (
            f"ADFClient(factory_name='{self.factory_name}', "
            f"resource_group='{self.resource_group_name}', "
            f"subscription_id='{self.subscription_id[:8]}...')"
        )
