"""
Fallback Computation

Computes answers from expense data when AI fails or returns invalid responses.
Uses financial dictionary for better query understanding.
"""

from typing import Dict, List, Optional
from collections import defaultdict

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from error_logger import log_info, log_warning, log_debug
from AI_py.config.financial_dictionary import FinancialDictionary


class FallbackComputer:
    """Computes answers from expense data as fallback."""
    
    def __init__(self):
        """Initialize fallback computer."""
        self.dictionary = FinancialDictionary()
    
    def compute_answer(
        self, 
        user_input: str, 
        expenses: List[Dict], 
        total: float, 
        all_months: Optional[Dict] = None
    ) -> str:
        """
        Compute answer from expense data.
        
        Args:
            user_input: User's query
            expenses: Current month's expenses
            total: Current month's total
            all_months: Optional dict of all months data for multi-month queries
            
        Returns:
            Computed answer string
        """
        user_lower = user_input.lower()
        
        # Expand query with dictionary
        expanded = self.dictionary.expand_query(user_input)
        
        # Handle "monthly average" queries
        if 'monthly average' in user_lower or ('average' in user_lower and 'month' in user_lower):
            return self._compute_monthly_average(expenses, total, all_months)
        
        # Handle multi-month comparison queries
        multi_month_indicators = ['compare', 'vs', 'versus', 'last month', 'previous month', 
                                   'trend', 'over time', 'history', 'year', 'annual']
        if any(indicator in user_lower for indicator in multi_month_indicators):
            return self._compute_multi_month_comparison(all_months)
        
        # Handle largest expense
        if 'largest' in user_lower or 'biggest' in user_lower or 'highest' in user_lower or 'most expensive' in user_lower:
            return self._compute_largest(expenses)
        
        # Handle lowest expense
        if 'lowest' in user_lower or 'smallest' in user_lower or 'minimum' in user_lower or 'cheapest' in user_lower:
            return self._compute_lowest(expenses)
        
        # Handle total
        if 'total' in user_lower or 'sum' in user_lower:
            return f"Your total is ${total:.2f}"
        
        # Handle percentage queries
        if 'percentage' in user_lower or 'percent' in user_lower or '%' in user_lower:
            return self._compute_percentage(user_input, user_lower, expenses, total)
        
        # Handle ratio/proportion queries
        if 'ratio' in user_lower or 'proportion' in user_lower:
            return self._compute_ratio(user_input, user_lower, expenses, total)
        
        # Handle category queries
        if 'categor' in user_lower or ('spend' in user_lower and 'most' in user_lower):
            return self._compute_categories(expenses)
        
        # Handle filtered queries (spending on X)
        if expanded['categories']:
            category = expanded['categories'][0]
            return self._compute_category_spending(expenses, category)
        
        # Generic fallback
        return f"You have {len(expenses)} expenses totaling ${total:.2f}"
    
    def _compute_monthly_average(
        self, 
        expenses: List[Dict], 
        total: float, 
        all_months: Optional[Dict]
    ) -> str:
        """Compute monthly average spending."""
        if all_months and len(all_months) > 0:
            # Calculate average spending per month across all months
            total_spending = sum(all_months[month][1] for month in all_months)
            month_count = len(all_months)
            if month_count > 0:
                monthly_avg = total_spending / month_count
                return f"Your average monthly spending is ${monthly_avg:.2f} across {month_count} month(s)."
            else:
                return "No monthly data available to calculate average."
        else:
            # Single month - compute average expense amount
            if len(expenses) > 0:
                avg_expense = total / len(expenses)
                return f"Your average expense amount is ${avg_expense:.2f} ({len(expenses)} expenses)."
            else:
                return "No expenses found to calculate average."
    
    def _compute_multi_month_comparison(self, all_months: Optional[Dict]) -> str:
        """Compute multi-month comparison."""
        if not all_months or len(all_months) < 2:
            return "I need access to multiple months of data to answer this question. This feature is still being refined."
        
        sorted_months = sorted(all_months.keys(), reverse=True)
        if len(sorted_months) >= 2:
            current_month = sorted_months[0]
            previous_month = sorted_months[1]
            current_total = all_months[current_month][1]
            previous_total = all_months[previous_month][1]
            
            if previous_total > 0:
                change = current_total - previous_total
                percent_change = (change / previous_total) * 100
                direction = "increase" if change > 0 else "decrease"
                return f"This month ({current_month}): ${current_total:.2f}\nLast month ({previous_month}): ${previous_total:.2f}\n{abs(percent_change):.1f}% {direction}"
            else:
                return f"This month ({current_month}): ${current_total:.2f}\nLast month ({previous_month}): ${previous_total:.2f}"
        
        return "I need access to multiple months of data to answer this question."
    
    def _compute_largest(self, expenses: List[Dict]) -> str:
        """Compute largest expense."""
        if not expenses:
            return "No expenses found."
        
        largest = max(expenses, key=lambda x: x.get('amount', 0))
        amount = largest.get('amount', 0)
        desc = largest.get('description', 'Unknown')
        date = largest.get('date', 'Unknown date')
        
        # Format date nicely
        if date != 'Unknown date' and len(date) == 10:
            try:
                from datetime import datetime
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                date_formatted = date_obj.strftime('%B %d, %Y')
            except:
                date_formatted = date
        else:
            date_formatted = date
        
        return f"Your largest expense is ${amount:.2f} for {desc} on {date_formatted}"
    
    def _compute_lowest(self, expenses: List[Dict]) -> str:
        """Compute lowest expense."""
        if not expenses:
            return "No expenses found."
        
        lowest = min(expenses, key=lambda x: x.get('amount', float('inf')))
        amount = lowest.get('amount', 0)
        desc = lowest.get('description', 'Unknown')
        date = lowest.get('date', 'Unknown date')
        
        # Format date nicely
        if date != 'Unknown date' and len(date) == 10:
            try:
                from datetime import datetime
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                date_formatted = date_obj.strftime('%B %d, %Y')
            except:
                date_formatted = date
        else:
            date_formatted = date
        
        return f"Your lowest expense is ${amount:.2f} for {desc} on {date_formatted}"
    
    def _compute_categories(self, expenses: List[Dict]) -> str:
        """Compute category spending."""
        if not expenses:
            return "No expenses found."
        
        # Group expenses by description (treating description as category)
        category_totals = defaultdict(float)
        for exp in expenses:
            desc = exp.get('description', 'Unknown').strip()
            if desc:
                category_totals[desc] += exp.get('amount', 0)
        
        # Sort by total amount (descending)
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        
        if not sorted_categories:
            return "No category data available."
        
        # Format top categories with better formatting
        top_categories = sorted_categories[:5]  # Top 5
        category_lines = []
        for i, (cat, amt) in enumerate(top_categories, 1):
            category_lines.append(f"{i}. {cat}: ${amt:,.2f}")
        
        result = "**Top Spending Categories:**\n" + "\n".join(category_lines)
        return result
    
    def _compute_category_spending(self, expenses: List[Dict], category: str) -> str:
        """Compute spending for a specific category."""
        # Use dictionary to find category synonyms
        category_normalized = self.dictionary.find_category(category)
        
        # Filter expenses by category (description matching)
        filtered = []
        for exp in expenses:
            desc = exp.get('description', '').lower()
            if category_normalized.lower() in desc or category.lower() in desc:
                filtered.append(exp)
        
        if not filtered:
            return f"You haven't spent anything on {category}."
        
        total = sum(exp.get('amount', 0) for exp in filtered)
        return f"You spent ${total:.2f} on {category} ({len(filtered)} expenses)"
    
    def _compute_percentage(self, user_input: str, user_lower: str, expenses: List[Dict], total: float) -> str:
        """Compute percentage of spending on a specific category."""
        if total == 0:
            return "No spending data available to calculate percentage."
        
        # Find category mentioned in query
        category_keywords = {
            'rent': ['rent'],
            'groceries': ['grocer', 'grocery'],
            'utilities': ['utilit', 'utility'],
            'entertainment': ['entertain', 'entertainment'],
            'dining': ['dining', 'dine', 'restaurant'],
            'gas': ['gas', 'fuel'],
            'shopping': ['shopping', 'shop']
        }
        
        category = None
        for cat, keywords in category_keywords.items():
            if any(kw in user_lower for kw in keywords):
                category = cat
                break
        
        if not category:
            return f"Your total spending is ${total:.2f}. To calculate a percentage, specify a category like 'What percentage of my spending is on groceries?'"
        
        # Calculate category total
        category_total = sum(exp.get('amount', 0) for exp in expenses 
                           if any(kw in exp.get('description', '').lower() for kw in category_keywords.get(category, [category])))
        
        if category_total == 0:
            return f"You haven't spent anything on {category}."
        
        percentage = (category_total / total) * 100
        return f"{category.capitalize()} represents {percentage:.1f}% of your total spending (${category_total:.2f} out of ${total:.2f})"
    
    def _compute_ratio(self, user_input: str, user_lower: str, expenses: List[Dict], total: float) -> str:
        """Compute ratio between expenses."""
        if not expenses or len(expenses) < 2:
            return "Need at least 2 expenses to calculate a ratio."
        
        # Check for largest to smallest ratio
        if 'largest' in user_lower and 'smallest' in user_lower:
            amounts = [exp.get('amount', 0) for exp in expenses if exp.get('amount', 0) > 0]
            if len(amounts) >= 2:
                largest = max(amounts)
                smallest = min(amounts)
                ratio = largest / smallest if smallest > 0 else 0
                
                # Find the actual expenses
                largest_exp = max(expenses, key=lambda x: x.get('amount', 0))
                smallest_exp = min(expenses, key=lambda x: x.get('amount', float('inf')))
                
                return f"The ratio of your largest expense (${largest:.2f} for {largest_exp.get('description', 'Unknown')}) to your smallest expense (${smallest:.2f} for {smallest_exp.get('description', 'Unknown')}) is {ratio:.2f}:1"
        
        # Check for category ratio (e.g., groceries to rent)
        elif 'grocer' in user_lower and 'rent' in user_lower:
            groceries_total = sum(exp.get('amount', 0) for exp in expenses if 'grocer' in exp.get('description', '').lower())
            rent_total = sum(exp.get('amount', 0) for exp in expenses if 'rent' in exp.get('description', '').lower())
            if groceries_total > 0 and rent_total > 0:
                ratio = rent_total / groceries_total
                return f"The ratio of rent to groceries spending is {ratio:.2f}:1 (Rent: ${rent_total:.2f}, Groceries: ${groceries_total:.2f})"
        
        # Generic ratio - largest to smallest
        amounts = [exp.get('amount', 0) for exp in expenses if exp.get('amount', 0) > 0]
        if len(amounts) >= 2:
            largest = max(amounts)
            smallest = min(amounts)
            ratio = largest / smallest if smallest > 0 else 0
            return f"The ratio of your largest expense (${largest:.2f}) to your smallest expense (${smallest:.2f}) is {ratio:.2f}:1"
        
        return "Unable to calculate ratio. Please specify what to compare (e.g., 'largest to smallest' or 'rent to groceries')."

