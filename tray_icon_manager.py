#!/usr/bin/env python3
"""
Tray Icon Manager for LiteFinPad
Handles system tray icon creation, tooltip management, and updates.
"""

from datetime import datetime
from tray_icon import create_simple_tray_icon
from error_logger import log_info, log_error, log_debug


class TrayIconManager:
    """
    Manages the system tray icon for the application.
    
    Responsibilities:
    - Tray icon creation and initialization
    - Tooltip generation with monthly totals
    - Tooltip updates when data changes
    - Tray icon lifecycle management (stop/cleanup)
    """
    
    def __init__(self, expense_tracker):
        """
        Initialize tray icon manager.
        
        Args:
            expense_tracker: Reference to main ExpenseTracker instance
        """
        self.app = expense_tracker
        self.tray_icon = None
    
    def create(self):
        """
        Create and start the system tray icon.
        
        Sets up callbacks for:
        - Toggle window (left click)
        - Quick add dialog (double click)
        - Quit application (context menu)
        """
        try:
            log_info("Creating tray icon...")
            
            def toggle_app_main_thread():
                """Toggle app visibility - runs on main thread"""
                try:
                    if self.app.window_manager.is_hidden:
                        self.app.window_manager.show_window()
                    else:
                        self.app.window_manager.hide_window()
                except Exception as e:
                    log_error("Error in toggle_app", e)
            
            # Generate tooltip with monthly total
            tooltip = self.get_tooltip()
            
            # Create and start tray icon
            self.tray_icon = create_simple_tray_icon(
                # Thread-safe toggle: Use gui_queue.put() for main thread execution
                toggle_callback=lambda: self.app.gui_queue.put(toggle_app_main_thread),
                quick_add_callback=self.app.show_quick_add_dialog,
                # Thread-safe quit: Use gui_queue.put() for main thread execution
                quit_callback=lambda: self.app.gui_queue.put(self.app.quit_app),
                tooltip=tooltip
            )
            
            # Start the tray icon
            if self.tray_icon.start():
                log_info("Tray icon created and started successfully")
            else:
                log_error("Failed to start tray icon")
            
        except Exception as e:
            log_error("Error creating tray icon", e)
    
    def get_tooltip(self):
        """
        Generate tooltip text for tray icon with monthly total.
        
        Returns:
            str: Formatted tooltip with month name and total
                 Format: "LiteFinPad\nOctober 2025: $5,176.00"
        """
        try:
            # Get month name and year
            month_name = datetime.strptime(
                self.app.current_month, "%Y-%m"
            ).strftime("%B %Y")
            
            # Calculate monthly total
            monthly_total = sum(
                expense['amount'] for expense in self.app.expenses
            )
            
            # Format tooltip with line break
            tooltip = f"LiteFinPad\n{month_name}: ${monthly_total:,.2f}"
            return tooltip
        except Exception as e:
            log_error(f"Error generating tray tooltip: {e}")
            return "LiteFinPad\nExpense Tracker"
    
    def update_tooltip(self):
        """
        Update the tray icon tooltip with current monthly total.
        
        Called after:
        - Adding new expenses
        - Editing expenses
        - Deleting expenses
        - Importing data
        """
        try:
            if self.tray_icon:
                tooltip = self.get_tooltip()
                self.tray_icon.update_tooltip(tooltip)
                log_info(f"Tooltip updated successfully: {tooltip}")
        except Exception as e:
            log_error(f"Error updating tray tooltip: {e}")
    
    def stop(self):
        """
        Stop and cleanup the tray icon.
        
        Called during application shutdown.
        """
        try:
            if self.tray_icon:
                log_debug("Stopping tray icon...")
                self.tray_icon.stop()
                log_debug("Tray icon stopped")
        except Exception as e:
            log_error(f"Error stopping tray icon: {e}")

