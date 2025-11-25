"""Expense analytics calculations. All functions are pure (no side effects)."""

from datetime import datetime, timedelta
import calendar
import json
import os
from date_utils import DateUtils


class ExpenseAnalytics:
    """Pure analytics class for expense calculations. All methods are static."""
    
    # ==========================================
    # HELPER METHODS: Expense Filtering
    # ==========================================
    # These methods centralize common expense filtering patterns to eliminate duplication.
    
    @staticmethod
    def _filter_expenses_by_date_range(expenses, start_date=None, end_date=None, current_date=None):
        """
        Filter expenses by date range.
        
        Args:
            expenses: List of expense dictionaries
            start_date: Start of range (inclusive), None for no limit
            end_date: End of range (inclusive), None excludes future if current_date provided
            current_date: Reference date for future filtering, defaults to today
        
        Returns:
            Filtered expense list
        """
        if current_date is None:
            current_date = datetime.now()
        
        filtered = []
        for expense in expenses:
            dt = DateUtils.parse_date(expense['date'])
            if not dt:
                continue  # Skip invalid dates
            
            expense_date = dt.date()
            
            if start_date and expense_date < start_date.date():
                continue
            
            if end_date:
                if expense_date > end_date.date():
                    continue
            elif expense_date > current_date.date():
                continue
            
            filtered.append(expense)
        
        return filtered
    
    @staticmethod
    def _filter_expenses_by_month(expenses, month_date, exclude_future=True):
        """
        Filter expenses for a specific month.
        
        Args:
            expenses: List of expense dictionaries
            month_date: Any date in the target month
            exclude_future: If True, exclude expenses after month_date
        
        Returns:
            Expenses for the specified month
        """
        month_start = month_date.replace(day=1)
        
        if month_date.month == 12:
            month_end = month_date.replace(year=month_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = month_date.replace(month=month_date.month + 1, day=1) - timedelta(days=1)
        
        end_date = month_date if exclude_future else month_end
        
        return ExpenseAnalytics._filter_expenses_by_date_range(
            expenses, 
            start_date=month_start, 
            end_date=end_date,
            current_date=month_date
        )
    
    @staticmethod
    def _filter_expenses_by_week(expenses, week_date, exclude_future=True):
        """
        Filter expenses for a specific week (Monday to Sunday).
        
        Args:
            expenses: List of expense dictionaries
            week_date: Any date in the target week
            exclude_future: If True, exclude expenses after week_date
        
        Returns:
            Expenses for the specified week
        """
        week_start = week_date - timedelta(days=week_date.weekday())  # Monday
        week_end = week_start + timedelta(days=6)  # Sunday
        
        end_date = week_date if exclude_future else week_end
        
        return ExpenseAnalytics._filter_expenses_by_date_range(
            expenses,
            start_date=week_start,
            end_date=end_date,
            current_date=week_date
        )
    
    @staticmethod
    def _filter_past_expenses(expenses, current_date=None):
        """
        Filter out future expenses (keep only past and today).
        
        Args:
            expenses: List of expense dictionaries
            current_date: Reference date, defaults to today
        
        Returns:
            Expenses with dates <= current_date
        """
        if current_date is None:
            current_date = datetime.now()
        
        return ExpenseAnalytics._filter_expenses_by_date_range(
            expenses,
            end_date=current_date,
            current_date=current_date
        )
    
    # ==========================================
    # PUBLIC METHODS: Analytics Calculations
    # ==========================================
    
    @staticmethod
    def calculate_day_progress(current_date=None):
        """
        Get current day progress in the month.
        
        Args:
            current_date: Date to calculate from, defaults to today
            
        Returns:
            (current_day, total_days_in_month)
        """
        if current_date is None:
            current_date = datetime.now()
        
        current_day = current_date.day
        total_days = calendar.monthrange(current_date.year, current_date.month)[1]
        
        return current_day, total_days
    
    @staticmethod
    def calculate_week_progress(current_date=None):
        """
        Get current week progress in the month with decimal precision.
        
        Args:
            current_date: Date to calculate from, defaults to today
            
        Returns:
            (precise_week, total_weeks)
        """
        if current_date is None:
            current_date = datetime.now()
        
        current_day = current_date.day
        
        # Base week number (1 for days 1-7, 2 for days 8-14, etc.)
        base_week = ((current_day - 1) // 7) + 1
        
        # Position within the week (0-6 for the 7 days)
        day_in_week = (current_day - 1) % 7
        
        # Decimal component (0.0 for first day, 0.1 for second, ... 0.9 for last day)
        week_decimal = day_in_week / 10.0
        
        precise_week = base_week + week_decimal
        
        # Total weeks in month (estimate based on total days)
        total_days = calendar.monthrange(current_date.year, current_date.month)[1]
        total_weeks = (total_days // 7) + (1 if total_days % 7 > 0 else 0)
        
        return precise_week, total_weeks
    
    @staticmethod
    def calculate_daily_average(expenses, current_date=None):
        """
        Calculate average spending per day (month total ÷ days elapsed).
        
        Args:
            expenses: List of expense dictionaries
            current_date: Date to calculate from, defaults to today
            
        Returns:
            (average_per_day, days_elapsed)
        """
        if not expenses:
            return 0.0, 0
        
        if current_date is None:
            current_date = datetime.now()
        
        # Get current month's expenses (excluding future dates) using helper method
        month_expenses = ExpenseAnalytics._filter_expenses_by_month(
            expenses, 
            month_date=current_date, 
            exclude_future=True
        )
        
        monthly_total = sum(e['amount'] for e in month_expenses)
        days_elapsed = current_date.day
        
        # Average per day = monthly total ÷ days elapsed
        avg_per_day = monthly_total / days_elapsed if days_elapsed > 0 else 0
        
        return avg_per_day, days_elapsed
    
    @staticmethod
    def calculate_weekly_average(expenses, current_date=None):
        """
        Calculate average spending per week (month total ÷ weeks elapsed).
        
        Args:
            expenses: List of expense dictionaries
            current_date: Date to calculate from, defaults to today
            
        Returns:
            (average_per_week, weeks_elapsed)
        """
        if not expenses:
            return 0.0, 0
        
        if current_date is None:
            current_date = datetime.now()
        
        # Get current month's expenses (excluding future dates) using helper method
        month_expenses = ExpenseAnalytics._filter_expenses_by_month(
            expenses,
            month_date=current_date,
            exclude_future=True
        )
        
        monthly_total = sum(e['amount'] for e in month_expenses)
        
        # Calculate weeks elapsed: (current day - 1) ÷ 7 + 1
        # This gives us the week number we're in (1, 2, 3, 4, etc.)
        current_day = current_date.day
        weeks_elapsed = ((current_day - 1) // 7) + 1
        
        # Average per week = monthly total ÷ weeks elapsed
        avg_per_week = monthly_total / weeks_elapsed if weeks_elapsed > 0 else 0
        
        return avg_per_week, weeks_elapsed
    
    @staticmethod
    def calculate_weekly_pace(expenses, current_date=None):
        """
        Calculate current week's spending pace (week total ÷ days elapsed this week).
        
        Args:
            expenses: List of expense dictionaries
            current_date: Date to calculate from, defaults to today
            
        Returns:
            (pace_per_day, days_elapsed_this_week)
        """
        if not expenses:
            return 0.0, 0
        
        if current_date is None:
            current_date = datetime.now()
        
        # Get current week's expenses (Monday to today, excluding future dates) using helper method
        week_expenses = ExpenseAnalytics._filter_expenses_by_week(
            expenses,
            week_date=current_date,
            exclude_future=True
        )
        
        weekly_total = sum(e['amount'] for e in week_expenses)
        week_start = current_date - timedelta(days=current_date.weekday())  # Monday of current week
        days_elapsed = (current_date - week_start).days + 1  # Days from Monday to today (inclusive)
        
        # Pace = weekly total ÷ days elapsed in current week
        pace_per_day = weekly_total / days_elapsed if days_elapsed > 0 else 0
        
        # Return pace and days for context
        return pace_per_day, days_elapsed
    
    @staticmethod
    def calculate_monthly_trend(prev_month_data_folder=None, current_month_total=None, viewed_month_key=None):
        """
        Get previous month's total and name for comparison, with trend indicator.
        
        Args:
            prev_month_data_folder: Folder path for previous month's data
            current_month_total: Current/viewed month's total for comparison
            viewed_month_key: Month being viewed (YYYY-MM), calculates contextual previous month if provided
            
        Returns:
            (prev_total_formatted, prev_month_name, comparison_indicator)
            
            comparison_indicator dict: 'symbol' (▲/▼/≈), 'percentage', 'direction', 'color'
        """
        # Determine which month's previous month to calculate
        if viewed_month_key:
            # Archive mode: Calculate previous month relative to viewed month
            viewed_date = datetime.strptime(viewed_month_key, '%Y-%m')
            prev_month_date = viewed_date.replace(day=1) - timedelta(days=1)
        else:
            # Normal mode: Calculate previous month relative to current month
            prev_month_date = datetime.now().replace(day=1) - timedelta(days=1)
        
        prev_month_key = prev_month_date.strftime('%Y-%m')
        prev_month_name = prev_month_date.strftime('%B %Y')  # e.g., "September 2025"
        
        # Check folders in priority order: test_data (dev) -> expense_data (production) -> root (legacy)
        test_data_folder = os.path.join("test_data", f"data_{prev_month_key}")
        expense_data_folder = os.path.join("expense_data", f"data_{prev_month_key}")
        root_data_folder = f"data_{prev_month_key}"
        
        # Determine which folder to use (priority: test_data > expense_data > root)
        if os.path.exists(test_data_folder):
            prev_data_folder = test_data_folder
        elif os.path.exists(expense_data_folder):
            prev_data_folder = expense_data_folder
        else:
            prev_data_folder = root_data_folder
        
        # Check if we have previous month data file
        prev_expenses_file = os.path.join(prev_data_folder, 'expenses.json')
        
        prev_total = 0.0
        if os.path.exists(prev_expenses_file):
            try:
                with open(prev_expenses_file, 'r') as f:
                    data = json.load(f)
                    # Handle both old format (list) and new format (dict with 'expenses' key)
                    if isinstance(data, list):
                        prev_expenses = data
                    elif isinstance(data, dict):
                        prev_expenses = data.get('expenses', [])
                    else:
                        prev_expenses = []
                    
                    prev_total = sum(e['amount'] for e in prev_expenses)
            except Exception:
                # If error reading file, use 0.00
                prev_total = 0.0
        
        # Calculate comparison indicator if current month total provided
        comparison_indicator = None
        if current_month_total is not None and prev_total > 0:
            difference = current_month_total - prev_total
            percentage = abs((difference / prev_total) * 100)
            
            # Determine direction and styling
            if percentage < 5.0:
                # Similar (less than 5% change)
                comparison_indicator = {
                    'symbol': '≈',
                    'percentage': percentage,
                    'direction': 'similar',
                    'color': '#999999'  # Light gray
                }
            elif difference > 0:
                # Increase (spending more)
                comparison_indicator = {
                    'symbol': '▲',
                    'percentage': percentage,
                    'direction': 'increase',
                    'color': '#C00000'  # Darker red (more prominent warning)
                }
            else:
                # Decrease (spending less)
                comparison_indicator = {
                    'symbol': '▼',
                    'percentage': percentage,
                    'direction': 'decrease',
                    'color': '#666666'  # Neutral gray
                }
        
        return f"${prev_total:.2f}", prev_month_name, comparison_indicator
    
    @staticmethod
    def calculate_median_expense(expenses, current_date=None):
        """
        Calculate median expense amount (typical expense size).
        
        Args:
            expenses: List of expense dictionaries
            current_date: Date to calculate from, defaults to today
            
        Returns:
            (median_amount, count)
        """
        if current_date is None:
            current_date = datetime.now()
        
        # Filter out future expenses using helper method
        past_expenses = ExpenseAnalytics._filter_past_expenses(expenses, current_date)
        
        if not past_expenses:
            return 0.0, 0
        
        # Get all expense amounts and sort them
        amounts = sorted([e['amount'] for e in past_expenses])
        count = len(amounts)
        
        # Calculate median
        if count % 2 == 0:
            # Even number: average of two middle values
            median = (amounts[count // 2 - 1] + amounts[count // 2]) / 2
        else:
            # Odd number: middle value
            median = amounts[count // 2]
        
        return median, count
    
    @staticmethod
    def calculate_largest_expense(expenses, current_date=None):
        """
        Get the largest expense amount and description.
        
        Args:
            expenses: List of expense dictionaries
            current_date: Date to calculate from, defaults to today
            
        Returns:
            (amount, description)
        """
        if current_date is None:
            current_date = datetime.now()
        
        # Filter out future expenses using helper method
        past_expenses = ExpenseAnalytics._filter_past_expenses(expenses, current_date)
        
        if not past_expenses:
            return 0.0, "No expenses"
        
        # Find the largest expense
        largest = max(past_expenses, key=lambda e: e['amount'])
        
        return largest['amount'], largest['description']

