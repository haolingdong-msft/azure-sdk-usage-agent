"""
Configuration settings and constants for the MCP SQL Server
"""
import os

# Server configuration
MCP_PORT = int(os.environ.get("FUNCTIONS_CUSTOMHANDLER_PORT", 8080))
MCP_PORT_KUSTO = int(os.environ.get("FUNCTIONS_CUSTOMHANDLER_PORT", 8082))

# SQL Server connection settings
SQL_SERVER = os.getenv('SQL_SERVER', 'azuresdkbi-server.database.windows.net')
SQL_DATABASE = os.getenv('SQL_DATABASE', 'azuresdkbi')
AZURE_SUBSCRIPTION_ID = os.getenv('AZURE_SUBSCRIPTION_ID', 'a18897a6-7e44-457d-9260-f2854c0aca42')
AZURE_RESOURCE_GROUP = os.getenv('AZURE_RESOURCE_GROUP', 'sdk-mgmt-bi-data')

# Azure authentication scopes (for legacy compatibility, MSI doesn't need explicit scopes)
MANAGEMENT_SCOPE = "https://management.azure.com/.default"
MANAGEMENT_URL = "https://management.azure.com"

# Schema file path
SCHEMA_FILE_PATH = 'reference/schemas/AMEAnalytics_Schema.json'
