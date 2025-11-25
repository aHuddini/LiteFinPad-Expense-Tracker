"""
Context Builder

Builds context strings for LLM prompts from expense data.
"""

import json
from typing import Dict, List, Tuple


class ContextBuilder:
    """Builds context strings for LLM prompts."""
    
    @staticmethod
    def build_single_month_context(expenses: List[Dict], total: float, month_key: str) -> str:
        """
        Build context for single month query.
        
        Args:
            expenses: List of expense dictionaries
            total: Total amount
            month_key: Month key (YYYY-MM)
            
        Returns:
            JSON string with expense data
        """
        # Limit to recent 50 expenses to avoid token limits
        recent_expenses = expenses[-50:] if len(expenses) > 50 else expenses
        
        context = {
            'month': month_key,
            'total': total,
            'count': len(expenses),
            'expenses': recent_expenses
        }
        
        return json.dumps(context, indent=2)
    
    @staticmethod
    def build_multi_month_context(
        all_months: Dict[str, Tuple[List[Dict], float]], 
        current_month_key: str
    ) -> str:
        """
        Build context for multi-month query.
        
        Args:
            all_months: Dict of {month_key: (expenses, total)}
            current_month_key: Current month key (YYYY-MM)
            
        Returns:
            JSON string with multi-month expense data
        """
        # Sort months chronologically
        sorted_months = sorted(all_months.keys(), reverse=True)
        
        # Prepare summary for each month (limit expenses per month)
        months_data = []
        for month_key in sorted_months[:12]:  # Last 12 months max
            expenses, total = all_months[month_key]
            
            # For each month, include summary + sample expenses
            month_info = {
                'month': month_key,
                'total': total,
                'count': len(expenses),
                'sample_expenses': expenses[-10:] if len(expenses) > 10 else expenses  # Last 10 expenses per month
            }
            months_data.append(month_info)
        
        context = {
            'current_month': current_month_key,
            'months': months_data,
            'total_months': len(months_data)
        }
        
        return json.dumps(context, indent=2)

