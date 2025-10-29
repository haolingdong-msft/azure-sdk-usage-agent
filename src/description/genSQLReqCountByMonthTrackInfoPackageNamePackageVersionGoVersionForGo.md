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