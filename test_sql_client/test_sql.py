"""
独立测试 SQL Server REST API 客户端
"""
import asyncio
import httpx
import os
from azure.identity import DefaultAzureCredential

# 配置参数 - 可根据需要修改
SQL_SERVER = os.getenv('SQL_SERVER', 'azuresdkbi-server.database.windows.net')
SQL_DATABASE = os.getenv('SQL_DATABASE', 'azuresdkbi')
AZURE_SUBSCRIPTION_ID = os.getenv('AZURE_SUBSCRIPTION_ID', 'a18897a6-7e44-457d-9260-f2854c0aca42')
AZURE_RESOURCE_GROUP = os.getenv('AZURE_RESOURCE_GROUP', 'sdk-mgmt-bi-data')

SQL_SCOPE = "https://database.windows.net/.default"
MANAGEMENT_SCOPE = "https://management.azure.com/.default"
MANAGEMENT_URL = "https://management.azure.com"

class SimpleSQLClient:
    """简化的 SQL Server REST API 客户端用于测试"""
    
    def __init__(self):
        self.credential = DefaultAzureCredential()
    
    async def get_access_token(self, scope: str) -> str:
        """获取 Azure AD 访问令牌"""
        try:
            print(f"🔑 正在获取访问令牌，作用域: {scope}")
            token = self.credential.get_token(scope)
            print(f"✅ 成功获取访问令牌 (过期时间: {token.expires_on})")
            return token.token
        except Exception as e:
            print(f"🔒 获取访问令牌失败: {str(e)}")
            raise
    
    async def test_connection(self, sql_query: str):
        """测试数据库连接和查询执行"""
        print(f"🔄 开始测试 SQL 查询: {sql_query}")
        
        # 尝试直接 SQL Database API
        try:
            print("\n=== 尝试直接 SQL Database API ===")
            result = await self._test_sql_database_api(sql_query)
            if result:
                print("✅ 直接 SQL Database API 连接成功!")
                return result
        except Exception as e:
            print(f"❌ 直接 SQL Database API 失败: {str(e)}")
        
        # 尝试 Azure Management API
        try:
            print("\n=== 尝试 Azure Management API ===")
            result = await self._test_management_api(sql_query)
            if result:
                print("✅ Azure Management API 连接成功!")
                return result
        except Exception as e:
            print(f"❌ Azure Management API 失败: {str(e)}")
        
        print("❌ 所有连接方式都失败了")
        return None
    
    async def _test_sql_database_api(self, sql_query: str):
        """测试直接 SQL Database API"""
        token = await self.get_access_token(SQL_SCOPE)
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        url = f"https://{SQL_SERVER}/api/sql/v1/query"
        print(f"🌐 连接到: {url}")
        
        payload = {
            "database": SQL_DATABASE,
            "query": sql_query,
            "timeout": 30
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            print("📡 发送 HTTP POST 请求...")
            response = await client.post(url, headers=headers, json=payload)
            
            print(f"📊 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"📄 响应内容: {response.text[:500]}...")
                return None
    
    async def _test_management_api(self, sql_query: str):
        """测试 Azure Management API"""
        token = await self.get_access_token(MANAGEMENT_SCOPE)
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        server_name = SQL_SERVER.split('.')[0]
        url = f"{MANAGEMENT_URL}/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourceGroups/{AZURE_RESOURCE_GROUP}/providers/Microsoft.Sql/servers/{server_name}/databases/{SQL_DATABASE}/query"
        print(f"🌐 连接到: {url}")
        print(f"📊 目标: 服务器={server_name}, 数据库={SQL_DATABASE}, 资源组={AZURE_RESOURCE_GROUP}")
        
        payload = {
            "query": sql_query
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            print("📡 发送 HTTP POST 请求...")
            response = await client.post(url, headers=headers, json=payload, params={"api-version": "2021-11-01"})
            
            print(f"📊 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"📄 响应内容: {response.text[:500]}...")
                return None

async def main():
    """主测试函数"""
    print("🚀 开始 SQL Server 连接测试")
    
    client = SimpleSQLClient()
    
    # 测试查询 - 可以修改为你想要的 SQL 语句
    test_queries = [
        "SELECT * FROM aa WHERE id = 1",
        "SELECT TOP 5 * FROM aa", 
        "SELECT COUNT(*) FROM aa"
    ]
    
    for sql in test_queries:
        print(f"\n{'='*50}")
        print(f"测试查询: {sql}")
        print(f"{'='*50}")
        
        try:
            result = await client.test_connection(sql)
            if result:
                print(f"✅ 查询成功，结果: {result}")
            else:
                print("❌ 查询失败")
        except Exception as e:
            print(f"💥 执行异常: {str(e)}")
        
        print("\n" + "-"*30)

if __name__ == "__main__":
    asyncio.run(main())
