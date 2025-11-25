# AI_py/tool_dispatcher.py
"""
Tool dispatcher for executing AI function calls.

Executes tool functions and returns results to the AI.
"""

import sys
import os
from typing import Dict, List, Optional, Tuple

# Import from parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from error_logger import log_info, log_warning, log_debug
from AI_py.handlers.simple_query_handler import SimpleQueryHandler
from AI_py.tools.definitions import get_tool_by_name


class ToolDispatcher:
    """Dispatches and executes tool function calls."""
    
    def __init__(self, simple_query_handler: SimpleQueryHandler):
        """Initialize with SimpleQueryHandler for computation."""
        self.handler = simple_query_handler
    
    def dispatch(self, tool_name: str, args: Dict, expenses: List[Dict], total: float, 
                 all_months: Optional[Dict] = None) -> str:
        """
        Execute a tool function call.
        
        Args:
            tool_name: Name of the tool to execute
            args: Tool arguments (dict)
            expenses: Current month's expenses
            total: Current month's total
            all_months: Optional dict of all months data for multi-month queries
            
        Returns:
            str: Tool execution result
        """
        log_info(f"[ToolDispatcher] Executing tool: {tool_name} with args: {args}")
        
        try:
            if tool_name == "get_largest_expense":
                return self.handler._compute_largest(expenses)
            
            elif tool_name == "get_lowest_expense":
                return self.handler._compute_lowest(expenses)
            
            elif tool_name == "get_total":
                return self.handler._compute_total(total)
            
            elif tool_name == "get_category_spending":
                category = args.get("category", "").lower()
                if not category:
                    return "Error: category parameter is required"
                # Use handler's filtered query logic
                user_input = f"spending on {category}"
                return self.handler._compute_filtered(user_input, user_input.lower(), expenses)
            
            elif tool_name == "get_average_expense":
                return self.handler._compute_average(expenses)
            
            elif tool_name == "get_category_percentage":
                category = args.get("category", "").lower()
                if not category:
                    return "Error: category parameter is required"
                user_input = f"percentage of spending on {category}"
                return self.handler._compute_percentage(user_input, user_input.lower(), expenses, total)
            
            elif tool_name == "get_expense_ratio":
                return self.handler._compute_ratio(expenses)
            
            elif tool_name == "get_expense_count":
                return self.handler._compute_count(expenses)
            
            elif tool_name == "get_top_categories":
                return self.handler._compute_categories(expenses)
            
            elif tool_name == "compare_months":
                month1 = args.get("month1", "")
                month2 = args.get("month2", "")
                if not month1 or not month2:
                    return "Error: month1 and month2 parameters are required"
                return self._compare_months(month1, month2, all_months)
            
            else:
                log_warning(f"[ToolDispatcher] Unknown tool: {tool_name}")
                return f"Error: Unknown tool '{tool_name}'"
                
        except Exception as e:
            log_warning(f"[ToolDispatcher] Error executing tool {tool_name}: {e}")
            return f"Error executing tool: {e}"
    
    def _compare_months(self, month1: str, month2: str, all_months: Optional[Dict]) -> str:
        """Compare spending between two months."""
        if not all_months:
            return "Error: Multi-month data not available"
        
        if month1 not in all_months or month2 not in all_months:
            return f"Error: One or both months not found. Available: {list(all_months.keys())}"
        
        total1 = all_months[month1][1]
        total2 = all_months[month2][1]
        
        change = total1 - total2
        if total2 > 0:
            percent_change = (change / total2) * 100
            direction = "increase" if change > 0 else "decrease"
            return f"{month1}: ${total1:.2f}\n{month2}: ${total2:.2f}\n{abs(percent_change):.1f}% {direction}"
        else:
            return f"{month1}: ${total1:.2f}\n{month2}: ${total2:.2f}"

