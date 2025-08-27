#!/usr/bin/env python3
"""
详细示例脚本：展示验证优先查询流程的各种用例
"""

import asyncio
import sys
import os
import json

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mssql_query_server import validateQueryMSSQL, mssqlQuery

def print_section(title: str):
    """打印章节标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_subsection(title: str):
    """打印小节标题"""
    print(f"\n{'-'*40}")
    print(f"  {title}")
    print(f"{'-'*40}")

def print_result(query: str, result: dict, show_data: bool = False):
    """格式化打印查询结果"""
    print(f"\n📝 查询: {query}")
    print("=" * min(len(query) + 6, 50))
    
    if result.get('valid', True):  # For validation results
        if 'generated_sql' in result:
            print(f"✅ 验证状态: 通过")
            print(f"🔧 生成的SQL: {result['generated_sql']}")
            print(f"📊 使用表: {result.get('table_used', 'N/A')}")
            print(f"📋 选择列: {', '.join(result.get('columns_selected', []))}")
            
            filters = result.get('filters_applied', 'None')
            if filters and filters != 'None':
                print(f"🔍 过滤条件: {filters}")
            
            ordering = result.get('ordering', 'None')
            if ordering and ordering != 'None':
                print(f"📈 排序: {ordering}")
                
            limit = result.get('limit', 'None')
            if limit and limit != 'None':
                print(f"🔢 限制: {limit}")
        
        elif 'success' in result:  # For actual query results
            print(f"✅ 执行状态: {'成功' if result['success'] else '失败'}")
            print(f"🔧 执行SQL: {result.get('query', 'N/A')}")
            print(f"📊 数据表: {result.get('table_used', 'N/A')}")
            print(f"📝 返回行数: {result.get('row_count', 0)}")
            
            if show_data and result.get('data'):
                print(f"📋 示例数据 (前3行):")
                for i, row in enumerate(result['data'][:3]):
                    print(f"   {i+1}. {row}")
            
            if 'validation_info' in result:
                val_info = result['validation_info']
                print(f"🔍 验证信息: 预验证={val_info.get('pre_validated', False)}")
    else:
        print(f"❌ 验证状态: 失败")
        print(f"💥 错误: {result.get('error', 'Unknown error')}")
        if 'suggestions' in result:
            print(f"💡 建议:")
            for suggestion in result['suggestions']:
                print(f"   • {suggestion}")

async def demo_validation_only():
    """演示验证功能（不执行实际查询）"""
    print_section("🔍 第一部分：查询验证演示")
    print("展示验证优先流程的第一步：SQL生成和验证")
    
    validation_examples = [
        # 基础查询
        ("基础查询", [
            "Show me request counts for Go-SDK",
            "What are the top 10 products by usage?",
            "How many requests were made this month?",
        ]),
        
        # 时间过滤查询
        ("时间过滤查询", [
            "Show me Go-SDK data for this month",
            "Python-SDK usage in 2024-01",
            "Request counts in 2024",
        ]),
        
        # 复杂过滤查询
        ("复杂过滤查询", [
            "Top 5 products with more than 1000 requests",
            "Windows users of Python-SDK this month",
            "POST requests for Java SDK",
        ]),
        
        # 可能失败的查询
        ("边界情况", [
            "Invalid nonsense query",
            "Show me data for non-existent product",
            "Random words without context",
        ])
    ]
    
    for category, queries in validation_examples:
        print_subsection(f"📂 {category}")
        
        for query in queries:
            try:
                result = await validateQueryMSSQL(query)
                print_result(query, result)
            except Exception as e:
                print(f"\n📝 查询: {query}")
                print(f"💥 异常: {str(e)}")

async def demo_query_categories():
    """演示不同类别的查询示例"""
    print_section("📊 第二部分：查询类别演示")
    print("展示各种类型查询的SQL生成结果")
    
    query_categories = {
        "Go SDK 专用查询": [
            "Show me Go SDK request counts by package",
            "Go SDK subscription counts this month",
            "Track 2 Go SDK usage",
        ],
        
        "产品对比查询": [
            "Compare Python-SDK vs Java-SDK usage",
            "Top 10 products by request count",
            "Least used Azure SDK products",
        ],
        
        "操作系统分析": [
            "Windows vs Linux SDK usage",
            "MacOS users of JavaScript SDK",
            "OS distribution for Python-SDK",
        ],
        
        "HTTP方法分析": [
            "GET vs POST request distribution",
            "PUT operations by product",
            "HTTP methods for .Net SDK",
        ],
        
        "时间序列分析": [
            "Monthly request trends for 2024",
            "This month vs last month comparison",
            "Request growth over time",
        ]
    }
    
    for category, queries in query_categories.items():
        print_subsection(f"🏷️ {category}")
        
        for query in queries:
            try:
                result = await validateQueryMSSQL(query)
                print_result(query, result)
            except Exception as e:
                print(f"\n📝 查询: {query}")
                print(f"💥 异常: {str(e)}")

async def demo_sql_features():
    """演示SQL特性识别"""
    print_section("🔧 第三部分：SQL特性识别演示")
    print("展示系统如何识别和处理不同的SQL特性")
    
    feature_examples = {
        "TOP N 查询": [
            "Show me top 5 products",
            "Bottom 3 performing SDKs",
            "First 10 records",
        ],
        
        "WHERE 条件": [
            "Products with more than 1000 requests",
            "Subscriptions with less than 100 requests", 
            "Exactly 500 requests",
        ],
        
        "时间范围": [
            "Data from 2024-01-01",
            "This month data",
            "January 2024 requests",
        ],
        
        "排序识别": [
            "Highest request counts first",
            "Oldest to newest data",
            "Ascending order by name",
        ]
    }
    
    for feature, queries in feature_examples.items():
        print_subsection(f"⚙️ {feature}")
        
        for query in queries:
            try:
                result = await validateQueryMSSQL(query)
                print_result(query, result)
            except Exception as e:
                print(f"\n📝 查询: {query}")
                print(f"💥 异常: {str(e)}")

async def demo_error_handling():
    """演示错误处理和建议系统"""
    print_section("🚨 第四部分：错误处理演示")
    print("展示系统如何处理无效查询并提供建议")
    
    error_examples = [
        "This is complete nonsense",
        "Show me unicorn data",
        "Delete all records",  # Should be blocked
        "",  # Empty query
        "?????",  # Special characters
    ]
    
    for query in error_examples:
        try:
            result = await validateQueryMSSQL(query)
            print_result(query, result)
        except Exception as e:
            print(f"\n📝 查询: {query}")
            print(f"💥 异常: {str(e)}")

async def demo_performance_comparison():
    """演示性能对比：验证 vs 直接执行"""
    print_section("⚡ 第五部分：性能优势演示")
    print("对比验证优先 vs 传统直接执行的性能差异")
    
    test_queries = [
        "Invalid query that would fail",
        "Show me nonexistent table data",
        "Query with syntax errors",
    ]
    
    print_subsection("🔍 验证优先流程（快速失败）")
    
    import time
    
    for query in test_queries:
        start_time = time.time()
        try:
            result = await validateQueryMSSQL(query)
            end_time = time.time()
            print(f"\n📝 查询: {query}")
            print(f"⏱️ 验证耗时: {(end_time - start_time)*1000:.2f}ms")
            print(f"🎯 结果: {'通过' if result.get('valid') else '失败（未连接数据库）'}")
            if not result.get('valid'):
                print(f"💡 快速反馈: {result.get('error', 'N/A')}")
        except Exception as e:
            end_time = time.time()
            print(f"\n📝 查询: {query}")
            print(f"⏱️ 验证耗时: {(end_time - start_time)*1000:.2f}ms")
            print(f"💥 异常: {str(e)}")

def create_summary_report():
    """创建功能总结报告"""
    print_section("📋 第六部分：功能总结报告")
    
    summary = {
        "✅ 验证优先流程优势": [
            "🚀 快速失败：无效查询立即返回，无需连接数据库",
            "💡 智能建议：提供具体的查询改进建议",
            "🔧 SQL预览：显示生成的SQL语句供用户确认",
            "📊 详细分析：展示表选择、列选择、过滤条件等详情",
            "⚡ 性能优化：避免无效的网络连接和认证请求"
        ],
        
        "🎯 支持的查询特性": [
            "📈 TOP N 查询：自动识别并转换为SQL LIMIT",
            "🔍 智能过滤：支持时间、产品、OS、HTTP方法等过滤",
            "📊 多表支持：根据查询内容智能选择最相关的表",
            "🏷️ 枚举识别：自动匹配产品名、Track信息等枚举值",
            "📅 时间解析：支持多种时间格式和相对时间表达"
        ],
        
        "🛡️ 安全和稳定性": [
            "🔒 SQL注入防护：预先验证和过滤危险操作",
            "✅ 语法检查：确保生成的SQL语法正确",
            "🎛️ 权限控制：只允许SELECT查询",
            "📝 详细日志：完整的处理步骤记录",
            "🔄 错误恢复：提供清晰的错误信息和解决建议"
        ],
        
        "🔧 技术实现亮点": [
            "🧠 智能解析：基于NLP的查询意图识别",
            "📊 表评分系统：多维度评分选择最佳表",
            "🎯 列映射：基于查询内容智能选择相关列",
            "⚙️ 条件构建：自动构建复杂的WHERE条件",
            "📈 排序识别：识别用户的排序意图"
        ]
    }
    
    for category, items in summary.items():
        print_subsection(category)
        for item in items:
            print(f"  {item}")

async def main():
    """主函数：运行所有演示"""
    print("🎉 MCP SQL Server - 验证优先查询流程完整演示")
    print("=" * 60)
    print("本演示将展示新的验证优先流程的各种功能和优势")
    
    try:
        # 运行各个演示部分
        await demo_validation_only()
        await demo_query_categories()
        await demo_sql_features()
        await demo_error_handling()
        await demo_performance_comparison()
        create_summary_report()
        
        print_section("🎊 演示完成")
        print("✅ 所有功能演示已完成！")
        print("📖 查看 README_VALIDATION_FLOW.md 了解更多详细信息")
        print("🚀 开始使用验证优先的查询流程，享受更快速、更可靠的数据查询体验！")
        
    except Exception as e:
        print(f"\n💥 演示过程中发生错误: {str(e)}")
        print("请检查环境配置和依赖安装")

if __name__ == "__main__":
    asyncio.run(main())
