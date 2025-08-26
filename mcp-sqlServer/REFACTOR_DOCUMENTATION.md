# SQL Query MCP Server - Refactored Version

## Overview

This refactored version of the SQL Query MCP server provides intelligent, natural language-based querying capabilities for Azure SQL Server data. Instead of requiring users to specify exact table names, columns, and conditions, users can now ask questions in plain English.

## Key Improvements

### 1. Natural Language Processing
- **Before**: Required exact parameters: `tableName`, `columns`, `conditions`
- **After**: Accepts natural language questions like "Show me the top 10 customers by request count"

### 2. Schema Awareness
- Automatically loads table schema from `fixture/tables_and_columns.json`
- Intelligently maps user questions to appropriate tables and columns
- Provides suggestions when queries can't be interpreted

### 3. Enhanced Error Handling
- Comprehensive error handling for database connections
- Detailed error messages with suggestions
- Protection against SQL injection attacks

### 4. Multiple Query Methods
- **Natural Language Query**: `sqlQuery(question)` - For everyday users
- **List Tables**: `listTables()` - To explore available data
- **Custom SQL**: `executeCustomSQL(sql)` - For advanced users

### 5. Improved Response Format
- Structured JSON responses with metadata
- Row counts and query information
- Success/error status indicators

## Usage Examples

### Natural Language Queries

```python
# Find top customers
await sqlQuery("Show me the top 10 customers by request count")

# Product analysis
await sqlQuery("What products were used in 2024-01?")

# Filter by criteria
await sqlQuery("Which customers have more than 1000 requests?")

# Subscription data
await sqlQuery("Show me subscription information for high-usage customers")
```

### Table Discovery

```python
# List all available tables and columns
await listTables()
```

### Custom SQL (Advanced)

```python
# Execute custom SQL with safety checks
await executeCustomSQL("SELECT TOP 5 CustomerName, RequestCount FROM AMEConciseFiteredNewProductCCIDCustomer ORDER BY RequestCount DESC")
```

## Response Format

### Successful Query Response
```json
{
  "success": true,
  "query": "SELECT TOP 10 CustomerName, RequestCount FROM AMEConciseFiteredNewProductCCIDCustomer ORDER BY RequestCount DESC",
  "data": [
    {
      "CustomerName": "Customer A",
      "RequestCount": 5000
    }
  ],
  "row_count": 10,
  "table_used": "AMEConciseFiteredNewProductCCIDCustomer"
}
```

### Error Response
```json
{
  "error": "Could not identify a relevant table from your question. Available topics: customer data, product usage, subscription information.",
  "suggestion": "Try asking questions like: 'Show me top 10 customers', 'What products were used this month?', 'Which customers have high request counts?'"
}
```

## Natural Language Understanding

The system can interpret various question patterns:

### Table Detection
- Keywords like "customer", "product", "subscription" map to appropriate tables
- Direct table name references are supported

### Column Selection
- Automatically selects relevant columns based on question context
- Falls back to important columns (names, counts, dates) if none specified
- Mentions of specific columns are detected and included

### Filtering (WHERE clauses)
- **Time-based**: "in 2024-01", "this month", "january"
- **Numeric**: "more than 1000", "greater than", "top 10"
- **String matching**: "customer named Microsoft", "product is Azure"

### Sorting and Limiting
- **Top N**: "top 10", "first 5"
- **Ordering**: "highest", "most", "lowest", "least"

## Security Features

### SQL Injection Protection
- Only SELECT statements allowed in custom SQL
- Dangerous keywords (DROP, DELETE, INSERT, etc.) are blocked
- Parameterized query building for natural language queries

### Connection Security
- Azure AD authentication using DefaultAzureCredential
- Secure token-based database connections
- Proper connection cleanup

## Configuration

### Environment Variables
- `SQL_SERVER`: Azure SQL Server hostname (default: azuresdkbi-server.database.windows.net)
- `SQL_DATABASE`: Database name (default: azuresdkbi)
- `FUNCTIONS_CUSTOMHANDLER_PORT`: Server port (default: 8080)

### Required Dependencies
```
httpx
mcp[cli]>=1.5.0
pyodbc
azure-identity
```

## Testing

Run the test suite to verify functionality:

```bash
python test_queries.py
```

This will test:
- Natural language query parsing
- Table listing functionality
- Custom SQL execution
- Error handling scenarios

## Available Tables

Based on the schema file, the following tables are available:

1. **AMEConciseFiteredNewProductCCIDCustomer**
   - Columns: Month, Product, CustomerName, TrackInfo, CCID, RequestCount

2. **AMEConciseFiteredNewProductCCIDCustomerSubscriptionId**
   - Columns: Month, Product, CCID, CustomerName, TrackInfo, SubscriptionId, RequestCount

## Future Enhancements

1. **Advanced NLP**: Integration with language models for better query understanding
2. **Query Optimization**: Automatic query optimization suggestions
3. **Data Visualization**: Integration with charting libraries
4. **Caching**: Query result caching for improved performance
5. **Audit Logging**: Comprehensive query logging and monitoring
