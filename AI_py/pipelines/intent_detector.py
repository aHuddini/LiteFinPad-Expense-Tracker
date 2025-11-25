"""
Intent Detection Pipeline

Detects user intent (add/edit/delete/query) from natural language input.
Uses financial dictionary for better understanding.
"""

from typing import Dict, List
from llama_cpp import Llama

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from error_logger import log_info, log_warning, log_debug
from AI_py.config.financial_dictionary import FinancialDictionary
from AI_py.llm.inference import InferenceEngine


class IntentDetector:
    """Detects user intent from natural language input."""
    
    def __init__(self, inference_engine: InferenceEngine):
        """
        Initialize intent detector.
        
        Args:
            inference_engine: Inference engine for AI-based detection
        """
        self.inference_engine = inference_engine
        self.dictionary = FinancialDictionary()
    
    def detect(self, user_input: str) -> str:
        """
        Detect user intent from input.
        
        Args:
            user_input: User's natural language input
            
        Returns:
            'add', 'delete', 'edit', 'query', or 'unknown'
        """
        user_lower = user_input.lower()
        
        # Keyword-based detection (fast path)
        intent = self._detect_by_keywords(user_lower)
        if intent != 'unknown':
            log_debug(f"[IntentDetector] Detected intent '{intent}' via keywords")
            return intent
        
        # AI-based detection (fallback for ambiguous cases)
        log_debug(f"[IntentDetector] Using AI for intent detection")
        return self._detect_with_ai(user_input)
    
    def _detect_by_keywords(self, user_lower: str) -> str:
        """Fast keyword-based intent detection."""
        # IMPORTANT: Check for dollar amounts FIRST - if present, likely an add
        # Pattern: "$X" or "$ X" or "X dollars" at start of message
        import re
        dollar_pattern = r'^\$?\s*\d+'
        if re.search(dollar_pattern, user_lower):
            # If it starts with a dollar amount, it's likely an add (unless it's a question)
            if '?' not in user_lower and not any(q in user_lower for q in ['what', 'how', 'when', 'where', 'why', 'which', 'who', 'show', 'tell', 'list', 'compare']):
                return 'add'
        
        # IMPORTANT: Check query patterns FIRST before add patterns
        # "Spending on X?" pattern is a query (asking about spending)
        if 'spending on' in user_lower or 'spending for' in user_lower:
            return 'query'
        
        # Query keywords (questions) - check before add keywords
        question_words = ['what', 'how', 'when', 'where', 'why', 'which', 'who', 'show', 'tell', 'list', 
                         'compare', 'spent', 'total', 'largest', 'smallest', 'lowest', 'highest']
        
        if any(word in user_lower for word in question_words):
            return 'query'
        
        # Check for question mark
        if '?' in user_lower:
            return 'query'
        
        # Add expense keywords (but NOT "spend" - that's ambiguous)
        add_keywords = ['add', 'record', 'enter', 'insert', 'create', 'new expense', 'log', 'save']
        if any(keyword in user_lower for keyword in add_keywords):
            return 'add'
        
        # Delete expense keywords
        delete_keywords = ['delete', 'remove', 'drop', 'cancel', 'erase', 'clear']
        if any(keyword in user_lower for keyword in delete_keywords):
            return 'delete'
        
        # Edit expense keywords
        edit_keywords = ['edit', 'update', 'modify', 'change', 'alter', 'correct']
        if any(keyword in user_lower for keyword in edit_keywords):
            return 'edit'
        
        return 'unknown'
    
    def _detect_with_ai(self, user_input: str) -> str:
        """Use AI to detect intent for ambiguous cases."""
        try:
            prompt = f"""Classify the user's intent. Respond with ONLY one word: add, delete, edit, or query.

Examples:
- "Add $50 for groceries" → add
- "Delete the coffee expense" → delete
- "Edit the rent amount to $1000" → edit
- "What's my total?" → query
- "How much did I spend?" → query

User input: "{user_input}"

Intent:"""
            
            messages = [
                {'role': 'system', 'content': 'You are an intent classifier. Respond with only one word: add, delete, edit, or query.'},
                {'role': 'user', 'content': prompt}
            ]
            
            response = self.inference_engine.chat_completion(
                messages=messages,
                max_tokens=10,
                temperature=0.0,
                top_p=0.1
            )
            
            content = self.inference_engine.extract_response_text(response)
            if content:
                intent = content.strip().lower()
                if intent in ['add', 'delete', 'edit', 'query']:
                    return intent
            
            return 'query'  # Default to query if unclear
        except Exception as e:
            log_warning(f"[IntentDetector] AI detection failed: {e}, defaulting to query")
            return 'query'

