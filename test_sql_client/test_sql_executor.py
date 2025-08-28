"""
真正执行 SQL 查询的测试脚本
使用 pyodbc + Azure AD 认证连接 Azure SQL Database
"""
import asyncio
import pyodbc
import struct
import os
from azure.identity import DefaultAzureCredential
from typing import List, Dict, Any, Optional

# 配置参数
SQL_SERVER = os.getenv('SQL_SERVER', 'azuresdkbi-server.database.windows.net')
SQL_DATABASE = os.getenv('SQL_DATABASE', 'azuresdkbi')

class AzureSQLExecutor:
    """Azure SQL Database 查询执行器"""
    
    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.server = SQL_SERVER
        self.database = SQL_DATABASE
        self.connection = None
    
    async def get_access_token(self) -> str:
        """获取访问令牌字符串格式"""
        try:
            print("🔑 正在获取 Azure AD 访问令牌...")
            token = self.credential.get_token("https://database.windows.net/.default")
            print(f"✅ 成功获取访问令牌 (过期时间: {token.expires_on})")
            return token.token
        except Exception as e:
            print(f"🔒 获取访问令牌失败: {str(e)}")
            raise
    
    async def connect(self) -> bool:
        """建立数据库连接"""
        try:
            print(f"🌐 正在连接到 {self.server}/{self.database}")
            
            # 获取访问令牌
            token = await self.get_access_token()
            
            # 构建连接字符串 - 使用 Active Directory Access Token 方式
            connection_string = (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"Authentication=ActiveDirectoryAccessToken;"
                f"AccessToken={token};"
                f"Encrypt=yes;"
                f"TrustServerCertificate=no;"
            )
            
            # 建立连接
            self.connection = pyodbc.connect(connection_string)
            print("✅ 数据库连接成功!")
            return True
            
        except Exception as e:
            print(f"❌ 数据库连接失败: {str(e)}")
            return False
    
    async def execute_query(self, sql: str) -> Optional[Dict[str, Any]]:
        """执行 SQL 查询并返回结果"""
        if not self.connection:
            print("❌ 数据库未连接，请先调用 connect()")
            return None
        
        try:
            print(f"📡 执行查询: {sql}")
            
            cursor = self.connection.cursor()
            cursor.execute(sql)
            
            # 检查是否有结果集
            if cursor.description:
                # SELECT 查询 - 有结果返回
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
                
                print(f"📊 查询成功! 返回 {len(rows)} 行数据")
                print(f"📋 列名: {columns}")
                
                # 转换为字典列表
                result_data = []
                for row in rows:
                    row_dict = {}
                    for i, value in enumerate(row):
                        row_dict[columns[i]] = value
                    result_data.append(row_dict)
                
                # 显示前几行数据
                for i, row_dict in enumerate(result_data[:3]):
                    print(f"   行 {i+1}: {row_dict}")
                
                if len(result_data) > 3:
                    print(f"   ... (还有 {len(result_data) - 3} 行)")
                
                return {
                    "success": True,
                    "query": sql,
                    "columns": columns,
                    "rows": result_data,
                    "count": len(result_data)
                }
            else:
                # INSERT/UPDATE/DELETE 查询 - 无结果返回
                affected_rows = cursor.rowcount
                print(f"✅ 查询执行成功! 影响了 {affected_rows} 行")
                
                return {
                    "success": True,
                    "query": sql,
                    "affected_rows": affected_rows,
                    "message": f"查询执行成功，影响了 {affected_rows} 行"
                }
                
        except Exception as e:
            print(f"❌ 查询执行失败: {str(e)}")
            return {
                "success": False,
                "query": sql,
                "error": str(e)
            }
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            print("🔌 数据库连接已关闭")

async def test_sql_queries():
    """测试各种 SQL 查询"""
    print("🚀 开始 Azure SQL Database 查询测试")
    
    executor = AzureSQLExecutor()
    
    try:
        # 连接数据库
        if not await executor.connect():
            print("❌ 无法连接到数据库，测试终止")
            return
        
        # 测试查询列表
        test_queries = [
            # 基础查询
            "SELECT @@VERSION AS database_version",
            "SELECT GETDATE() AS current_time",
            "SELECT DB_NAME() AS current_database",
            
            # 查看表结构
            "SELECT TOP 10 TABLE_NAME, TABLE_TYPE FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'",
            
            # 查看列信息
            "SELECT TOP 5 TABLE_NAME, COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS ORDER BY TABLE_NAME",
            
            # 你的自定义查询（根据实际表名修改）
            # "SELECT * FROM aa WHERE id = 1",
            # "SELECT TOP 5 * FROM aa",
            # "SELECT COUNT(*) AS total_count FROM aa",
        ]
        
        results = []
        
        for i, sql in enumerate(test_queries, 1):
            print(f"\n{'='*60}")
            print(f"测试 {i}/{len(test_queries)}: {sql}")
            print(f"{'='*60}")
            
            result = await executor.execute_query(sql)
            results.append(result)
            
            print("-" * 40)
        
        # 总结结果
        print(f"\n{'='*60}")
        print("测试结果总结")
        print(f"{'='*60}")
        
        success_count = 0
        for i, result in enumerate(results, 1):
            if result and result.get("success"):
                success_count += 1
                status = "✅ 成功"
                if "count" in result:
                    status += f" ({result['count']} 行)"
                elif "affected_rows" in result:
                    status += f" ({result['affected_rows']} 行受影响)"
            else:
                status = "❌ 失败"
                if result and "error" in result:
                    status += f" - {result['error']}"
            
            query = test_queries[i-1][:50] + "..." if len(test_queries[i-1]) > 50 else test_queries[i-1]
            print(f"测试 {i:2d}: {status}")
            print(f"         {query}")
        
        print(f"\n📊 总体结果: {success_count}/{len(results)} 项测试通过")
        
        if success_count > 0:
            print(f"\n🎉 SQL 查询测试成功!")
            print(f"💡 你现在可以:")
            print(f"   - 修改测试查询中的表名和条件")
            print(f"   - 添加你自己的 SQL 语句")
            print(f"   - 执行 SELECT、INSERT、UPDATE、DELETE 操作")
        
        return results
        
    finally:
        # 确保关闭连接
        executor.close()

async def test_custom_query(sql: str):
    """测试单个自定义 SQL 查询"""
    print(f"🔍 测试自定义查询: {sql}")
    
    executor = AzureSQLExecutor()
    
    try:
        if await executor.connect():
            result = await executor.execute_query(sql)
            
            if result and result.get("success"):
                print("🎉 查询执行成功!")
                if "rows" in result:
                    print(f"📋 返回数据:")
                    for i, row in enumerate(result["rows"][:10], 1):  # 只显示前10行
                        print(f"   {i}: {row}")
                    if len(result["rows"]) > 10:
                        print(f"   ... (还有 {len(result['rows']) - 10} 行)")
                return result
            else:
                print("❌ 查询执行失败")
                return result
        else:
            print("❌ 无法连接到数据库")
            return None
    finally:
        executor.close()

async def main():
    """主函数"""
    print("🚀 Azure SQL Database 查询执行器")
    print("=" * 50)
    
    # 选择测试模式
    print("请选择测试模式:")
    print("1. 运行预设的测试查询")
    print("2. 执行自定义查询")
    
    try:
        choice = input("请输入选择 (1 或 2): ").strip()
        
        if choice == "1":
            # 运行预设测试
            await test_sql_queries()
        elif choice == "2":
            # 执行自定义查询
            sql = input("请输入 SQL 查询: ").strip()
            if sql:
                await test_custom_query(sql)
            else:
                print("❌ 未输入查询语句")
        else:
            print("❌ 无效选择，运行默认测试")
            await test_sql_queries()
            
    except KeyboardInterrupt:
        print("\n👋 用户取消操作")
    except Exception as e:
        print(f"💥 程序异常: {str(e)}")

if __name__ == "__main__":
    # 如果直接运行，执行预设测试
    asyncio.run(test_sql_queries())
