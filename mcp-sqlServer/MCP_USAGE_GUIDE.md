# MCP Kusto 查询服务使用指南

## 🚨 重要提醒

当用户请求生成 KQL 查询时：

1. **直接使用 MCP 工具**，不要先查看 schema 文件
2. **优先级**：MCP 工具 > 静态文件分析
3. **当前启用的服务**：`main_kusto.py` (不依赖 AMEAnalytics_Schema.json)

## 可用的 MCP 工具

- `modifyKustoQuery()` - 生成/修改 KQL 查询
- `validateKustoSyntax()` - 验证 KQL 语法
- `explainKustoQuery()` - 解释 KQL 查询

## 正确的工作流程

```
用户查询请求 → 直接调用 MCP 工具 → 返回结果
```

**❌ 错误做法：**
```
用户查询请求 → 查看 schema.json → 分析结构 → 再考虑 MCP
```

## 架构说明

- `mcp_tools.py` - SQL Server MCP (需要 schema.json)
- `mcp_tools_kusto.py` - Kusto MCP (独立，不需要 schema.json)
- 当前启用：Kusto MCP

---
创建日期：2025-09-04
目的：避免重复的行为模式问题
