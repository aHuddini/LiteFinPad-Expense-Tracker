"""Prompt configuration and templates."""

from typing import Dict, List
from AI_py.tools.definitions import TOOLS, get_tool_names

class PromptConfig:
    """Manages prompt templates and system prompts."""
    
    @staticmethod
    def get_system_prompt() -> str:
        """Get system prompt with tool calling instructions."""
        # Build tool descriptions
        tool_descs = []
        for tool in TOOLS:
            name = tool.get("name_for_model", tool["name"])
            desc = tool["description"]
            params = tool.get("parameters", {})
            required = params.get("required", [])
            
            tool_desc = f"### {tool.get('name_for_human', name)}\n\n"
            tool_desc += f"{name}: {desc}\n"
            if required:
                tool_desc += f"Required parameters: {', '.join(required)}\n"
            tool_descs.append(tool_desc)
        
        tool_names = ', '.join(get_tool_names())
        
        return f"""You are an expense analysis assistant. You can answer queries by calling tools (functions).

# Tools

## You have access to the following tools:

{chr(10).join(tool_descs)}

## When you need to call a tool, insert the following command in your reply:

[FUNCTION]: tool_name
[ARGS]: {{"param": "value"}}
[RESULT]: tool_result (will be filled after tool execution)
[RETURN]: final_answer (your response to the user)

## How to use tools:

1. **Identify the right tool** from the list above
2. **Call the tool** using [FUNCTION] and [ARGS] markers
3. **Wait for tool result** - the system will execute the tool and provide [RESULT]
4. **Provide final answer** using [RETURN] marker

## Examples:

User: "What's my largest expense?"
You: [FUNCTION]: get_largest_expense
[ARGS]: {{}}
[RESULT]: (system will fill this)
[RETURN]: Your largest expense is $100.00 for groceries on November 15, 2025

User: "How much did I spend on groceries?"
You: [FUNCTION]: get_category_spending
[ARGS]: {{"category": "groceries"}}
[RESULT]: (system will fill this)
[RETURN]: You spent $500.00 on groceries (10 expenses)

## Important:
- Always use [FUNCTION] and [ARGS] to call tools
- Extract category names from user queries (e.g., "groceries", "rent")
- Use [RETURN] to provide the final answer to the user
- Do NOT write code or explain how to use the app - just call tools and answer"""
    
    @staticmethod
    def get_capabilities_response() -> str:
        """Get capabilities response for user queries."""
        return """I'm your AI expense assistant for LiteFinPad! Here's what I can do:

📝 **Add Expenses**
• "Add $50 for groceries on November 15th"
• "Add $100 groceries and $200 rent"
• "Record $25 coffee yesterday"
• Batch entry: "Add $50 groceries, $30 gas, $20 lunch"

🔍 **Query Your Expenses**
• "What's my largest expense?"
• "How much did I spend on groceries?"
• "Show me expenses from last week"
• "What category did I spend the most on?"

📊 **Analyze Spending**
• "Compare my spending this month vs last month"
• "What's my total spending for November?"
• "Which category is eating up my budget?"

All processing happens 100% offline on your machine - your data never leaves your computer!"""

