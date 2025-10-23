Analyze user question to determine the appropriate tool selection.
Use this FIRST to understand which tool (SQL vs KQL) to use for a question.

This tool helps avoid the mistake of using SQL tools for questions that require
total ARM data (which only KQL can provide).

Args:
    user_question: The user's natural language question
    
Returns:
    Analysis with tool recommendation and reasoning