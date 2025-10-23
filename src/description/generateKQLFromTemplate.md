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