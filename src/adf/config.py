"""
Configuration for Azure Data Factory SDK.
"""

import os
from pathlib import Path


# ==================== Default Configuration ====================

# Default Azure configuration
DEFAULT_SUBSCRIPTION_ID = "a18897a6-7e44-457d-9260-f2854c0aca42"
DEFAULT_RESOURCE_GROUP = "sdk-mgmt-bi-data"
DEFAULT_FACTORY_NAME = "azuremgmtsdkbi-datafactory"

# Default polling interval in seconds
DEFAULT_POLL_INTERVAL = 30

# Default timeout in seconds
DEFAULT_TIMEOUT = 3600

# Default logging configuration
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FORMAT = "text"

# Default output configuration
# DEFAULT_AUTO_SAVE_RESULTS = False
DEFAULT_AUTO_SAVE_RESULTS = True
DEFAULT_OUTPUT_DIR = Path("output")

# Default pipeline configuration
DEFAULT_PIPELINE_NAME = "QueryARMProd-Parm"
# DEFAULT_PIPELINE_NAME = "RegExp"
DEFAULT_PIPELINE_PARAMETER_KEY = "KustoQuery"


# ==================== Configuration ====================

class Config:
    """Global configuration for ADF SDK."""
    
    def __init__(self):
        # Azure connection parameters
        self.subscription_id = os.getenv(
            "AZURE_SUBSCRIPTION_ID", 
            DEFAULT_SUBSCRIPTION_ID
        )
        self.resource_group_name = os.getenv(
            "AZURE_RESOURCE_GROUP", 
            DEFAULT_RESOURCE_GROUP
        )
        self.factory_name = os.getenv(
            "AZURE_FACTORY_NAME", 
            DEFAULT_FACTORY_NAME
        )
        
        # Pipeline configuration
        self.pipeline_name = os.getenv(
            "ADF_PIPELINE_NAME", 
            DEFAULT_PIPELINE_NAME
        )
        self.pipeline_parameter_key = os.getenv(
            "ADF_QUERY_PARAM_KEY", 
            DEFAULT_PIPELINE_PARAMETER_KEY
        )
        
        # Runtime parameters
        self.poll_interval = int(os.getenv("ADF_POLL_INTERVAL", str(DEFAULT_POLL_INTERVAL)))
        self.timeout = int(os.getenv("ADF_TIMEOUT", str(DEFAULT_TIMEOUT)))
        
        # Logging configuration
        self.log_level = os.getenv("ADF_LOG_LEVEL", DEFAULT_LOG_LEVEL)
        self.log_format = os.getenv("ADF_LOG_FORMAT", DEFAULT_LOG_FORMAT)
        
        # Output configuration
        self.auto_save_results = os.getenv("ADF_AUTO_SAVE", str(DEFAULT_AUTO_SAVE_RESULTS).lower()).lower() == "true"
        self.output_dir = Path(os.getenv("ADF_OUTPUT_DIR", str(DEFAULT_OUTPUT_DIR)))
        
        # Create output directory if auto_save is enabled
        if self.auto_save_results:
            self.output_dir.mkdir(parents=True, exist_ok=True)


# ==================== Global Instance ====================

# Global config instance - reads from environment variables or uses defaults
config = Config()
