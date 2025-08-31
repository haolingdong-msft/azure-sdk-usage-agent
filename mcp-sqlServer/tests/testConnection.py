import pyodbc
from azure.identity import DefaultAzureCredential

# Azure SQL Server 连接信息
server = "azuresdkbi-server.database.windows.net"
database = "azuresdkbi"
driver = "{ODBC Driver 18 for SQL Server}"

# 1. 获取 Azure AD Token (Managed Identity / DefaultAzureCredential 会自动处理)
#    注意 scope 必须是数据库的 .default 结尾
credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)
access_token = credential.get_token("https://database.windows.net/.default")

# 2. ODBC 连接 (access token 传入 PWD 字段)
conn_str = (
    f"DRIVER={driver};"
    f"SERVER={server};"
    f"DATABASE={database};"
    "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
)
# SQL_CONNECTION_STRING="" \
# "Driver={ODBC Driver 18 for SQL Server};" \
# "Server=<server_name>;" \
# "Database={<database_name>};" \
# "Encrypt=yes;TrustServerCertificate=no;Authentication=ActiveDirectoryMsi"
# pyodbc 需要 token 作为字节串传递
token_bytes = access_token.token.encode("utf-8")
print("Token preview:", access_token.token[:200])  # 打印前200字符
print("Token length (string):", len(access_token.token))

# 3. 建立连接

try:
    conn = pyodbc.connect(conn_str, attrs_before={1256: token_bytes})
    cursor = conn.cursor()
    # cursor.execute("SELECT SUSER_SNAME()")
    # print(cursor.fetchone())
    conn.close()
except Exception as e:
    print("ODBC connect error:", e)

# conn = pyodbc.connect(conn_str, attrs_before={1256: token_bytes})  
# # 1256 = SQL_COPT_SS_ACCESS_TOKEN (ODBC 的特殊选项)

# cursor = conn.cursor()
# cursor.execute("select top 10 * from dbo.AMEConciseSubReqCCIDCountByMonthProduct;")
# print(cursor.fetchone())
# # for row in cursor.fetchall():
# #     print(row)

# conn.close()
