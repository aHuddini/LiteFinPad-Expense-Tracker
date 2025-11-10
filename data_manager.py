"""Expense data persistence operations (loading/saving). All functions are pure with no UI dependencies."""

import json
import os
from datetime import datetime
from error_logger import log_error, log_info, log_warning, log_data_load
from date_utils import DateUtils
import config


class ExpenseDataManager:
    """Pure data manager for expense persistence. All methods are static."""
    
    @staticmethod
    def load_expenses(expenses_file, data_folder, current_month):
        """Load expense data from JSON file. Returns (expenses_list, monthly_total)."""
        log_info(f"Loading data from: {expenses_file}")
        log_info(f"Data folder: {data_folder}")
        log_info(f"Current month: {current_month}")
        
        if os.path.exists(expenses_file):
            try:
                with open(expenses_file, 'r') as f:
                    data = json.load(f)
                    expenses = data.get('expenses', [])
                    
                    monthly_total = ExpenseDataManager.calculate_monthly_total(expenses)
                    
                    log_data_load("expenses", len(expenses), expenses_file)
                    log_info(f"Monthly total calculated: ${monthly_total:.2f}")
                    
                    return expenses, monthly_total
                    
            except FileNotFoundError:
                log_warning(f"Expenses file not found (deleted after check): {expenses_file}")
                return [], 0.0
            except json.JSONDecodeError as e:
                log_error(f"Invalid JSON in {expenses_file}: {e}", e)
                print(f"{config.Messages.ERROR_LOADING_DATA}: Invalid JSON format - {e}")
                return [], 0.0
            except PermissionError as e:
                log_error(f"Permission denied reading {expenses_file}: {e}", e)
                print(f"{config.Messages.ERROR_LOADING_DATA}: Permission denied - {e}")
                return [], 0.0
            except OSError as e:
                log_error(f"OS error reading {expenses_file}: {e}", e)
                print(f"{config.Messages.ERROR_LOADING_DATA}: System error - {e}")
                return [], 0.0
            except Exception as e:
                log_error(f"Unexpected error loading {expenses_file}: {e}", e)
                print(f"{config.Messages.ERROR_LOADING_DATA}: {e}")
                return [], 0.0
        else:
            log_warning(f"Expenses file not found: {expenses_file}")
            log_info(f"Current working directory: {os.getcwd()}")
            log_info(f"Files in current directory: {os.listdir('.')[:10]}")
            return [], 0.0
    
    @staticmethod
    def save_expenses(data_folder, expenses_file, expenses, monthly_total):
        """Save expense data to JSON file. Returns True if successful."""
        os.makedirs(data_folder, exist_ok=True)
        
        data = {
            'expenses': expenses,
            'monthly_total': monthly_total
        }
        
        try:
            with open(expenses_file, 'w') as f:
                json.dump(data, f, indent=2)
            log_info(f"Data saved: {len(expenses)} expenses to {expenses_file}")
            return True
            
        except PermissionError as e:
            log_error(f"Permission denied writing to {expenses_file}: {e}", e)
            print(f"{config.Messages.ERROR_SAVING_DATA}: Permission denied - {e}")
            return False
        except OSError as e:
            log_error(f"OS error writing to {expenses_file}: {e}", e)
            print(f"{config.Messages.ERROR_SAVING_DATA}: System error - {e}")
            return False
        except Exception as e:
            log_error(f"Unexpected error saving to {expenses_file}: {e}", e)
            print(f"{config.Messages.ERROR_SAVING_DATA}: {e}")
            return False
    
    @staticmethod
    def calculate_monthly_total(expenses):
        """Calculate monthly total from expenses, excluding future expenses."""
        today = datetime.now().date()
        
        total = sum(
            expense['amount'] for expense in expenses
            if (dt := DateUtils.parse_date(expense['date'])) and dt.date() <= today
        )
        
        return total

