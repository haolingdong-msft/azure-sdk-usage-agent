"""
Advanced usage example for Azure Data Factory pipeline runner using SDK.

Run this script using UV (as a module to support relative imports):
    uv run python -m src.adf.examples.kusto_query_usage
"""
from pathlib import Path
from ..client import ADFClient
from ..config import ADFConfig
from ..exceptions import PipelineTriggerError, PipelineTimeoutError


def main():
    """
    Example: Triggering and monitoring an Azure Data Factory pipeline without parameters.
    
    This example demonstrates:
    1. Different ways to create ADF SDK client (environment, config, context manager)
    2. Using the convenient run_pipeline() method
    3. Handling pipeline execution results
    4. Retrieving detailed activity run information
    5. Error handling best practices
    
    Requirements:
        Environment variables must be set:
        - AZURE_SUBSCRIPTION_ID
        - AZURE_RESOURCE_GROUP
        - AZURE_FACTORY_NAME
    """
    
    print(f"{'=' * 60}")
    print("Azure Data Factory Pipeline Runner - Simple Usage")
    print(f"{'=' * 60}\n")
    
    # Example 1: Using new() (recommended)
    example_basic()
    
    # Example 2: Using custom configuration
    # example_with_config()
    
    # Example 3: Using context manager
    # example_with_context_manager()
    
    # Example 4: Run custom pipeline without parameters
    # example_custom_pipeline_no_params()
    
    # Example 5: Run env pipeline with Kusto query parameters
    # example_env_pipeline_with_params()


def example_basic():
    """Basic example using new()."""
    
    # Pipeline name for this example with remote signal pipeline without parameters
    PIPELINE_NAME = "RegExp"
    
    try:
        # Step 1: Create client from environment variables
        print("🔐 Authenticating with Azure...")
        
        print("📝 Creating config with custom pipelineName...")
        config = ADFConfig(
            pipeline_name = PIPELINE_NAME
        )
         
        client = ADFClient.new(config=config)
        print("✓ Authentication successful\n")
        
        print(f"Configuration:")
        print(f"  Subscription:    {client.subscription_id}")
        print(f"  Resource Group:  {client.resource_group_name}")
        print(f"  Factory Name:    {client.factory_name}")
        print(f"  Pipeline Name:   {client.config.pipeline_name}")
        print(f"{'=' * 60}\n")
        
        # Step 2: Run pipeline using convenient method (trigger + wait)
        print(f"🚀 Running pipeline: {PIPELINE_NAME}")
        print("   (This will trigger the pipeline and wait for completion)\n")
        
        final_status = client.run_pipeline()
        
        # Step 3: Display pipeline results
        print(f"\n{'=' * 60}")
        print(f"Pipeline Execution Result")
        print(f"{'=' * 60}")
        print(f"Status:        {final_status.get('status')}")
        print(f"Run ID:        {final_status.get('run_id')}")
        print(f"Pipeline:      {final_status.get('pipeline_name')}")
        print(f"Started:       {final_status.get('run_start')}")
        print(f"Ended:         {final_status.get('run_end')}")
        print(f"Duration (ms): {final_status.get('duration_in_ms')}")
        
        # Step 4: Get activity runs
        start_time = final_status.get("run_start")
        end_time = final_status.get("run_end")
        
        if start_time and end_time:
            print(f"\n{'=' * 60}")
            print(f"Activity Runs")
            print(f"{'=' * 60}")
            
            activity_runs = client.get_activity_runs(
                run_id=final_status.get('run_id'),
                start_time=start_time,
                end_time=end_time
            )
            
            for idx, activity in enumerate(activity_runs, 1):
                status_icon = "✓" if activity.get('status') == 'Succeeded' else "✗"
                print(f"\n{idx}. {status_icon} {activity.get('activity_name')}")
                print(f"   Type:     {activity.get('activity_type')}")
                print(f"   Status:   {activity.get('status')}")
                print(f"   Duration: {activity.get('duration_in_ms')} ms")
                
                if activity.get('status') == 'Failed':
                    error = activity.get('error', {})
                    if isinstance(error, dict):
                        print(f"   Error Code: {error.get('error_code', 'N/A')}")
                        print(f"   Error Msg:  {error.get('message', 'Unknown error')}")
                    else:
                        print(f"   Error: {str(error)}")
        
        # Step 5: Display final result
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


def example_with_config():
    """Example using custom configuration with various creation methods."""
    
    print("\n" + "=" * 60)
    print("Example 2: Custom Configuration")
    print("=" * 60 + "\n")
    
    # Method 1: Create custom configuration directly
    print("📝 Method 1: Creating config with custom parameters...")
    config = ADFConfig(
        poll_interval=15,        # Poll every 15 seconds (faster than default 30s)
        timeout=7200,            # 2 hour timeout (longer than default 1h)
        log_level="DEBUG",       # More detailed logging
        auto_save_results=True,  # Auto-save activity runs to file
        output_dir="custom_output"  # Custom output directory
    )
    
    # Config is a dataclass with all attributes accessible
    print(f"✓ Config created:")
    print(f"  - Poll interval: {config.poll_interval}s")
    print(f"  - Timeout: {config.timeout}s ({config.timeout/3600}h)")
    print(f"  - Log level: {config.log_level}")
    print(f"  - Auto save: {config.auto_save_results}")
    print(f"  - Output dir: {config.output_dir}")
    print(f"  - Subscription: {config.subscription_id[:20]}...")
    print(f"  - Resource group: {config.resource_group_name}")
    print(f"  - Factory: {config.factory_name}\n")
    
    # Method 2: Create from environment variables (reads ADF_* env vars)
    print("📝 Method 2: Creating config from environment variables...")
    config_from_env = ADFConfig.from_env()
    print(f"✓ Config loaded from env vars\n")
    
    # Method 3: Create from dictionary
    print("📝 Method 3: Creating config from dictionary...")
    config_dict = {
        "poll_interval": 20,
        "timeout": 5000,
        "log_level": "INFO"
    }
    config_from_dict = ADFConfig.from_dict(config_dict)
    print(f"✓ Config created from dict: {config_dict}\n")
    
    # Convert config to dictionary
    print("📝 Converting config to dictionary...")
    dict_output = config.to_dict()
    print(f"✓ Config as dict has {len(dict_output)} keys\n")
    
    # Create client with custom config
    print("🔐 Creating ADF client with custom config...")
    client = ADFClient.new(config=config)
    print("✓ Client created successfully\n")
    
    # Run pipeline with custom settings
    print(f"🚀 Running pipeline with custom config...")
    result = client.run_pipeline(PIPELINE_NAME, wait=True)
    
    print(f"\n✓ Pipeline completed with status: {result.get('status')}")
    print(f"  Results saved to: {config.output_dir}" if config.auto_save_results else "  (Results not saved)")
    
    client.close()
    print(f"\n{'=' * 60}\n")


def example_with_context_manager():
    """Example using context manager for automatic resource cleanup."""
    
    with ADFClient.new() as client:
        # List available pipelines
        pipelines = client.list_pipelines()
        print(f"Available pipelines: {pipelines}")
        
        # Run pipeline
        result = client.run_pipeline(
            pipeline_name=PIPELINE_NAME,
            wait=True
        )
        
        print(f"Pipeline status: {result.get('status')}")
    
    # Client is automatically closed when exiting the context


def example_custom_pipeline_no_params():
    """Example: Run custom pipeline without parameters.
    
    This example shows how to run a specific pipeline (RegExp) without parameters.
    Only the pipeline_name needs to be specified in config.
    """
    
    print("\n" + "=" * 60)
    print("Example 4: Custom Pipeline Without Parameters")
    print("=" * 60 + "\n")
    
    try:
        # Create client from environment, only specify the custom pipeline name
        print("🔐 Creating client from environment...")
        client = ADFClient.new()
        print("✓ Authentication successful\n")
        
        # Custom pipeline name (different from env variable)
        custom_pipeline = "RegExp"
        
        print(f"Running custom pipeline: {custom_pipeline}")
        print(f"  (Environment pipeline: {client.config.pipeline_name})\n")
        
        # Run the custom pipeline
        print(f"🚀 Running pipeline: {custom_pipeline}")
        final_status = client.run_pipeline(
            pipeline_name=custom_pipeline,
            wait=True
        )
        
        # Display results
        print(f"\n{'=' * 60}")
        print(f"Pipeline Execution Result")
        print(f"{'=' * 60}")
        print(f"Status:        {final_status.get('status')}")
        print(f"Run ID:        {final_status.get('run_id')}")
        print(f"Pipeline:      {final_status.get('pipeline_name')}")
        print(f"Duration (ms): {final_status.get('duration_in_ms')}")
        
        # Get activity runs
        start_time = final_status.get("run_start")
        end_time = final_status.get("run_end")
        
        if start_time and end_time:
            activity_runs = client.get_activity_runs(
                run_id=final_status.get('run_id'),
                start_time=start_time,
                end_time=end_time
            )
            
            print(f"\n{'=' * 60}")
            print(f"Activity Runs: {len(activity_runs)} activities")
            print(f"{'=' * 60}")
            
            for idx, activity in enumerate(activity_runs, 1):
                status_icon = "✓" if activity.get('status') == 'Succeeded' else "✗"
                print(f"{idx}. {status_icon} {activity.get('activity_name')} - {activity.get('status')}")
        
        print(f"\n{'=' * 60}")
        if final_status.get("status") == "Succeeded":
            print("✓ Custom pipeline completed successfully!")
        else:
            print(f"✗ Pipeline finished with status: {final_status.get('status')}")
        print(f"{'=' * 60}\n")
        
        client.close()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        raise


def example_env_pipeline_with_params():
    """Example: Run environment pipeline with Kusto query parameters.
    
    This example shows how to run the pipeline from environment variables
    but with custom parameters (Kusto query from file).
    """
    
    print("\n" + "=" * 60)
    print("Example 5: Environment Pipeline With Kusto Query Parameters")
    print("=" * 60 + "\n")
    
    try:
        # Step 1: Read KQL query from file
        query_file = Path(__file__).parent / "example_query.kql"
        # query_file = Path(__file__).parent / "example_query_failed.kql"
        # query_file = Path(__file__).parent / "example_NoParam.kql"
        
        print(f"📄 Reading KQL query from: {query_file.name}")
        
        if not query_file.exists():
            print(f"⚠️  Query file not found: {query_file}")
            print("   Skipping this example.\n")
            return
        
        with open(query_file, 'r', encoding='utf-8') as f:
            kusto_query = f.read()
        
        print(f"✓ Query loaded ({len(kusto_query)} characters)\n")
        
        # Step 2: Create client with auto_save_results enabled
        # Only specify the parameters you want to change, others use defaults
        print("🔐 Creating client with auto-save enabled...")
        config = ADFConfig(auto_save_results=True)
        client = ADFClient.new(config=config)
        print("✓ Authentication successful\n")
        
        print(f"Configuration:")
        print(f"  Pipeline:      {client.config.pipeline_name}")
        print(f"  Parameter Key: {client.config.pipeline_parameter_key}")
        print(f"{'=' * 60}\n")
        
        # Step 3: Prepare pipeline parameters
        pipeline_parameters = {
            client.config.pipeline_parameter_key: kusto_query
        }
        
        # Step 4: Trigger pipeline with parameters
        print(f"🚀 Triggering pipeline: {client.config.pipeline_name}")
        print(f"   with parameter: {client.config.pipeline_parameter_key}\n")
        
        run_id = client.trigger_pipeline(
            pipeline_name=client.config.pipeline_name,
            parameters=pipeline_parameters
        )
        print(f"✓ Pipeline triggered successfully")
        print(f"  Run ID: {run_id}\n")
        
        # Step 5: Wait for completion
        print("⏳ Waiting for pipeline to complete...\n")
        
        final_status = client.wait_for_pipeline(
            run_id=run_id,
            poll_interval=30,
            timeout=3600
        )
        
        # Step 6: Display results
        print(f"\n{'=' * 60}")
        print(f"Pipeline Execution Result")
        print(f"{'=' * 60}")
        print(f"Status:        {final_status.get('status')}")
        print(f"Run ID:        {final_status.get('run_id')}")
        print(f"Pipeline:      {final_status.get('pipeline_name')}")
        print(f"Started:       {final_status.get('run_start')}")
        print(f"Ended:         {final_status.get('run_end')}")
        print(f"Duration (ms): {final_status.get('duration_in_ms')}")
        
        # Step 7: Get activity runs
        start_time = final_status.get("run_start")
        end_time = final_status.get("run_end")
        
        if start_time and end_time:
            activity_runs = client.get_activity_runs(
                run_id=run_id,
                start_time=start_time,
                end_time=end_time
            )
            
            print(f"\n{'=' * 60}")
            print(f"Activity Runs: {len(activity_runs)} activities")
            print(f"{'=' * 60}")
            
            for idx, activity in enumerate(activity_runs, 1):
                status_icon = "✓" if activity.get('status') == 'Succeeded' else "✗"
                print(f"\n{idx}. {status_icon} {activity.get('activity_name')}")
                print(f"   Type:     {activity.get('activity_type')}")
                print(f"   Status:   {activity.get('status')}")
                print(f"   Duration: {activity.get('duration_in_ms')} ms")
                
                if activity.get('status') == 'Failed':
                    error = activity.get('error', {})
                    if isinstance(error, dict):
                        print(f"   Error Code: {error.get('error_code', 'N/A')}")
                        print(f"   Error Msg:  {error.get('message', 'Unknown error')}")
        
        # Step 8: Display final result
        print(f"\n{'=' * 60}")
        if final_status.get("status") == "Succeeded":
            print("✓ Pipeline with parameters completed successfully!")
        else:
            print(f"✗ Pipeline finished with status: {final_status.get('status')}")
        print(f"{'=' * 60}\n")
        
        client.close()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
