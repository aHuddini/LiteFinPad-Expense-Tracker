"""
Page Manager Module for LiteFinPad v3.5.3+
============================================

Manages page navigation and visibility for the application's multi-page interface.

Features:
- Clean page switching abstraction
- Automatic frame visibility management
- Status bar visibility control per page
- Page-specific update triggers
- Simple state tracking

Usage:
    page_manager = PageManager()
    page_manager.register_page("main", main_frame)
    page_manager.register_page("expense_list", expense_list_frame)
    
    # Switch pages
    page_manager.show_page("expense_list", status_manager, table_manager, expense_tracker)
    
    # Get current page
    current = page_manager.current_page  # "expense_list"
"""


class PageManager:
    """
    Manages page navigation and visibility for multi-page interfaces.
    
    Handles:
    - Page frame visibility (show/hide)
    - Status bar visibility per page
    - Page-specific callbacks and updates
    - Current page state tracking
    """
    
    # Page identifiers
    PAGE_MAIN = "main"
    PAGE_EXPENSE_LIST = "expense_list"
    
    def __init__(self):
        """Initialize the page manager"""
        self.current_page = self.PAGE_MAIN
        self.pages = {}  # {page_id: frame_widget}
        
    def register_page(self, page_id, frame):
        """
        Register a page frame with the manager.
        
        Args:
            page_id (str): Unique identifier for the page (e.g., "main", "expense_list")
            frame (tk.Frame): The frame widget for this page
        """
        self.pages[page_id] = frame
        
    def show_main_page(self, status_manager=None):
        """
        Show the main dashboard page.
        
        Args:
            status_manager (StatusBarManager, optional): Status bar manager to hide
        """
        self.current_page = self.PAGE_MAIN
        
        # Hide all other pages
        for page_id, frame in self.pages.items():
            if page_id != self.PAGE_MAIN:
                frame.grid_remove()
        
        # Show main page
        if self.PAGE_MAIN in self.pages:
            self.pages[self.PAGE_MAIN].grid()
        
        # Hide status bar on main page
        if status_manager:
            status_manager.set_visible(False)
    
    def show_expense_list_page(self, status_manager=None, table_manager=None, 
                                expense_tracker=None, update_metrics_callback=None):
        """
        Show the expense list page.
        
        Args:
            status_manager (StatusBarManager, optional): Status bar manager to show
            table_manager (ExpenseTable, optional): Table manager to refresh expenses
            expense_tracker (ExpenseTracker, optional): Expense tracker for data
            update_metrics_callback (callable, optional): Callback to update metrics
        """
        self.current_page = self.PAGE_EXPENSE_LIST
        
        # Hide all other pages
        for page_id, frame in self.pages.items():
            if page_id != self.PAGE_EXPENSE_LIST:
                frame.grid_remove()
        
        # Show expense list page
        if self.PAGE_EXPENSE_LIST in self.pages:
            self.pages[self.PAGE_EXPENSE_LIST].grid()
        
        # Show status bar for expense list page
        if status_manager:
            status_manager.set_visible(True)
        
        # Update metrics
        if update_metrics_callback:
            update_metrics_callback()
        
        # Load expenses into table
        if table_manager and expense_tracker:
            if hasattr(table_manager, 'load_expenses'):
                table_manager.load_expenses(expense_tracker.expenses)
    
    def get_current_page(self):
        """
        Get the currently visible page ID.
        
        Returns:
            str: Current page identifier
        """
        return self.current_page
    
    def is_on_page(self, page_id):
        """
        Check if currently on a specific page.
        
        Args:
            page_id (str): Page identifier to check
            
        Returns:
            bool: True if on the specified page
        """
        return self.current_page == page_id

