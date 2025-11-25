# tests/test_app_integration.py
"""End-to-end integration tests that verify tests match actual application behavior."""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AI_py.query_engine import QueryEngine
from main import ExpenseTracker


class TestAppIntegration(unittest.TestCase):
    """Test that QueryEngine behavior matches actual app usage."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures once for all tests."""
        print("\n" + "="*70)
        print("APP INTEGRATION TESTS")
        print("="*70)
        print("Verifying that test results match actual application behavior")
        print("="*70 + "\n")
        
        # Create actual ExpenseTracker instance (like the real app)
        cls.app = ExpenseTracker()
        cls.engine = QueryEngine(cls.app)
    
    def test_greeting_through_app_engine(self):
        """Test that greeting works through the actual app's QueryEngine instance."""
        print("\n[TEST] Greeting through app's QueryEngine: 'hello'")
        
        # This is exactly how the app uses QueryEngine
        result = self.engine.process("hello")
        
        # Verify it's a general question (not expense data)
        response = result['response'].lower()
        self.assertNotIn("$", response, "Should NOT return expense data")
        # Allow "expenses" in context like "your expenses" as that's natural for a greeting
        # Just ensure it's not returning expense data
        
        # Should be a greeting
        self.assertTrue(
            any(word in response for word in ['hello', 'hi', 'assist', 'help']),
            f"Should be a greeting, got: {response[:100]}"
        )
        
        print(f"[OK] Response: {result['response'][:100]}...")
        print(f"[OK] Intent: {result['intent']}")
        print(f"[OK] Expenses to add: {len(result.get('expenses_to_add', []))}")
    
    def test_query_through_app_engine(self):
        """Test that queries work through the actual app's QueryEngine instance."""
        print("\n[TEST] Query through app's QueryEngine: 'What's my largest expense?'")
        
        # This is exactly how the app uses QueryEngine
        result = self.engine.process("What's my largest expense?")
        
        # Verify it's a query intent
        self.assertEqual(result['intent'], 'query', "Should be query intent")
        
        # Verify response contains expense data
        response = result['response']
        self.assertIn("$", response, "Should return an amount")
        self.assertIn("largest", response.lower(), "Should mention 'largest'")
        
        # Should NOT try to add expenses
        self.assertEqual(len(result.get('expenses_to_add', [])), 0, "Should NOT add expenses")
        
        print(f"[OK] Response: {response[:150]}...")
        print(f"[OK] Intent: {result['intent']}")
    
    def test_add_expense_through_app_engine(self):
        """Test that adding expenses works through the actual app's QueryEngine instance."""
        print("\n[TEST] Add expense through app's QueryEngine: 'Add $50 for test expense today'")
        
        # This is exactly how the app uses QueryEngine
        result = self.engine.process("Add $50 for test expense today")
        
        # Verify it's an add intent
        self.assertEqual(result['intent'], 'add', "Should be add intent")
        
        # Verify expenses are extracted
        expenses = result.get('expenses_to_add', [])
        self.assertGreater(len(expenses), 0, "Should extract at least one expense")
        
        # Verify expense structure matches what app expects
        if expenses:
            exp = expenses[0]
            self.assertIn('amount', exp, "Should have amount")
            self.assertIn('description', exp, "Should have description")
            self.assertIn('date', exp, "Should have date")
            self.assertEqual(exp['amount'], 50.0, "Amount should be 50.0")
            self.assertIn('test expense', exp['description'].lower(), "Should contain 'test expense'")
        
        print(f"[OK] Intent: {result['intent']}")
        print(f"[OK] Expenses extracted: {len(expenses)}")
        if expenses:
            print(f"[OK] First expense: ${expenses[0]['amount']:.2f} - {expenses[0]['description']} on {expenses[0]['date']}")
    
    def test_query_with_thinking_callback(self):
        """Test that QueryEngine works with thinking callback (like the app uses)."""
        print("\n[TEST] Query with thinking callback (simulating app's thinking_callback)")
        
        thinking_steps = []
        
        def thinking_callback(step: str):
            """Simulate the app's thinking callback."""
            thinking_steps.append(step)
            # Remove emojis for Windows console compatibility
            step_clean = step.encode('ascii', 'ignore').decode('ascii')
            print(f"  [THINKING] {step_clean}")
        
        # This is exactly how the app calls QueryEngine
        result = self.engine.process("What's my total?", thinking_callback=thinking_callback)
        
        # Verify thinking steps were captured
        self.assertGreater(len(thinking_steps), 0, "Should have thinking steps")
        
        # Verify response is correct
        response = result['response']
        self.assertIn("$", response, "Should return an amount")
        
        print(f"[OK] Thinking steps captured: {len(thinking_steps)}")
        print(f"[OK] Response: {response[:100]}...")
    
    def test_result_structure_matches_app_expectations(self):
        """Test that result structure matches what the app expects."""
        print("\n[TEST] Verifying result structure matches app expectations")
        
        # Test query result
        query_result = self.engine.process("What's my total?")
        required_keys = ['intent', 'response', 'expenses_to_add', 'confirmation_needed']
        for key in required_keys:
            self.assertIn(key, query_result, f"Result should have '{key}' key")
        
        # Test add result
        add_result = self.engine.process("Add $25 for coffee today")
        for key in required_keys:
            self.assertIn(key, add_result, f"Result should have '{key}' key")
        
        # Verify intent values match app expectations
        self.assertIn(query_result['intent'], ['query', 'add', 'delete'], "Intent should be valid")
        self.assertIn(add_result['intent'], ['query', 'add', 'delete'], "Intent should be valid")
        
        print("[OK] Result structure matches app expectations")
        print(f"[OK] Query result keys: {list(query_result.keys())}")
        print(f"[OK] Add result keys: {list(add_result.keys())}")
    
    def test_app_expense_tracker_integration(self):
        """Test that QueryEngine correctly uses the app's ExpenseTracker."""
        print("\n[TEST] Verifying QueryEngine uses app's ExpenseTracker correctly")
        
        # Verify engine has access to expense tracker
        self.assertIsNotNone(self.engine.expense_tracker, "Should have expense tracker")
        self.assertEqual(self.engine.expense_tracker, self.app, "Should use the same instance")
        
        # Verify it can access viewed month
        self.assertIsNotNone(self.app.viewed_month, "Should have viewed month")
        
        # Verify it can access expenses
        self.assertIsNotNone(self.app.expenses, "Should have expenses list")
        
        print(f"[OK] ExpenseTracker instance: {type(self.app).__name__}")
        print(f"[OK] Viewed month: {self.app.viewed_month}")
        print(f"[OK] Expenses count: {len(self.app.expenses)}")
    
    def test_filtered_query_through_app(self):
        """Test filtered query through actual app flow."""
        print("\n[TEST] Filtered query through app: 'What did I spend on groceries?'")
        
        result = self.engine.process("What did I spend on groceries?")
        
        # Verify it's a query
        self.assertEqual(result['intent'], 'query', "Should be query intent")
        
        # Verify response format
        response = result['response']
        self.assertIn("$", response, "Should return an amount")
        self.assertIn("groceries", response.lower(), "Should mention groceries")
        
        print(f"[OK] Response: {response[:150]}...")
    
    def test_multi_month_query_through_app(self):
        """Test multi-month query through actual app flow."""
        print("\n[TEST] Multi-month query through app: 'Compare my spending this month vs last month'")
        
        result = self.engine.process("Compare my spending this month vs last month")
        
        # Verify it's a query
        self.assertEqual(result['intent'], 'query', "Should be query intent")
        
        # Verify response exists
        response = result['response']
        self.assertIsNotNone(response, "Should have a response")
        self.assertGreater(len(response), 0, "Response should not be empty")
        
        print(f"[OK] Response: {response[:200]}...")
    
    def test_delete_intent_through_app(self):
        """Test delete intent through actual app flow."""
        print("\n[TEST] Delete intent through app: 'Delete the coffee expense'")
        
        result = self.engine.process("Delete the coffee expense")
        
        # Should be delete intent (or query if no match found)
        self.assertIn(result['intent'], ['delete', 'query'], "Should be delete or query intent")
        
        print(f"[OK] Intent: {result['intent']}")
        print(f"[OK] Response: {result['response'][:150]}...")


if __name__ == '__main__':
    # Run with verbose output
    unittest.main(verbosity=2)

