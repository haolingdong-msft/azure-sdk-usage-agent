# generateSQLQuery 使用指南

## 🎯 简介

`generateSQLQuery` 是一个强大的AI工具，可以将自然语言问题直接转换为数据库查询结果。

## 🚀 基本使用

### 最简单的用法
```python
result = await generateSQLQuery("Show me the top 10 customers")
```

### 带提示的用法
```python
result = await generateSQLQuery(
    user_question="What products are trending?",
    schema_hint="focus on Product usage data"
)
```

## 📊 返回结果结构

```json
{
    "success": true,                    // 是否成功
    "data": [...],                      // 查询结果数据
    "generated_sql": "SELECT ...",      // 生成的SQL查询
    "confidence": 0.85,                 // 置信度 (0-1)
    "row_count": 42,                    // 返回行数
    "explanation": "Based on...",       // 详细解释
    "execution_time": "2.5s",           // 执行时间
    "query_parameters": {...}           // 查询参数详情
}
```

## 💡 示例查询

### 1. 排序和限制
```python
# 获取使用量最高的客户
result = await generateSQLQuery("Show me the top 5 customers by request count")

# 获取最新的数据
result = await generateSQLQuery("Give me the most recent usage data")
```

### 2. 时间范围查询
```python
# 本月数据
result = await generateSQLQuery("What happened this month?")

# 最近几个月的趋势
result = await generateSQLQuery("Show me trends in recent months")
```

### 3. 产品相关查询
```python
# 流行产品
result = await generateSQLQuery("What are the most popular Azure products?")

# 特定产品
result = await generateSQLQuery("Find usage data for Python SDK")
```

### 4. 用户和客户分析
```python
# 活跃用户
result = await generateSQLQuery("Who are the most active customers?")

# 低使用量分析
result = await generateSQLQuery("Find customers with low usage")
```

## 🔧 高级用法

### 使用 Schema 提示
```python
# 指定关注的表
result = await generateSQLQuery(
    "Show customer data",
    schema_hint="CustomerProductUsage table"
)

# 指定关注的列
result = await generateSQLQuery(
    "Analyze usage patterns", 
    schema_hint="focus on Month and RequestCount columns"
)
```

### 置信度检查
```python
result = await generateSQLQuery("complex query here")

if result["confidence"] > 0.8:
    print("高置信度，结果可靠")
    data = result["data"]
elif result["confidence"] > 0.6:
    print("中等置信度，建议检查")
    print(f"生成的SQL: {result['generated_sql']}")
    data = result["data"]
else:
    print("低置信度，建议重新提问")
    print(f"解释: {result['explanation']}")
```

## 📝 最佳实践

### 1. 问题表述
✅ **好的问题**:
- "Show me the top 10 customers by request count"
- "What products were used most this month?"
- "Find customers with declining usage"

❌ **避免的问题**:
- "Data" (太模糊)
- "Everything about customers" (太宽泛)
- "Complex join with multiple conditions" (太复杂)

### 2. 使用提示
```python
# 当你知道要查询的表时
result = await generateSQLQuery(
    "Show usage data",
    schema_hint="AMEConciseSubReqCCIDCountByMonthProductOS table"
)

# 当你想关注特定列时
result = await generateSQLQuery(
    "Analyze patterns",
    schema_hint="focus on Product and Month columns"
)
```

### 3. 结果处理
```python
result = await generateSQLQuery("your question")

if result["success"]:
    print(f"✅ 成功获取 {result['row_count']} 行数据")
    print(f"📊 置信度: {result['confidence']:.2f}")
    
    # 处理数据
    for row in result["data"]:
        print(row)
        
    # 显示生成的SQL（调试用）
    print(f"🔍 SQL: {result['generated_sql']}")
else:
    print(f"❌ 查询失败: {result['error']}")
```

## 🐛 故障排除

### 常见问题

1. **置信度低**
   ```python
   # 尝试更具体的问题
   instead of: "Show data"
   try: "Show customer request counts for this month"
   ```

2. **无数据返回**
   ```python
   # 检查生成的SQL和条件
   print(f"SQL: {result['generated_sql']}")
   print(f"解释: {result['explanation']}")
   ```

3. **结果不符合预期**
   ```python
   # 使用schema提示指导
   result = await generateSQLQuery(
       "your question",
       schema_hint="focus on specific table or columns"
   )
   ```

### 调试技巧

```python
# 获取详细信息进行调试
result = await generateSQLQuery("your question")

print("🔍 调试信息:")
print(f"表名: {result['query_parameters']['table_name']}")
print(f"列名: {result['query_parameters']['columns']}")
print(f"条件: {result['query_parameters']['where_clause']}")
print(f"排序: {result['query_parameters']['order_clause']}")
print(f"限制: {result['query_parameters']['limit_clause']}")
print(f"完整SQL: {result['generated_sql']}")
```

## 🎨 实际应用场景

### 数据分析师
```python
# 快速探索数据
trends = await generateSQLQuery("Show me usage trends by month")
top_products = await generateSQLQuery("What are the top products this quarter?")
```

### 业务用户
```python
# 业务洞察
customer_growth = await generateSQLQuery("How is our customer base growing?")
product_performance = await generateSQLQuery("Which products perform best?")
```

### 开发者
```python
# 快速原型
test_data = await generateSQLQuery("Get some sample customer data")
validation = await generateSQLQuery("Check data quality for recent uploads")
```

## 🔄 与其他工具的协作

### 与 aiQueryHelper 结合
```python
# 先了解schema
schema_info = await aiQueryHelper("customer usage data")

# 然后精确查询
result = await generateSQLQuery(
    "Show customer usage patterns",
    schema_hint=f"use {schema_info['suggested_table']['name']} table"
)
```

### 与 executeSQLQuery 结合
```python
# 对于标准查询，使用 generateSQLQuery
standard_result = await generateSQLQuery("top customers this month")

# 对于精确控制，使用 executeSQLQuery  
precise_result = await executeSQLQuery(
    table_name="specific_table",
    columns=["exact", "columns"],
    where_clause="precise = condition"
)
```

---

🎉 **generateSQLQuery 让数据查询变得简单直观，从自然语言问题到数据结果，一步到位！**