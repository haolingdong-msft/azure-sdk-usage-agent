"""
使用 Azure REST API 测试数据库连接
不依赖 pyodbc 或 sqlalchemy，纯 REST API 方式
"""
import asyncio
import httpx
import json
import os
from azure.identity import DefaultAzureCredential

# 配置参数
SQL_SERVER = os.getenv('SQL_SERVER', 'azuresdkbi-server.database.windows.net')
SQL_DATABASE = os.getenv('SQL_DATABASE', 'azuresdkbi')
AZURE_SUBSCRIPTION_ID = os.getenv('AZURE_SUBSCRIPTION_ID', 'a18897a6-7e44-457d-9260-f2854c0aca42')
AZURE_RESOURCE_GROUP = os.getenv('AZURE_RESOURCE_GROUP', 'sdk-mgmt-bi-data')

class AzureRESTSQLClient:
    """使用 Azure REST API 连接 SQL Database"""
    
    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.subscription_id = AZURE_SUBSCRIPTION_ID
        self.resource_group = AZURE_RESOURCE_GROUP
        self.server_name = SQL_SERVER.split('.')[0]  # 提取服务器名称
        self.database_name = SQL_DATABASE
    
    async def get_access_token(self, scope: str):
        """获取访问令牌"""
        try:
            print(f"🔑 正在获取访问令牌，作用域: {scope}")
            token = self.credential.get_token(scope)
            print(f"✅ 成功获取访问令牌")
            return token.token
        except Exception as e:
            print(f"🔒 获取访问令牌失败: {str(e)}")
            raise
    
    async def test_database_info(self):
        """测试获取数据库信息"""
        try:
            print("\n=== 测试获取数据库信息 ===")
            token = await self.get_access_token("https://management.azure.com/.default")
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # 获取数据库信息的 REST API
            url = (f"https://management.azure.com/subscriptions/{self.subscription_id}/"
                   f"resourceGroups/{self.resource_group}/"
                   f"providers/Microsoft.Sql/servers/{self.server_name}/"
                   f"databases/{self.database_name}")
            
            params = {"api-version": "2021-11-01"}
            
            print(f"🌐 获取数据库信息: {url}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(url, headers=headers, params=params)
                
                print(f"📊 响应状态码: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print("✅ 成功获取数据库信息!")
                    
                    # 提取关键信息
                    db_info = {
                        "数据库名称": data.get("name"),
                        "状态": data.get("properties", {}).get("status"),
                        "服务等级": data.get("properties", {}).get("currentServiceObjectiveName"),
                        "创建日期": data.get("properties", {}).get("creationDate"),
                        "位置": data.get("location"),
                        "资源ID": data.get("id")
                    }
                    
                    print("📋 数据库信息:")
                    for key, value in db_info.items():
                        print(f"   {key}: {value}")
                    
                    return {"success": True, "data": db_info}
                else:
                    error_text = response.text
                    print(f"❌ 获取数据库信息失败: {error_text}")
                    return {"success": False, "error": error_text}
                    
        except Exception as e:
            print(f"💥 获取数据库信息异常: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_server_info(self):
        """测试获取服务器信息"""
        try:
            print("\n=== 测试获取服务器信息 ===")
            token = await self.get_access_token("https://management.azure.com/.default")
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # 获取服务器信息的 REST API
            url = (f"https://management.azure.com/subscriptions/{self.subscription_id}/"
                   f"resourceGroups/{self.resource_group}/"
                   f"providers/Microsoft.Sql/servers/{self.server_name}")
            
            params = {"api-version": "2021-11-01"}
            
            print(f"🌐 获取服务器信息: {url}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(url, headers=headers, params=params)
                
                print(f"📊 响应状态码: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print("✅ 成功获取服务器信息!")
                    
                    # 提取关键信息
                    server_info = {
                        "服务器名称": data.get("name"),
                        "状态": data.get("properties", {}).get("state"),
                        "版本": data.get("properties", {}).get("version"),
                        "管理员登录": data.get("properties", {}).get("administratorLogin"),
                        "完全限定域名": data.get("properties", {}).get("fullyQualifiedDomainName"),
                        "位置": data.get("location"),
                        "资源ID": data.get("id")
                    }
                    
                    print("📋 服务器信息:")
                    for key, value in server_info.items():
                        print(f"   {key}: {value}")
                    
                    return {"success": True, "data": server_info}
                else:
                    error_text = response.text
                    print(f"❌ 获取服务器信息失败: {error_text}")
                    return {"success": False, "error": error_text}
                    
        except Exception as e:
            print(f"💥 获取服务器信息异常: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_list_databases(self):
        """测试列出服务器上的所有数据库"""
        try:
            print("\n=== 测试列出所有数据库 ===")
            token = await self.get_access_token("https://management.azure.com/.default")
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # 列出数据库的 REST API
            url = (f"https://management.azure.com/subscriptions/{self.subscription_id}/"
                   f"resourceGroups/{self.resource_group}/"
                   f"providers/Microsoft.Sql/servers/{self.server_name}/"
                   f"databases")
            
            params = {"api-version": "2021-11-01"}
            
            print(f"🌐 列出数据库: {url}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(url, headers=headers, params=params)
                
                print(f"📊 响应状态码: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    databases = data.get("value", [])
                    print(f"✅ 成功获取数据库列表! 找到 {len(databases)} 个数据库")
                    
                    print("📋 数据库列表:")
                    for i, db in enumerate(databases, 1):
                        db_name = db.get("name")
                        db_status = db.get("properties", {}).get("status", "未知")
                        db_tier = db.get("properties", {}).get("currentServiceObjectiveName", "未知")
                        print(f"   {i}. {db_name} (状态: {db_status}, 服务等级: {db_tier})")
                    
                    return {"success": True, "count": len(databases), "databases": databases}
                else:
                    error_text = response.text
                    print(f"❌ 获取数据库列表失败: {error_text}")
                    return {"success": False, "error": error_text}
                    
        except Exception as e:
            print(f"💥 获取数据库列表异常: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_firewall_rules(self):
        """测试获取防火墙规则"""
        try:
            print("\n=== 测试获取防火墙规则 ===")
            token = await self.get_access_token("https://management.azure.com/.default")
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # 获取防火墙规则的 REST API
            url = (f"https://management.azure.com/subscriptions/{self.subscription_id}/"
                   f"resourceGroups/{self.resource_group}/"
                   f"providers/Microsoft.Sql/servers/{self.server_name}/"
                   f"firewallRules")
            
            params = {"api-version": "2021-11-01"}
            
            print(f"🌐 获取防火墙规则: {url}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(url, headers=headers, params=params)
                
                print(f"📊 响应状态码: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    rules = data.get("value", [])
                    print(f"✅ 成功获取防火墙规则! 找到 {len(rules)} 条规则")
                    
                    print("📋 防火墙规则:")
                    for i, rule in enumerate(rules, 1):
                        rule_name = rule.get("name")
                        start_ip = rule.get("properties", {}).get("startIpAddress")
                        end_ip = rule.get("properties", {}).get("endIpAddress")
                        print(f"   {i}. {rule_name}: {start_ip} - {end_ip}")
                    
                    return {"success": True, "count": len(rules), "rules": rules}
                else:
                    error_text = response.text
                    print(f"❌ 获取防火墙规则失败: {error_text}")
                    return {"success": False, "error": error_text}
                    
        except Exception as e:
            print(f"💥 获取防火墙规则异常: {str(e)}")
            return {"success": False, "error": str(e)}

async def main():
    """主测试函数"""
    print("🚀 开始 Azure SQL Database REST API 连接测试")
    print(f"🎯 目标订阅: {AZURE_SUBSCRIPTION_ID}")
    print(f"🎯 目标资源组: {AZURE_RESOURCE_GROUP}")
    print(f"🎯 目标服务器: {SQL_SERVER}")
    print(f"🎯 目标数据库: {SQL_DATABASE}")
    
    client = AzureRESTSQLClient()
    
    # 执行各种测试
    tests = [
        ("获取服务器信息", client.test_server_info),
        ("获取数据库信息", client.test_database_info),
        ("列出所有数据库", client.test_list_databases),
        ("获取防火墙规则", client.test_firewall_rules),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"测试: {test_name}")
        print(f"{'='*60}")
        
        try:
            result = await test_func()
            result["test_name"] = test_name
            results.append(result)
        except Exception as e:
            print(f"💥 测试异常: {str(e)}")
            results.append({"test_name": test_name, "success": False, "error": str(e)})
        
        print("\n" + "-"*40)
    
    # 总结结果
    print(f"\n{'='*60}")
    print("测试结果总结")
    print(f"{'='*60}")
    
    success_count = 0
    for result in results:
        test_name = result.get("test_name", "未知测试")
        success = result.get("success", False)
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{test_name:20} : {status}")
        
        if success:
            success_count += 1
        else:
            error = result.get("error", "未知错误")
            print(f"{'':22}   错误: {error}")
    
    print(f"\n📊 总体结果: {success_count}/{len(results)} 项测试通过")
    
    if success_count > 0:
        print(f"\n✅ 连接测试成功! Azure SQL Database 资源可以通过 REST API 访问")
        print(f"💡 这意味着:")
        print(f"   - Azure AD 认证工作正常")
        print(f"   - 网络连接正常")
        print(f"   - 资源配置正确")
        print(f"   - 权限设置适当")
    else:
        print(f"\n❌ 所有测试都失败了，请检查:")
        print(f"   - Azure AD 认证配置")
        print(f"   - 订阅ID和资源组名称")
        print(f"   - 服务器和数据库名称")
        print(f"   - 用户权限设置")

if __name__ == "__main__":
    asyncio.run(main())
