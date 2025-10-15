"""

Azure SDK Usage Data Query Server

This module provides table-specific SQL MCP tools for querying Azure SDK usage data.
Supports both SQL queries for structured data and KQL queries for broader telemetry analysis.

🔍 CRITICAL DATA SCOPE UNDERSTANDING:
- SQL Tools: Query pre-aggregated tables containing ONLY SDK request data
- KQL Tool: Query raw HttpIncomingRequests containing ALL ARM requests (SDK + non-SDK)

USAGE STRATEGY:
1. FIRST: Call analyzeUserIntent(user_question) to get tool recommendation
2. For SDK vs TOTAL ARM analysis → MUST use generateKQLFromTemplate (only tool with all data)
3. For SDK-only analysis → use generateSQLBy... tools (faster, structured)
4. For fallback scenarios → use generateKQLFromTemplate when SQL lacks required dimensions

CRITICAL DECISION KEYWORDS:
- "total ARM", "vs total", "SDK percentage", "non-SDK" → KQL REQUIRED
- "SDK adoption", "SDK comparison", "Track1 vs Track2" → SQL APPROPRIATE

SQL TOOLS: Best for SDK adoption, SDK comparisons, SDK performance within SDK ecosystem
KQL TOOL: Required for SDK vs total traffic, complete ARM telemetry, non-SDK data inclusion

"""
import sys
from mcp.server.fastmcp import FastMCP
from src.config import MCP_PORT
from src.services.sql_mcp_tools import SQLServerMCPTools
from src.services.kusto_mcp_tools import KQLGeneratorMCP
from src.utils.file_utils import load_and_format_prompt

def analyze_user_intent(user_question: str) -> str:
    """
    Analyze user question to provide tool selection guidance.
    This is a diagnostic function to help identify the right tool.
    
    Returns:
        str: Analysis with tool recommendation and reasoning
    """
    question_lower = user_question.lower()
    
    # Critical keywords that REQUIRE KQL (total ARM data)
    total_arm_indicators = [
        'total arm', 'all arm', 'vs total', 'percentage of total', '% of total',
        'sdk vs arm', 'sdk percentage', 'importance of sdk', 'vs all requests',
        'non-sdk', 'portal', 'cli', 'powershell', 'rest api', 'arm templates',
        'all requests', 'total requests', 'complete traffic', 'overall arm'
    ]
    
    # Keywords that suggest SQL is sufficient (SDK-only analysis)
    sdk_only_indicators = [
        'sdk adoption', 'sdk comparison', 'track1 vs track2', 'sdk trends',
        'between sdks', 'among sdks', 'sdk migration', 'language version',
        'package version', 'api version', 'sdk performance', 'sdk usage'
    ]
    
    found_total_arm = [kw for kw in total_arm_indicators if kw in question_lower]
    found_sdk_only = [kw for kw in sdk_only_indicators if kw in question_lower]
    
    if found_total_arm:
        return f"🚨 KQL REQUIRED: Question contains total ARM indicators: {found_total_arm}. SQL cannot answer this - it only has SDK data, not complete ARM traffic."
    elif found_sdk_only:
        return f"✅ SQL APPROPRIATE: Question focuses on SDK-only analysis: {found_sdk_only}. Use genSQLBy... tools for faster, structured queries."
    else:
        return f"⚠️ UNCLEAR: Could not determine if question needs total ARM data or SDK-only data. Consider: Does the question need non-SDK traffic (portal, CLI, etc.)? If yes → KQL. If no → SQL."

def create_sdk_usage_mcp_server():
    """Create and configure the MCP server with table-specific SQL generation tools"""
    mcp = FastMCP(
        "create_sdk_usage_mcp_server", 
        stateless_http=True, 
        port=MCP_PORT,
        instructions="""This MCP provides two ways to query data from the Azure Resource Manager (ARM) telemetry system.
    All data originates from the HttpIncomingRequests table in the ARMProd Kusto cluster, 
which is part of the core ARM Data set.

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

🔍 CRITICAL DATA SCOPE DIFFERENCE:

1. SQL Server Query Tools (genSQLBy...)
   - Data Source: Pre-aggregated subset of HttpIncomingRequests
   - Scope: ONLY SDK-related requests (requests with SDK user-agents)
   - Use for: SDK-to-SDK comparisons, SDK adoption metrics, SDK performance analysis
   - Cannot answer: "What % of total ARM calls are SDK calls?" - only shows SDK data

2. Kusto Query Tool (generateKQLFromTemplate)  
   - Data Source: Complete HttpIncomingRequests table in ARMProd
   - Scope: ALL ARM requests (SDK + non-SDK: portal, CLI, REST API, ARM templates, etc.)
   - Use for: SDK vs total ARM analysis, complete traffic analysis, broader telemetry investigation
   - Can answer: "What % of total ARM calls are SDK calls?" - includes all request types

🚨 TOOL SELECTION RULES:
- Question about SDK vs TOTAL ARM traffic → MUST use generateKQLFromTemplate
- Question comparing different SDKs → use genSQLBy... tools  
- Question about SDK adoption/trends → use genSQLBy... tools
- Question about complete ARM telemetry → use generateKQLFromTemplate

The SQL tools are a subset of what KQL can access - SQL cannot see non-SDK traffic.
""")
    
    mcpSqltools = SQLServerMCPTools()
    mcpKustoTools = KQLGeneratorMCP()

    @mcp.tool()
    async def analyzeUserIntent(user_question: str):
        """
        Analyze user question to determine the appropriate tool selection.
        Use this FIRST to understand which tool (SQL vs KQL) to use for a question.
        
        This tool helps avoid the mistake of using SQL tools for questions that require
        total ARM data (which only KQL can provide).
        
        Args:
            user_question: The user's natural language question
            
        Returns:
            Analysis with tool recommendation and reasoning
        """
        return analyze_user_intent(user_question)

    @mcp.tool()
    async def genSQLByMonthProductSubscriptionId(user_question: str):
        """
        Generate SQL query for AMEConciseFiteredNewProductCCIDCustomerSubscriptionId table.
        
        🔍 DATA SCOPE: SDK requests only - pre-filtered Azure SDK usage data
        ❌ CANNOT answer: "What % of total ARM calls are SDK calls?" - only shows SDK data
        ✅ USE FOR: SDK adoption metrics, subscription-level SDK analysis, SDK comparisons
        
        ⚠️ For SDK vs TOTAL ARM traffic analysis, use generateKQLFromTemplate instead
        
        Table Description: Filtered Azure SDK usage data by product, and subscription ID
        
        Available Columns:
        - Month: The month of the data in YYYY-MM-01 format (string, format: date, pattern: ^\\d{4}-\\d{2}-01$)
        - Product: Azure SDK product name (string, enum: [".Net Code-gen", ".Net Fluent", "Ansible", "AzureCLI", "AzurePowershell", "Go-SDK", "Java Fluent Lite", "Java Fluent Premium", "JavaScript", "JavaScript (Node.JS)", "JavaScript RLC", "PHP-SDK", "Python-SDK", "Ruby-SDK", "Rust", "Terraform", "VS Code Azure Extension"])
        - TrackInfo: SDK track information (Track 1 or Track 2) (string, enum: ["Track1", "Track2"])
        - SubscriptionId: Azure subscription identifier (string, pattern: ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$)
        - RequestCount: Number of API requests made (integer, minimum: 0)
        
        Args:
            user_question: A natural language question about the data
            
        Returns:
            A prompt for generating SQL query for this specific table
        """
        return load_and_format_prompt("AMEConciseFiteredNewProductCCIDCustomerSubscriptionId", user_question, __file__)

    @mcp.tool()
    async def genSQLByMonthProduct(user_question: str):
        """
        Generate SQL query for AMEConciseSubReqCCIDCountByMonthProduct table.
        
        🔍 DATA SCOPE: SDK requests only - pre-filtered Azure SDK usage data
        ❌ CANNOT answer: "What % of total ARM calls are SDK calls?" - only shows SDK data
        ✅ USE FOR: SDK adoption metrics, product comparison, SDK trend analysis
        
        ⚠️ For SDK vs TOTAL ARM traffic analysis, use generateKQLFromTemplate instead
        
        Table Description: Subscription, request, and CCID counts by month and product
        
        Available Columns:
        - Month: The month of the data in YYYY-MM-01 format (string, format: date, pattern: ^\\d{4}-\\d{2}-01$)
        - Product: Azure SDK product name (string, enum: [".Net Code-gen", ".Net Fluent", "Ansible", "AzureCLI", "AzurePowershell", "Go-SDK", "Java Fluent Lite", "Java Fluent Premium", "JavaScript", "JavaScript (Node.JS)", "JavaScript RLC", "PHP-SDK", "Python-SDK", "Ruby-SDK", "Rust", "Terraform", "VS Code Azure Extension"])
        - RequestCount: Number of API requests made (integer, minimum: 0)
        - SubscriptionCount: Number of unique subscriptions (integer, minimum: 0)
        
        Args:
            user_question: A natural language question about the data
            
        Returns:
            A prompt for generating SQL query for this specific table
        """
        return load_and_format_prompt("AMEConciseSubReqCCIDCountByMonthProduct", user_question, __file__)

    @mcp.tool()
    async def genSQLByMonthProductHttpMethod(user_question: str):
        """
        Generate SQL query for AMEConciseSubReqCCIDCountByMonthProductHttpMethod table.
        
        🔍 DATA SCOPE: SDK requests only - pre-filtered Azure SDK usage data
        ❌ CANNOT answer: "What % of total ARM calls are SDK calls?" - only shows SDK data
        ✅ USE FOR: SDK HTTP method analysis, product-specific method patterns, SDK behavior analysis
        
        ⚠️ For SDK vs TOTAL ARM traffic analysis, use generateKQLFromTemplate instead
        
        Table Description: Subscription, request, and CCID counts by month, product, and HTTP method
        
        Available Columns:
        - Month: The month of the data in YYYY-MM-01 format (string, format: date, pattern: ^\\d{4}-\\d{2}-01$)
        - Product: Azure SDK product name (string, enum: [".Net Code-gen", ".Net Fluent", "Ansible", "AzureCLI", "AzurePowershell", "Go-SDK", "Java Fluent Lite", "Java Fluent Premium", "JavaScript", "JavaScript (Node.JS)", "JavaScript RLC", "PHP-SDK", "Python-SDK", "Ruby-SDK", "Rust", "Terraform", "VS Code Azure Extension"])
        - HttpMethod: HTTP method used for the request (string, enum: ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
        - RequestCount: Number of API requests made (integer, minimum: 0)
        - SubscriptionCount: Number of unique subscriptions (integer, minimum: 0)
        
        Args:
            user_question: A natural language question about the data
            
        Returns:
            A prompt for generating SQL query for this specific table
        """
        return load_and_format_prompt("AMEConciseSubReqCCIDCountByMonthProductHttpMethod", user_question, __file__)

    @mcp.tool()
    async def genSQLByMonthProductOS(user_question: str):
        """
        Generate SQL query for AMEConciseSubReqCCIDCountByMonthProductOS table.
        
        🔍 DATA SCOPE: SDK requests only - pre-filtered Azure SDK usage data
        ❌ CANNOT answer: "What % of total ARM calls are SDK calls?" - only shows SDK data
        ✅ USE FOR: SDK OS distribution analysis, platform-specific SDK usage, client environment patterns
        
        ⚠️ For SDK vs TOTAL ARM traffic analysis, use generateKQLFromTemplate instead
        
        Table Description: Subscription, request, and CCID counts by month, product, and operating system
        
        Available Columns:
        - Month: The month of the data in YYYY-MM-01 format (string, format: date, pattern: ^\\d{4}-\\d{2}-01$)
        - Product: Azure SDK product name (string, enum: [".Net Code-gen", ".Net Fluent", "Ansible", "AzureCLI", "AzurePowershell", "Go-SDK", "Java Fluent Lite", "Java Fluent Premium", "JavaScript", "JavaScript (Node.JS)", "JavaScript RLC", "PHP-SDK", "Python-SDK", "Ruby-SDK", "Rust", "Terraform", "VS Code Azure Extension"])
        - OS: Operating system of the client making the request (string, enum: ["Windows", "Linux", "MacOS", "Unknown"])
        - RequestCount: Number of API requests made (integer, minimum: 0)
        - SubscriptionCount: Number of unique subscriptions (integer, minimum: 0)
        
        Args:
            user_question: A natural language question about the data
            
        Returns:
            A prompt for generating SQL query for this specific table
        """
        return load_and_format_prompt("AMEConciseSubReqCCIDCountByMonthProductOS", user_question, __file__)

    @mcp.tool()
    async def genSQLByMonthProductProviderTrackInfo(user_question: str):
        """
        Generate SQL query for AMEConciseSubReqCCIDCountByMonthProductProviderTrackInfo table.
        
        🔍 DATA SCOPE: SDK requests only - pre-filtered Azure SDK usage data
        ❌ CANNOT answer: "What % of total ARM calls are SDK calls?" - only shows SDK data
        ✅ USE FOR: SDK usage by Azure service provider, Track1 vs Track2 analysis, service-specific SDK adoption
        
        ⚠️ For SDK vs TOTAL ARM traffic analysis, use generateKQLFromTemplate instead
        
        Table Description: Subscription, request, and CCID counts by month, product, provider, and track info
        
        Available Columns:
        - Month: The month of the data in YYYY-MM-01 format (string, format: date, pattern: ^\\d{4}-\\d{2}-01$)
        - Product: Azure SDK product name (string, enum: [".Net Code-gen", ".Net Fluent", "Ansible", "AzureCLI", "AzurePowershell", "Go-SDK", "Java Fluent Lite", "Java Fluent Premium", "JavaScript", "JavaScript (Node.JS)", "JavaScript RLC", "PHP-SDK", "Python-SDK", "Ruby-SDK", "Rust", "Terraform", "VS Code Azure Extension"])
        - Provider: Azure resource provider name (string)
        - TrackInfo: SDK track information (Track 1 or Track 2) (string, enum: ["Track1", "Track2"])
        - RequestCount: Number of API requests made (integer, minimum: 0)
        - SubscriptionCount: Number of unique subscriptions (integer, minimum: 0)
        
        Args:
            user_question: A natural language question about the data
            
        Returns:
            A prompt for generating SQL query for this specific table
        """
        return load_and_format_prompt("AMEConciseSubReqCCIDCountByMonthProductProviderTrackInfo", user_question, __file__)

    @mcp.tool()
    async def genSQLByMonthProductProviderTrackInfoApiVersion(user_question: str):
        """
        Generate SQL query for AMEConciseSubReqCCIDCountByMonthProductProviderTrackInfoApiVersion table.
        
        🔍 DATA SCOPE: SDK requests only - pre-filtered Azure SDK usage data
        ❌ CANNOT answer: "What % of total ARM calls are SDK calls?" - only shows SDK data
        ✅ USE FOR: SDK API version usage patterns, provider-specific SDK adoption by version
        
        ⚠️ For SDK vs TOTAL ARM traffic analysis, use generateKQLFromTemplate instead
        
        Table Description: Subscription, request, and CCID counts by month, product, provider, track info, and API version
        
        Available Columns:
        - Month: The month of the data in YYYY-MM-01 format (string, format: date, pattern: ^\\d{4}-\\d{2}-01$)
        - Product: Azure SDK product name (string, enum: [".Net Code-gen", ".Net Fluent", "Ansible", "AzureCLI", "AzurePowershell", "Go-SDK", "Java Fluent Lite", "Java Fluent Premium", "JavaScript", "JavaScript (Node.JS)", "JavaScript RLC", "PHP-SDK", "Python-SDK", "Ruby-SDK", "Rust", "Terraform", "VS Code Azure Extension"])
        - Provider: Azure resource provider name (string)
        - TrackInfo: SDK track information (Track 1 or Track 2) (string, enum: ["Track1", "Track2"])
        - ApiVersion: Version of the Azure API being used (string, pattern: ^\\d{4}-\\d{2}-\\d{2}(-preview)?$)
        - RequestCount: Number of API requests made (integer, minimum: 0)
        - SubscriptionCount: Number of unique subscriptions (integer, minimum: 0)
        
        Args:
            user_question: A natural language question about the data
            
        Returns:
            A prompt for generating SQL query for this specific table
        """
        return load_and_format_prompt("AMEConciseSubReqCCIDCountByMonthProductProviderTrackInfoApiVersion", user_question, __file__)

    @mcp.tool()
    async def genSQLByMonthProductProviderTrackInfoPUT(user_question: str):
        """
        Generate SQL query for AMEConciseSubReqCCIDCountByMonthProductProviderTrackInfoPUT table.
        
        🔍 DATA SCOPE: SDK requests only - pre-filtered Azure SDK usage data
        ❌ CANNOT answer: "What % of total ARM calls are SDK calls?" - only shows SDK data
        ✅ USE FOR: SDK PUT operation analysis, write-heavy SDK usage patterns by provider
        
        ⚠️ For SDK vs TOTAL ARM traffic analysis, use generateKQLFromTemplate instead
        
        Table Description: PUT operation subscription, request, and CCID counts by month, product, provider, and track info
        
        Available Columns:
        - Month: The month of the data in YYYY-MM-01 format (string, format: date, pattern: ^\\d{4}-\\d{2}-01$)
        - Product: Azure SDK product name (string, enum: [".Net Code-gen", ".Net Fluent", "Ansible", "AzureCLI", "AzurePowershell", "Go-SDK", "Java Fluent Lite", "Java Fluent Premium", "JavaScript", "JavaScript (Node.JS)", "JavaScript RLC", "PHP-SDK", "Python-SDK", "Ruby-SDK", "Rust", "Terraform", "VS Code Azure Extension"])
        - Provider: Azure resource provider name (string)
        - TrackInfo: SDK track information (Track 1 or Track 2) (string, enum: ["Track1", "Track2"])
        - RequestCount: Number of API requests made (integer, minimum: 0)
        - SubscriptionCount: Number of unique subscriptions (integer, minimum: 0)
        
        Args:
            user_question: A natural language question about the data
            
        Returns:
            A prompt for generating SQL query for this specific table
        """
        return load_and_format_prompt("AMEConciseSubReqCCIDCountByMonthProductProviderTrackInfoPUT", user_question, __file__)

    @mcp.tool()
    async def genSQLByMonthProductTrackInfo(user_question: str):
        """
        Generate SQL query for AMEConciseSubReqCCIDCountByMonthProductTrackInfo table.
        
        🔍 DATA SCOPE: SDK requests only - pre-filtered Azure SDK usage data
        ❌ CANNOT answer: "What % of total ARM calls are SDK calls?" - only shows SDK data
        ✅ USE FOR: Track1 vs Track2 SDK adoption analysis, SDK migration patterns
        
        ⚠️ For SDK vs TOTAL ARM traffic analysis, use generateKQLFromTemplate instead
        
        Table Description: Subscription, request, and CCID counts by month, product, and track info
        
        Available Columns:
        - Month: The month of the data in YYYY-MM-01 format (string, format: date, pattern: ^\\d{4}-\\d{2}-01$)
        - Product: Azure SDK product name (string, enum: [".Net Code-gen", ".Net Fluent", "Ansible", "AzureCLI", "AzurePowershell", "Go-SDK", "Java Fluent Lite", "Java Fluent Premium", "JavaScript", "JavaScript (Node.JS)", "JavaScript RLC", "PHP-SDK", "Python-SDK", "Ruby-SDK", "Rust", "Terraform", "VS Code Azure Extension"])
        - TrackInfo: SDK track information (Track 1 or Track 2) (string, enum: ["Track1", "Track2"])
        - RequestCount: Number of API requests made (integer, minimum: 0)
        - SubscriptionCount: Number of unique subscriptions (integer, minimum: 0)
        
        Args:
            user_question: A natural language question about the data
            
        Returns:
            A prompt for generating SQL query for this specific table
        """
        return load_and_format_prompt("AMEConciseSubReqCCIDCountByMonthProductTrackInfo", user_question, __file__)

    @mcp.tool()
    async def genSQLByMonthProductTrackInfoMinorLanguageVersion(user_question: str):
        """
        Generate SQL query for AMEConciseSubReqCountByMonthProductMinorLanguageVersion table.
        
        🔍 DATA SCOPE: SDK requests only - pre-filtered Azure SDK usage data
        ❌ CANNOT answer: "What % of total ARM calls are SDK calls?" - only shows SDK data
        ✅ USE FOR: SDK language version adoption analysis, runtime version patterns
        
        ⚠️ For SDK vs TOTAL ARM traffic analysis, use generateKQLFromTemplate instead
        
        Table Description: Subscription and request counts by month, product, track info, and minor language version
        
        Available Columns:
        - Month: The month of the data in YYYY-MM-01 format (string, format: date, pattern: ^\\d{4}-\\d{2}-01$)
        - RequestCount: Number of API requests made (integer, minimum: 0)
        - SubscriptionCount: Number of unique subscriptions (integer, minimum: 0)
        - Product: Azure SDK product name (string, enum: [".Net Code-gen", ".Net Fluent", "Ansible", "AzureCLI", "AzurePowershell", "Go-SDK", "Java Fluent Lite", "Java Fluent Premium", "JavaScript", "JavaScript (Node.JS)", "JavaScript RLC", "PHP-SDK", "Python-SDK", "Ruby-SDK", "Rust", "Terraform", "VS Code Azure Extension"])
        - TrackInfo: SDK track information (Track 1 or Track 2) (string, enum: ["Track1", "Track2"])
        - MinorLanguageVersion: Minor version of the programming language
        
        Args:
            user_question: A natural language question about the data
            
        Returns:
            A prompt for generating SQL query for this specific table
        """
        return load_and_format_prompt("AMEConciseSubReqCountByMonthProductMinorLanguageVersion", user_question, __file__)

    @mcp.tool()
    async def genSQLByMonthProductTrackInfoMinorLanguageVersionPatchLanguageVersion(user_question: str):
        """
        Generate SQL query for AMEConciseSubReqCountByMonthProductPatchLanguageVersion table.
        
        🔍 DATA SCOPE: SDK requests only - pre-filtered Azure SDK usage data
        ❌ CANNOT answer: "What % of total ARM calls are SDK calls?" - only shows SDK data
        ✅ USE FOR: Detailed SDK version analysis, patch-level adoption patterns
        
        ⚠️ For SDK vs TOTAL ARM traffic analysis, use generateKQLFromTemplate instead
        
        Table Description: Subscription and request counts by month, product, track info, patch, and minor language versions
        
        Available Columns:
        - Month: The month of the data in YYYY-MM-01 format (string, format: date, pattern: ^\\d{4}-\\d{2}-01$)
        - RequestCount: Number of API requests made (integer, minimum: 0)
        - SubscriptionCount: Number of unique subscriptions (integer, minimum: 0)
        - Product: Azure SDK product name (string, enum: [".Net Code-gen", ".Net Fluent", "Ansible", "AzureCLI", "AzurePowershell", "Go-SDK", "Java Fluent Lite", "Java Fluent Premium", "JavaScript", "JavaScript (Node.JS)", "JavaScript RLC", "PHP-SDK", "Python-SDK", "Ruby-SDK", "Rust", "Terraform", "VS Code Azure Extension"])
        - TrackInfo: SDK track information (Track 1 or Track 2) (string, enum: ["Track1", "Track2"])
        - PatchLanguageVersion: Patch version of the programming language
        - MinorLanguageVersion: Minor version of the programming language
        
        Args:
            user_question: A natural language question about the data
            
        Returns:
            A prompt for generating SQL query for this specific table
        """
        return load_and_format_prompt("AMEConciseSubReqCountByMonthProductPatchLanguageVersion", user_question, __file__)

    @mcp.tool()
    async def genSQLReqCountByMonthTrackInfoPackageNamePackageVersionGoVersionForGo(user_question: str):
        """
        Generate SQL query for AMEGoSDKReqCountCustomerDataByMonth table.
        
        🔍 DATA SCOPE: SDK requests only - pre-filtered Azure SDK usage data
        ❌ CANNOT answer: "What % of total ARM calls are SDK calls?" - only shows SDK data
        ✅ USE FOR: Go SDK-specific analysis, Go package and version patterns
        
        ⚠️ For SDK vs TOTAL ARM traffic analysis, use generateKQLFromTemplate instead
        
        Table Description: Go SDK customer request counts aggregated by month
        
        Available Columns:
        - RequestsDate: Date when the requests were made in YYYY-MM-01 format (string, format: date, pattern: ^\\d{4}-\\d{2}-01$)
        - RequestCount: Number of API requests made (integer, minimum: 0)
        - GoVersion: Version of Go programming language
        - PackageName: Name of the Go SDK package
        - PackageVersion: Version of the Go SDK package
        - IsTrack2: Boolean indicating if this is Track 2 SDK (boolean)
        
        Args:
            user_question: A natural language question about the data
            
        Returns:
            A prompt for generating SQL query for this specific table
        """
        return load_and_format_prompt("AMEGoSDKReqCountCustomerDataByMonth", user_question, __file__)

    @mcp.tool()
    async def genSQLSubCountByMonthPackageNamePackageVersionForGo(user_question: str):
        """
        Generate SQL query for AMEGoSDKSubCountCustomerDataByMonthPackageName table.
        
        🔍 DATA SCOPE: SDK requests only - pre-filtered Azure SDK usage data
        ❌ CANNOT answer: "What % of total ARM calls are SDK calls?" - only shows SDK data
        ✅ USE FOR: Go SDK package adoption analysis, Go-specific subscription patterns
        
        ⚠️ For SDK vs TOTAL ARM traffic analysis, use generateKQLFromTemplate instead
        
        Table Description: Go SDK subscription counts by month and package name
        
        Available Columns:
        - RequestsDate: Date when the requests were made in YYYY-MM-01 format (string, format: date, pattern: ^\\d{4}-\\d{2}-01$)
        - PackageName: Name of the Go SDK package
        - PackageVersion: Version of the Go SDK package
        - SubscriptionCount: Number of unique subscriptions (integer, minimum: 0)
        
        Args:
            user_question: A natural language question about the data
            
        Returns:
            A prompt for generating SQL query for this specific table
        """
        return load_and_format_prompt("AMEGoSDKSubCountCustomerDataByMonthPackageName", user_question, __file__)

    @mcp.tool()
    async def genSQLSubCountByMonthTrackInfoForGo(user_question: str):
        """
        Generate SQL query for AMEGoSDKSubCountCustomerDataByMonthTrackInfo table.
        
        🔍 DATA SCOPE: SDK requests only - pre-filtered Azure SDK usage data
        ❌ CANNOT answer: "What % of total ARM calls are SDK calls?" - only shows SDK data
        ✅ USE FOR: Go SDK Track1/Track2 adoption analysis, Go migration patterns
        
        ⚠️ For SDK vs TOTAL ARM traffic analysis, use generateKQLFromTemplate instead
        
        Table Description: Go SDK subscription counts by month and track info
        
        Available Columns:
        - RequestsDate: Date when the requests were made in YYYY-MM-01 format (string, format: date, pattern: ^\\d{4}-\\d{2}-01$)
        - SubscriptionCount: Number of unique subscriptions (integer, minimum: 0)
        - IsTrack2: Boolean indicating if this is Track 2 SDK (boolean)
        
        Args:
            user_question: A natural language question about the data
            
        Returns:
            A prompt for generating SQL query for this specific table
        """
        return load_and_format_prompt("AMEGoSDKSubCountCustomerDataByMonthTrackInfo", user_question, __file__)

    @mcp.tool()
    async def genSQLSubCountByMonthGoVersionForGo(user_question: str):
        """
        Generate SQL query for AMEGoSDKSubCountCustomerDataByMonthVersion table.
        
        🔍 DATA SCOPE: SDK requests only - pre-filtered Azure SDK usage data
        ❌ CANNOT answer: "What % of total ARM calls are SDK calls?" - only shows SDK data
        ✅ USE FOR: Go runtime version analysis, Go SDK version distribution
        
        ⚠️ For SDK vs TOTAL ARM traffic analysis, use generateKQLFromTemplate instead
        
        Table Description: Go SDK subscription counts by month and Go version
        
        Available Columns:
        - RequestsDate: Date when the requests were made in YYYY-MM-01 format (string, format: date, pattern: ^\\d{4}-\\d{2}-01$)
        - SubscriptionCount: Number of unique subscriptions (integer, minimum: 0)
        - GoVersion: Version of Go programming language
        
        Args:
            user_question: A natural language question about the data
            
        Returns:
            A prompt for generating SQL query for this specific table
        """
        return load_and_format_prompt("AMEGoSDKSubCountCustomerDataByMonthVersion", user_question, __file__)

    @mcp.tool()
    async def executeSQLQuery(sql_query: str):
        """
        Execute a SQL query from generateSQLQuery for MS SQL Server.

        Args:
            sql_query: The SQL query string to execute

        Returns:
            A JSON object containing the query results
        """
        return await mcpSqltools.execute_sql_query(sql_query)
    
    @mcp.tool()
    async def generateKQLFromTemplate(user_question: str):
        """
        Generate KQL query based on Azure SDK usage query template and user question
        
        🔍 DATA SCOPE: Complete ARM dataset - includes ALL requests (SDK + non-SDK)
         REQUIRED for questions comparing SDK vs TOTAL ARM traffic 🚨
        
        🔥 TRIGGER KEYWORDS - Use KQL when user question contains:
        - "total ARM", "all ARM", "vs total", "percentage of total", "% of total"
        - "SDK vs ARM", "SDK percentage", "importance of SDK", "SDK calls vs total"
        - "non-SDK", "portal", "CLI", "PowerShell", "REST API", "ARM templates"
        - "all requests", "total requests", "complete traffic", "overall ARM"
        
        Use this KQL tool when:
        ✅ REQUIRED SCENARIOS (ONLY tool with complete data):
        - Calculating SDK percentage of TOTAL ARM calls
        - Comparing SDK vs non-SDK traffic (portal, CLI, REST API, etc.)
        - Questions about "all Azure API calls" or "total ARM requests"
        - Analysis requiring both SDK and non-SDK data
        - Questions like "what % of total ARM calls are SDK calls"
        
        ✅ OPTIONAL SCENARIOS (fallback when SQL can't satisfy):
        - None of the 14 enabled SQL tables contain required data dimensions
        - Need real-time or recent data (last 48 hours)
        - Require complex multi-dimensional analysis beyond SQL table capabilities
        - Need custom time ranges or advanced analytics functions
        
        ❌ Use SQL tools instead for:
        - Monthly/quarterly/yearly SDK-only aggregation
        - Product, subscription, version analysis within SDKs
        - HTTP method, OS, provider filtering for SDK data
        - Structured data in enabled tables (SDK comparisons)
        
        Available SQL tables: AMEConciseFiteredNewProductCCIDCustomerSubscriptionId, 
        AMEConciseSubReqCCIDCountByMonthProduct, AMEConciseSubReqCCIDCountByMonthProductHttpMethod,
        AMEConciseSubReqCCIDCountByMonthProductOS, AMEConciseSubReqCCIDCountByMonthProductProviderTrackInfo,
        AMEConciseSubReqCCIDCountByMonthProductProviderTrackInfoApiVersion, 
        AMEConciseSubReqCCIDCountByMonthProductProviderTrackInfoPUT, 
        AMEConciseSubReqCCIDCountByMonthProductTrackInfo, 
        AMEConciseSubReqCountByMonthProductMinorLanguageVersion,
        AMEConciseSubReqCountByMonthProductPatchLanguageVersion, 
        AMEGoSDKReqCountCustomerDataByMonth, AMEGoSDKSubCountCustomerDataByMonthPackageName,
        AMEGoSDKSubCountCustomerDataByMonthTrackInfo, AMEGoSDKSubCountCustomerDataByMonthVersion
        
        This tool will:
        1. Read src/templates/queries/azure_sdk_usage_query.kql as template
        2. Return user question and template together to AI
        3. Let AI generate new KQL query based on template and question
        
        Args:
            user_question: User's query requirement (e.g.: "Show percentage analysis of Go SDK resource providers last month")
            
        Returns:
            Structured data containing template and user question for AI to generate new KQL query
        """
        return await mcpKustoTools.generate_kql_from_template(user_question)


    return mcp


def start_sdk_usage_query_server():
    """Main entry point for the table-specific SQL MCP server"""
    try:
        print("Starting Azure SDK Usage Data Query Server...")
        print("Server provides SQL tools for structured queries and KQL as fallback")
        print(f"Server running on port {MCP_PORT}")
        
        # Initialize and run the server
        mcp = create_sdk_usage_mcp_server()
        mcp.run(transport="streamable-http")
        
    except Exception as e:
        print(f"Error while running Table-Specific SQL MCP server: {e}", file=sys.stderr)
