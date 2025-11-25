# tests/test_multi_month_detection.py
"""Unit tests for multi-month query detection."""

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


class TestMultiMonthDetection(unittest.TestCase):
    """Test multi-month query detection logic."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tracker = MockExpenseTracker()
        self.engine = QueryEngine(self.tracker)
    
    def test_multi_month_keywords(self):
        """Test multi-month query detection."""
        multi_month_queries = [
            "compare my spending this month vs last month",
            "how much more did I spend this month?",
            "what's my spending trend over time",
            "show me my annual total",
            "what's my monthly average?",
            "compare this year to last year",
            "spending trend over months",
            "last month vs this month",
            "what are my spending trends?",
            "show history of expenses"
        ]
        
        # Access query pipeline's method
        query_pipeline = self.engine.query_pipeline
        for query in multi_month_queries:
            with self.subTest(query=query):
                is_multi_month = query_pipeline._is_multi_month_query(query)
                self.assertTrue(is_multi_month, f"Should detect as multi-month: {query}")
    
    def test_single_month_queries(self):
        """Test single-month queries are NOT detected as multi-month."""
        single_month_queries = [
            "what's my largest expense?",
            "what did I spend on groceries?",
            "what's my total?",
            "spending on rent?",
            "show me my expenses"
        ]
        
        # Access query pipeline's method
        query_pipeline = self.engine.query_pipeline
        for query in single_month_queries:
            with self.subTest(query=query):
                is_multi_month = query_pipeline._is_multi_month_query(query)
                self.assertFalse(is_multi_month, f"Should NOT detect as multi-month: {query}")


if __name__ == '__main__':
    unittest.main()

