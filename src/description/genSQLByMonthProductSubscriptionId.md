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