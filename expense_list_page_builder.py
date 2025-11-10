"""UI construction for expense list page, separated from update logic."""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import config
from analytics import ExpenseAnalytics


class ExpenseListPageBuilder:
    """Handles UI construction for the expense list page."""
    
    def __init__(self, parent_frame, expense_tracker, callbacks, theme_manager=None):
        """Initialize builder with parent frame, expense tracker, callbacks, and optional theme manager."""
        self.parent_frame = parent_frame
        self.expense_tracker = expense_tracker
        self.callbacks = callbacks
        self.theme_manager = theme_manager
        
        self.colors = theme_manager.get_colors() if theme_manager else config.Colors
        
        self._previous_expense_count = [len(self.expense_tracker.expenses)]
        
    def build_all(self):
        """Build complete expense list page and return widget references."""
        frame_bg = self.colors.BG_SECONDARY if self.theme_manager.is_dark_mode() else self.colors.BG_LIGHT_GRAY
        expense_list_frame = ctk.CTkFrame(self.parent_frame, fg_color=frame_bg)
        expense_list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=15, pady=(8, 2))
        
        expense_list_frame.columnconfigure(0, weight=1)
        expense_list_frame.rowconfigure(3, weight=1)
        
        self._create_header(expense_list_frame)
        metric_labels = self._create_metrics_section(expense_list_frame)
        table_manager = self._create_table_section(expense_list_frame)
        quick_add_helper = self._create_quick_add_section(expense_list_frame, table_manager)
        
        expense_list_frame.grid_remove()
        
        return {
            'expense_list_frame': expense_list_frame,
            'metric_labels': metric_labels,
            'table_manager': table_manager,
            'count_tracker': self._previous_expense_count,
            'quick_add_helper': quick_add_helper
        }
    
    def _create_header(self, parent):
        """Create header with back button, title, and export/import buttons."""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.grid(row=0, column=0, pady=(0, 5), sticky=(tk.W, tk.E))
        header_frame.columnconfigure(1, weight=1)
        
        back_button = ctk.CTkButton(
            header_frame, 
            text="←", 
            command=self.callbacks['show_main_page'],
            width=40,
            height=30,  # Match other buttons
            corner_radius=config.CustomTkinterTheme.CORNER_RADIUS,
            font=config.get_font(config.Fonts.SIZE_LARGE),  # Larger font for bigger arrow
            fg_color=self.colors.BLUE_DARK_NAVY,  # Dark navy blue
            hover_color=self.colors.BLUE_NAVY,  # Lighter navy on hover
            text_color="white"
        )
        back_button.grid(row=0, column=0, sticky=tk.W, padx=(0, 15))
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="Expense List", 
            font=config.Fonts.TITLE,
            text_color=self.colors.TEXT_BLACK
        )
        title_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        button_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        button_frame.grid(row=0, column=2, sticky=tk.E, padx=(15, 0))
        
        export_button = ctk.CTkButton(
            button_frame, 
            text="↑ Export", 
            command=self.callbacks['export_dialog'],
            width=100,
            height=30,  # Compact height like dashboard buttons
            corner_radius=config.CustomTkinterTheme.CORNER_RADIUS,
            font=config.Fonts.BUTTON,
            fg_color=self.colors.BLUE_DARK_NAVY,  # Dark navy blue
            hover_color=self.colors.BLUE_NAVY,  # Lighter navy on hover
            text_color="white"
        )
        export_button.pack(pady=(0, 3))  # Reduced spacing
        
        # Import button (below Export) - using CTkButton with down arrow and dark navy blue
        import_button = ctk.CTkButton(
            button_frame, 
            text="↓ Import", 
            command=self.callbacks['import_dialog'],
            width=100,
            height=30,  # Compact height like dashboard buttons
            corner_radius=config.CustomTkinterTheme.CORNER_RADIUS,
            font=config.Fonts.BUTTON,
            fg_color=self.colors.BLUE_DARK_NAVY,  # Dark navy blue
            hover_color=self.colors.BLUE_NAVY,  # Lighter navy on hover
            text_color="white"
        )
        import_button.pack()
    
    def _create_metrics_section(self, parent):
        """Create expense metrics section (median, total, largest)."""
        # Title label OUTSIDE the frame (like dashboard sections)
        # Use theme-aware text color: TEXT_BLACK (light) or TEXT_PRIMARY (dark)
        # Match parent background to avoid light gray background
        parent_bg = self.colors.BG_SECONDARY if self.theme_manager.is_dark_mode() else self.colors.BG_LIGHT_GRAY
        title_label = ttk.Label(
            parent, 
            text="Expense Insights", 
            font=config.get_font(config.Fonts.SIZE_SMALL),
            foreground=self.colors.TEXT_BLACK,  # Theme-aware: TEXT_BLACK in light, TEXT_PRIMARY in dark
            background=parent_bg  # Match parent container background
        )
        title_label.grid(row=1, column=0, pady=(0, 0), sticky=tk.W)  # Title above frame
        
        # Frame uses theme-aware background with subtle border
        frame_bg = parent_bg
        border_color = self.colors.BG_DARK_GRAY
        metrics_frame = ctk.CTkFrame(
            parent,
            fg_color=frame_bg,
            border_width=1,
            border_color=border_color
        )
        metrics_frame.grid(row=2, column=0, pady=(0, 0), sticky=(tk.W, tk.E))  # No spacing to move table closer
        
        # Get initial metrics data
        median_expense, expense_count = ExpenseAnalytics.calculate_median_expense(
            self.expense_tracker.expenses
        )
        largest_expense, largest_desc = ExpenseAnalytics.calculate_largest_expense(
            self.expense_tracker.expenses
        )
        total_amount = self.expense_tracker.monthly_total
        
        # Three columns: Typical Expense | Total Amount | Largest Expense
        # Match Analytics section: Use custom style to match CTkFrame background (prevents black bar)
        frame_bg = self.colors.BG_SECONDARY if self.theme_manager.is_dark_mode() else self.colors.BG_LIGHT_GRAY
        style = ttk.Style()
        style.configure('Metrics.TFrame', background=frame_bg)
        row = ttk.Frame(metrics_frame, style='Metrics.TFrame')  # Use ttk.Frame for internal layout like dashboard
        row.pack(fill=tk.X, padx=10, pady=(8, 8))  # Match dashboard padding
        
        # Typical expense (left) - using ttk.Label with Analytics.TLabel style for values (matches dashboard)
        # Use accent color for label, Analytics.TLabel style for value (theme-aware)
        # Frame uses same background as parent
        typical_frame = ttk.Frame(row, style='Metrics.TFrame')
        typical_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        # Label uses same background as frame
        ttk.Label(typical_frame, text="Typical Expense", 
                 font=config.get_font(config.Fonts.SIZE_SMALL, 'bold'), 
                 foreground=self.colors.TEXT_GRAY_DARK,
                 background=frame_bg).pack()
        list_median_label = ttk.Label(typical_frame, text=f"${median_expense:.2f}", 
                                     font=config.get_font(config.Fonts.SIZE_NORMAL),  # Match Analytics.TLabel font size
                                     foreground=self.colors.TEXT_BLACK,  # Match main window value colors
                                     background=frame_bg)  # Explicit background
        list_median_label.pack()
        median_count_label = ttk.Label(typical_frame, 
                                      text=f"(median of {expense_count} expense{'s' if expense_count != 1 else ''})", 
                                      font=config.Fonts.LABEL_SMALL, 
                                      foreground=self.colors.TEXT_GRAY_MEDIUM,
                                      background=frame_bg)
        median_count_label.pack()
        
        total_frame = ttk.Frame(row, style='Metrics.TFrame')
        total_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(total_frame, text="Total Amount", 
                 font=config.get_font(config.Fonts.SIZE_SMALL, 'bold'), 
                 foreground=self.colors.GREEN_PRIMARY,
                 background=frame_bg).pack()
        list_total_label = ttk.Label(total_frame, text=f"${total_amount:.2f}", 
                                    style='Analytics.TLabel',  # Use Analytics.TLabel style (theme-aware)
                                    foreground=self.colors.GREEN_PRIMARY,  # Override with green for total
                                    background=frame_bg)  # Explicit background
        list_total_label.pack()
        expense_count_total = len(self.expense_tracker.expenses)
        total_count_label = ttk.Label(total_frame, 
                                     text=f"({expense_count_total} expense{'s' if expense_count_total != 1 else ''})", 
                                     font=config.Fonts.LABEL_SMALL, 
                                     foreground=self.colors.TEXT_GRAY_MEDIUM,
                                     background=frame_bg)  # Explicit background
        total_count_label.pack()
        
        # Largest expense (right) - using ttk.Label with Analytics.TLabel style for values (matches dashboard)
        # Frame uses same background as parent
        largest_frame = ttk.Frame(row, style='Metrics.TFrame')
        largest_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Label uses same background as frame
        ttk.Label(largest_frame, text="Largest Expense", 
                 font=config.get_font(config.Fonts.SIZE_SMALL, 'bold'), 
                 foreground=self.colors.RED_PRIMARY,
                 background=frame_bg).pack()
        largest_label = ttk.Label(largest_frame, text=f"${largest_expense:.2f}", 
                                 font=config.get_font(config.Fonts.SIZE_NORMAL),  # Match Analytics.TLabel font size
                                 foreground=self.colors.TEXT_BLACK,  # Match main window value colors
                                 background=frame_bg)  # Explicit background
        largest_label.pack()
        largest_desc_label = ttk.Label(largest_frame, text=f"({largest_desc})", 
                                      font=config.Fonts.LABEL_SMALL, 
                                      foreground=self.colors.TEXT_GRAY_MEDIUM,
                                      background=frame_bg)  # Explicit background
        largest_desc_label.pack()
        
        return {
            'list_median_label': list_median_label,
            'median_count_label': median_count_label,
            'list_total_label': list_total_label,
            'total_count_label': total_count_label,
            'largest_label': largest_label,
            'largest_desc_label': largest_desc_label
        }
    
    def _create_table_section(self, parent):
        """Create expense table manager."""
        # Create callback for expense changes
        def on_expense_change():
            status_manager = self.callbacks['status_manager']
            update_display = self.callbacks['update_display']
            update_metrics = self.callbacks['update_expense_metrics']
            
            from expense_table import ExpenseTableManager
            table_expenses = table_manager.get_expenses()
            current_count = len(table_expenses)
            
            self.expense_tracker.expenses = [exp.to_dict() for exp in table_expenses]
            self.expense_tracker.monthly_total = sum(exp['amount'] for exp in self.expense_tracker.expenses)
            
            self.expense_tracker.save_data()
            
            if current_count < self._previous_expense_count[0]:
                status_manager.show(config.Messages.EXPENSE_DELETED, config.StatusBar.SUCCESS_ICON)
            elif current_count == self._previous_expense_count[0]:
                status_manager.show(config.Messages.EXPENSE_EDITED, config.StatusBar.SUCCESS_ICON)
            
            self._previous_expense_count[0] = current_count
            
            update_display()
            update_metrics()
            self.expense_tracker.tray_icon_manager.update_tooltip()
        
        table_container = ctk.CTkFrame(parent, fg_color="transparent")
        table_container.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        table_container.columnconfigure(0, weight=1)
        table_container.rowconfigure(0, weight=1)
        
        from expense_table import ExpenseTableManager
        table_manager = ExpenseTableManager(table_container, on_expense_change, theme_manager=self.theme_manager)
        
        self._previous_expense_count[0] = len(self.expense_tracker.expenses)
        
        return table_manager
    
    def _create_quick_add_section(self, parent, table_manager):
        """Create quick add section at the bottom."""
        from quick_add_helper import QuickAddHelper
        
        description_history = getattr(self.expense_tracker, 'description_history', None)
        
        quick_add_helper = QuickAddHelper(
            parent_widget=parent,
            expense_tracker=self.expense_tracker,
            on_add_callback=self.callbacks['update_display'],
            status_manager=self.callbacks['status_manager'],
            page_manager=self.callbacks['page_manager'],
            table_manager=table_manager,
            update_metrics_callback=self.callbacks['update_expense_metrics'],
            count_tracker=self._previous_expense_count,
            gui_instance=self.callbacks['gui_instance'],
            description_history=description_history,
            theme_manager=self.theme_manager
        )
        quick_add_frame = quick_add_helper.create_ui()
        quick_add_frame.grid(row=4, column=0, pady=(5, 0), sticky=(tk.W, tk.E))  # Reduced spacing
        
        # Store reference for later use (e.g., archive mode)
        return quick_add_helper

