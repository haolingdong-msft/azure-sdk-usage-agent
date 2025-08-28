"""
使用 Azure SQL Database 官方 Python 库测试数据库连接
使用 azure-identity + pyodbc/sqlalchemy 的官方推荐方式
"""
import asyncio
import os
import struct
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.core.exceptions import ClientAuthenticationError

# 配置参数
SQL_SERVER = os.getenv('SQL_SERVER', 'azuresdkbi-server.database.windows.net')
SQL_DATABASE = os.getenv('SQL_DATABASE', 'azuresdkbi')

class AzureSQLClient:
    """Azure SQL Database 官方库客户端"""
    
    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.server = SQL_SERVER
        self.database = SQL_DATABASE
    
    async def get_connection_token(self):
        """获取数据库连接令牌"""
        try:
            print("🔑 正在获取 Azure SQL Database 访问令牌...")
            token = self.credential.get_token("https://database.windows.net/.default")
            print(f"✅ 成功获取访问令牌 (过期时间: {token.expires_on})")
            
            # 将令牌转换为 SQL Server 可接受的格式
            token_bytes = token.token.encode("utf-16-le")
            token_struct = struct.pack(f"<I{len(token_bytes)}s", len(token_bytes), token_bytes)
            
            return token_struct
        except Exception as e:
            print(f"🔒 获取访问令牌失败: {str(e)}")
            raise
    
    async def test_with_pyodbc(self, sql_query: str):
        """使用 pyodbc 测试连接（需要安装 pyodbc）"""
        try:
            import pyodbc
            
            print("\n=== 使用 pyodbc 连接 ===")
            token = await self.get_connection_token()
            
            # 构建连接字符串
            connection_string = (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"Encrypt=yes;"
                f"TrustServerCertificate=no;"
            )
            
            print(f"🌐 连接到: {self.server}/{self.database}")
            
            # 建立连接，使用 Azure AD 令牌
            conn_attrs = {
                pyodbc.SQL_COPT_SS_ACCESS_TOKEN: token
            }
            
            with pyodbc.connect(connection_string, attrs_before=conn_attrs) as conn:
                print("✅ pyodbc 连接成功!")
                
                cursor = conn.cursor()
                print(f"📡 执行查询: {sql_query}")
                cursor.execute(sql_query)
                
                # 获取结果
                if cursor.description:
                    columns = [column[0] for column in cursor.description]
                    rows = cursor.fetchall()
                    
                    print(f"📊 查询成功! 返回 {len(rows)} 行数据")
                    print(f"📋 列名: {columns}")
                    
                    # 显示结果
                    for i, row in enumerate(rows[:3]):  # 只显示前3行
                        row_dict = dict(zip(columns, row))
                        print(f"   行 {i+1}: {row_dict}")
                    
                    if len(rows) > 3:
                        print(f"   ... (还有 {len(rows) - 3} 行)")
                    
                    return {
                        "method": "pyodbc",
                        "success": True,
                        "columns": columns,
                        "count": len(rows),
                        "data": [dict(zip(columns, row)) for row in rows[:5]]
                    }
                else:
                    print("✅ 查询执行成功 (无返回数据)")
                    return {"method": "pyodbc", "success": True, "message": "查询执行成功"}
                    
        except ImportError:
            print("❌ pyodbc 未安装，跳过 pyodbc 测试")
            return {"method": "pyodbc", "success": False, "error": "pyodbc not installed"}
        except Exception as e:
            print(f"❌ pyodbc 连接失败: {str(e)}")
            return {"method": "pyodbc", "success": False, "error": str(e)}
    
    async def test_with_sqlalchemy(self, sql_query: str):
        """使用 SQLAlchemy 测试连接（需要安装 sqlalchemy）"""
        try:
            from sqlalchemy import create_engine, text
            from sqlalchemy.engine import URL
            
            print("\n=== 使用 SQLAlchemy 连接 ===")
            
            # 获取访问令牌 (字符串格式)
            token = self.credential.get_token("https://database.windows.net/.default")
            
            # 构建 SQLAlchemy 连接 URL
            connection_url = URL.create(
                "mssql+pyodbc",
                query={
                    "driver": "ODBC Driver 18 for SQL Server",
                    "server": self.server,
                    "database": self.database,
                    "encrypt": "yes",
                    "trustservercertificate": "no",
                    "authentication": "ActiveDirectoryAccessToken",
                    "accesstoken": token.token
                }
            )
            
            print(f"🌐 连接到: {self.server}/{self.database}")
            
            # 创建引擎并连接
            engine = create_engine(connection_url)
            
            with engine.connect() as conn:
                print("✅ SQLAlchemy 连接成功!")
                
                print(f"📡 执行查询: {sql_query}")
                result = conn.execute(text(sql_query))
                
                # 获取结果
                rows = result.fetchall()
                columns = list(result.keys()) if result.keys() else []
                
                print(f"📊 查询成功! 返回 {len(rows)} 行数据")
                if columns:
                    print(f"📋 列名: {columns}")
                
                # 显示结果
                for i, row in enumerate(rows[:3]):  # 只显示前3行
                    if columns:
                        row_dict = dict(zip(columns, row))
                        print(f"   行 {i+1}: {row_dict}")
                    else:
                        print(f"   行 {i+1}: {row}")
                
                if len(rows) > 3:
                    print(f"   ... (还有 {len(rows) - 3} 行)")
                
                return {
                    "method": "sqlalchemy",
                    "success": True,
                    "columns": columns,
                    "count": len(rows),
                    "data": [dict(zip(columns, row)) if columns else list(row) for row in rows[:5]]
                }
                    
        except ImportError as e:
            print(f"❌ SQLAlchemy 相关包未安装: {str(e)}")
            return {"method": "sqlalchemy", "success": False, "error": f"Package not installed: {str(e)}"}
        except Exception as e:
            print(f"❌ SQLAlchemy 连接失败: {str(e)}")
            return {"method": "sqlalchemy", "success": False, "error": str(e)}
    
    async def test_connection_simple(self, sql_query: str):
        """简化的连接测试，不依赖额外的数据库驱动"""
        try:
            print("\n=== 简化连接测试 (仅验证认证) ===")
            
            # 只测试 Azure AD 认证是否工作
            token = self.credential.get_token("https://database.windows.net/.default")
            print("✅ Azure AD 认证成功!")
            print(f"📋 令牌信息:")
            print(f"   - 长度: {len(token.token)} 字符")
            print(f"   - 过期时间: {token.expires_on}")
            print(f"   - 前缀: {token.token[:20]}...")
            
            return {
                "method": "simple_auth",
                "success": True,
                "token_length": len(token.token),
                "expires_on": token.expires_on
            }
            
        except Exception as e:
            print(f"❌ Azure AD 认证失败: {str(e)}")
            return {"method": "simple_auth", "success": False, "error": str(e)}

async def main():
    """主测试函数"""
    print("🚀 开始 Azure SQL Database 官方库连接测试")
    print(f"🎯 目标服务器: {SQL_SERVER}")
    print(f"🎯 目标数据库: {SQL_DATABASE}")
    
    client = AzureSQLClient()
    
    # 测试查询
    test_queries = [
        "SELECT @@VERSION AS version",  # 获取数据库版本
        "SELECT GETDATE() AS current_time",  # 获取当前时间
        "SELECT TOP 3 * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'",  # 查看表
        # "SELECT * FROM aa WHERE id = 1",  # 你的自定义查询（取消注释使用）
    ]
    
    results = []
    
    # 首先测试简化认证
    print(f"\n{'='*60}")
    print("步骤 1: 测试 Azure AD 认证")
    print(f"{'='*60}")
    
    auth_result = await client.test_connection_simple("")
    results.append(auth_result)
    
    if not auth_result["success"]:
        print("❌ Azure AD 认证失败，无法继续测试数据库连接")
        return
    
    # 测试不同的连接方法
    for sql in test_queries:
        print(f"\n{'='*60}")
        print(f"测试查询: {sql}")
        print(f"{'='*60}")
        
        # 测试 pyodbc
        pyodbc_result = await client.test_with_pyodbc(sql)
        results.append(pyodbc_result)
        
        # 测试 SQLAlchemy
        sqlalchemy_result = await client.test_with_sqlalchemy(sql)
        results.append(sqlalchemy_result)
        
        print("\n" + "-"*40)
    
    # 总结结果
    print(f"\n{'='*60}")
    print("测试结果总结")
    print(f"{'='*60}")
    
    for result in results:
        method = result.get("method", "unknown")
        success = result.get("success", False)
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{method:15} : {status}")
        if not success and "error" in result:
            print(f"                  错误: {result['error']}")
    
    print(f"\n💡 提示:")
    print(f"   - 如需使用 pyodbc: pip install pyodbc")
    print(f"   - 如需使用 SQLAlchemy: pip install sqlalchemy pyodbc")
    print(f"   - 确保已安装 ODBC Driver 18 for SQL Server")

if __name__ == "__main__":
    asyncio.run(main())
