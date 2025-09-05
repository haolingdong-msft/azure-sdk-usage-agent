"""
Product alias mapping for natural language queries
"""
from typing import Dict, List, Set


class ProductAliasMapper:
    """Maps common product aliases to official product names"""
    
    def __init__(self):
        # Define alias mappings
        self.alias_mappings = {
            # JavaScript aliases
            'js': ['JavaScript', 'JavaScript (Node.JS)', 'JavaScript RLC'],
            'javascript': ['JavaScript', 'JavaScript (Node.JS)', 'JavaScript RLC'],
            'node': ['JavaScript (Node.JS)'],
            'nodejs': ['JavaScript (Node.JS)'],
            'node.js': ['JavaScript (Node.JS)'],
            'rlc': ['JavaScript RLC'],
            
            # .NET aliases
            '.net': ['.Net Code-gen', '.Net Fluent'],
            'dotnet': ['.Net Code-gen', '.Net Fluent'],
            'csharp': ['.Net Code-gen', '.Net Fluent'],
            'c#': ['.Net Code-gen', '.Net Fluent'],
            'net': ['.Net Code-gen', '.Net Fluent'],
            
            # Java aliases
            'java': ['Java Fluent Lite', 'Java Fluent Premium'],
            
            # Python aliases
            'python': ['Python-SDK'],
            'py': ['Python-SDK'],
            
            # Go aliases
            'go': ['Go-SDK'],
            'golang': ['Go-SDK'],
            
            # PHP aliases
            'php': ['PHP-SDK'],
            
            # Ruby aliases
            'ruby': ['Ruby-SDK'],
            'rb': ['Ruby-SDK'],
            
            # Rust aliases
            'rust': ['Rust'],
            'rs': ['Rust'],
            
            # CLI/PowerShell aliases
            'cli': ['AzureCLI'],
            'azure-cli': ['AzureCLI'],
            'az': ['AzureCLI'],
            'powershell': ['AzurePowershell'],
            'ps': ['AzurePowershell'],
            'pwsh': ['AzurePowershell'],
            
            # Infrastructure as Code aliases
            'terraform': ['Terraform'],
            'tf': ['Terraform'],
            'ansible': ['Ansible'],
            
            # IDE/Editor aliases
            'vscode': ['VS Code Azure Extension'],
            'vs-code': ['VS Code Azure Extension'],
            'visual-studio-code': ['VS Code Azure Extension'],
        }
        
        # Create reverse mapping for fast lookup
        self.product_to_aliases = {}
        for alias, products in self.alias_mappings.items():
            for product in products:
                if product not in self.product_to_aliases:
                    self.product_to_aliases[product] = set()
                self.product_to_aliases[product].add(alias)
    
    def find_products_by_query(self, query_text: str, available_products: List[str]) -> List[str]:
        """
        Find products that match the query text using aliases or direct names
        
        Args:
            query_text: User query text
            available_products: List of available product names from schema
            
        Returns:
            List of matching product names
        """
        query_lower = query_text.lower()
        matched_products = set()
        
        # First check for direct product name matches
        for product in available_products:
            if product.lower() in query_lower:
                matched_products.add(product)
        
        # If no direct matches, check aliases
        if not matched_products:
            for alias, products in self.alias_mappings.items():
                if alias in query_lower:
                    # Only add products that are actually available in the schema
                    for product in products:
                        if product in available_products:
                            matched_products.add(product)
        
        return list(matched_products)
    
    def get_aliases_for_product(self, product_name: str) -> Set[str]:
        """Get all aliases for a given product name"""
        return self.product_to_aliases.get(product_name, set())
    
    def get_all_aliases(self) -> Dict[str, List[str]]:
        """Get all alias mappings"""
        return self.alias_mappings.copy()
    
    def add_alias(self, alias: str, product_names: List[str]):
        """Add a new alias mapping"""
        alias_lower = alias.lower()
        if alias_lower not in self.alias_mappings:
            self.alias_mappings[alias_lower] = []
        
        for product in product_names:
            if product not in self.alias_mappings[alias_lower]:
                self.alias_mappings[alias_lower].append(product)
            
            # Update reverse mapping
            if product not in self.product_to_aliases:
                self.product_to_aliases[product] = set()
            self.product_to_aliases[product].add(alias_lower)
