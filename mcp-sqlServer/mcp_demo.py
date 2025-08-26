#!/usr/bin/env python3
"""
演示如何直接调用 MCP sqlQuery 工具来查询 Python SDK 使用情况
这个脚本展示了 MCP 工具的正确调用方式
"""

import asyncio
import json

def mock_sqlQuery_tool():
    """
    模拟 MCP sqlQuery 工具的行为
    这展示了工具如何解析自然语言查询并生成 SQL
    """
    
    # 模拟用户问题
    user_questions = [
        "Show Python-SDK usage this month",
        "Show top 10 products by request count", 
        "What is Track1 vs Track2 usage for Python-SDK?",
        "Show Python-SDK usage by operating system",
        "Which providers are most used with Python-SDK?"
    ]
    
    print("🚀 MCP sqlQuery 工具演示")
    print("=" * 70)
    
    for i, question in enumerate(user_questions, 1):
        print(f"\n📝 查询 {i}: {question}")
        print("-" * 50)
        
        # 根据问题类型生成相应的查询结果
        if "this month" in question and "Python-SDK" in question:
            result = {
                "success": True,
                "query": "SELECT Month, Product, RequestCount, SubscriptionCount FROM AMEConciseSubReqCCIDCountByMonthProduct WHERE Product = 'Python-SDK' AND Month LIKE '2025-08%' ORDER BY RequestCount DESC",
                "table_used": "AMEConciseSubReqCCIDCountByMonthProduct",
                "explanation": "查询 Python-SDK 在2025年8月的使用情况",
                "mock_data": [
                    {"Month": "2025-08-01", "Product": "Python-SDK", "RequestCount": 15420, "SubscriptionCount": 892},
                    {"Month": "2025-08-15", "Product": "Python-SDK", "RequestCount": 12850, "SubscriptionCount": 756}
                ],
                "row_count": 2
            }
            
        elif "top 10" in question and "products" in question:
            result = {
                "success": True,
                "query": "SELECT TOP 10 Product, RequestCount, SubscriptionCount FROM AMEConciseSubReqCCIDCountByMonthProduct WHERE Month LIKE '2025-08%' ORDER BY RequestCount DESC",
                "table_used": "AMEConciseSubReqCCIDCountByMonthProduct", 
                "explanation": "查询请求量最高的前10个产品",
                "mock_data": [
                    {"Product": "AzureCLI", "RequestCount": 45230, "SubscriptionCount": 2156},
                    {"Product": "AzurePowershell", "RequestCount": 38920, "SubscriptionCount": 1834},
                    {"Product": "Python-SDK", "RequestCount": 28270, "SubscriptionCount": 1648},
                    {"Product": "JavaScript", "RequestCount": 22150, "SubscriptionCount": 1423}
                ],
                "row_count": 10
            }
            
        elif "Track1 vs Track2" in question and "Python-SDK" in question:
            result = {
                "success": True,
                "query": "SELECT TrackInfo, RequestCount, SubscriptionCount FROM AMEConciseSubReqCCIDCountByMonthProductTrackInfo WHERE Product = 'Python-SDK' AND Month LIKE '2025-08%' ORDER BY RequestCount DESC",
                "table_used": "AMEConciseSubReqCCIDCountByMonthProductTrackInfo",
                "explanation": "比较 Python-SDK 的 Track1 和 Track2 使用情况",
                "mock_data": [
                    {"TrackInfo": "Track2", "RequestCount": 18760, "SubscriptionCount": 1124},
                    {"TrackInfo": "Track1", "RequestCount": 9510, "SubscriptionCount": 524}
                ],
                "row_count": 2
            }
            
        elif "operating system" in question and "Python-SDK" in question:
            result = {
                "success": True,
                "query": "SELECT OS, RequestCount, SubscriptionCount FROM AMEConciseSubReqCCIDCountByMonthProductOS WHERE Product = 'Python-SDK' AND Month LIKE '2025-08%' ORDER BY RequestCount DESC",
                "table_used": "AMEConciseSubReqCCIDCountByMonthProductOS",
                "explanation": "按操作系统统计 Python-SDK 使用情况", 
                "mock_data": [
                    {"OS": "Linux", "RequestCount": 12840, "SubscriptionCount": 756},
                    {"OS": "Windows", "RequestCount": 10230, "SubscriptionCount": 634},
                    {"OS": "MacOS", "RequestCount": 5200, "SubscriptionCount": 258}
                ],
                "row_count": 3
            }
            
        elif "providers" in question and "Python-SDK" in question:
            result = {
                "success": True,
                "query": "SELECT Provider, RequestCount, SubscriptionCount FROM AMEConciseSubReqCCIDCountByMonthProductProviderTrackInfo WHERE Product = 'Python-SDK' AND Month LIKE '2025-08%' ORDER BY RequestCount DESC",
                "table_used": "AMEConciseSubReqCCIDCountByMonthProductProviderTrackInfo",
                "explanation": "统计 Python-SDK 最常用的 Azure 服务提供商",
                "mock_data": [
                    {"Provider": "Microsoft.Compute", "RequestCount": 8420, "SubscriptionCount": 467},
                    {"Provider": "Microsoft.Storage", "RequestCount": 6780, "SubscriptionCount": 389},
                    {"Provider": "Microsoft.Network", "RequestCount": 4520, "SubscriptionCount": 312},
                    {"Provider": "Microsoft.Web", "RequestCount": 3890, "SubscriptionCount": 256}
                ],
                "row_count": 4
            }
        
        # 打印结果
        if result["success"]:
            print(f"✅ 查询成功")
            print(f"📊 使用表: {result['table_used']}")
            print(f"📈 返回行数: {result['row_count']}")
            print(f"🔍 生成的SQL:")
            print(f"   {result['query']}")
            print(f"📝 说明: {result['explanation']}")
            print(f"📋 模拟数据:")
            for row in result['mock_data']:
                print(f"   {row}")
        else:
            print(f"❌ 查询失败: {result.get('error', '未知错误')}")

def show_mcp_tool_interface():
    """展示 MCP 工具的接口定义"""
    
    print("\n" + "=" * 70)
    print("🔧 MCP sqlQuery 工具接口")
    print("=" * 70)
    
    tool_definition = {
        "name": "sqlQuery",
        "description": "Execute a SQL query based on a natural language question about SQL Server data",
        "inputSchema": {
            "type": "object",
            "properties": {
                "request": {
                    "type": "string",
                    "description": "A natural language question about the data (e.g., 'Show me the top 10 customers by request count', 'What products were used in 2024-01?', 'Which customers have more than 1000 requests?')"
                }
            },
            "required": ["request"]
        }
    }
    
    print("📋 工具定义:")
    print(json.dumps(tool_definition, indent=2, ensure_ascii=False))
    
    print("\n💡 调用示例:")
    print("```python")
    print('# 异步调用 MCP 工具')
    print('result = await sqlQuery("Show Python-SDK usage this month")')
    print('print(result)')
    print("```")

def show_actual_usage():
    """展示实际使用场景"""
    
    print("\n" + "=" * 70)
    print("🎯 实际使用场景")
    print("=" * 70)
    
    scenarios = [
        {
            "scenario": "产品经理查看SDK采用情况",
            "query": "Show Python-SDK vs Java SDK usage trends this year",
            "benefit": "了解不同语言SDK的市场接受度"
        },
        {
            "scenario": "开发团队分析迁移进度", 
            "query": "What is Track1 to Track2 migration status for all products?",
            "benefit": "跟踪从旧版本到新版本的迁移情况"
        },
        {
            "scenario": "服务团队优化资源配置",
            "query": "Which Azure providers have highest usage with Python-SDK?",
            "benefit": "识别热门服务，优化资源分配"
        },
        {
            "scenario": "用户体验团队分析平台分布",
            "query": "Show Python-SDK usage by operating system this month", 
            "benefit": "了解用户平台偏好，优化跨平台支持"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['scenario']}")
        print(f"   🔍 查询: {scenario['query']}")
        print(f"   💼 价值: {scenario['benefit']}")

if __name__ == "__main__":
    # 演示 MCP 工具调用
    mock_sqlQuery_tool()
    
    # 展示工具接口
    show_mcp_tool_interface()
    
    # 展示实际使用场景
    show_actual_usage()
    
    print("\n" + "=" * 70)
    print("✨ 总结")
    print("=" * 70)
    print("🎯 MCP sqlQuery 工具的优势:")
    print("  1. 自然语言查询 - 无需学习复杂的SQL语法")
    print("  2. 智能表选择 - 自动选择最合适的数据表")
    print("  3. 动态过滤 - 根据查询意图生成过滤条件")
    print("  4. 结果优化 - 自动排序和限制返回结果")
    print("  5. 错误处理 - 提供友好的错误信息和建议")
    print("\n🚀 要执行实际查询，需要:")
    print("  1. 配置数据库连接")
    print("  2. 安装 ODBC 驱动")
    print("  3. 设置 Azure 认证")
    print("  4. 调用: await sqlQuery('Your question here')")
