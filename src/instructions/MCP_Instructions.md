# Azure SDK Usage Data Query MCP Instructions

This MCP provides two ways to query data from the Azure Resource Manager (ARM) telemetry system.
All data originates from the HttpIncomingRequests table in the ARMProd Kusto cluster, 
which is part of the core ARM Data set.

## ARM Data Overview

ARM Data records all control-plane operations that go through Azure Resource Manager.
It includes every incoming HTTP request, execution status, and metadata used for performance monitoring, 
diagnostics, and behavioral analysis.

HttpIncomingRequests is a detailed, near real-time log of all requests handled by ARM.
It captures information such as:
- Timestamp: when the request reached ARM
- RequestId: unique identifier for the request
- OperationName: the operation performed (e.g., Microsoft.Compute/virtualMachines/read)
- SubscriptionId: the associated subscription
- CallerIpAddress: client IP address
- HttpStatusCode: HTTP response code
- DurationMs: request processing time in milliseconds
- Region: processing region
- ClientRequestId: client-provided correlation ID

## 🔍 CRITICAL DATA SCOPE DIFFERENCE

### 1. SQL Server Query Tools (genSQLBy...)
- **Data Source**: Pre-aggregated subset of HttpIncomingRequests
- **Scope**: ONLY SDK-related requests (requests with SDK user-agents)
- **Use for**: SDK-to-SDK comparisons, SDK adoption metrics, SDK performance analysis
- **Cannot answer**: "What % of total ARM calls are SDK calls?" - only shows SDK data

### 2. Kusto Query Tool (generateKQLFromTemplate)  
- **Data Source**: Complete HttpIncomingRequests table in ARMProd
- **Scope**: ALL ARM requests (SDK + non-SDK: portal, CLI, REST API, ARM templates, etc.)
- **Use for**: SDK vs total ARM analysis, complete traffic analysis, broader telemetry investigation
- **Can answer**: "What % of total ARM calls are SDK calls?" - includes all request types

## 🚨 TOOL SELECTION RULES

- Question about SDK vs TOTAL ARM traffic → **MUST use generateKQLFromTemplate**
- Question comparing different SDKs → **use genSQLBy... tools**  
- Question about SDK adoption/trends → **use genSQLBy... tools**
- Question about complete ARM telemetry → **use generateKQLFromTemplate**

The SQL tools are a subset of what KQL can access - SQL cannot see non-SDK traffic.