"""
简化的 SQL 查询测试 - 使用 Azure AD 集成认证
"""
import asyncio
import pyodbc
import os
from azure.identity import DefaultAzureCredential
from typing import Dict, Any, Optional

# 配置参数
SQL_SERVER = os.getenv('SQL_SERVER', 'azuresdkbi-server.database.windows.net')
SQL_DATABASE = os.getenv('SQL_DATABASE', 'azuresdkbi')

class SimpleSQLExecutor:
    """简化的 SQL 执行器"""
    
    def __init__(self):
        self.server = SQL_SERVER
        self.database = SQL_DATABASE
        self.connection = None
    
    async def connect_with_integrated_auth(self) -> bool:
        """使用 Azure AD 集成认证连接"""
        try:
            print(f"🌐 正在连接到 {self.server}/{self.database}")
            print("🔑 尝试使用 Azure AD 集成认证...")
            
            # 使用 Azure AD 集成认证
            connection_string = (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"Authentication=ActiveDirectoryIntegrated;"
                f"Encrypt=yes;"
                f"TrustServerCertificate=no;"
            )
            
            self.connection = pyodbc.connect(connection_string, timeout=30)
            print("✅ Azure AD 集成认证连接成功!")
            return True
            
        except Exception as e:
            print(f"❌ Azure AD 集成认证连接失败: {str(e)}")
            return False
    
    async def connect_with_default_auth(self) -> bool:
        """使用默认认证方式连接"""
        try:
            print(f"🌐 正在连接到 {self.server}/{self.database}")
            print("🔑 尝试使用默认认证...")
            
            # 基本连接字符串
            connection_string = (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"Trusted_Connection=yes;"
                f"Encrypt=yes;"
                f"TrustServerCertificate=no;"
            )
            
            self.connection = pyodbc.connect(connection_string, timeout=30)
            print("✅ 默认认证连接成功!")
            return True
            
        except Exception as e:
            print(f"❌ 默认认证连接失败: {str(e)}")
            return False
    
    async def connect_with_sql_auth(self, username: str = None, password: str = None) -> bool:
        """使用 SQL Server 认证连接"""
        try:
            # 从环境变量获取用户名和密码
            username = username or os.getenv('SQL_USERNAME')
            password = password or os.getenv('SQL_PASSWORD')
            
            if not username or not password:
                print("❌ 缺少 SQL Server 用户名或密码")
                return False
            
            print(f"🌐 正在连接到 {self.server}/{self.database}")
            print(f"🔑 尝试使用 SQL Server 认证 (用户: {username})...")
            
            connection_string = (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"UID={username};"
                f"PWD={password};"
                f"Encrypt=yes;"
                f"TrustServerCertificate=no;"
            )
            
            self.connection = pyodbc.connect(connection_string, timeout=30)
            print("✅ SQL Server 认证连接成功!")
            return True
            
        except Exception as e:
            print(f"❌ SQL Server 认证连接失败: {str(e)}")
            return False
    
    async def try_all_connections(self) -> bool:
        """尝试所有可能的连接方式"""
        connection_methods = [
            ("Azure AD 集成认证", self.connect_with_integrated_auth),
            ("默认认证", self.connect_with_default_auth),
            ("SQL Server 认证", self.connect_with_sql_auth),
        ]
        
        for method_name, method in connection_methods:
            print(f"\n--- 尝试 {method_name} ---")
            try:
                if await method():
                    print(f"✅ {method_name} 连接成功!")
                    return True
            except Exception as e:
                print(f"❌ {method_name} 连接异常: {str(e)}")
            
            print("-" * 30)
        
        print("❌ 所有连接方式都失败了")
        return False
    
    async def execute_query(self, sql: str) -> Optional[Dict[str, Any]]:
        """执行 SQL 查询"""
        if not self.connection:
            print("❌ 数据库未连接")
            return None
        
        try:
            print(f"📡 执行查询: {sql}")
            
            cursor = self.connection.cursor()
            cursor.execute(sql)
            
            # 检查是否有结果集
            if cursor.description:
                # SELECT 查询
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
                
                print(f"📊 查询成功! 返回 {len(rows)} 行数据")
                
                # 转换为字典列表
                result_data = []
                for row in rows:
                    row_dict = {}
                    for i, value in enumerate(row):
                        row_dict[columns[i]] = value
                    result_data.append(row_dict)
                
                # 显示前几行
                print(f"📋 列名: {columns}")
                for i, row_dict in enumerate(result_data[:5]):
                    print(f"   行 {i+1}: {row_dict}")
                
                if len(result_data) > 5:
                    print(f"   ... (还有 {len(result_data) - 5} 行)")
                
                return {
                    "success": True,
                    "query": sql,
                    "columns": columns,
                    "rows": result_data,
                    "count": len(result_data)
                }
            else:
                # 非查询语句
                affected_rows = cursor.rowcount
                print(f"✅ 查询执行成功! 影响了 {affected_rows} 行")
                
                return {
                    "success": True,
                    "query": sql,
                    "affected_rows": affected_rows
                }
                
        except Exception as e:
            print(f"❌ 查询执行失败: {str(e)}")
            return {
                "success": False,
                "query": sql,
                "error": str(e)
            }
    
    def close(self):
        """关闭连接"""
        if self.connection:
            self.connection.close()
            print("🔌 数据库连接已关闭")

async def test_connection_and_queries():
    """测试连接和查询"""
    print("🚀 开始 Azure SQL Database 连接和查询测试")
    
    executor = SimpleSQLExecutor()
    
    try:
        # 尝试连接
        print(f"\n{'='*60}")
        print("步骤 1: 尝试连接数据库")
        print(f"{'='*60}")
        
        if not await executor.try_all_connections():
            print("❌ 无法连接到数据库，测试终止")
            print("\n💡 可能的解决方案:")
            print("   1. 检查网络连接")
            print("   2. 确认服务器地址和数据库名称")
            print("   3. 检查防火墙规则")
            print("   4. 确认用户权限")
            print("   5. 设置环境变量 SQL_USERNAME 和 SQL_PASSWORD")
            return
        
        # 执行测试查询
        print(f"\n{'='*60}")
        print("步骤 2: 执行测试查询")
        print(f"{'='*60}")
        
        test_queries = [
            "SELECT @@VERSION AS database_version",
            "SELECT GETDATE() AS current_time",
            "SELECT DB_NAME() AS current_database",
            "SELECT USER_NAME() AS current_user",
            "SELECT TOP 5 TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'",
        ]
        
        success_count = 0
        for i, sql in enumerate(test_queries, 1):
            print(f"\n--- 测试查询 {i} ---")
            result = await executor.execute_query(sql)
            
            if result and result.get("success"):
                success_count += 1
                print(f"✅ 查询 {i} 成功")
            else:
                print(f"❌ 查询 {i} 失败")
            
            print("-" * 30)
        
        print(f"\n📊 测试结果: {success_count}/{len(test_queries)} 项查询成功")
        
        if success_count > 0:
            print("\n🎉 数据库连接和查询测试成功!")
            print("💡 你现在可以执行自定义 SQL 查询了")
            
            # 提示用户可以执行自定义查询
            print(f"\n{'='*60}")
            print("你想执行自定义查询吗? (y/n)")
            
            try:
                user_input = input().strip().lower()
                if user_input in ['y', 'yes']:
                    custom_sql = input("请输入 SQL 查询: ").strip()
                    if custom_sql:
                        print(f"\n--- 执行自定义查询 ---")
                        result = await executor.execute_query(custom_sql)
                        
                        if result and result.get("success"):
                            print("🎉 自定义查询执行成功!")
                        else:
                            print("❌ 自定义查询执行失败")
            except KeyboardInterrupt:
                print("\n👋 用户取消操作")
        
    finally:
        executor.close()

async def main():
    """主函数"""
    await test_connection_and_queries()

if __name__ == "__main__":
    asyncio.run(main())
