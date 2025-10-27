"""
Status Bar Manager Module for LiteFinPad v3.5.3+
================================================

Centralized status bar management for displaying user feedback messages.

Features:
- Minimal, purposeful feedback for important operations
- Auto-clear timer (configurable)
- Icon support for visual categorization
- Show/hide for different pages
- Clean API for status updates

Usage:
    status_manager = StatusBarManager(parent_widget)
    frame = status_manager.create_ui()
    # Grid the frame where needed
    
    # Show status message
    status_manager.show("Expense added", icon="✓", auto_clear=True)
    
    # Clear status
    status_manager.clear()
    
    # Show/hide status bar
    status_manager.set_visible(True)
"""

import tkinter as tk
from tkinter import ttk
import config


class StatusBarManager:
    """
    Manages status bar UI and messaging for the application.
    
    Provides a clean interface for showing/clearing status messages with
    automatic timer management and visibility control.
    """
    
    def __init__(self, parent_widget, config_module=None):
        """
        Initialize the status bar manager.
        
        Args:
            parent_widget: Tkinter parent widget (root window or frame)
            config_module: Optional config module (defaults to imported config)
        """
        self.parent = parent_widget
        self.config = config_module if config_module else config
        
        # Status bar widgets (created in create_ui())
        self.status_bar_frame = None
        self.status_label = None
        
        # Timer management
        self.status_clear_timer = None
    
    def create_ui(self) -> tk.Frame:
        """
        Create and return the status bar frame widget.
        
        Note: The frame is NOT gridded by this method. The caller should
        grid it where appropriate (e.g., at the bottom of the window).
        
        Returns:
            tk.Frame: The status bar frame widget
        """
        # Status bar frame
        self.status_bar_frame = tk.Frame(
            self.parent,
            bg=self.config.StatusBar.BG_COLOR,
            height=self.config.StatusBar.HEIGHT,
            relief=tk.FLAT,
            borderwidth=0
        )
        
        # Prevent frame from shrinking
        self.status_bar_frame.grid_propagate(False)
        
        # Add top border for separation
        separator = tk.Frame(
            self.status_bar_frame,
            bg=self.config.StatusBar.BORDER_COLOR,
            height=1
        )
        separator.pack(side=tk.TOP, fill=tk.X)
        
        # Status label (left-aligned with minimal padding)
        self.status_label = tk.Label(
            self.status_bar_frame,
            text="",
            bg=self.config.StatusBar.BG_COLOR,
            fg=self.config.StatusBar.TEXT_COLOR,
            font=self.config.get_font(self.config.Fonts.SIZE_SMALL),
            anchor='w',
            padx=10,
            pady=3
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        return self.status_bar_frame
    
    def show(self, message: str, icon: str = 'ℹ️', auto_clear: bool = True):
        """
        Display a status message in the status bar.
        
        Args:
            message: The message text to display
            icon: Icon to show before the message (default: info icon)
            auto_clear: Whether to automatically clear after delay (default: True)
        
        Example:
            manager.show("Expense added", icon="✓")
            manager.show("Export failed", icon="⚠", auto_clear=False)
        """
        if not self.status_label:
            return  # Status bar not created yet
        
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
        """
        Manually clear the status bar message.
        
        This cancels any pending auto-clear timer and clears the displayed text.
        """
        if not self.status_label:
            return
        
        self.status_label.config(text="")
        self._cancel_timer()
    
    def set_visible(self, visible: bool):
        """
        Show or hide the status bar.
        
        Args:
            visible: True to show, False to hide
        
        Note: The status bar frame must have been gridded before calling this.
        This method uses grid()/grid_remove() for visibility control.
        """
        if not self.status_bar_frame:
            return
        
        if visible:
            # Show status bar (assumes it was gridded with proper row/column)
            self.status_bar_frame.grid()
        else:
            # Hide status bar
            self.status_bar_frame.grid_remove()
    
    def _cancel_timer(self):
        """
        Cancel the auto-clear timer if one is active.
        
        Private method for internal timer management.
        """
        if self.status_clear_timer:
            self.parent.after_cancel(self.status_clear_timer)
            self.status_clear_timer = None

