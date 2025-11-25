# tests/test_ai_responses.py
"""Integration tests for AI model responses - tests actual AI inference."""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AI_py.query_engine import QueryEngine


class MockExpenseTracker:
    """Mock expense tracker with test data.
    
    Note: QueryEngine loads REAL data from data_YYYY-MM folder,
    so test expectations should match actual data, not this mock.
    This mock is just for QueryEngine initialization."""
    def __init__(self):
        self.viewed_month = "2025-11"
        self.expenses = []  # Real data will be loaded by QueryEngine
        self.monthly_total = 0.0  # Real total will be calculated by QueryEngine


class TestAIResponses(unittest.TestCase):
    """Test actual AI model responses."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures once for all tests."""
        cls.tracker = MockExpenseTracker()
        cls.engine = QueryEngine(cls.tracker)
        print("\n" + "="*70)
        print("AI RESPONSE INTEGRATION TESTS")
        print("="*70)
        # Access LLM manager for model name
        model_name = cls.engine.llm_manager.get_preferred_model()
        print(f"Testing with model: {model_name}")
        print("Note: Tests use data from test_data folder")
        print("="*70 + "\n")
    
    # ==========================================
    # GREETING TESTS - Should NOT return expense data
    # ==========================================
    
    def test_greeting_hello(self):
        """Test that 'hello' does NOT return expense data."""
        print("\n[TEST] Greeting: 'hello'")
        result = self.engine.process("hello")
        response = result['response'].lower()
        
        # Should NOT contain specific expense amounts
        self.assertNotIn("$1200", response, "Should NOT return largest expense for greeting")
        self.assertNotIn("$700", response, "Should NOT return expense data for greeting")
        
        # Should be a general response or greeting
        print(f"[OK] Response: {result['response'][:100]}...")
    
    def test_greeting_hi(self):
        """Test that 'hi' does NOT return expense data."""
        print("\n[TEST] Greeting: 'hi'")
        result = self.engine.process("hi")
        response = result['response'].lower()
        
        self.assertNotIn("$1200", response, "Should NOT return expense data for 'hi'")
        print(f"[OK] Response: {result['response'][:100]}...")
    
    # ==========================================
    # SIMPLE QUERY TESTS - Should use Python handler
    # ==========================================
    
    def test_largest_expense_query(self):
        """Test 'What's my largest expense?' returns correct answer."""
        print("\n[TEST] Query: 'What's my largest expense?'")
        result = self.engine.process("What's my largest expense?")
        response = result['response']
        
        # Should contain largest expense (checking that it returns SOME expense data)
        # Using data from test_data folder
        self.assertIn("$", response, "Should return an amount")
        self.assertIn("largest expense", response.lower(), "Should mention 'largest expense'")
        
        # Should use Python handler (instant)
        self.assertEqual(result['intent'], 'query')
        print(f"[OK] Response: {response}")
    
    def test_lowest_expense_query(self):
        """Test 'What's my lowest expense?' returns correct answer."""
        print("\n[TEST] Query: 'What's my lowest expense?'")
        result = self.engine.process("What's my lowest expense?")
        response = result['response']
        
        # Should contain lowest expense (checking format, not specific values)
        self.assertIn("$", response, "Should return an amount")
        self.assertIn("lowest expense", response.lower(), "Should mention 'lowest expense'")
        
        print(f"[OK] Response: {response}")
    
    def test_total_query(self):
        """Test 'What's my total?' returns correct answer."""
        print("\n[TEST] Query: 'What's my total?'")
        result = self.engine.process("What's my total?")
        response = result['response']
        
        # Should contain total (checking format)
        self.assertIn("$", response, "Should return an amount")
        self.assertIn("total", response.lower(), "Should mention 'total'")
        
        print(f"[OK] Response: {response}")
    
    def test_filtered_query_groceries(self):
        """Test 'What did I spend on groceries?' returns correct answer."""
        print("\n[TEST] Query: 'What did I spend on groceries?'")
        result = self.engine.process("What did I spend on groceries?")
        response = result['response']
        
        # Should contain groceries spending (checking format)
        self.assertIn("$", response, "Should return an amount")
        self.assertIn("groceries", response.lower(), "Should mention groceries")
        
        print(f"[OK] Response: {response}")
    
    def test_filtered_query_rent(self):
        """Test 'What did I spend on rent?' returns correct answer."""
        print("\n[TEST] Query: 'What did I spend on rent?'")
        result = self.engine.process("What did I spend on rent?")
        response = result['response']
        
        # Should contain rent spending (checking format)
        self.assertIn("$", response, "Should return an amount")
        self.assertIn("rent", response.lower(), "Should mention rent")
        
        print(f"[OK] Response: {response}")
    
    # ==========================================
    # MULTI-MONTH QUERY TESTS - AI Processing
    # ==========================================
    
    def test_multi_month_comparison(self):
        """Test 'Compare my spending this month vs last month' does NOT return wrong data."""
        print("\n[TEST] Query: 'Compare my spending this month vs last month'")
        result = self.engine.process("Compare my spending this month vs last month")
        response = result['response'].lower()
        
        # Should NOT just return largest expense
        # If it returns ONLY "$1200.00 for Rent", that's wrong
        if "$1200" in response and "rent" in response:
            # Check if there's comparison language
            comparison_words = ['vs', 'versus', 'comparison', 'compare', 'last month', 'this month', 'increase', 'decrease', 'more', 'less']
            has_comparison = any(word in response for word in comparison_words)
            
            if not has_comparison:
                self.fail(f"Multi-month query returned single expense instead of comparison: {response[:200]}")
        
        print(f"[OK] Response: {result['response'][:200]}...")
    
    def test_monthly_average_query(self):
        """Test 'What's my monthly average?' does NOT return largest expense."""
        print("\n[TEST] Query: 'What's my monthly average?'")
        result = self.engine.process("What's my monthly average?")
        response = result['response'].lower()
        
        # Should NOT just return largest expense
        if "$1200" in response and "rent" in response:
            # Check if there's average/monthly language
            average_words = ['average', 'monthly', 'per month', 'month']
            has_average = any(word in response for word in average_words)
            
            # If it just says "$1200 Rent" without average context, that's wrong
            if not has_average:
                self.fail(f"Monthly average query returned single expense: {response[:200]}")
        
        print(f"[OK] Response: {result['response'][:200]}...")
    
    def test_spending_more_query(self):
        """Test 'How much more did I spend this month?' does NOT return largest expense."""
        print("\n[TEST] Query: 'How much more did I spend this month?'")
        result = self.engine.process("How much more did I spend this month?")
        response = result['response'].lower()
        
        # Should NOT just return largest expense
        if "$1200" in response and "rent" in response and "november 03" in response:
            # This is the wrong response (largest expense)
            self.fail(f"'How much more' query incorrectly returned largest expense: {response[:200]}")
        
        print(f"[OK] Response: {result['response'][:200]}...")
    
    # ==========================================
    # EDGE CASES
    # ==========================================
    
    def test_spending_on_gas_not_add(self):
        """Test 'Spending on gas?' is QUERY not ADD."""
        print("\n[TEST] Query: 'Spending on gas?'")
        result = self.engine.process("Spending on gas?")
        
        # Should be query, not add
        self.assertEqual(result['intent'], 'query', "Should detect as QUERY not ADD")
        self.assertEqual(len(result.get('expenses_to_add', [])), 0, "Should NOT add expense")
        
        # Should return gas spending (checking format)
        response = result['response']
        self.assertIn("$", response, "Should return an amount")
        self.assertIn("gas", response.lower(), "Should mention gas")
        
        print(f"[OK] Intent: {result['intent']}, Response: {response}")
    
    def test_categories_query(self):
        """Test 'What categories did I spend the most on?' returns category breakdown."""
        print("\n[TEST] Query: 'What categories did I spend the most on?'")
        result = self.engine.process("What categories did I spend the most on?")
        response = result['response']
        
        # Should contain categories (checking format, not specific category names)
        self.assertIn("$", response, "Should return amounts")
        self.assertTrue(
            "categories" in response.lower() or ":" in response,
            "Should mention categories or show breakdown"
        )
        
        print(f"[OK] Response: {response[:200]}...")


if __name__ == '__main__':
    # Run with verbose output
    unittest.main(verbosity=2)

