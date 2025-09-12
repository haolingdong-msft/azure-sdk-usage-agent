import pyodbc
import struct
from azure import identity

server = "azuresdkbi-server.database.windows.net"
database = "azuresdkbi"
driver = "{ODBC Driver 18 for SQL Server}"
scope = "https://database.windows.net/.default"

# Azure SQL Server connection information
connection_string = f"DRIVER={driver};" \
                   f'Server=tcp:{server},1433;' \
                   f'Database={database};' \
                   'Encrypt=yes;' \
                   'TrustServerCertificate=no;' \
                   'Connection Timeout=30'

def get_conn():
    credential = identity.DefaultAzureCredential(exclude_interactive_browser_credential=False)
    token_bytes = credential.get_token("https://database.windows.net/.default").token.encode("UTF-16-LE")
    token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)
    SQL_COPT_SS_ACCESS_TOKEN = 1256  # This connection option is defined by microsoft in msodbcsql.h
    conn = pyodbc.connect(connection_string, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})
    return conn

def test_connection(sql_query="SELECT TOP 5 * FROM dbo.AMEConciseSubReqCCIDCountByMonthProduct;"):
    """Test database connection with custom SQL query"""
    try:
        print("Testing database connection...")
        conn = get_conn()
        cursor = conn.cursor()
        
        # Test query user information
        cursor.execute("SELECT SUSER_SNAME()")
        user_info = cursor.fetchone()
        print(f"Connection successful! Current user: {user_info[0]}")
        
        # Execute custom query
        print(f"Executing query: {sql_query}")
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        print(f"Query successful! Retrieved {len(rows)} rows of data")
        
        # Print first few rows of data
        for i, row in enumerate(rows):
            print(f"Row {i+1}: {row}")
        
        conn.close()
        print("Connection test completed!")
        
    except Exception as e:
        print(f"Connection test failed: {e}")

# python testConnection.py "SELECT top 2 * from dbo.AMEConciseSubReqCCIDCountByMonthProduct;"
if __name__ == "__main__":
    test_connection()
