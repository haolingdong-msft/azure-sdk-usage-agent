from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.exceptions import KustoServiceError

# --- Configuration ---
CLUSTER = "https://help.kusto.windows.net/.default"  # Kusto cluster URL
DATABASE = "Samples"                         # Database name

def get_kusto_client(cluster: str) -> KustoClient:
    """
    Get a KustoClient using MSI (Managed Identity) authentication.
    Note: Ensure that the environment where this code runs has access to the Kusto cluster via MSI/other authentication methods.
    Reference: https://learn.microsoft.com/en-us/kusto/api/get-started/app-authentication-methods?view=azure-data-explorer&tabs=python
    """
    # Managed Identity authentication
    # kcsb = KustoConnectionStringBuilder.with_aad_managed_service_identity_authentication(cluster)
    
    # Interactive user sign-in authentication
    kcsb = KustoConnectionStringBuilder.with_interactive_login(cluster)

    client = KustoClient(kcsb)
    return client

def validate_kusto_query(query: str, client: KustoClient, database: str) -> bool:
    """
    Validate Kusto query by attempting to execute it with 0 results (take 0)
    """
    try:
        # append take 0 to avoid fetching data
        test_query = f"{query} | take 0"
        client.execute(database, test_query)
        return True
    except KustoServiceError as e:
        print("Validation failed:", e)
        return False

if __name__ == "__main__":
    client = get_kusto_client(CLUSTER)

    # Valid query
    query_ok = "StormEvents | take 10"
    print("Valid query check:", validate_kusto_query(query_ok, client, DATABASE))

    # Invalid query
    query_bad = "StormEventsss | take 10"
    print("Invalid query check:", validate_kusto_query(query_bad, client, DATABASE))
