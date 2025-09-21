from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.exceptions import KustoServiceError
import pandas as pd

# --- Configuration ---
CLUSTER = "https://help.kusto.windows.net/.default"  # Kusto cluster URL
DATABASE = "Samples"                         # Database name

def get_kusto_client(cluster: str) -> KustoClient:
    """
    Get a KustoClient using MSI (Managed Identity) authentication.
    Note: Ensure that the environment where this code runs has access to the Kusto cluster via MSI/other authentication methods.
    Reference: https://learn.microsoft.com/en-us/kusto/api/get-started/app-authentication-methods?view=azure-data-explorer&tabs=python
    """
    # Managed Identity authentication (IMDS required; not usable for local development)
    # kcsb = KustoConnectionStringBuilder.with_aad_managed_service_identity_authentication(cluster)
    
    # Interactive user sign-in authentication
    kcsb = KustoConnectionStringBuilder.with_interactive_login(cluster)
    client = KustoClient(kcsb)
    return client

def execute_kusto_query(query: str, client: KustoClient, database: str):
    """
    Execute a Kusto query and return the results as a list of dictionaries.
    """
    try:
        response = client.execute(database, query)
        results = []

        columns = [col.column_name for col in response.primary_results[0].columns]

        for row in response.primary_results[0]:
            row_dict = {columns[i]: row[i] for i in range(len(columns))}
            results.append(row_dict)

        return results
    except KustoServiceError as e:
        print("Query execution failed:", e)
        return None

def execute_kusto_query_df(query: str, client: KustoClient, database: str) -> pd.DataFrame:
    """
    Execute a Kusto query and return the results as a Pandas DataFrame.
    """
    results = execute_kusto_query(query, client, database)
    if results:
        return pd.DataFrame(results)
    else:
        return pd.DataFrame()

if __name__ == "__main__":
    client = get_kusto_client(CLUSTER)

    # Example query
    query = "StormEvents | take 2"
    results = execute_kusto_query(query, client, DATABASE)

    # 1. Returns a dictionary of lists
    results_list = execute_kusto_query(query, client, DATABASE)
    if results_list:
        print("List of dicts result:")
        for row in results_list:
            print(row)
    else:
        print("Query failed or returned no data.")

    # 2. Returns a Pandas DataFrame
    results_df = execute_kusto_query_df(query, client, DATABASE)
    if not results_df.empty:
        print("\nPandas DataFrame result:")
        print(results_df)
    else:
        print("Query failed or returned no data.")