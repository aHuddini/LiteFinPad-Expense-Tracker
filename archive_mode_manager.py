"""Archive mode manager - handles UI styling and behavior when viewing past/future months."""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import calendar
import config
import customtkinter as ctk


class ArchiveModeManager:
    """Manages archive mode UI styling and behavior."""
    
    def __init__(self, root, expense_tracker, page_manager=None, 
                 main_frame=None, expense_list_frame=None,
                 main_container=None,
                 month_label=None, add_expense_btn=None, 
                 quick_add_helper=None, table_manager=None,
                 tooltip_creator=None,
                 update_display_callback=None,
                 update_metrics_callback=None,
                 theme_manager=None):
        """Initialize the Archive Mode Manager."""
        self.root = root
        self.expense_tracker = expense_tracker
        self.page_manager = page_manager
        self.main_frame = main_frame
        self.expense_list_frame = expense_list_frame
        self.main_container = main_container
        self.month_label = month_label
        self.add_expense_btn = add_expense_btn
        self.quick_add_helper = quick_add_helper
        self.table_manager = table_manager
        self.tooltip_creator = tooltip_creator
        self.update_display_callback = update_display_callback
        self.update_metrics_callback = update_metrics_callback
        self.theme_manager = theme_manager
    
    def is_archive_mode(self):
        """Check if viewing past/future month (archive mode) vs current month."""
        viewed_month = getattr(self.expense_tracker, 'viewed_month', None)
        if viewed_month is None:
            return False
        
        current_month_key = datetime.now().strftime('%Y-%m')
        return viewed_month != current_month_key
    
    def get_context_date(self):
        """Get context date for analytics: last day of viewed month (archive) or current date (normal)."""
        if self.is_archive_mode():
            viewed_month = self.expense_tracker.viewed_month
            year, month = map(int, viewed_month.split('-'))
            last_day = calendar.monthrange(year, month)[1]
            return datetime(year, month, last_day)
        else:
            return datetime.now()
    
    def refresh_ui(self):
        """Update UI styling based on viewing mode (current vs archive)."""
        viewing_mode = self.expense_tracker.viewing_mode
        viewed_month = self.expense_tracker.viewed_month
        
        try:
            with open('version.txt', 'r') as f:
                version = f.read().strip()
        except:
            version = "Unknown"
        
        month_display_text = self.expense_tracker.month_viewer.format_month_display(
            viewed_month,
            include_archive_indicator=False
        )
        
        if viewing_mode == "archive":
            self._apply_archive_mode(version, month_display_text)
        else:
            self._apply_normal_mode(version, month_display_text)
        
        if self.update_display_callback:
            try:
                self.update_display_callback()
            except Exception as e:
                from error_logger import log_error
                log_error(f"Error calling update_display_callback: {e}", e)
        else:
            from error_logger import log_warning
            log_warning("update_display_callback is None - display will not update")
        
        # Update ttk.Style configurations first (before widget updates)
        self._update_ttk_styles(viewing_mode == "archive")
        
        # Re-apply styles after update_display() runs
        archive = viewing_mode == "archive"
        
        if self.main_frame:
            self.apply_styles_to_widgets(self.main_frame, archive=archive)
            self.apply_customtkinter_styles(self.main_frame, archive=archive)
        
        if self.expense_list_frame:
            self.apply_styles_to_widgets(self.expense_list_frame, archive=archive)
            self.apply_customtkinter_styles(self.expense_list_frame, archive=archive)
        
        try:
            self.root.update_idletasks()
            self.root.update_idletasks()
            self.root.update()
        except:
            pass
        
        if (self.page_manager and self.page_manager.is_on_page("expense_list") 
            and self.table_manager):
            self.table_manager.load_expenses(self.expense_tracker.expenses)
            if hasattr(self.table_manager, 'refresh_status_bar_style'):
                self.table_manager.refresh_status_bar_style()
            if self.update_metrics_callback:
                self.update_metrics_callback()
    
    def _apply_archive_mode(self, version, month_display_text):
        """Apply archive mode styling to all UI elements."""
        month_obj = datetime.strptime(self.expense_tracker.viewed_month, "%Y-%m")
        month_name = month_obj.strftime('%B %Y')
        
        # Window title: Show archive mode
        self.root.title(f"LiteFinPad v{version} - 📚 Archive: {month_name}")
        
        # Background: Theme-aware archive tint (light lavender for light mode, dark purple for dark mode)
        archive_tint = self.theme_manager.get_archive_tint() if self.theme_manager else config.Colors.BG_ARCHIVE_TINT
        # Root window uses archive tint
        self.root.configure(bg=archive_tint)
        
        # Main container also uses archive tint
        if self.main_container:
            if isinstance(self.main_container, ctk.CTkFrame):
                self.main_container.configure(fg_color=archive_tint)
        
        # Switch main_frame to archive style
        if self.main_frame:
            # Check if it's a CustomTkinter widget or ttk widget
            # Use both isinstance and winfo_class for robust detection
            is_ctk_frame = isinstance(self.main_frame, ctk.CTkFrame) or hasattr(self.main_frame, 'fg_color')
            if is_ctk_frame:
                # CustomTkinter: use fg_color
                try:
                    self.main_frame.configure(fg_color=archive_tint)
                except Exception as e:
                    from error_logger import log_error
                    log_error(f"Error configuring main_frame fg_color: {e}", e)
            else:
                # ttk widget: use style
                try:
                    self.main_frame.configure(style='Archive.TFrame')
                except Exception as e:
                    from error_logger import log_error
                    log_error(f"Error configuring main_frame style: {e}", e)
            self.apply_styles_to_widgets(self.main_frame, archive=True)
        
        if self.expense_list_frame:
            is_ctk_frame = isinstance(self.expense_list_frame, ctk.CTkFrame) or hasattr(self.expense_list_frame, 'fg_color')
            if is_ctk_frame:
                # CustomTkinter: use fg_color
                try:
                    self.expense_list_frame.configure(fg_color=archive_tint)
                except Exception as e:
                    from error_logger import log_error
                    log_error(f"Error configuring expense_list_frame fg_color: {e}", e)
            else:
                try:
                    self.expense_list_frame.configure(style='Archive.TFrame')
                except Exception as e:
                    from error_logger import log_error
                    log_error(f"Error configuring expense_list_frame style: {e}", e)
            self.apply_styles_to_widgets(self.expense_list_frame, archive=True)
        
        if self.month_label:
            self.month_label.configure(text=month_display_text)
        
        if self.main_frame:
            self.apply_customtkinter_styles(self.main_frame, archive=True)
        
        if self.main_frame:
            try:
                self.main_frame.update_idletasks()
            except:
                pass
        if self.root:
            try:
                self.root.update_idletasks()
            except:
                pass
        
        if self.add_expense_btn:
            if isinstance(self.add_expense_btn, ctk.CTkButton):
                self.add_expense_btn.configure(state='disabled')
            else:
                self.add_expense_btn.config(state='disabled')
            actual_month_name = self.expense_tracker.month_viewer.format_month_display(
                self.expense_tracker.current_month,
                include_archive_indicator=False
            )
            if self.tooltip_creator:
                if hasattr(self.tooltip_creator, '__self__') and hasattr(self.tooltip_creator.__self__, 'update'):
                    self.tooltip_creator.__self__.update(
                        self.add_expense_btn,
                        f"Cannot add expenses in Archive mode. Switch to {actual_month_name}."
                    )
                else:
                    try:
                        self.add_expense_btn.unbind("<Enter>")
                        self.add_expense_btn.unbind("<Leave>")
                    except:
                        pass
                    if hasattr(self.add_expense_btn, 'tooltip'):
                        try:
                            self.add_expense_btn.tooltip.destroy()
                        except:
                            pass
                        delattr(self.add_expense_btn, 'tooltip')
                self.tooltip_creator(
                    self.add_expense_btn,
                    f"Cannot add expenses in Archive mode. Switch to {actual_month_name}."
                )
        
        if self.quick_add_helper:
            actual_month_name = self.expense_tracker.month_viewer.format_month_display(
                self.expense_tracker.current_month,
                include_archive_indicator=False
            )
            self.quick_add_helper.set_enabled(
                False,
                tooltip_text=f"Cannot add expenses in Archive mode. Switch to {actual_month_name}."
            )
    
    def _apply_normal_mode(self, version, month_display_text):
        """Apply normal mode styling to all UI elements - Simplified and reliable."""
        # Window title: Normal
        self.root.title(f"LiteFinPad v{version} - Monthly Expense Tracker")
        
        colors = self.theme_manager.get_colors() if self.theme_manager else config.Colors
        is_dark = self.theme_manager.is_dark_mode() if self.theme_manager else False
        
        # Root window uses theme-aware background
        root_bg = colors.BG_MAIN if is_dark else colors.BG_WHITE
        self.root.configure(bg=root_bg)
        
        # Main container uses theme-aware background
        container_bg = colors.BG_SECONDARY if is_dark else colors.BG_LIGHT_GRAY
        if self.main_container:
            if isinstance(self.main_container, ctk.CTkFrame):
                self.main_container.configure(fg_color=container_bg)
        
        # Main frame uses BG_LIGHT_GRAY (light) or BG_SECONDARY (dark)
        frame_bg = colors.BG_SECONDARY if is_dark else colors.BG_LIGHT_GRAY
        
        # Switch main_frame to normal style - Simplified
        if self.main_frame:
            if isinstance(self.main_frame, ctk.CTkFrame) or hasattr(self.main_frame, 'fg_color'):
                try:
                    self.main_frame.configure(fg_color=frame_bg)
                except Exception:
                    pass
            else:
                try:
                    self.main_frame.configure(style='TFrame')
                except Exception:
                    pass
            # Apply styles to all widgets (this updates all labels with explicit backgrounds)
            self.apply_styles_to_widgets(self.main_frame, archive=False)
        
        if self.expense_list_frame:
            if isinstance(self.expense_list_frame, ctk.CTkFrame) or hasattr(self.expense_list_frame, 'fg_color'):
                try:
                    self.expense_list_frame.configure(fg_color=frame_bg)
                except Exception:
                    pass
            else:
                try:
                    self.expense_list_frame.configure(style='TFrame')
                except Exception:
                    pass
            self.apply_styles_to_widgets(self.expense_list_frame, archive=False)
        
        if self.month_label:
            self.month_label.configure(text=month_display_text)
        
        if self.main_frame:
            self.apply_customtkinter_styles(self.main_frame, archive=False)
        if self.expense_list_frame:
            self.apply_customtkinter_styles(self.expense_list_frame, archive=False)
        
        if self.main_frame:
            self.apply_styles_to_widgets(self.main_frame, archive=False)
        if self.expense_list_frame:
            self.apply_styles_to_widgets(self.expense_list_frame, archive=False)
        
        if self.add_expense_btn:
            if isinstance(self.add_expense_btn, ctk.CTkButton):
                self.add_expense_btn.configure(state='normal')
            else:
                self.add_expense_btn.config(state='normal')
            if hasattr(self.tooltip_creator, '__self__') and hasattr(self.tooltip_creator.__self__, 'destroy'):
                self.tooltip_creator.__self__.destroy(self.add_expense_btn)
            else:
                try:
                    self.add_expense_btn.unbind("<Enter>")
                    self.add_expense_btn.unbind("<Leave>")
                except:
                    pass
                if hasattr(self.add_expense_btn, 'tooltip'):
                    try:
                        self.add_expense_btn.tooltip.destroy()
                    except:
                        pass
                    delattr(self.add_expense_btn, 'tooltip')
        
        if self.quick_add_helper:
            self.quick_add_helper.set_enabled(True)
    
    def apply_styles_to_widgets(self, parent, archive=True):
        """
        Recursively apply archive or normal styles to all ttk widgets.
        
        Args:
            parent: Parent widget to start from
            archive: True to apply archive styles, False for normal styles
        """
        prefix = 'Archive.' if archive else ''
        
        for widget in parent.winfo_children():
            widget_class = widget.winfo_class()
            
            if widget_class == 'TLabel':
                if archive:
                    target_bg = self.theme_manager.get_archive_tint() if self.theme_manager else config.Colors.BG_ARCHIVE_TINT
                else:
                    theme_colors = self.theme_manager.get_colors() if self.theme_manager else config.Colors
                    is_dark = self.theme_manager.is_dark_mode() if self.theme_manager else False
                    target_bg = theme_colors.BG_SECONDARY if is_dark else config.Colors.BG_LIGHT_GRAY
                
                try:
                    widget.configure(background=target_bg)
                except (tk.TclError, AttributeError):
                    pass
                
                try:
                    current_style = str(widget.cget('style'))
                    # Strip any existing 'Archive.' prefix
                    base_style = current_style.replace('Archive.', '')
                    
                    if base_style:
                        # Has a specific style (Title.TLabel, etc.) - add/remove Archive prefix
                        new_style = f"{prefix}{base_style}"
                    else:
                        # No specific style - use default TLabel style
                        new_style = 'Archive.TLabel' if archive else 'TLabel'
                    
                    widget.configure(style=new_style)
                except (tk.TclError, AttributeError):
                    # Style update failed, continue
                    pass
            
            # Update ttk.Frame widgets
            elif widget_class == 'TFrame':
                # Check if widget has a custom style (like Analytics.TFrame, Progress.TFrame)
                try:
                    current_style = str(widget.cget('style'))
                    # Strip any existing 'Archive.' prefix
                    base_style = current_style.replace('Archive.', '')
                    
                    # If it's a custom style (Analytics.TFrame, Progress.TFrame, Expenses.TFrame, Metrics.TFrame, StatusBar.TFrame), preserve it
                    if base_style in ['Analytics.TFrame', 'Progress.TFrame', 'Expenses.TFrame', 'Metrics.TFrame', 'StatusBar.TFrame']:
                        new_style = f'{prefix}{base_style}'
                    else:
                        # Default TFrame style
                        new_style = f'{prefix}TFrame'
                    
                    widget.configure(style=new_style)
                except (tk.TclError, AttributeError):
                    # Fallback to default style if we can't read current style
                    widget.configure(style=f'{prefix}TFrame')
                
                # Recursively update children
                self.apply_styles_to_widgets(widget, archive)
            
            # Update ttk.LabelFrame widgets
            elif widget_class == 'TLabelframe':
                widget.configure(style=f'{prefix}TLabelframe')
                # Recursively update children
                self.apply_styles_to_widgets(widget, archive)
            
            # Update tk.Frame widgets (regular Frame, not ttk.Frame)
            elif widget_class == 'Frame':
                # Check if this is the status bar frame (has status_label as child)
                is_status_frame = False
                try:
                    for child in widget.winfo_children():
                        if hasattr(child, 'winfo_class') and child.winfo_class() == 'TLabel':
                            # Check if it's the status label by checking if it has specific text patterns
                            try:
                                text = str(child.cget('text'))
                                if 'expenses' in text.lower() or text == 'No expenses':
                                    is_status_frame = True
                                    break
                            except:
                                pass
                except:
                    pass
                
                # Only update status bar frames - preserve their dark gray background
                if is_status_frame:
                    # Get theme-aware status bar background color
                    if self.theme_manager:
                        is_dark = self.theme_manager.is_dark_mode()
                        if is_dark:
                            status_bg = self.theme_manager.get_colors().BG_TERTIARY  # #2d2d30 (darker gray for status bar)
                        else:
                            status_bg = config.Colors.BG_LIGHT_GRAY  # #e5e5e5
                    else:
                        status_bg = config.Colors.BG_LIGHT_GRAY
                    
                    try:
                        widget.configure(bg=status_bg)
                        widget.update_idletasks()  # Force update
                    except (tk.TclError, AttributeError):
                        pass
                
                # Recursively check children
                self.apply_styles_to_widgets(widget, archive)
            
            # Update CTkFrame widgets (CustomTkinter frames)
            elif widget_class == 'CTkFrame':
                # Recursively check children (CTkFrame styling handled by apply_customtkinter_styles)
                self.apply_styles_to_widgets(widget, archive)
            
            # Recursively check other containers
            elif widget_class in ['Labelframe']:
                self.apply_styles_to_widgets(widget, archive)
    
    def apply_customtkinter_styles(self, parent, archive=True):
        """
        Recursively apply archive or normal styles to all CustomTkinter widgets.
        
        Args:
            parent: Parent widget to start from
            archive: True to apply archive styles, False for normal styles
        """
        # Use theme-aware colors
        if self.theme_manager:
            colors = self.theme_manager.get_colors()
            if archive:
                bg_color = self.theme_manager.get_archive_tint()
            else:
                # Normal mode: use BG_LIGHT_GRAY (light) or BG_SECONDARY (dark)
                bg_color = colors.BG_SECONDARY if self.theme_manager.is_dark_mode() else colors.BG_LIGHT_GRAY
        else:
            # Fallback to config colors if theme_manager not available
            bg_color = config.Colors.BG_ARCHIVE_TINT if archive else config.Colors.BG_LIGHT_GRAY
        
        try:
            children = parent.winfo_children()
        except (tk.TclError, AttributeError):
            # Parent widget doesn't support winfo_children or is destroyed
            return
        
        for widget in children:
            try:
                # Update CTkLabel widgets
                if isinstance(widget, ctk.CTkLabel):
                    try:
                        current_fg = widget.cget('fg_color')
                        # Update labels that use standard background colors
                        # Keep transparent labels transparent (they inherit from parent)
                        # Check against both light and dark mode colors
                        theme_colors = self.theme_manager.get_colors() if self.theme_manager else config.Colors
                        light_bg = config.Colors.BG_LIGHT_GRAY
                        dark_bg = theme_colors.BG_SECONDARY if self.theme_manager and self.theme_manager.is_dark_mode() else None
                        dark_bg_alt = theme_colors.BG_LIGHT_GRAY if self.theme_manager and self.theme_manager.is_dark_mode() else None  # BG_LIGHT_GRAY in dark mode is #2d2d30
                        light_archive = config.Colors.BG_ARCHIVE_TINT
                        dark_archive = self.theme_manager.get_archive_tint() if self.theme_manager else None
                        
                        # Update if label matches any standard background color (skip transparent)
                        if (current_fg == light_bg or current_fg == light_archive or 
                            (dark_bg and current_fg == dark_bg) or 
                            (dark_bg_alt and current_fg == dark_bg_alt) or  # Also catch BG_LIGHT_GRAY in dark mode
                            (dark_archive and current_fg == dark_archive)):
                            # Update to new background color
                            widget.configure(fg_color=bg_color)
                        # Skip transparent labels - they inherit from parent
                    except (tk.TclError, AttributeError, RuntimeError):
                        # Widget might be destroyed or not fully initialized
                        pass
                
                # Update CTkFrame widgets
                elif isinstance(widget, ctk.CTkFrame):
                    try:
                        # Check if this is the status bar frame (has status_label as child)
                        is_status_frame = False
                        try:
                            for child in widget.winfo_children():
                                if hasattr(child, 'winfo_class') and child.winfo_class() == 'TLabel':
                                    # Check if it's the status label by checking if it has specific text patterns
                                    try:
                                        text = str(child.cget('text'))
                                        if 'expenses' in text.lower() or text == 'No expenses':
                                            is_status_frame = True
                                            break
                                    except:
                                        pass
                        except:
                            pass
                        
                        # Skip status bar frames - they have their own color management
                        if is_status_frame:
                            # Recursively check children but don't modify status bar frame itself
                            self.apply_customtkinter_styles(widget, archive)
                            continue
                        
                        current_fg = widget.cget('fg_color')
                        # Update ALL frames that aren't transparent (more aggressive update for proper refresh)
                        # Check against both light and dark mode colors, and archive colors
                        theme_colors = self.theme_manager.get_colors() if self.theme_manager else config.Colors
                        light_bg = config.Colors.BG_LIGHT_GRAY
                        dark_bg = theme_colors.BG_SECONDARY if self.theme_manager and self.theme_manager.is_dark_mode() else None
                        dark_bg_alt = theme_colors.BG_LIGHT_GRAY if self.theme_manager and self.theme_manager.is_dark_mode() else None  # BG_LIGHT_GRAY in dark mode is #2d2d30
                        light_archive = config.Colors.BG_ARCHIVE_TINT
                        dark_archive = self.theme_manager.get_archive_tint() if self.theme_manager else None
                        
                        # Update if frame matches any standard background color OR if it's not transparent
                        # This ensures all frames get updated when switching modes
                        if (current_fg == light_bg or current_fg == light_archive or 
                            (dark_bg and current_fg == dark_bg) or 
                            (dark_bg_alt and current_fg == dark_bg_alt) or  # Also catch BG_LIGHT_GRAY in dark mode
                            (dark_archive and current_fg == dark_archive)):
                            # Update to new background color
                            widget.configure(fg_color=bg_color)
                        # Skip transparent frames - they inherit from parent
                    except (tk.TclError, AttributeError, RuntimeError):
                        # Widget might be destroyed or not fully initialized
                        pass
                
                # Recursively check all containers (including non-CustomTkinter widgets)
                try:
                    self.apply_customtkinter_styles(widget, archive)
                except (tk.TclError, AttributeError, RuntimeError):
                    # Widget doesn't support winfo_children or is destroyed
                    pass
            except (tk.TclError, AttributeError, RuntimeError):
                # Widget might be destroyed during iteration
                continue
    
    def _update_ttk_styles(self, archive=False):
        """
        Update ttk.Style configurations when switching modes.
        This ensures styles like 'Analytics.TFrame' and 'Progress.TFrame' are updated.
        
        Args:
            archive: True to apply archive styles, False for normal styles
        """
        try:
            from tkinter import ttk
            style = ttk.Style()
            
            if self.theme_manager:
                colors = self.theme_manager.get_colors()
                is_dark = self.theme_manager.is_dark_mode()
                if archive:
                    frame_bg = self.theme_manager.get_archive_tint()
                else:
                    frame_bg = colors.BG_SECONDARY if is_dark else colors.BG_LIGHT_GRAY
            else:
                frame_bg = config.Colors.BG_ARCHIVE_TINT if archive else config.Colors.BG_LIGHT_GRAY
            
            # Update custom frame styles used in dashboard
            prefix = 'Archive.' if archive else ''
            
            # Analytics.TFrame - used in analytics section
            style.configure(f'{prefix}Analytics.TFrame', background=frame_bg)
            
            # Progress.TFrame - used in progress section
            style.configure(f'{prefix}Progress.TFrame', background=frame_bg)
            
            # Expenses.TFrame - used in recent expenses section
            style.configure(f'{prefix}Expenses.TFrame', background=frame_bg)
            
            # Metrics.TFrame - used in expense insights section
            style.configure(f'{prefix}Metrics.TFrame', background=frame_bg)
            
            # StatusBar.TFrame - used in expense table status bar
            # Use BG_TERTIARY in dark mode for gray status bar, BG_LIGHT_GRAY in light mode
            status_bg = colors.BG_TERTIARY if is_dark else config.Colors.BG_LIGHT_GRAY
            style.configure(f'{prefix}StatusBar.TFrame', background=status_bg)
            
        except Exception:
            # Style update failed, continue
            pass

