# tests/test_simple_query_handler.py
"""Unit tests for SimpleQueryHandler."""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AI_py.handlers.simple_query_handler import SimpleQueryHandler


class TestSimpleQueryHandler(unittest.TestCase):
    """Test SimpleQueryHandler logic."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.handler = SimpleQueryHandler()
        
        # Sample expense data
        self.expenses = [
            {'date': '2025-11-01', 'amount': 100.0, 'description': 'Groceries'},
            {'date': '2025-11-02', 'amount': 50.0, 'description': 'Gas'},
            {'date': '2025-11-03', 'amount': 1200.0, 'description': 'Rent'},
            {'date': '2025-11-04', 'amount': 75.0, 'description': 'Groceries'},
            {'date': '2025-11-05', 'amount': 25.0, 'description': 'Coffee'},
        ]
        self.total = sum(exp['amount'] for exp in self.expenses)
    
    def test_can_handle_simple_queries(self):
        """Test that handler recognizes simple queries."""
        simple_queries = [
            "what's my largest expense?",
            "what's my lowest expense?",
            "what's my total?",
            "what categories did I spend the most on?",
            "what did I spend on groceries?",
            "how much did I spend on rent?"
        ]
        
        for query in simple_queries:
            with self.subTest(query=query):
                self.assertTrue(self.handler.can_handle(query), f"Should handle: {query}")
    
    def test_cannot_handle_multi_month_queries(self):
        """Test that handler rejects multi-month queries."""
        multi_month_queries = [
            "compare my spending this month vs last month",
            "what's my spending trend over time",
            "show me my annual total",
            "compare this year to last year"
        ]
        
        for query in multi_month_queries:
            with self.subTest(query=query):
                self.assertFalse(self.handler.can_handle(query), f"Should NOT handle: {query}")
    
    def test_largest_expense(self):
        """Test largest expense calculation."""
        result = self.handler.handle("what's my largest expense?", self.expenses, self.total)
        self.assertIn("$1200.00", result)
        self.assertIn("Rent", result)
    
    def test_lowest_expense(self):
        """Test lowest expense calculation."""
        result = self.handler.handle("what's my lowest expense?", self.expenses, self.total)
        self.assertIn("$25.00", result)
        self.assertIn("Coffee", result)
    
    def test_total(self):
        """Test total calculation."""
        result = self.handler.handle("what's my total?", self.expenses, self.total)
        self.assertIn(f"${self.total:.2f}", result)
    
    def test_filtered_query_exact_match(self):
        """Test filtered query with exact match."""
        result = self.handler.handle("what did I spend on rent?", self.expenses, self.total)
        self.assertIn("$1200.00", result)
        self.assertIn("rent", result.lower())
        self.assertIn("1 expense", result)
    
    def test_filtered_query_multiple_matches(self):
        """Test filtered query with multiple matches."""
        result = self.handler.handle("what did I spend on groceries?", self.expenses, self.total)
        self.assertIn("$175.00", result)  # 100 + 75
        self.assertIn("groceries", result.lower())
        self.assertIn("2 expense", result)
    
    def test_filtered_query_no_match(self):
        """Test filtered query with no match."""
        result = self.handler.handle("what did I spend on utilities?", self.expenses, self.total)
        self.assertIn("haven't spent anything on utilities", result.lower())
    
    def test_filtered_query_case_insensitive(self):
        """Test filtered query is case-insensitive."""
        result = self.handler.handle("what did I spend on GROCERIES?", self.expenses, self.total)
        self.assertIn("$175.00", result)
    
    def test_filtered_query_with_punctuation(self):
        """Test filtered query strips punctuation."""
        result = self.handler.handle("spending on groceries?", self.expenses, self.total)
        self.assertIn("$175.00", result)
    
    def test_category_query(self):
        """Test category analysis."""
        result = self.handler.handle("what categories did I spend the most on?", self.expenses, self.total)
        self.assertIn("Rent", result)
        self.assertIn("$1200.00", result)
        self.assertIn("Groceries", result)
        self.assertIn("$175.00", result)
    
    def test_empty_expenses(self):
        """Test handling of empty expense list."""
        result = self.handler.handle("what's my total?", [], 0.0)
        self.assertIn("$0.00", result)


if __name__ == '__main__':
    unittest.main()

