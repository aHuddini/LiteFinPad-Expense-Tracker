"""Smooth slide-in and slide-out animations for the main window."""

import tkinter as tk
import time
import config


class WindowAnimator:
    """Handles window slide animations with proper rendering timing."""
    
    def __init__(self, root_window):
        self.root = root_window
        self.is_animating = False
        
    def slide_in(self, target_x, target_y, width, height, duration=config.Animation.SLIDE_OUT_DURATION_MS):
        """Show window with anti-flicker techniques (fade-in)."""
        if self.is_animating:
            return
            
        try:
            self.is_animating = True
            
            self.root.geometry(f"{width}x{height}+{target_x}+{target_y}")
            self.root.attributes('-alpha', 0.0)
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
            self.root.update_idletasks()
            self.root.update()
            
            def fade_in():
                try:
                    for alpha in config.Animation.FADE_IN_STEPS:
                        self.root.attributes('-alpha', alpha)
                        self.root.update_idletasks()
                        self.root.after(config.Animation.FADE_IN_STEP_DELAY_MS)
                    self.is_animating = False
                except Exception as e:
                    print(f"Error in fade-in: {e}")
                    self.root.attributes('-alpha', 1.0)
                    self.is_animating = False
            
            self.root.after(config.Animation.FADE_IN_INITIAL_DELAY_MS, fade_in)
            
        except Exception as e:
            print(f"Error showing window: {e}")
            self.root.geometry(f"{width}x{height}+{target_x}+{target_y}")
            self.root.attributes('-alpha', 1.0)
            self.is_animating = False
    
    def slide_out(self, start_x, start_y, duration=config.Animation.SLIDE_OUT_DURATION_MS):
        """Animate window sliding out to the right with fade-out."""
        if self.is_animating:
            return
            
        try:
            self.is_animating = True
            
            screen_width = self.root.winfo_screenwidth()
            end_x = screen_width + 50
            total_distance = end_x - start_x
            
            import time
            start_time = time.perf_counter()
            
            def ease_out_quad(t):
                return 1 - pow(1 - t, config.Animation.EASE_OUT_POWER)
            
            current_geometry = self.root.geometry()
            size_part = current_geometry.split('+')[0]
            
            frame_count = 0
            last_frame_time = start_time
            last_x = start_x
            
            from error_logger import log_info
            log_info(f"[ANIMATION START] Duration={duration}ms, Distance={total_distance}px, Start X={start_x}px Y={start_y}px, End X={end_x}px")
            
            def animate_step():
                nonlocal frame_count, last_frame_time, last_x
                
                if not self.is_animating:
                    return
                
                # Calculate elapsed time
                current_time = time.perf_counter()
                elapsed = (current_time - start_time) * 1000  # Convert to ms
                frame_delta = (current_time - last_frame_time) * 1000  # Time since last frame
                last_frame_time = current_time
                
                # Calculate progress (0 to 1)
                progress = min(elapsed / duration, 1.0)
                
                if progress < 1.0:
                    # Apply easing (but ensure first frame starts at exact position)
                    if frame_count == 0:
                        # First frame: ensure we start at the exact starting position
                        eased_progress = 0.0
                        current_x = start_x
                    else:
                        eased_progress = ease_out_quad(progress)
                        current_x = start_x + (total_distance * eased_progress)
                    pixel_delta = current_x - last_x
                    
                    fade_start = config.Animation.FADE_START_PROGRESS
                    if progress > fade_start:
                        fade_duration = 1.0 - fade_start
                        fade_progress = (progress - fade_start) / fade_duration
                        fade_amount = 1.0 - config.Animation.FADE_END_OPACITY
                        opacity = 1.0 - (fade_progress * fade_amount)
                    else:
                        opacity = 1.0
                    
                    fps = 1000 / frame_delta if frame_delta > 0 else 0
                    log_info(f"[FRAME {frame_count:3d}] Elapsed={elapsed:6.2f}ms | Delta={frame_delta:5.2f}ms | FPS={fps:5.1f} | Progress={progress*100:5.1f}% | Eased={eased_progress*100:5.1f}% | X={int(current_x):4d}px Y={start_y}px | ΔX={pixel_delta:+.1f}px | Opacity={opacity:.2f}")
                    
                    self.root.geometry(f"{size_part}+{int(current_x)}+{start_y}")
                    self.root.attributes('-alpha', opacity)
                    
                    last_x = current_x
                    frame_count += 1
                    self.root.after(1, animate_step)
                else:
                    total_time = (current_time - start_time) * 1000
                    avg_fps = frame_count / (total_time / 1000) if total_time > 0 else 0
                    log_info(f"[ANIMATION END] Total={total_time:.2f}ms | Frames={frame_count} | Avg FPS={avg_fps:.1f}")
                    self.root.withdraw()
                    self.is_animating = False
            
            animate_step()
            
        except Exception as e:
            print(f"Error in slide-out animation: {e}")
            self.root.withdraw()
            self.is_animating = False
    
    def stop_animation(self):
        """Stop any ongoing animation."""
        self.is_animating = False
    
    def is_animation_running(self):
        """Check if animation is currently running."""
        return self.is_animating


def create_window_animator(root_window):
    """Factory function to create a WindowAnimator instance."""
    return WindowAnimator(root_window)
