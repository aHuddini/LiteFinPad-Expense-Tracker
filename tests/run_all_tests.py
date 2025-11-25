# tests/run_all_tests.py
"""Run all AI chat unit tests and generate report."""

import unittest
import sys
import os
from io import StringIO

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test modules
from tests.test_intent_detection import TestIntentDetection
from tests.test_simple_query_handler import TestSimpleQueryHandler
from tests.test_multi_month_detection import TestMultiMonthDetection
from tests.test_expense_extraction import TestExpenseExtraction
from tests.test_ai_responses import TestAIResponses
from tests.test_app_integration import TestAppIntegration


def run_tests():
    """Run all tests and generate report."""
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestIntentDetection))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSimpleQueryHandler))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMultiMonthDetection))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExpenseExtraction))
    
    # Add AI response integration tests (slower - actual model inference)
    print("\n" + "="*70)
    print("RUNNING AI RESPONSE INTEGRATION TESTS (may take 10-30 seconds)")
    print("="*70)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAIResponses))
    
    # Add app integration tests (verify tests match actual app behavior)
    print("\n" + "="*70)
    print("RUNNING APP INTEGRATION TESTS (verifying app code paths)")
    print("="*70)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAppIntegration))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("="*70)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())

