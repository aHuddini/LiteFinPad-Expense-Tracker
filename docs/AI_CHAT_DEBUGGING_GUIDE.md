# AI Chat Debugging Guide

## Session Logging

### Location
All AI chat sessions are automatically logged to: `logs/ai_chat_YYYYMMDD_HHMMSS.json`

### Log Format
```json
{
  "session_start": "2025-11-16T10:30:00",
  "session_end": "2025-11-16T10:45:00",
  "model": "qwen:0.5b",
  "conversations": [
    {
      "timestamp": "2025-11-16T10:30:15",
      "user_input": "What's my largest expense?",
      "ai_response": "Your largest expense is $8989.00 for 7667 on November 09, 2025",
      "intent": "query",
      "thinking_steps": [
        "🤔 Detecting intent (add/edit/query)...",
        "✓ Detected intent: query",
        "💡 Computing answer directly..."
      ],
      "expenses_added": 0,
      "expenses_deleted": 0
    }
  ]
}
```

### How to Use
1. **After Testing**: Close the AI chat window
2. **Find Latest Log**: Check `logs/` folder for most recent `ai_chat_*.json` file
3. **Review Issues**: Look at `intent`, `thinking_steps`, and `ai_response` for each exchange
4. **Share with Developer**: Send the entire log file for debugging

---

## Known Issues & Fixes

### ✅ FIXED: "Spending on gas?" Triggered ADD Instead of QUERY
**Bug**: Queries like "Spending on X?" were misclassified as ADD commands
**Fix**: Added "spending", "spent", "spend", "compare" to query indicators
**Status**: Fixed in v3.6.3

### ⚠️ IN PROGRESS: Multi-Month Queries Returning Wrong Data
**Issue**: Queries like "Compare this month vs last month" return largest expense instead of comparison
**Current Investigation**: AI processing path may be using wrong data context
**Next Steps**: Review `_prepare_multi_month_context` and AI response parsing

### ⚠️ IN PROGRESS: "hello" Returning Largest Expense
**Issue**: Casual greetings trigger query logic instead of general conversation
**Current Investigation**: `_is_general_question` needs improvement
**Next Steps**: Add better greeting detection

---

## Debugging Checklist

When reporting AI chat issues, please provide:

- [ ] **Exact user input** (copy-paste from chat)
- [ ] **AI response** (copy-paste from chat)
- [ ] **Expected behavior** (what should have happened)
- [ ] **Session log file** (from `logs/` folder)
- [ ] **Model being used** (shown in chat window status)
- [ ] **Date/time of issue**

---

## Test Query Categories

### Simple Queries (Python Handler - Instant <50ms)
- "What's my largest expense?"
- "What's my lowest expense?"
- "What's my total?"
- "What categories did I spend the most on?"
- "What did I spend on [category]?"

### Multi-Month Queries (AI Processing - 2-5s)
- "Compare my spending this month vs. last month"
- "How much more did I spend this month?"
- "What's my monthly average?"
- "Which month did I spend the most?"

### CRUD Operations
- "Add $X for [item] on [date]"
- "Delete the [item] expense"

---

## Intent Detection Flow

```
User Input
    ↓
Strong Keywords? (add/delete/edit)
    ↓ NO
Question Words? (what/how/spend/compare/?)
    ↓ NO
AI Classification (ambiguous cases)
    ↓
Route to Handler (add/delete/edit/query)
```

### Strong Add Keywords
`add`, `create`, `new expense`, `enter`, `record`, `log`, `save`

### Strong Delete Keywords
`delete`, `remove`, `erase`, `clear`

### Query Indicators
`what`, `how`, `when`, `where`, `why`, `which`, `who`, `show`, `tell`, `list`, 
`compare`, `spent`, `spending`, `spend`, `total`, `largest`, `smallest`, `lowest`, `highest`, `?`

---

## Model Comparison

### SmolLM 360M (Original)
- **Size**: 220MB
- **Strengths**: Fast, low resource
- **Weaknesses**: Poor instruction following (41% IFEval), code generation issues
- **Use Case**: Speed over accuracy

### Qwen 0.5B (Current)
- **Size**: 379MB
- **Strengths**: Better instruction following (55% IFEval), structured outputs
- **Weaknesses**: Slightly slower, larger file
- **Use Case**: Multi-month analysis, complex queries

---

## Common Response Issues

### Issue: Generic Responses
**Symptom**: "You have 23 expenses totaling $14593.00"
**Cause**: Query handler falling through to generic fallback
**Debug**: Check intent detection and simple query handler matching

### Issue: Wrong Data Returned
**Symptom**: Asked for comparison, got largest expense
**Cause**: AI response parsing triggering wrong fallback
**Debug**: Check `_compute_answer_fallback` logic and multi-month context

### Issue: Code Generation
**Symptom**: AI returns Python code instead of answer
**Cause**: Model limitation (SmolLM) or prompt issues
**Solution**: Switch to Qwen 0.5B, check code detection fallback

---

## Performance Metrics

### Target Response Times
- **Simple Queries**: <50ms (Python handler)
- **Filtered Queries**: <50ms (Python handler)
- **Multi-Month AI Queries**: 2-5 seconds (AI processing)
- **Add/Delete Operations**: 1-3 seconds (AI extraction + validation)

### Success Rates (Expected with Qwen 0.5B)
- **Intent Detection**: >95%
- **Simple Queries**: 100%
- **Multi-Month Queries**: >85%
- **Expense Extraction**: >90%

---

## Next Steps for Full Debugging

1. ✅ Implement session logging (DONE)
2. ✅ Fix "Spending on X?" intent detection (DONE)
3. ⏳ Fix multi-month query responses
4. ⏳ Fix "hello" greeting detection
5. ⏳ Review delete operation accuracy
6. ⏳ Add unit tests for intent detection
7. ⏳ Add integration tests for query handlers

