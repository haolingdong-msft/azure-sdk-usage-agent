"""
Table-Specific SQL MCP Server that provides generateSQLBy<tablename> tools
for each enabled table in SQL_Schema.json

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

def tableSpecificSqlMCP():
    """Create and configure the MCP server with table-specific SQL generation tools"""
    mcp = FastMCP("tableSpecificSqlServer", stateless_http=True, port=MCP_PORT)
    
    mcpSqltools = SQLServerMCPTools()
    mcpKustoTools = KQLGeneratorMCP()

    @mcp.tool()
    async def generateSQLByAMEConciseFiteredNewProductCCIDCustomerSubscriptionId(user_question: str):
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
        
        prompt = f"""
You are a SQL query generator for Azure SDK usage analytics. Generate a SQL query for the AMEConciseFiteredNewProductCCIDCustomerSubscriptionId table based on the user question.

TABLE: AMEConciseFiteredNewProductCCIDCustomerSubscriptionId
DESCRIPTION: Filtered Azure SDK usage data by product, and subscription ID

SCHEMA:
- Month (string): The month of the data in YYYY-MM-01 format. Example: '2024-01-01', '2024-02-01'
- Product (string): Azure SDK product name. Valid values: [".Net Code-gen", ".Net Fluent", "Ansible", "AzureCLI", "AzurePowershell", "Go-SDK", "Java Fluent Lite", "Java Fluent Premium", "JavaScript", "JavaScript (Node.JS)", "JavaScript RLC", "PHP-SDK", "Python-SDK", "Ruby-SDK", "Rust", "Terraform", "VS Code Azure Extension"]
- TrackInfo (string): SDK track information. Valid values: ["Track1", "Track2"]
- SubscriptionId (string): Azure subscription identifier in UUID format
- RequestCount (integer): Number of API requests made (≥ 0)

USER QUESTION: {user_question}

Generate a SQL query that answers the user's question using only the columns available in this table. Return only the SQL query without any additional text or formatting.
"""
        
        return prompt

    @mcp.tool()
    async def generateSQLByAMEConciseSubReqCCIDCountByMonthProduct(user_question: str):
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
        
        prompt = f"""
You are a SQL query generator for Azure SDK usage analytics. Generate a SQL query for the AMEConciseSubReqCCIDCountByMonthProduct table based on the user question.

TABLE: AMEConciseSubReqCCIDCountByMonthProduct
DESCRIPTION: Subscription, request, and CCID counts by month and product

SCHEMA:
- Month (string): The month of the data in YYYY-MM-01 format. Example: '2024-01-01', '2024-02-01'
- Product (string): Azure SDK product name. Valid values: [".Net Code-gen", ".Net Fluent", "Ansible", "AzureCLI", "AzurePowershell", "Go-SDK", "Java Fluent Lite", "Java Fluent Premium", "JavaScript", "JavaScript (Node.JS)", "JavaScript RLC", "PHP-SDK", "Python-SDK", "Ruby-SDK", "Rust", "Terraform", "VS Code Azure Extension"]
- RequestCount (integer): Number of API requests made (≥ 0)
- SubscriptionCount (integer): Number of unique subscriptions (≥ 0)

USER QUESTION: {user_question}

Generate a SQL query that answers the user's question using only the columns available in this table. Return only the SQL query without any additional text or formatting.
"""
        
        return prompt

    @mcp.tool()
    async def generateSQLByAMEConciseSubReqCCIDCountByMonthProductHttpMethod(user_question: str):
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
        
        prompt = f"""
You are a SQL query generator for Azure SDK usage analytics. Generate a SQL query for the AMEConciseSubReqCCIDCountByMonthProductHttpMethod table based on the user question.

TABLE: AMEConciseSubReqCCIDCountByMonthProductHttpMethod
DESCRIPTION: Subscription, request, and CCID counts by month, product, and HTTP method

SCHEMA:
- Month (string): The month of the data in YYYY-MM-01 format. Example: '2024-01-01', '2024-02-01'
- Product (string): Azure SDK product name. Valid values: [".Net Code-gen", ".Net Fluent", "Ansible", "AzureCLI", "AzurePowershell", "Go-SDK", "Java Fluent Lite", "Java Fluent Premium", "JavaScript", "JavaScript (Node.JS)", "JavaScript RLC", "PHP-SDK", "Python-SDK", "Ruby-SDK", "Rust", "Terraform", "VS Code Azure Extension"]
- HttpMethod (string): HTTP method used for the request. Valid values: ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
- RequestCount (integer): Number of API requests made (≥ 0)
- SubscriptionCount (integer): Number of unique subscriptions (≥ 0)

USER QUESTION: {user_question}

Generate a SQL query that answers the user's question using only the columns available in this table. Return only the SQL query without any additional text or formatting.
"""
        
        return prompt

    @mcp.tool()
    async def generateSQLByAMEConciseSubReqCCIDCountByMonthProductOS(user_question: str):
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
        
        prompt = f"""
You are a SQL query generator for Azure SDK usage analytics. Generate a SQL query for the AMEConciseSubReqCCIDCountByMonthProductOS table based on the user question.

TABLE: AMEConciseSubReqCCIDCountByMonthProductOS
DESCRIPTION: Subscription, request, and CCID counts by month, product, and operating system

SCHEMA:
- Month (string): The month of the data in YYYY-MM-01 format. Example: '2024-01-01', '2024-02-01'
- Product (string): Azure SDK product name. Valid values: [".Net Code-gen", ".Net Fluent", "Ansible", "AzureCLI", "AzurePowershell", "Go-SDK", "Java Fluent Lite", "Java Fluent Premium", "JavaScript", "JavaScript (Node.JS)", "JavaScript RLC", "PHP-SDK", "Python-SDK", "Ruby-SDK", "Rust", "Terraform", "VS Code Azure Extension"]
- OS (string): Operating system of the client making the request. Valid values: ["Windows", "Linux", "MacOS", "Unknown"]
- RequestCount (integer): Number of API requests made (≥ 0)
- SubscriptionCount (integer): Number of unique subscriptions (≥ 0)

USER QUESTION: {user_question}

Generate a SQL query that answers the user's question using only the columns available in this table. Return only the SQL query without any additional text or formatting.
"""
        
        return prompt

    @mcp.tool()
    async def generateSQLByAMEConciseSubReqCCIDCountByMonthProductProviderTrackInfo(user_question: str):
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
        
        prompt = f"""
You are a SQL query generator for Azure SDK usage analytics. Generate a SQL query for the AMEConciseSubReqCCIDCountByMonthProductProviderTrackInfo table based on the user question.

TABLE: AMEConciseSubReqCCIDCountByMonthProductProviderTrackInfo
DESCRIPTION: Subscription, request, and CCID counts by month, product, provider, and track info

SCHEMA:
- Month (string): The month of the data in YYYY-MM-01 format. Example: '2024-01-01', '2024-02-01'
- Product (string): Azure SDK product name. Valid values: [".Net Code-gen", ".Net Fluent", "Ansible", "AzureCLI", "AzurePowershell", "Go-SDK", "Java Fluent Lite", "Java Fluent Premium", "JavaScript", "JavaScript (Node.JS)", "JavaScript RLC", "PHP-SDK", "Python-SDK", "Ruby-SDK", "Rust", "Terraform", "VS Code Azure Extension"]
- Provider (string): Azure resource provider name (e.g., Microsoft.Storage, Microsoft.Compute, etc.)
- TrackInfo (string): SDK track information. Valid values: ["Track1", "Track2"]
- RequestCount (integer): Number of API requests made (≥ 0)
- SubscriptionCount (integer): Number of unique subscriptions (≥ 0)

USER QUESTION: {user_question}

Generate a SQL query that answers the user's question using only the columns available in this table. Return only the SQL query without any additional text or formatting.
"""
        
        return prompt

    @mcp.tool()
    async def generateSQLByAMEConciseSubReqCCIDCountByMonthProductProviderTrackInfoApiVersion(user_question: str):
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
        
        prompt = f"""
You are a SQL query generator for Azure SDK usage analytics. Generate a SQL query for the AMEConciseSubReqCCIDCountByMonthProductProviderTrackInfoApiVersion table based on the user question.

TABLE: AMEConciseSubReqCCIDCountByMonthProductProviderTrackInfoApiVersion
DESCRIPTION: Subscription, request, and CCID counts by month, product, provider, track info, and API version

SCHEMA:
- Month (string): The month of the data in YYYY-MM-01 format. Example: '2024-01-01', '2024-02-01'
- Product (string): Azure SDK product name. Valid values: [".Net Code-gen", ".Net Fluent", "Ansible", "AzureCLI", "AzurePowershell", "Go-SDK", "Java Fluent Lite", "Java Fluent Premium", "JavaScript", "JavaScript (Node.JS)", "JavaScript RLC", "PHP-SDK", "Python-SDK", "Ruby-SDK", "Rust", "Terraform", "VS Code Azure Extension"]
- Provider (string): Azure resource provider name (e.g., Microsoft.Storage, Microsoft.Compute, etc.)
- TrackInfo (string): SDK track information. Valid values: ["Track1", "Track2"]
- ApiVersion (string): Version of the Azure API being used. Format: YYYY-MM-DD or YYYY-MM-DD-preview (e.g., '2023-01-01', '2023-01-01-preview')
- RequestCount (integer): Number of API requests made (≥ 0)
- SubscriptionCount (integer): Number of unique subscriptions (≥ 0)

USER QUESTION: {user_question}

Generate a SQL query that answers the user's question using only the columns available in this table. Return only the SQL query without any additional text or formatting.
"""
        
        return prompt

    @mcp.tool()
    async def generateSQLByAMEConciseSubReqCCIDCountByMonthProductProviderTrackInfoPUT(user_question: str):
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
        
        prompt = f"""
You are a SQL query generator for Azure SDK usage analytics. Generate a SQL query for the AMEConciseSubReqCCIDCountByMonthProductProviderTrackInfoPUT table based on the user question.

TABLE: AMEConciseSubReqCCIDCountByMonthProductProviderTrackInfoPUT
DESCRIPTION: PUT operation subscription, request, and CCID counts by month, product, provider, and track info

SCHEMA:
- Month (string): The month of the data in YYYY-MM-01 format. Example: '2024-01-01', '2024-02-01'
- Product (string): Azure SDK product name. Valid values: [".Net Code-gen", ".Net Fluent", "Ansible", "AzureCLI", "AzurePowershell", "Go-SDK", "Java Fluent Lite", "Java Fluent Premium", "JavaScript", "JavaScript (Node.JS)", "JavaScript RLC", "PHP-SDK", "Python-SDK", "Ruby-SDK", "Rust", "Terraform", "VS Code Azure Extension"]
- Provider (string): Azure resource provider name (e.g., Microsoft.Storage, Microsoft.Compute, etc.)
- TrackInfo (string): SDK track information. Valid values: ["Track1", "Track2"]
- RequestCount (integer): Number of API requests made for PUT operations (≥ 0)
- SubscriptionCount (integer): Number of unique subscriptions (≥ 0)

NOTE: This table specifically contains data for PUT HTTP operations only.

USER QUESTION: {user_question}

Generate a SQL query that answers the user's question using only the columns available in this table. Return only the SQL query without any additional text or formatting.
"""
        
        return prompt

    @mcp.tool()
    async def generateSQLByAMEConciseSubReqCCIDCountByMonthProductTrackInfo(user_question: str):
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
        
        prompt = f"""
You are a SQL query generator for Azure SDK usage analytics. Generate a SQL query for the AMEConciseSubReqCCIDCountByMonthProductTrackInfo table based on the user question.

TABLE: AMEConciseSubReqCCIDCountByMonthProductTrackInfo
DESCRIPTION: Subscription, request, and CCID counts by month, product, and track info

SCHEMA:
- Month (string): The month of the data in YYYY-MM-01 format. Example: '2024-01-01', '2024-02-01'
- Product (string): Azure SDK product name. Valid values: [".Net Code-gen", ".Net Fluent", "Ansible", "AzureCLI", "AzurePowershell", "Go-SDK", "Java Fluent Lite", "Java Fluent Premium", "JavaScript", "JavaScript (Node.JS)", "JavaScript RLC", "PHP-SDK", "Python-SDK", "Ruby-SDK", "Rust", "Terraform", "VS Code Azure Extension"]
- TrackInfo (string): SDK track information. Valid values: ["Track1", "Track2"]
- RequestCount (integer): Number of API requests made (≥ 0)
- SubscriptionCount (integer): Number of unique subscriptions (≥ 0)

USER QUESTION: {user_question}

Generate a SQL query that answers the user's question using only the columns available in this table. Return only the SQL query without any additional text or formatting.
"""
        
        return prompt

    @mcp.tool()
    async def generateSQLByAMEConciseSubReqCountByMonthProductMinorLanguageVersion(user_question: str):
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
        
        prompt = f"""
You are a SQL query generator for Azure SDK usage analytics. Generate a SQL query for the AMEConciseSubReqCountByMonthProductMinorLanguageVersion table based on the user question.

TABLE: AMEConciseSubReqCountByMonthProductMinorLanguageVersion
DESCRIPTION: Subscription and request counts by month, product, track info, and minor language version

SCHEMA:
- Month (string): The month of the data in YYYY-MM-01 format. Example: '2024-01-01', '2024-02-01'
- RequestCount (integer): Number of API requests made (≥ 0)
- SubscriptionCount (integer): Number of unique subscriptions (≥ 0)
- Product (string): Azure SDK product name. Valid values: [".Net Code-gen", ".Net Fluent", "Ansible", "AzureCLI", "AzurePowershell", "Go-SDK", "Java Fluent Lite", "Java Fluent Premium", "JavaScript", "JavaScript (Node.JS)", "JavaScript RLC", "PHP-SDK", "Python-SDK", "Ruby-SDK", "Rust", "Terraform", "VS Code Azure Extension"]
- TrackInfo (string): SDK track information. Valid values: ["Track1", "Track2"]
- MinorLanguageVersion (string): Minor version of the programming language (e.g., for Python: "3.8", "3.9", "3.10")

USER QUESTION: {user_question}

Generate a SQL query that answers the user's question using only the columns available in this table. Return only the SQL query without any additional text or formatting.
"""
        
        return prompt

    @mcp.tool()
    async def generateSQLByAMEConciseSubReqCountByMonthProductPatchLanguageVersion(user_question: str):
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
        
        prompt = f"""
You are a SQL query generator for Azure SDK usage analytics. Generate a SQL query for the AMEConciseSubReqCountByMonthProductPatchLanguageVersion table based on the user question.

TABLE: AMEConciseSubReqCountByMonthProductPatchLanguageVersion
DESCRIPTION: Subscription and request counts by month, product, track info, patch, and minor language versions

SCHEMA:
- Month (string): The month of the data in YYYY-MM-01 format. Example: '2024-01-01', '2024-02-01'
- RequestCount (integer): Number of API requests made (≥ 0)
- SubscriptionCount (integer): Number of unique subscriptions (≥ 0)
- Product (string): Azure SDK product name. Valid values: [".Net Code-gen", ".Net Fluent", "Ansible", "AzureCLI", "AzurePowershell", "Go-SDK", "Java Fluent Lite", "Java Fluent Premium", "JavaScript", "JavaScript (Node.JS)", "JavaScript RLC", "PHP-SDK", "Python-SDK", "Ruby-SDK", "Rust", "Terraform", "VS Code Azure Extension"]
- TrackInfo (string): SDK track information. Valid values: ["Track1", "Track2"]
- PatchLanguageVersion (string): Patch version of the programming language (e.g., for Python: "3.8.10", "3.9.16")
- MinorLanguageVersion (string): Minor version of the programming language (e.g., for Python: "3.8", "3.9", "3.10")

USER QUESTION: {user_question}

Generate a SQL query that answers the user's question using only the columns available in this table. Return only the SQL query without any additional text or formatting.
"""
        
        return prompt

    @mcp.tool()
    async def generateSQLByAMEGoSDKReqCountCustomerDataByMonth(user_question: str):
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
        
        prompt = f"""
You are a SQL query generator for Azure SDK usage analytics. Generate a SQL query for the AMEGoSDKReqCountCustomerDataByMonth table based on the user question.

TABLE: AMEGoSDKReqCountCustomerDataByMonth
DESCRIPTION: Go SDK customer request counts aggregated by month

SCHEMA:
- RequestsDate (string): Date when the requests were made in YYYY-MM-01 format. Example: '2024-01-01', '2024-02-01'
- RequestCount (integer): Number of API requests made (≥ 0)
- GoVersion (string): Version of Go programming language (e.g., "1.19", "1.20", "1.21")
- PackageName (string): Name of the Go SDK package (e.g., "azblob", "azidentity", "azcore")
- PackageVersion (string): Version of the Go SDK package (e.g., "1.0.0", "1.1.2")
- IsTrack2 (boolean): Boolean indicating if this is Track 2 SDK (true/false)

USER QUESTION: {user_question}

Generate a SQL query that answers the user's question using only the columns available in this table. Return only the SQL query without any additional text or formatting.
"""
        
        return prompt

    @mcp.tool()
    async def generateSQLByAMEGoSDKSubCountCustomerDataByMonthPackageName(user_question: str):
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
        
        prompt = f"""
You are a SQL query generator for Azure SDK usage analytics. Generate a SQL query for the AMEGoSDKSubCountCustomerDataByMonthPackageName table based on the user question.

TABLE: AMEGoSDKSubCountCustomerDataByMonthPackageName
DESCRIPTION: Go SDK subscription counts by month and package name

SCHEMA:
- RequestsDate (string): Date when the requests were made in YYYY-MM-01 format. Example: '2024-01-01', '2024-02-01'
- PackageName (string): Name of the Go SDK package (e.g., "azblob", "azidentity", "azcore")
- PackageVersion (string): Version of the Go SDK package (e.g., "1.0.0", "1.1.2")
- SubscriptionCount (integer): Number of unique subscriptions (≥ 0)

USER QUESTION: {user_question}

Generate a SQL query that answers the user's question using only the columns available in this table. Return only the SQL query without any additional text or formatting.
"""
        
        return prompt

    @mcp.tool()
    async def generateSQLByAMEGoSDKSubCountCustomerDataByMonthTrackInfo(user_question: str):
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
        
        prompt = f"""
You are a SQL query generator for Azure SDK usage analytics. Generate a SQL query for the AMEGoSDKSubCountCustomerDataByMonthTrackInfo table based on the user question.

TABLE: AMEGoSDKSubCountCustomerDataByMonthTrackInfo
DESCRIPTION: Go SDK subscription counts by month and track info

SCHEMA:
- RequestsDate (string): Date when the requests were made in YYYY-MM-01 format. Example: '2024-01-01', '2024-02-01'
- SubscriptionCount (integer): Number of unique subscriptions (≥ 0)
- IsTrack2 (boolean): Boolean indicating if this is Track 2 SDK (true/false)

USER QUESTION: {user_question}

Generate a SQL query that answers the user's question using only the columns available in this table. Return only the SQL query without any additional text or formatting.
"""
        
        return prompt

    @mcp.tool()
    async def generateSQLByAMEGoSDKSubCountCustomerDataByMonthVersion(user_question: str):
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
        
        prompt = f"""
You are a SQL query generator for Azure SDK usage analytics. Generate a SQL query for the AMEGoSDKSubCountCustomerDataByMonthVersion table based on the user question.

TABLE: AMEGoSDKSubCountCustomerDataByMonthVersion
DESCRIPTION: Go SDK subscription counts by month and Go version

SCHEMA:
- RequestsDate (string): Date when the requests were made in YYYY-MM-01 format. Example: '2024-01-01', '2024-02-01'
- SubscriptionCount (integer): Number of unique subscriptions (≥ 0)
- GoVersion (string): Version of Go programming language (e.g., "1.19", "1.20", "1.21")

USER QUESTION: {user_question}

Generate a SQL query that answers the user's question using only the columns available in this table. Return only the SQL query without any additional text or formatting.
"""
        
        return prompt

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


def main():
    """Main entry point for the table-specific SQL MCP server"""
    try:
        print("Starting Table-Specific SQL MCP Server...")
        print("\n=== USAGE STRATEGY ===")
        print("1. Try table-specific SQL tools first (generateSQLBy...)")
        print("2. Use generateKQLFromTemplate as fallback if SQL tables cannot satisfy requirements")
        print("\n=== AVAILABLE TOOLS ===")
        print("SQL Tools (try first):")
        print("  - generateSQLByAMEConciseFiteredNewProductCCIDCustomerSubscriptionId")
        print("  - generateSQLByAMEConciseSubReqCCIDCountByMonthProduct")
        print("  - generateSQLByAMEConciseSubReqCCIDCountByMonthProductHttpMethod")
        print("  - generateSQLByAMEConciseSubReqCCIDCountByMonthProductOS")
        print("  - generateSQLByAMEConciseSubReqCCIDCountByMonthProductProviderTrackInfo")
        print("  - generateSQLByAMEConciseSubReqCCIDCountByMonthProductProviderTrackInfoApiVersion")
        print("  - generateSQLByAMEConciseSubReqCCIDCountByMonthProductProviderTrackInfoPUT")
        print("  - generateSQLByAMEConciseSubReqCCIDCountByMonthProductTrackInfo")
        print("  - generateSQLByAMEConciseSubReqCountByMonthProductMinorLanguageVersion")
        print("  - generateSQLByAMEConciseSubReqCountByMonthProductPatchLanguageVersion")
        print("  - generateSQLByAMEGoSDKReqCountCustomerDataByMonth")
        print("  - generateSQLByAMEGoSDKSubCountCustomerDataByMonthPackageName")
        print("  - generateSQLByAMEGoSDKSubCountCustomerDataByMonthTrackInfo")
        print("  - generateSQLByAMEGoSDKSubCountCustomerDataByMonthVersion")
        print("\nOther Tools:")
        print("  - executeSQLQuery: Execute generated SQL queries")
        print("\nFallback Tool (use only if SQL tools cannot satisfy):")
        print("  - generateKQLFromTemplate: KQL query generation for complex/unsupported queries")
        
        # Initialize and run the server
        mcp = tableSpecificSqlMCP()
        mcp.run(transport="streamable-http")
        
    except Exception as e:
        print(f"Error while running Table-Specific SQL MCP server: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()