# AI_py/handlers/simple_query_handler.py
"""Handler for simple queries that can be computed using Python without AI."""

import sys
import os
from typing import List, Dict
from collections import defaultdict
from datetime import datetime

# Import from parent directory (app root)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from error_logger import log_info, log_warning, log_debug


class SimpleQueryHandler:
    """
    Handles simple queries using pure Python computation (no AI).
    
    Supports:
    - Largest/biggest/highest/most expensive expense
    - Lowest/smallest/minimum/cheapest expense
    - Total/sum of expenses
    - Category analysis (spending by category)
    - Expense listing
    
    Design Pattern: Strategy Pattern
    - Implements query strategy without AI overhead
    - Fast (<50ms) Python-based computation
    - Handles 80% of common user queries
    """
    
    # Keywords that trigger simple query handling
    # Expanded per Grok recommendations to cover more cases and bypass AI
    SIMPLE_QUERY_KEYWORDS = [
        'largest', 'biggest', 'highest', 'most expensive', 'max',
        'lowest', 'smallest', 'minimum', 'cheapest', 'min', 'least',
        'total', 'sum', 'how much', 'spent', 'spend',
        'categor', 'spend most', 'spending most', 'top categor', 'top spending',  # Category queries
        'average', 'mean', 'avg', 'average expense', 'average amount',  # Average queries
        # Removed 'percentage', 'percent', '%', 'ratio' - let AI handle these for better NLP
        'count', 'how many', 'number of', 'how many expenses',  # Count queries
        'what did i spend', 'spending on', 'spent on',  # Category spending queries
        # Removed 'most of my budget', 'takes up', 'category takes' - let AI handle for better understanding
    ]
    
    # Keywords that indicate complex/analytical queries (should go to AI)
    COMPLEX_QUERY_KEYWORDS = [
        'analyze', 'analysis', 'insights', 'patterns', 'trends', 'trend',
        'habits', 'cut back', 'should', 'recommend', 'suggest', 'advice',
        'eating up', 'where did', 'most of my money', 'budget', 'eating'
    ]
    
    # Keywords that indicate multi-month queries (should NOT be handled by simple handler)
    MULTI_MONTH_KEYWORDS = [
        'compare', 'comparison', 'vs', 'versus', 'last month', 'previous month',
        'this month', 'trend', 'over time', 'history', 'months', 'year', 'annual'
    ]
    
    # Keywords that indicate all-time queries (across all months)
    ALL_TIME_KEYWORDS = [
        'all-time', 'all time', 'all-time', 'ever', 'all months', 'all years',
        'across all', 'throughout', 'entire history', 'all data'
    ]
    
    def can_handle(self, user_input: str) -> bool:
        """
        Check if this handler can handle the query.
        
        Excludes multi-month queries and complex analytical queries even if they contain simple keywords.
        
        Args:
            user_input: User's natural language query
            
        Returns:
            bool: True if query matches simple query keywords and is NOT multi-month or complex
        """
        user_lower = user_input.lower()
        
        # Exclude multi-month queries - they need AI processing
        if any(keyword in user_lower for keyword in self.MULTI_MONTH_KEYWORDS):
            log_debug(f"[SimpleQueryHandler] Excluding multi-month query: '{user_input}'")
            return False
        
        # Exclude complex/analytical queries - they need AI processing
        if any(keyword in user_lower for keyword in self.COMPLEX_QUERY_KEYWORDS):
            log_debug(f"[SimpleQueryHandler] Excluding complex query: '{user_input}'")
            return False
        
        # Check if matches simple query keywords
        return any(keyword in user_lower for keyword in self.SIMPLE_QUERY_KEYWORDS)
    
    def handle(self, user_input: str, expenses: List[Dict], total: float) -> str:
        """
        Handle a simple query using Python computation.
        
        Args:
            user_input: User's natural language query
            expenses: List of expense dictionaries
            total: Total amount of all expenses
            
        Returns:
            str: Direct answer to the query
        """
        user_lower = user_input.lower()
        
        log_info(f"[SimpleQueryHandler] Handling query: '{user_input}'")
        log_debug(f"[SimpleQueryHandler] {len(expenses)} expenses, total: ${total:.2f}")
        
        # Route to appropriate computation method
        # IMPORTANT: Check more specific queries FIRST before general ones
        # This prevents misrouting (e.g., ratio query being caught as largest query)
        
        # Removed percentage and ratio queries - route to AI for consistent behavior
        # Percentage and ratio queries should be handled by AI with Python fallback
        
        if self._is_average_query(user_lower):
            return self._compute_average(expenses)
        
        elif self._is_category_query(user_lower):
            return self._compute_categories(expenses)
        
        elif self._is_filtered_query(user_lower):
            return self._compute_filtered(user_input, user_lower, expenses)
        
        elif self._is_largest_query(user_lower):
            return self._compute_largest(expenses)
        
        elif self._is_lowest_query(user_lower):
            return self._compute_lowest(expenses)
        
        elif self._is_total_query(user_lower):
            return self._compute_total(total)
        
        elif self._is_count_query(user_lower):
            return self._compute_count(expenses)
        
        elif self._is_expense_list_query(user_lower):
            return self._list_expenses(expenses)
        
        # Generic fallback
        log_warning(f"[SimpleQueryHandler] No specific handler matched, using generic response")
        return self._generic_response(expenses, total)
    
    # ==========================================
    # Query Type Detection
    # ==========================================
    
    def _is_largest_query(self, user_lower: str) -> bool:
        """Check if query is asking for largest expense."""
        # Exclude ratio/proportion queries (which also contain "largest")
        is_ratio = 'ratio' in user_lower or 'proportion' in user_lower or ('largest' in user_lower and 'smallest' in user_lower and ('to' in user_lower or 'vs' in user_lower))
        if is_ratio:
            return False
        return any(kw in user_lower for kw in ['largest', 'biggest', 'highest', 'most expensive'])
    
    def _is_lowest_query(self, user_lower: str) -> bool:
        """Check if query is asking for lowest expense."""
        return any(kw in user_lower for kw in ['lowest', 'smallest', 'minimum', 'cheapest', 'least'])
    
    def _is_total_query(self, user_lower: str) -> bool:
        """Check if query is asking for total."""
        return 'total' in user_lower or 'sum' in user_lower
    
    def _is_category_query(self, user_lower: str) -> bool:
        """Check if query is asking for category analysis."""
        return 'categor' in user_lower or ('spend' in user_lower and 'most' in user_lower)
    
    def _is_filtered_query(self, user_lower: str) -> bool:
        """Check if query is asking for spending on a specific item/category."""
        # Queries like "how much did I spend on groceries", "spending on rent", "what did I spend on rent"
        # BUT NOT percentage queries (which also have "spending" and "on")
        # Check for spending-related words + "on"/"for"
        spending_words = ['how much', 'spending', 'spent', 'spend', 'what', 'how']
        has_spending_word = any(word in user_lower for word in spending_words)
        has_preposition = ' on ' in user_lower or ' for ' in user_lower
        
        # Exclude percentage and ratio queries (they should go to AI)
        is_percentage = any(kw in user_lower for kw in ['percentage', 'percent', '%'])
        is_ratio = 'ratio' in user_lower or 'proportion' in user_lower
        
        return has_spending_word and has_preposition and not is_percentage and not is_ratio
    
    def _is_expense_list_query(self, user_lower: str) -> bool:
        """Check if query is asking for expense list."""
        # Only match if NOT a category query, filtered query, or analytical query
        is_category = self._is_category_query(user_lower)
        is_filtered = self._is_filtered_query(user_lower)
        is_average = self._is_average_query(user_lower)
        is_percentage = self._is_percentage_query(user_lower)
        is_ratio = self._is_ratio_query(user_lower)
        
        # Exclude analytical queries - check these FIRST
        if is_average or is_percentage or is_ratio:
            return False
        
        # Also exclude if query contains "percentage" or "ratio" keywords (should go to AI)
        # Average can be handled here, but percentage/ratio should go to AI
        if any(kw in user_lower for kw in ['percentage', 'percent', '%', 'ratio', 'proportion']):
            return False
        
        return not is_category and not is_filtered and (
            ('expenses' in user_lower and 'what' not in user_lower) or
            ('what' in user_lower and 'categor' not in user_lower and 'spend' not in user_lower and 
             'average' not in user_lower and 'percentage' not in user_lower and 'ratio' not in user_lower)
        )
    
    def _is_average_query(self, user_lower: str) -> bool:
        """Check if query is asking for average expense amount."""
        # Match "average expense" or "monthly average" or "average amount" or "typically spend"
        has_avg = any(kw in user_lower for kw in ['average', 'mean', 'avg', 'typically', 'typical', 'usually'])
        has_expense_context = 'expense' in user_lower or 'amount' in user_lower or 'monthly' in user_lower or 'per expense' in user_lower
        return has_avg and has_expense_context
    
    def _is_percentage_query(self, user_lower: str) -> bool:
        """Check if query is asking for percentage calculation."""
        # Removed - percentage queries should go to AI
        # This method kept for reference but should not be called
        return False
    
    def _is_ratio_query(self, user_lower: str) -> bool:
        """Check if query is asking for ratio calculation."""
        # Removed - ratio queries should go to AI
        # This method kept for reference but should not be called
        return False
    
    def _is_count_query(self, user_lower: str) -> bool:
        """Check if query is asking for count of expenses."""
        return any(kw in user_lower for kw in ['count', 'how many', 'number of']) and 'expense' in user_lower
    
    # ==========================================
    # Computation Methods
    # ==========================================
    
    def _compute_largest(self, expenses: List[Dict]) -> str:
        """Compute largest expense."""
        if not expenses:
            return "No expenses found."
        
        largest = max(expenses, key=lambda x: x.get('amount', 0))
        amount = largest.get('amount', 0)
        desc = largest.get('description', 'Unknown')
        date = largest.get('date', 'Unknown date')
        
        # Format date nicely if it's in YYYY-MM-DD format
        date_formatted = self._format_date(date)
        
        # Format with better structure
        result = f"**Largest Expense:**\n${amount:,.2f} for {desc}\nDate: {date_formatted}"
        log_info(f"[SimpleQueryHandler] Largest expense: ${amount:.2f}")
        return result
    
    def _compute_lowest(self, expenses: List[Dict]) -> str:
        """Compute lowest expense."""
        if not expenses:
            return "No expenses found."
        
        lowest = min(expenses, key=lambda x: x.get('amount', float('inf')))
        amount = lowest.get('amount', 0)
        desc = lowest.get('description', 'Unknown')
        date = lowest.get('date', 'Unknown date')
        
        # Format date nicely if it's in YYYY-MM-DD format
        date_formatted = self._format_date(date)
        
        # Format with better structure
        result = f"**Lowest Expense:**\n${amount:,.2f} for {desc}\nDate: {date_formatted}"
        log_info(f"[SimpleQueryHandler] Lowest expense: ${amount:.2f}")
        return result
    
    def _compute_total(self, total: float) -> str:
        """Return total amount."""
        result = f"Your total is ${total:.2f}"
        log_info(f"[SimpleQueryHandler] Total: ${total:.2f}")
        return result
    
    def _compute_filtered(self, user_input: str, user_lower: str, expenses: List[Dict]) -> str:
        """Compute spending on a specific item/category."""
        if not expenses:
            return "No expenses found."
        
        # Extract the filter term (what comes after "on" or "for")
        filter_term = None
        if ' on ' in user_lower:
            parts = user_lower.split(' on ', 1)
            if len(parts) > 1:
                filter_term = parts[1].strip()
        elif ' for ' in user_lower:
            parts = user_lower.split(' for ', 1)
            if len(parts) > 1:
                filter_term = parts[1].strip()
        
        if not filter_term:
            log_warning(f"[SimpleQueryHandler] Could not extract filter term from: '{user_input}'")
            return self._generic_response(expenses, 0)
        
        # Remove trailing punctuation (?, !, ., etc.)
        import string
        filter_term = filter_term.rstrip(string.punctuation)
        
        log_debug(f"[SimpleQueryHandler] Filtering expenses for: '{filter_term}'")
        
        # Filter expenses by description (case-insensitive partial match)
        filtered_expenses = []
        for exp in expenses:
            desc = exp.get('description', '').lower()
            if filter_term in desc:
                filtered_expenses.append(exp)
        
        if not filtered_expenses:
            result = f"You haven't spent anything on {filter_term}."
            log_info(f"[SimpleQueryHandler] No expenses found for '{filter_term}'")
            return result
        
        # Calculate total for filtered expenses
        filtered_total = sum(exp.get('amount', 0) for exp in filtered_expenses)
        
        result = f"You spent ${filtered_total:.2f} on {filter_term} ({len(filtered_expenses)} expense{'s' if len(filtered_expenses) != 1 else ''})"
        log_info(f"[SimpleQueryHandler] Filtered total for '{filter_term}': ${filtered_total:.2f} ({len(filtered_expenses)} expenses)")
        return result
    
    def _compute_categories(self, expenses: List[Dict]) -> str:
        """Group expenses by description and return top categories."""
        if not expenses:
            return "No expenses found."
        
        log_debug(f"[SimpleQueryHandler] Computing category analysis for {len(expenses)} expenses")
        
        # Group expenses by description (treating description as category)
        category_totals = defaultdict(float)
        for exp in expenses:
            desc = exp.get('description', 'Unknown').strip()
            if desc:
                category_totals[desc] += exp.get('amount', 0)
        
        # Sort by total amount (descending)
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        
        if not sorted_categories:
            return "No categories found."
        
        # Return top 3-5 categories with better formatting
        top_categories = sorted_categories[:5]
        category_lines = []
        for i, (desc, amount) in enumerate(top_categories, 1):
            category_lines.append(f"{i}. {desc}: ${amount:,.2f}")
        
        result = "**Top Spending Categories:**\n" + "\n".join(category_lines)
        log_info(f"[SimpleQueryHandler] Top category: {sorted_categories[0][0]} (${sorted_categories[0][1]:.2f})")
        return result
    
    def _list_expenses(self, expenses: List[Dict]) -> str:
        """List first few expenses with dates."""
        if not expenses:
            return "No expenses found."
        
        expense_list = []
        for exp in expenses[:10]:  # Limit to first 10
            amount = exp.get('amount', 0)
            desc = exp.get('description', 'Unknown')
            date = exp.get('date', '')
            
            if date:
                date_formatted = self._format_date(date, short=True)
                expense_list.append(f"${amount:.2f} for {desc} on {date_formatted}")
            else:
                expense_list.append(f"${amount:.2f} for {desc}")
        
        if len(expenses) > 10:
            result = f"You have {len(expenses)} expenses. Recent: {', '.join(expense_list)}"
        else:
            result = f"You have {len(expenses)} expenses: {', '.join(expense_list)}"
        
        log_info(f"[SimpleQueryHandler] Listed {min(10, len(expenses))} of {len(expenses)} expenses")
        return result
    
    def _compute_average(self, expenses: List[Dict]) -> str:
        """Compute average expense amount."""
        if not expenses:
            return "No expenses found."
        
        total = sum(exp.get('amount', 0) for exp in expenses)
        count = len(expenses)
        average = total / count if count > 0 else 0
        
        result = f"Your average expense amount is ${average:.2f} ({count} expenses)"
        log_info(f"[SimpleQueryHandler] Average: ${average:.2f} from {count} expenses")
        return result
    
    def _compute_percentage(self, user_input: str, user_lower: str, expenses: List[Dict], total: float) -> str:
        """Compute percentage of spending on a specific category."""
        if not expenses or total == 0:
            return "No expenses found."
        
        # Extract the category/item from the query
        # Look for patterns like "percentage of my spending is on groceries"
        filter_term = None
        
        # Try to extract after "on" or "for"
        if ' on ' in user_lower:
            parts = user_lower.split(' on ', 1)
            if len(parts) > 1:
                filter_term = parts[1].strip()
        elif ' for ' in user_lower:
            parts = user_lower.split(' for ', 1)
            if len(parts) > 1:
                filter_term = parts[1].strip()
        
        # Also try "spending is on" pattern
        if not filter_term and 'spending is on' in user_lower:
            parts = user_lower.split('spending is on', 1)
            if len(parts) > 1:
                filter_term = parts[1].strip()
        
        if not filter_term:
            # Fallback: try to find category words
            category_words = ['groceries', 'rent', 'utilities', 'gas', 'coffee', 'food', 'dining']
            for word in category_words:
                if word in user_lower:
                    filter_term = word
                    break
        
        if not filter_term:
            return f"Your total spending is ${total:.2f}. To calculate a percentage, specify a category like 'What percentage of my spending is on groceries?'"
        
        # Remove trailing punctuation
        import string
        filter_term = filter_term.rstrip(string.punctuation)
        
        # Filter expenses by description
        filtered_total = 0
        for exp in expenses:
            desc = exp.get('description', '').lower()
            if filter_term in desc:
                filtered_total += exp.get('amount', 0)
        
        if filtered_total == 0:
            return f"You haven't spent anything on {filter_term}, so it's 0% of your spending."
        
        percentage = (filtered_total / total) * 100
        
        result = f"{filter_term.capitalize()} represents {percentage:.1f}% of your total spending (${filtered_total:.2f} out of ${total:.2f})"
        log_info(f"[SimpleQueryHandler] Percentage: {percentage:.1f}% for '{filter_term}'")
        return result
    
    def _compute_ratio(self, expenses: List[Dict]) -> str:
        """Compute ratio of largest to smallest expense."""
        if not expenses or len(expenses) < 2:
            return "Need at least 2 expenses to calculate a ratio."
        
        largest = max(expenses, key=lambda x: x.get('amount', 0))
        smallest = min(expenses, key=lambda x: x.get('amount', float('inf')))
        
        largest_amount = largest.get('amount', 0)
        smallest_amount = smallest.get('amount', 0)
        
        if smallest_amount == 0:
            return "Cannot calculate ratio: smallest expense is $0.00"
        
        ratio = largest_amount / smallest_amount
        
        largest_desc = largest.get('description', 'Unknown')
        smallest_desc = smallest.get('description', 'Unknown')
        
        result = f"The ratio of your largest expense (${largest_amount:.2f} for {largest_desc}) to your smallest expense (${smallest_amount:.2f} for {smallest_desc}) is {ratio:.2f}:1"
        log_info(f"[SimpleQueryHandler] Ratio: {ratio:.2f}:1 (${largest_amount:.2f} / ${smallest_amount:.2f})")
        return result
    
    def _compute_count(self, expenses: List[Dict]) -> str:
        """Compute count of expenses."""
        count = len(expenses)
        
        if count == 0:
            result = "You have no expenses."
        elif count == 1:
            result = "You have 1 expense."
        else:
            result = f"You have {count} expenses."
        
        log_info(f"[SimpleQueryHandler] Count: {count} expenses")
        return result
    
    def _generic_response(self, expenses: List[Dict], total: float) -> str:
        """Generic fallback response."""
        result = f"You have {len(expenses)} expenses totaling ${total:.2f}"
        log_info(f"[SimpleQueryHandler] Generic response: {len(expenses)} expenses, ${total:.2f}")
        return result
    
    # ==========================================
    # Utility Methods
    # ==========================================
    
    def _format_date(self, date: str, short: bool = False) -> str:
        """
        Format date string nicely.
        
        Args:
            date: Date string in YYYY-MM-DD format
            short: If True, return "Nov 15" format; if False, return "November 15, 2025"
            
        Returns:
            Formatted date string
        """
        if date == 'Unknown date' or not date or len(date) != 10:
            return date
        
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            if short:
                return date_obj.strftime('%b %d')
            else:
                return date_obj.strftime('%B %d, %Y')
        except Exception:
            return date

