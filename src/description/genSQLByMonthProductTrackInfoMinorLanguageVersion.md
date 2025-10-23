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