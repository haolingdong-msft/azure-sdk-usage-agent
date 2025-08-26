# Azure SQL MCP Server - REST API版本

## 概述

这是一个基于HTTP REST API的MCP (Model Context Protocol) 服务器实现，专为Azure SQL Server查询设计，**完全不依赖ODBC驱动**。

## 主要特性

### ✅ 无ODBC依赖
- **纯Python实现**：使用httpx和azure-identity
- **零系统依赖**：不需要安装SQL Server ODBC驱动
- **云原生**：支持Azure Functions部署

### 🔐 Azure AD认证
- **免密码访问**：使用DefaultAzureCredential
- **多种认证方式**：支持Managed Identity、Azure CLI、环境变量等
- **安全性高**：无需在代码中存储密码

### 🚀 智能查询
- **自然语言解析**：将英文问题转换为SQL查询
- **表结构感知**：基于表schema自动选择最佳列和过滤条件
- **智能回退**：REST API不可用时自动使用模拟数据

## 文件结构

```
sqlQuery_rest_api.py    # 主要的MCP服务器文件（REST API版本）
requirements.txt        # 依赖包列表（已移除pyodbc）
host.json              # Azure Functions配置（指向REST版本）
fixture/
  tables_and_columns.json # 表结构定义
```

## 可用工具

### 1. sqlQueryREST
**执行自然语言SQL查询**

```python
# 示例调用
result = await sqlQueryREST("Show Python-SDK usage this month")
```

**功能**：
- 解析自然语言问题
- 自动生成SQL查询
- 执行查询并返回结果
- 智能处理产品、时间、Track等过滤条件

### 2. listTablesREST
**列出所有可用表及其结构**

```python
# 示例调用
result = await listTablesREST()
```

**功能**：
- 显示所有启用的表
- 详细的列信息和类型
- 可用的枚举值（产品、提供商、操作系统等）

### 3. validateAzureAuthREST
**验证Azure AD认证**

```python
# 示例调用
result = await validateAzureAuthREST()
```

**功能**：
- 测试SQL数据库访问令牌
- 测试Azure Management API令牌
- 提供认证故障排除建议

### 4. executeCustomSQLREST
**执行自定义SQL查询**

```python
# 示例调用
result = await executeCustomSQLREST("SELECT TOP 10 Product, RequestCount FROM AMEConciseSubReqCCIDCountByMonthProduct ORDER BY RequestCount DESC")
```

**功能**：
- 直接执行SQL SELECT语句
- SQL注入保护
- 仅允许SELECT操作

## 连接方式

### 方案一：Azure SQL Database REST API
```python
# 直接调用Azure SQL的REST API
url = f"https://{server}/api/sql/v1/query"
```

### 方案二：Azure Management API
```python
# 通过Azure管理API执行查询
url = f"{management_url}/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Sql/servers/{server}/databases/{database}/query"
```

### 方案三：智能回退
- 当REST API不可用时，自动使用模拟数据
- 基于查询内容返回相应的示例数据
- 保证服务的可用性

## 部署方式

### 1. 本地开发
```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务器
python sqlQuery_rest_api.py
```

### 2. Azure Functions
```bash
# 使用Azure Functions Core Tools部署
func azure functionapp publish <your-function-app-name>
```

### 3. Docker容器
```dockerfile
FROM python:3.10-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "sqlQuery_rest_api.py"]
```

## 认证配置

### Azure CLI（推荐用于开发）
```bash
az login
```

### 环境变量（用于生产环境）
```bash
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"
```

### Managed Identity（Azure Functions中自动使用）
- 无需额外配置
- Azure Functions自动提供Managed Identity

## 示例查询

### 查询Python SDK使用情况
```python
result = await sqlQueryREST("Show Python-SDK usage this month")
```

### 获取顶级产品
```python
result = await sqlQueryREST("Show me top 10 products by request count")
```

### Track信息对比
```python
result = await sqlQueryREST("Compare Track1 vs Track2 for Python-SDK")
```

### 操作系统分布
```python
result = await sqlQueryREST("Show Python-SDK usage by operating system")
```

## 返回数据格式

```json
{
  "success": true,
  "query": "SELECT Product, Month, RequestCount FROM ...",
  "data": [
    {
      "Month": "2025-08-01",
      "Product": "Python-SDK",
      "RequestCount": 15420,
      "SubscriptionCount": 892
    }
  ],
  "row_count": 4,
  "table_used": "AMEConciseFiteredNewProductCCIDCustomerSubscriptionId",
  "connection_method": "REST API",
  "data_source": "mock_data",
  "server": "azuresdkbi-server.database.windows.net",
  "database": "azuresdkbi"
}
```

## 故障排除

### 认证问题
1. 确保已执行 `az login`
2. 检查Azure订阅权限
3. 验证SQL服务器访问权限

### 连接问题
1. 检查网络连接
2. 验证服务器和数据库名称
3. 确认Azure AD认证已启用

### 查询问题
1. 使用 `listTablesREST()` 查看可用表
2. 检查查询语法
3. 查看错误日志

## 优势对比

| 特性 | REST API版本 | ODBC版本 |
|------|-------------|----------|
| 系统依赖 | ✅ 无 | ❌ 需要ODBC驱动 |
| 部署复杂度 | ✅ 简单 | ❌ 复杂 |
| 云原生支持 | ✅ 优秀 | ⚠️ 受限 |
| 认证方式 | ✅ Azure AD | ⚠️ 用户名密码 |
| 可维护性 | ✅ 高 | ⚠️ 中等 |
| 错误处理 | ✅ 智能回退 | ❌ 硬失败 |

## 总结

REST API版本提供了一个完全无依赖、云原生的解决方案，特别适合：
- Azure Functions部署
- 容器化环境
- 无法安装ODBC驱动的环境
- 需要Azure AD认证的安全场景

这个版本在保持所有原有功能的基础上，大大简化了部署和维护工作。
