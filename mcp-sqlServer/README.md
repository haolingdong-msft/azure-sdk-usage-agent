# Azure SQL MCP Server - Intelligent Natural Language Database Querying

A sophisticated Model Context Protocol (MCP) server that provides intelligent SQL querying capabilities for Azure SQL Server data. Transform natural language questions into SQL queries, making database interactions accessible without SQL expertise.

## 🔄 Work Flow 

**Two-Step Query Processing:**
```
User Question → 🔍 parseUserQuery → Extract Table/Columns/Conditions → � executeSQLQuery → Validate Auth → Execute → Return Results
                ↘ ❌ Parse Error → Return Error & Suggestions                    ↘ ❌ Auth Fail → Return Auth Error
```

## ✨ Core Features

### 🤖 Natural Language Querying
- **Plain English Questions**: "Show me the top 10 customers by request count"
- **Automatic Detection**: Smart table and column identification
- **Two-Step Processing**: Parse first, then execute with authentication
- **Intelligent Filtering**: Context-aware filtering and sorting

## 🏗️ Architecture

### Two-Step Query Design
Our MCP server uses a clean two-step approach:

1. **Parse Step** (`parseUserQuery`):
   - Analyzes natural language input
   - Identifies relevant tables and columns
   - Generates WHERE, ORDER BY, and LIMIT clauses
   - Returns structured query components
   - No database connection required

2. **Execute Step** (`executeSQLQuery`):
   - Validates Azure AD authentication first
   - Constructs SQL from parsed components
   - Executes query via REST API
   - Returns formatted results
   - Handles authentication errors gracefully

This separation provides better error handling, security, and flexibility for different use cases.

### 🛠️ MCP Tools
- **`parseUserQuery()`** - Parse natural language into table names, columns, and conditions
- **`executeSQLQuery()`** - Execute SQL using parsed components with Azure AD authentication

### 🔐 Security & Performance
- **ODBC-Free**: REST API architecture with Azure AD authentication
- **Built-in Auth Validation**: Authentication checked before every query execution
- **SQL Injection Protection**: Only SELECT operations allowed
- **Two-Step Processing**: Parse first, then execute with validation
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

## 📝 Usage Examples

### Two-Step Query Process
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
```

## 🎯 Getting Started

Ready to start? Follow these steps:

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Authenticate with Azure**: `az login`
3. **Set environment variables** for your SQL server
4. **Start the server**: `func start`
5. **Parse your first question**: `await parseUserQuery("Show me the top 10 Azure SDK products by usage")`
6. **Execute the query**: Use the parsed results with `executeSQLQuery()`

Experience faster, more reliable data analysis with our two-step query processing! 🚀

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see [LICENSE.md](LICENSE.md) for details.
