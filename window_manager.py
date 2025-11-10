"""Main window lifecycle, positioning, animations, and event handling."""

import tkinter as tk
from error_logger import log_info, log_debug, log_error
import config
from window_animation import create_window_animator


class WindowManager:
    """Manages main window lifecycle, positioning, and animation."""
    
    def __init__(self, root, animator, gui, close_dialogs_callback, quit_callback):
        """Initialize window manager with root, animator, GUI, and callbacks."""
        self.root = root
        self.animator = animator
        self.gui = gui
        self.close_dialogs_callback = close_dialogs_callback
        self.quit_callback = quit_callback
        self.is_hidden = True
        
        self._cached_screen_width = None
        self._cached_screen_height = None
        self._cached_window_x = None
        self._cached_window_y = None
        self._cache_screen_info()
        
        self._setup_event_handlers()
    
    def _cache_screen_info(self):
        """Cache screen dimensions and pre-calculate window position."""
        try:
            self._cached_screen_width = self.root.winfo_screenwidth()
            self._cached_screen_height = self.root.winfo_screenheight()
            
            window_width = config.Window.WIDTH
            window_height = config.Window.COMPACT_HEIGHT
            self._cached_window_x = self._cached_screen_width - window_width - config.Animation.SCREEN_MARGIN
            self._cached_window_y = self._cached_screen_height - window_height - 450
            
            log_debug(f"[WINDOW] Screen info cached: {self._cached_screen_width}x{self._cached_screen_height}, Position: ({self._cached_window_x}, {self._cached_window_y})")
        except (tk.TclError, AttributeError) as e:
            log_error(f"[WINDOW] ERROR caching screen info (Tkinter error): {e}", e)
        except Exception as e:
            log_error(f"[WINDOW] ERROR caching screen info (unexpected): {e}", e)
    
    def _setup_event_handlers(self):
        """Set up window event handlers."""
        self.root.bind("<Unmap>", self.on_window_unmap)
        self.root.bind("<Map>", self.on_window_map)
        self.root.bind("<Destroy>", self.on_window_destroy)
    
    def show_window(self):
        """Show main window positioned near taskbar with slide animation."""
        try:
            log_info(f"[WINDOW] Showing window")
            log_debug(f"[WINDOW] Hidden state: {self.is_hidden}")
            
            window_width = config.Window.WIDTH
            window_height = config.Window.COMPACT_HEIGHT
            x = self._cached_window_x
            y = self._cached_window_y
            
            self.animator.slide_in(x, y, window_width, window_height)
            self.is_hidden = False
            
            def update_display_async():
                try:
                    self.gui.update_recent_expenses()
                    self.gui.update_display()
                except (tk.TclError, AttributeError) as e:
                    log_error(f"[WINDOW] ERROR updating display (Tkinter error): {e}", e)
                except RuntimeError as e:
                    log_error(f"[WINDOW] ERROR updating display (runtime error): {e}", e)
                except Exception as e:
                    log_error(f"[WINDOW] ERROR updating display (unexpected): {e}", e)
            
            self.root.after(30, update_display_async)
            
            self.root.lift()
            self.root.focus_force()
            
            self._apply_topmost_setting()
                
        except (tk.TclError, AttributeError) as e:
            log_error(f"[WINDOW] ERROR in show_window (Tkinter error): {e}", e)
            print(f"Error showing window: {e}")
            self.root.deiconify()
        except RuntimeError as e:
            log_error(f"[WINDOW] ERROR in show_window (runtime error): {e}", e)
            print(f"Error showing window: {e}")
            self.root.deiconify()
        except Exception as e:
            log_error(f"[WINDOW] ERROR in show_window (unexpected): {e}", e)
            print(f"Error showing window: {e}")
            self.root.deiconify()
    
    def hide_window(self):
        """Hide window to system tray with slide animation."""
        try:
            log_info(f"[WINDOW] Hiding window")
            log_debug(f"[WINDOW] Hidden state: {self.is_hidden}")
            
            self.is_hidden = True
            
            self._cache_screen_info()
            
            self.close_dialogs_callback()
            
            current_geometry = self.root.geometry()
            if 'x' in current_geometry and '+' in current_geometry:
                parts = current_geometry.split('+')
                if len(parts) >= 3:
                    current_x = int(parts[1])
                    current_y = int(parts[2])
                    
                    self.animator.slide_out(current_x, current_y)
                    return
            
            log_debug("[WINDOW] Using fallback withdraw()")
            self.root.withdraw()
            
        except (tk.TclError, AttributeError) as e:
            log_error(f"[WINDOW] ERROR in hide_window (Tkinter error): {e}", e)
            print(f"Error in hide animation: {e}")
            self.root.withdraw()
        except RuntimeError as e:
            log_error(f"[WINDOW] ERROR in hide_window (runtime error): {e}", e)
            print(f"Error in hide animation: {e}")
            self.root.withdraw()
        except Exception as e:
            log_error(f"[WINDOW] ERROR in hide_window (unexpected): {e}", e)
            print(f"Error in hide animation: {e}")
            self.root.withdraw()
    
    def force_hide_window(self):
        """Force hide window without animation (for testing)."""
        self.close_dialogs_callback()
        self.root.withdraw()
    
    def recalculate_screen_info(self):
        """Recalculate screen info and position (call when screen config changes)."""
        log_info("[WINDOW] Recalculating screen info...")
        self._cache_screen_info()
    
    def toggle_stay_on_top(self):
        """Toggle stay on top functionality."""
        if self.gui.stay_on_top_var.get():
            self.root.attributes('-topmost', True)
        else:
            self.root.attributes('-topmost', False)
    
    def _apply_topmost_setting(self):
        """Apply topmost setting based on GUI preference."""
        if self.gui.stay_on_top_var.get():
            log_debug("[WINDOW] Stay on top enabled")
            self.root.attributes('-topmost', True)
        else:
            log_debug("[WINDOW] Using temporary topmost")
            self.root.attributes('-topmost', True)
            self.root.update()
            self.root.attributes('-topmost', False)
    
    # Event Handlers
    
    def on_window_unmap(self, event):
        """Handle window unmapping (minimize or close)."""
        pass
    
    def on_window_map(self, event):
        """Handle window mapping (restore from minimize)."""
        pass
    
    def on_window_destroy(self, event):
        """Handle window destroy event."""
        if event.widget == self.root:
            self.quit_callback()

