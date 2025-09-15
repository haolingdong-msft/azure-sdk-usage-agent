# generateSQLQueryParams Tool Usage Guide

## 功能描述 (Function Description)

`generateSQLQueryParams` 工具可以根据用户的自然语言问题和可选的 schema 提示，生成执行 `executeSQLQuery` 所需的参数。

The `generateSQLQueryParams` tool generates the parameters needed for `executeSQLQuery` based on a user's natural language question and optional schema hints.

## 输入参数 (Input Parameters)

- `user_question` (required): 用户的自然语言问题
- `schema_hint` (optional): 可选的 schema 提示，用于指定特定的表或字段

## 输出结果 (Output Result)

返回包含以下字段的 JSON 对象：

- `table_name`: 建议的表名
- `columns`: 建议的列名列表
- `where_clause`: 建议的 WHERE 条件（可选）
- `order_clause`: 建议的 ORDER BY 条件（可选）
- `limit_clause`: 建议的 LIMIT/TOP 条件（可选）
- `confidence`: 建议的置信度评分 (0-1)
- `explanation`: 人类可读的参数解释

## 使用示例 (Usage Examples)

### 示例 1: 基本查询
```json
{
  "user_question": "Show me the top 10 customers by request count this month"
}
```

预期输出：
```json
{
  "table_name": "CustomerProductUsage",
  "columns": ["Customer", "RequestCount"],
  "where_clause": "Month LIKE '2025-09%'",
  "order_clause": "ORDER BY RequestCount DESC",
  "limit_clause": "TOP 10",
  "confidence": 0.85,
  "explanation": "Based on your question 'Show me the top 10 customers by request count this month':\n• Selected table: CustomerProductUsage\n• Suggested columns: Customer, RequestCount\n• Filter conditions: Month LIKE '2025-09%'\n• Sorting: ORDER BY RequestCount DESC\n• Result limit: TOP 10\n• Confidence: High"
}
```

### 示例 2: 带 Schema 提示的查询
```json
{
  "user_question": "What products are most popular?",
  "schema_hint": "focus on ProductUsage table"
}
```

### 示例 3: 复杂查询
```json
{
  "user_question": "Find customers using Azure SDK with more than 1000 requests in recent months"
}
```

## 工作流程 (Workflow)

1. **表选择**: 首先根据 schema_hint 或问题内容确定目标表
2. **列分析**: 分析问题意图，确定需要查询的列
3. **条件生成**: 根据时间、数量等关键词生成 WHERE 条件
4. **排序生成**: 识别排序需求，生成 ORDER BY 子句
5. **限制生成**: 识别数量限制，生成 TOP/LIMIT 子句
6. **置信度评估**: 计算参数建议的置信度
7. **解释生成**: 生成人类可读的解释

## 关键词映射 (Keyword Mapping)

### 列映射 (Column Mapping)
- `count`, `number`, `requests` → `RequestCount`
- `product`, `tool`, `sdk` → `Product`
- `customer`, `user` → `Customer`
- `month`, `time`, `date`, `when` → `Month`
- `region`, `location` → `Region`

### 时间条件 (Time Conditions)
- `this month` → `Month LIKE 'YYYY-MM%'`
- `recent`, `latest` → `Month >= DATEADD(month, -3, GETDATE())`
- `last month` → `Month >= DATEADD(month, -1, GETDATE())`

### 排序条件 (Sorting Conditions)
- `top`, `highest`, `most` → `ORDER BY RequestCount DESC`
- `bottom`, `lowest`, `least` → `ORDER BY RequestCount ASC`
- `recent`, `latest` → `ORDER BY Month DESC`

### 限制条件 (Limit Conditions)
- `top N`, `first N` → `TOP N`
- 默认限制词 → `TOP 10`

## 最佳实践 (Best Practices)

1. **明确问题**: 提供清晰、具体的问题描述
2. **使用提示**: 当需要特定表时，使用 `schema_hint` 参数
3. **检查置信度**: 低置信度时，请检查并调整生成的参数
4. **结合使用**: 将生成的参数直接用于 `executeSQLQuery` 工具

## 注意事项 (Notes)

- 工具会尝试智能推断最合适的参数，但可能需要人工调整
- 置信度低于 0.5 时，建议手动检查参数
- 复杂查询可能需要多次迭代优化
- 支持中英文问题输入