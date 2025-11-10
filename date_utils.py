"""Date utility functions. All dates use ISO 8601 format (YYYY-MM-DD) internally."""

from datetime import datetime, timedelta
from calendar import monthrange
from typing import Optional, Tuple


class DateUtils:
    """Static utility methods for date operations"""
    
    # Standard date format used throughout the application
    DATE_FORMAT = "%Y-%m-%d"
    MONTH_FORMAT = "%Y-%m"
    DISPLAY_FORMAT = "%B %Y"  # e.g., "October 2025"
    
    @staticmethod
    def parse_date(date_str: str) -> Optional[datetime]:
        """Parse YYYY-MM-DD date string to datetime. Returns None if invalid."""
        try:
            return datetime.strptime(date_str, DateUtils.DATE_FORMAT)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def is_valid_date(date_str: str) -> bool:
        """Check if date string is valid YYYY-MM-DD format."""
        return DateUtils.parse_date(date_str) is not None
    
    @staticmethod
    def format_date(dt: datetime) -> str:
        """Format datetime as YYYY-MM-DD string."""
        return dt.strftime(DateUtils.DATE_FORMAT)
    
    @staticmethod
    def get_current_date_str() -> str:
        """Get current date as YYYY-MM-DD string."""
        return datetime.now().strftime(DateUtils.DATE_FORMAT)
    
    @staticmethod
    def get_current_month_str() -> str:
        """Get current month as YYYY-MM string."""
        return datetime.now().strftime(DateUtils.MONTH_FORMAT)
    
    @staticmethod
    def get_month_folder_name(dt: datetime) -> str:
        """Get data folder name for date (format: "data_YYYY-MM")."""
        return f"data_{dt.strftime(DateUtils.MONTH_FORMAT)}"
    
    @staticmethod
    def get_month_folder_from_string(date_str: str) -> Optional[str]:
        """Get data folder name from YYYY-MM-DD date string. Returns None if invalid."""
        dt = DateUtils.parse_date(date_str)
        if dt:
            return DateUtils.get_month_folder_name(dt)
        return None
    
    @staticmethod
    def parse_month_folder_name(folder_name: str) -> Optional[Tuple[int, int]]:
        """Parse "data_YYYY-MM" folder name to (year, month) tuple. Returns None if invalid."""
        try:
            if folder_name.startswith("data_"):
                month_str = folder_name[5:]  # Remove "data_" prefix
                year, month = map(int, month_str.split('-'))
                if 1 <= month <= 12:
                    return (year, month)
        except (ValueError, AttributeError):
            pass
        return None
    
    @staticmethod
    def get_previous_month(dt: datetime) -> datetime:
        """Get first day of previous month from given date."""
        # Go to first day of current month, then subtract one day
        first_of_month = dt.replace(day=1)
        last_of_prev_month = first_of_month - timedelta(days=1)
        return last_of_prev_month.replace(day=1)
    
    @staticmethod
    def get_next_month(dt: datetime) -> datetime:
        """Get first day of next month from given date."""
        # Get the last day of current month, then add one day
        last_day = monthrange(dt.year, dt.month)[1]
        last_of_month = dt.replace(day=last_day)
        first_of_next = last_of_month + timedelta(days=1)
        return first_of_next
    
    @staticmethod
    def format_month_display(dt: datetime) -> str:
        """Format datetime as display-friendly month name (e.g., "October 2025")."""
        return dt.strftime(DateUtils.DISPLAY_FORMAT)
    
    @staticmethod
    def get_month_name(month: int) -> str:
        """Get full month name from month number (1-12)."""
        try:
            dt = datetime(2000, month, 1)  # Use year 2000 as dummy
            return dt.strftime("%B")
        except ValueError:
            return ""
    
    @staticmethod
    def get_first_day_of_month(year: int, month: int) -> str:
        """Get first day of month as YYYY-MM-DD string."""
        dt = datetime(year, month, 1)
        return DateUtils.format_date(dt)
    
    @staticmethod
    def get_last_day_of_month(year: int, month: int) -> str:
        """Get last day of month as YYYY-MM-DD string."""
        last_day = monthrange(year, month)[1]
        dt = datetime(year, month, last_day)
        return DateUtils.format_date(dt)
    
    @staticmethod
    def extract_year_month(date_str: str) -> Optional[Tuple[int, int]]:
        """Extract (year, month) tuple from YYYY-MM-DD date string. Returns None if invalid."""
        dt = DateUtils.parse_date(date_str)
        if dt:
            return (dt.year, dt.month)
        return None

