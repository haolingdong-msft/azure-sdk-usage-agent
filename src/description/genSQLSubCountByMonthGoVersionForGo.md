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