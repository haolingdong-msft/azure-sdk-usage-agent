"""
Schema utilities for SQL schema operations
Provides utilities for loading and processing SQL schema definitions
"""
import json
from src.utils.file_utils import read_file_content


async def getSQLSchemaDefinitions(field_names: list = None):
    """
    Extract complete field definitions from SQL_Schema.json with all attributes.
    Returns the exact definition structure including title, description, type, enum, pattern, etc.
    
    Args:
        field_names: List of field names to retrieve from definitions (optional).
                    If None, returns all definitions.
                    Example: ["TrackInfo", "Product", "HttpMethod", "OS"]
        
    Returns:
        Complete field definitions in their original format, e.g.:
        {
            "Product": {
                "title": "Product",
                "description": "Azure SDK product name", 
                "type": "string",
                "enum": [".Net Code-gen", ".Net Fluent", ...]
            }
        }
    """
    try:
        print(f"Loading SQL schema definitions for fields: {field_names}")
        
        schema_content = read_file_content('../schemas/SQL_Schema.json', relative_to_file=__file__)
        sql_schema = json.loads(schema_content)
        
        definitions = sql_schema.get("definitions", {})
        
        if field_names is None:
            return definitions
        
        filtered_definitions = {}
        
        for field_name in field_names:
            if field_name in definitions:
                # Return the complete definition with all attributes
                filtered_definitions[field_name] = definitions[field_name]
        
        return filtered_definitions
        
    except Exception as e:
        print(f"Error in getSQLSchemaDefinitions tool: {str(e)}")
        return {
            "_error": f"Error loading schema definitions: {str(e)}",
            "_available_fields": []
        }