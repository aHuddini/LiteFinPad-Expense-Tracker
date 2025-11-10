"""Reusable dialog creation and positioning utilities."""

import tkinter as tk
from tkinter import ttk
import config


class DialogHelper:
    """Static helper methods for creating and managing dialogs."""
    
    @staticmethod
    def create_dialog(parent, title, width, height, colors=None):
        """Create a standard Toplevel dialog with common settings."""
        if colors is None:
            colors = config.Colors
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.resizable(False, False)
        dialog.transient(parent)
        dialog_bg = colors.BG_SECONDARY if hasattr(colors, 'BG_SECONDARY') and hasattr(colors, 'BG_MAIN') else colors.BG_DIALOG
        dialog.configure(bg=dialog_bg)
        dialog.geometry(f"{width}x{height}")
        dialog.withdraw()
        return dialog
    
    @staticmethod
    def create_dialog_no_transient(parent, title, width, height, colors=None):
        """Create Toplevel dialog without transient setting (works independently of parent)."""
        if colors is None:
            colors = config.Colors
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.resizable(False, False)
        dialog_bg = colors.BG_SECONDARY if hasattr(colors, 'BG_SECONDARY') and hasattr(colors, 'BG_MAIN') else colors.BG_DIALOG
        dialog.configure(bg=dialog_bg)
        dialog.geometry(f"{width}x{height}")
        dialog.withdraw()
        return dialog
    
    @staticmethod
    def create_content_frame(dialog, padding="15"):
        """Create a standard content frame for dialogs."""
        content_frame = ttk.Frame(dialog, padding=padding)
        content_frame.pack(fill=tk.BOTH, expand=True)
        return content_frame
    
    @staticmethod
    def center_on_parent(dialog, parent, dialog_width, dialog_height):
        """Center the dialog over its parent window."""
        dialog.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)
        
        dialog.geometry(f"+{x}+{y}")
    
    @staticmethod
    def position_lower_right(dialog, parent, dialog_width, dialog_height):
        """Position dialog in lower-right corner relative to parent with screen boundary checks."""
        dialog.update_idletasks()
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        
        # Calculate position relative to parent's lower-right
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        x = parent_x + parent_width - dialog_width
        y = parent_y + parent_height - dialog_height
        
        if x + dialog_width > screen_width:
            x = screen_width - dialog_width - config.Window.MARGIN_RIGHT
        if y + dialog_height > screen_height:
            y = screen_height - dialog_height - config.Window.MARGIN_BOTTOM
        if x < config.Window.MARGIN_LEFT:
            x = config.Window.MARGIN_LEFT
        if y < config.Window.MARGIN_TOP:
            y = config.Window.MARGIN_TOP
        
        dialog.geometry(f"+{x}+{y}")
    
    @staticmethod
    def position_right_of_parent(dialog, parent, dialog_width, dialog_height, gap=10):
        """Position dialog to the right of parent with fallbacks (left or center if off-screen)."""
        dialog.update_idletasks()
        
        # Get parent position and size
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        
        x = parent_x + parent_width + gap
        y = parent_y
        
        if x + dialog_width > screen_width:
            x = parent_x - dialog_width - gap
            
            if x < 0:
                x = (screen_width - dialog_width) // 2
                y = (screen_height - dialog_height) // 2
        
        dialog.geometry(f"+{x}+{y}")
    
    @staticmethod
    def position_with_main_window(dialog, screen_width, screen_height, 
                                   main_width=650, main_height=725, offset=450,
                                   dialog_width=None, dialog_height=None):
        """Position dialog to align with main window in lower-right corner (screen-relative)."""
        if dialog_width is None or dialog_height is None:
            dialog.update_idletasks()
            dialog_width = dialog.winfo_reqwidth()
            dialog_height = dialog.winfo_reqheight()
        
        x = screen_width - main_width - 20
        y = screen_height - main_height - offset
        
        if y < 20:
            y = 20
        if x < 20:
            x = 20
        
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    @staticmethod
    def bind_escape_to_close(dialog):
        """Bind Escape key to close the dialog."""
        dialog.bind('<Escape>', lambda e: dialog.destroy())
    
    @staticmethod
    def bind_escape_with_cleanup(dialog, cleanup_callback):
        """Bind Escape key to close dialog with custom cleanup logic."""
        dialog.bind('<Escape>', lambda e: cleanup_callback())
    
    @staticmethod
    def show_dialog(dialog, grab_set=True, focus_set=True):
        """Show dialog and optionally grab focus."""
        dialog.deiconify()
        if grab_set:
            dialog.grab_set()
        if focus_set:
            dialog.focus_set()

