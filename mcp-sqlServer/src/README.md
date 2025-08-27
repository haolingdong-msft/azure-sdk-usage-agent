# MCP SQL Server - 模块化重构说明

## 文件结构

代码已重构为以下模块化结构：

```
src/
├── __init__.py          # 包初始化文件
├── config.py           # 配置和常量
├── models.py           # 数据模型和类型定义
├── schema_loader.py    # 模式加载器
├── sql_client.py       # SQL REST 客户端
├── query_parser.py     # 查询解析器
├── mcp_tools.py        # MCP 工具实现
└── main.py             # 主程序入口
```

## 模块说明

### 1. config.py - 配置和常量
包含所有配置参数和常量：
- MCP 服务器端口配置
- SQL Server 连接设置
- Azure 认证作用域
- 模式文件路径

### 2. models.py - 数据模型
定义了核心数据结构：
- `TableInfo`: 数据库表信息
- `QueryInfo`: 解析后的查询信息
- `QueryResult`: SQL 查询结果

### 3. schema_loader.py - 模式加载器
负责加载和管理数据库模式：
- 从 JSON 文件加载表结构
- 提供枚举值访问
- 缓存模式信息以提高性能

### 4. sql_client.py - SQL REST 客户端
实现与 Azure SQL Database 的 REST API 连接：
- Azure AD 认证
- 双重 API 策略（直接 API + 管理 API）
- 错误处理和重试逻辑

### 5. query_parser.py - 查询解析器
将自然语言转换为 SQL 查询：
- 表名识别
- 列选择逻辑
- WHERE 子句构建
- 排序和限制处理

### 6. mcp_tools.py - MCP 工具实现
包含所有 MCP 工具的业务逻辑：
- `execute_sql_query`: 执行自然语言查询
- `list_tables`: 列出可用表
- `validate_azure_auth`: 验证 Azure 认证
- `execute_custom_sql`: 执行自定义 SQL
- `get_enum_values`: 获取枚举值
- `validate_query`: 验证查询

### 7. main.py - 主程序入口
创建和配置 MCP 服务器：
- 初始化所有组件
- 注册 MCP 工具
- 服务器启动逻辑

## 向后兼容性

原有的 `mssql_query_server.py` 文件已更新为向后兼容的包装器，它简单地导入并使用新的模块化组件。这确保了现有的部署和引用不会中断。

## 好处

1. **可维护性**: 每个模块都有明确的职责
2. **可测试性**: 模块可以独立测试
3. **可扩展性**: 容易添加新功能而不影响现有代码
4. **可重用性**: 组件可以在其他项目中重用
5. **代码组织**: 相关功能被组织在一起，更容易理解和修改

## 使用方式

使用方式保持不变：

```bash
python mssql_query_server.py
```

或者直接使用新的主入口：

```bash
python -m src.main
```
