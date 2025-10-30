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