# AI_py/tool_definitions.py
"""
Tool definitions for AI function calling.

These tools are exposed to the AI model so it can call structured functions
instead of trying to generate JSON or compute answers directly.
"""

TOOLS = [
    {
        "name": "get_largest_expense",
        "name_for_human": "Get Largest Expense",
        "name_for_model": "get_largest_expense",
        "description": "Get the largest (most expensive) expense from your expense list. Returns the expense with the highest amount, including its description and date.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_lowest_expense",
        "name_for_human": "Get Lowest Expense",
        "name_for_model": "get_lowest_expense",
        "description": "Get the lowest (cheapest) expense from your expense list. Returns the expense with the smallest amount, including its description and date.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_total",
        "name_for_human": "Get Total Spending",
        "name_for_model": "get_total",
        "description": "Get the total amount of all expenses for the current month.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_category_spending",
        "name_for_human": "Get Category Spending",
        "name_for_model": "get_category_spending",
        "description": "Get total spending for a specific category or description. Use this when the user asks about spending on a specific item like 'groceries', 'rent', 'gas', etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "The category or description to filter by (e.g., 'groceries', 'rent', 'gas', 'utilities')"
                }
            },
            "required": ["category"]
        }
    },
    {
        "name": "get_average_expense",
        "name_for_human": "Get Average Expense",
        "name_for_model": "get_average_expense",
        "description": "Get the average expense amount. Calculates the mean of all expense amounts.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_category_percentage",
        "name_for_human": "Get Category Percentage",
        "name_for_model": "get_category_percentage",
        "description": "Get the percentage of total spending for a specific category. Use this when the user asks 'what percentage of my spending is on X?'",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "The category to analyze (e.g., 'groceries', 'rent')"
                }
            },
            "required": ["category"]
        }
    },
    {
        "name": "get_expense_ratio",
        "name_for_human": "Get Expense Ratio",
        "name_for_model": "get_expense_ratio",
        "description": "Get the ratio of largest to smallest expense. Use this when the user asks about the ratio between expenses.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_expense_count",
        "name_for_human": "Get Expense Count",
        "name_for_model": "get_expense_count",
        "description": "Get the total number of expenses. Use this when the user asks 'how many expenses do I have?' or 'count my expenses'.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_top_categories",
        "name_for_human": "Get Top Categories",
        "name_for_model": "get_top_categories",
        "description": "Get the top spending categories. Returns categories sorted by total spending amount. Use this when the user asks 'what categories did I spend the most on?' or 'show me spending by category'.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "compare_months",
        "name_for_human": "Compare Months",
        "name_for_model": "compare_months",
        "description": "Compare spending between two months. Use this when the user asks to compare months (e.g., 'compare this month to last month', 'compare November to October').",
        "parameters": {
            "type": "object",
            "properties": {
                "month1": {
                    "type": "string",
                    "description": "First month to compare (format: YYYY-MM, e.g., '2025-11')"
                },
                "month2": {
                    "type": "string",
                    "description": "Second month to compare (format: YYYY-MM, e.g., '2025-10')"
                }
            },
            "required": ["month1", "month2"]
        }
    }
]

def get_tool_names() -> list[str]:
    """Get list of all tool names."""
    return [tool["name_for_model"] for tool in TOOLS]

def get_tool_by_name(name: str) -> dict | None:
    """Get tool definition by name."""
    for tool in TOOLS:
        if tool["name"] == name or tool["name_for_model"] == name:
            return tool
    return None

