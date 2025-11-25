"""
Expense Operations Pipeline

Handles add, edit, and delete operations for expenses.
"""

import json
import re
from typing import Dict, List, Optional, Callable
from datetime import datetime

from AI_py.llm.inference import InferenceEngine
from AI_py.config.financial_dictionary import FinancialDictionary

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from error_logger import log_info, log_warning, log_error, log_debug
from validation import ValidationPresets, InputValidation


class ExpenseOperations:
    """Handles expense add, edit, and delete operations."""
    
    def __init__(self, expense_tracker, inference_engine: InferenceEngine):
        """
        Initialize expense operations.
        
        Args:
            expense_tracker: Expense tracker instance
            inference_engine: Inference engine for AI operations
        """
        self.expense_tracker = expense_tracker
        self.inference_engine = inference_engine
        self.dictionary = FinancialDictionary()
    
    def add_expense(
        self, 
        user_input: str, 
        month_key: str, 
        thinking_callback: Optional[Callable[[str], None]] = None
    ) -> Dict:
        """
        Add expense(s) from natural language input.
        
        Args:
            user_input: Natural language input describing expense(s)
            month_key: Month key (YYYY-MM)
            thinking_callback: Optional callback for thinking steps
            
        Returns:
            Dict with 'intent', 'response', 'expenses_to_add'
        """
        def _think(msg):
            if thinking_callback:
                thinking_callback(msg)
        
        try:
            _think("🤖 Using AI to extract expense data...")
            
            # Get extraction prompt - use conversation-style few-shot examples
            system_prompt, few_shot_examples = self._get_extraction_prompt(month_key)
            
            # Build messages with few-shot examples in conversation format
            messages = [
                {'role': 'system', 'content': system_prompt}
            ]
            
            # Add few-shot examples as conversation history
            for example_input, example_output in few_shot_examples:
                messages.append({'role': 'user', 'content': example_input})
                messages.append({'role': 'assistant', 'content': example_output})
            
            # Add actual user input
            messages.append({'role': 'user', 'content': user_input})
            
            response = self.inference_engine.chat_completion(
                messages=messages,
                max_tokens=200,
                temperature=0.0,
                top_p=0.1
            )
            
            _think("📋 Parsing AI response...")
            response_content = self.inference_engine.extract_response_text(response)
            if not response_content:
                return self._handle_extraction_failure(user_input, month_key, "Empty response from model", thinking_callback)
            
            log_debug(f"[ExpenseOperations] Raw extraction response: {response_content}")
            log_info(f"[ExpenseOperations] AI extraction attempt for: '{user_input}' -> Response: {response_content[:100]}...")
            
            # Extract and parse JSON (single consolidated path)
            parsed_expenses = self._extract_and_parse_json(response_content, user_input, month_key, thinking_callback)
            
            if parsed_expenses is None:
                # All extraction failed - use fallback
                return self._handle_extraction_failure(user_input, month_key, "Could not extract valid expense data", thinking_callback)
            
            # Validate expenses
            _think("✅ Validating expense data...")
            validated_expenses = []
            for exp in parsed_expenses:
                validated = self._validate_expense(exp, month_key, user_input)
                if validated:
                    validated_expenses.append(validated)
                else:
                    log_debug(f"Expense validation failed: {exp}")
            
            if not validated_expenses:
                return self._handle_extraction_failure(user_input, month_key, "Validation failed for all expenses", thinking_callback)
            
            _think(f"✓ Validated {len(validated_expenses)} expense(s)")
            
            # Build response
            if len(validated_expenses) == 1:
                exp = validated_expenses[0]
                response_text = f"Adding expense: ${exp['amount']:.2f} for {exp['description']} on {exp['date']}..."
            else:
                response_text = f"Adding {len(validated_expenses)} expenses:\n"
                for exp in validated_expenses:
                    response_text += f"  • ${exp['amount']:.2f} - {exp['description']} ({exp['date']})\n"
            
            return {
                'intent': 'add',
                'response': response_text,
                'expenses_to_add': validated_expenses,
                'confirmation_needed': False
            }
            
        except Exception as e:
            log_error(f"Error handling add expense: {e}", e)
            return self._handle_extraction_failure(user_input, month_key, f"Error: {e}", thinking_callback)
    
    def _extract_and_parse_json(self, response_content: str, user_input: str, month_key: str, thinking_callback=None) -> Optional[List[Dict]]:
        """
        Extract JSON from AI response and parse it.
        Returns list of expense dicts or None if extraction fails.
        """
        def _think(msg):
            if thinking_callback:
                thinking_callback(msg)
        
        log_debug(f"[ExpenseOperations] Attempting to extract JSON from: {response_content[:200]}")
        
        # Extract JSON from response (handle both {} and [] formats)
        json_start = response_content.find('{')
        json_end = response_content.rfind('}') + 1
        if json_start != -1 and json_end > json_start:
            extracted_json = response_content[json_start:json_end]
        elif '[' in response_content:
            json_start = response_content.find('[')
            json_end = response_content.rfind(']') + 1
            if json_start != -1 and json_end > json_start:
                extracted_json = response_content[json_start:json_end]
            else:
                log_debug(f"[ExpenseOperations] No valid JSON found in response")
                return None
        else:
            log_debug(f"[ExpenseOperations] No JSON brackets found in response")
            return None
        
        log_debug(f"[ExpenseOperations] Extracted JSON: {extracted_json[:200]}")
        
        # Check for code patterns (single check after extraction)
        code_indicators = ['float(', 'expense)', '.split(', '.strip()', 'user_input', 'def ', 'import ', '"amount": amount', '"description": description']
        if any(indicator in extracted_json for indicator in code_indicators):
            log_debug(f"[ExpenseOperations] Code detected in JSON, extraction failed: {extracted_json[:200]}")
            return None
        
        # Fix common JSON errors (simplified)
        # Fix double decimals: "25.99.0" -> "25.99"
        original_json = extracted_json
        extracted_json = re.sub(r'(\d+\.\d+)\.(\d+)', r'\1', extracted_json)
        if original_json != extracted_json:
            log_debug(f"[ExpenseOperations] Fixed JSON error: {original_json[:100]} -> {extracted_json[:100]}")
        
        # Parse JSON
        try:
            parsed = json.loads(extracted_json)
            log_debug(f"[ExpenseOperations] Successfully parsed JSON: {parsed}")
        except json.JSONDecodeError as e:
            log_warning(f"[ExpenseOperations] JSON parse error: {e}, content: {extracted_json[:200]}")
            return None
        
        # Extract expenses from parsed structure
        expenses = []
        if isinstance(parsed, list):
            expenses = parsed
        elif isinstance(parsed, dict):
            if 'expenses' in parsed:
                expenses = parsed['expenses']
            elif all(isinstance(v, dict) and 'amount' in v for v in parsed.values()):
                expenses = list(parsed.values())
            elif 'amount' in parsed or 'description' in parsed:
                expenses = [parsed]
            else:
                log_warning(f"[ExpenseOperations] Unexpected JSON structure: {parsed}")
                return None
        
        # Validate and normalize dates (fix hallucinated dates)
        year, month = month_key.split('-')
        from datetime import datetime
        today = datetime.now()
        today_str = f"{year}-{month}-{today.day:02d}"
        
        normalized_expenses = []
        for exp in expenses:
            if isinstance(exp, dict):
                # Check for placeholders
                amount = exp.get('amount')
                if amount == 'amount' or amount == 'description' or (isinstance(amount, str) and not amount.replace('.', '').isdigit()):
                    log_debug(f"[ExpenseOperations] Placeholder detected in expense: {exp}")
                    continue
                
                # Validate and fix date - ALWAYS parse from user input first (more reliable)
                ai_date = exp.get('date', '')
                log_debug(f"[ExpenseOperations] AI returned date: {ai_date} for input: '{user_input}'")
                
                # Priority: User input parsing > AI extraction > Today default
                # ALWAYS try to parse from user input first - it's more reliable
                parsed_date = self._parse_date_from_input(user_input, month_key)
                log_debug(f"[ExpenseOperations] Parsed date from user input: '{parsed_date}'")
                
                if parsed_date:
                    # User input parsing succeeded - use it (highest priority)
                    date_str = parsed_date
                    log_debug(f"[ExpenseOperations] Using parsed date from user input: {date_str} (overriding AI date: {ai_date})")
                elif ai_date:
                    # No date from user input, but AI provided one - validate it
                    date_str = ai_date
                    try:
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        date_month = date_obj.strftime('%Y-%m')
                        if date_month != month_key:
                            # Date is in wrong month - use today instead
                            date_str = today_str
                            log_debug(f"[ExpenseOperations] AI date {ai_date} is in wrong month ({date_month} != {month_key}), using today: {today_str}")
                        else:
                            log_debug(f"[ExpenseOperations] Using AI date: {date_str}")
                    except ValueError:
                        # Invalid date format - use today
                        date_str = today_str
                        log_debug(f"[ExpenseOperations] Invalid AI date format '{ai_date}', using today: {today_str}")
                else:
                    # No date from AI and couldn't parse from input - use today
                    date_str = today_str
                    log_debug(f"[ExpenseOperations] No date found, using today: {today_str}")
                
                # Create normalized expense
                normalized_exp = {
                    'amount': float(amount) if isinstance(amount, (int, float)) else float(str(amount).replace('$', '').replace(',', '')),
                    'description': str(exp.get('description', '')).strip(),
                    'date': date_str
                }
                normalized_expenses.append(normalized_exp)
        
        if not normalized_expenses:
            log_debug(f"[ExpenseOperations] No valid expenses after normalization")
            return None
        
        log_debug(f"[ExpenseOperations] Successfully extracted {len(normalized_expenses)} expense(s)")
        return normalized_expenses
    
    def _handle_extraction_failure(self, user_input: str, month_key: str, reason: str, thinking_callback=None) -> Dict:
        """
        Handle extraction failure by trying fallback extraction.
        Consolidated fallback point for all failure scenarios.
        """
        def _think(msg):
            if thinking_callback:
                thinking_callback(msg)
        
        log_debug(f"Extraction failed: {reason}, trying fallback...")
        _think("🔄 Trying fallback extraction...")
        
        fallback_expense = self._extract_expense_fallback(user_input, month_key)
        if fallback_expense:
            validated = self._validate_expense(fallback_expense, month_key, user_input)
            if validated:
                _think(f"✓ Fallback extraction successful")
                response_text = f"Adding expense: ${validated['amount']:.2f} for {validated['description']} on {validated['date']}..."
                return {
                    'intent': 'add',
                    'response': response_text,
                    'expenses_to_add': [validated],
                    'confirmation_needed': False
                }
        
        # All extraction methods failed
        return {
            'intent': 'add',
            'response': f"I couldn't extract valid expense data from: '{user_input}'. Please try: 'Add $50 for groceries on November 15th'",
            'expenses_to_add': [],
            'confirmation_needed': False
        }
    
    def delete_expense(
        self,
        user_input: str,
        month_key: str,
        thinking_callback: Optional[Callable[[str], None]] = None
    ) -> Dict:
        """
        Delete expense(s) from natural language input.
        
        Args:
            user_input: Natural language input describing expense to delete
            month_key: Month key (YYYY-MM)
            thinking_callback: Optional callback for thinking steps
            
        Returns:
            Dict with 'intent', 'response', 'deleted_expense_index'
        """
        def _think(msg):
            if thinking_callback:
                thinking_callback(msg)
        
        _think("🔍 Searching for matching expenses...")
        
        expenses = self.expense_tracker.expenses
        
        if not expenses:
            return {
                'intent': 'delete',
                'response': f"No expenses found for {month_key}.",
                'expenses_to_add': [],
                'confirmation_needed': False
            }
        
        # Check for batch delete
        user_lower = user_input.lower()
        batch_keywords = ['all', 'every', 'remove all', 'delete all']
        is_batch = any(keyword in user_lower for keyword in batch_keywords)
        
        if is_batch:
            return self._handle_batch_delete(user_input, expenses, month_key, thinking_callback)
        
        # Use AI to identify expense
        try:
            _think("🤖 Using AI to identify expense to delete...")
            
            expense_summary = []
            for i, exp in enumerate(expenses):
                expense_summary.append(f"{i}: ${exp['amount']:.2f} - {exp['description']} ({exp['date']})")
            
            delete_prompt = f"""Identify which expense the user wants to delete from this list:

{chr(10).join(expense_summary)}

User request: {user_input}

CRITICAL MATCHING RULES (in priority order):
1. DESCRIPTION is MOST IMPORTANT - must match the description keywords
2. DATE matching (if user mentions a date)
3. AMOUNT matching (if user mentions an amount)

Return ONLY the index number (0-based) of the expense to delete, or -1 if no match found.
Return ONLY a number, nothing else."""
            
            messages = [
                {'role': 'system', 'content': 'You are an expense tracker assistant. Return ONLY a number.'},
                {'role': 'user', 'content': delete_prompt}
            ]
            
            response = self.inference_engine.chat_completion(
                messages=messages,
                max_tokens=3,
                temperature=0.0
            )
            
            _think("📋 Parsing deletion response...")
            
            response_text = self.inference_engine.extract_response_text(response)
            if not response_text:
                raise ValueError("Empty response")
            
            # Extract number
            match = re.search(r'-?\d+', response_text)
            expense_index = int(match.group()) if match else -1
            
            if expense_index < 0 or expense_index >= len(expenses):
                # Try fuzzy matching
                expense_index = self._fuzzy_match_expense(user_input, expenses)
                if expense_index < 0:
                    return {
                        'intent': 'delete',
                        'response': f"I couldn't find a matching expense. Try: 'Delete the $X [description] expense'",
                        'expenses_to_add': [],
                        'confirmation_needed': False
                    }
            
            expense_to_delete = expenses[expense_index]
            _think(f"✓ Found expense: ${expense_to_delete['amount']:.2f} - {expense_to_delete['description']}")
            
            # Delete expense
            del self.expense_tracker.expenses[expense_index]
            self.expense_tracker.save_data()
            
            response_text = f"Deleted expense: ${expense_to_delete['amount']:.2f} for {expense_to_delete['description']} on {expense_to_delete['date']}"
            
            return {
                'intent': 'delete',
                'response': response_text,
                'expenses_to_add': [],
                'confirmation_needed': False,
                'deleted_expense_index': expense_index
            }
            
        except Exception as e:
            log_error(f"Error handling delete expense: {e}", e)
            return {
                'intent': 'delete',
                'response': f"Error deleting expense: {e}",
                'expenses_to_add': [],
                'confirmation_needed': False
            }
    
    def _handle_batch_delete(
        self,
        user_input: str,
        expenses: List[Dict],
        month_key: str,
        thinking_callback: Optional[Callable[[str], None]]
    ) -> Dict:
        """Handle batch delete operations."""
        def _think(msg):
            if thinking_callback:
                thinking_callback(msg)
        
        user_lower = user_input.lower()
        
        # Extract category/description from input
        category_keywords = []
        for category, synonyms in self.dictionary.CATEGORY_SYNONYMS.items():
            if any(syn in user_lower for syn in synonyms):
                category_keywords.append(category)
                category_keywords.extend(synonyms)
        
        # Find expenses to delete
        expenses_to_delete = []
        for i, exp in enumerate(expenses):
            desc_lower = exp['description'].lower()
            if any(keyword.lower() in desc_lower for keyword in category_keywords):
                expenses_to_delete.append((i, exp))
        
        if not expenses_to_delete:
            return {
                'intent': 'delete',
                'response': f"No matching expenses found to delete.",
                'expenses_to_add': [],
                'confirmation_needed': False
            }
        
        # Delete in reverse order to maintain indices
        deleted_count = 0
        for i, exp in reversed(expenses_to_delete):
            del self.expense_tracker.expenses[i]
            deleted_count += 1
        
        self.expense_tracker.save_data()
        
        response_text = f"Deleted {deleted_count} expense(s)."
        
        return {
            'intent': 'delete',
            'response': response_text,
            'expenses_to_add': [],
            'confirmation_needed': False
        }
    
    def _fuzzy_match_expense(self, user_input: str, expenses: List[Dict]) -> int:
        """Fuzzy match expense by description/amount."""
        user_lower = user_input.lower()
        skip_words = {'the', 'for', 'on', 'delete', 'remove', 'bill', 'expense', 'november', 'nov', '15th', '15'}
        description_keywords = [w for w in user_lower.split() if w not in skip_words and len(w) > 2]
        
        best_match = -1
        best_score = 0
        
        for i, exp in enumerate(expenses):
            score = 0
            desc_lower = exp['description'].lower()
            
            # Description match (required)
            desc_match = any(keyword in desc_lower for keyword in description_keywords)
            if not desc_match:
                continue
            
            score += 20
            
            # Amount match (bonus)
            if str(int(exp['amount'])) in user_lower:
                score += 5
            
            # Date match (bonus)
            if exp['date'] in user_input:
                score += 3
            
            if score > best_score:
                best_score = score
                best_match = i
        
        return best_match if best_score >= 15 else -1
    
    def _validate_expense(self, exp: Dict, month_key: str, user_input: str = '') -> Optional[Dict]:
        """Validate and normalize expense data."""
        try:
            # Extract and validate amount
            amount = exp.get('amount', 0)
            if not isinstance(amount, (int, float)) or amount <= 0:
                log_warning(f"Invalid amount: {amount}")
                return None
            
            # Extract and validate description
            description = exp.get('description', '').strip()
            if not description:
                log_warning("Missing description")
                return None
            
            # Remove "Today" or date words from description if present
            date_words = ['today', 'yesterday', 'tomorrow', 'november', 'nov', 'december', 'dec']
            desc_words = description.split()
            description = ' '.join([w for w in desc_words if w.lower() not in date_words])
            
            # Extract and validate date
            date_str = exp.get('date', '')
            if not date_str:
                # Try to parse from user input
                date_str = self._parse_date_from_input(user_input, month_key)
            
            if not date_str:
                # Default to today
                year, month = month_key.split('-')
                from datetime import datetime
                today = datetime.now()
                date_str = f"{year}-{month}-{today.day:02d}"
            
            # Parse and validate date
            date_obj = self._parse_relative_date(date_str, month_key)
            if not date_obj:
                log_warning(f"Invalid date: {date_str}")
                return None
            
            date_formatted = date_obj.strftime('%Y-%m-%d')
            
            # Validate using ValidationPresets (expects strings)
            validation_result = ValidationPresets.manual_add_expense(
                str(amount),
                description,
                date_formatted
            )
            
            if not validation_result.is_valid:
                log_warning(f"Validation failed: {validation_result.error_message}")
                return None
            
            # Use sanitized values from validation
            sanitized = validation_result.sanitized_value
            
            return {
                'amount': float(sanitized['amount']),
                'description': sanitized['description'],
                'date': sanitized['date']
            }
            
        except Exception as e:
            log_warning(f"Error validating expense: {e}")
            return None
    
    def _extract_expense_fallback(self, user_input: str, month_key: str) -> Optional[Dict]:
        """Fallback expense extraction using regex when AI fails."""
        try:
            # Extract amount
            amount_match = re.search(r'\$?\s*(\d+(?:\.\d{2})?)', user_input)
            if not amount_match:
                return None
            amount = float(amount_match.group(1))
            
            # Extract description (text after "for" or after amount)
            # Pattern: "for X" or "$50 X" or "Add $50 X"
            desc_patterns = [
                r'for\s+([^0-9$]+?)(?:\s+on|\s+today|\s+yesterday|$)',
                r'\$\d+(?:\.\d{2})?\s+for\s+([^0-9$]+?)(?:\s+on|\s+today|\s+yesterday|$)',
                r'Add\s+\$?\d+(?:\.\d{2})?\s+([^0-9$]+?)(?:\s+on|\s+today|\s+yesterday|$)',
            ]
            
            description = None
            for pattern in desc_patterns:
                match = re.search(pattern, user_input, re.IGNORECASE)
                if match:
                    description = match.group(1).strip()
                    # Remove common words
                    description = re.sub(r'\b(for|on|today|yesterday|the|a|an)\b', '', description, flags=re.IGNORECASE).strip()
                    if description:
                        break
            
            if not description:
                # Last resort: extract text between amount and date words
                parts = re.split(r'\$?\d+(?:\.\d{2})?', user_input, maxsplit=1)
                if len(parts) > 1:
                    desc_part = parts[1]
                    # Remove date-related words
                    desc_part = re.sub(r'\b(on|today|yesterday|november|nov|december|dec|\d{1,2}(?:st|nd|rd|th)?)\b', '', desc_part, flags=re.IGNORECASE)
                    description = desc_part.strip()
                    # Remove "for" if present
                    description = re.sub(r'^for\s+', '', description, flags=re.IGNORECASE).strip()
            
            if not description:
                return None
            
            # Extract date
            year, month = month_key.split('-')
            date_str = self._parse_date_from_input(user_input, month_key)
            if not date_str:
                from datetime import datetime
                today = datetime.now()
                date_str = f"{year}-{month}-{today.day:02d}"
            
            return {
                'amount': amount,
                'description': description,
                'date': date_str
            }
        except Exception as e:
            log_warning(f"Fallback extraction failed: {e}")
            return None
    
    def _parse_date_from_input(self, user_input: str, month_key: str) -> str:
        """Parse date from user input - enhanced to handle more cases."""
        from datetime import datetime, timedelta
        
        user_lower = user_input.lower()
        year, month = month_key.split('-')
        
        # Handle "today"
        if 'today' in user_lower:
            today = datetime.now()
            return f"{year}-{month}-{today.day:02d}"
        
        # Handle "yesterday" - use actual yesterday's date, not just day number
        if 'yesterday' in user_lower:
            yesterday = datetime.now() - timedelta(days=1)
            # If yesterday was in a different month, use that month
            if yesterday.strftime('%Y-%m') != month_key:
                return yesterday.strftime('%Y-%m-%d')
            return f"{year}-{month}-{yesterday.day:02d}"
        
        # Try to extract day number (e.g., "20th", "the 20th", "on the 20th", "20")
        # Priority: patterns with "on" or "the" first (more specific), then generic
        day_patterns = [
            r'on\s+the\s+(\d{1,2})(?:st|nd|rd|th)?',  # "on the 20th" - highest priority
            r'on\s+(\d{1,2})(?:st|nd|rd|th)?',        # "on 20th"
            r'the\s+(\d{1,2})(?:st|nd|rd|th)?',       # "the 20th"
            r'\b(\d{1,2})(?:st|nd|rd|th)\b',          # "20th"
        ]
        
        for pattern in day_patterns:
            day_match = re.search(pattern, user_input, re.IGNORECASE)
            if day_match:
                day = int(day_match.group(1))
                # Validate day is reasonable (1-31)
                if 1 <= day <= 31:
                    # For patterns with "on" or "the", we can trust them (they're date indicators)
                    if 'on' in pattern or 'the' in pattern:
                        return f"{year}-{month}-{day:02d}"
                    
                    # For generic patterns like "20th", check context
                    # If it appears after "for" or "on", it's likely a date
                    match_pos = day_match.start()
                    before_match = user_input[:match_pos].lower()
                    
                    # Check if this appears in a date context (after "for", "on", etc.)
                    if any(word in before_match for word in ['for', 'on', 'the']):
                        return f"{year}-{month}-{day:02d}"
                    
                    # If there's a dollar sign before, check if "for" or "on" appears between $ and this number
                    if '$' in before_match:
                        # Extract text between $ and the match
                        dollar_pos = before_match.rfind('$')
                        between = user_input[dollar_pos:match_pos].lower()
                        # If "for" or "on" appears between $ and the number, it's likely a date
                        if 'for' in between or 'on' in between:
                            return f"{year}-{month}-{day:02d}"
                        # Otherwise, might be matching the amount - skip
                        continue
        
        return ''
    
    def _parse_relative_date(self, date_str: str, month_key: str) -> Optional[datetime]:
        """Parse relative date string."""
        try:
            date_lower = date_str.lower()
            
            # Handle "today"
            if 'today' in date_lower:
                return datetime.now()
            
            # Handle "yesterday"
            if 'yesterday' in date_lower:
                from datetime import timedelta
                return datetime.now() - timedelta(days=1)
            
            # Try YYYY-MM-DD format first
            if len(date_str) == 10 and date_str.count('-') == 2:
                return datetime.strptime(date_str, '%Y-%m-%d')
            
            # Try to extract from month_key context
            year, month = month_key.split('-')
            
            # Extract day from date_str
            day_match = re.search(r'\d{1,2}', date_str)
            if day_match:
                day = int(day_match.group())
                return datetime(int(year), int(month), day)
            
            return None
        except:
            return None
    
    def _get_extraction_prompt(self, month_key: str) -> tuple:
        """
        Get prompt for expense extraction using conversation-style few-shot learning.
        Returns (system_prompt, few_shot_examples) where examples are (input, output) tuples.
        """
        year, month = month_key.split('-')
        from datetime import datetime
        today = datetime.now()
        today_str = f"{year}-{month}-{today.day:02d}"
        
        # Calculate yesterday's date for prompt
        from datetime import timedelta
        yesterday = datetime.now() - timedelta(days=1)
        yesterday_str = yesterday.strftime('%Y-%m-%d')
        
        # System prompt - ultra-concise to save tokens (must fit in 2048 context)
        system_prompt = f"""Extract expense from user message. Return JSON only.

Format: {{"amount": NUMBER, "description": "TEXT", "date": "YYYY-MM-DD"}}
Today: {today_str}
Yesterday: {yesterday_str}

Date rules:
- "today" or no date → {today_str}
- "yesterday" → {yesterday_str}
- "20th" or "on the 20th" → {year}-{month}-20
- Extract date from message if mentioned"""
        
        # Few-shot examples - use different example to avoid exact match confusion
        # Use a different amount/description so model doesn't just copy
        few_shot_examples = [
            (
                "$200 rent today",
                json.dumps({"amount": 200, "description": "rent", "date": today_str})
            )
        ]
        
        return system_prompt, few_shot_examples

