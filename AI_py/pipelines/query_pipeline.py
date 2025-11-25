"""
Query Processing Pipeline

Orchestrates query processing flow: routing, data loading, AI inference, and response generation.
"""

from typing import Dict, List, Optional, Callable
from AI_py.llm.manager import LLMManager
from AI_py.llm.inference import InferenceEngine
from AI_py.utils.data_loader import DataLoader
from AI_py.utils.context_builder import ContextBuilder
from AI_py.utils.temp_file_manager import TempFileManager
from AI_py.fallback.compute import FallbackComputer
from AI_py.handlers.simple_query_handler import SimpleQueryHandler
from AI_py.tools import ToolDispatcher, parse_function_call, extract_final_answer, FN_NAME
from AI_py.config.prompt_config import PromptConfig
from AI_py.config.prompt_config_simple import SimplePromptConfig
from AI_py.config.financial_dictionary import FinancialDictionary

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from error_logger import log_info, log_warning, log_debug


class QueryPipeline:
    """Orchestrates query processing pipeline."""
    
    def __init__(self, expense_tracker, enable_sketching: bool = True, llm_manager=None):
        """
        Initialize query pipeline.
        
        Args:
            expense_tracker: Expense tracker instance for data access
            enable_sketching: If True, write sketches to temp_AI folder (default: True)
            llm_manager: Optional LLMManager instance to share (default: creates new)
        """
        self.expense_tracker = expense_tracker
        self.llm_manager = llm_manager if llm_manager is not None else LLMManager()
        self.inference_engine = None  # Lazy-loaded
        self.data_loader = DataLoader()
        self.context_builder = ContextBuilder()
        self.fallback_computer = FallbackComputer()
        self.simple_query_handler = SimpleQueryHandler()
        self.tool_dispatcher = ToolDispatcher(self.simple_query_handler)
        self.prompt_config = PromptConfig()
        self.simple_prompt_config = SimplePromptConfig()
        self.dictionary = FinancialDictionary()
        
        # Check if using small model (use simplified prompts)
        # SmolLM2 (1.7B) is NOT a small model - it can handle more complex prompts
        preferred_model = self.llm_manager.get_preferred_model()
        if preferred_model:
            # Only treat very small models (<1B) as "small"
            self.is_small_model = any(m in preferred_model.lower() for m in ['0.5b', '360m', 'smollm:360m', 'qwen:0.5b'])
        else:
            # Default to small model if we can't determine (safer assumption)
            self.is_small_model = True
            log_warning("[QueryPipeline] Could not determine model size, defaulting to small model mode")
        self.enable_sketching = enable_sketching
        self.thinking_steps = []  # Track thinking steps for sketching
    
    def _get_inference_engine(self) -> InferenceEngine:
        """Get or create inference engine."""
        if self.inference_engine is None:
            model = self.llm_manager.get_model()
            self.inference_engine = InferenceEngine(model)
        return self.inference_engine
    
    def process_query(
        self, 
        user_input: str, 
        month_key: str, 
        thinking_callback: Optional[Callable[[str], None]] = None
    ) -> Dict:
        """
        Process a query through the pipeline.
        
        Args:
            user_input: User's query
            month_key: Month key (YYYY-MM)
            thinking_callback: Optional callback for thinking steps
            
        Returns:
            Dict with 'intent', 'response', 'expenses_to_add', 'confirmation_needed'
        """
        def _think(msg):
            if thinking_callback:
                thinking_callback(msg)
            # Track thinking steps for sketching
            if self.enable_sketching:
                self.thinking_steps.append(msg)
        
        # Reset thinking steps for this query
        self.thinking_steps = []
        
        # Check if LLM is available
        if not self.llm_manager.is_available():
            return {
                'intent': 'error',
                'response': "AI features require llama-cpp-python and a model file. Please install: pip install llama-cpp-python",
                'expenses_to_add': [],
                'confirmation_needed': False
            }
        
        # Check if general question
        if self._is_general_question(user_input):
            _think("💭 THOUGHT: Is this a general question? True")
            _think("⚡ ACTION: Routing to general question handler")
            return self._handle_general_question(user_input, thinking_callback)
        
        # Check if capability question
        if self._is_capability_question(user_input):
            _think("💭 THOUGHT: Is this a capability question? True")
            _think("⚡ ACTION: Returning capabilities response")
            capabilities = self.simple_prompt_config.get_capabilities_response() if self.is_small_model else self.prompt_config.get_capabilities_response()
            return {
                'intent': 'query',
                'response': capabilities,
                'expenses_to_add': [],
                'confirmation_needed': False
            }
        
        # Check if multi-month query
        is_multi_month = self._is_multi_month_query(user_input)
        
        if is_multi_month:
            _think("📊 Loading multiple months...")
            all_months = self.data_loader.load_all_available_months(current_month_key=month_key)
            
            if not all_months:
                return {
                    'intent': 'query',
                    'response': "No expense data found.",
                    'expenses_to_add': [],
                    'confirmation_needed': False
                }
            
            # For all models, handle multi-month queries with Python (more reliable and concise)
            # AI tends to be too verbose for multi-month comparisons
            _think("⚡ ACTION: Using Python computation for multi-month query (more reliable)")
            response_text = self.fallback_computer.compute_answer(user_input, [], 0.0, all_months)
            _think(f"✅ ANSWER: {response_text}")
            result = {
                'intent': 'query',
                'response': response_text,
                'expenses_to_add': [],
                'confirmation_needed': False
            }
            if self.enable_sketching:
                self._sketch_query_result(user_input, response_text, "python_multi_month", {"reason": "Python computation for reliability"})
            return result
            
            # Legacy AI processing for multi-month (not used anymore - Python is more reliable)
            # All multi-month queries now use Python computation above
        else:
            # Single month query
            expenses, total = self.data_loader.load_month_data(month_key)
            
            if not expenses:
                return {
                    'intent': 'query',
                    'response': f"No expense data found for {month_key}.",
                    'expenses_to_add': [],
                    'confirmation_needed': False
                }
            
            context = self.context_builder.build_single_month_context(expenses, total, month_key)
            log_info(f"[AI Processing] Built single-month context for {month_key}: {len(expenses)} expenses, total ${total:.2f}")
        
        # Check if all-time query (across all months)
        user_lower = user_input.lower()
        is_all_time = any(kw in user_lower for kw in ['all-time', 'all time', 'ever', 'all months', 'all years', 'across all', 'throughout', 'entire history'])
        all_months_count = 0
        
        # If all-time query, load all months and aggregate
        if is_all_time:
            _think("📊 Loading all-time data (all months)...")
            all_months_data = self.data_loader.load_all_available_months(current_month_key=month_key)
            if all_months_data:
                # Aggregate all expenses across all months
                all_expenses = []
                all_total = 0.0
                for month_key_data, (month_expenses, month_total) in all_months_data.items():
                    all_expenses.extend(month_expenses)
                    all_total += month_total
                expenses = all_expenses
                total = all_total
                all_months_count = len(all_months_data)
                _think(f"📊 Loaded {all_months_count} months, {len(expenses)} total expenses")
        
        # Try simple query handler first
        _think("💭 THOUGHT: Checking if query can be handled by SimpleQueryHandler...")
        if self.simple_query_handler.can_handle(user_input):
            _think("⚡ ACTION: Using SimpleQueryHandler (fast path)")
            response = self.simple_query_handler.handle(user_input, expenses, total)
            
            # Add context if all-time query
            if is_all_time and all_months_count > 0:
                response = f"{response}\n\n*(All-time across {all_months_count} months)*"
            
            _think(f"✅ ANSWER: {response}")
            
            # Sketch simple query response
            if self.enable_sketching:
                self._sketch_query_result(
                    user_input, 
                    response, 
                    "simple_handler",
                    {"expense_count": len(expenses), "total": total}
                )
            
            return {
                'intent': 'query',
                'response': response,
                'expenses_to_add': [],
                'confirmation_needed': False
            }
        
        # Process with AI
        _think("💭 THOUGHT: Query requires AI processing")
        _think("⚡ ACTION: Processing with AI inference engine")
        
        return self._process_with_ai(
            user_input, 
            context, 
            expenses, 
            total, 
            all_months if is_multi_month else None,
            thinking_callback
        )
    
    def _process_with_ai(
        self,
        user_input: str,
        context: str,
        expenses: List[Dict],
        total: float,
        all_months: Optional[Dict],
        thinking_callback: Optional[Callable[[str], None]]
    ) -> Dict:
        """Process query with AI inference."""
        def _think(msg):
            if thinking_callback:
                thinking_callback(msg)
            # Track thinking steps for sketching
            if self.enable_sketching:
                self.thinking_steps.append(msg)
        
        # Sketch input context before processing
        if self.enable_sketching:
            self._sketch_input_context(user_input, context, expenses, total, all_months)
        
        # Log context summary for user visibility
        context_summary = self._get_context_summary(context, expenses, total)
        _think(f"📊 DATA: {context_summary}")
        log_info(f"[AI Processing] Context summary: {context_summary}")
        
        # Build messages - use simplified prompts for small models, enhanced prompts for larger models
        # SmolLM2 (1.7B) can handle enhanced prompts with better context
        if self.is_small_model:
            # Ultra-simple approach for small models (no tool calling)
            messages = [
                {'role': 'system', 'content': self.simple_prompt_config.get_system_prompt()},
                {'role': 'user', 'content': self.simple_prompt_config.get_query_prompt(user_input, context)}
            ]
        else:
            # For SmolLM2 and larger models: use direct prompts with full context
            # Enhanced prompt with specific instructions for percentage/ratio queries
            user_lower = user_input.lower()
            if 'percentage' in user_lower or 'percent' in user_lower or '%' in user_lower:
                enhanced_prompt = f"""Question: {user_input}

Expense Data:
{context}

Instructions:
- Calculate the percentage: (category_total / total_spending) * 100
- Format as: "X% of your spending" or "X percent"
- Include the category name and percentage
- Do NOT explain the calculation, just provide the answer

Answer:"""
            elif 'ratio' in user_lower or 'proportion' in user_lower:
                enhanced_prompt = f"""Question: {user_input}

Expense Data:
{context}

Instructions:
- Calculate the ratio between the two values
- Format as: "X:1" or "X to 1"
- Include what is being compared
- Do NOT explain the calculation, just provide the answer

Answer:"""
            else:
                enhanced_prompt = f"""Question: {user_input}

Expense Data:
{context}

Instructions:
- Answer the question directly using the expense data provided
- Include specific numbers and amounts
- Format amounts as $XX.XX
- Do NOT explain how to calculate, just provide the answer

Answer:"""
            
            messages = [
                {'role': 'system', 'content': 'You are a financial assistant. Answer questions about expenses directly and accurately using the provided data. Always provide specific numbers and calculations.'},
                {'role': 'user', 'content': enhanced_prompt}
            ]
            
            # Log prompt details
            prompt_type = "percentage" if ('percentage' in user_input.lower() or 'percent' in user_input.lower() or '%' in user_input.lower()) else ("ratio" if ('ratio' in user_input.lower() or 'proportion' in user_input.lower()) else "general")
            _think(f"💡 PROMPT: Using {prompt_type} query prompt")
            log_info(f"[AI Processing] Prompt type: {prompt_type}")
            log_debug(f"[AI Processing] Full prompt:\n{enhanced_prompt[:500]}...")
        
        _think("⚡ ACTION: Calling AI model for inference...")
        log_info(f"[AI Processing] Sending request to model: {self.llm_manager.get_preferred_model()}")
        
        try:
            inference = self._get_inference_engine()
            # Optimized parameters for small models (per Grok recommendations)
            # temperature=0.2 allows slight variability to escape biased patterns
            # top_p=0.5 provides broader sampling without chaos
            response = inference.chat_completion(
                messages=messages,
                max_tokens=300,
                temperature=0.2,  # Increased from 0.0 for better flexibility
                top_p=0.5  # Increased from 0.1 for broader sampling
            )
            
            response_content = inference.extract_response_text(response)
            if not response_content:
                raise ValueError("Empty response from model")
            
            # Log full response
            _think(f"👁️ OBSERVATION: Model returned response: {response_content[:200]}...")
            log_info(f"[AI Processing] Full AI response: {response_content}")
            
            # Show reasoning if it's a calculation query
            if any(word in user_input.lower() for word in ['percentage', 'percent', 'ratio', 'proportion', 'calculate']):
                reasoning = self._extract_reasoning_from_context(context, user_input, expenses, total)
                if reasoning:
                    _think(f"🧮 CALCULATION: {reasoning}")
                    log_info(f"[AI Processing] Calculation reasoning: {reasoning}")
            
            # Sketch raw AI response
            if self.enable_sketching:
                self._sketch_raw_response(user_input, response_content, messages)
            
            # For small models, skip tool calling and use direct response
            if self.is_small_model:
                # Small models: use response directly, fallback if it looks like code/instructions
                response_lower = response_content.lower()
                has_code = 'def ' in response_content or '```' in response_content or 'import ' in response_content
                # Enhanced instruction detection per Grok recommendations
                has_instructions = any(p in response_lower for p in [
                    'you can', 'simply type', 'use the', 'here\'s how', 'here is how',
                    'you can use', 'following formula', 'formula', 'calculate', 'to compare',
                    'to determine', 'to find', 'to get', 'to answer', 'implement this',
                    'you need to', 'you should', 'step', 'method', 'approach', 'way to',
                    'how to', 'how you can', 'can use', 'use this', 'try this'
                ])
                
                # Strip quotes from response
                response_content = response_content.strip('"').strip("'").strip()
                
                # Validate answer relevance - check if AI actually answered the question
                answer_relevant = self._validate_answer_relevance(user_input, response_content)
                
                # Validate numerical accuracy for percentage/ratio queries
                answer_accurate = True
                calculated_value = None
                if any(word in user_input.lower() for word in ['percentage', 'percent', '%', 'ratio', 'proportion']):
                    calculated_value = self._calculate_expected_value(user_input, expenses, total)
                    if calculated_value is not None:
                        answer_accurate = self._validate_answer_accuracy(user_input, response_content, calculated_value)
                        if not answer_accurate:
                            _think(f"⚠️ ACCURACY: AI answer differs from calculation")
                            log_warning(f"[AI Processing] Accuracy check failed: AI={response_content}, Calculated={calculated_value}")
                
                if has_code or has_instructions or not answer_relevant or not answer_accurate:
                    reason = "Code/instructions detected" if (has_code or has_instructions) else (
                        "Answer not relevant" if not answer_relevant else "Answer accuracy check failed"
                    )
                    _think(f"⚠️ OBSERVATION: {reason}, using fallback")
                    
                    # Use Python computation (more reliable)
                    response_text = self.fallback_computer.compute_answer(user_input, expenses, total, all_months)
                    
                    # If we have a calculated value and AI was wrong, show both
                    if calculated_value is not None and not answer_accurate:
                        _think(f"📊 CALCULATED: {calculated_value}")
                    
                    _think(f"✅ ANSWER: {response_text}")
                    result = {
                        'intent': 'query',
                        'response': response_text,
                        'expenses_to_add': [],
                        'confirmation_needed': False
                    }
                    if self.enable_sketching:
                        self._sketch_query_result(user_input, response_text, "fallback_small_model", {
                            "reason": reason,
                            "calculated_value": calculated_value,
                            "ai_response": response_content
                        })
                    return result
                else:
                    # Direct response from small model
                    _think(f"✅ ANSWER: {response_content[:200]}...")
                    result = {
                        'intent': 'query',
                        'response': response_content,
                        'expenses_to_add': [],
                        'confirmation_needed': False
                    }
                    if self.enable_sketching:
                        self._sketch_query_result(user_input, response_content, "direct_small_model", {})
                    return result
            
            # For larger models (SmolLM2): validate answer relevance, accuracy, and check for issues
            # SmolLM2 doesn't use tool calling - it provides direct answers
            
            # Strip quotes from response
            response_content = response_content.strip('"').strip("'").strip()
            
            # Validate answer relevance
            answer_relevant = self._validate_answer_relevance(user_input, response_content)
            
            # Validate numerical accuracy for percentage/ratio queries
            answer_accurate = True
            calculated_value = None
            if any(word in user_input.lower() for word in ['percentage', 'percent', '%', 'ratio', 'proportion']):
                calculated_value = self._calculate_expected_value(user_input, expenses, total)
                if calculated_value is not None:
                    answer_accurate = self._validate_answer_accuracy(user_input, response_content, calculated_value)
                    if not answer_accurate:
                        _think(f"⚠️ ACCURACY: AI answer differs from calculation (AI may be wrong)")
                        log_warning(f"[AI Processing] Accuracy check failed: AI={response_content}, Calculated={calculated_value}")
            
            response_lower = response_content.lower()
            has_code = 'def ' in response_content or '```' in response_content or 'import ' in response_content
            has_instructions = any(p in response_lower for p in [
                'you can', 'simply type', 'use the', 'here\'s how', 'here is how',
                'you can use', 'following formula', 'formula', 'calculate', 'to compare',
                'to determine', 'to find', 'to get', 'to answer', 'implement this'
            ])
            
            if has_code or has_instructions or not answer_relevant or not answer_accurate:
                reason = "Code/instructions detected" if (has_code or has_instructions) else (
                    "Answer not relevant" if not answer_relevant else "Answer accuracy check failed"
                )
                _think(f"⚠️ OBSERVATION: {reason}, using fallback")
                
                # Use Python computation (more reliable)
                response_text = self.fallback_computer.compute_answer(user_input, expenses, total, all_months)
                
                # If we have a calculated value and AI was wrong, show both
                if calculated_value is not None and not answer_accurate:
                    _think(f"📊 CALCULATED: {calculated_value}")
                    log_info(f"[AI Processing] Using calculated value: {calculated_value} (AI was inaccurate)")
                
                _think(f"✅ ANSWER: {response_text}")
                result = {
                    'intent': 'query',
                    'response': response_text,
                    'expenses_to_add': [],
                    'confirmation_needed': False
                }
                if self.enable_sketching:
                    self._sketch_query_result(user_input, response_text, "fallback_large_model", {
                        "reason": reason,
                        "calculated_value": calculated_value,
                        "ai_response": response_content
                    })
                return result
            
            # Valid response from larger model
            _think(f"✅ ANSWER: {response_content[:200]}...")
            result = {
                'intent': 'query',
                'response': response_content,
                'expenses_to_add': [],
                'confirmation_needed': False
            }
            if self.enable_sketching:
                self._sketch_query_result(user_input, response_content, "direct_large_model", {
                    "calculated_value": calculated_value
                })
            return result
            
            # Legacy tool-calling code (kept for reference, but not used for SmolLM2)
            has_function_marker = FN_NAME in response_content or '✿FUNCTION✿' in response_content
            
            if has_function_marker:
                _think("💭 THOUGHT: Function call detected")
                tool_call = parse_function_call(response_content)
                
                if tool_call:
                    tool_name, tool_args = tool_call
                    _think(f"⚡ ACTION: Executing tool: {tool_name}")
                    
                    tool_result = self.tool_dispatcher.dispatch(
                        tool_name,
                        tool_args,
                        expenses,
                        total,
                        all_months
                    )
                    
                    _think(f"👁️ OBSERVATION: Tool result: {tool_result[:150]}...")
                    
                    # Sketch tool execution
                    if self.enable_sketching:
                        self._sketch_tool_execution(tool_name, tool_args, tool_result)
                    
                    # Check if AI provided final answer
                    final_answer = extract_final_answer(response_content)
                    if final_answer:
                        _think(f"✅ ANSWER: {final_answer}")
                        result = {
                            'intent': 'query',
                            'response': final_answer,
                            'expenses_to_add': [],
                            'confirmation_needed': False
                        }
                        if self.enable_sketching:
                            self._sketch_query_result(user_input, final_answer, "tool_call_with_answer", {"tool": tool_name})
                        return result
                    else:
                        # Use tool result as answer
                        _think(f"✅ ANSWER: {tool_result}")
                        result = {
                            'intent': 'query',
                            'response': tool_result,
                            'expenses_to_add': [],
                            'confirmation_needed': False
                        }
                        if self.enable_sketching:
                            self._sketch_query_result(user_input, tool_result, "tool_call_result", {"tool": tool_name})
                        return result
            
            # Check if AI echoed prompt or returned instructions
            if response_content.startswith('User:') or ('User:' in response_content and 'Expense Data:' in response_content):
                _think("⚠️ OBSERVATION: AI echoed prompt, using fallback")
                response_text = self.fallback_computer.compute_answer(user_input, expenses, total, all_months)
                _think(f"✅ ANSWER: {response_text}")
                result = {
                    'intent': 'query',
                    'response': response_text,
                    'expenses_to_add': [],
                    'confirmation_needed': False
                }
                if self.enable_sketching:
                    self._sketch_query_result(user_input, response_text, "fallback_echo", {"reason": "AI echoed prompt"})
                return result
            
            # Check for instruction patterns and code generation
            response_lower = response_content.lower()
            instruction_patterns = [
                'to determine', 'you can use', 'simply type', 'add expenses',
                'you can say', 'try:', 'use the', 'in the', 'field',
                'here\'s how', 'here is how', 'you can implement', 'def ', 'import ',
                '```python', '```', 'function', 'return ', 'if tool =='
            ]
            
            # Check for Python code blocks
            has_code_block = '```python' in response_content or '```' in response_content
            has_python_code = 'def ' in response_content and ('return ' in response_content or 'if ' in response_content)
            
            if any(pattern in response_lower for pattern in instruction_patterns) or has_code_block or has_python_code:
                _think("⚠️ OBSERVATION: Code/instructions detected, using fallback")
                response_text = self.fallback_computer.compute_answer(user_input, expenses, total, all_months)
                _think(f"✅ ANSWER: {response_text}")
                result = {
                    'intent': 'query',
                    'response': response_text,
                    'expenses_to_add': [],
                    'confirmation_needed': False
                }
                if self.enable_sketching:
                    self._sketch_query_result(user_input, response_text, "fallback_code", {"reason": "Code/instructions detected"})
                return result
            
            # Use response as-is
            _think(f"✅ ANSWER: {response_content[:200]}...")
            result = {
                'intent': 'query',
                'response': response_content,
                'expenses_to_add': [],
                'confirmation_needed': False
            }
            if self.enable_sketching:
                self._sketch_query_result(user_input, response_content, "direct_response", {})
            return result
            
        except Exception as e:
            log_warning(f"[QueryPipeline] AI processing failed: {e}")
            _think(f"⚠️ OBSERVATION: AI processing failed, using fallback")
            response_text = self.fallback_computer.compute_answer(user_input, expenses, total, all_months)
            _think(f"✅ ANSWER: {response_text}")
            result = {
                'intent': 'query',
                'response': response_text,
                'expenses_to_add': [],
                'confirmation_needed': False
            }
            if self.enable_sketching:
                self._sketch_query_result(user_input, response_text, "fallback", {"error": str(e)})
            return result
    
    def _is_general_question(self, user_input: str) -> bool:
        """Check if query is a general question (not expense-related)."""
        user_lower = user_input.lower()
        
        # Explicitly exclude expense-related queries
        expense_keywords = ['expense', 'largest', 'total', 'spending', 'spent', 'spend', 
                           'category', 'groceries', 'rent', 'budget', 'cost', 'price', 'amount']
        if any(kw in user_lower for kw in expense_keywords):
            return False
        
        general_keywords = ['hello', 'hi', 'hey', 'help', 'what can you do', 'how does this work']
        return any(kw in user_lower for kw in general_keywords)
    
    def _is_capability_question(self, user_input: str) -> bool:
        """Check if query is asking about capabilities."""
        user_lower = user_input.lower()
        capability_keywords = ['what can you', 'what do you', 'capabilities', 'features', 
                              'help', 'how to', 'how do i', 'what are you']
        return any(kw in user_lower for kw in capability_keywords)
    
    def _is_multi_month_query(self, user_input: str) -> bool:
        """Check if query requires multiple months of data."""
        user_lower = user_input.lower()
        multi_month_keywords = [
            'compare', 'comparison', 'vs', 'versus', 'last month', 'previous month',
            'this month', 'trend', 'over time', 'past', 'months', 'history',
            'average per month', 'monthly average', 'year', 'annual'
        ]
        return any(keyword in user_lower for keyword in multi_month_keywords)
    
    def _handle_general_question(
        self, 
        user_input: str, 
        thinking_callback: Optional[Callable[[str], None]] = None
    ) -> Dict:
        """Handle general questions (greetings, etc.)."""
        def _think(msg):
            if thinking_callback:
                thinking_callback(msg)
        
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ['hello', 'hi', 'hey']):
            return {
                'intent': 'query',
                'response': "Hello! How can I assist you with your expenses today?",
                'expenses_to_add': [],
                'confirmation_needed': False
            }
        
        # Default general response
        return {
            'intent': 'query',
            'response': "I'm your AI expense assistant. I can help you add expenses, query your spending, and analyze your financial data. What would you like to know?",
            'expenses_to_add': [],
            'confirmation_needed': False
        }
    
    def _sketch_input_context(
        self, 
        user_input: str, 
        context: str, 
        expenses: List[Dict], 
        total: float,
        all_months: Optional[Dict]
    ) -> None:
        """Sketch input context before AI processing."""
        sketch_data = {
            "query": user_input,
            "context_preview": context[:500] + "..." if len(context) > 500 else context,
            "context_length": len(context),
            "expense_count": len(expenses),
            "total": total,
            "has_multiple_months": all_months is not None,
            "month_count": len(all_months) if all_months else 1
        }
        TempFileManager.write_temp_file("input_context", sketch_data, format="json")
    
    def _sketch_raw_response(
        self, 
        user_input: str, 
        response_content: str, 
        messages: List[Dict]
    ) -> None:
        """Sketch raw AI response."""
        sketch_data = {
            "query": user_input,
            "raw_response": response_content,
            "response_length": len(response_content),
            "system_prompt": messages[0]['content'] if messages else None,
            "user_prompt_preview": messages[1]['content'][:200] + "..." if len(messages) > 1 and len(messages[1]['content']) > 200 else (messages[1]['content'] if len(messages) > 1 else None)
        }
        TempFileManager.write_temp_file("raw_ai_response", sketch_data, format="json")
    
    def _sketch_tool_execution(
        self, 
        tool_name: str, 
        tool_args: Dict, 
        tool_result: str
    ) -> None:
        """Sketch tool execution details."""
        sketch_data = {
            "tool_name": tool_name,
            "tool_args": tool_args,
            "tool_result": tool_result,
            "result_length": len(tool_result)
        }
        TempFileManager.write_temp_file("tool_execution", sketch_data, format="json")
    
    def _sketch_query_result(
        self, 
        user_input: str, 
        response: str, 
        processing_type: str,
        metadata: Dict
    ) -> None:
        """Sketch final query result with full processing metadata."""
        sketch_data = {
            "query": user_input,
            "response": response,
            "processing_type": processing_type,  # "simple_handler", "tool_call", "direct_response", "fallback", etc.
            "metadata": metadata,
            "thinking_steps": self.thinking_steps.copy(),  # Include all thinking steps
            "thinking_step_count": len(self.thinking_steps)
        }
        TempFileManager.write_ai_sketch(user_input, response, sketch_data)
    
    def _validate_answer_relevance(self, user_input: str, ai_response: str) -> bool:
        """
        Validate if AI response actually answers the user's question.
        
        Args:
            user_input: User's original question
            ai_response: AI's response
            
        Returns:
            True if answer seems relevant, False otherwise
        """
        user_lower = user_input.lower()
        response_lower = ai_response.lower()
        
        # Check for percentage queries
        if 'percentage' in user_lower or 'percent' in user_lower or '%' in user_lower:
            # Response should contain percentage or percent
            if '%' not in ai_response and 'percent' not in response_lower:
                return False
            # Should not be answering with "largest expense" for percentage questions
            if 'largest' in response_lower or 'biggest' in response_lower:
                return False
        
        # Check for ratio queries
        if 'ratio' in user_lower or 'proportion' in user_lower:
            # Response should contain ratio indicator
            if ':' not in ai_response and 'to' not in response_lower and 'ratio' not in response_lower:
                return False
        
        # Check for budget queries
        if 'budget' in user_lower:
            # Should mention budget or percentage
            if 'budget' not in response_lower and '%' not in ai_response:
                return False
        
        # Check if response seems to answer a different question
        # If user asks about percentage but gets "largest expense", it's wrong
        if 'percentage' in user_lower or 'percent' in user_lower:
            if 'largest' in response_lower or 'biggest' in response_lower or 'most expensive' in response_lower:
                return False
        
        # If response is too generic or doesn't contain numbers for numeric queries
        if any(word in user_lower for word in ['how much', 'what', 'how many', 'total', 'amount']):
            # Should contain at least one number or dollar amount
            if '$' not in ai_response and not any(char.isdigit() for char in ai_response):
                return False
        
        return True
    
    def _get_context_summary(self, context: str, expenses: List[Dict], total: float) -> str:
        """Get a human-readable summary of the context being sent to AI."""
        expense_count = len(expenses)
        context_preview = context[:200] + "..." if len(context) > 200 else context
        
        # Try to extract key info from context
        summary_parts = []
        summary_parts.append(f"{expense_count} expense(s)")
        summary_parts.append(f"Total: ${total:.2f}")
        
        # Extract category info if available
        if expenses:
            categories = {}
            for exp in expenses:
                desc = exp.get('description', '').lower()
                amount = exp.get('amount', 0)
                # Simple category detection
                if 'rent' in desc:
                    categories['rent'] = categories.get('rent', 0) + amount
                elif 'grocer' in desc:
                    categories['groceries'] = categories.get('groceries', 0) + amount
            
            if categories:
                cat_summary = ", ".join([f"{k}: ${v:.2f}" for k, v in categories.items()])
                summary_parts.append(f"Categories: {cat_summary}")
        
        return " | ".join(summary_parts)
    
    def _extract_reasoning_from_context(self, context: str, user_input: str, expenses: List[Dict], total: float) -> str:
        """Extract reasoning/calculation steps from context for display."""
        user_lower = user_input.lower()
        
        # For percentage queries, show the calculation
        if 'percentage' in user_lower or 'percent' in user_lower or '%' in user_lower:
            # Find the category mentioned
            category = None
            if 'rent' in user_lower:
                category = 'rent'
            elif 'grocer' in user_lower:
                category = 'groceries'
            elif 'utilit' in user_lower:
                category = 'utilities'
            
            if category:
                # Calculate category total
                category_total = sum(exp.get('amount', 0) for exp in expenses 
                                   if category in exp.get('description', '').lower())
                if category_total > 0 and total > 0:
                    percentage = (category_total / total) * 100
                    return f"{category.capitalize()} total: ${category_total:.2f} / Total: ${total:.2f} = {percentage:.1f}%"
        
        # For ratio queries
        elif 'ratio' in user_lower or 'proportion' in user_lower:
            if 'largest' in user_lower and 'smallest' in user_lower:
                amounts = [exp.get('amount', 0) for exp in expenses if exp.get('amount', 0) > 0]
                if len(amounts) >= 2:
                    largest = max(amounts)
                    smallest = min(amounts)
                    ratio = largest / smallest if smallest > 0 else 0
                    return f"Largest: ${largest:.2f} / Smallest: ${smallest:.2f} = {ratio:.2f}:1"
        
        return None
    
    def _calculate_expected_value(self, user_input: str, expenses: List[Dict], total: float) -> Optional[str]:
        """
        Calculate the expected value for percentage/ratio queries.
        
        Returns:
            String representation of expected answer, or None if can't calculate
        """
        user_lower = user_input.lower()
        
        # For percentage queries
        if 'percentage' in user_lower or 'percent' in user_lower or '%' in user_lower:
            # Find the category mentioned
            category = None
            category_keywords = {
                'rent': ['rent'],
                'groceries': ['grocer', 'grocery'],
                'utilities': ['utilit', 'utility'],
                'entertainment': ['entertain', 'entertainment'],
                'dining': ['dining', 'dine', 'restaurant'],
                'gas': ['gas', 'fuel'],
                'shopping': ['shopping', 'shop']
            }
            
            for cat, keywords in category_keywords.items():
                if any(kw in user_lower for kw in keywords):
                    category = cat
                    break
            
            if category:
                # Calculate category total
                category_total = sum(exp.get('amount', 0) for exp in expenses 
                                   if any(kw in exp.get('description', '').lower() for kw in category_keywords.get(category, [category])))
                if category_total > 0 and total > 0:
                    percentage = (category_total / total) * 100
                    return f"{category.capitalize()}: {percentage:.1f}%"
        
        # For ratio queries
        elif 'ratio' in user_lower or 'proportion' in user_lower:
            if 'largest' in user_lower and 'smallest' in user_lower:
                amounts = [exp.get('amount', 0) for exp in expenses if exp.get('amount', 0) > 0]
                if len(amounts) >= 2:
                    largest = max(amounts)
                    smallest = min(amounts)
                    ratio = largest / smallest if smallest > 0 else 0
                    return f"Ratio: {ratio:.2f}:1"
            elif 'grocer' in user_lower and 'rent' in user_lower:
                # Specific category ratio
                groceries_total = sum(exp.get('amount', 0) for exp in expenses if 'grocer' in exp.get('description', '').lower())
                rent_total = sum(exp.get('amount', 0) for exp in expenses if 'rent' in exp.get('description', '').lower())
                if groceries_total > 0 and rent_total > 0:
                    ratio = rent_total / groceries_total
                    return f"Rent to Groceries: {ratio:.2f}:1"
        
        return None
    
    def _validate_answer_accuracy(self, user_input: str, ai_response: str, calculated_value: str, tolerance: float = 0.05) -> bool:
        """
        Validate if AI's numerical answer matches calculated value.
        
        Args:
            user_input: User's question
            ai_response: AI's response
            calculated_value: Expected calculated value (e.g., "Rent: 57.1%")
            tolerance: Allowed difference (5% = 0.05)
            
        Returns:
            True if answer is accurate, False otherwise
        """
        if not calculated_value:
            return True  # Can't validate if no calculated value
        
        # Extract percentage from calculated value
        import re
        calc_match = re.search(r'(\d+\.?\d*)%', calculated_value)
        if not calc_match:
            # Try ratio
            calc_match = re.search(r'(\d+\.?\d*):1', calculated_value)
            if not calc_match:
                return True  # Can't extract, assume valid
        
        calc_num = float(calc_match.group(1))
        
        # Extract percentage/ratio from AI response
        ai_match = re.search(r'(\d+\.?\d*)%', ai_response)
        if not ai_match:
            # Try ratio
            ai_match = re.search(r'(\d+\.?\d*):1', ai_response)
            if not ai_match:
                return False  # AI didn't provide a number
        
        ai_num = float(ai_match.group(1))
        
        # Check if difference is within tolerance
        difference = abs(calc_num - ai_num) / calc_num if calc_num > 0 else abs(calc_num - ai_num)
        
        is_accurate = difference <= tolerance
        
        if not is_accurate:
            log_warning(f"[AI Processing] Accuracy mismatch: AI={ai_num}, Calculated={calc_num}, Difference={difference:.1%}")
        
        return is_accurate

