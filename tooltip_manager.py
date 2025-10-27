"""
LiteFinPad - Tooltip Manager
Handles tooltip creation, updates, and lifecycle management for GUI widgets.
"""

import tkinter as tk
import config


class TooltipManager:
    """
    Manages tooltips for GUI widgets.
    
    Provides centralized tooltip creation, positioning, styling, and updates.
    """
    
    def __init__(self):
        """Initialize the tooltip manager"""
        pass
    
    def create(self, widget, text):
        """
        Create a tooltip for a widget.
        
        Args:
            widget: The tkinter widget to attach the tooltip to
            text: The tooltip text to display
        """
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_attributes('-topmost', True)  # Ensure tooltip appears on top
            
            # Create label first to get its size
            label = tk.Label(
                tooltip,
                text=text,
                background="lightyellow",
                relief="solid",
                borderwidth=1,
                font=config.Fonts.LABEL_SMALL
            )
            label.pack()
            
            # Update to get actual size
            tooltip.update_idletasks()
            tooltip_width = tooltip.winfo_width()
            
            # Position tooltip to the LEFT of cursor to prevent off-screen overflow
            x_pos = event.x_root - tooltip_width - 10
            y_pos = event.y_root + 10
            
            tooltip.wm_geometry(f"+{x_pos}+{y_pos}")
            widget.tooltip = tooltip
            
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
                
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def update(self, widget, new_text):
        """
        Update the tooltip text for a widget.
        
        Args:
            widget: The widget whose tooltip to update
            new_text: The new tooltip text
        """
        # Destroy existing tooltip if visible
        if hasattr(widget, 'tooltip'):
            widget.tooltip.destroy()
            del widget.tooltip
        
        # Recreate tooltip with new text
        self.create(widget, new_text)
    
    def destroy(self, widget):
        """
        Destroy the tooltip for a widget.
        
        Args:
            widget: The widget whose tooltip to destroy
        """
        if hasattr(widget, 'tooltip'):
            widget.tooltip.destroy()
            del widget.tooltip

