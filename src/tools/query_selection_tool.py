"""
Query Tool Selection Service for Azure SDK Usage Analysis

Analyzes user questions to recommend appropriate query tools (SQL vs KQL).
"""

class QueryToolSelector:
    """Analyzes user intent and provides query tool selection guidance"""
    
    def __init__(self):
        # Critical keywords that REQUIRE KQL (total ARM data)
        self.total_arm_indicators = [
            'total arm', 'all arm', 'vs total', 'percentage of total', '% of total',
            'sdk vs arm', 'sdk percentage', 'importance of sdk', 'vs all requests',
            'non-sdk', 'portal', 'cli', 'powershell', 'rest api', 'arm templates',
            'all requests', 'total requests', 'complete traffic', 'overall arm'
        ]
        
        # Keywords that suggest SQL is sufficient (SDK-only analysis)
        self.sdk_only_indicators = [
            'sdk adoption', 'sdk comparison', 'track1 vs track2', 'sdk trends',
            'between sdks', 'among sdks', 'sdk migration', 'language version',
            'package version', 'api version', 'sdk performance', 'sdk usage'
        ]
    
    def analyze_user_intent(self, user_question: str) -> str:
        """
        Analyze user question to provide tool selection guidance.
        
        Args:
            user_question: The user's question or request
            
        Returns:
            Analysis result with tool recommendation and reasoning
        """
        question_lower = user_question.lower()
        
        found_total_arm = [kw for kw in self.total_arm_indicators if kw in question_lower]
        found_sdk_only = [kw for kw in self.sdk_only_indicators if kw in question_lower]
        
        if found_total_arm:
            return f"🚨 KQL REQUIRED: Question contains total ARM indicators: {found_total_arm}. SQL cannot answer this - it only has SDK data, not complete ARM traffic."
        elif found_sdk_only:
            return f"✅ SQL APPROPRIATE: Question focuses on SDK-only analysis: {found_sdk_only}. Use genSQLBy... tools for faster, structured queries."
        else:
            return f"⚠️ UNCLEAR: Could not determine if question needs total ARM data or SDK-only data. Consider: Does the question need non-SDK traffic (portal, CLI, etc.)? If yes → KQL. If no → SQL."
