import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import calendar
import webbrowser
import config
from dialog_helpers import DialogHelper
from analytics import ExpenseAnalytics
from widgets import CollapsibleDateCombobox
from status_bar_manager import StatusBarManager
from page_manager import PageManager
from quick_add_helper import QuickAddHelper
from archive_mode_manager import ArchiveModeManager
from tooltip_manager import TooltipManager
from dashboard_page_builder import DashboardPageBuilder
from expense_list_page_builder import ExpenseListPageBuilder
from validation import InputValidation


class LiteFinPadGUI:
    def __init__(self, root, expense_tracker):
        self.root = root
        self.expense_tracker = expense_tracker
        self.setup_window()
        self.setup_styles()
        
        # Initialize managers
        self.status_manager = StatusBarManager(self.root)
        self.page_manager = PageManager()
        self.tooltip_manager = TooltipManager()
        
        self.create_widgets()
        
    def setup_window(self):
        """Configure the main window with proper sizing and anti-flicker optimizations"""
        # Read version dynamically from version.txt
        try:
            with open('version.txt', 'r') as f:
                version = f.read().strip()
        except:
            version = "3.5.3"  # Fallback version
        
        self.root.title(f"LiteFinPad v{version} - Monthly Expense Tracker")
        self.root.geometry(f"{config.Window.WIDTH}x{config.Window.HEIGHT}")  # Increased height for inline Quick Add section
        self.root.resizable(False, False)
        self.root.configure(bg=config.Colors.BG_LIGHT_GRAY)
        
        # Anti-flicker optimizations
        self.root.update_idletasks()  # Force initial rendering
        self.root.update()  # Complete any pending updates
        
    def setup_styles(self):
        """Configure modern Windows 11 styling"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # === NORMAL MODE STYLES ===
        # Frame backgrounds
        self.style.configure('TFrame', background=config.Colors.BG_LIGHT_GRAY)
        self.style.configure('TLabelframe', background=config.Colors.BG_LIGHT_GRAY)
        self.style.configure('TLabelframe.Label', background=config.Colors.BG_LIGHT_GRAY)
        
        # Default TLabel - must explicitly match frame background for labels without specific styles
        self.style.configure('TLabel', background=config.Colors.BG_LIGHT_GRAY)
        
        # Specific label styles (explicit background to match frames)
        self.style.configure('Title.TLabel', font=config.Fonts.TITLE, foreground=config.Colors.TEXT_BLACK, background=config.Colors.BG_LIGHT_GRAY)
        self.style.configure('Month.TLabel', font=config.Fonts.SUBTITLE, foreground=config.Colors.TEXT_BLACK, background=config.Colors.BG_LIGHT_GRAY)
        self.style.configure('Count.TLabel', font=config.get_font(config.Fonts.SIZE_LARGE), foreground=config.Colors.TEXT_BLACK, background=config.Colors.BG_LIGHT_GRAY)
        self.style.configure('Total.TLabel', font=config.Fonts.HERO_TOTAL, foreground=config.Colors.GREEN_PRIMARY, background=config.Colors.BG_LIGHT_GRAY)
        self.style.configure('Rate.TLabel', font=config.get_font(config.Fonts.SIZE_MEDIUM), foreground=config.Colors.TEXT_GRAY_DARK, background=config.Colors.BG_LIGHT_GRAY)
        self.style.configure('Analytics.TLabel', font=config.get_font(config.Fonts.SIZE_NORMAL), foreground=config.Colors.TEXT_GRAY_MEDIUM, background=config.Colors.BG_LIGHT_GRAY)
        self.style.configure('Trend.TLabel', font=config.get_font(config.Fonts.SIZE_NORMAL), foreground=config.Colors.PURPLE_PRIMARY, background=config.Colors.BG_LIGHT_GRAY)
        
        # === ARCHIVE MODE STYLES ===
        self.style.configure('Archive.TFrame', background=config.Colors.BG_ARCHIVE_TINT)
        self.style.configure('Archive.TLabelframe', background=config.Colors.BG_ARCHIVE_TINT)
        self.style.configure('Archive.TLabelframe.Label', background=config.Colors.BG_ARCHIVE_TINT)
        self.style.configure('Archive.TLabel', background=config.Colors.BG_ARCHIVE_TINT)
        
        # Archive label styles
        self.style.configure('Archive.Title.TLabel', font=config.Fonts.TITLE, foreground=config.Colors.TEXT_BLACK, background=config.Colors.BG_ARCHIVE_TINT)
        self.style.configure('Archive.Month.TLabel', font=config.Fonts.SUBTITLE, foreground=config.Colors.TEXT_BLACK, background=config.Colors.BG_ARCHIVE_TINT)
        self.style.configure('Archive.Count.TLabel', font=config.get_font(config.Fonts.SIZE_LARGE), foreground=config.Colors.TEXT_BLACK, background=config.Colors.BG_ARCHIVE_TINT)
        self.style.configure('Archive.Total.TLabel', font=config.Fonts.HERO_TOTAL, foreground=config.Colors.PURPLE_ARCHIVE, background=config.Colors.BG_ARCHIVE_TINT)
        self.style.configure('Archive.Rate.TLabel', font=config.get_font(config.Fonts.SIZE_MEDIUM), foreground=config.Colors.TEXT_GRAY_DARK, background=config.Colors.BG_ARCHIVE_TINT)
        self.style.configure('Archive.Analytics.TLabel', font=config.get_font(config.Fonts.SIZE_NORMAL), foreground=config.Colors.TEXT_GRAY_MEDIUM, background=config.Colors.BG_ARCHIVE_TINT)
        self.style.configure('Archive.Trend.TLabel', font=config.get_font(config.Fonts.SIZE_NORMAL), foreground=config.Colors.PURPLE_PRIMARY, background=config.Colors.BG_ARCHIVE_TINT)
        
        # Button styles
        self.style.configure('Modern.TButton', font=config.Fonts.BUTTON, anchor='center')
        
        # Configure Add Expense button style with green accent and proper centering
        self.style.configure('AddExpense.TButton', font=config.Fonts.BUTTON, 
                           background=config.Colors.GREEN_PRIMARY, foreground='#ffffff',
                           anchor='center')
        self.style.map('AddExpense.TButton',
                      background=[('active', config.Colors.GREEN_HOVER), ('pressed', config.Colors.GREEN_PRESSED), ('disabled', '#cccccc')],
                      foreground=[('active', '#ffffff'), ('pressed', '#ffffff'), ('disabled', '#666666')])
        
        # Configure toolbutton style for crisp emoji rendering
        self.style.configure('Toolbutton', font=config.get_font(config.Fonts.SIZE_MEDIUM))
        self.style.map('Toolbutton', 
                      background=[('active', config.Colors.BUTTON_ACTIVE_BG), ('pressed', config.Colors.BUTTON_PRESSED_BG)],
                      relief=[('pressed', 'sunken'), ('!pressed', 'flat')])
        
    def create_widgets(self):
        """Create all GUI widgets with proper layout"""
        # Main container frame - this will hold both pages
        self.main_container = ttk.Frame(self.root)
        self.main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_container.columnconfigure(0, weight=1)
        self.main_container.rowconfigure(0, weight=1)
        
        # Create main dashboard page
        self.create_main_page()
        
        # Create expense list page
        self.create_expense_list_page()
        
        # Register pages with page manager
        self.page_manager.register_page(PageManager.PAGE_MAIN, self.main_frame)
        self.page_manager.register_page(PageManager.PAGE_EXPENSE_LIST, self.expense_list_frame)
        
        # Initialize archive mode manager (after all widgets are created)
        self.archive_mode_manager = ArchiveModeManager(
            root=self.root,
            expense_tracker=self.expense_tracker,
            page_manager=self.page_manager,
            main_frame=self.main_frame,
            expense_list_frame=self.expense_list_frame,
            month_label=self.month_label,
            add_expense_btn=self.add_expense_btn,
            quick_add_helper=self.quick_add_helper if hasattr(self, 'quick_add_helper') else None,
            table_manager=self.table_manager if hasattr(self, 'table_manager') else None,
            tooltip_creator=self.tooltip_manager.create,
            update_display_callback=self.update_display,
            update_metrics_callback=self.update_expense_metrics
        )
        
        # Create status bar (at bottom of window)
        status_bar_frame = self.status_manager.create_ui()
        # Grid it but hide initially (shown only on expense list page)
        status_bar_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.status_manager.set_visible(False)
        
    def create_main_page(self):
        """Create the main dashboard page"""
        # Main frame with standard padding (status bar hidden on main page)
        self.main_frame = ttk.Frame(self.main_container, padding="15 15 15 2")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(7, weight=1)  # Allow Recent Expenses to expand
        
        # Build dashboard using DashboardPageBuilder
        callbacks = {
            'show_month_navigation_menu': self.show_month_navigation_menu,
            'show_about_dialog': self.show_about_dialog,
            'toggle_stay_on_top_visual': self.toggle_stay_on_top_visual,
            'get_context_date': self._get_context_date,
            'is_archive_mode': self._is_archive_mode
        }
        
        builder = DashboardPageBuilder(
            self.main_frame,
            self.expense_tracker,
            callbacks,
            self.tooltip_manager
        )
        
        # Build all sections and store widget references
        widgets = builder.build_all()
        
        # Store widget references as instance attributes for updates
        self.month_label = widgets['month_label']
        self.about_label = widgets['about_label']
        self.stay_on_top_var = widgets['stay_on_top_var']
        self.stay_on_top_label = widgets['stay_on_top_label']
        self.minimize_button = widgets['minimize_button']
        self.total_label = widgets['total_label']
        self.count_label = widgets['count_label']
        self.day_progress_label = widgets['day_progress_label']
        self.week_progress_label = widgets['week_progress_label']
        self.daily_avg_label = widgets['daily_avg_label']
        self.weekly_avg_label = widgets['weekly_avg_label']
        self.pace_label = widgets['pace_label']
        self.trend_label = widgets['trend_label']
        self.comparison_label = widgets['comparison_label']
        self.trend_context_label = widgets['trend_context_label']
        self.recent_expense_1 = widgets['recent_expense_1']
        self.recent_expense_2 = widgets['recent_expense_2']
        self.add_expense_btn = widgets['add_expense_btn']
        
        # Update recent expenses display
        self.update_recent_expenses()
        
    
    def toggle_stay_on_top_visual(self):
        """Toggle stay on top with visual feedback - SIMPLE version"""
        # Toggle the state
        current_state = self.stay_on_top_var.get()
        new_state = not current_state
        self.stay_on_top_var.set(new_state)
        
        # Get the header frame's background color for OFF state
        header_bg = self.style.lookup('TFrame', 'background')
        
        # Update label appearance - simple background color change
        if new_state:
            # ON - gray background
            self.stay_on_top_label.config(background=config.Colors.BG_BUTTON_DISABLED)
            # Update tooltip
            self.tooltip_manager.update(self.stay_on_top_label, "Stay on Top (ON)")
        else:
            # OFF - match header background (no visible background)
            self.stay_on_top_label.config(background=header_bg)
            # Update tooltip
            self.tooltip_manager.update(self.stay_on_top_label, "Stay on Top (OFF)")
        
        # Call the actual toggle function
        self.expense_tracker.window_manager.toggle_stay_on_top()
    
    # ==========================================
    # DIALOG & MENU METHODS
    # ==========================================
    
    def show_about_dialog(self):
        """Show About dialog with version and credits"""
        # Read version
        try:
            version = open('version.txt').read().strip()
        except:
            version = "3.5.3"
        
        # Create dialog
        dialog = DialogHelper.create_dialog(
            self.root, "About LiteFinPad",
            config.Dialog.ABOUT_WIDTH, config.Dialog.ABOUT_HEIGHT
        )
        content = DialogHelper.create_content_frame(dialog, padding="20")
        
        # Helper function for creating labels
        def add_label(text, font, color, pady=(0, 10), **kwargs):
            label = ttk.Label(content, text=text, font=font, 
                            foreground=color, justify=tk.CENTER, **kwargs)
            label.pack(pady=pady)
            return label
        
        # App title and version
        add_label("LiteFinPad", config.Fonts.ABOUT_TITLE, 
                 config.Colors.BLUE_LINK, pady=(0, 5))
        add_label(f"Version {version}\nMonthly Expense Tracker", 
                 config.Fonts.LABEL_SMALL, config.Colors.TEXT_GRAY_MEDIUM, 
                 pady=(0, 15))
        
        # Separator
        ttk.Separator(content, orient='horizontal').pack(fill=tk.X, pady=(0, 15))
        
        # Credits, features, and license combined
        add_label("Built with AI assistance\n(Cursor + Claude Sonnet 4)\n\n"
                 "✓ 100% offline - no internet connection required\n"
                 "✓ Lightweight and fast\n"
                 "✓ Export to Excel and PDF\n\n"
                 "License: MIT", 
                 config.Fonts.LABEL_SMALL, config.Colors.TEXT_GRAY_DARK,
                 pady=(0, 15))
        
        # Clickable GitHub link
        github = add_label("GitHub", config.get_font(config.Fonts.SIZE_TINY, 'underline'),
                          config.Colors.BLUE_LINK, pady=(0, 20), cursor='hand2')
        github.bind('<Button-1>', lambda e: webbrowser.open('https://github.com/aHuddini/LiteFinPad'))
        
        # Clickable Close link
        close = add_label("Close", config.get_font(config.Fonts.SIZE_SMALL, 'underline'),
                         config.Colors.BLUE_LINK, cursor='hand2')
        close.bind('<Button-1>', lambda e: dialog.destroy())
        
        # Finalize dialog
        DialogHelper.bind_escape_to_close(dialog)
        DialogHelper.center_on_parent(dialog, self.root, 
            config.Dialog.ABOUT_WIDTH,
                                      config.Dialog.ABOUT_HEIGHT)
        DialogHelper.show_dialog(dialog)
    
    def show_month_navigation_menu(self, event):
        """Show hierarchical month navigation menu (Year > Months)"""
        # Create navigation menu using month viewer
        menu = self.expense_tracker.month_viewer.create_navigation_menu(
            self.root,
            on_select_callback=self.on_month_selected
        )
        
        # Show menu at mouse position
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def on_month_selected(self, month_key: str):
        """
        Callback when a month is selected from the dropdown
        
        Args:
            month_key: Selected month in YYYY-MM format
        """
        # Switch to the selected month
        self.expense_tracker.switch_month(month_key)
    
    # ==========================================
    # HELPER METHODS (Internal Utilities)
    # ==========================================
    
    def _is_archive_mode(self):
        """
        Helper method that delegates to archive_mode_manager if available.
        Provides fallback during initialization when manager doesn't exist yet.
        """
        if hasattr(self, 'archive_mode_manager'):
            return self.archive_mode_manager.is_archive_mode()
        else:
            # Fallback during initialization
            viewed_month = getattr(self.expense_tracker, 'viewed_month', None)
            if viewed_month is None:
                return False
            current_month_key = datetime.now().strftime('%Y-%m')
            return viewed_month != current_month_key
    
    def _get_context_date(self):
        """
        Helper method that delegates to archive_mode_manager if available.
        Provides fallback during initialization when manager doesn't exist yet.
        """
        if hasattr(self, 'archive_mode_manager'):
            return self.archive_mode_manager.get_context_date()
        else:
            # Fallback during initialization
            if self._is_archive_mode():
                viewed_month = self.expense_tracker.viewed_month
                year, month = map(int, viewed_month.split('-'))
                last_day = calendar.monthrange(year, month)[1]
                return datetime(year, month, last_day)
            else:
                return datetime.now()
    
    # ==========================================
    # DASHBOARD UPDATE METHODS
    # ==========================================
        
    def update_display(self):
        """Update all display elements"""
        # Update total
        self.total_label.config(text=f"${self.expense_tracker.monthly_total:.2f}")
        
        # Get context date for analytics
        context_date = self._get_context_date()
        
        # Update count (exclude future expenses)
        from datetime import datetime
        today = datetime.now().date()
        past_expenses = [e for e in self.expense_tracker.expenses 
                        if datetime.strptime(e['date'], '%Y-%m-%d').date() <= today]
        expense_count = len(past_expenses)
        self.count_label.config(text=f"{expense_count} expenses this month")
        
        # Update day/week progress
        current_day, total_days = ExpenseAnalytics.calculate_day_progress(context_date)
        current_week, total_weeks = ExpenseAnalytics.calculate_week_progress(context_date)
        self.day_progress_label.config(text=f"{current_day} / {total_days}")
        
        # For archive mode, show clean week numbers (no decimals for completed months)
        if self._is_archive_mode():
            # Round to nearest integer for past months (looks cleaner)
            week_display = f"{round(current_week)} / {total_weeks}"
        else:
            # Current month: show decimal precision for progress within week
            week_display = f"{current_week:.1f} / {total_weeks}"
        self.week_progress_label.config(text=week_display)
        
        # Update progress (averages in progress section)
        daily_avg, days_elapsed = ExpenseAnalytics.calculate_daily_average(
            self.expense_tracker.expenses, context_date
        )
        weekly_avg, weeks_elapsed = ExpenseAnalytics.calculate_weekly_average(
            self.expense_tracker.expenses, context_date
        )
        
        self.daily_avg_label.config(text=f"${daily_avg:.2f} /day")
        self.weekly_avg_label.config(text=f"${weekly_avg:.2f} /week")
        
        # Update analytics (weekly pace and previous month) with archive context
        context_date = self._get_context_date()
        weekly_pace, pace_days = ExpenseAnalytics.calculate_weekly_pace(
            self.expense_tracker.expenses, context_date
        )
        
        # Calculate previous month data with comparison
        # Pass viewed_month only if truly in archive mode (not current month)
        viewed_month = self.expense_tracker.viewed_month if self._is_archive_mode() else None
        prev_month_date = datetime.now().replace(day=1) - timedelta(days=1)
        prev_month_key = prev_month_date.strftime('%Y-%m')
        prev_data_folder = f"data_{prev_month_key}"
        trend_text, trend_context, comparison = ExpenseAnalytics.calculate_monthly_trend(
            prev_data_folder,
            self.expense_tracker.monthly_total,
            viewed_month
        )
        
        self.pace_label.config(text=f"${weekly_pace:.2f} /day")
        self.trend_label.config(text=f"{trend_text} ")
        self.trend_context_label.config(text=trend_context)  # Update month name
        
        # Update comparison indicator
        if hasattr(self, 'comparison_label') and comparison:
            indicator_text = f"{comparison['symbol']} "
            if comparison['direction'] == 'similar':
                indicator_text += f"+{comparison['percentage']:.1f}%"
            else:
                sign = "+" if comparison['direction'] == 'increase' else "-"
                indicator_text += f"{sign}{comparison['percentage']:.0f}%"
            
            self.comparison_label.config(
                text=indicator_text,
                foreground=comparison['color']
            )
        elif hasattr(self, 'comparison_label'):
            # Clear indicator if no comparison available
            self.comparison_label.config(text="")
        
        # Update recent expenses
        self.update_recent_expenses()
    
    def update_recent_expenses(self):
        """Update the recent expenses display (excluding future expenses)"""
        from datetime import datetime
        
        # Filter out future expenses and get last 2 (not 3)
        today = datetime.now().date()
        past_expenses = [e for e in self.expense_tracker.expenses 
                        if datetime.strptime(e['date'], '%Y-%m-%d').date() <= today]
        recent_expenses = past_expenses[-2:] if past_expenses else []
        
        expense_labels = [self.recent_expense_1, self.recent_expense_2]
        
        for i, expense in enumerate(recent_expenses):
            if i < len(expense_labels):
                # Format date as MM/DD/YY
                date_obj = datetime.strptime(expense['date'], '%Y-%m-%d')
                formatted_date = date_obj.strftime("%m/%d/%y")
                
                # Format: • Date - Amount - Description
                expense_text = f"• {formatted_date} - ${expense['amount']:.2f} - {expense['description']}"
                expense_labels[i].config(text=expense_text)
        
        # Clear remaining labels
        for i in range(len(recent_expenses), len(expense_labels)):
            expense_labels[i].config(text="")
        
    def create_expense_list_page(self):
        """Create the expense list page using ExpenseListPageBuilder"""
        # Create builder with all necessary callbacks
        builder = ExpenseListPageBuilder(
            parent_frame=self.main_container,
            expense_tracker=self.expense_tracker,
            callbacks={
                'show_main_page': self.show_main_page,
                'export_dialog': self.expense_tracker.export_expenses_dialog,
                'import_dialog': self.expense_tracker.import_expenses_dialog,
                'on_expense_change': None,  # Builder creates this internally
                'update_display': self.update_display,
                'update_expense_metrics': self.update_expense_metrics,
                'status_manager': self.status_manager,
                'page_manager': self.page_manager,
                'gui_instance': self
            }
        )
        
        # Build the page and get widget references
        widgets = builder.build_all()
        
        # Store references needed for updates
        self.expense_list_frame = widgets['expense_list_frame']
        self.table_manager = widgets['table_manager']
        self._expense_count_tracker = widgets['count_tracker']
        self.quick_add_helper = widgets['quick_add_helper']
        
        # Store metric label references for update_expense_metrics()
        for label_name, label_widget in widgets['metric_labels'].items():
            setattr(self, label_name, label_widget)
    
    # ==========================================
    # EXPENSE LIST UPDATE METHODS
    # ==========================================
        
    def update_expense_metrics(self):
        """Update the expense metrics on the expense list page"""
        median_expense, expense_count = ExpenseAnalytics.calculate_median_expense(
            self.expense_tracker.expenses
        )
        largest_expense, largest_desc = ExpenseAnalytics.calculate_largest_expense(
            self.expense_tracker.expenses
        )
        total_amount = self.expense_tracker.monthly_total
        
        self.list_median_label.config(text=f"${median_expense:.2f}")
        self.median_count_label.config(text=f"(median of {expense_count} expense{'s' if expense_count != 1 else ''})")
        self.list_total_label.config(text=f"${total_amount:.2f}")
        expense_count_total = len(self.expense_tracker.expenses)
        self.total_count_label.config(text=f"({expense_count_total} expense{'s' if expense_count_total != 1 else ''})")
        self.largest_label.config(text=f"${largest_expense:.2f}")
        self.largest_desc_label.config(text=f"({largest_desc})")
    
    # ==========================================
    # PAGE NAVIGATION METHODS
    # ==========================================
    
    def show_expense_list_page(self):
        """Show the expense list page"""
        self.page_manager.show_expense_list_page(
            status_manager=self.status_manager,
            table_manager=self.table_manager if hasattr(self, 'table_manager') else None,
            expense_tracker=self.expense_tracker,
            update_metrics_callback=self.update_expense_metrics
        )
        
    def show_main_page(self):
        """Show the main dashboard page"""
        self.page_manager.show_main_page(status_manager=self.status_manager)
