"""
Simplified prompt configuration for small language models (500M-1B parameters).

Small models like Qwen 0.5B cannot handle complex tool-calling or multi-step reasoning.
This module provides ultra-simple, direct prompts that work better with small models.
"""

class SimplePromptConfig:
    """Simplified prompts optimized for small language models."""
    
    @staticmethod
    def get_system_prompt() -> str:
        """
        Get ultra-simple system prompt for small models.
        
        Small models need:
        - Direct instructions (no abstraction)
        - Short prompts (save tokens)
        - Clear examples
        - No tool calling complexity
        """
        return """You are a direct-answer expense assistant. Follow these rules strictly:

OUTPUT FORMAT:
- Output ONLY the answer in natural language
- Format: Direct statement with amounts as $XX.XX
- Include dates when relevant (format: Month DD, YYYY)
- Do NOT explain, use formulas, code, or say "you can use"

CRITICAL RULES:
- Answer DIRECTLY - do NOT explain how to calculate
- Do NOT write formulas, code, or instructions
- Do NOT say "you can use", "here's how", "to compare", "to determine", "to find"
- Just provide the answer using the data

EXAMPLES (Good - DO THIS):
User: "What's my largest expense?"
Data: [{"amount": 100, "description": "rent", "date": "2025-11-15"}]
Answer: Your largest expense is $100.00 for rent on November 15, 2025

User: "Compare my spending this month vs. last month"
Data: This month: $1000, Last month: $800
Answer: This month (2025-11): $1000.00
Last month (2025-10): $800.00
25.0% increase

User: "How much did I spend on groceries?"
Data: [{"amount": 50, "description": "groceries", "date": "2025-11-10"}]
Answer: You spent $50.00 on groceries (1 expense)

EXAMPLES (Bad - DO NOT DO THIS):
User: "Compare my spending this month vs. last month"
Bad Answer: "To compare your spending, you can use the following formula: Current - Last = Difference"
Good Answer: "This month (2025-11): $1000.00
Last month (2025-10): $800.00
25.0% increase"

User: "What's my largest expense?"
Bad Answer: "Here's how you can implement this: ```python def get_expense_result..."
Good Answer: "Your largest expense is $100.00 for rent on November 15, 2025"

Remember: Answer directly, no explanations, no code, no formulas."""
    
    @staticmethod
    def get_query_prompt(user_input: str, context: str) -> str:
        """
        Get simplified query prompt for small models.
        
        Args:
            user_input: User's question
            context: Expense data context (should be limited to avoid context overflow)
            
        Returns:
            Simple, direct prompt
        """
        # Limit context size for small models (they have limited context windows)
        # Take first 1000 chars of context to avoid overflow
        context_limited = context[:1000] + "..." if len(context) > 1000 else context
        
        return f"""Question: {user_input}

Expense Data:
{context_limited}

Output only the direct answer. Do NOT explain methods, write code, or use formulas.
Answer:"""
    
    @staticmethod
    def get_capabilities_response() -> str:
        """Get capabilities response."""
        return """I can help you with expenses:
- Add expenses: "Add $50 for groceries"
- Query expenses: "What's my total?"
- Delete expenses: "Delete the coffee expense"
All processing is 100% offline."""

