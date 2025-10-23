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