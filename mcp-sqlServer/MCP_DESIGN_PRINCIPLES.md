# MCP工具设计原则

## 正确的MCP设计 ✅

MCP (Model Context Protocol) 工具应该：

### 1. **提供结构化数据**
```python
# ✅ 正确：返回结构化数据给AI助手
return {
    "success": True,
    "original_kql": original_kql,
    "user_question": user_question,
    "ai_prompt": ai_prompt,
    "instructions": {...},
    "context": {...}
}
```

### 2. **不直接调用AI API**
```python
# ❌ 错误：MCP工具内部调用AI API
ai_response = await openai.ChatCompletion.acreate(...)

# ✅ 正确：准备AI提示，让调用方处理
ai_prompt = self._generate_ai_prompt(original_kql, user_question)
return {"ai_prompt": ai_prompt, ...}
```

### 3. **职责分离**
- **MCP工具职责**：
  - 数据预处理
  - 格式验证
  - 生成结构化提示
  - 提供上下文信息

- **AI助手职责**：
  - 处理AI提示
  - 调用AI API
  - 解析AI响应
  - 格式化最终结果

## 修改后的工作流程

```
用户请求 → MCP工具 → AI助手 → 用户
    ↓         ↓         ↓
  输入    结构化数据   AI处理
```

### 详细流程：

1. **用户输入**：
   ```
   原始KQL查询 + 修改需求
   ```

2. **MCP工具处理**：
   ```python
   {
     "success": True,
     "ai_prompt": "你是KQL专家，请修改...",
     "instructions": {
       "task": "modify_kusto_query",
       "expected_format": {...}
     },
     "context": {
       "original_query_length": 23,
       "modification_request": "只显示Python SDK数据"
     }
   }
   ```

3. **AI助手处理**：
   - 接收MCP工具返回的数据
   - 使用AI提示调用AI API
   - 解析AI响应并格式化

4. **返回给用户**：
   ```
   修改后的KQL查询 + 修改说明
   ```

## 优势

### 🎯 **明确职责**
- MCP工具专注数据处理
- AI助手专注AI交互

### 🔧 **易于维护**
- 修改AI逻辑不需要改MCP工具
- MCP工具更稳定可靠

### 🚀 **更好性能**
- MCP工具无外部API依赖
- 减少网络请求链

### 💰 **成本控制**
- AI调用由调用方控制
- 更好的使用量监控

## 示例对比

### ❌ 错误设计
```python
class MCPTool:
    async def process(self, data):
        # 错误：MCP工具内部调用AI
        ai_result = await openai.call(data)
        return ai_result
```

### ✅ 正确设计
```python
class MCPTool:
    async def process(self, data):
        # 正确：准备数据，让调用方处理AI
        prompt = self.prepare_prompt(data)
        return {
            "ai_prompt": prompt,
            "instructions": {...},
            "context": {...}
        }
```

## 总结

修改后的 `ModifyKustoQuerySimple` 遵循了正确的MCP设计原则：
- ✅ 提供结构化的AI提示
- ✅ 不直接调用AI API  
- ✅ 让AI助手处理实际的AI交互
- ✅ 职责清晰分离

这样的设计更符合MCP协议的设计理念，也更适合在实际项目中使用。
