"""
使用标准数据库连接测试 Azure SQL Database
"""
import asyncio
import pyodbc
import os
from azure.identity import DefaultAzureCredential

# 配置参数
SQL_SERVER = os.getenv('SQL_SERVER', 'azuresdkbi-server.database.windows.net')
SQL_DATABASE = os.getenv('SQL_DATABASE', 'azuresdkbi')

class DirectSQLClient:
    """使用 ODBC 直接连接 Azure SQL Database"""
    
    def __init__(self):
        self.credential = DefaultAzureCredential()
    
    async def get_access_token(self):
        """获取访问令牌用于数据库认证"""
        try:
            print("🔑 正在获取 Azure AD 访问令牌...")
            token = self.credential.get_token("https://database.windows.net/.default")
            print("✅ 成功获取访问令牌")
            return token.token
        except Exception as e:
            print(f"🔒 获取访问令牌失败: {str(e)}")
            raise
    
    async def test_connection(self, sql_query: str):
        """测试数据库连接和查询执行"""
        print(f"🔄 开始测试 SQL 查询: {sql_query}")
        
        try:
            # 获取访问令牌
            token = await self.get_access_token()
            
            # 构建连接字符串
            connection_string = (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={SQL_SERVER};"
                f"DATABASE={SQL_DATABASE};"
                f"Authentication=ActiveDirectoryAccessToken;"
                f"AccessToken={token};"
                f"Encrypt=yes;"
                f"TrustServerCertificate=no;"
            )
            
            print(f"🌐 连接到数据库: {SQL_SERVER}/{SQL_DATABASE}")
            
            # 建立连接
            with pyodbc.connect(connection_string) as conn:
                print("✅ 数据库连接成功!")
                
                cursor = conn.cursor()
                
                # 执行查询
                print(f"📡 执行查询: {sql_query}")
                cursor.execute(sql_query)
                
                # 获取结果
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
                
                print(f"📊 查询成功! 返回 {len(rows)} 行数据")
                print(f"📋 列名: {columns}")
                
                # 显示前几行数据
                for i, row in enumerate(rows[:5]):  # 只显示前5行
                    print(f"   行 {i+1}: {dict(zip(columns, row))}")
                
                if len(rows) > 5:
                    print(f"   ... (还有 {len(rows) - 5} 行)")
                
                return {
                    "columns": columns,
                    "rows": [dict(zip(columns, row)) for row in rows],
                    "count": len(rows)
                }
                
        except pyodbc.Error as e:
            print(f"❌ 数据库错误: {str(e)}")
            return None
        except Exception as e:
            print(f"💥 执行异常: {str(e)}")
            return None

async def main():
    """主测试函数"""
    print("🚀 开始 Azure SQL Database 直连测试")
    
    client = DirectSQLClient()
    
    # 测试查询 - 可以修改为你想要的 SQL 语句
    test_queries = [
        "SELECT TOP 5 * FROM INFORMATION_SCHEMA.TABLES",  # 查看表信息
        "SELECT @@VERSION",  # 查看数据库版本
        "SELECT GETDATE() AS current_time",  # 获取当前时间
        # "SELECT * FROM aa WHERE id = 1",  # 你的自定义查询
    ]
    
    for sql in test_queries:
        print(f"\n{'='*60}")
        print(f"测试查询: {sql}")
        print(f"{'='*60}")
        
        try:
            result = await client.test_connection(sql)
            if result:
                print(f"✅ 查询成功!")
            else:
                print("❌ 查询失败")
        except Exception as e:
            print(f"💥 执行异常: {str(e)}")
        
        print("\n" + "-"*40)

if __name__ == "__main__":
    asyncio.run(main())
