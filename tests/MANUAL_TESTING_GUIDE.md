# Manual Testing Guide - AI Chat

## 🎯 **How to Access AI Chat**

1. **Right-click the system tray icon** (LiteFinPad icon in system tray)
2. **Click "AI Chat"** from the context menu
3. The AI Chat window will open

---

## 📋 **Sample Test Questions**

### ✅ **1. Greeting Tests** (Should return greetings, NOT expense data)

```
hello
hi
hey
thanks
```

**Expected**: Friendly greeting response, NO expense data

---

### ✅ **2. Simple Query Tests** (Should use Python handler - instant responses)

```
What's my largest expense?
What's my lowest expense?
What's my total?
What's my most expensive expense?
What's my smallest expense?
```

**Expected**: Direct answers with amounts and descriptions

---

### ✅ **3. Filtered Query Tests** (Should filter by category/description)

```
What did I spend on groceries?
How much did I spend on rent?
What did I spend on gas?
Spending on utilities?
What did I spend on coffee?
```

**Expected**: Total amount for that specific category/item

---

### ✅ **4. Category Analysis Tests**

```
What categories did I spend the most on?
What are my top spending categories?
Show me my spending by category
```

**Expected**: Breakdown of spending by category

---

### ✅ **5. Multi-Month Query Tests** (Should use AI processing)

```
Compare my spending this month vs last month
What's my monthly average?
How much more did I spend this month?
What's my spending trend?
Show me my spending over the past 3 months
```

**Expected**: Multi-month analysis or comparison

---

### ✅ **6. Add Expense Tests** (Should extract and add expenses)

```
Add $50 for groceries on November 15th
Add $100 for rent today
Add $25 for coffee yesterday
Add $200 for utilities on November 20th
```

**Expected**: Expense extracted and added automatically

---

### ✅ **7. Batch Add Expense Tests**

```
Add $50 groceries, $30 gas, $20 lunch
Add $100 rent and $50 utilities for today
```

**Expected**: Multiple expenses extracted and added

---

### ✅ **8. Delete Expense Tests**

```
Delete the groceries expense
Delete the rent payment for November 15th
Remove the coffee expense
Delete expenses from November 15th
```

**Expected**: Expense(s) identified and deleted

---

### ✅ **9. Edge Cases & Ambiguous Queries**

```
Spending on gas?          (Should be QUERY, not ADD)
What's my budget?         (General question)
How do I add expenses?    (Capability question)
Show me my expenses       (List expenses)
```

**Expected**: Appropriate responses based on intent

---

### ✅ **10. Complex Queries** (Test AI reasoning)

```
What's my average expense per day?
Which day did I spend the most?
What percentage of my spending is on groceries?
How many times did I buy coffee this month?
```

**Expected**: Calculated answers or AI-processed responses

---

## 🐛 **Known Issues to Watch For**

### ❌ **Should NOT Happen:**

1. **Greeting returns expense data**
   - ❌ "hello" → "$700.00 groceries"
   - ✅ "hello" → "Hello! How can I assist you today?"

2. **Query returns code/instructions**
   - ❌ "What's my largest expense?" → "Here's how to find it: ```python..."
   - ✅ "What's my largest expense?" → "Your largest expense is $8989.00..."

3. **Query returns raw data**
   - ❌ "What's my total?" → `{"expenses": [...]}`
   - ✅ "What's my total?" → "Your total is $14668.00"

4. **Multi-month query returns single expense**
   - ❌ "Compare this month vs last month" → "$1200.00 Rent"
   - ✅ "Compare this month vs last month" → "This month: $1000, Last month: $800..."

5. **"Spending on X?" detected as ADD**
   - ❌ "Spending on gas?" → Adds expense
   - ✅ "Spending on gas?" → Returns spending amount

---

## 📊 **Test Results Template**

Use this to track your manual testing:

```
Test Date: ___________
Model: Qwen 0.5B

[ ] Greeting Tests (4 tests)
    [ ] hello
    [ ] hi
    [ ] hey
    [ ] thanks

[ ] Simple Query Tests (5 tests)
    [ ] What's my largest expense?
    [ ] What's my lowest expense?
    [ ] What's my total?
    [ ] What's my most expensive expense?
    [ ] What's my smallest expense?

[ ] Filtered Query Tests (5 tests)
    [ ] What did I spend on groceries?
    [ ] How much did I spend on rent?
    [ ] What did I spend on gas?
    [ ] Spending on utilities?
    [ ] What did I spend on coffee?

[ ] Category Analysis Tests (3 tests)
    [ ] What categories did I spend the most on?
    [ ] What are my top spending categories?
    [ ] Show me my spending by category

[ ] Multi-Month Query Tests (5 tests)
    [ ] Compare my spending this month vs last month
    [ ] What's my monthly average?
    [ ] How much more did I spend this month?
    [ ] What's my spending trend?
    [ ] Show me my spending over the past 3 months

[ ] Add Expense Tests (4 tests)
    [ ] Add $50 for groceries on November 15th
    [ ] Add $100 for rent today
    [ ] Add $25 for coffee yesterday
    [ ] Add $200 for utilities on November 20th

[ ] Batch Add Tests (2 tests)
    [ ] Add $50 groceries, $30 gas, $20 lunch
    [ ] Add $100 rent and $50 utilities for today

[ ] Delete Expense Tests (4 tests)
    [ ] Delete the groceries expense
    [ ] Delete the rent payment for November 15th
    [ ] Remove the coffee expense
    [ ] Delete expenses from November 15th

[ ] Edge Cases (4 tests)
    [ ] Spending on gas?
    [ ] What's my budget?
    [ ] How do I add expenses?
    [ ] Show me my expenses

[ ] Complex Queries (4 tests)
    [ ] What's my average expense per day?
    [ ] Which day did I spend the most?
    [ ] What percentage of my spending is on groceries?
    [ ] How many times did I buy coffee this month?

Total Tests: 44
Passed: ___
Failed: ___
```

---

## 🎯 **Quick Test Checklist**

### **Critical Tests (Must Pass):**
- [ ] "hello" returns greeting (NOT expense data)
- [ ] "What's my largest expense?" returns largest expense
- [ ] "What did I spend on groceries?" returns filtered total
- [ ] "Add $50 for groceries today" adds expense correctly
- [ ] "Spending on gas?" is QUERY (not ADD)

### **Important Tests (Should Pass):**
- [ ] "Compare this month vs last month" returns comparison
- [ ] "What categories did I spend the most on?" returns breakdown
- [ ] "Delete the groceries expense" deletes correctly
- [ ] Batch add works ("Add $50 groceries, $30 gas")

### **Nice-to-Have Tests (May vary):**
- [ ] Complex queries return reasonable answers
- [ ] Multi-month trends work correctly
- [ ] Edge cases handled gracefully

---

## 💡 **Tips for Testing**

1. **Test one category at a time** - Don't mix query types
2. **Check the response format** - Should be natural language, not code
3. **Verify expense additions** - Check the main app window updates
4. **Test edge cases** - Try unusual queries
5. **Note any issues** - Document bugs for fixing

---

## 📝 **Reporting Issues**

If you find a bug, note:
1. **Your input**: Exact text you typed
2. **Expected response**: What you expected
3. **Actual response**: What you got
4. **Screenshot** (if possible): Visual evidence

---

## ✅ **Expected Behavior Summary**

| Query Type | Response Time | Response Format | Uses AI? |
|------------|---------------|-----------------|----------|
| **Greeting** | < 1s | Friendly greeting | ✅ Yes |
| **Simple Query** | < 50ms | Direct answer | ❌ No (Python) |
| **Filtered Query** | < 50ms | Filtered total | ❌ No (Python) |
| **Category Query** | < 50ms | Category breakdown | ❌ No (Python) |
| **Multi-Month** | 2-5s | Comparison/analysis | ✅ Yes |
| **Add Expense** | 2-5s | Confirmation + adds | ✅ Yes |
| **Delete Expense** | 2-5s | Confirmation + deletes | ✅ Yes |

---

**Happy Testing!** 🎉

