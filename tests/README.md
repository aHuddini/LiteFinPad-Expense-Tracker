# AI Chat Test Suite

## Overview

Automated unit tests for the LiteFinPad AI Chat system.

## Test Coverage

### 1. Intent Detection (`test_intent_detection.py`)
- ✅ ADD intent with strong keywords (add, create, new, enter, record, log, save)
- ✅ DELETE intent with strong keywords (delete, remove, erase, clear)
- ✅ QUERY intent with question words (what, how, when, where, why, etc.)
- ✅ QUERY intent with spending words (spending, spent, spend, compare, total, etc.)
- ✅ QUERY intent with question marks (?)
- ✅ Ambiguous cases (hello, hi, thanks, etc.)

### 2. Simple Query Handler (`test_simple_query_handler.py`)
- ✅ Can handle simple queries (largest, lowest, total, categories, filtered)
- ✅ Cannot handle multi-month queries (compare, trend, annual, etc.)
- ✅ Largest expense calculation
- ✅ Lowest expense calculation
- ✅ Total calculation
- ✅ Filtered queries (exact match, multiple matches, no match)
- ✅ Case-insensitive filtering
- ✅ Punctuation stripping
- ✅ Category analysis
- ✅ Empty expense list handling

### 3. Multi-Month Detection (`test_multi_month_detection.py`)
- ✅ Multi-month keywords (compare, vs, last month, trend, annual, etc.)
- ✅ Single-month queries NOT detected as multi-month

### 4. Expense Extraction (`test_expense_extraction.py`)
- ✅ Amount validation (valid and invalid amounts)
- ✅ Description validation (valid and invalid descriptions)
- ✅ Relative date parsing (today, yesterday)
- ✅ Specific date parsing (DateUtils integration)
- ✅ Invalid date handling

### 5. AI Response Integration (`test_ai_responses.py`)
- ✅ Greeting tests (hello, hi) - ensures greetings don't return expense data
- ✅ Simple query tests (largest, lowest, total, filtered, categories)
- ✅ Multi-month query tests (comparisons, averages, trends)
- ✅ Edge cases (intent detection accuracy)
- **Tests use REAL data** from data folders (true integration testing)
- **Tests actual AI model responses** (catches real bugs)

## Running Tests

### Run All Tests
```bash
python tests/run_all_tests.py
```

### Run Individual Test Files
```bash
python -m unittest tests.test_intent_detection
python -m unittest tests.test_simple_query_handler
python -m unittest tests.test_multi_month_detection
python -m unittest tests.test_expense_extraction
```

### Run Specific Test Case
```bash
python -m unittest tests.test_intent_detection.TestIntentDetection.test_add_intent_keywords
```

## Expected Output

```
----------------------------------------------------------------------
Ran 41 tests in 19.057s

OK

======================================================================
TEST SUMMARY
======================================================================
Tests run: 41
Successes: 41
Failures: 0
Errors: 0
Success rate: 100.0%
======================================================================
```

**Note**: AI response tests take longer (~17 seconds) due to actual model inference.

## Test Data

### Sample Expense Data
```python
expenses = [
    {'date': '2025-11-01', 'amount': 100.0, 'description': 'Groceries'},
    {'date': '2025-11-02', 'amount': 50.0, 'description': 'Gas'},
    {'date': '2025-11-03', 'amount': 1200.0, 'description': 'Rent'},
    {'date': '2025-11-04', 'amount': 75.0, 'description': 'Groceries'},
    {'date': '2025-11-05', 'amount': 25.0, 'description': 'Coffee'},
]
```

## Adding New Tests

1. Create new test file in `tests/` directory
2. Import necessary modules
3. Create test class inheriting from `unittest.TestCase`
4. Write test methods starting with `test_`
5. Add test class to `run_all_tests.py`

### Example Test
```python
def test_new_feature(self):
    """Test description."""
    result = self.handler.new_feature("input")
    self.assertEqual(result, "expected_output")
```

## Known Limitations

- **No AI Model Tests**: Tests use mock data and don't require actual AI model
- **No Integration Tests**: Tests focus on unit-level logic
- **No Performance Tests**: No latency or throughput testing

## Future Test Coverage

- [ ] End-to-end integration tests
- [ ] Performance benchmarks
- [ ] Stress testing with large datasets
- [ ] AI model response quality tests
- [ ] Multi-threading safety tests
- [ ] Error recovery tests

## Continuous Integration

To run tests automatically:

### Pre-commit Hook
```bash
#!/bin/bash
python tests/run_all_tests.py
if [ $? -ne 0 ]; then
    echo "Tests failed! Commit aborted."
    exit 1
fi
```

### GitHub Actions
```yaml
name: AI Chat Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python tests/run_all_tests.py
```

## Troubleshooting

### Import Errors
Make sure parent directory is in Python path:
```python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

### Test Discovery Issues
Run from project root:
```bash
cd LiteFinPad
python tests/run_all_tests.py
```

### Module Not Found
Install all dependencies:
```bash
pip install -r requirements.txt
```

