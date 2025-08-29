"""
Query parser for natural language to SQL conversion
"""
import re
from typing import Any, Dict, List, Optional
from .models import QueryInfo
from .schema_loader import SchemaLoader
from .product_aliases import ProductAliasMapper


class QueryParser:
    """Parses natural language queries into SQL components"""
    
    def __init__(self, schema_loader: SchemaLoader):
        self.schema_loader = schema_loader
        self.product_mapper = ProductAliasMapper()
        self._enum_cache = {}
    
    def _get_enum_values(self, enum_name: str) -> List[str]:
        """Get enum values with caching"""
        if enum_name not in self._enum_cache:
            self._enum_cache[enum_name] = self.schema_loader.get_enum_values(enum_name)
        return self._enum_cache[enum_name]
    
    def find_table_by_name(self, query_text: str) -> Optional[str]:
        """Find the most likely table name from user query with enhanced matching."""
        query_lower = query_text.lower()
        
        # Get enabled tables only
        enabled_tables = self.schema_loader.get_enabled_tables()
        
        # Direct table name matches
        for table_key, table_info in enabled_tables.items():
            if table_key in query_lower or table_info.name.lower() in query_lower:
                return table_info.name
        
        # Enhanced keyword-based matching with scoring
        table_scores = {}
        
        for table_key, table_info in enabled_tables.items():
            score = 0
            table_name = table_info.name.lower()
            description = table_info.description.lower()
            columns = table_info.columns  # Define columns early
            
            # Score based on table name components
            if 'product' in query_lower and 'product' in table_name:
                score += 2
            if 'customer' in query_lower and 'customer' in table_name:
                score += 2
            if 'subscription' in query_lower and 'subscription' in table_name:
                score += 2
            if 'go' in query_lower and 'gosdk' in table_name:
                score += 3
            # Enhanced product matching using alias mapper
            if 'Product' in columns:
                # Get available products for this table (from schema)
                available_products = self._get_enum_values('Product') if hasattr(self, '_get_enum_values') else []
                if available_products:
                    matched_products = self.product_mapper.find_products_by_query(query_lower, available_products)
                    if matched_products:
                        score += 3  # High score for product match
            if 'request' in query_lower and ('req' in table_name or 'request' in description):
                score += 1
            if 'count' in query_lower and 'count' in table_name:
                score += 1
            if 'track' in query_lower and 'track' in table_name:
                score += 1
            if 'api' in query_lower and 'api' in table_name:
                score += 1
            if 'version' in query_lower and 'version' in table_name:
                score += 1
            if 'language' in query_lower and 'language' in table_name:
                score += 1
            if 'os' in query_lower and 'os' in table_name:
                score += 1
            if 'provider' in query_lower and 'provider' in table_name:
                score += 1
            
            # Score based on column availability (columns already defined above)
            if 'provider' in query_lower and 'Provider' in columns:
                score += 1
            if 'resource' in query_lower and 'Resource' in columns:
                score += 1
            if 'http' in query_lower and 'HttpMethod' in columns:
                score += 1
            if 'method' in query_lower and 'HttpMethod' in columns:
                score += 1
            if 'os' in query_lower and 'OS' in columns:
                score += 1
            
            if score > 0:
                table_scores[table_info.name] = score
        
        # Return the highest scoring table
        if table_scores:
            return max(table_scores.items(), key=lambda x: x[1])[0]
        
        # Fallback to first enabled table
        if enabled_tables:
            return list(enabled_tables.values())[0].name
        
        return None

    def extract_columns_from_query(self, query_text: str, table_name: str) -> List[str]:
        """Extract relevant columns based on user query and enhanced table schema."""
        table_info = self.schema_loader.get_table_info(table_name)
        if not table_info:
            return ['*']
        
        available_columns = table_info.columns
        column_metadata = table_info.column_metadata
        query_lower = query_text.lower()
        
        # Check for specific column mentions
        mentioned_columns = []
        for col in available_columns:
            col_lower = col.lower()
            # Check column name and aliases
            if col_lower in query_lower:
                mentioned_columns.append(col)
            # Check column title/description for better matching
            elif col in column_metadata:
                meta = column_metadata[col]
                title_lower = meta.get('title', '').lower()
                desc_lower = meta.get('description', '').lower()
                if title_lower in query_lower or any(word in desc_lower for word in query_lower.split()):
                    mentioned_columns.append(col)
        
        # Enhanced column selection based on query intent
        if not mentioned_columns:
            intent_columns = []
            
            # Product-related queries
            if any(word in query_lower for word in ['product', 'sdk', 'tool']):
                if 'Product' in available_columns:
                    intent_columns.append('Product')
            
            # Track-related queries
            if any(word in query_lower for word in ['track', 'version']):
                if 'TrackInfo' in available_columns:
                    intent_columns.append('TrackInfo')
            
            # Provider/Resource queries
            if any(word in query_lower for word in ['provider', 'service']):
                if 'Provider' in available_columns:
                    intent_columns.append('Provider')
            if any(word in query_lower for word in ['resource', 'type']):
                if 'Resource' in available_columns:
                    intent_columns.append('Resource')
            
            # HTTP method queries
            if any(word in query_lower for word in ['method', 'http', 'get', 'post', 'put', 'delete']):
                if 'HttpMethod' in available_columns:
                    intent_columns.append('HttpMethod')
            
            # OS queries
            if any(word in query_lower for word in ['os', 'operating', 'system', 'windows', 'linux', 'mac']):
                if 'OS' in available_columns:
                    intent_columns.append('OS')
            
            # Always include key columns for context
            key_columns = ['Month', 'RequestCount', 'SubscriptionCount']
            for col in key_columns:
                if col in available_columns and col not in intent_columns:
                    intent_columns.append(col)
            
            if intent_columns:
                return intent_columns
            else:
                # Return most important columns
                priority_columns = ['Month', 'Product', 'RequestCount', 'SubscriptionCount', 'TrackInfo']
                result = []
                for col in priority_columns:
                    if col in available_columns:
                        result.append(col)
                return result[:5]  # Limit to 5 columns
        
        return mentioned_columns

    def build_where_clause(self, query_text: str, table_name: str) -> str:
        """Build WHERE clause based on user query intent with enhanced enum support."""
        table_info = self.schema_loader.get_table_info(table_name)
        if not table_info:
            return "1=1"  # Return all records if no specific filtering
        
        available_columns = table_info.columns
        query_lower = query_text.lower()
        conditions = []
        
        # Month filtering (improved pattern matching)
        month_patterns = re.findall(r'(\d{4}-\d{2}-\d{2}|\d{4}-\d{2}|\d{4}/\d{2})', query_lower)
        if month_patterns and 'Month' in available_columns:
            for month in month_patterns:
                if len(month) == 7:  # YYYY-MM format
                    conditions.append(f"Month LIKE '{month}%'")
                else:
                    conditions.append(f"Month = '{month}'")
        
        # This month filtering
        if 'this month' in query_lower and 'Month' in available_columns:
            conditions.append("Month LIKE '2025-08%'")
        
        # Product filtering with alias support
        if 'Product' in available_columns:
            product_enum = self._get_enum_values('Product')
            matched_products = self.product_mapper.find_products_by_query(query_lower, product_enum)
            
            if matched_products:
                if len(matched_products) == 1:
                    conditions.append(f"Product = '{matched_products[0]}'")
                else:
                    # Multiple products matched, use OR condition
                    product_conditions = [f"Product = '{p}'" for p in matched_products]
                    conditions.append(f"({' OR '.join(product_conditions)})")
        
        # Track filtering with enum support
        if 'TrackInfo' in available_columns:
            track_enum = self._get_enum_values('TrackInfo')
            for track in track_enum:
                if track.lower() in query_lower:
                    conditions.append(f"TrackInfo = '{track}'")
                    break
            # Also check for track1/track2 patterns
            if 'track 1' in query_lower or 'track1' in query_lower:
                conditions.append("TrackInfo = 'Track1'")
            elif 'track 2' in query_lower or 'track2' in query_lower:
                conditions.append("TrackInfo = 'Track2'")
        
        # Provider filtering - now uses text matching instead of enum
        if 'Provider' in available_columns:
            # Look for common provider patterns in the query
            provider_patterns = [
                r'microsoft\.(\w+)',  # Microsoft.Compute, Microsoft.Storage, etc.
                r'microsoft\s+(\w+)',  # Microsoft Compute, Microsoft Storage, etc.
                r'compute|storage|network|web|sql|keyvault|resources|container|documentdb|authorization'
            ]
            
            for pattern in provider_patterns:
                matches = re.findall(pattern, query_lower)
                if matches:
                    if pattern.startswith('microsoft'):
                        # Construct Microsoft.ServiceName format
                        service_name = matches[0].capitalize()
                        conditions.append(f"Provider LIKE '%Microsoft.{service_name}%'")
                    else:
                        # General service name matching
                        conditions.append(f"Provider LIKE '%{matches[0]}%'")
                    break
        
        # Resource filtering - now uses text matching instead of enum
        if 'Resource' in available_columns:
            # Look for common resource type patterns
            resource_keywords = [
                'virtualmachines', 'vm', 'virtual machines',
                'storageaccounts', 'storage accounts', 'storage',
                'virtualnetworks', 'vnet', 'virtual networks', 'network',
                'webapps', 'web apps', 'webapp',
                'sqlservers', 'sql servers', 'sql',
                'keyvaults', 'key vaults', 'keyvault',
                'resourcegroups', 'resource groups',
                'kubernetesclusters', 'kubernetes', 'aks',
                'cosmosdbaccounts', 'cosmos', 'cosmosdb',
                'roleassignments', 'role assignments'
            ]
            
            for keyword in resource_keywords:
                if keyword in query_lower:
                    # Convert keyword to likely resource name format
                    if keyword in ['vm', 'virtual machines']:
                        conditions.append("Resource LIKE '%virtualMachines%'")
                    elif keyword in ['storage accounts', 'storage']:
                        conditions.append("Resource LIKE '%storageAccounts%'")
                    elif keyword in ['vnet', 'virtual networks', 'network']:
                        conditions.append("Resource LIKE '%virtualNetworks%'")
                    elif keyword in ['web apps', 'webapp']:
                        conditions.append("Resource LIKE '%webApps%'")
                    elif keyword in ['sql servers', 'sql']:
                        conditions.append("Resource LIKE '%sqlServers%'")
                    elif keyword in ['key vaults', 'keyvault']:
                        conditions.append("Resource LIKE '%keyVaults%'")
                    elif keyword in ['resource groups']:
                        conditions.append("Resource LIKE '%resourceGroups%'")
                    elif keyword in ['kubernetes', 'aks']:
                        conditions.append("Resource LIKE '%kubernetesClusters%'")
                    elif keyword in ['cosmos', 'cosmosdb']:
                        conditions.append("Resource LIKE '%cosmosDbAccounts%'")
                    elif keyword in ['role assignments']:
                        conditions.append("Resource LIKE '%roleAssignments%'")
                    else:
                        # Direct match for exact resource names
                        conditions.append(f"Resource LIKE '%{keyword}%'")
                    break
        
        # HTTP Method filtering with enum support
        if 'HttpMethod' in available_columns:
            http_method_enum = self._get_enum_values('HttpMethod')
            for method in http_method_enum:
                if method.lower() in query_lower:
                    conditions.append(f"HttpMethod = '{method}'")
                    break
        
        # OS filtering with enum support
        if 'OS' in available_columns:
            os_enum = self._get_enum_values('OS')
            for os_name in os_enum:
                if os_name.lower() in query_lower:
                    conditions.append(f"OS = '{os_name}'")
                    break
        
        # Request/Subscription count filtering
        count_columns = ['RequestCount', 'SubscriptionCount', 'RequestCounts', 'CCIDCount']
        for count_col in count_columns:
            if count_col in available_columns:
                # Extract numeric comparisons
                patterns = [
                    (r'(?:more than|greater than|above)\s+(\d+)', lambda x: f"{count_col} > {x}"),
                    (r'(?:less than|below|under)\s+(\d+)', lambda x: f"{count_col} < {x}"),
                    (r'(?:at least|minimum of)\s+(\d+)', lambda x: f"{count_col} >= {x}"),
                    (r'(?:at most|maximum of)\s+(\d+)', lambda x: f"{count_col} <= {x}"),
                    (r'(?:exactly|equal to)\s+(\d+)', lambda x: f"{count_col} = {x}"),
                ]
                
                for pattern, formatter in patterns:
                    match = re.search(pattern, query_lower)
                    if match:
                        conditions.append(formatter(match.group(1)))
                        break
        
        return ' AND '.join(conditions) if conditions else "1=1"

    def parse_user_query(self, user_question: str) -> Dict[str, Any]:
        """Parse user question into SQL query components."""
        table_name = self.find_table_by_name(user_question)
        
        if not table_name:
            return {
                'error': 'Could not identify a relevant table from your question. Available topics: customer data, product usage, subscription information.'
            }
        
        columns = self.extract_columns_from_query(user_question, table_name)
        where_clause = self.build_where_clause(user_question, table_name)
        
        # Handle TOP N queries
        limit_clause = ""
        top_match = re.search(r'top\s+(\d+)', user_question.lower())
        if top_match:
            limit_clause = f"TOP {top_match.group(1)}"
        
        # Handle ORDER BY (enhanced)
        order_clause = ""
        order_column = None
        order_direction = "DESC"
        
        table_info = self.schema_loader.get_table_info(table_name)
        if table_info:
            # Determine sort column
            if any(word in user_question.lower() for word in ['count', 'request', 'usage']):
                if 'RequestCount' in table_info.columns:
                    order_column = 'RequestCount'
                elif 'SubscriptionCount' in table_info.columns:
                    order_column = 'SubscriptionCount'
            elif 'date' in user_question.lower() or 'time' in user_question.lower():
                if 'Month' in table_info.columns:
                    order_column = 'Month'
                elif 'RequestsDate' in table_info.columns:
                    order_column = 'RequestsDate'
        
        # Determine sort direction
        if any(word in user_question.lower() for word in ['lowest', 'least', 'minimum', 'asc', 'ascending', 'oldest']):
            order_direction = "ASC"
        elif any(word in user_question.lower() for word in ['highest', 'most', 'maximum', 'desc', 'descending', 'latest', 'newest']):
            order_direction = "DESC"
        
        if order_column:
            order_clause = f"ORDER BY {order_column} {order_direction}"
        
        return {
            'table_name': table_name,
            'columns': columns,
            'where_clause': where_clause,
            'limit_clause': limit_clause,
            'order_clause': order_clause
        }
