"""
Advanced usage example for Azure Data Factory pipeline runner using SDK.

Run this script using UV (as a module to support relative imports):
    uv run python -m src.adf.examples.kusto_query_usage
"""
from pathlib import Path
from ..client import ADFClient
from ..config import config
from ..models import KustoQuery, KustoQueryPipelineParameters
from ..exceptions import PipelineTriggerError, PipelineTimeoutError
from ..utils import setup_logging

# Configure logging once at application startup
setup_logging(level=config.log_level, log_format=config.log_format)


def main():
    """
    Example: Triggering and monitoring an Azure Data Factory pipeline.
    
    This example demonstrates:
    1. Creating ADF client with global config
    2. Using the convenient run_pipeline() method
    3. Handling pipeline execution results
    4. Retrieving detailed activity run information
    5. Error handling best practices
    
    Requirements:
        Environment variables can be set to override defaults:
        - AZURE_SUBSCRIPTION_ID
        - AZURE_RESOURCE_GROUP
        - AZURE_FACTORY_NAME
        - ADF_PIPELINE_NAME
    """
    
    print(f"{'=' * 60}")
    print("Azure Data Factory Pipeline Runner - Simple Usage")
    print(f"{'=' * 60}\n")
    
    # Example 1: Basic usage without context manager
    # example_basic_usage()
    
    # Example 2: Using context manager (recommended)
    example_context_manager_usage()


def example_basic_usage():
    """Basic usage example demonstrating pipeline execution without context manager.
    
    This example shows manual client creation and cleanup.
    """
    
    try:
        # Step 1: Read KQL query from file
        query_file = Path(__file__).parent / "example_query.kql"
        # query_file = Path(__file__).parent / "example_query_failed.kql"
        # query_file = Path(__file__).parent / "example_query_easy.kql"
        
        if not query_file.exists():
            print(f"⚠️  Query file not found: {query_file}")
            print("   Skipping this example.\n")
            return
        
        with open(query_file, 'r', encoding='utf-8') as f:
            kusto_query: KustoQuery = f.read()
        pipeline_parameters: KustoQueryPipelineParameters = {config.pipeline_parameter_key: kusto_query}
        print(f"📄 Query loaded from {query_file.name} ({len(kusto_query)} characters)\n")
        
        # Step 2: Create client using global config
        print("🔐 Authenticating with Azure...")
        client = ADFClient(
            subscription_id=config.subscription_id,
            resource_group_name=config.resource_group_name,
            factory_name=config.factory_name
        )
        print(
            "✓ Authentication successful",
            "",
            "Configuration:",
            f"  Subscription:    {client.subscription_id}",
            f"  Resource Group:  {client.resource_group_name}",
            f"  Factory Name:    {client.factory_name}",
            f"  Pipeline Name:   {config.pipeline_name}",
            f"{'=' * 60}",
            "",
            sep='\n'
        )
        
        # Step 3: Run pipeline using convenient method (trigger + wait)
        print(f"🚀 Running pipeline: {config.pipeline_name}")
        print(f"   with parameter: {config.pipeline_parameter_key}\n")
        final_status = client.run_pipeline(
            pipeline_name=config.pipeline_name,
            parameters=pipeline_parameters,
            poll_interval=config.poll_interval,
            timeout=config.timeout,
            save_to_file=config.auto_save_results
        )
        
        # Step 4: Display pipeline results
        print(
            "",
            f"{'=' * 60}",
            "Pipeline Execution Result",
            f"{'=' * 60}",
            f"Status:        {final_status.get('status')}",
            f"Run ID:        {final_status.get('run_id')}",
            f"Pipeline:      {final_status.get('pipeline_name')}",
            f"Started:       {final_status.get('run_start')}",
            f"Ended:         {final_status.get('run_end')}",
            f"Duration (ms): {final_status.get('duration_in_ms')}",
            sep='\n'
        )
        
        # Step 5: Get activity runs
        start_time = final_status.get("run_start")
        end_time = final_status.get("run_end")
        
        if start_time and end_time:
            print(
                "",
                f"{'=' * 60}",
                "Activity Runs",
                f"{'=' * 60}",
                sep='\n'
            )
            
            activity_runs = client.get_activity_runs(
                run_id=final_status.get('run_id'),
                start_time=start_time,
                end_time=end_time,
                save_to_file=config.auto_save_results
            )
            
            for idx, activity in enumerate(activity_runs, 1):
                status_icon = "✓" if activity.get('status') == 'Succeeded' else "✗"
                print(
                    "",
                    f"{idx}. {status_icon} {activity.get('activity_name')}",
                    f"   Type:     {activity.get('activity_type')}",
                    f"   Status:   {activity.get('status')}",
                    f"   Duration: {activity.get('duration_in_ms')} ms",
                    sep='\n'
                )
                
                if activity.get('status') == 'Failed':
                    error = activity.get('error', {})
                    if isinstance(error, dict):
                        print(
                            f"   Error Code: {error.get('error_code', 'N/A')}",
                            f"   Error Msg:  {error.get('message', 'Unknown error')}",
                            sep='\n'
                        )
                    else:
                        print(f"   Error: {str(error)}")
        
        # Step 6: Display final result
        print(f"\n{'=' * 60}")
        if final_status.get("status") == "Succeeded":
            print("✓ Pipeline completed successfully!")
        else:
            print(f"✗ Pipeline finished with status: {final_status.get('status')}")
        print(f"{'=' * 60}\n")
        
        # Cleanup
        client.close()
            
    except PipelineTriggerError as e:
        print(f"\n❌ Failed to trigger pipeline: {e}")
        raise
    except PipelineTimeoutError as e:
        print(f"\n❌ Pipeline execution timed out: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        raise


def example_context_manager_usage():
    """Recommended usage example using context manager for automatic resource cleanup.
    
    This is the preferred approach as it ensures proper resource cleanup.
    """
    
    print("\n" + "=" * 60)
    print("Example 2: Using Context Manager")
    print("=" * 60 + "\n")
    
    try:
        # Step 1: Read KQL query from file
        query_file = Path(__file__).parent / "example_query.kql"
        # query_file = Path(__file__).parent / "example_query_failed.kql"
        # query_file = Path(__file__).parent / "example_query_easy.kql"
        
        if not query_file.exists():
            print(f"⚠️  Query file not found: {query_file}")
            print("   Skipping this example.\n")
            return
        
        with open(query_file, 'r', encoding='utf-8') as f:
            kusto_query: KustoQuery = f.read()
        pipeline_parameters: KustoQueryPipelineParameters = {config.pipeline_parameter_key: kusto_query}
        print(f"📄 Query loaded from {query_file.name} ({len(kusto_query)} characters)\n")
        
        # Step 2: Create client using context manager
        print("🔐 Authenticating with Azure...")
        with ADFClient(
            subscription_id=config.subscription_id,
            resource_group_name=config.resource_group_name,
            factory_name=config.factory_name
        ) as client:
            print(
                "✓ Authentication successful",
                "",
                "Configuration:",
                f"  Subscription:    {client.subscription_id}",
                f"  Resource Group:  {client.resource_group_name}",
                f"  Factory Name:    {client.factory_name}",
                f"  Pipeline Name:   {config.pipeline_name}",
                f"{'=' * 60}",
                "",
                sep='\n'
            )
            
            # Step 3: Run pipeline using convenient method (trigger + wait)
            print(f"🚀 Running pipeline: {config.pipeline_name}")
            print(f"   with parameter: {config.pipeline_parameter_key}\n")
            final_status = client.run_pipeline(
                pipeline_name=config.pipeline_name,
                parameters=pipeline_parameters,
                poll_interval=config.poll_interval,
                timeout=config.timeout,
                save_to_file=config.auto_save_results
            )
            
            # Step 4: Display pipeline results
            print(
                "",
                f"{'=' * 60}",
                "Pipeline Execution Result",
                f"{'=' * 60}",
                f"Status:        {final_status.get('status')}",
                f"Run ID:        {final_status.get('run_id')}",
                f"Pipeline:      {final_status.get('pipeline_name')}",
                f"Started:       {final_status.get('run_start')}",
                f"Ended:         {final_status.get('run_end')}",
                f"Duration (ms): {final_status.get('duration_in_ms')}",
                sep='\n'
            )
            
            # Step 5: Get activity runs
            start_time = final_status.get("run_start")
            end_time = final_status.get("run_end")
            
            if start_time and end_time:
                print(
                    "",
                    f"{'=' * 60}",
                    "Activity Runs",
                    f"{'=' * 60}",
                    sep='\n'
                )
                
                activity_runs = client.get_activity_runs(
                    run_id=final_status.get('run_id'),
                    start_time=start_time,
                    end_time=end_time,
                    save_to_file=config.auto_save_results
                )
                
                for idx, activity in enumerate(activity_runs, 1):
                    status_icon = "✓" if activity.get('status') == 'Succeeded' else "✗"
                    print(
                        "",
                        f"{idx}. {status_icon} {activity.get('activity_name')}",
                        f"   Type:     {activity.get('activity_type')}",
                        f"   Status:   {activity.get('status')}",
                        f"   Duration: {activity.get('duration_in_ms')} ms",
                        sep='\n'
                    )
                    
                    if activity.get('status') == 'Failed':
                        error = activity.get('error', {})
                        if isinstance(error, dict):
                            print(
                                f"   Error Code: {error.get('error_code', 'N/A')}",
                                f"   Error Msg:  {error.get('message', 'Unknown error')}",
                                sep='\n'
                            )
                        else:
                            print(f"   Error: {str(error)}")
            
            # Step 6: Display final result
            print(f"\n{'=' * 60}")
            if final_status.get("status") == "Succeeded":
                print("✓ Pipeline completed successfully!")
            else:
                print(f"✗ Pipeline finished with status: {final_status.get('status')}")
            print(f"{'=' * 60}\n")
        
        # Client is automatically closed when exiting the context
        print("✓ Client automatically closed\n")
        
    except PipelineTriggerError as e:
        print(f"\n❌ Failed to trigger pipeline: {e}")
        raise
    except PipelineTimeoutError as e:
        print(f"\n❌ Pipeline execution timed out: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
