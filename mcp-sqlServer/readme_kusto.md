# Kusto Query Modifier MCP Server

基于MCP (Model Context Protocol) 的Kusto查询修改服务器，支持根据用户自然语言问题智能修改已有的Kusto查询。

## 🚀 功能特性

- **智能查询修改**: 根据用户问题自动修改Kusto查询
- **保持结构完整**: 只修改必要部分，保持原始查询结构
- **中英文支持**: 支持中文和英文用户问题
- **多种修改类型**: 支持时间范围、过滤条件、结果限制等修改
- **合法输出**: 输出的查询可直接在Kusto环境中执行

## 📋 支持的修改类型

### 1. 时间范围修改
- **过去7天**: "过去7天的数据", "last 7 days", "past week"
- **过去30天**: "过去30天的数据", "last 30 days", "past month"  
- **过去24小时**: "过去24小时", "last 24 hours", "past day"
- **过去3个月**: "过去3个月", "last 3 months"

### 2. 产品/SDK过滤
- **Python SDK**: "只显示Python SDK的数据", "只要Python相关的"
- **Java SDK**: "只要Java相关的数据", "Java SDK数据"
- **.NET SDK**: ".NET相关数据", "C#数据"
- **JavaScript SDK**: "JavaScript数据", "JS相关"

### 3. 操作系统过滤
- **Windows**: "只显示Windows数据"
- **Linux**: "只显示Linux数据"

### 4. 结果限制
- **Top N**: "显示前10个结果", "top 10", "前5个最高的"
- **Bottom N**: "显示后10个结果", "bottom 10", "最低的5个"

### 5. 分组修改
- **按产品分组**: "按产品分组", "group by product"
- **按提供商分组**: "按provider分组", "group by provider"
- **按操作系统分组**: "按OS分组", "group by operating system"

## 🛠️ 安装和使用

### 环境要求
- Python 3.8+
- FastMCP库
- 相关依赖包

### 启动服务器
```bash
# 启动Kusto MCP服务器
python -m src.mains.main_kusto
```

### MCP工具调用

#### 1. 修改Kusto查询
```python
await modifyKustoQuery(
    original_kql="<原始KQL查询>",
    user_question="只显示Python SDK的数据"
)
```

#### 2. 验证查询语法
```python
await validateKustoSyntax(
    kql_query="<要验证的KQL查询>"
)
```

#### 3. 解释查询功能
```python
await explainKustoQuery(
    kql_query="<要解释的KQL查询>"
)
```

## 📝 使用示例

### 示例1: 添加产品过滤
**用户问题**: "只显示Python SDK的数据"

**原始查询**:
```kusto
Unionizer("Requests", "HttpIncomingRequests")
| where TIMESTAMP >= startDateTime and TIMESTAMP < endDateTime
| extend Product = GetProduct(userAgent)
| where isnotnull(Product) and isnotempty(Product)
| summarize counts = count() by subscriptionId, Product
```

**修改后查询**:
```kusto
Unionizer("Requests", "HttpIncomingRequests")
| where TIMESTAMP >= startDateTime and TIMESTAMP < endDateTime
| extend Product = GetProduct(userAgent)
| where isnotnull(Product) and isnotempty(Product)
| where Product == "Python-SDK"
| summarize counts = count() by subscriptionId, Product
```

### 示例2: 修改时间范围
**用户问题**: "过去7天的数据"

**修改前**:
```kusto
let startDateTime = datetime_add("day", -15, currentDateTime);
let endDateTime = datetime_add("minute", 30, startDateTime);
```

**修改后**:
```kusto
let startDateTime = datetime_add("day", -7, currentDateTime);
let endDateTime = currentDateTime;
```

### 示例3: 添加结果限制
**用户问题**: "显示前10个结果按计数排序"

**在project语句前添加**:
```kusto
| top 10 by counts desc
```

## 🧪 测试

### 运行完整测试
```bash
cd /path/to/mcp-sqlServer
PYTHONPATH=$(pwd) python tests/testKustoQueryModify.py
```

### 运行简单测试
```bash
PYTHONPATH=$(pwd) python tests/simple_kql_test.py
```

### 运行演示
```bash
PYTHONPATH=$(pwd) python tests/demo_kusto_modify.py
```

## 📂 文件结构

```
mcp-sqlServer/
├── src/
│   ├── mains/
│   │   ├── __init__.py
│   │   ├── main.py              # SQL MCP服务器主入口
│   │   ├── main_kusto.py        # Kusto MCP服务器主入口
│   │   └── main_with_ai.py      # AI辅助SQL MCP服务器入口
│   ├── mcp_tools.py             # MCP工具实现（包含modify_kusto_query）
│   ├── config.py                # 配置文件
│   └── ...
├── tests/
│   ├── testKustoQueryModify.py  # 完整功能测试
│   ├── demo_kusto_modify.py     # 演示脚本
│   └── simple_kql_test.py       # 简单测试
├── reference/
│   └── samples/
│       └── sample.kql           # 示例Kusto查询
└── readme_kusto.md             # 本文档
```

## 🔧 核心实现

### modify_kusto_query 函数
位于 `src/mcp_tools.py`，主要功能：

1. **用户问题分析**: 解析自然语言问题确定修改类型
2. **时间范围修改**: 修改startDateTime和endDateTime变量
3. **过滤条件添加**: 在适当位置添加where子句
4. **结果排序限制**: 添加top/bottom子句
5. **分组修改**: 修改summarize语句的分组字段

### 关键Helper函数
- `_modify_time_range()`: 修改时间范围
- `_add_product_filter()`: 添加产品过滤
- `_add_os_filter()`: 添加操作系统过滤
- `_add_top_limit()`: 添加结果限制
- `_modify_grouping()`: 修改分组字段

## 💡 使用建议

1. **保持查询格式**: 确保原始查询有标准的Kusto格式
2. **明确用户需求**: 使用具体的问题描述，如"前10个"而不是"一些"
3. **验证输出**: 建议使用validateKustoSyntax验证修改后的查询
4. **测试执行**: 在实际Kusto环境中测试修改后的查询

## 🚨 注意事项

- 修改功能基于模式匹配，复杂查询可能需要手动调整
- 某些高级KQL功能可能不被完全支持
- 建议在生产环境使用前充分测试修改后的查询
- 中文问题识别基于关键词匹配，可能需要使用标准表达

## 📊 API响应格式

### 成功响应
```json
{
    "success": true,
    "modified_kql": "<修改后的KQL查询>",
    "original_question": "<用户原始问题>",
    "modifications_applied": ["添加的修改类型列表"]
}
```

### 错误响应
```json
{
    "success": false,
    "error": "<错误描述>",
    "original_kql": "<原始查询>",
    "user_question": "<用户问题>"
}
```

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个工具。

## 📄 许可证

请参考项目根目录的LICENSE文件。
