"""Page navigation and visibility management for multi-page interface."""


class PageManager:
    """Manages page navigation and visibility for multi-page interfaces."""
    
    # Page identifiers
    PAGE_MAIN = "main"
    PAGE_EXPENSE_LIST = "expense_list"
    
    def __init__(self):
        """Initialize the page manager"""
        self.current_page = self.PAGE_MAIN
        self.pages = {}  # {page_id: frame_widget}
        
    def register_page(self, page_id, frame):
        """Register a page frame with the manager."""
        self.pages[page_id] = frame
        
    def show_main_page(self, status_manager=None):
        """Show the main dashboard page."""
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
        """Show the expense list page."""
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
        """Get the currently visible page ID."""
        return self.current_page
    
    def is_on_page(self, page_id):
        """Check if currently on a specific page."""
        return self.current_page == page_id

