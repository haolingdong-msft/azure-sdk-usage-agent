param name string
@description('Primary location for all resources')
param location string = resourceGroup().location
param tags object = {}
param appServicePlanId string
param appSettings object = {}
param runtimeName string 
param runtimeVersion string 
param serviceName string = 'api'
param storageAccountName string

@allowed(['SystemAssigned', 'UserAssigned'])
param identityType string = 'SystemAssigned'

var kind = 'functionapp,linux'

resource stg 'Microsoft.Storage/storageAccounts@2022-09-01' existing = {
  name: storageAccountName
}

// Create a traditional Consumption Function App with managed identity support
module api 'br/public:avm/res/web/site:0.15.1' = {
  name: '${serviceName}-consumption'
  params: {
    kind: kind
    name: name
    location: location
    tags: union(tags, { 'azd-service-name': serviceName})
    serverFarmResourceId: appServicePlanId
    managedIdentities: {
      systemAssigned: true
      userAssignedResourceIds: []
    }
    siteConfig: {
      alwaysOn: false
      linuxFxVersion: '${toUpper(runtimeName)}|${runtimeVersion}'
    }
    appSettingsKeyValuePairs: union(appSettings, {
      // Use managed identity for all storage operations in App Service Plan
      AzureWebJobsStorage__accountName: stg.name
      AzureWebJobsStorage__credential: 'managedidentity'
      AzureWebJobsStorage__blobServiceUri: stg.properties.primaryEndpoints.blob
      AzureWebJobsStorage__queueServiceUri: stg.properties.primaryEndpoints.queue
      AzureWebJobsStorage__tableServiceUri: stg.properties.primaryEndpoints.table
      // App Service Plan doesn't require WEBSITE_CONTENTAZUREFILECONNECTIONSTRING
      // Function runtime settings
      FUNCTIONS_EXTENSION_VERSION: '~4'
      FUNCTIONS_WORKER_RUNTIME: runtimeName
    })
  }
}

output SERVICE_API_NAME string = api.outputs.name
// Ensure output is always string, handle potential null from module output if SystemAssigned is not used
output SERVICE_API_IDENTITY_PRINCIPAL_ID string = identityType == 'SystemAssigned' ? api.outputs.?systemAssignedMIPrincipalId ?? '' : ''
