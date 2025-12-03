"""
Configuration constants for Azure Data Factory REST API.
"""

# import os
# from dataclasses import dataclass

# API version for Azure Data Factory REST API
API_VERSION = "2018-06-01"

# Azure Management API scope
MANAGEMENT_SCOPE = "https://management.azure.com/.default"

# Base URL for Azure Management API
MANAGEMENT_BASE_URL = "https://management.azure.com"

# Default polling interval in seconds
DEFAULT_POLL_INTERVAL = 30

# Default timeout in seconds
DEFAULT_TIMEOUT = 3600

# @dataclass
# class AzureSettings:
#     subscription_id: str = os.environ["AZURE_SUBSCRIPTION_ID"]
#     resource_group: str = os.environ["AZURE_RESOURCE_GROUP"]
#     factory_name: str = os.environ["AZURE_DATA_FACTORY_NAME"]
#     api_version: str = "2018-06-01"

# settings = AzureSettings()
