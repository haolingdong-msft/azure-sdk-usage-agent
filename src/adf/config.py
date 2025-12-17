"""
Configuration for Azure Data Factory SDK.
Independent configuration without external dependencies.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from .exceptions import ConfigurationError


# ==================== Constants ====================

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
DEFAULT_AUTO_SAVE_RESULTS = False
DEFAULT_OUTPUT_DIR = Path("output")

# Default pipeline configuration
DEFAULT_PIPELINE_NAME = "QueryARMProd-Parm"
DEFAULT_PIPELINE_PARAMETER_KEY = "KustoQuery"


# ==================== Configuration Class ====================

@dataclass
class ADFConfig:
    """
    Configuration for ADF SDK.
    
    Attributes:
        subscription_id: Azure subscription ID
        resource_group_name: Resource group name
        factory_name: Data Factory name
        poll_interval: Seconds between status checks (default: 30)
        timeout: Maximum seconds to wait for pipeline completion (default: 3600)
        log_level: Logging level (default: INFO)
        log_format: Log format - "text" or "json" (default: text)
        auto_save_results: Whether to automatically save results to files (default: False)
        output_dir: Directory for output files (default: output/)
        pipeline_name: Default pipeline name with parameters (default: QueryARMProd-Parm)
        pipeline_parameter_key: ADF pipeline parameter key for Kusto query (default: KustoQuery)
    """
    
    # Required ADF connection parameters
    subscription_id: str = field(
        default_factory=lambda: os.getenv(
            "AZURE_SUBSCRIPTION_ID", 
            DEFAULT_SUBSCRIPTION_ID
        )
    )
    resource_group_name: str = field(
        default_factory=lambda: os.getenv(
            "AZURE_RESOURCE_GROUP", 
            DEFAULT_RESOURCE_GROUP
        )
    )
    factory_name: str = field(
        default_factory=lambda: os.getenv(
            "AZURE_FACTORY_NAME", 
            DEFAULT_FACTORY_NAME
        )
    )
    
    # Pipeline execution parameters
    poll_interval: int = field(default=DEFAULT_POLL_INTERVAL)
    timeout: int = field(default=DEFAULT_TIMEOUT)
    
    # Logging configuration
    log_level: str = field(default=DEFAULT_LOG_LEVEL)
    log_format: str = field(default=DEFAULT_LOG_FORMAT)  # "text" or "json"
    
    # Output configuration
    auto_save_results: bool = field(default=DEFAULT_AUTO_SAVE_RESULTS)
    output_dir: Path = field(default=DEFAULT_OUTPUT_DIR)
    
    # Pipeline configuration
    pipeline_name: str = field(
        default_factory=lambda: os.getenv("ADF_PIPELINE_NAME", DEFAULT_PIPELINE_NAME)
    )
    pipeline_parameter_key: str = field(
        default_factory=lambda: os.getenv("ADF_QUERY_PARAM_KEY", DEFAULT_PIPELINE_PARAMETER_KEY)
    )
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate()
        
        # Convert output_dir to Path if string
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)
        
        # Create output directory if auto_save is enabled
        if self.auto_save_results:
            self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def validate(self) -> None:
        """
        Validate required configuration fields.
        
        Raises:
            ConfigurationError: If required fields are missing or invalid
        """
        missing_fields = []
        
        # Allow default values, only fail if explicitly set to empty
        if self.subscription_id is None or (self.subscription_id == "" and not os.getenv("AZURE_SUBSCRIPTION_ID")):
            missing_fields.append("subscription_id")
        if self.resource_group_name is None or (self.resource_group_name == "" and not os.getenv("AZURE_RESOURCE_GROUP")):
            missing_fields.append("resource_group_name")
        if self.factory_name is None or (self.factory_name == "" and not os.getenv("AZURE_FACTORY_NAME")):
            missing_fields.append("factory_name")
        
        if missing_fields:
            raise ConfigurationError(
                f"Missing required configuration fields: {', '.join(missing_fields)}. "
                f"Set them via constructor or environment variables "
                f"(AZURE_SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP, AZURE_FACTORY_NAME).",
                missing_fields=missing_fields
            )
        
        # Validate poll_interval and timeout
        if self.poll_interval <= 0:
            raise ConfigurationError(f"poll_interval must be positive, got: {self.poll_interval}")
        
        if self.timeout <= 0:
            raise ConfigurationError(f"timeout must be positive, got: {self.timeout}")
        
        if self.timeout < self.poll_interval:
            raise ConfigurationError(
                f"timeout ({self.timeout}) must be greater than poll_interval ({self.poll_interval})"
            )
        
        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_log_levels:
            raise ConfigurationError(
                f"Invalid log_level: {self.log_level}. Must be one of: {', '.join(valid_log_levels)}"
            )
        
        # Validate log format
        if self.log_format not in ["text", "json"]:
            raise ConfigurationError(
                f"Invalid log_format: {self.log_format}. Must be 'text' or 'json'"
            )
    
    @classmethod
    def from_env(cls) -> "ADFConfig":
        """
        Create configuration from environment variables.
        
        Environment variables:
            - AZURE_SUBSCRIPTION_ID: Azure subscription ID
            - AZURE_RESOURCE_GROUP: Resource group name
            - AZURE_FACTORY_NAME: Data Factory name
            - ADF_PIPELINE_NAME: Default pipeline name (optional)
            - ADF_QUERY_PARAM_KEY: Pipeline parameter key for Kusto query (optional)
            - ADF_POLL_INTERVAL: Poll interval in seconds (optional)
            - ADF_TIMEOUT: Timeout in seconds (optional)
            - ADF_LOG_LEVEL: Log level (optional)
            - ADF_LOG_FORMAT: Log format (optional)
            - ADF_AUTO_SAVE: Auto save results (optional)
            - ADF_OUTPUT_DIR: Output directory (optional)
        
        Returns:
            ADFConfig instance
            
        Raises:
            ConfigurationError: If required environment variables are missing
        """
        config = cls(
            poll_interval=int(os.getenv("ADF_POLL_INTERVAL", DEFAULT_POLL_INTERVAL)),
            timeout=int(os.getenv("ADF_TIMEOUT", DEFAULT_TIMEOUT)),
            log_level=os.getenv("ADF_LOG_LEVEL", DEFAULT_LOG_LEVEL),
            log_format=os.getenv("ADF_LOG_FORMAT", DEFAULT_LOG_FORMAT),
            auto_save_results=os.getenv("ADF_AUTO_SAVE", "false").lower() == "true",
            output_dir=Path(os.getenv("ADF_OUTPUT_DIR", str(DEFAULT_OUTPUT_DIR))),
            pipeline_name=os.getenv("ADF_PIPELINE_NAME", DEFAULT_PIPELINE_NAME),
            pipeline_parameter_key=os.getenv("ADF_QUERY_PARAM_KEY", DEFAULT_PIPELINE_PARAMETER_KEY),
        )
        return config
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> "ADFConfig":
        """
        Create configuration from dictionary.
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            ADFConfig instance
        """
        return cls(**config_dict)
    
    def to_dict(self) -> dict:
        """
        Convert configuration to dictionary.
        
        Returns:
            Configuration dictionary
        """
        return {
            "subscription_id": self.subscription_id,
            "resource_group_name": self.resource_group_name,
            "factory_name": self.factory_name,
            "poll_interval": self.poll_interval,
            "timeout": self.timeout,
            "log_level": self.log_level,
            "log_format": self.log_format,
            "auto_save_results": self.auto_save_results,
            "output_dir": str(self.output_dir),
            "pipeline_name": self.pipeline_name,
            "pipeline_parameter_key": self.pipeline_parameter_key,
        }
