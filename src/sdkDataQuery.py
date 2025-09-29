"""

Azure SDK Usage Data Query Server

This module provides table-specific SQL MCP tools for querying Azure SDK usage data.
Supports both SQL queries for structured data and KQL queries as fallback.

USAGE STRATEGY:
1. First try table-specific SQL tools (generateSQLBy...) for structured queries on enabled tables
2. Use generateKQLFromTemplate as fallback when SQL tables cannot satisfy requirements

SQL TOOLS: Best for monthly aggregation, product analysis, subscription data, version tracking
KQL TOOL: Fallback for complex queries, real-time data, or when SQL tables lack required dimensions

"""
import sys
from mcp.server.fastmcp import FastMCP
from src.config import MCP_PORT
from src.services.sql_mcp_tools import SQLServerMCPTools
from src.services.kusto_mcp_tools import KQLGeneratorMCP
from src.utils.file_utils import load_and_format_prompt

def create_sdk_usage_mcp_server():
    """Create and configure the MCP server with table-specific SQL generation tools"""
    mcp = FastMCP("create_sdk_usage_mcp_server", stateless_http=True, port=MCP_PORT)
    
    mcpSqltools = SQLServerMCPTools()
    mcpKustoTools = KQLGeneratorMCP()

    @mcp.tool()
    async def genSQLByMonthProductSubscriptionId(user_question: str):
        """
        Generate SQL query for AMEConciseFiteredNewProductCCIDCustomerSubscriptionId table.
        
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
        
        **USE AS FALLBACK**: This tool should be used ONLY when none of the table-specific SQL tools 
        (generateSQLBy...) can satisfy your query requirements.
        
        Try SQL tools first for:
        - Monthly/quarterly/yearly aggregation
        - Product, subscription, version analysis  
        - HTTP method, OS, provider filtering
        - Structured data in enabled tables
        
        Use this KQL tool when:
        - None of the 14 enabled SQL tables contain required data dimensions
        - Need real-time or recent data (last 48 hours)
        - Require complex multi-dimensional analysis beyond SQL table capabilities
        - Need custom time ranges or advanced analytics functions
        
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
