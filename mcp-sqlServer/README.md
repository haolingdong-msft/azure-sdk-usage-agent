# Azure SQL MCP Server - Intelligent Natural Language Database Querying

A sophisticated Model Context Protocol (MCP) server that provides intelligent SQL querying capabilities for Azure SQL Server data. Transform natural language questions into SQL queries, making database interactions accessible without SQL expertise.

## 🔄 Work Flow 

**Two-Step Query Processing:**
```
User Question → 🔍 parseUserQuery → Extract Table/Columns/Conditions → 🛡️ executeSQLQuery → Validate Auth → Execute → Return Results
                ↘ ❌ Parse Error → Return Error & Suggestions                    ↘ ❌ Auth Fail → Return Auth Error
```

**AI-Enhanced Query Processing (main_with_ai.py):**
```
User Question → 🤖 aiQueryHelper → Schema Analysis & Suggestions → 🛡️ executeSQLQuery → MSI Auth → Execute → Return Results
                ↘ Schema-aware suggestions                        ↘ ❌ Auth Fail → Return Auth Error
```

## ✨ Core Features

### 🤖 Natural Language Querying
- **Plain English Questions**: "Show me the top 10 customers by request count"
- **Automatic Detection**: Smart table and column identification
- **Two-Step Processing**: Parse first, then execute with authentication
- **AI-Enhanced Schema Analysis**: `aiQueryHelper` provides intelligent schema-aware suggestions
- **Intelligent Filtering**: Context-aware filtering and sorting

### � Dual Server Modes
- **Standard Mode** (`main.py`): Full two-step processing with `parseUserQuery` + `executeSQLQuery`
- **AI Mode** (`main_with_ai.py`): Schema-aware processing with `aiQueryHelper` + `executeSQLQuery`

## 🏗️ Architecture

### Server Configurations

#### Standard Mode (main.py)
Complete two-step query processing:

1. **Parse Step** (`parseUserQuery`):
   - Analyzes natural language input
   - Identifies relevant tables and columns
   - Generates WHERE, ORDER BY, and LIMIT clauses
   - Returns structured query components
   - No database connection required

2. **Execute Step** (`executeSQLQuery`):
   - Validates Azure AD authentication first
   - Constructs SQL from parsed components
   - Executes query with MSI authentication
   - Returns formatted results
   - Handles authentication errors gracefully

#### AI Mode (main_with_ai.py)
Schema-aware intelligent processing:

1. **AI Analysis Step** (`aiQueryHelper`):
   - Analyzes user question against database schema
   - Provides table and column suggestions
   - Returns example conditions and metadata
   - Schema-aware intelligent recommendations

2. **Execute Step** (`executeSQLQuery`):
   - Same robust execution as standard mode
   - MSI authentication validation
   - Structured error handling

### 🛠️ MCP Tools

#### Standard Mode Tools
- **`parseUserQuery()`** - Parse natural language into table names, columns, and conditions
- **`executeSQLQuery()`** - Execute SQL using parsed components with Azure AD authentication

#### AI Mode Tools
- **`aiQueryHelper()`** - AI-powered schema analysis and query suggestions
- **`executeSQLQuery()`** - Execute SQL using parsed components with Azure AD authentication

### 🔐 Security & Authentication Evolution

#### Current: MSI Authentication (Recommended)
- **Passwordless Authentication**: Managed Service Identity integration
- **Built-in Auth Validation**: Authentication checked before every query execution
- **Azure Native**: Follows Microsoft's recommended patterns
- **Token Auto-Renewal**: Azure handles token lifecycle automatically
- **RBAC Integration**: Works with Azure Role-Based Access Control

#### Legacy: ODBC with Access Tokens (Deprecated)
- **pyodbc Integration**: Direct ODBC database connections
- **Access Token Auth**: Manual token management
- **Performance**: Direct database connections for better performance

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Azure subscription with SQL Database access
- Azure CLI (for development)
- ODBC Driver 18 for SQL Server (for MSI authentication)
- Managed Identity enabled on Azure resource

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd mcp-sqlServer

# Install dependencies
pip install -r requirements.txt

# Configure Azure authentication
az login
```

### Database Setup for MSI Authentication
```sql
-- Create user for managed identity
CREATE USER [<managed-identity-name>] FROM EXTERNAL PROVIDER;
ALTER ROLE db_datareader ADD MEMBER [<managed-identity-name>];
ALTER ROLE db_datawriter ADD MEMBER [<managed-identity-name>];
```

### Environment Variables
Add local.settings.json in root 
```json
{
    "IsEncrypted": false,
    "Values": {
        "FUNCTIONS_WORKER_RUNTIME": "custom",
        "FUNCTIONS_CUSTOMHANDLER_PORT": "8080",
        "SQL_SERVER": "******",
        "SQL_DATABASE": "****",
        "AZURE_SUBSCRIPTION_ID": "****",
        "AZURE_RESOURCE_GROUP": "***"
    }
}
```

### Start the Server

#### Standard Mode (Two-Step Processing)
```bash
# Azure Functions runtime
func start

# Or direct Python execution
python -m src.main
```

#### AI Mode (Schema-Aware Processing)  
```bash
# Direct Python execution with AI helper
python -m src.main_with_ai
```

#### Legacy ODBC Mode
```bash
# For environments still using ODBC with access tokens
python mssql_query_server.py
```

## 📝 Usage Examples

### Standard Mode: Two-Step Query Process
```python
# Step 1: Parse user question
parse_result = await parseUserQuery("Show me Python-SDK usage this month")
# Returns: {
#   "success": True,
#   "table_name": "AMEConciseSubReqCCIDCountByMonthProduct", 
#   "columns": ["Product", "RequestCount", "YearMonth"],
#   "where_clause": "Product LIKE '%Python-SDK%' AND YearMonth LIKE '2024-%'",
#   "order_clause": "ORDER BY RequestCount DESC"
# }

# Step 2: Execute with parsed components
result = await executeSQLQuery(
    table_name=parse_result["table_name"],
    columns=parse_result["columns"], 
    where_clause=parse_result["where_clause"],
    order_clause=parse_result["order_clause"]
)
```

### AI Mode: Schema-Aware Query Process
```python
# Step 1: Get AI-powered schema analysis
helper_result = await aiQueryHelper("Show me Python-SDK usage this month")
# Returns: {
#   "available_tables": [...],
#   "suggested_table": "AMEConciseSubReqCCIDCountByMonthProduct",
#   "available_columns": ["Product", "RequestCount", "YearMonth", ...],
#   "column_metadata": {...},
#   "enum_values": {...},
#   "example_conditions": [...],
#   "example_columns": [...]
# }

# Step 2: Execute with AI suggestions
result = await executeSQLQuery(
    table_name=helper_result["suggested_table"],
    columns=helper_result["example_columns"],
    where_clause="Product LIKE '%Python-SDK%' AND YearMonth LIKE '2024-%'",
    order_clause="ORDER BY RequestCount DESC"
)
```

### MSI Authentication Examples
```python
# Basic query execution with MSI
client = MSSQLMSIClient()
result = await client.execute_query("SELECT * FROM users")
if result['status'] == 'success':
    print(f"Found {result['row_count']} rows")

# Connection testing
client = MSSQLMSIClient()
test_result = client.test_connection()
print(f"Connection status: {test_result['status']}")
```

### Common Query Patterns
```python
# Basic usage analysis
await parseUserQuery("Show me Python-SDK usage this month")
await parseUserQuery("Top 10 products by request count")

# Comparative analysis  
await parseUserQuery("Python-SDK vs Java-SDK usage comparison")
await parseUserQuery("Windows users of Python-SDK")

# Time-based queries
await parseUserQuery("Request trends for 2024")
await parseUserQuery("This month vs last month Azure SDK usage")

# AI-enhanced queries
await aiQueryHelper("What are the available columns for analyzing SDK usage?")
await aiQueryHelper("Show me schema information for product analysis")
```

## 🎯 Getting Started

Ready to start? Choose your deployment mode:

### Standard Mode Setup
1. **Install dependencies**: `pip install -r requirements.txt`
2. **Configure managed identity** on your Azure resource
3. **Set environment variables** for your SQL server
4. **Create database user** for managed identity
5. **Start server**: `func start` or `python -m src.main`
6. **Parse your first question**: `await parseUserQuery("Show me the top 10 Azure SDK products by usage")`
7. **Execute the query**: Use parsed results with `executeSQLQuery()`

### AI Mode Setup  
1. **Follow standard mode steps 1-4**
2. **Start AI server**: `python -m src.main_with_ai`
3. **Get schema analysis**: `await aiQueryHelper("What columns are available for product analysis?")`
4. **Execute with suggestions**: Use AI recommendations with `executeSQLQuery()`

### Development & Testing
```bash
# Test MSI connection
python -m src.sql_client

# Run test suite
pytest tests/

# Test specific functionality
python tests/test_connection_pytest.py
```

Experience faster, more reliable data analysis with our dual-mode processing architecture! 🚀

## 🔧 Troubleshooting

### MSI Authentication Issues
1. **Verify managed identity**: Ensure MSI is enabled on Azure resource
2. **Check database permissions**: Confirm user exists and has proper roles
3. **Validate ODBC driver**: Ensure ODBC Driver 18 is installed
4. **Network connectivity**: Verify firewall rules allow SQL access

### Connection Diagnostics
```python
# Test MSI connection
from src.sql_client import MSSQLMSIClient
client = MSSQLMSIClient()
result = client.test_connection()
print(f"Status: {result['status']}")
```

### Legacy Migration Support
For environments still using legacy authentication methods, refer to the migration history section for step-by-step upgrade guidance.

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see [LICENSE.md](LICENSE.md) for details.
