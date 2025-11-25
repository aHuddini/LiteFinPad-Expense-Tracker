# tests/test_intent_detection.py
"""Unit tests for AI intent detection."""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AI_py.query_engine import QueryEngine


class MockExpenseTracker:
    """Mock expense tracker for testing."""
    def __init__(self):
        self.viewed_month = "2025-11"
        self.expenses = []
        self.monthly_total = 0.0


class TestIntentDetection(unittest.TestCase):
    """Test intent detection logic."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tracker = MockExpenseTracker()
        self.engine = QueryEngine(self.tracker)
    
    def _get_intent_detector(self):
        """Get intent detector from engine."""
        return self.engine._get_intent_detector()
    
    def test_add_intent_keywords(self):
        """Test ADD intent with strong keywords."""
        add_queries = [
            "add $50 for groceries",
            "create expense $100 rent",
            "new expense $25 coffee",
            "enter $200 utilities",
            "record $75 gas",
            "log $30 lunch",
            "save $50 dinner"
        ]
        
        detector = self._get_intent_detector()
        for query in add_queries:
            with self.subTest(query=query):
                intent = detector.detect(query)
                self.assertEqual(intent, 'add', f"Failed for: {query}")
    
    def test_delete_intent_keywords(self):
        """Test DELETE intent with strong keywords."""
        delete_queries = [
            "delete the groceries expense",
            "remove the rent payment",
            "erase coffee expense",
            "clear the gas entry"
        ]
        
        detector = self._get_intent_detector()
        for query in delete_queries:
            with self.subTest(query=query):
                intent = detector.detect(query)
                self.assertEqual(intent, 'delete', f"Failed for: {query}")
    
    def test_query_intent_question_words(self):
        """Test QUERY intent with question words."""
        query_queries = [
            "what's my largest expense?",
            "how much did I spend?",
            "when did I spend on groceries?",
            "where are my expenses?",
            "why is my total so high?",
            "which expense is largest?",
            "who spent this much?",
            "show me my expenses",
            "tell me my total",
            "list my expenses"
        ]
        
        detector = self._get_intent_detector()
        for query in query_queries:
            with self.subTest(query=query):
                intent = detector.detect(query)
                self.assertEqual(intent, 'query', f"Failed for: {query}")
    
    def test_query_intent_spending_words(self):
        """Test QUERY intent with spending-related words."""
        spending_queries = [
            "spending on groceries?",
            "spent on rent?",
            "spend on utilities?",
            "compare my spending",
            "total expenses",
            "largest expense",
            "smallest purchase",
            "lowest cost",
            "highest amount"
        ]
        
        detector = self._get_intent_detector()
        for query in spending_queries:
            with self.subTest(query=query):
                intent = detector.detect(query)
                self.assertEqual(intent, 'query', f"Failed for: {query}")
    
    def test_query_intent_question_mark(self):
        """Test QUERY intent with question mark."""
        question_mark_queries = [
            "spending on gas?",
            "my total?",
            "largest expense?",
            "groceries?"
        ]
        
        detector = self._get_intent_detector()
        for query in question_mark_queries:
            with self.subTest(query=query):
                intent = detector.detect(query)
                self.assertEqual(intent, 'query', f"Failed for: {query}")
    
    def test_ambiguous_cases(self):
        """Test ambiguous cases that should default to query."""
        ambiguous_queries = [
            "hello",
            "hi there",
            "thanks",
            "ok"
        ]
        
        detector = self._get_intent_detector()
        for query in ambiguous_queries:
            with self.subTest(query=query):
                intent = detector.detect(query)
                # Should be 'query' (safe default)
                self.assertIn(intent, ['query'], f"Failed for: {query}")


if __name__ == '__main__':
    unittest.main()

