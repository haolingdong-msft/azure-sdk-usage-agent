targetScope = 'resourceGroup'

@minLength(1)
@maxLength(64)
@description('Name of the the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@minLength(1)
@description('Primary location for all resources & Flex Consumption Function App')
@allowed([
  'australiaeast'
  'brazilsouth'
  'eastus'
  'southeastasia'
  'westeurope'
  'southafricanorth'
  'uaenorth'
])
@metadata({
  azd: {
    type: 'location'
  }
})
param location string
@description('Name of the API service (Function App)')
param apiServiceName string
@description('Name of the App Service Plan')  
param appServicePlanName string
@description('Name of the Storage Account')
param storageAccountName string

var tags = { 'azd-env-name': environmentName }
var functionAppName = apiServiceName

// Create an App Service Plan for Basic tier
module appServicePlan 'br/public:avm/res/web/serverfarm:0.1.1' = {
  name: 'appserviceplan'
  params: {
    name: appServicePlanName
    sku: {
      name: 'B1'
      tier: 'Basic'
    }
    reserved: true
    location: location
    tags: tags
  }
}

module api './app/api.bicep' = {
  name: 'api'
  params: {
    name: functionAppName
    location: location
    tags: tags
    appServicePlanId: appServicePlan.outputs.resourceId
    runtimeName: 'python'
    runtimeVersion: '3.12'
    storageAccountName: storage.outputs.name
    appSettings: {
      PYTHONPATH: '/home/site/wwwroot/.python_packages/lib/site-packages'
    }
  }
}

// Backing storage for Azure functions backend API
module storage 'br/public:avm/res/storage/storage-account:0.8.3' = {
  name: 'storage'
  params: {
    name: storageAccountName
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false // Try with managed identity first
    dnsEndpointType: 'Standard'
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
      bypass: 'AzureServices'
    }
    blobServices: {
      containers: []
    }
    minimumTlsVersion: 'TLS1_2'  // Enforcing TLS 1.2 for better security
    location: location
    tags: tags
  }
}

// App outputs
output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output SERVICE_API_NAME string = api.outputs.SERVICE_API_NAME
output AZURE_FUNCTION_NAME string = api.outputs.SERVICE_API_NAME
