"""
Data Loading Utilities

Handles loading expense data from files and preparing it for AI processing.
"""

import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from error_logger import log_info, log_warning, log_debug
from data_manager import ExpenseDataManager


class DataLoader:
    """Handles expense data loading operations."""
    
    @staticmethod
    def load_month_data(month_key: str, use_test_data: bool = True) -> Tuple[List[Dict], float]:
        """
        Load expense data for a specific month.
        Checks test_data folder first, then regular data folders.
        
        Args:
            month_key: Month key in YYYY-MM format
            use_test_data: If True, check test_data folder first (default: True)
            
        Returns:
            Tuple of (expenses list, total amount)
        """
        # Try test_data folder first if enabled
        if use_test_data:
            test_data_folder = os.path.join("test_data", f"data_{month_key}")
            test_expenses_file = os.path.join(test_data_folder, "expenses.json")
            
            if os.path.exists(test_expenses_file):
                try:
                    expenses, total = ExpenseDataManager.load_expenses(
                        test_expenses_file,
                        test_data_folder,
                        month_key
                    )
                    log_debug(f"[DataLoader] Loaded {month_key} from test_data: {len(expenses)} expenses, ${total:.2f}")
                    return expenses, total
                except Exception as e:
                    log_warning(f"[DataLoader] Failed to load {month_key} from test_data: {e}")
        
        # Fall back to expense_data folder (production), then root (legacy)
        expense_data_folder = os.path.join("expense_data", f"data_{month_key}")
        expense_data_file = os.path.join(expense_data_folder, "expenses.json")
        
        if os.path.exists(expense_data_file):
            try:
                expenses, total = ExpenseDataManager.load_expenses(
                    expense_data_file,
                    expense_data_folder,
                    month_key
                )
                log_debug(f"[DataLoader] Loaded {month_key} from expense_data: {len(expenses)} expenses, ${total:.2f}")
                return expenses, total
            except Exception as e:
                log_warning(f"[DataLoader] Failed to load {month_key} from expense_data: {e}")
        
        # Final fallback to root (legacy support)
        data_folder = f"data_{month_key}"
        expenses_file = os.path.join(data_folder, "expenses.json")
        
        if not os.path.exists(expenses_file):
            log_warning(f"[DataLoader] No expense data found for {month_key}")
            return [], 0.0
        
        try:
            expenses, total = ExpenseDataManager.load_expenses(
                expenses_file,
                data_folder,
                month_key
            )
            log_debug(f"[DataLoader] Loaded {month_key} from root (legacy): {len(expenses)} expenses, ${total:.2f}")
            return expenses, total
        except Exception as e:
            log_warning(f"[DataLoader] Failed to load {month_key}: {e}")
            return [], 0.0
    
    @staticmethod
    def load_all_available_months(current_month_key: Optional[str] = None, use_test_data: bool = True) -> Dict[str, Tuple[List[Dict], float]]:
        """
        Load all available months from data folders.
        Checks test_data folder first, then regular data folders.
        Only includes months up to and including the current month (excludes future months).
        
        Args:
            current_month_key: Current month key (YYYY-MM) to filter out future months
            use_test_data: If True, check test_data folder first (default: True)
            
        Returns:
            Dict of {month_key: (expenses, total)} for available months
        """
        available_months = {}
        
        # Get current month for filtering future months
        if current_month_key:
            try:
                current_year, current_month = map(int, current_month_key.split('-'))
            except (ValueError, AttributeError):
                # Fallback to system date
                now = datetime.now()
                current_year, current_month = now.year, now.month
        else:
            # Use system date
            now = datetime.now()
            current_year, current_month = now.year, now.month
        
        log_debug(f"[DataLoader] Filtering months: Only including months up to {current_year}-{current_month:02d}")
        
        # Scan test_data folder first if enabled
        if use_test_data:
            test_data_dir = "test_data"
            if os.path.exists(test_data_dir):
                try:
                    for item in os.listdir(test_data_dir):
                        if item.startswith('data_') and os.path.isdir(os.path.join(test_data_dir, item)):
                            month_key = item.replace('data_', '')
                            
                            # Validate format
                            try:
                                month_year, month_month = map(int, month_key.split('-'))
                                
                                # Filter out future months
                                if month_year > current_year or (month_year == current_year and month_month > current_month):
                                    log_debug(f"[DataLoader] Skipping future month in test_data: {month_key}")
                                    continue
                                
                                # Load month data (use_test_data=False to avoid recursion)
                                expenses, total = DataLoader.load_month_data(month_key, use_test_data=True)
                                if expenses:  # Only add if we have data
                                    available_months[month_key] = (expenses, total)
                                    log_debug(f"[DataLoader] Loaded {month_key} from test_data")
                            except (ValueError, Exception) as e:
                                log_warning(f"[DataLoader] Failed to process {month_key} from test_data: {e}")
                                continue
                except Exception as e:
                    log_warning(f"[DataLoader] Error scanning test_data folder: {e}")
        
        # Scan expense_data folder (production) if enabled
        if use_test_data:
            expense_data_dir = "expense_data"
            if os.path.exists(expense_data_dir):
                try:
                    for item in os.listdir(expense_data_dir):
                        if item.startswith('data_') and os.path.isdir(os.path.join(expense_data_dir, item)):
                            month_key = item.replace('data_', '')
                            
                            # Skip if already loaded from test_data
                            if month_key in available_months:
                                continue
                            
                            # Validate format
                            try:
                                month_year, month_month = map(int, month_key.split('-'))
                                
                                # Filter out future months
                                if month_year > current_year or (month_year == current_year and month_month > current_month):
                                    log_debug(f"[DataLoader] Skipping future month in expense_data: {month_key}")
                                    continue
                                
                                # Load month data (use_test_data=False to avoid recursion)
                                expenses, total = DataLoader.load_month_data(month_key, use_test_data=False)
                                if expenses:  # Only add if we have data
                                    available_months[month_key] = (expenses, total)
                                    log_debug(f"[DataLoader] Loaded {month_key} from expense_data")
                            except (ValueError, Exception) as e:
                                log_warning(f"[DataLoader] Failed to process {month_key} from expense_data: {e}")
                                continue
                except Exception as e:
                    log_warning(f"[DataLoader] Error scanning expense_data folder: {e}")
        
        # Scan root directory (legacy support, only if not already loaded)
        try:
            for item in os.listdir('.'):
                if item.startswith('data_') and os.path.isdir(item):
                    month_key = item.replace('data_', '')
                    
                    # Skip if already loaded from test_data or expense_data
                    if month_key in available_months:
                        continue
                    
                    # Validate format
                    try:
                        month_year, month_month = map(int, month_key.split('-'))
                        
                        # Filter out future months
                        if month_year > current_year or (month_year == current_year and month_month > current_month):
                            log_debug(f"[DataLoader] Skipping future month: {month_key} (current: {current_year}-{current_month:02d})")
                            continue
                        
                        # Load month data
                        expenses, total = DataLoader.load_month_data(month_key, use_test_data=False)
                        if expenses:  # Only add if we have data
                            available_months[month_key] = (expenses, total)
                    except (ValueError, Exception) as e:
                        log_warning(f"[DataLoader] Failed to process {month_key}: {e}")
                        continue
        except Exception as e:
            log_warning(f"[DataLoader] Error scanning for months: {e}")
        
        return available_months

