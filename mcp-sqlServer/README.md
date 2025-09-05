# Azure SQL MCP Server

A Model Context Protocol (MCP) server that transforms natural language questions into SQL queries for Azure SQL Server databases.

## Features

- **Natural Language to SQL**: Convert plain English questions to SQL queries
- **Two Server Modes**: Standard parsing mode and AI-enhanced schema analysis mode
- **Azure Authentication**: Secure MSI (Managed Service Identity) authentication
- **Two-Step Processing**: Parse questions first, then execute with validation

## Quick Start

### Prerequisites
- Python 3.10+
- Azure SQL Database access
- Azure CLI
- ODBC Driver 18 for SQL Server

### Installation
```bash
pip install -r requirements.txt
az login
```

### Configuration
Create `local.settings.json`:
```json
{
    "IsEncrypted": false,
    "Values": {
        "FUNCTIONS_WORKER_RUNTIME": "custom",
        "FUNCTIONS_CUSTOMHANDLER_PORT": "8080",
        "SQL_SERVER": "your-server.database.windows.net",
        "SQL_DATABASE": "your-database",
        "AZURE_SUBSCRIPTION_ID": "your-subscription-id",
        "AZURE_RESOURCE_GROUP": "your-resource-group"
    }
}
```

### Start Server
```bash
# Standard mode
func start
# or
python -m src.main

# AI mode
python -m src.main_with_ai
```
## Usage Examples

### Standard Mode
```python
# Parse question
result = await parseUserQuery("Show me top 10 Python SDK users")

# Execute query
data = await executeSQLQuery(
    table_name=result["table_name"],
    columns=result["columns"],
    where_clause=result["where_clause"]
)
```

### AI Mode
```python
# Get schema suggestions
suggestions = await aiQueryHelper("Show Python SDK usage")

# Execute with suggestions
data = await executeSQLQuery(
    table_name=suggestions["suggested_table"],
    columns=suggestions["example_columns"]
)
```

## Troubleshooting

- **Authentication Issues**: Ensure managed identity is enabled and database user exists
- **Connection Issues**: Check firewall rules and ODBC driver installation
- **Permission Issues**: Verify database roles and RBAC settings

## License

MIT License - see [LICENSE.md](LICENSE.md)
