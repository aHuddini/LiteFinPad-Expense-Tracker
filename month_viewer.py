"""Month navigation and archive mode management."""

import os
from datetime import datetime
from typing import List, Dict, Tuple
import tkinter as tk


class MonthViewer:
    """Manages month navigation and archive mode functionality."""
    
    def __init__(self, data_directory: str = "."):
        """Initialize MonthViewer with data directory."""
        self.data_directory = data_directory
        self.actual_month = datetime.now().strftime("%Y-%m")
        self.viewed_month = self.actual_month
        self.viewing_mode = "current"  # "current" or "archive"
    
    def get_available_months(self) -> List[str]:
        """Scan data directory for available months (YYYY-MM format, sorted descending)."""
        available_months = []
        
        try:
            # Look for data_YYYY-MM folders
            for item in os.listdir(self.data_directory):
                if item.startswith("data_") and os.path.isdir(os.path.join(self.data_directory, item)):
                    # Extract YYYY-MM from folder name
                    month_key = item.replace("data_", "")
                    
                    # Validate format
                    try:
                        datetime.strptime(month_key, "%Y-%m")
                        
                        # Check if expenses.json exists
                        expenses_file = os.path.join(self.data_directory, item, "expenses.json")
                        if os.path.exists(expenses_file):
                            available_months.append(month_key)
                    except ValueError:
                        continue
        except Exception as e:
            print(f"Error scanning for available months: {e}")
        
        if self.actual_month not in available_months:
            available_months.append(self.actual_month)
        
        available_months.sort(reverse=True)
        return available_months
    
    def group_months_by_year(self, months: List[str]) -> Dict[str, List[str]]:
        """Group month keys by year."""
        months_by_year = {}
        
        for month_key in months:
            year = month_key.split('-')[0]
            if year not in months_by_year:
                months_by_year[year] = []
            months_by_year[year].append(month_key)
        
        for year in months_by_year:
            months_by_year[year].sort(reverse=True)
        
        return months_by_year
    
    def create_navigation_menu(self, root_widget: tk.Widget, on_select_callback) -> tk.Menu:
        """Create hierarchical navigation menu (Year > Months)."""
        menu = tk.Menu(root_widget, tearoff=0)
        
        available_months = self.get_available_months()
        
        if not available_months:
            menu.add_command(label="No archived months", state='disabled')
            return menu
        
        months_by_year = self.group_months_by_year(available_months)
        
        for year in sorted(months_by_year.keys(), reverse=True):
            year_menu = tk.Menu(menu, tearoff=0)
            
            for month_key in months_by_year[year]:
                month_obj = datetime.strptime(month_key, "%Y-%m")
                month_name = month_obj.strftime('%B')
                
                is_current = month_key == self.actual_month
                is_selected = month_key == self.viewed_month
                
                label = f"{month_name}"
                if is_current:
                    label += " (Current)"
                if is_selected:
                    label = f"✓ {label}"
                
                year_menu.add_command(
                    label=label,
                    command=lambda m=month_key: on_select_callback(m)
                )
            
            menu.add_cascade(label=year, menu=year_menu)
        
        return menu
    
    def switch_to_month(self, month_key: str) -> Tuple[str, str]:
        """Switch to a different month (YYYY-MM format). Returns (viewed_month, viewing_mode)."""
        self.viewed_month = month_key
        self.viewing_mode = "current" if month_key == self.actual_month else "archive"
        return self.viewed_month, self.viewing_mode
    
    def is_archive_mode(self) -> bool:
        """Check if currently in archive mode."""
        return self.viewing_mode == "archive"
    
    def is_current_mode(self) -> bool:
        """Check if currently in current mode."""
        return self.viewing_mode == "current"
    
    def get_data_folder(self, month_key: str = None) -> str:
        """Get data folder path for a given month (defaults to viewed_month)."""
        if month_key is None:
            month_key = self.viewed_month
        
        return os.path.join(self.data_directory, f"data_{month_key}")
    
    def get_expenses_file(self, month_key: str = None) -> str:
        """Get expenses.json file path for a given month (defaults to viewed_month)."""
        return os.path.join(self.get_data_folder(month_key), "expenses.json")
    
    def get_calculations_file(self, month_key: str = None) -> str:
        """Get calculations.json file path for a given month (defaults to viewed_month)."""
        return os.path.join(self.get_data_folder(month_key), "calculations.json")
    
    def format_month_display(self, month_key: str = None, include_archive_indicator: bool = True) -> str:
        """Format month for display in UI. Adds archive indicator if requested."""
        if month_key is None:
            month_key = self.viewed_month
        
        month_obj = datetime.strptime(month_key, "%Y-%m")
        month_text = month_obj.strftime('%B %Y')
        
        if include_archive_indicator and month_key != self.actual_month:
            return f"📚 {month_text} (Archive)"
        
        return month_text

