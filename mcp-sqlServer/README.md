# Azure SQL MCP Server - Intelligent Natural Language Database Querying

A sophisticated Model Context Protocol (MCP) server that provides intelligent SQL querying capabilities for Azure SQL Server data. Transform natural language questions into SQL queries, making database interactions accessible without SQL expertise.

## 🔄 Work Flow 

**Validation-First Approach:**
```
User Question → 🔍 Validate & Generate SQL → ✅ Pass → 🔗 Connect to Database → Execute Query → Return Results
                                        ↘ ❌ Fail → Immediately Return Error & Suggestions
```

## ✨ Core Features

### 🤖 Natural Language Querying
- **Plain English Questions**: "Show me the top 10 customers by request count"
- **Automatic Detection**: Smart table and column identification
- **Query Validation**: Pre-validation ensures correctness before execution
- **Intelligent Filtering**: Context-aware filtering and sorting

### 🛠️ Multiple Query Methods
- **`mssqlQuery()`** - Natural language queries with validation
- **`listTablesMSSQL()`** - Explore available data structures
- **`validateQueryMSSQL()`** - Validate queries before execution
- **`executeCustomSQLMSSQL()`** - Advanced custom SQL with safety checks
- **`validateAzureAuthMSSQL()`** - Check Azure authentication status

### 🔐 Security & Performance
- **ODBC-Free**: REST API architecture with Azure AD authentication
- **SQL Injection Protection**: Only SELECT operations allowed
- **Validation-First**: Fast failure for invalid queries
- **Connection Optimization**: Smart connection strategies and caching

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Azure subscription with SQL Database access
- Azure CLI (for development)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd mcp-sqlServer

# Install dependencies
pip install -r requirements.txt

# Configure Azure authentication
az login

### Start the Server
```bash
# Local development
func start

# Or direct Python execution
python mssql_query_server.py
```

## 📝 Simple Examples

### Natural Language Queries
```python
# Basic usage analysis
await mssqlQuery("Show me Python-SDK usage this month")
await mssqlQuery("Top 10 products by request count")

# Comparative analysis  
await mssqlQuery("Python-SDK vs Java-SDK usage comparison")
await mssqlQuery("Windows users of Python-SDK")

# Time-based queries
await mssqlQuery("Request trends for 2024")
await mssqlQuery("This month vs last month Azure SDK usage")
```

### Discovery and Validation
```python
# Explore available data
await listTablesMSSQL()

# Validate authentication
await validateAzureAuthMSSQL()

# Validate query before execution
await validateQueryMSSQL("Show me top 10 products")

# Advanced custom SQL
await executeCustomSQLMSSQL("SELECT TOP 5 Product, RequestCount FROM AMEConciseSubReqCCIDCountByMonthProduct ORDER BY RequestCount DESC")
```

## 🎯 Getting Started

Ready to start? Follow these steps:

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Authenticate with Azure**: `az login`
3. **Set environment variables** for your SQL server
4. **Start the server**: `func start`
5. **Ask your first question**: "Show me the top 10 Azure SDK products by usage"

Experience faster, more reliable data analysis with our validation-first query flow! 🚀

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see [LICENSE.md](LICENSE.md) for details.
