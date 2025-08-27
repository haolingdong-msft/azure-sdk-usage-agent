# MCP SQL Server - 验证优先查询流程

## 🎯 概述

本项目实现了一个基于验证优先的智能 SQL 查询系统，通过 Model Context Protocol (MCP) 为 Azure SQL 数据库提供自然语言查询接口。

## 🔄 核心改进：验证优先流程

### 传统流程 vs 新流程

**❌ 传统流程（问题多）:**
```
用户问题 → 解析SQL → 立即连接数据库 → 执行查询 → 返回结果
          ↘ 如果SQL错误 → 浪费连接时间 → 返回数据库错误
```

**✅ 新的验证优先流程:**
```
用户问题 → 🔍 验证&生成SQL → ✅ 验证通过 → 🔗 连接数据库 → 执行查询 → 返回结果
                              ↘ ❌ 验证失败 → 立即返回错误和建议（无需连接）
```

### 🚀 流程优势

1. **快速失败机制**: SQL语法或逻辑错误立即被发现
2. **资源优化**: 避免无效的网络连接和认证请求
3. **更好的用户体验**: 快速反馈，详细的错误提示和建议
4. **清晰的日志**: 分步骤的处理过程，便于调试

## 📋 主要组件

### 1. MSSQLRestClient
负责与 Azure SQL 数据库的 REST API 连接，支持双重fallback策略：
- 直接 SQL Database API
- Azure Management API

### 2. 查询验证系统
- `validateQueryMSSQL()`: 验证自然语言查询并生成SQL
- `parse_user_query()`: 解析用户问题为SQL组件
- 智能表选择和列映射

### 3. MCP工具集
- `mssqlQuery()`: 主要查询接口（验证优先）
- `listTablesMSSQL()`: 列出可用表和字段
- `validateAzureAuthMSSQL()`: 验证Azure认证
- `executeCustomSQLMSSQL()`: 执行自定义SQL（高级用户）

## 🛠️ 使用示例

### 示例 1: Go SDK 请求统计

```python
# 自然语言查询
query = "Show me the request count for Go-SDK this month"

# 验证结果
{
  "valid": true,
  "generated_sql": "SELECT RequestsDate, RequestCount, PackageName, PackageVersion, IsTrack2 FROM AMEGoSDKReqCountCustomerDataByMonth WHERE RequestsDate LIKE '2025-08%' ORDER BY RequestCount DESC",
  "table_used": "AMEGoSDKReqCountCustomerDataByMonth",
  "columns_selected": ["RequestsDate", "RequestCount", "PackageName", "PackageVersion", "IsTrack2"],
  "filters_applied": "RequestsDate LIKE '2025-08%'",
  "ordering": "ORDER BY RequestCount DESC"
}
```

### 示例 2: 产品使用排行

```python
# 自然语言查询
query = "What are the top 10 products by request count?"

# 验证结果
{
  "valid": true,
  "generated_sql": "SELECT TOP 10 Month, Product, RequestCount FROM AMEConciseSubReqCCIDCountByMonthProduct ORDER BY RequestCount DESC",
  "table_used": "AMEConciseSubReqCCIDCountByMonthProduct",
  "columns_selected": ["Month", "Product", "RequestCount"],
  "filters_applied": "None",
  "ordering": "ORDER BY RequestCount DESC",
  "limit": "TOP 10"
}
```

### 示例 3: 特定产品和时间过滤

```python
# 自然语言查询
query = "How many requests for Python-SDK in 2024-01?"

# 验证结果
{
  "valid": true,
  "generated_sql": "SELECT Month, RequestCount FROM AMEConciseSubReqCCIDCountByMonthProduct WHERE Month LIKE '2024-01%' AND Product = 'Python-SDK' ORDER BY RequestCount DESC",
  "table_used": "AMEConciseSubReqCCIDCountByMonthProduct",
  "columns_selected": ["Month", "RequestCount"],
  "filters_applied": "Month LIKE '2024-01%' AND Product = 'Python-SDK'",
  "ordering": "ORDER BY RequestCount DESC"
}
```

### 示例 4: 验证失败的情况

```python
# 无效查询
query = "Invalid query with nonsense"

# 验证结果（如果失败）
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

## 🔧 技术实现

### 验证优先的查询处理

```python
async def mssqlQuery(request: str) -> Dict[str, Any]:
    # Step 1: 验证和生成SQL（不连接数据库）
    print("🔍 Step 1: Validating query and generating SQL...")
    validation_result = await validateQueryMSSQL(request)
    
    if not validation_result.get('valid', False):
        # 立即返回验证错误，无需连接数据库
        return {
            "error": "Query validation failed",
            "validation_error": validation_result.get('error'),
            "suggestions": validation_result.get('suggestions', [])
        }
    
    # Step 2: 验证通过后再连接数据库
    print("🔗 Step 2: Connecting to database and executing query...")
    sql_query = validation_result['generated_sql']
    
    # 执行查询...
```

### 智能表选择算法

```python
def find_table_by_name(query_text: str) -> Optional[str]:
    """基于查询内容智能选择最相关的表"""
    query_lower = query_text.lower()
    enabled_tables = {k: v for k, v in TABLE_SCHEMA['tables'].items() if v['enabled']}
    
    # 评分系统
    table_scores = {}
    for table_key, table_info in enabled_tables.items():
        score = 0
        # Go SDK特殊处理
        if 'go' in query_lower and 'gosdk' in table_info['name'].lower():
            score += 3
        # 产品相关
        if 'product' in query_lower and 'product' in table_info['name'].lower():
            score += 2
        # ... 更多评分规则
        
    return max(table_scores.items(), key=lambda x: x[1])[0] if table_scores else None
```

## 📊 详细日志输出

系统提供清晰的步骤日志：

```
Received question: Show me the request count for Go-SDK this month
🔍 Step 1: Validating query and generating SQL...
✅ SQL validation successful: SELECT RequestsDate, RequestCount, PackageName...
🔗 Step 2: Connecting to database and executing query...
🎯 Attempting direct SQL Database API connection...
🔐 Obtaining access token for SQL Database scope...
✅ Successfully obtained SQL Database access token
```

## 🚀 快速开始

### 1. 环境配置

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
export SQL_SERVER="azuresdkbi-server.database.windows.net"
export SQL_DATABASE="azuresdkbi"
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export AZURE_RESOURCE_GROUP="your-resource-group"
```

### 2. 启动服务

```bash
# 启动 Azure Functions
func start

# 或直接运行 MCP 服务器
python mssql_query_server.py
```

### 3. 测试验证流程

```bash
# 运行验证测试
python test_validation_flow.py
```

## 🎯 支持的查询类型

### 产品相关查询
- "Show me request counts for Go-SDK"
- "Top 10 products by usage"
- "Python-SDK usage in 2024"

### 时间过滤查询
- "Data for this month"
- "Usage in 2024-01"
- "Latest request counts"

### 聚合和排序查询
- "Top 10 customers by requests"
- "Lowest usage products"
- "Most active subscriptions"

### 多维度过滤
- "Windows users of Python-SDK"
- "POST requests for Java SDK"
- "Microsoft.Compute provider usage"

## 🔍 可用表结构

系统支持多个 Azure SDK 使用数据表：

1. **AMEGoSDKReqCountCustomerDataByMonth**: Go SDK专用请求数据
2. **AMEConciseSubReqCCIDCountByMonthProduct**: 按产品的订阅和请求统计
3. **AMEConciseSubReqCCIDCountByMonthProductOS**: 按操作系统的使用统计
4. **AMEConciseSubReqCCIDCountByMonthProductHttpMethod**: 按HTTP方法的请求统计
5. **更多表...**: 支持API版本、提供商、资源类型等维度

## 🛡️ 安全特性

- **SQL注入防护**: 只允许SELECT查询，禁止危险操作
- **Azure AD认证**: 使用Azure身份验证访问数据库
- **查询验证**: 预先验证SQL语法和逻辑
- **错误隔离**: 验证错误不会触发数据库连接

## 📈 性能优化

1. **快速失败**: 无效查询立即返回，不浪费资源
2. **智能缓存**: 表结构信息本地缓存
3. **连接复用**: REST API连接优化
4. **分步处理**: 清晰的处理阶段，便于优化

## 🐛 故障排除

### 常见问题

1. **验证失败**: 检查查询语法，参考示例
2. **连接失败**: 验证Azure认证和网络连接
3. **权限错误**: 确认账户有数据库访问权限

### 调试工具

```bash
# 验证Azure认证
curl -X POST "http://localhost:8080/validateAzureAuthMSSQL"

# 查看可用表
curl -X POST "http://localhost:8080/listTablesMSSQL"

# 验证查询（不执行）
curl -X POST "http://localhost:8080/validateQueryMSSQL" \
  -d '{"user_question": "your query here"}'
```

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'Add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 提交 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。
