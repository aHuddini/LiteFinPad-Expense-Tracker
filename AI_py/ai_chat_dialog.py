# AI_py/ai_chat_dialog.py
"""Standalone AI chat dialog window - 100% CustomTkinter."""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from theme_manager import ThemeManager
from AI_py.query_engine import QueryEngine
from AI_py.ai_manager import AIManager
from AI_py.chat_logger import ChatLogger
from error_logger import log_info, log_error

class AIChatDialog:
    """Standalone AI chat dialog window - CustomTkinter only."""
    
    def __init__(self, parent, expense_tracker):
        """Initialize chat dialog."""
        self.parent = parent
        self.expense_tracker = expense_tracker
        
        self.theme_manager = ThemeManager()
        self.ai_manager = AIManager(expense_tracker)
        self.chat_logger = ChatLogger()
        self.dialog = None
        self.chat_history = None
        self.query_entry = None
        self._thinking_line_start = None  # Track thinking indicator position
        self._thinking_steps_start = None  # Track where thinking steps begin
        self._current_thinking_steps = []  # Track thinking steps for logging
        
        # Start chat session logging
        model = self.ai_manager.get_preferred_model()
        self.chat_logger.start_session(model)
        log_info(f"AI Chat session started - logging to: {self.chat_logger.session_file}")
        
        self._create_dialog()
    
    def _create_dialog(self):
        """Create the chat dialog window."""
        colors = self.theme_manager.get_colors()
        bg_color = colors.BG_SECONDARY if self.theme_manager.is_dark_mode() else colors.BG_LIGHT_GRAY
        
        # Create standalone window (CTkToplevel for CustomTkinter)
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("AI Chat - LiteFinPad")
        self.dialog.geometry("800x700")  # Wider to accommodate summary panel
        
        # Set appearance mode to match main app
        ctk.set_appearance_mode("dark" if self.theme_manager.is_dark_mode() else "light")
        
        # Independent window (not modal - allows interaction with parent)
        # No transient() or grab_set() - window operates independently
        
        # Prevent resizing
        self.dialog.resizable(False, False)
        
        # Build chat interface (100% CustomTkinter)
        self._build_chat_ui()
        
        # Center dialog on screen
        self._center_dialog()
        
        # Focus on input field
        self.dialog.after(100, lambda: self.query_entry.focus_set())
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_close)
        
        log_info("AI Chat dialog created")
    
    def _build_chat_ui(self):
        """Build the chat interface using only CustomTkinter widgets."""
        colors = self.theme_manager.get_colors()
        bg_color = colors.BG_SECONDARY if self.theme_manager.is_dark_mode() else colors.BG_LIGHT_GRAY
        text_color = colors.TEXT_BLACK
        
        # Main container with horizontal layout
        main_container = ctk.CTkFrame(self.dialog, fg_color=bg_color, corner_radius=0)
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Left side: Chat interface
        chat_frame = ctk.CTkFrame(main_container, fg_color=bg_color, corner_radius=0)
        chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Right side: Expense summary panel
        summary_frame = ctk.CTkFrame(main_container, fg_color=bg_color, corner_radius=5, width=200)
        summary_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        summary_frame.pack_propagate(False)
        
        # Build summary panel
        self._build_summary_panel(summary_frame, colors, text_color)
        
        # Title (CTkLabel) - in chat frame
        title = ctk.CTkLabel(
            chat_frame,
            text="💬 AI Expense Assistant",
            font=config.Fonts.TITLE,
            text_color=text_color
        )
        title.pack(pady=(10, 5))
        
        # Status indicator (CTkLabel) - dynamic model name
        if self.ai_manager.can_use_ai_chat():
            model_name = self.ai_manager.get_preferred_model()
            # Format model name for display (e.g., "qwen:0.5b" -> "Qwen 0.5B")
            model_display = model_name.replace('smollm:', 'SmolLM ').replace('qwen:', 'Qwen ').replace('tinyllama', 'TinyLlama 1.1B').upper()
            status_text = f"🟢 AI Ready ({model_display})"
            status_color = colors.GREEN_PRIMARY
        else:
            model_name = self.ai_manager.get_preferred_model()
            status_text = f"🔴 AI Not Available - Model {model_name} not found"
            status_color = colors.RED_PRIMARY
        
        status_label = ctk.CTkLabel(
            chat_frame,
            text=status_text,
            font=config.get_font(config.Fonts.SIZE_SMALL),
            text_color=status_color
        )
        status_label.pack(pady=(0, 15))
        
        # Chat history (CTkTextbox - CustomTkinter's scrollable text widget)
        chat_bg = colors.BG_WHITE if not self.theme_manager.is_dark_mode() else colors.BG_TERTIARY
        self.chat_history = ctk.CTkTextbox(
            chat_frame,
            width=500,
            height=450,
            font=config.Fonts.LABEL,
            fg_color=chat_bg,
            text_color=text_color,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.chat_history.pack(padx=10, pady=(0, 15), fill=tk.BOTH, expand=True)
        
        # Welcome message
        self.chat_history.configure(state=tk.NORMAL)
        welcome_msg = "AI Assistant: Hi! I can help you manage expenses.\n"
        welcome_msg += "Try: 'Add $50 for groceries' or 'What's my largest expense?'\n\n"
        self.chat_history.insert("1.0", welcome_msg)
        self.chat_history.configure(state=tk.DISABLED)
        
        # Input frame (CTkFrame)
        input_frame = ctk.CTkFrame(chat_frame, fg_color="transparent", corner_radius=0)
        input_frame.pack(padx=10, pady=(0, 10), fill=tk.X)
        
        # Input entry (CTkEntry)
        self.query_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Ask a question or add an expense...",
            font=config.Fonts.LABEL,
            height=config.CustomTkinterTheme.ENTRY_HEIGHT
        )
        self.query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        def on_submit():
            user_input = self.query_entry.get().strip()
            if not user_input:
                return
            
            # Check if AI is available
            if not self.ai_manager.can_use_ai_chat():
                model_name = self.ai_manager.get_preferred_model()
                self._add_message(f"❌ AI features require the {model_name} model.\n")
                self._add_message(f"Please ensure the model file is available in the ./models/ directory.\n")
                self._add_message(f"Expected file: {model_name.replace(':', '-')}.gguf\n\n")
                return
            
            # Add user message to chat
            self._add_message(f"You: {user_input}\n\n")
            
            # Clear input
            self.query_entry.delete(0, tk.END)
            
            # Show thinking indicator
            self._show_thinking()
            self.dialog.update()
            
            # Process input (determines intent: query/add/edit)
            try:
                engine = QueryEngine(self.expense_tracker)
                
                # Reset thinking steps for this exchange
                self._current_thinking_steps = []
                self._thinking_steps_start = None  # Track where thinking steps begin
                
                # Define thinking callback to show steps in real-time
                def show_thinking_step(step_msg):
                    """Show thinking step in chat and log it."""
                    self._current_thinking_steps.append(step_msg)
                    # Track where thinking steps start (first step)
                    if self._thinking_steps_start is None:
                        self._thinking_steps_start = self.chat_history.index(tk.END + "-1c")
                    self._add_message(f"💭 {step_msg}\n", color="gray")
                    self.dialog.update()  # Update UI immediately
                
                result = engine.process(user_input, thinking_callback=show_thinking_step)
                
                # Remove only the "Thinking..." indicator, keep all thinking steps visible
                self._hide_thinking_indicator_only()
                
                # Add separator before final response
                if self._current_thinking_steps:
                    self._add_message("─" * 50 + "\n", color="gray")
                
                self._add_message(f"AI: {result['response']}\n\n")
                
                # Count expenses for logging
                expenses_added = len(result.get('expenses_to_add', []))
                expenses_deleted = result.get('expenses_deleted_count', 0)
                
                # Log the exchange
                self.chat_logger.log_exchange(
                    user_input=user_input,
                    ai_response=result['response'],
                    intent=result.get('intent', 'unknown'),
                    thinking_steps=self._current_thinking_steps,
                    expenses_added=expenses_added,
                    expenses_deleted=expenses_deleted
                )
                
                # Handle expense additions
                if result['intent'] == 'add' and result['expenses_to_add']:
                    self._handle_expense_addition(result)
                
                # Handle expense deletions (single or batch)
                if result['intent'] == 'delete':
                    self._handle_expense_deletion(result)
                    
            except Exception as e:
                log_error(f"Error processing AI request: {e}", e)
                self._hide_thinking_indicator_only()
                error_msg = f"❌ Error: {str(e)}"
                self._add_message(f"{error_msg}\n\n")
                
                # Log error exchange
                self.chat_logger.log_exchange(
                    user_input=user_input,
                    ai_response=error_msg,
                    intent='error',
                    thinking_steps=self._current_thinking_steps
                )
        
        # Send button (CTkButton)
        submit_btn = ctk.CTkButton(
            input_frame,
            text="Send",
            command=on_submit,
            font=config.Fonts.BUTTON,
            width=100,
            height=config.CustomTkinterTheme.BUTTON_HEIGHT
        )
        submit_btn.pack(side=tk.RIGHT)
        
        # Bind Enter key
        self.query_entry.bind('<Return>', lambda e: on_submit())
    
    def _build_summary_panel(self, parent_frame, colors, text_color):
        """Build the expense summary panel on the right side."""
        from datetime import datetime
        
        # Panel title
        title = ctk.CTkLabel(
            parent_frame,
            text="📊 Quick Summary",
            font=config.Fonts.TITLE,
            text_color=text_color
        )
        title.pack(pady=(15, 10))
        
        # Current month display
        current_month = self.expense_tracker.viewed_month
        try:
            month_obj = datetime.strptime(current_month, '%Y-%m')
            month_display = month_obj.strftime('%B %Y')
        except:
            month_display = current_month
        
        month_label = ctk.CTkLabel(
            parent_frame,
            text=f"📅 {month_display}",
            font=config.get_font(config.Fonts.SIZE_MEDIUM),
            text_color=text_color
        )
        month_label.pack(pady=(0, 15))
        
        # Total spending
        total = self.expense_tracker.monthly_total
        total_label = ctk.CTkLabel(
            parent_frame,
            text=f"💰 Total: ${total:,.2f}",
            font=config.get_font(config.Fonts.SIZE_MEDIUM, weight='bold'),
            text_color=colors.GREEN_PRIMARY if total > 0 else text_color
        )
        total_label.pack(pady=(0, 10))
        
        # Expense count
        count = len(self.expense_tracker.expenses)
        count_label = ctk.CTkLabel(
            parent_frame,
            text=f"📝 {count} expense{'s' if count != 1 else ''}",
            font=config.get_font(config.Fonts.SIZE_SMALL),
            text_color=text_color
        )
        count_label.pack(pady=(0, 15))
        
        # Recent expenses list
        list_title = ctk.CTkLabel(
            parent_frame,
            text="Recent Expenses:",
            font=config.get_font(config.Fonts.SIZE_SMALL, weight='bold'),
            text_color=text_color
        )
        list_title.pack(pady=(0, 5))
        
        # Scrollable text for expenses
        list_bg = colors.BG_WHITE if not self.theme_manager.is_dark_mode() else colors.BG_TERTIARY
        self.expense_list = ctk.CTkTextbox(
            parent_frame,
            width=180,
            height=300,
            font=config.get_font(config.Fonts.SIZE_SMALL),
            fg_color=list_bg,
            text_color=text_color,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.expense_list.pack(padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)
        
        # Update expense list
        self._update_expense_list()
    
    def _update_expense_list(self):
        """Update the expense list in the summary panel."""
        self.expense_list.configure(state=tk.NORMAL)
        self.expense_list.delete("1.0", tk.END)
        
        # Show last 10 expenses (most recent first)
        expenses = sorted(
            self.expense_tracker.expenses,
            key=lambda x: x.get('date', ''),
            reverse=True
        )[:10]
        
        if not expenses:
            self.expense_list.insert("1.0", "No expenses yet.")
        else:
            for exp in expenses:
                amount = exp.get('amount', 0)
                desc = exp.get('description', 'Unknown')
                date = exp.get('date', '')
                
                # Format date (show day only if in current month)
                try:
                    from datetime import datetime
                    date_obj = datetime.strptime(date, '%Y-%m-%d')
                    date_str = date_obj.strftime('%b %d')
                except:
                    date_str = date
                
                # Truncate description if too long
                if len(desc) > 20:
                    desc = desc[:17] + "..."
                
                line = f"${amount:,.2f} - {desc}\n{date_str}\n\n"
                self.expense_list.insert(tk.END, line)
        
        self.expense_list.configure(state=tk.DISABLED)
        self.expense_list.see("1.0")
    
    def _add_message(self, message: str, color=None):
        """Add a message to the chat history."""
        self.chat_history.configure(state=tk.NORMAL)
        
        # If color specified, try to use text color tag (CustomTkinter supports this)
        if color:
            # For gray thinking steps, use a lighter color
            if color == "gray":
                # Insert with a tag for styling (if supported)
                start = self.chat_history.index(tk.END)
                self.chat_history.insert(tk.END, message)
                end = self.chat_history.index(tk.END)
                # Note: CustomTkinter CTkTextbox may not support tags, so we'll just use the message
                # The emoji prefix (💭) already makes it visually distinct
        else:
            self.chat_history.insert(tk.END, message)
        
        self.chat_history.configure(state=tk.DISABLED)
        self.chat_history.see(tk.END)
    
    def _show_thinking(self):
        """Show thinking indicator in chat."""
        self.chat_history.configure(state=tk.NORMAL)
        self._thinking_line_start = self.chat_history.index(tk.END + "-1c")
        self.chat_history.insert(tk.END, "AI: Thinking...\n")
        self.chat_history.configure(state=tk.DISABLED)
        self.chat_history.see(tk.END)
    
    def _hide_thinking(self):
        """Remove thinking indicator from chat (legacy method - kept for compatibility)."""
        self._hide_thinking_indicator_only()
    
    def _hide_thinking_indicator_only(self):
        """Remove only the 'AI: Thinking...' indicator, keeping all thinking steps visible."""
        if self._thinking_line_start:
            self.chat_history.configure(state=tk.NORMAL)
            # Find the end of the "AI: Thinking..." line (just that line, not all content)
            try:
                line_end = self.chat_history.index(f"{self._thinking_line_start} lineend")
                # Delete only the thinking indicator line, not the thinking steps
                self.chat_history.delete(self._thinking_line_start, f"{line_end}+1c")
            except:
                # Fallback: if lineend doesn't work, just delete the line
                self.chat_history.delete(self._thinking_line_start, f"{self._thinking_line_start} lineend+1c")
            self.chat_history.configure(state=tk.DISABLED)
            self._thinking_line_start = None
    
    def _handle_expense_addition(self, result: dict):
        """Handle expense addition - automatically add without confirmation."""
        # Always add expenses directly without confirmation popup
        self._add_expenses(result['expenses_to_add'])
    
    def _handle_expense_deletion(self, result: dict):
        """Handle expense deletion - refresh display after deletion."""
        # Reload expense table if we're on the expense list page
        if hasattr(self.expense_tracker.gui, 'table_manager') and self.expense_tracker.gui.table_manager:
            from page_manager import PageManager
            if self.expense_tracker.gui.page_manager.is_on_page(PageManager.PAGE_EXPENSE_LIST):
                self.expense_tracker.gui.table_manager.load_expenses(self.expense_tracker.expenses)
                # Update metrics if callback exists
                if hasattr(self.expense_tracker.gui, 'update_expense_metrics'):
                    self.expense_tracker.gui.update_expense_metrics()
        
        # Update display (updates totals, counts, etc.)
        self.expense_tracker.gui.update_display()
        self.expense_tracker.tray_icon_manager.update_tooltip()
        
        # Update summary panel
        self._update_expense_list()
        
        # Confirm in chat (check if batch delete)
        deleted_count = len(result.get('deleted_expense_indices', [])) or (1 if 'deleted_expense_index' in result else 0)
        if deleted_count > 1:
            self._add_message(f"✅ {deleted_count} expenses deleted!\n\n")
        else:
            self._add_message(f"✅ Expense deleted!\n\n")
    
    def _add_expenses(self, expenses_to_add: list):
        """Add expenses to the expense tracker."""
        for exp_dict in expenses_to_add:
            message = self.expense_tracker.add_expense_to_correct_month(exp_dict)
            if message:
                self._add_message(f"ℹ️ {message}\n\n")
        
        # Reload expense table if we're on the expense list page
        if hasattr(self.expense_tracker.gui, 'table_manager') and self.expense_tracker.gui.table_manager:
            from page_manager import PageManager
            if self.expense_tracker.gui.page_manager.is_on_page(PageManager.PAGE_EXPENSE_LIST):
                self.expense_tracker.gui.table_manager.load_expenses(self.expense_tracker.expenses)
                # Update metrics if callback exists
                if hasattr(self.expense_tracker.gui, 'update_expense_metrics'):
                    self.expense_tracker.gui.update_expense_metrics()
        
        # Update display (updates totals, counts, etc.)
        self.expense_tracker.gui.update_display()
        self.expense_tracker.tray_icon_manager.update_tooltip()
        
        # Update summary panel
        self._update_expense_list()
        
        # Confirm in chat
        count = len(expenses_to_add)
        if count == 1:
            self._add_message(f"✅ Expense added!\n\n")
        else:
            self._add_message(f"✅ Added {count} expense(s) successfully!\n\n")
    
    def _center_dialog(self):
        """Center dialog on parent window."""
        self.dialog.update_idletasks()
        
        # Get parent window position
        try:
            parent_x = self.parent.winfo_x()
            parent_y = self.parent.winfo_y()
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()
        except:
            # If parent window not available, center on screen
            parent_x = 0
            parent_y = 0
            parent_width = 0
            parent_height = 0
        
        # Get dialog size
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        # Calculate centered position
        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)
        
        # Ensure dialog stays on screen
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        
        x = max(0, min(x, screen_width - dialog_width))
        y = max(0, min(y, screen_height - dialog_height))
        
        self.dialog.geometry(f"+{x}+{y}")
    
    def _on_close(self):
        """Handle window close event."""
        # End chat session logging
        self.chat_logger.end_session()
        log_info(f"AI Chat dialog closed - session log saved to: {self.chat_logger.session_file}")
        self.dialog.destroy()

