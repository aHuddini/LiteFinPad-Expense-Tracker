"""
Dashboard Page Builder - UI Construction for Main Dashboard

Handles all widget creation and layout for the main dashboard page.
Separates UI construction from update logic and event handling.
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import config
from analytics import ExpenseAnalytics


class DashboardPageBuilder:
    """
    Constructs the main dashboard UI with all sections.
    
    Responsibilities:
    - Create all dashboard widgets
    - Set up layout and styling
    - Wire up event handlers
    - Return widget references for updates
    """
    
    def __init__(self, parent_frame, expense_tracker, callbacks, tooltip_manager):
        """
        Initialize the dashboard builder.
        
        Args:
            parent_frame: The main frame to build widgets in
            expense_tracker: Reference to ExpenseTracker for data access
            callbacks: Dict of callback functions for events
            tooltip_manager: TooltipManager for creating tooltips
        """
        self.frame = parent_frame
        self.tracker = expense_tracker
        self.callbacks = callbacks
        self.tooltip_manager = tooltip_manager
        
        # Widget references to be returned
        self.widgets = {}
        
    def build_all(self):
        """Build all dashboard sections and return widget references"""
        self.create_header()
        self.create_total_section()
        self.create_progress_section()
        self.create_analytics_section()
        self.create_expenses_section()  # Row 6
        self.create_buttons_section()    # Row 7
        
        return self.widgets
        
    def create_header(self):
        """Create header with perfectly centered title and controls"""
        # Header frame - full width
        header_frame = ttk.Frame(self.frame)
        header_frame.grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky=(tk.W, tk.E))
        header_frame.columnconfigure(0, weight=1)  # Full width for centering
        
        # Month/Year title - perfectly centered and clickable
        month_text = self.tracker.month_viewer.format_month_display(
            self.tracker.viewed_month
        )
        month_label = ttk.Label(
            header_frame, 
            text=month_text, 
            style='Title.TLabel',
            cursor='hand2'  # Hand cursor to indicate clickability
        )
        month_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Bind click event to open month navigation menu
        month_label.bind('<Button-1>', self.callbacks['show_month_navigation_menu'])
        
        # Store reference
        self.widgets['month_label'] = month_label
        
        # Control buttons frame - positioned absolutely on the right
        controls_frame = ttk.Frame(header_frame)
        controls_frame.place(relx=1.0, x=-15, y=5, anchor='ne')
        
        # About button (info icon) - leftmost
        about_label = ttk.Label(
            controls_frame,
            text="ℹ️",
            font=config.get_font(config.Fonts.SIZE_MEDIUM),
            cursor='hand2'
        )
        about_label.pack(side=tk.LEFT, padx=(0, 2))
        
        # Bind click event
        about_label.bind('<Button-1>', lambda e: self.callbacks['show_about_dialog']())
        
        # Add tooltip
        self.tooltip_manager.create(about_label, "About LiteFinPad")
        
        # Store reference
        self.widgets['about_label'] = about_label
        
        # Stay on top control (default: enabled) - use a simple Label as a clickable icon
        stay_on_top_var = tk.BooleanVar(value=True)
        self.widgets['stay_on_top_var'] = stay_on_top_var
        
        # Use a Label instead of Button - no hover effects, no button behavior
        stay_on_top_label = tk.Label(
            controls_frame,
            text="📌",
            font=config.get_font(config.Fonts.SIZE_MEDIUM),
            background=config.Colors.BG_BUTTON_DISABLED,  # Gray background when ON
            cursor='hand2',  # Hand cursor to show it's clickable
            padx=5,
            pady=2
        )
        stay_on_top_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Bind click event
        stay_on_top_label.bind('<Button-1>', lambda e: self.callbacks['toggle_stay_on_top_visual']())
        
        # Add tooltip
        self.tooltip_manager.create(stay_on_top_label, "Stay on Top (ON)")
        
        # Store reference
        self.widgets['stay_on_top_label'] = stay_on_top_label
        
        # Minimize to tray button
        minimize_button = ttk.Button(
            controls_frame,
            text="➖",
            command=self.tracker.window_manager.hide_window,
            style='Toolbutton',
            width=3
        )
        minimize_button.pack(side=tk.LEFT)
        
        # Add tooltip
        self.tooltip_manager.create(minimize_button, "Minimize to Tray")
        
        # Store reference
        self.widgets['minimize_button'] = minimize_button
        
    def create_total_section(self):
        """Create monthly total display section"""
        # Monthly total display
        total_label = ttk.Label(self.frame, text=f"${self.tracker.monthly_total:.2f}", style='Total.TLabel')
        total_label.grid(row=1, column=0, columnspan=2, pady=(0, 5))
        self.widgets['total_label'] = total_label
        
        # Sublabel: (Total Monthly)
        ttk.Label(self.frame, text="(Total Monthly)", font=config.Fonts.LABEL, foreground=config.Colors.TEXT_GRAY_MEDIUM).grid(row=2, column=0, columnspan=2, pady=(0, 10))
        
        # Expense count display (exclude future expenses)
        today = datetime.now().date()
        past_expenses = [e for e in self.tracker.expenses 
                        if datetime.strptime(e['date'], '%Y-%m-%d').date() <= today]
        expense_count = len(past_expenses)
        count_label = ttk.Label(self.frame, text=f"{expense_count} expenses this month", style='Count.TLabel')
        count_label.grid(row=3, column=0, columnspan=2, pady=(0, 12))
        self.widgets['count_label'] = count_label
        
    def create_progress_section(self):
        """Create current progress section with averages"""
        progress_frame = ttk.LabelFrame(self.frame, text="Current Progress", padding="10")
        progress_frame.grid(row=4, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Get progress data (use archive context if in archive mode)
        context_date = self.callbacks['get_context_date']()
        current_day, total_days = ExpenseAnalytics.calculate_day_progress(context_date)
        current_week, total_weeks = ExpenseAnalytics.calculate_week_progress(context_date)
        daily_avg, days_elapsed = ExpenseAnalytics.calculate_daily_average(
            self.tracker.expenses, context_date
        )
        weekly_avg, weeks_elapsed = ExpenseAnalytics.calculate_weekly_average(
            self.tracker.expenses, context_date
        )
        
        # Top row: Day and Week progress (simplified, single line)
        top_row = ttk.Frame(progress_frame)
        top_row.pack(fill=tk.X, pady=(0, 8))
        
        # Day progress (left) - split label and value
        day_frame = ttk.Frame(top_row)
        day_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        day_container = ttk.Frame(day_frame)
        day_container.pack()
        ttk.Label(day_container, text="Day: ", font=config.get_font(config.Fonts.SIZE_NORMAL, 'bold'), foreground=config.Colors.BLUE_NAVY).pack(side=tk.LEFT)
        day_progress_label = ttk.Label(day_container, text=f"{current_day} / {total_days}", style='Analytics.TLabel')
        day_progress_label.pack(side=tk.LEFT)
        self.widgets['day_progress_label'] = day_progress_label
        
        # Week progress (right) - split label and value
        week_frame = ttk.Frame(top_row)
        week_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        week_container = ttk.Frame(week_frame)
        week_container.pack()
        ttk.Label(week_container, text="Week: ", font=config.get_font(config.Fonts.SIZE_NORMAL, 'bold'), foreground=config.Colors.BLUE_NAVY).pack(side=tk.LEFT)
        
        # For archive mode, show clean week numbers (no decimals for completed months)
        if self.callbacks['is_archive_mode']():
            week_display = f"{round(current_week)} / {total_weeks}"
        else:
            week_display = f"{current_week:.1f} / {total_weeks}"
        week_progress_label = ttk.Label(week_container, text=week_display, style='Analytics.TLabel')
        week_progress_label.pack(side=tk.LEFT)
        self.widgets['week_progress_label'] = week_progress_label
        
        # Bottom row: Daily and Weekly averages
        bottom_row = ttk.Frame(progress_frame)
        bottom_row.pack(fill=tk.X, pady=(8, 0))
        
        # Daily average (left)
        daily_avg_frame = ttk.Frame(bottom_row)
        daily_avg_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ttk.Label(daily_avg_frame, text="Daily Average", font=config.get_font(config.Fonts.SIZE_NORMAL, 'bold'), foreground=config.Colors.RED_PRIMARY).pack()
        daily_avg_label = ttk.Label(daily_avg_frame, text=f"${daily_avg:.2f} /day", style='Analytics.TLabel')
        daily_avg_label.pack()
        self.widgets['daily_avg_label'] = daily_avg_label
        
        # Weekly average (right)
        weekly_avg_frame = ttk.Frame(bottom_row)
        weekly_avg_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        ttk.Label(weekly_avg_frame, text="Weekly Average", font=config.get_font(config.Fonts.SIZE_NORMAL, 'bold'), foreground=config.Colors.GREEN_PRIMARY).pack()
        weekly_avg_label = ttk.Label(weekly_avg_frame, text=f"${weekly_avg:.2f} /week", style='Analytics.TLabel')
        weekly_avg_label.pack()
        self.widgets['weekly_avg_label'] = weekly_avg_label
        
    def create_analytics_section(self):
        """Create spending analysis section"""
        analytics_frame = ttk.LabelFrame(self.frame, text="Spending Analysis", padding="10")
        analytics_frame.grid(row=5, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Get analytics data (use archive context if in archive mode)
        context_date = self.callbacks['get_context_date']()
        weekly_pace, pace_days = ExpenseAnalytics.calculate_weekly_pace(
            self.tracker.expenses, context_date
        )
        
        # Calculate previous month data with comparison
        # Pass viewed_month only if truly in archive mode (not current month)
        viewed_month = self.tracker.viewed_month if self.callbacks['is_archive_mode']() else None
        prev_month_date = datetime.now().replace(day=1) - timedelta(days=1)
        prev_month_key = prev_month_date.strftime('%Y-%m')
        prev_data_folder = f"data_{prev_month_key}"
        prev_month_total, prev_month_name, comparison = ExpenseAnalytics.calculate_monthly_trend(
            prev_data_folder,
            self.tracker.monthly_total,
            viewed_month
        )
        
        # Side by side: Weekly Pace and Previous Month
        row = ttk.Frame(analytics_frame)
        row.pack(fill=tk.X)
        
        # Weekly pace (left)
        pace_frame = ttk.Frame(row)
        pace_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ttk.Label(pace_frame, text="Weekly Pace", font=config.get_font(config.Fonts.SIZE_NORMAL, 'bold'), foreground=config.Colors.ORANGE_PRIMARY).pack()
        pace_label = ttk.Label(pace_frame, text=f"${weekly_pace:.2f} /day", style='Analytics.TLabel')
        pace_label.pack()
        ttk.Label(pace_frame, text=f"(this week: {pace_days} day{'s' if pace_days != 1 else ''})", font=config.Fonts.LABEL, foreground=config.Colors.TEXT_GRAY_MEDIUM).pack()
        self.widgets['pace_label'] = pace_label
        
        # Previous month (right)
        prev_month_frame = ttk.Frame(row)
        prev_month_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        ttk.Label(prev_month_frame, text="Previous Month", font=config.get_font(config.Fonts.SIZE_NORMAL, 'bold'), foreground=config.Colors.PURPLE_PRIMARY).pack()
        
        # Amount with comparison indicator (side-by-side)
        amount_container = tk.Frame(prev_month_frame, background=config.Colors.BG_LIGHT_GRAY)
        amount_container.pack()
        
        # Previous month amount
        trend_label = ttk.Label(amount_container, text=f"{prev_month_total} ", style='Trend.TLabel')
        trend_label.pack(side=tk.LEFT)
        self.widgets['trend_label'] = trend_label
        
        # Comparison indicator (smaller font, colored)
        comparison_label = tk.Label(
            amount_container,
            text="",  # Will be updated with indicator
            font=config.get_font(9),  # Smaller font (9pt instead of 11pt in PoC)
            background=config.Colors.BG_LIGHT_GRAY,
            foreground='#999999'  # Default gray
        )
        comparison_label.pack(side=tk.LEFT)
        self.widgets['comparison_label'] = comparison_label
        
        # Update comparison indicator if available
        if comparison:
            indicator_text = f"{comparison['symbol']} "
            if comparison['direction'] == 'similar':
                indicator_text += f"+{comparison['percentage']:.1f}%"
            else:
                sign = "+" if comparison['direction'] == 'increase' else "-"
                indicator_text += f"{sign}{comparison['percentage']:.0f}%"
            
            comparison_label.config(
                text=indicator_text,
                foreground=comparison['color']
            )
        
        # Month name context (will update dynamically when switching months)
        trend_context_label = ttk.Label(prev_month_frame, text=prev_month_name, font=config.Fonts.LABEL, foreground=config.Colors.TEXT_GRAY_MEDIUM)
        trend_context_label.pack()
        self.widgets['trend_context_label'] = trend_context_label
        
    def create_expenses_section(self):
        """Create recent expenses section"""
        expenses_frame = ttk.LabelFrame(self.frame, text="Recent Expenses", padding="10")
        expenses_frame.grid(row=6, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure minimum height for the frame
        expenses_frame.grid_propagate(False)
        expenses_frame.configure(height=90)  # Reduced height for 2 entries
        
        # Configure the expenses frame to expand
        expenses_frame.rowconfigure(0, weight=1)
        expenses_frame.columnconfigure(0, weight=1)
        
        # Container for expense labels with padding
        expenses_container = ttk.Frame(expenses_frame)
        expenses_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create individual expense labels for better visibility (left-aligned, brown color)
        # Only showing 2 most recent expenses
        recent_expense_1 = ttk.Label(expenses_container, text="No recent expenses", 
                                      font=config.Fonts.LABEL, foreground=config.Colors.TEXT_BROWN, anchor='w')
        recent_expense_1.pack(pady=3, fill=tk.X)
        self.widgets['recent_expense_1'] = recent_expense_1
        
        recent_expense_2 = ttk.Label(expenses_container, text="", 
                                      font=config.Fonts.LABEL, foreground=config.Colors.TEXT_BROWN, anchor='w')
        recent_expense_2.pack(pady=3, fill=tk.X)
        self.widgets['recent_expense_2'] = recent_expense_2
        
    def create_buttons_section(self):
        """Create button section with proper spacing"""
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Add expense button (with green accent) - on left for easier access
        add_expense_btn = ttk.Button(button_frame, text="+ Add Expense", command=self.tracker.add_expense, style='AddExpense.TButton')
        add_expense_btn.grid(row=0, column=0, padx=(0, 10), sticky=(tk.W, tk.E))
        self.widgets['add_expense_btn'] = add_expense_btn
        
        # Navigation button to switch to Expense List page
        nav_button = ttk.Button(button_frame, text="📋 Expense List", command=self.tracker.show_expense_list_page, style='Modern.TButton')
        nav_button.grid(row=0, column=1, padx=(10, 0), sticky=(tk.W, tk.E))
        
        # Configure button frame columns
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

