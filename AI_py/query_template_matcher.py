# AI_py/query_template_matcher.py
"""Query template matcher for better query parsing and understanding."""

import re
from typing import Optional, Dict, List, Tuple
from error_logger import log_debug, log_info


class QueryTemplateMatcher:
    """
    Matches user queries to predefined templates for better parsing.
    
    This helps the AI model understand queries better by:
    1. Normalizing query variations
    2. Extracting parameters (category, date, etc.)
    3. Identifying operation type (average, percentage, ratio, etc.)
    4. Routing to appropriate handlers
    
    Design Pattern: Template Method Pattern
    """
    
    # Query templates with regex patterns and parameter extraction
    TEMPLATES: Dict[str, List[Tuple[str, Dict[str, int]]]] = {
        'average': [
            (r"average\s+expense", {}),
            (r"mean\s+expense", {}),
            (r"avg\s+expense", {}),
            (r"what'?s?\s+my\s+average", {}),
            (r"what'?s?\s+the\s+average", {}),
            (r"average\s+amount", {}),
            (r"mean\s+amount", {}),
        ],
        'percentage': [
            (r"percentage.*spending.*on\s+(\w+)", {'category': 1}),
            (r"percent.*spending.*on\s+(\w+)", {'category': 1}),
            (r"what\s+percent.*(\w+)", {'category': 1}),
            (r"what\s+percentage.*(\w+)", {'category': 1}),
            (r"how\s+much.*spending.*(\w+)", {'category': 1}),
            (r"%\s+of\s+spending.*(\w+)", {'category': 1}),
        ],
        'ratio': [
            (r"ratio.*largest.*smallest", {}),
            (r"ratio.*largest.*to\s+smallest", {}),
            (r"largest.*to\s+smallest", {}),
            (r"largest.*vs\s+smallest", {}),
            (r"largest.*compared\s+to\s+smallest", {}),
        ],
        'count': [
            (r"how\s+many\s+expenses", {}),
            (r"count\s+of\s+expenses", {}),
            (r"number\s+of\s+expenses", {}),
            (r"how\s+many\s+do\s+i\s+have", {}),
        ],
        'largest': [
            (r"largest\s+expense", {}),
            (r"biggest\s+expense", {}),
            (r"most\s+expensive", {}),
            (r"highest\s+expense", {}),
            (r"max\s+expense", {}),
        ],
        'smallest': [
            (r"smallest\s+expense", {}),
            (r"lowest\s+expense", {}),
            (r"cheapest\s+expense", {}),
            (r"minimum\s+expense", {}),
            (r"min\s+expense", {}),
        ],
        'total': [
            (r"what'?s?\s+my\s+total", {}),
            (r"what'?s?\s+the\s+total", {}),
            (r"total\s+spending", {}),
            (r"total\s+amount", {}),
            (r"sum\s+of\s+expenses", {}),
        ],
        'filtered': [
            (r"spending.*on\s+(\w+)", {'category': 1}),
            (r"spent.*on\s+(\w+)", {'category': 1}),
            (r"spend.*on\s+(\w+)", {'category': 1}),
            (r"how\s+much.*(\w+)", {'category': 1}),
            (r"what.*spent.*(\w+)", {'category': 1}),
        ],
    }
    
    def __init__(self):
        """Initialize the template matcher."""
        self.match_cache = {}  # Cache for performance
    
    def match(self, query: str) -> Optional[Dict]:
        """
        Match query to a template and extract parameters.
        
        Args:
            query: User's natural language query
            
        Returns:
            Dict with 'type', 'params', 'confidence', or None if no match
        """
        # Check cache first
        query_lower = query.lower().strip()
        if query_lower in self.match_cache:
            return self.match_cache[query_lower]
        
        # Try to match against templates
        for template_type, patterns in self.TEMPLATES.items():
            for pattern, param_map in patterns:
                match = re.search(pattern, query_lower, re.IGNORECASE)
                if match:
                    # Extract parameters
                    params = {}
                    for param_name, group_idx in param_map.items():
                        if group_idx <= len(match.groups()):
                            params[param_name] = match.group(group_idx)
                    
                    result = {
                        'type': template_type,
                        'params': params,
                        'confidence': 'high',
                        'matched_pattern': pattern
                    }
                    
                    # Cache result
                    self.match_cache[query_lower] = result
                    
                    log_debug(f"[QueryTemplateMatcher] Matched '{query}' to template '{template_type}' with params: {params}")
                    return result
        
        # No match found
        log_debug(f"[QueryTemplateMatcher] No template match for: '{query}'")
        self.match_cache[query_lower] = None
        return None
    
    def normalize_query(self, query: str) -> str:
        """
        Normalize query to standard form.
        
        Examples:
        - "what's my total" → "what is my total"
        - "how much did i spend" → "what is my total spending"
        - "show me expenses" → "list expenses"
        """
        normalized = query.lower().strip()
        
        # Normalize contractions
        normalized = re.sub(r"what's", "what is", normalized)
        normalized = re.sub(r"that's", "that is", normalized)
        normalized = re.sub(r"it's", "it is", normalized)
        
        # Normalize variations
        normalized = re.sub(r"how much did i spend", "what is my total spending", normalized)
        normalized = re.sub(r"show me", "list", normalized)
        normalized = re.sub(r"tell me", "what is", normalized)
        
        return normalized
    
    def extract_operation(self, query: str) -> Optional[str]:
        """
        Extract the operation type from query.
        
        Returns:
            Operation type: 'average', 'percentage', 'ratio', 'count', etc.
        """
        match = self.match(query)
        if match:
            return match['type']
        return None
    
    def extract_category(self, query: str) -> Optional[str]:
        """
        Extract category/description from query.
        
        Returns:
            Category name if found, None otherwise
        """
        match = self.match(query)
        if match and 'category' in match.get('params', {}):
            return match['params']['category']
        return None
    
    def clear_cache(self):
        """Clear the match cache."""
        self.match_cache.clear()
        log_debug("[QueryTemplateMatcher] Cache cleared")


# Singleton instance for reuse
_template_matcher = None

def get_template_matcher() -> QueryTemplateMatcher:
    """Get singleton template matcher instance."""
    global _template_matcher
    if _template_matcher is None:
        _template_matcher = QueryTemplateMatcher()
    return _template_matcher

