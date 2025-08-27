# 🚀 快速开始指南

## 验证优先查询流程使用指南

### 📦 安装和配置

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
export SQL_SERVER="azuresdkbi-server.database.windows.net"
export SQL_DATABASE="azuresdkbi"
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export AZURE_RESOURCE_GROUP="your-resource-group"

# 3. 启动服务
func start
```

### 🎯 核心功能

#### 1. 验证查询（推荐）
```python
# 先验证查询，不连接数据库
result = await validateQueryMSSQL("Show me Go-SDK request counts")

# 检查验证结果
if result['valid']:
    print(f"SQL: {result['generated_sql']}")
    print(f"表: {result['table_used']}")
    print(f"列: {result['columns_selected']}")
else:
    print(f"错误: {result['error']}")
    print(f"建议: {result['suggestions']}")
```

#### 2. 执行查询（验证优先）
```python
# 自动先验证，然后执行
result = await mssqlQuery("Top 10 products by request count")

if result.get('success'):
    print(f"查询成功，返回 {result['row_count']} 行数据")
    print(f"验证信息: {result['validation_info']}")
else:
    print(f"查询失败: {result['error']}")
```

### 🔍 查询示例

#### Go SDK 专用查询
```
"Show me Go-SDK request counts this month"
"Go SDK usage by package version"
"Track 2 Go SDK adoption"
```

#### 产品对比分析
```
"Top 10 Azure SDKs by usage"
"Python-SDK vs Java-SDK comparison"
"Least used SDK products"
```

#### 时间序列分析
```
"Request trends for 2024"
"This month vs last month"
"January 2024 usage data"
```

#### 多维度过滤
```
"Windows users of Python-SDK"
"GET requests for JavaScript SDK"
"Microsoft.Compute API usage"
```

### ⚡ 性能优势

| 功能 | 传统方式 | 验证优先方式 |
|------|---------|-------------|
| 错误检测 | 连接数据库后才发现 | 立即检测，无需连接 |
| 响应时间 | 慢（网络+认证+查询） | 快（本地验证） |
| 资源消耗 | 高（无效连接） | 低（避免无效连接） |
| 用户体验 | 延迟反馈 | 即时反馈 |

### 🛠️ 测试工具

```bash
# 运行验证测试
python test_validation_flow.py

# 运行完整演示
python demo_validation_flow.py

# 验证Azure认证
curl -X POST "http://localhost:8080/validateAzureAuthMSSQL"
```

### 📊 返回结果格式

#### 验证结果
```json
{
  "valid": true,
  "generated_sql": "SELECT ...",
  "table_used": "AMEGoSDKReqCountCustomerDataByMonth",
  "columns_selected": ["RequestsDate", "RequestCount"],
  "filters_applied": "Month LIKE '2025-08%'",
  "ordering": "ORDER BY RequestCount DESC",
  "limit": "TOP 10"
}
```

#### 查询结果
```json
{
  "success": true,
  "query": "SELECT ...",
  "data": [...],
  "row_count": 150,
  "table_used": "AMEGoSDKReqCountCustomerDataByMonth",
  "validation_info": {
    "pre_validated": true,
    "columns_selected": [...],
    "filters_applied": "...",
    "ordering": "..."
  }
}
```

### 🔧 常用MCP工具

```bash
# 查看可用表
listTablesMSSQL()

# 验证查询
validateQueryMSSQL("your question")

# 执行查询
mssqlQuery("your question")

# 验证认证
validateAzureAuthMSSQL()

# 自定义SQL
executeCustomSQLMSSQL("SELECT * FROM table")
```

### 💡 最佳实践

1. **先验证再执行**: 使用 `validateQueryMSSQL` 确认SQL正确性
2. **查看建议**: 验证失败时查看 `suggestions` 字段
3. **利用枚举**: 使用标准产品名如 "Python-SDK", "Go-SDK"
4. **时间格式**: 使用 "2024-01" 或 "this month" 格式
5. **明确意图**: 包含 "top 10", "count", "usage" 等关键词

### 🚨 故障排除

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 验证失败 | 查询语义不清 | 参考示例，使用标准格式 |
| 连接失败 | Azure认证问题 | 运行 `az login` 重新认证 |
| 权限错误 | 数据库访问权限 | 检查Azure RBAC设置 |
| 空结果 | 过滤条件过严 | 简化查询条件 |

开始使用验证优先查询流程，享受更快速、更可靠的数据分析体验！ 🎉
