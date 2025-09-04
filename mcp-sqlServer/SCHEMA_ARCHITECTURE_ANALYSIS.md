# Schema 架构设计问题分析

## ⚠️ AI 助手注意事项

**重要提醒**：当用户请求 KQL 查询生成时，应该：
1. **直接使用 MCP 工具**（如 `modifyKustoQuery`）
2. **不要先分析 schema.json 文件**
3. **当前项目使用 Kusto MCP**，它独立于 SQL MCP，不依赖 schema 文件

## 问题背景

在当前的 MCP SQL Server 项目中，存在一个设计问题：为什么要读取 `AMEAnalytics_Schema.json` 文件而不是直接调用 MCP 来获取 schema 信息？

## 当前架构分析

### 为什么使用 JSON Schema 文件

#### 1. **本地缓存策略**
- `SchemaLoader` 类使用本地 JSON 文件作为数据库 schema 的缓存
- 避免每次都需要查询数据库来获取表结构信息
- 提高响应速度，减少网络开销

```python
class SchemaLoader:
    def __init__(self, schema_file_path: str):
        self.schema_file_path = schema_file_path
        self._schema_cache = None  # 内存缓存
```

#### 2. **离线开发支持**
- 开发者可以在没有数据库连接的情况下进行开发和测试
- JSON 文件提供了完整的表结构、列信息、数据类型和枚举值
- 支持本地开发环境的独立性

#### 3. **MCP 架构设计**
- 该项目本身就是一个 **MCP 服务器**，而不是 MCP 客户端
- `mcp_tools.py` 和 `mcp_tools_kusto.py` 是 MCP 工具的实现
- 需要 schema 信息来验证和构建查询

## 存在的问题

### 1. **数据同步问题** ⚠️

**问题描述：**
```python
# Schema 可能过时
self._schema_cache = None  # 只在内存中缓存，重启后需要重新读取文件
```

**具体风险：**
- JSON 文件可能与实际数据库 schema 不同步
- 当数据库结构更新时，JSON 文件需要手动更新
- 没有自动验证机制确保 schema 一致性
- 可能导致查询失败或返回错误的列信息

### 2. **硬编码依赖** ⚠️

**问题代码：**
```python
schema_file = 'reference/schemas/AMEAnalytics_Schema.json'  # 硬编码路径
```

**具体问题：**
- 对特定文件路径的硬依赖
- 文件丢失或路径变更会导致系统失败
- 不利于不同环境的部署和配置

### 3. **混合架构复杂性** ⚠️

**架构冲突：**
- 同时存在 SQL Server 连接 (`sql_client`) 和静态 schema 文件
- 真实数据来自数据库，但 schema 来自文件，可能出现不一致
- 增加了系统的复杂性和维护难度

### 4. **缺乏动态发现** ⚠️

**缺失功能：**
```python
# 没有动态获取真实数据库 schema 的机制
enabled_tables_dict = self.schema_loader.get_enabled_tables()  # 只从文件读取
```

**影响：**
- 无法感知数据库结构的实时变化
- 新增的表或列无法自动发现
- 依赖手动维护 schema 文件

## 改进方案

### 1. **混合方案**（推荐）

实现动态 schema 获取与文件缓存的结合：

```python
async def get_live_schema_with_fallback(self):
    """
    先尝试从数据库获取实时 schema，失败时使用本地文件
    """
    try:
        # 尝试查询数据库获取实时 schema
        live_schema = await self.sql_client.get_database_schema()
        
        # 可选：将实时 schema 写入文件作为缓存
        await self.cache_schema_to_file(live_schema)
        
        return live_schema
    except Exception as e:
        print(f"无法获取实时 schema，使用本地文件: {e}")
        return self.schema_loader.load_table_schema()
```

### 2. **定期同步验证**

添加 schema 一致性检查机制：

```python
async def validate_schema_consistency(self):
    """
    验证本地 schema 文件与数据库的一致性
    """
    try:
        # 获取数据库实际结构
        db_schema = await self.sql_client.get_database_schema()
        
        # 读取本地文件 schema
        file_schema = self.schema_loader.load_table_schema()
        
        # 比较差异
        differences = self.compare_schemas(db_schema, file_schema)
        
        if differences:
            print("⚠️ Schema 不一致，发现以下差异：")
            for diff in differences:
                print(f"  - {diff}")
            
            return {
                "consistent": False,
                "differences": differences,
                "recommendation": "建议更新本地 schema 文件"
            }
        
        return {"consistent": True, "message": "Schema 一致"}
        
    except Exception as e:
        return {"error": f"验证失败: {str(e)}"}
```

### 3. **配置化路径**

使用环境变量和配置文件：

```python
import os
from pathlib import Path

class SchemaLoader:
    def __init__(self, schema_file_path: str = None):
        # 支持多种配置方式
        self.schema_file_path = (
            schema_file_path or 
            os.getenv('SCHEMA_FILE_PATH') or 
            Path(__file__).parent.parent / 'reference/schemas/AMEAnalytics_Schema.json'
        )
```

### 4. **缓存策略优化**

实现更智能的缓存机制：

```python
class SchemaCache:
    def __init__(self, cache_ttl: int = 3600):  # 1小时缓存
        self.cache_ttl = cache_ttl
        self._cache = None
        self._cache_timestamp = None
    
    def is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        if not self._cache or not self._cache_timestamp:
            return False
        
        return (datetime.now() - self._cache_timestamp).seconds < self.cache_ttl
    
    async def get_schema(self) -> Dict[str, Any]:
        """获取 schema，优先使用缓存"""
        if self.is_cache_valid():
            return self._cache
        
        # 缓存过期，重新获取
        schema = await self.fetch_fresh_schema()
        self._cache = schema
        self._cache_timestamp = datetime.now()
        
        return schema
```

## 实施建议

### 短期改进（立即可做）
1. 添加配置化路径支持
2. 实现 schema 一致性检查工具
3. 添加错误处理和降级机制

### 中期改进（1-2周）
1. 实现混合 schema 获取方案
2. 添加智能缓存机制
3. 创建 schema 同步工具

### 长期改进（1个月+）
1. 完全动态的 schema 发现
2. 自动化 schema 文件更新
3. 监控和告警机制

## 风险评估

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| Schema 不同步 | 高 | 中 | 实施定期验证和告警 |
| 文件路径依赖 | 中 | 低 | 配置化路径管理 |
| 性能影响 | 低 | 低 | 智能缓存策略 |
| 维护复杂性 | 中 | 中 | 文档化和自动化工具 |

## 结论

当前的 schema 管理方案虽然提供了性能和离线开发的优势，但存在数据同步和维护复杂性的问题。建议采用混合方案，结合动态获取和文件缓存的优点，同时添加一致性验证机制，确保系统的可靠性和可维护性。

---

**文档创建时间**: 2025-09-04  
**分析人员**: AI Assistant  
**项目**: MCP SQL Server - Azure SDK Usage Agent
