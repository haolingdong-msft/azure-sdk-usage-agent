# 使用示例：如何使用新的 generateSQLQueryParams 工具

## 概述

现在您可以使用两种方式来查询数据库：

1. **原有方式**：使用 `aiQueryHelper` 获取 schema 信息，然后手动构建 `executeSQLQuery` 参数
2. **新方式**：使用 `generateSQLQueryParams` 自动生成 `executeSQLQuery` 参数，然后直接执行

## 新的工作流程

### 步骤 1: 生成 SQL 查询参数

```python
# 调用 generateSQLQueryParams
params = await generateSQLQueryParams(
    user_question="Show me the top 10 customers by request count this month",
    schema_hint=""  # 可选
)

# 返回结果示例:
{
    "success": True,
    "table_name": "AMEConciseFiteredNewProductCCIDCustomerSubscriptionId",
    "columns": ["Customer", "RequestCount"],
    "where_clause": "Month LIKE '2025-09%' AND RequestCount > 100",
    "order_clause": "ORDER BY RequestCount DESC", 
    "limit_clause": "TOP 10",
    "confidence": 0.80,
    "explanation": "Based on your question...",
    "user_question": "Show me the top 10 customers by request count this month"
}
```

### 步骤 2: 执行 SQL 查询

```python
# 直接使用生成的参数执行查询
result = await executeSQLQuery(
    table_name=params["table_name"],
    columns=params["columns"],
    where_clause=params["where_clause"],
    order_clause=params["order_clause"],
    limit_clause=params["limit_clause"]
)
```

## 完整示例

### 示例 1: 查找热门产品

```python
# 1. 生成参数
params = await generateSQLQueryParams(
    user_question="What are the most popular Azure SDK products this year?",
    schema_hint="focus on Product table"
)

# 2. 检查置信度
if params["confidence"] > 0.7:
    # 3. 执行查询
    result = await executeSQLQuery(
        table_name=params["table_name"],
        columns=params["columns"],
        where_clause=params["where_clause"],
        order_clause=params["order_clause"],
        limit_clause=params["limit_clause"]
    )
    print("Query Results:", result)
else:
    print("Low confidence, please review parameters:", params["explanation"])
```

### 示例 2: 时间范围查询

```python
# 1. 生成参数
params = await generateSQLQueryParams(
    user_question="Find customers with declining usage in recent months"
)

# 2. 可选：手动调整参数
if params["success"]:
    # 可以手动微调参数
    params["where_clause"] += " AND Customer != 'TestCustomer'"
    
    # 3. 执行查询
    result = await executeSQLQuery(**{
        k: v for k, v in params.items() 
        if k in ["table_name", "columns", "where_clause", "order_clause", "limit_clause"]
    })
```

### 示例 3: 复杂查询

```python
# 对于复杂查询，可以分步骤处理
questions = [
    "Show me Azure Python SDK usage by month",
    "Which customers use the most Azure services?",
    "Find the latest usage trends for .NET SDK"
]

for question in questions:
    print(f"\n📊 Processing: {question}")
    
    # 生成参数
    params = await generateSQLQueryParams(user_question=question)
    
    if params["success"] and params["confidence"] > 0.6:
        # 执行查询
        result = await executeSQLQuery(
            table_name=params["table_name"],
            columns=params["columns"], 
            where_clause=params["where_clause"],
            order_clause=params["order_clause"],
            limit_clause=params["limit_clause"]
        )
        
        print(f"✅ Results found: {len(result.get('data', []))} rows")
        print(f"📋 Explanation: {params['explanation']}")
    else:
        print(f"❌ Low confidence ({params.get('confidence', 0):.2f})")
        print(f"💡 Suggestion: {params.get('explanation', 'N/A')}")
```

## 高级用法

### 使用 Schema 提示

```python
# 当您知道要查询的特定表时
params = await generateSQLQueryParams(
    user_question="Show customer usage data",
    schema_hint="CustomerProductUsage table with focus on monthly data"
)
```

### 置信度检查

```python
def should_execute_query(params):
    """根据置信度决定是否执行查询"""
    confidence = params.get("confidence", 0)
    
    if confidence > 0.8:
        return True, "High confidence - safe to execute"
    elif confidence > 0.6:
        return True, "Medium confidence - review parameters"
    elif confidence > 0.4:
        return False, "Low confidence - manual review required"
    else:
        return False, "Very low confidence - rephrase question"

# 使用示例
params = await generateSQLQueryParams(user_question="complex question here")
should_execute, message = should_execute_query(params)

if should_execute:
    result = await executeSQLQuery(...)
else:
    print(f"Skipping execution: {message}")
```

## 与原有 aiQueryHelper 的对比

| 功能 | aiQueryHelper | generateSQLQueryParams |
|------|---------------|----------------------|
| 返回内容 | Schema 信息和建议 | 可直接执行的 SQL 参数 |
| 使用方式 | 需要手动构建查询参数 | 自动生成查询参数 |
| 适用场景 | 探索 schema，了解数据结构 | 快速生成并执行查询 |
| 输出格式 | 详细的表和列信息 | 结构化的 SQL 参数 |
| 工作流程 | 多步骤手动构建 | 一步生成，直接使用 |

## 最佳实践

1. **先用新工具**: 对于大多数查询，先尝试 `generateSQLQueryParams`
2. **检查置信度**: 低置信度时，考虑使用 `aiQueryHelper` 探索 schema
3. **渐进式查询**: 从简单问题开始，逐步增加复杂性
4. **参数验证**: 重要查询执行前，人工验证生成的参数
5. **错误处理**: 始终检查 `success` 字段和错误信息

## 故障排除

### 常见问题

1. **置信度低**: 尝试使用更具体的问题描述或添加 schema_hint
2. **表选择错误**: 使用 schema_hint 指定正确的表
3. **列名不匹配**: 检查 explanation 中的建议，调整问题措辞
4. **条件过于复杂**: 将复杂查询分解为多个简单查询

### 调试技巧

```python
# 启用详细输出
params = await generateSQLQueryParams(user_question="your question")
print("Debug info:", params.get("debug_info", {}))
print("Full explanation:", params.get("explanation", ""))
```