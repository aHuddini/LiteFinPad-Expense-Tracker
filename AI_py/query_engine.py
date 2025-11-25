"""
Query Engine - Main Entry Point

Simplified facade that orchestrates query processing through pipelines.
Following best practices: separation of concerns, single responsibility.
"""

from typing import Dict, Optional, Callable

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from error_logger import log_info, log_warning, log_debug

from AI_py.llm.manager import LLMManager
from AI_py.llm.inference import InferenceEngine
from AI_py.pipelines.intent_detector import IntentDetector
from AI_py.pipelines.query_pipeline import QueryPipeline
from AI_py.pipelines.expense_operations import ExpenseOperations
from AI_py.handlers.simple_query_handler import SimpleQueryHandler


class QueryEngine:
    """
    Main query engine - orchestrates all AI operations.
    
    This is a facade that delegates to specialized pipelines:
    - Intent detection
    - Query processing
    - Expense operations (add/edit/delete)
    """
    
    def __init__(self, expense_tracker):
        """
        Initialize query engine.
        
        Args:
            expense_tracker: Expense tracker instance for data access
        """
        self.expense_tracker = expense_tracker
        
        # Initialize LLM manager
        self.llm_manager = LLMManager()
        
        # Initialize inference engine (lazy-loaded)
        self.inference_engine = None
        
        # Initialize pipelines (share LLMManager instance)
        self.intent_detector = None  # Lazy-loaded (needs inference engine)
        self.query_pipeline = QueryPipeline(expense_tracker, llm_manager=self.llm_manager)
        self.expense_operations = None  # Lazy-loaded (needs inference engine)
    
    def _get_inference_engine(self) -> InferenceEngine:
        """Get or create inference engine."""
        if self.inference_engine is None:
            model = self.llm_manager.get_model()
            self.inference_engine = InferenceEngine(model)
        return self.inference_engine
    
    def _get_intent_detector(self) -> IntentDetector:
        """Get or create intent detector."""
        if self.intent_detector is None:
            inference = self._get_inference_engine()
            self.intent_detector = IntentDetector(inference)
        return self.intent_detector
    
    def _get_expense_operations(self) -> ExpenseOperations:
        """Get or create expense operations."""
        if self.expense_operations is None:
            inference = self._get_inference_engine()
            self.expense_operations = ExpenseOperations(self.expense_tracker, inference)
        return self.expense_operations
    
    def process(
        self, 
        user_input: str, 
        month_key: Optional[str] = None, 
        thinking_callback: Optional[Callable[[str], None]] = None
    ) -> Dict:
        """
        Process user input - main entry point.
        
        Args:
            user_input: Natural language input from user
            month_key: Optional month key (YYYY-MM), defaults to viewed_month
            thinking_callback: Optional callback function(message: str) to show thinking steps
            
        Returns:
            Dict with keys:
            - 'intent': 'query', 'add', 'edit', 'delete', 'error', or 'unknown'
            - 'response': AI response text
            - 'expenses_to_add': List of expense dicts (if intent is 'add')
            - 'confirmation_needed': bool
            - 'thinking_steps': List of thinking messages (if callback provided)
        """
        thinking_steps = []
        
        def _add_thinking(msg):
            """Helper to add thinking step and call callback if provided."""
            thinking_steps.append(msg)
            if thinking_callback:
                thinking_callback(msg)
        
        # Check if LLM is available
        if not self.llm_manager.is_available():
            return {
                'intent': 'error',
                'response': "AI features require llama-cpp-python and a model file. Please install: pip install llama-cpp-python",
                'expenses_to_add': [],
                'confirmation_needed': False,
                'thinking_steps': thinking_steps
            }
        
        # Get month context
        if month_key is None:
            month_key = self.expense_tracker.viewed_month
        
        # Detect intent
        _add_thinking("🤔 Detecting intent (add/edit/delete/query)...")
        intent_detector = self._get_intent_detector()
        intent = intent_detector.detect(user_input)
        _add_thinking(f"✓ Detected intent: {intent}")
        
        # Route to appropriate handler
        if intent == 'add':
            _add_thinking(f"📅 Processing expense addition for {month_key}...")
            _add_thinking("🤖 Parsing expense from your message...")
            operations = self._get_expense_operations()
            result = operations.add_expense(user_input, month_key, thinking_callback)
            result['thinking_steps'] = thinking_steps
            return result
            
        elif intent == 'delete':
            _add_thinking(f"📅 Processing expense deletion for {month_key}...")
            _add_thinking("🗑️ Finding expense to delete...")
            operations = self._get_expense_operations()
            result = operations.delete_expense(user_input, month_key, thinking_callback)
            result['thinking_steps'] = thinking_steps
            return result
            
        elif intent == 'edit':
            _add_thinking(f"📅 Processing expense edit for {month_key}...")
            _add_thinking("✏️ Expense editing is not yet implemented")
            result = {
                'intent': 'edit',
                'response': "Expense editing is not yet implemented. Please delete and re-add the expense.",
                'expenses_to_add': [],
                'confirmation_needed': False,
                'thinking_steps': thinking_steps
            }
            return result
            
        elif intent == 'query':
            _add_thinking("🔍 REACT: Analyzing query routing...")
            result = self.query_pipeline.process_query(user_input, month_key, thinking_callback)
            result['thinking_steps'] = thinking_steps
            return result
            
        else:
            return {
                'intent': 'unknown',
                'response': "I'm not sure what you're asking. Try: 'Add $50 for groceries' or 'What's my total?'",
                'expenses_to_add': [],
                'confirmation_needed': False,
                'thinking_steps': thinking_steps
            }
