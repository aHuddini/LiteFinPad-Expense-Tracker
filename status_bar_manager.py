"""Centralized status bar management for displaying user feedback messages."""

import tkinter as tk
from tkinter import ttk
import config


class StatusBarManager:
    """Manages status bar UI and messaging for the application."""
    
    def __init__(self, parent_widget, config_module=None, theme_manager=None):
        """Initialize the status bar manager."""
        self.parent = parent_widget
        self.config = config_module if config_module else config
        self.theme_manager = theme_manager
        
        # Status bar widgets (created in create_ui())
        self.status_bar_frame = None
        self.status_label = None
        
        # Timer management
        self.status_clear_timer = None
    
    def create_ui(self) -> tk.Frame:
        """Create and return the status bar frame widget. Caller must grid it."""
        # Get theme-aware colors
        if self.theme_manager:
            colors = self.theme_manager.get_colors()
            is_dark = self.theme_manager.is_dark_mode()
            # Use BG_TERTIARY (#2d2d30) in dark mode for dark gray status bar
            # Use BG_COLOR (#e5e5e5) in light mode
            bg_color = colors.BG_TERTIARY if is_dark else self.config.StatusBar.BG_COLOR
            # Use white text in dark mode for maximum visibility
            text_color = '#ffffff' if is_dark else self.config.StatusBar.TEXT_COLOR
            # Use BG_DARK_GRAY for border in dark mode, BORDER_COLOR in light mode
            border_color = colors.BG_DARK_GRAY if is_dark else self.config.StatusBar.BORDER_COLOR
        else:
            bg_color = self.config.StatusBar.BG_COLOR
            text_color = self.config.StatusBar.TEXT_COLOR
            border_color = self.config.StatusBar.BORDER_COLOR
        
        # Status bar frame
        self.status_bar_frame = tk.Frame(
            self.parent,
            bg=bg_color,
            height=self.config.StatusBar.HEIGHT,
            relief=tk.FLAT,
            borderwidth=0
        )
        
        # Prevent frame from shrinking
        self.status_bar_frame.grid_propagate(False)
        
        # Add top border for separation
        separator = tk.Frame(
            self.status_bar_frame,
            bg=border_color,
            height=1
        )
        separator.pack(side=tk.TOP, fill=tk.X)
        
        # Status label (left-aligned with minimal padding)
        self.status_label = tk.Label(
            self.status_bar_frame,
            text="",
            bg=bg_color,
            fg=text_color,
            font=self.config.get_font(self.config.Fonts.SIZE_SMALL),
            anchor='w',
            padx=10,
            pady=3
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        return self.status_bar_frame
    
    def show(self, message: str, icon: str = 'ℹ️', auto_clear: bool = True):
        """Display a status message in the status bar."""
        if not self.status_label:
            return  # Status bar not created yet
        
        # Refresh theme-aware colors in case theme changed
        if self.theme_manager:
            colors = self.theme_manager.get_colors()
            is_dark = self.theme_manager.is_dark_mode()
            bg_color = colors.BG_TERTIARY if is_dark else self.config.StatusBar.BG_COLOR
            text_color = '#ffffff' if is_dark else self.config.StatusBar.TEXT_COLOR
            
            # Update frame and label colors
            self.status_bar_frame.configure(bg=bg_color)
            self.status_label.configure(bg=bg_color, fg=text_color)
        
        # Update label text
        self.status_label.config(text=f"{icon} {message}")
        
        # Cancel any existing timer
        self._cancel_timer()
        
        # Schedule auto-clear if enabled
        if auto_clear:
            self.status_clear_timer = self.parent.after(
                self.config.StatusBar.CLEAR_DELAY_MS,
                self.clear
            )
    
    def clear(self):
        """Manually clear the status bar message and cancel any pending auto-clear timer."""
        if not self.status_label:
            return
        
        self.status_label.config(text="")
        self._cancel_timer()
    
    def set_visible(self, visible: bool):
        """Show or hide the status bar. Frame must be gridded before calling this."""
        if not self.status_bar_frame:
            return
        
        if visible:
            # Show status bar (assumes it was gridded with proper row/column)
            self.status_bar_frame.grid()
        else:
            # Hide status bar
            self.status_bar_frame.grid_remove()
    
    def _cancel_timer(self):
        """Cancel the auto-clear timer if one is active."""
        if self.status_clear_timer:
            self.parent.after_cancel(self.status_clear_timer)
            self.status_clear_timer = None

