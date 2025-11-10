"""Inline Quick Add expense functionality with validation, cross-month routing, and archive mode integration."""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import customtkinter as ctk
import config
from widgets import CollapsibleDateCombobox, AutoCompleteEntry
from expense_table import ExpenseData
from validation import InputValidation


class QuickAddHelper:
    """Manages the inline Quick Add expense functionality."""
    
    def __init__(self, parent_widget, expense_tracker, on_add_callback=None, 
                 status_manager=None, page_manager=None, table_manager=None,
                 update_metrics_callback=None, count_tracker=None, gui_instance=None,
                 description_history=None, theme_manager=None):
        """Initialize the Quick Add Helper."""
        self.parent = parent_widget
        self.expense_tracker = expense_tracker
        self.on_add_callback = on_add_callback
        self.status_manager = status_manager
        self.page_manager = page_manager
        self.table_manager = table_manager
        self.update_metrics_callback = update_metrics_callback
        self.count_tracker = count_tracker
        self.gui = gui_instance
        self.description_history = description_history
        self.theme_manager = theme_manager
        
        # Get theme-aware colors
        if self.theme_manager:
            self.colors = self.theme_manager.get_colors()
        else:
            self.colors = config.Colors
        
        # UI elements (will be created in create_ui())
        self.amount_var = None
        self.amount_entry = None
        self.description_entry = None
        self.date_combo = None
        self.add_button = None
        self.frame = None
    
    def create_ui(self):
        """Create and return the Quick Add UI frame."""
        self.frame = ttk.LabelFrame(self.parent, text="Quick Add Expense", padding="15")
        self.frame.columnconfigure(0, weight=1)
        
        style = ttk.Style()
        style.configure("TLabelframe.Label", foreground=self.colors.TEXT_BLACK)
        
        is_dark = self.theme_manager.is_dark_mode() if self.theme_manager else False
        frame_bg = self.colors.BG_SECONDARY if is_dark else self.colors.BG_LIGHT_GRAY
        border_color = self.colors.BG_DARK_GRAY
        style.configure("QuickAdd.TLabelframe", 
                        background=frame_bg, 
                        bordercolor=border_color, 
                        borderwidth=1,
                        relief='flat')
        style.configure("QuickAdd.TLabelframe.Label", 
                        background=frame_bg, 
                        foreground=self.colors.TEXT_BLACK)
        self.frame.configure(style="QuickAdd.TLabelframe")
        
        style.map("QuickAdd.TLabelframe",
                 background=[('active', frame_bg), ('!active', frame_bg)])
        
        entry_bg = self.colors.BG_MEDIUM_GRAY if is_dark else self.colors.BG_WHITE
        entry_fg = self.colors.TEXT_BLACK
        style.configure('QuickAdd.TEntry',
                       fieldbackground=entry_bg,
                       foreground=entry_fg,
                       borderwidth=1,
                       relief='solid')
        style.configure('QuickAdd.TCombobox',
                       fieldbackground=entry_bg,
                       foreground=entry_fg,
                       borderwidth=1)
        
        style.configure("QuickAdd.TFrame", background=frame_bg)
        
        row1_container = ttk.Frame(self.frame, style="QuickAdd.TFrame")
        row1_container.pack(fill=tk.X, pady=(0, 3))
        
        amount_frame = ttk.Frame(row1_container, style="QuickAdd.TFrame")
        amount_frame.pack(side=tk.LEFT, padx=(0, 15))
        style.configure("QuickAdd.TLabel", background=frame_bg, foreground=self.colors.TEXT_BLACK)
        ttk.Label(amount_frame, text="Amount ($):", font=config.Fonts.LABEL, style="QuickAdd.TLabel").pack(anchor=tk.W)
        self.amount_var = tk.StringVar()
        
        # Register validation function for amount field
        vcmd = (self.parent.register(InputValidation.validate_amount), '%P')
        
        self.amount_entry = ttk.Entry(
            amount_frame, 
            textvariable=self.amount_var, 
            font=config.Fonts.ENTRY, 
            width=15,
            validate='key', 
            validatecommand=vcmd,
            style='QuickAdd.TEntry'  # Apply theme-aware styling
        )
        self.amount_entry.pack(pady=(2, 0))  # 2px gap between label and entry
        
        # Description field (right, reduced width)
        desc_frame = ttk.Frame(row1_container, style="QuickAdd.TFrame")
        desc_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(desc_frame, text="Description:", font=config.Fonts.LABEL, style="QuickAdd.TLabel").pack(anchor=tk.W)
        
        # Use AutoCompleteEntry if description_history is available, otherwise plain Entry
        if self.description_history:
            # Auto-complete entry with recurring expense suggestions
            def get_suggestions(partial_text, limit=None):
                """Get suggestions, accepting optional limit parameter"""
                if limit is not None:
                    return self.description_history.get_suggestions(partial_text, limit=limit)
                else:
                    return self.description_history.get_suggestions(partial_text)
            
            self.description_entry = AutoCompleteEntry(
                desc_frame,
                get_suggestions_callback=get_suggestions,
                show_on_focus=self.description_history.should_show_on_focus(),
                min_chars=self.description_history.get_min_chars(),
                font=config.Fonts.ENTRY,
                style='QuickAdd.TCombobox'  # Apply theme-aware styling
            )
            self.description_entry.pack(fill=tk.X, pady=(2, 0))  # 2px gap between label and entry
        else:
            # Plain entry (fallback if no description_history)
            self.description_entry = ttk.Entry(desc_frame, 
                                             font=config.Fonts.ENTRY,
                                             style='QuickAdd.TEntry')  # Apply theme-aware styling
            self.description_entry.pack(fill=tk.X, pady=(2, 0))  # 2px gap between label and entry
        
        def handle_amount_enter(event):
            """Enter in amount field moves to description"""
            self.description_entry.focus_set()
            return "break"  # Prevent default behavior
        
        def handle_description_enter(event):
            """Enter in description field submits the form"""
            self.add_expense()
            return "break"  # Prevent default behavior
        
        self.amount_entry.bind('<Return>', handle_amount_enter)
        if hasattr(self.description_entry, 'entry'):
            self.description_entry.entry.bind('<Return>', handle_description_enter, add='+')
        else:
            self.description_entry.bind('<Return>', handle_description_enter)
        
        row2_container = ttk.Frame(self.frame, style="QuickAdd.TFrame")
        row2_container.pack(fill=tk.X, pady=(0, 0))
        
        date_frame = ttk.Frame(row2_container, style="QuickAdd.TFrame")
        date_frame.pack(side=tk.LEFT, padx=(0, 15))
        ttk.Label(date_frame, text="Date:", font=config.Fonts.LABEL, style="QuickAdd.TLabel").pack(anchor=tk.W)
        
        self.date_combo = CollapsibleDateCombobox(date_frame)
        self.date_combo.pack(pady=(2, 0))
        
        button_frame = ttk.Frame(row2_container, style="QuickAdd.TFrame")
        button_frame.pack(side=tk.LEFT, padx=(15, 0))
        ttk.Label(button_frame, text=" ", font=config.Fonts.LABEL, style="QuickAdd.TLabel").pack()
        self.add_button = ctk.CTkButton(
            button_frame, 
            text="+ Add Item", 
            command=self.add_expense,
            corner_radius=config.CustomTkinterTheme.CORNER_RADIUS,
            height=30,  # Match other buttons
            font=config.Fonts.BUTTON,
            fg_color=config.Colors.GREEN_PRIMARY,  # Green color like Add Expense button
            hover_color=config.Colors.GREEN_HOVER,
            text_color="white"
        )
        self.add_button.pack(pady=(2, 0))  # 2px gap after spacer label
        
        return self.frame
    
    def add_expense(self):
        """Validate and add expense from form. Handles cross-month routing and form clearing."""
        amount_str = self.amount_var.get().strip()
        if not amount_str:
            messagebox.showerror(config.Messages.TITLE_ERROR, config.Messages.AMOUNT_REQUIRED)
            return
        
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror(config.Messages.TITLE_ERROR, config.Messages.AMOUNT_POSITIVE)
                return
        except ValueError:
            messagebox.showerror(config.Messages.TITLE_ERROR, config.Messages.AMOUNT_INVALID)
            return
        
        description = self.description_entry.get().strip()
        if not description:
            messagebox.showerror(config.Messages.TITLE_ERROR, config.Messages.DESCRIPTION_REQUIRED)
            return
        
        selected_date = self.date_combo.get_selected_date()
        
        if not selected_date:
            messagebox.showerror(config.Messages.TITLE_ERROR, config.Messages.DATE_REQUIRED)
            return
        
        expense = ExpenseData(selected_date, amount, description)
        expense_dict = expense.to_dict()
        
        message = self.expense_tracker.add_expense_to_correct_month(expense_dict)
        
        if self.page_manager and self.table_manager:
            from page_manager import PageManager
            if self.page_manager.is_on_page(PageManager.PAGE_EXPENSE_LIST):
                self.table_manager.load_expenses(self.expense_tracker.expenses)
                
                if self.update_metrics_callback:
                    self.update_metrics_callback()
                
                if self.count_tracker:
                    self.count_tracker[0] = len(self.expense_tracker.expenses)
        
        if self.on_add_callback:
            self.on_add_callback()
        
        if self.status_manager:
            if message:
                # Message format: "💡 Past/Future expense saved to [Month] [Year] data folder ($amount)"
                self.status_manager.show(message, config.StatusBar.SUCCESS_ICON)
            else:
                # Normal current month expense
                self.status_manager.show(config.Messages.EXPENSE_ADDED, config.StatusBar.SUCCESS_ICON)
        
        # Clear form
        self.clear_form()
        
        # Focus back to amount field for quick entry
        self.focus_amount()
    
    def set_enabled(self, enabled, tooltip_text=None):
        """Enable or disable Quick Add fields (for archive mode)."""
        state = 'normal' if enabled else 'disabled'
        
        if self.amount_entry:
            self.amount_entry.config(state=state)
        
        if self.description_entry:
            # Handle both AutoCompleteEntry and plain Entry widgets
            if hasattr(self.description_entry, 'combo'):
                # AutoCompleteEntry - configure the underlying combobox
                self.description_entry.combo.config(state=state)
            else:
                # Plain Entry widget
                self.description_entry.config(state=state)
        
        if self.date_combo:
            # Combobox uses 'readonly' for normal state
            combo_state = 'readonly' if enabled else 'disabled'
            self.date_combo.combo.config(state=combo_state)
        
        if self.add_button:
            # Check if it's a CustomTkinter widget (use configure) or ttk/tk widget (use config)
            # CustomTkinter buttons have fg_color attribute and don't have config() method
            if isinstance(self.add_button, ctk.CTkButton) or (hasattr(self.add_button, 'fg_color') and not hasattr(self.add_button, 'config')):
                # CustomTkinter CTkButton path - use configure
                self.add_button.configure(state=state)
            else:
                # Legacy ttk.Button or tk.Button path - use config
                self.add_button.config(state=state)
            
            # Update tooltip if provided and GUI instance available
            if self.gui:
                if tooltip_text and not enabled:
                    # Remove old tooltip if exists
                    if hasattr(self.add_button, 'tooltip'):
                        self.add_button.tooltip.destroy()
                        del self.add_button.tooltip
                    
                    # Create new tooltip
                    self.gui.tooltip_manager.create(self.add_button, tooltip_text)
                elif enabled:
                    # Remove tooltip when enabled
                    if hasattr(self.add_button, 'tooltip'):
                        self.add_button.tooltip.destroy()
                        del self.add_button.tooltip
                    
                    # Add default tooltip
                    self.gui.tooltip_manager.create(self.add_button, "Quickly add a new expense")
    
    def clear_form(self):
        """Clear all form fields and reset to defaults."""
        if self.amount_var:
            self.amount_var.set('')
        
        if self.description_entry:
            # Handle both AutoCompleteEntry and plain Entry widgets
            if hasattr(self.description_entry, 'entry_var'):
                # AutoCompleteEntry - clear using StringVar
                self.description_entry.entry_var.set('')
            else:
                # Plain Entry widget
                self.description_entry.delete(0, tk.END)
        
        if self.date_combo:
            # Reset date to today using widget's method
            self.date_combo.set_default_date()
    
    def focus_amount(self):
        """Set focus to amount field (for quick entry)."""
        if self.amount_entry:
            self.amount_entry.focus_set()
    
    def get_button(self):
        """Get reference to the Add button (for tooltip management)."""
        return self.add_button

