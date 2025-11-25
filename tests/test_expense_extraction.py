# tests/test_expense_extraction.py
"""Unit tests for expense extraction and validation."""

import unittest
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AI_py.query_engine import QueryEngine
from validation import InputValidation
from date_utils import DateUtils


class MockExpenseTracker:
    """Mock expense tracker for testing."""
    def __init__(self):
        self.viewed_month = "2025-11"
        self.expenses = []
        self.monthly_total = 0.0


class TestExpenseExtraction(unittest.TestCase):
    """Test expense extraction and validation logic."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tracker = MockExpenseTracker()
        self.engine = QueryEngine(self.tracker)
    
    def test_validate_amount_valid(self):
        """Test amount validation with valid amounts."""
        valid_amounts = ["50", "50.00", "100.50", "1000", "0.01"]
        
        for amount in valid_amounts:
            with self.subTest(amount=amount):
                result = InputValidation.validate_final_amount(amount)
                self.assertTrue(result.is_valid, f"Should be valid: {amount}")
    
    def test_validate_amount_invalid(self):
        """Test amount validation with invalid amounts."""
        invalid_amounts = ["", "abc", "-50", "0", "0.00"]
        
        for amount in invalid_amounts:
            with self.subTest(amount=amount):
                result = InputValidation.validate_final_amount(amount)
                self.assertFalse(result.is_valid, f"Should be invalid: {amount}")
    
    def test_validate_description_valid(self):
        """Test description validation with valid descriptions."""
        valid_descriptions = ["Groceries", "Rent Payment", "Gas Station", "Coffee"]
        
        for desc in valid_descriptions:
            with self.subTest(desc=desc):
                result = InputValidation.validate_description(desc)
                self.assertTrue(result.is_valid, f"Should be valid: {desc}")
    
    def test_validate_description_invalid(self):
        """Test description validation with invalid descriptions."""
        invalid_descriptions = ["", "   ", "a" * 101]  # Empty, whitespace, too long
        
        for desc in invalid_descriptions:
            with self.subTest(desc=desc):
                result = InputValidation.validate_description(desc)
                self.assertFalse(result.is_valid, f"Should be invalid: {desc}")
    
    def test_parse_relative_date_today(self):
        """Test relative date parsing for 'today'."""
        # Access expense operations method
        operations = self.engine._get_expense_operations()
        result = operations._parse_relative_date("today", "2025-11")
        expected = datetime.now().date()
        # Result is datetime object, compare dates
        self.assertEqual(result.date() if hasattr(result, 'date') else result, expected)
    
    def test_parse_relative_date_yesterday(self):
        """Test relative date parsing for 'yesterday'."""
        # Access expense operations method
        operations = self.engine._get_expense_operations()
        result = operations._parse_relative_date("yesterday", "2025-11")
        from datetime import timedelta
        expected = (datetime.now() - timedelta(days=1)).date()
        # Result is datetime object, compare dates
        self.assertEqual(result.date() if hasattr(result, 'date') else result, expected)
    
    def test_parse_relative_date_specific(self):
        """Test relative date parsing for specific dates."""
        # Access expense operations method
        operations = self.engine._get_expense_operations()
        # For specific dates, should return parsed datetime object (not None)
        result = operations._parse_relative_date("november 15th", "2025-11")
        # Should return a datetime object for valid date
        self.assertIsNotNone(result)
    
    def test_date_utils_parse_valid(self):
        """Test DateUtils parsing with valid dates."""
        valid_dates = [
            ("2025-11-15", True),
            ("2025-01-01", True),
            ("2025-12-31", True)
        ]
        
        for date_str, should_be_valid in valid_dates:
            with self.subTest(date=date_str):
                result = DateUtils.parse_date(date_str)
                if should_be_valid:
                    self.assertIsNotNone(result, f"Should parse: {date_str}")
                else:
                    self.assertIsNone(result, f"Should NOT parse: {date_str}")
    
    def test_date_utils_parse_invalid(self):
        """Test DateUtils parsing with invalid dates."""
        invalid_dates = ["", "invalid", "2025-13-01", "2025-11-32", "11/15/2025"]
        
        for date_str in invalid_dates:
            with self.subTest(date=date_str):
                result = DateUtils.parse_date(date_str)
                self.assertIsNone(result, f"Should NOT parse: {date_str}")


if __name__ == '__main__':
    unittest.main()

