"""
Configuration settings and constants for the MCP SQL Server
"""
import os

# Server configuration
MCP_PORT = int(os.environ.get("FUNCTIONS_CUSTOMHANDLER_PORT", 8080))

# SQL Server connection settings
SQL_SERVER = os.getenv('SQL_SERVER', 'azuresdkbi-server.database.windows.net')
SQL_DATABASE = os.getenv('SQL_DATABASE', 'azuresdkbi')
AZURE_SUBSCRIPTION_ID = os.getenv('AZURE_SUBSCRIPTION_ID', 'a18897a6-7e44-457d-9260-f2854c0aca42')
AZURE_RESOURCE_GROUP = os.getenv('AZURE_RESOURCE_GROUP', 'sdk-mgmt-bi-data')

# Azure authentication scopes
SQL_SCOPE = "https://database.windows.net/.default"
MANAGEMENT_SCOPE = "https://management.azure.com/.default"
MANAGEMENT_URL = "https://management.azure.com"

# Schema file path
SCHEMA_FILE_PATH = 'fixture/tables_and_columns.json'
