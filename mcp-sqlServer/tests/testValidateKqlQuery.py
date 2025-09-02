from azure.kusto.data import KustoConnectionStringBuilder, KustoClient, ClientRequestProperties
from azure.identity import DefaultAzureCredential

def validate_kql_query_msi(cluster: str, database: str, query: str) -> bool:
    """
    使用 MSI 验证 Kusto Query 是否有效（语法层面，不执行查询）

    :param cluster: Kusto Cluster URL，例如 "https://help.kusto.windows.net"
    :param database: 数据库名，例如 "Samples"
    :param query: 需要验证的 KQL 语句
    :return: True 表示语法有效，False 表示无效
    """
    # 使用 MSI / Managed Identity
    credential = DefaultAzureCredential(exclude_interactive_browser_credential=True)
    kcsb = KustoConnectionStringBuilder.with_aad_application_token_authentication(
        cluster, credential.get_token("https://help.kusto.windows.net/.default").token
    )
    
    client = KustoClient(kcsb)

    # 设置只做验证，不执行
    crp = ClientRequestProperties()
    crp.set_option("validate_only", True)

    try:
        client.execute(database, query, client_request_properties=crp)
        return True
    except Exception as e:
        print(f"❌ Invalid query: {e}")
        return False


if __name__ == "__main__":
    cluster = "https://help.kusto.windows.net"
    database = "Samples"

    # 正确查询
    query1 = "StormEvents | summarize count() by State"
    print("Query1 valid?", validate_kql_query_msi(cluster, database, query1))

    # 错误查询
    query2 = "StormEvents | summariz count() by State"
    print("Query2 valid?", validate_kql_query_msi(cluster, database, query2))
