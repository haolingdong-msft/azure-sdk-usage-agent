# Infrastructure as Code (IaC) - Azure Resources

AS YOU HAVE NO PERMISSION ON SUBSCRIPTION.YOU CAN USE THIS.

This folder contains Bicep templates for deploying Azure resources required for the MCP SQL Server application.

## Architecture Overview

The infrastructure creates the following Azure resources:

- **Azure Function App** - Hosts the MCP SQL Server API
- **App Service Plan** - Basic tier (B1) plan for the Function App
- **Storage Account** - Backend storage for the Function App with managed identity access

## Resource Details

### 1. App Service Plan
- **Type**: Basic Plan (B1 tier)
- **Platform**: Linux
- **Billing**: Fixed monthly cost (~$13/month)
- **Scaling**: Manual scaling, supports up to 3 instances
- **Benefits**: More stable performance, supports managed identity for all storage operations

### 2. Azure Function App
- **Runtime**: Python 3.12
- **Platform**: Linux
- **Identity**: System-assigned managed identity
- **Authentication**: Uses managed identity for secure storage access
- **Content Storage**: No longer requires WEBSITE_CONTENTAZUREFILECONNECTIONSTRING (App Service Plan benefit)

### 3. Storage Account
- **Security**: 
  - Blob public access disabled
  - Shared key access disabled (secure managed identity access)
  - Minimum TLS version 1.2
- **Network**: Public access enabled with Azure Services bypass
- **Access Method**: Managed identity authentication for all operations
- **Purpose**: Stores Function App runtime data and application storage needs

## Files Structure

```
infra/
├── README.md                    # This documentation
├── main.bicep                   # Main infrastructure template
├── main.parameters.json         # Parameter configuration
├── abbreviations.json           # Resource naming abbreviations
├── bicepconfig.json            # Bicep configuration
└── app/
    └── api.bicep               # Function App configuration
```

**Note**: The following files have been removed as they are not needed for the current simplified architecture:
- `rbac.bicep` (RBAC permissions will be configured manually)
- `storage-PrivateEndpoint.bicep` (No private networking required)
- `vnet.bicep` (No virtual network required)
- `apim/` and `apim-mcp/` directories (API Management not used)

## Deployment

### Prerequisites
- [Azure Developer CLI (azd)](https://aka.ms/azd-install) installed
- Azure subscription with appropriate permissions
- Valid Azure location from the allowed regions

### Allowed Regions
- Australia East (`australiaeast`)
- Brazil South (`brazilsouth`)
- East US (`eastus`)
- Southeast Asia (`southeastasia`)
- West Europe (`westeurope`)
- South Africa North (`southafricanorth`)
- UAE North (`uaenorth`)

### Deploy with AZD

1. **Initialize the project** (if not already done):
   ```bash
   azd init
   ```

2. **Create or select an environment**:
   
   Check existing environments:
   ```bash
   azd env list
   ```
   
   If you need to create a new environment or the current environment is incorrect:
   ```bash
   azd env new <environment-name>
   ```
   
   Or switch to an existing environment:
   ```bash
   azd env select <environment-name>
   ```

3. **Deploy the infrastructure**:
   ```bash
   azd up
   ```

   You will be prompted to provide:
   - **Environment Name**: Unique identifier for this deployment (if creating new environment)
   - **Location**: Azure region from the allowed list
   - **API Service Name**: Name for the Function App
   - **App Service Plan Name**: Name for the App Service Plan
   - **Storage Account Name**: Name for the Storage Account

### Alternative Deployment Methods

#### Using Environment Variables
Set environment variables before running `azd up`:

```bash
export AZURE_ENV_NAME="my-mcp-env"
export AZURE_LOCATION="eastus"
export AZURE_API_SERVICE_NAME="my-mcp-api"
export AZURE_APP_SERVICE_PLAN_NAME="my-mcp-plan"
export AZURE_STORAGE_ACCOUNT_NAME="mymcpstorage"

azd up
```

#### Using Command Line Parameters
```bash
azd up \
  --set apiServiceName=my-mcp-api \
  --set appServicePlanName=my-mcp-plan \
  --set storageAccountName=mymcpstorage
```

## Parameters

### Required Parameters
| Parameter | Description | Type | Constraints |
|-----------|-------------|------|-------------|
| `environmentName` | Environment identifier | string | 1-64 characters |
| `location` | Azure region | string | Must be from allowed regions list |
| `apiServiceName` | Function App name | string | Must be unique globally |
| `appServicePlanName` | App Service Plan name | string | Must be unique in resource group |
| `storageAccountName` | Storage Account name | string | 3-24 characters, lowercase, alphanumeric only |

## Outputs

After successful deployment, the following outputs are available:

| Output | Description |
|--------|-------------|
| `AZURE_LOCATION` | Deployed region |
| `AZURE_TENANT_ID` | Azure tenant ID |
| `SERVICE_API_NAME` | Function App name |
| `AZURE_FUNCTION_NAME` | Function App name (duplicate) |

## Security Features

- **Managed Identity**: Function App uses system-assigned managed identity for all Azure service authentication
- **No Shared Keys**: Storage account disables shared key access, uses managed identity instead
- **TLS 1.2**: Enforced minimum TLS version
- **Private Access**: Blob public access disabled
- **Network Security**: Proper network ACLs configured
- **Manual RBAC**: Storage permissions configured manually for enhanced security control

## Cost Considerations

### App Service Plan B1 vs Consumption Plan

**Basic Plan (B1) - Current Configuration:**
- **Cost**: ~$13 USD/month fixed cost
- **Benefits**: 
  - Full managed identity support
  - No WEBSITE_CONTENTAZUREFILECONNECTIONSTRING requirement
  - More predictable performance
  - Better for consistent workloads

**Consumption Plan Alternative:**
- **Cost**: Pay-per-execution (can be $0 for low usage)
- **Limitations**: 
  - Requires WEBSITE_CONTENTAZUREFILECONNECTIONSTRING
  - Needs shared key access enabled on storage
  - More complex security configuration

**Storage Account:**
- **Cost**: Minimal (~$1-5/month depending on usage)
- **LRS (Locally Redundant Storage)**: Included in template

## Monitoring & Tagging

All resources are tagged with:
- `azd-env-name`: Environment name for resource organization

## Troubleshooting

### Common Issues

1. **Storage Account Name Conflicts**
   - Storage account names must be globally unique
   - Use only lowercase letters and numbers
   - Length must be 3-24 characters

2. **Region Availability**
   - Ensure the selected region supports all required resource types
   - Check Azure service availability in your chosen region

3. **Permission Issues**
   - Ensure you have Contributor role on the target subscription
   - Verify Azure CLI is authenticated: `az login`

4. **Managed Identity Permissions** (Post-deployment)
   - After deployment, manually assign storage permissions to the Function App's managed identity
   - Required roles: "Storage Blob Data Contributor", "Storage Queue Data Contributor", "Storage Table Data Contributor"
   - Go to Storage Account > Access Control (IAM) > Add role assignment

### Validation

Before deployment, you can validate the template:

```bash
az deployment group validate \
  --resource-group <your-rg> \
  --template-file main.bicep \
  --parameters main.parameters.json
```

## Clean Up

To delete all deployed resources:

```bash
azd down
```

## Support

For issues related to:
- **Infrastructure**: Check this README and Bicep files
- **Application Code**: See main project documentation
- **Azure Services**: Refer to [Azure Documentation](https://docs.microsoft.com/azure/)
