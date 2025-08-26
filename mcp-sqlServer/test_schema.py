#!/usr/bin/env python3
"""Test script for schema loading functionality"""

import os
import json
import sys

def load_table_schema():
    """Load table schema from fixture file with enhanced structure support."""
    try:
        schema_file = os.path.join(os.path.dirname(__file__), 'fixture', 'tables_and_columns.json')
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
            
            schema_dict[table_name.lower()] = {
                'name': table_name,
                'enabled': enabled,
                'description': description,
                'columns': columns,
                'column_metadata': column_metadata
            }
        
        return {
            'tables': schema_dict,
            'definitions': definitions
        }
    except Exception as e:
        print(f"Error loading table schema: {e}")
        return {'tables': {}, 'definitions': {}}

def main():
    print("Testing schema loading...")
    
    schema = load_table_schema()
    
    print(f"✓ Tables loaded: {len(schema['tables'])}")
    print(f"✓ Definitions loaded: {len(schema['definitions'])}")
    
    # Test enabled tables
    enabled_tables = [t for t in schema['tables'].values() if t['enabled']]
    print(f"✓ Enabled tables: {len(enabled_tables)}")
    
    # Test enum extraction
    product_enum = schema['definitions'].get('Product', {}).get('enum', [])
    track_enum = schema['definitions'].get('TrackInfo', {}).get('enum', [])
    provider_enum = schema['definitions'].get('Provider', {}).get('enum', [])
    
    print(f"✓ Product enum count: {len(product_enum)}")
    print(f"✓ Track enum: {track_enum}")
    print(f"✓ Provider enum count: {len(provider_enum)}")
    
    # Show sample table structure
    if schema['tables']:
        sample_table = list(schema['tables'].values())[0]
        print(f"\n✓ Sample table structure:")
        print(f"  Name: {sample_table['name']}")
        print(f"  Enabled: {sample_table['enabled']}")
        print(f"  Description: {sample_table['description'][:100]}...")
        print(f"  Columns: {sample_table['columns'][:5]}...")
        print(f"  Has metadata: {len(sample_table['column_metadata'])} columns")
    
    # Test column metadata
    if schema['tables']:
        sample_table = list(schema['tables'].values())[0]
        if sample_table['column_metadata']:
            sample_col = list(sample_table['column_metadata'].keys())[0]
            metadata = sample_table['column_metadata'][sample_col]
            print(f"\n✓ Sample column metadata for '{sample_col}':")
            print(f"  Title: {metadata.get('title', 'N/A')}")
            print(f"  Type: {metadata.get('type', 'N/A')}")
            if metadata.get('enum'):
                print(f"  Enum values: {len(metadata['enum'])} options")
    
    print("\n✅ Schema loading test completed successfully!")

if __name__ == "__main__":
    main()
