# Azure SQL MCP Server - Intelligent Natural Language Database Querying

This repository contains a sophisticated Model Context Protocol (MCP) server that provides intelligent SQL querying capabilities for Azure SQL Server data. The server accepts natural language questions and converts them into appropriate SQL queries, making database interactions accessible to users without SQL expertise.

### 🔄 Work Flow 

**Validation-First Flow:**
```
User Question → 🔍 Validate & Generate SQL → ✅ Pass → 🔗 Connect to Database → Execute Query → Return Results
                                        ↘ ❌ Fail → Immediately Return Error & Suggestions
```

## 🤖 Natural Language Querying

### Intelligent Query Processing
- Ask questions in plain English: "Show me the top 10 customers by request count"
- Automatic table and column detection based on question context
- Smart filtering and sorting based on query intent
- Pre-validation mechanism ensures query correctness

### 📊 Multiple Query Methods
- **Natural Language**: `mssqlQuery()` - For everyday users (with validation)
- **Query Validation**: `validateQueryMSSQL()` - Validate before execution
- **Table Discovery**: `listTablesMSSQL()` - Explore available data structures  
- **Custom SQL**: `executeCustomSQLMSSQL()` - For advanced users with safety checks
- **Auth Validation**: `validateAzureAuthMSSQL()` - Check Azure authentication

## 🎯 Quick Start Examples

### Natural Language Query Examples
```python
# Go SDK specific queries
await mssqlQuery("Show me Go-SDK request counts this month")
await mssqlQuery("Top Go packages by usage")

# Product comparison analysis
await mssqlQuery("Top 10 Azure SDKs by request count")
await mssqlQuery("Python-SDK vs Java-SDK usage comparison")

# Time series analysis
await mssqlQuery("Request trends for 2024")
await mssqlQuery("This month vs last month Azure SDK usage")

# Multi-dimensional filtering
await mssqlQuery("Windows users of Python-SDK")
await mssqlQuery("GET requests for JavaScript SDK")
```

### Additional Features
```python
# Discover available data
await listTablesMSSQL()

# Validate Azure authentication
await validateAzureAuthMSSQL()

# Advanced custom SQL (with safety checks)
await executeCustomSQLMSSQL("SELECT TOP 5 Product, RequestCount FROM AMEConciseSubReqCCIDCountByMonthProduct ORDER BY RequestCount DESC")
```

## 🔧 Technical Implementation

### REST API Architecture (ODBC-Free)

This implementation is completely **ODBC-free** and uses REST APIs for Azure SQL connectivity:

#### 🔐 Azure AD Authentication
- **Password-Free Access**: Uses DefaultAzureCredential
- **Multiple Auth Methods**: Supports Managed Identity, Azure CLI, environment variables
- **High Security**: No need to store passwords in code

### Available Tools

#### 1. `sqlQueryREST` / `mssqlQuery`
**Execute natural language SQL queries**

```python
# Example usage
result = await mssqlQuery("Show Python-SDK usage this month")
```

**Features**:
- Parses natural language questions
- Automatically generates SQL queries
- Executes queries and returns results
- Intelligently handles product, time, and Track filtering conditions

#### 2. `listTablesREST` / `listTablesMSSQL`
**List all available tables and their structure**

```python
# Example usage
result = await listTablesMSSQL()
```

**Features**:
- Shows all enabled tables
- Detailed column information and types
- Available enumeration values (products, providers, operating systems, etc.)

#### 3. `validateAzureAuthREST` / `validateAzureAuthMSSQL`
**Validate Azure AD authentication**

```python
# Example usage
result = await validateAzureAuthMSSQL()
```

**Features**:
- Tests SQL database access tokens
- Tests Azure Management API tokens
- Provides authentication troubleshooting suggestions

#### 4. `executeCustomSQLREST` / `executeCustomSQLMSSQL`
**Execute custom SQL queries**

```python
# Example usage
result = await executeCustomSQLMSSQL("SELECT TOP 10 Product, RequestCount FROM AMEConciseSubReqCCIDCountByMonthProduct ORDER BY RequestCount DESC")
```

**Features**:
- Directly executes SQL SELECT statements
- SQL injection protection
- Only allows SELECT operations

## 🛠️ Installation and Setup

### Prerequisites
- Python 3.8+
- Azure subscription with SQL Database access
- Azure CLI (for development) or appropriate service principal (for production)

### Dependencies
```bash
pip install -r requirements.txt
```

**Key dependencies:**
- `httpx` - HTTP client for REST API calls
- `azure-identity` - Azure AD authentication
- `mcp[cli]>=1.5.0` - Model Context Protocol framework

### Environment Variables
```bash
export SQL_SERVER="azuresdkbi-server.database.windows.net"
export SQL_DATABASE="azuresdkbi"
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export AZURE_RESOURCE_GROUP="your-resource-group"
export FUNCTIONS_CUSTOMHANDLER_PORT="8080"
```

### Authentication Setup

#### For Development (Azure CLI)
```bash
az login
```

#### For Production (Environment Variables)
```bash
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"
```

#### For Azure Functions (Managed Identity)
- No additional configuration needed
- Azure Functions automatically provides Managed Identity

## 🚀 Deployment Options

### 1. Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
func start
# or
python mssql_query_server.py
```

### 2. Azure Functions
```bash
# Deploy using Azure Functions Core Tools
func azure functionapp publish <your-function-app-name>
```

### 3. Azure Developer CLI (Recommended)
```bash
# One-command deployment
azd up
```

This creates and deploys:
- Function App with the MCP server
- Required Azure resources
- Proper networking and security configurations

## 📊 Supported Query Types & Examples

### Product-Related Queries
```python
# SDK usage analysis
"Show me request counts for Go-SDK"
"Top 10 products by usage" 
"Python-SDK usage in 2024"
"Compare Track1 vs Track2 for Python-SDK"
```

### Time-Based Filtering
```python
# Temporal analysis
"Data for this month"
"Usage in 2024-01"
"Latest request counts"
"Request trends for 2024"
```

### Aggregation and Sorting
```python
# Statistical queries
"Top 10 customers by requests"
"Lowest usage products"
"Most active subscriptions"
"Which customers have more than 1000 requests?"
```

### Multi-Dimensional Filtering
```python
# Complex filtering
"Windows users of Python-SDK"
"POST requests for Java SDK"
"Microsoft.Compute provider usage"
"JavaScript SDK usage by operating system"
```

### Validation Examples

#### Successful Validation
```python
# Query: "Show me Go-SDK request counts this month"
{
  "valid": true,
  "generated_sql": "SELECT RequestsDate, RequestCount, PackageName, PackageVersion, IsTrack2 FROM AMEGoSDKReqCountCustomerDataByMonth WHERE RequestsDate LIKE '2025-08%' ORDER BY RequestCount DESC",
  "table_used": "AMEGoSDKReqCountCustomerDataByMonth",
  "columns_selected": ["RequestsDate", "RequestCount", "PackageName", "PackageVersion", "IsTrack2"],
  "filters_applied": "RequestsDate LIKE '2025-08%'",
  "ordering": "ORDER BY RequestCount DESC"
}
```

#### Failed Validation
```python
# Query: "Invalid query with nonsense"
{
  "valid": false,
  "error": "Could not identify relevant filters for your question",
  "suggestions": [
    "Try asking about products, customers, or request counts",
    "Include specific dates like '2024-01' or time periods",
    "Mention specific products like 'Python-SDK' or 'Java Fluent Premium'",
    "Ask for top/bottom N results"
  ]
}
```

## 🔍 Available Data Tables

The system supports multiple Azure SDK usage data tables:

### 1. **AMEGoSDKReqCountCustomerDataByMonth**
- **Purpose**: Go SDK specific request data
- **Key Columns**: RequestsDate, RequestCount, PackageName, PackageVersion, IsTrack2
- **Use Cases**: Go SDK usage analysis, Track2 migration tracking

### 2. **AMEConciseSubReqCCIDCountByMonthProduct** 
- **Purpose**: Subscription and request statistics by product
- **Key Columns**: Month, Product, RequestCount, SubscriptionCount
- **Use Cases**: Product comparison, usage trends

### 3. **AMEConciseSubReqCCIDCountByMonthProductOS**
- **Purpose**: Usage statistics by operating system
- **Key Columns**: Month, Product, OperatingSystem, RequestCount
- **Use Cases**: OS-specific usage analysis

### 4. **AMEConciseSubReqCCIDCountByMonthProductHttpMethod**
- **Purpose**: Request statistics by HTTP method
- **Key Columns**: Month, Product, HttpMethod, RequestCount
- **Use Cases**: API usage pattern analysis

### 5. **Additional Tables**
- Support for API versions, providers, resource types, and other dimensions
- Complete schema available via `listTablesMSSQL()` tool

## 📈 Response Format

### Successful Query Response
```json
{
  "success": true,
  "query": "SELECT Month, Product, RequestCount FROM AMEConciseSubReqCCIDCountByMonthProduct WHERE Month LIKE '2025-08%' AND Product = 'Python-SDK' ORDER BY RequestCount DESC",
  "data": [
    {
      "Month": "2025-08-01",
      "Product": "Python-SDK", 
      "RequestCount": 15420
    }
  ],
  "row_count": 4,
  "table_used": "AMEConciseSubReqCCIDCountByMonthProduct",
  "validation_info": {
    "pre_validated": true,
    "columns_selected": ["Month", "Product", "RequestCount"],
    "filters_applied": "Month LIKE '2025-08%' AND Product = 'Python-SDK'",
    "ordering": "ORDER BY RequestCount DESC"
  },
  "connection_method": "REST API",
  "server": "azuresdkbi-server.database.windows.net",
  "database": "azuresdkbi"
}
```

### Error Response
```json
{
  "error": "Query validation failed",
  "validation_error": "Could not identify relevant table for your question",
  "suggestions": [
    "Try asking about products, customers, or request counts",
    "Include specific dates like '2024-01' or time periods", 
    "Mention specific products like 'Python-SDK' or 'Go-SDK'",
    "Ask for top/bottom N results"
  ]
}
```

## 🛡️ Security Features

### SQL Injection Protection
- Only SELECT statements allowed in custom SQL
- Dangerous keywords (DROP, DELETE, INSERT, etc.) are blocked  
- Parameterized query building for natural language queries
- Input validation and sanitization

### Azure AD Authentication
- Password-free database access using DefaultAzureCredential
- Support for multiple authentication methods:
  - Managed Identity (recommended for production)
  - Azure CLI (for development)
  - Service Principal (environment variables)
  - User-assigned managed identity

### Access Control
- Read-only database access (SELECT operations only)
- Proper connection cleanup and resource management
- Secure token-based authentication
- Connection timeout and retry mechanisms

## 📊 Performance Optimizations

### Validation-First Benefits
1. **Fast Failure**: Invalid queries return immediately without resource waste
2. **Smart Caching**: Table structure information cached locally
3. **Connection Reuse**: REST API connection optimization  
4. **Step-by-Step Processing**: Clear processing stages for optimization

### Connection Strategies
- **Primary**: Direct Azure SQL Database REST API
- **Fallback**: Azure Management API
- **Emergency**: Mock data for service availability
- **Intelligent Routing**: Automatic selection of best connection method

## 🧪 Testing and Validation

### Running Tests
```bash
# Test validation flow
python test_validation_flow.py

# Run complete feature demonstration  
python demo_validation_flow.py

# Validate Azure authentication
curl -X POST "http://localhost:8080/validateAzureAuthMSSQL"

# List available tables
curl -X POST "http://localhost:8080/listTablesMSSQL"

# Validate query without execution
curl -X POST "http://localhost:8080/validateQueryMSSQL" \
  -d '{"user_question": "Show me top 10 products"}'
```

### Debug Tools
```bash
# Check authentication status
await validateAzureAuthMSSQL()

# Explore available data
await listTablesMSSQL()

# Validate before execution
await validateQueryMSSQL("your query here")
```

## 🚨 Troubleshooting

### Common Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| Validation Failed | Query semantics unclear | Reference examples, use standard format |
| Connection Failed | Azure authentication issue | Run `az login` to re-authenticate |
| Permission Error | Database access rights | Check Azure RBAC settings |
| Empty Results | Filters too restrictive | Simplify query conditions |

### Error Categories

#### Authentication Errors
```bash
# Re-authenticate with Azure CLI
az login

# Check subscription access
az account show

# Verify SQL server permissions
az sql server show --name <server-name> --resource-group <rg-name>
```

#### Query Validation Errors
- **Unclear Intent**: Rephrase question with specific keywords
- **Table Not Found**: Use `listTablesMSSQL()` to see available tables
- **Invalid Filters**: Check date formats and product names

#### Connection Issues
- **Network Problems**: Verify connectivity to Azure
- **Firewall Rules**: Ensure SQL server allows your IP
- **Service Outages**: Check Azure status page

### Best Practices

1. **Always Validate First**: Use `validateQueryMSSQL()` before executing
2. **Check Suggestions**: Review `suggestions` field when validation fails
3. **Use Standard Names**: Reference products as "Python-SDK", "Go-SDK", etc.
4. **Date Formats**: Use "2024-01" or "this month" format
5. **Clear Intent**: Include keywords like "top 10", "count", "usage"



### VS Code Integration

1. **Local Development**: Start server locally with `func start`
2. **MCP Configuration**: Configure in `.vscode/mcp.json`
3. **Agent Mode**: Use Copilot in Agent mode to interact with the server
4. **Remote Deployment**: Deploy to Azure and connect remotely

### APIM Integration (Optional)

For additional security, deploy with Azure API Management (APIM):
- **Entra ID Authentication**: Redirects clients to authenticate before connecting
- **Protected Resource Metadata**: Follows MCP authorization specification
- **Policy-Based Security**: Custom policies for access control

## 🔗 Integration Examples

### VS Code Copilot Integration
```json
{
  "mcpServers": {
    "local-mcp-server": {
      "command": "func",
      "args": ["start"],
      "env": {
        "FUNCTIONS_CUSTOMHANDLER_PORT": "8080"
      }
    }
  }
}
```

### Claude Desktop Integration
```json
{
  "mcpServers": {
    "azure-sql": {
      "command": "python",
      "args": ["mssql_query_server.py"],
      "env": {
        "SQL_SERVER": "your-server.database.windows.net",
        "SQL_DATABASE": "your-database"
      }
    }
  }
}
```

## 📚 Additional Resources

### Documentation Links
- [Azure Functions Custom Handlers](https://docs.microsoft.com/azure/azure-functions/functions-custom-handlers)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Azure SQL Database REST API](https://docs.microsoft.com/rest/api/sql/)
- [Azure AD Authentication](https://docs.microsoft.com/azure/active-directory/develop/)

### Sample Queries for Testing
```python
# Basic usage queries
"Show me Python-SDK usage this month"
"Top 10 products by request count"
"Go SDK request trends for 2024"

# Comparative analysis
"Compare Python-SDK vs Java-SDK usage"
"Track1 vs Track2 adoption rates"
"Windows vs Linux usage patterns"

# Time-based analysis  
"Request counts for January 2024"
"This month vs last month comparison"
"Quarterly usage trends"

# Advanced filtering
"High-usage customers with more than 1000 requests"
"GET requests for REST APIs"
"Microsoft.Compute resource provider usage"
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Install dependencies: `pip install -r requirements.txt`
4. Make your changes and add tests
5. Run tests: `python test_validation_flow.py`
6. Commit changes: `git commit -m 'Add amazing feature'`
7. Push branch: `git push origin feature/amazing-feature`
8. Submit a Pull Request

### Code Standards
- Follow PEP 8 style guidelines
- Add comprehensive docstrings
- Include unit tests for new features
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.

## 🎉 Getting Started

Ready to start using the Azure SQL MCP Server? Follow these simple steps:

1. **Clone the repository**
2. **Install dependencies**: `pip install -r requirements.txt`  
3. **Configure Azure authentication**: `az login`
4. **Set environment variables** for your SQL server
5. **Start the server**: `func start`
6. **Connect from VS Code** using the MCP configuration
7. **Ask your first question**: "Show me the top 10 Azure SDK products by usage"

Experience faster, more reliable data analysis with our validation-first query flow! 🚀
