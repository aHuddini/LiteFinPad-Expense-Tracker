# AI Chat Test Questions

**Date**: November 16, 2025  
**Purpose**: Comprehensive test suite for AI chat functionality with tool calling integration

---

## Test Categories

### 1. Basic Queries (SimpleQueryHandler - 100% Bypass)
These should be handled instantly by Python computation without AI:

1. "What's my largest expense?"
2. "What's my lowest expense?"
3. "What's my total?"
4. "How many expenses do I have?"
5. "What's my biggest expense?"
6. "What's my smallest expense?"
7. "What's my total spending?"

**Expected**: Fast responses (<50ms), accurate Python-computed answers

---

### 2. Category/Filtered Spending Queries
These should use SimpleQueryHandler's filtered query logic:

8. "How much did I spend on groceries?"
9. "What did I spend on rent?"
10. "Spending on gas?"
11. "How much for utilities?"
12. "What did I spend on coffee?"
13. "How much did I spend on dining out?"
14. "Spending on entertainment?"

**Expected**: Accurate category totals with expense counts

---

### 3. Analytical Queries (Recently Fixed)
These should use specific computation methods:

15. "What's my average expense amount?"
16. "What's my monthly average?"
17. "What percentage of my spending is on groceries?"
18. "What's the ratio of my largest to smallest expense?"
19. "What's my average spending per expense?"
20. "What percent of my budget goes to rent?"

**Expected**: 
- Average queries → Average amount calculation
- Percentage queries → Percentage calculation
- Ratio queries → Ratio calculation (not just largest expense)

---

### 4. Category Analysis Queries

21. "What categories did I spend the most on?"
22. "What are my top spending categories?"
23. "Which category takes up most of my budget?"
24. "Show me spending by category"

**Expected**: Top categories sorted by total spending

---

### 5. Multi-Month Comparison Queries
These should use AI processing with multi-month data:

25. "Compare my spending this month vs. last month"
26. "Compare November to October"
27. "How does this month compare to last month?"
28. "Compare my spending across the last 3 months"
29. "What's my spending trend?"

**Expected**: Month-to-month comparisons with percentage changes

---

### 6. Complex/Ambiguous Queries
These should test AI reasoning and tool calling:

30. "What's my most expensive purchase?"
31. "Where did most of my money go?"
32. "What's eating up my budget?"
33. "Show me my biggest expenses"
34. "What should I cut back on?"

**Expected**: AI should use appropriate tools or provide helpful analysis

---

### 7. Edge Cases

35. "What's my total?" (duplicate of #3, test consistency)
36. "How much did I spend?" (ambiguous - could be total or category)
37. "What's my average?" (ambiguous - could be expense amount or monthly spending)
38. "Show me expenses" (should list expenses)
39. "What expenses do I have?" (should list expenses)

**Expected**: Consistent, logical responses

---

### 8. Tool Calling Tests (If AI is Used)
These should trigger tool calling if SimpleQueryHandler doesn't catch them:

40. "Analyze my spending patterns"
41. "Give me insights about my expenses"
42. "What can you tell me about my spending habits?"
43. "Help me understand my expense data"

**Expected**: AI should call appropriate tools or provide analysis

---

## Test Checklist

### ✅ What to Verify

- [ ] **Response Speed**: Basic queries should be instant (<50ms)
- [ ] **Accuracy**: All calculations should be correct
- [ ] **Routing**: Queries should route to correct handlers
- [ ] **No Instructions**: AI should never return code or "how to use" instructions
- [ ] **Consistency**: Same query should return same answer
- [ ] **Formatting**: Responses should be well-formatted and readable
- [ ] **ReAct Steps**: If visible, thinking steps should show correct routing

### ⚠️ Known Issues to Watch For

- "What's my monthly average?" → Should return average, not expense list
- "What percentage..." → Should return percentage, not just total
- "What's the ratio..." → Should return ratio, not just largest expense
- Multi-month queries → Should compare months correctly

---

## Expected Behavior Summary

| Query Type | Handler | Speed | Tool Calling? |
|------------|---------|-------|---------------|
| Basic (largest, total, count) | SimpleQueryHandler | <50ms | No |
| Category spending | SimpleQueryHandler | <50ms | No |
| Analytical (avg, %, ratio) | SimpleQueryHandler | <50ms | No |
| Category analysis | SimpleQueryHandler | <50ms | No |
| Multi-month | AI + Tool Calling | 1-3s | Yes (compare_months) |
| Complex/Ambiguous | AI + Tool Calling | 1-3s | Maybe |
| Edge cases | SimpleQueryHandler or AI | Varies | Maybe |

---

## Success Criteria

✅ **All basic queries work correctly**  
✅ **All analytical queries return correct calculations**  
✅ **No instruction/code responses from AI**  
✅ **Multi-month queries provide accurate comparisons**  
✅ **Consistent responses for same queries**  
✅ **Fast response times for simple queries**

---

## Notes

- Tool calling is implemented but may not be used if SimpleQueryHandler catches queries first
- This is intentional - SimpleQueryHandler is faster and more reliable for known patterns
- Tool calling will be used for ambiguous/complex queries that SimpleQueryHandler can't handle
- ReAct pattern thinking steps should be visible in the chat interface for debugging

