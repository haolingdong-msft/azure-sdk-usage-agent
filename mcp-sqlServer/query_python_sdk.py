#!/usr/bin/env python3
"""
直接调用 MCP sqlQuery 工具来查询 Python SDK 使用情况
"""

import asyncio
import json
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入 sqlQuery 工具，但不导入依赖 pyodbc 的部分
def load_schema_only():
    """只加载 schema，不连接数据库"""
    import json
    schema_file = os.path.join(os.path.dirname(__file__), 'fixture', 'tables_and_columns.json')
    with open(schema_file, 'r') as f:
        return json.load(f)

def simulate_python_sdk_query():
    """模拟查询 Python SDK 本月使用情况的 SQL 生成"""
    
    # 加载表结构
    schema_data = load_schema_only()
    
    # 用户问题：查询 Python SDK 本月使用情况
    user_question = "Show Python-SDK usage this month"
    
    print(f"用户问题: {user_question}")
    print("=" * 50)
    
    try:
        # 直接实现查询解析逻辑，避免导入有依赖的模块
        
        # 1. 查找合适的表
        # 对于 Python SDK 使用情况，我们选择包含产品信息的表
        table_name = "AMEConciseSubReqCCIDCountByMonthProduct"  # 按月份和产品统计
        
        # 2. 选择相关列
        columns = ["Month", "Product", "RequestCount", "SubscriptionCount"]
        
        # 3. 构建 WHERE 条件
        # 当前是 2025年8月，所以查询 2025-08-01
        where_conditions = ["Product = 'Python-SDK'", "Month LIKE '2025-08%'"]
        where_clause = " AND ".join(where_conditions)
        
        # 4. 添加排序
        order_clause = "ORDER BY RequestCount DESC"
        
        # 构建 SQL 查询
        columns_str = ', '.join(columns)
        sql_query = f"SELECT {columns_str} FROM {table_name} WHERE {where_clause} {order_clause}"
        
        print("✅ 查询解析成功!")
        print(f"📊 使用的表: {table_name}")
        print(f"🔍 选择的列: {', '.join(columns)}")
        print(f"📝 过滤条件: {where_clause}")
        print(f"📈 排序: {order_clause}")
        print()
        print("🚀 生成的 SQL 查询:")
        print(sql_query)
        print()
        
        # 显示查询说明
        print("📖 查询说明:")
        print("- 这个查询会显示 Python-SDK 在本月(2025年8月)的使用情况")
        print("- 包含月份、产品名称、请求计数和订阅计数")
        print("- 按请求计数降序排列，显示最活跃的使用情况")
        
        # 显示可用的产品列表（从 schema 获取）
        products = schema_data['definitions']['Product']['enum']
        print("\n📋 可用的产品列表:")
        for i, product in enumerate(products, 1):
            marker = "👉" if product == "Python-SDK" else "  "
            print(f"{marker} {i:2d}. {product}")
        
        # 创建查询信息字典
        query_info = {
            'table_name': table_name,
            'columns': columns,
            'where_clause': where_clause,
            'order_clause': order_clause,
            'limit_clause': ''
        }
        
        return query_info, sql_query
        
    except Exception as e:
        print(f"❌ 处理查询时出错: {str(e)}")
        return None, None

def show_available_tables():
    """显示可用的表"""
    schema_data = load_schema_only()
    
    print("\n📊 可用的数据表:")
    print("=" * 60)
    
    enabled_tables = [t for t in schema_data['Tables'] if t.get('enabled', 'true') == 'true']
    
    for i, table in enumerate(enabled_tables, 1):
        print(f"{i:2d}. {table['TableName']}")
        print(f"    📝 描述: {table.get('Description', '无描述')}")
        print(f"    📋 列数: {len(table.get('Columns', []))}")
        
        # 显示前几个列
        columns = [col['ColumnName'] for col in table.get('Columns', [])[:5]]
        if len(table.get('Columns', [])) > 5:
            columns.append('...')
        print(f"    🔧 主要列: {', '.join(columns)}")
        print()

def suggest_queries():
    """建议一些查询示例"""
    print("\n💡 建议的查询示例:")
    print("=" * 50)
    
    examples = [
        "Show Python-SDK usage this month",
        "Show top 10 products by request count",
        "What are Java products used in 2024-08?",
        "Show Go-SDK subscription counts by month",
        "Which customers have more than 1000 requests?",
        "Show Track1 vs Track2 usage for Python-SDK",
        "List all products usage in August 2025"
    ]
    
    for i, example in enumerate(examples, 1):
        marker = "👉" if "Python-SDK" in example else "  "
        print(f"{marker} {i}. {example}")

if __name__ == "__main__":
    print("🔍 Azure SDK 使用数据查询演示")
    print("=" * 60)
    
    # 显示可用表
    show_available_tables()
    
    # 模拟查询
    query_info, sql_query = simulate_python_sdk_query()
    
    # 显示建议查询
    suggest_queries()
    
    print("\n" + "=" * 60)
    print("ℹ️  注意: 这是查询结构的演示，实际执行需要数据库连接")
