# SQL Server Client Migration to pyodbc

## 概述
已成功将 `sql_client.py` 从使用 REST API 方式改为使用 pyodbc 直接连接 Azure SQL Database。

## 主要更改

### 1. 依赖项更新
- 在 `requirements.txt` 中添加了 `pyodbc` 包
- 移除了对 `httpx` 的依赖（在查询执行部分）

### 2. sql_client.py 的重大重构
- **移除了**: REST API 相关的所有代码和方法
- **新增了**: 基于 pyodbc 的直接数据库连接功能
- **保留了**: Azure AD 认证逻辑

#### 主要方法变更:
- `_build_connection_string()`: 新增，构建 ODBC 连接字符串
- `_get_connection()`: 新增，创建和管理数据库连接
- `execute_query_via_rest()`: 重构为使用 pyodbc 执行查询
- 移除了 `_try_sql_database_api()` 和 `_try_management_api()` 方法

### 3. 连接字符串配置
使用 ODBC Driver 17 for SQL Server，配置包括：
- Azure AD Access Token 认证
- SSL 加密连接
- 30秒连接超时

### 4. 数据类型处理
增强了对不同数据类型的处理：
- DateTime 对象转换为 ISO 格式
- 二进制数据解码为 UTF-8
- 空值和基本类型的正确处理

### 5. mcp_tools.py 更新
- 更新了所有错误消息和日志，将 "REST API" 改为 "pyodbc"
- 更新了故障排除建议
- 移除了对管理 API scope 的引用
- 更新了连接方法描述

## 连接方式对比

### 之前 (REST API)
- 使用概念性的 REST 端点
- 需要订阅 ID 和资源组信息
- 双重认证范围 (SQL + Management)
- 连接可靠性较低

### 现在 (pyodbc)
- 直接 ODBC 数据库连接
- 只需要数据库服务器和数据库名
- 单一认证范围 (SQL Database)
- 更高的性能和可靠性
- 原生 SQL Server 功能支持

## 系统要求
- ODBC Driver 17 for SQL Server (或更高版本)
- pyodbc Python 包
- Azure AD 认证配置

## 测试
创建了 `test_connection.py` 脚本来验证连接功能。

## 优势
1. **性能提升**: 直接数据库连接比 REST API 调用更快
2. **可靠性**: 减少了网络层和 API 层的复杂性
3. **功能完整**: 支持完整的 SQL Server 功能
4. **错误处理**: 更清晰的数据库级别错误信息
5. **资源使用**: 更少的网络开销和更好的连接池管理

## 配置示例
```python
connection_string = (
    f"Driver={{ODBC Driver 17 for SQL Server}};"
    f"Server=tcp:{SQL_SERVER},1433;"
    f"Database={SQL_DATABASE};"
    f"Encrypt=yes;"
    f"TrustServerCertificate=no;"
    f"Connection Timeout=30;"
    f"AccessToken={access_token}"
)
```

## 故障排除
如果遇到连接问题：
1. 确保已安装 ODBC Driver 17 for SQL Server
2. 验证 Azure AD 登录状态 (`az login`)
3. 检查数据库访问权限
4. 确认网络连接到 Azure SQL Database
