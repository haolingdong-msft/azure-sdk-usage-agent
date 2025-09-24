# Building an MCP Server with Official MCP SDKs in Azure Functions

This repository is a secondary development based on [Azure-Samples](https://github.com/Azure-Samples/mcp-sdk-functions-hosting-python)
. It contains an MCP server for Azure SDK Data Search, built with the Python MCP SDK on Azure Functions. You can easily test it locally and deploy it remotely with func publish in just a few minutes.

## Prerequisites
Before running or deploying this MCP server, make sure you have the following:

### Required Azure Services
- Azure Functions — to host the MCP server (requires an App Service Plan).
- Azure Storage Account — required by Azure Functions for triggers, logs, and state.
- Azure SQL Server — for querying SDK-related data.
- Application Insights — for monitoring and diagnostics.

### Required Permissions
- Subscription — Contributor role on the target subscription (for deployment with `func publish`).
- SQL Server — *Read-only* access to the target database.
  - Required for both the developer account and the Function App's managed identity.
- Function App — *Storage Blob Data Owner* role on the linked Storage Account.
  - Requires System Assigned Managed Identity to be enabled on the Function App.

### Local Environment Requirements
* [Python 3.12](https://www.python.org/downloads/) installed.
* [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
* [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)
* [Azure Functions Core Tools](https://learn.microsoft.com/azure/azure-functions/functions-run-local?tabs=windows%2Cisolated-process%2Cnode-v4%2Cpython-v2%2Chttp-trigger%2Ccontainer-apps&pivots=programming-language-typescript) (latest version).
* [Visual Studio Code](https://code.visualstudio.com/)
* [Azure Functions extension on Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-azurefunctions)

### Run the server locally

1. Clone the repo and open the sample in Visual Studio Code

    ```shell
    git clone https://github.com/haolingdong-msft/azure-sdk-usage-agent
    ```

1. Create a virtual environment and install the packages in requirements.txt. On Visual Studio Code, this can be done easily by opening command palette (`Ctrl+Shift+P` / `Cmd+Shift+P`), searching for **Python: Create Environment**, and selecting **Venv**
1. In the root directory, activate the virtual environment

    **macOS/Linux:**

    ```bash
    source .venv/bin/activate
    ```

   **Windows Command Prompt:**
  
   ```cmd
   .venv\Scripts\activate.bat
   ```

1. Run `func start`
1. Open _mcp.json_ (in the _vscode_ directory)
1. Start the server by selecting the _Start_ button above the **local-mcp-server**
1. Click on the Copilot icon at the top to open chat, and then change to _Agent_ mode in the question window.
1. Ask "How many request count for js this month?" Copilot should call one of the weather tools to help answer this question.

### Deploy

In the root directory, run `az login`to sign in and select the subscription where you want to deploy. Then run `func azure functionapp publish <YourFunctionAppName> --python` to publish the app.

When the command finishes, your terminal will display output similar to the following:

  ```shell
  Remote build succeeded!
  ```

### Connect to server on Visual Studio Code

1. After deployment completes, navigate to the Function App resource in the Azure portal, as you will need the key from there.
1. Open _mcp.json_ in VS Code.
1. Stop the local server by selecting the _Stop_ button above the **local-mcp-server**
1. Start the remote server by selecting the _Start_ button above the **remote-mcp-server**
1. VS Code will prompt you for the Function App name. Copy it from either the terminal output or the Portal.
1. VS Code will next prompt you for the Function App key. Copy that from the _default_ key on the **Functions** -> **App keys** page in the Azure portal.

>[!TIP]
>In addition to starting an MCP server in _mcp.json_, you can see output of a server by clicking _More..._ -> _Show Output_. The output provides useful information like why a connection might've failed.

## Server authorization using Azure API Management (APIM) WILL DO

In addition to protecting server access through function keys, you can also add APIM in front of the Function app to add an extra layer of security. This sample leverages APIM's policy feature to redirect a client to authenticate with Entra ID before connecting to the MCP server. Specifically, this is achieved by creating two policies on the APIM resource that follow the [MCP authorization specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization#authorization-server-discovery). One policy checks access tokens from incoming requests, and if validation fails, returns a 404 with header containining the path to Protected Resource Metadata (PRM). Another policy returns the PRM, which a client can use to figure out the authorization server (Entra ID in this case) that provides access tokens to the MCP server.

To see the above in action, test connecting to the server using the APIM endpoint instead of the Function app endpoint:

1. Open _mcp.json_ in VS Code
1. Stop the **remote-mcp-server** or **local-mcp-server** servers if still running
1. Start the **remote-mcp-server-apim** server
1. VS Code will prompt you for the APIM resource name
1. Click **Allow** when a window pops up saying the MCP Server wants to authenticate to Microsoft.
1. Sign into your Microsoft account to connect to the server  

### Support for other clients

Since Entra ID doesn't provide native support for DCR (Dynamic Client Registration) and PKCE (Proof Key for Code Exchange) today,the above authorization flow is only supported on VS Code. If you use other clients (like Claude or Cursor), the easier option is to access the MCP server using the Function App endpoint and access key. The other option is to try out an [experimental approach](https://github.com/localden/remote-auth-mcp-apim-py/) that provides a workaround, which also leverages APIM.


## Existing Azure Resources
Here are the details of the existing Azure services used for this MCP server:
| Resource Type            | Name / Identifier                | Region     | SKU / Plan           | Notes / Purpose                                                                 |
| ------------------------ | -------------------------------- | ---------- | -------------------- | ------------------------------------------------------------------------------- |
| **Subscription**         | `Azure SDK Developer Playground` | N/A        | N/A                  | Subscription used for deployment and resource access                            |
| **Resource Group**       | `openai-shared`     | N/A  | N/A                  | Contains Function App, Storage Account, SQL Server, and other related resources |
| **Function App**         | `fuc-sdkusagemcp`       | `East US` | `plan-sdkusagemcp` | Hosts the MCP server; **System Assigned Managed Identity enabled**              |
| **Storage Account**      | `stsdkusagemcp`    | `East US` | `<SKU>`              | Required for Function App triggers, logs, and state                             |
| **Azure SQL Server**     | `azuresdkbi`         | `East US` | `<SKU>`              | Existing independent resource in Azure SDK Engineering System/sdk-mgmt-bi-data; Stores SDK Data; **read-only access** required for Function App and developer. |
| **Application Insights** | `fuc-sdkusagemcp-insight`       | `East US` | `<Pricing Tier>`     | Used for monitoring and diagnostics                                   |
