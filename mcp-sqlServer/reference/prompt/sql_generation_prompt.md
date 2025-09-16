# SQL查询生成Prompt

## 任务
根据用户的自然语言问题和数据库schema，生成一个可执行的SQL查询。

## 输入
- 用户问题: {user_question}
- Schema提示: {schema_hint}
- 可用表信息: {available_tables}
- 表结构详情: {table_details}

## 输出格式
请返回JSON格式的结果:
```json
{
    "table_name": "选择的表名",
    "columns": ["列名1", "列名2"],
    "where_clause": "WHERE条件 (可选)",
    "order_clause": "ORDER BY子句 (可选)", 
    "limit_clause": "TOP N 或 LIMIT N (可选)",
    "confidence": 0.85,
    "explanation": "查询逻辑的详细解释"
}
```

## 分析步骤
1. 分析用户问题的意图
2. 根据schema提示和可用表选择最合适的表
3. 根据问题意图选择需要的列
4. 生成适当的WHERE条件
5. 确定是否需要排序和限制
6. 评估查询的置信度

## 示例

### 输入:
- 用户问题: "Show me the top 10 customers by request count"
- Schema提示: ""
- 可用表: [{"name": "CustomerUsage", "description": "Customer usage data"}]

### 输出:
```json
{
    "table_name": "CustomerUsage",
    "columns": ["Customer", "RequestCount"],
    "where_clause": "",
    "order_clause": "ORDER BY RequestCount DESC",
    "limit_clause": "TOP 10", 
    "confidence": 0.9,
    "explanation": "查询客户使用量最高的前10名客户，按请求数量降序排列"
}
```

## 注意事项
- 优先考虑schema提示中的指导
- 确保选择的列存在于目标表中
- WHERE条件要符合数据类型要求
- 时间条件使用适当的SQL函数
- 置信度基于表选择准确性、列匹配度、条件合理性等因素