"""
Schema loader for table and column information
"""
import os
import json
from typing import Any, Dict, List
from .models import TableInfo


class SchemaLoader:
    """Loads and manages database schema information"""
    
    def __init__(self, schema_file_path: str):
        self.schema_file_path = schema_file_path
        self._schema_cache = None
        
    def load_table_schema(self) -> Dict[str, Any]:
        """Load table schema from fixture file with enhanced structure support."""
        if self._schema_cache is not None:
            return self._schema_cache
            
        try:
            schema_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), self.schema_file_path)
            with open(schema_file, 'r') as f:
                schema_data = json.load(f)
            
            # Convert to dict for easier lookup with enhanced metadata
            schema_dict = {}
            definitions = schema_data.get('definitions', {})
            
            for table in schema_data.get('Tables', []):
                table_name = table['TableName']
                enabled = table.get('enabled', 'true') == 'true'
                description = table.get('Description', '')
                
                columns = []
                column_metadata = {}
                
                for col in table.get('Columns', []):
                    col_name = col['ColumnName']
                    columns.append(col_name)
                    
                    # Extract column metadata from definitions
                    ref = col.get('$ref', '').replace('#/definitions/', '')
                    if ref in definitions:
                        def_info = definitions[ref]
                        column_metadata[col_name] = {
                            'title': def_info.get('title', col_name),
                            'description': def_info.get('description', ''),
                            'type': def_info.get('type', 'string'),
                            'enum': def_info.get('enum'),
                            'pattern': def_info.get('pattern'),
                            'format': def_info.get('format'),
                            'minimum': def_info.get('minimum')
                        }
                
                schema_dict[table_name.lower()] = TableInfo(
                    name=table_name,
                    enabled=enabled,
                    description=description,
                    columns=columns,
                    column_metadata=column_metadata
                )
            
            self._schema_cache = {
                'tables': schema_dict,
                'definitions': definitions
            }
            return self._schema_cache
            
        except Exception as e:
            print(f"Error loading table schema: {e}")
            return {'tables': {}, 'definitions': {}}
    
    def get_enum_values(self, enum_name: str) -> List[str]:
        """Get enum values for a specific definition"""
        schema = self.load_table_schema()
        definitions = schema.get('definitions', {})
        return definitions.get(enum_name, {}).get('enum', [])
    
    def get_enabled_tables(self) -> Dict[str, TableInfo]:
        """Get only enabled tables"""
        schema = self.load_table_schema()
        tables = schema.get('tables', {})
        return {k: v for k, v in tables.items() if v.enabled}
    
    def get_table_info(self, table_name: str) -> TableInfo:
        """Get information for a specific table"""
        schema = self.load_table_schema()
        tables = schema.get('tables', {})
        return tables.get(table_name.lower())
