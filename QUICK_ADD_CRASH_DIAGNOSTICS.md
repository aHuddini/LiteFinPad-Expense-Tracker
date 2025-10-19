# Quick Add Dialog Crash - Diagnostic Plan

**Issue**: Intermittent crash when interacting with system tray icon while Quick Add dialog is open  
**Status**: Under observation, diagnostics prepared  
**Last Updated**: October 19, 2025

---

## Crash Symptoms

### Observed Behaviors
1. **Double-Click Crash** (Initial report)
   - Crash occurs when double-clicking system tray icon
   - Not consistently reproducible
   - No error log captured

2. **Single-Click with Dialog Open** (Updated report)
   - Quick Add dialog is already open
   - User single-clicks system tray icon
   - Application crashes
   - Still intermittent, not every time

### What We Know
- No error logs are being captured (suggests abrupt termination)
- Crash only occurs with Quick Add dialog interactions
- Related to tray icon click handlers
- May involve dialog lifecycle management

---

## Potential Root Causes

### 1. **Double-Click Detection Race Condition**
**File**: `tray_icon.py`, lines 49-53, 60-64  
**Code**: 110ms double-click detection window with timer

```python
# Current implementation in tray_icon.py
if (current_time - self.last_click_time) < self.double_click_window:
    # Double-click detected
    self.cancel_pending_single_click()
    self.on_double_click(event)
else:
    # Schedule single-click action with delay
    self.pending_single_click_timer = self.icon.after(
        int(self.double_click_window * 1000),
        lambda: self.on_single_click(event)
    )
```

**Issue**: If user single-clicks while Quick Add dialog is open, the timer might fire while dialog is being destroyed by FocusOut, causing conflict.

---

### 2. **Dialog Lifecycle + Window Toggle Conflict**
**File**: `tray_icon.py` (toggle_window) + `main.py` (show_quick_add_dialog)

**Scenario**:
1. Quick Add dialog opens (flag `_quick_add_dialog_open = True`)
2. User single-clicks tray icon
3. `toggle_window()` tries to show/hide main window
4. Dialog's FocusOut event fires due to window change
5. Dialog tries to destroy itself
6. Race condition between dialog destruction and window toggle

---

### 3. **Recursive FocusOut Binding**
**File**: `main.py`, line 181, `bind_focus_out_recursive` function

```python
def bind_focus_out_recursive(widget):
    """Recursively bind FocusOut to all children"""
    widget.bind('<FocusOut>', on_focus_out)
    for child in widget.winfo_children():
        bind_focus_out_recursive(child)
```

**Issue**: Every widget in the dialog (including number pad buttons) has FocusOut bound. If multiple widgets fire FocusOut simultaneously, could trigger multiple destruction attempts.

---

### 4. **Dialog Already Destroyed**
**File**: `main.py`, lines 406-582, `show_quick_add_dialog`

```python
def check_focus_and_close():
    """Check if focus is truly outside dialog before closing"""
    if dialog.winfo_exists():  # Safety check
        focused = dialog.focus_get()
        # ...
        if focus_outside:
            dialog.destroy()
            self._quick_add_dialog_open = False
```

**Issue**: If dialog is destroyed between `winfo_exists()` check and `destroy()` call, could cause crash.

---

## Diagnostic Implementation Plan

### Phase 1: Enhanced Logging (Implement First)

Add comprehensive logging to track event sequence leading to crash.

#### A. Tray Icon Click Logging
**File**: `tray_icon.py`

```python
# Add at top of file
from error_logger import log_info, log_error

# Modify on_click method
def on_click(self, event):
    """Handle system tray icon click"""
    log_info(f"[TRAY] Click detected at {time.time()}")
    
    current_time = time.time()
    time_since_last = current_time - self.last_click_time
    
    log_info(f"[TRAY] Time since last click: {time_since_last:.3f}s")
    log_info(f"[TRAY] Double-click window: {self.double_click_window}s")
    
    if time_since_last < self.double_click_window:
        log_info("[TRAY] DOUBLE-CLICK DETECTED - Cancelling pending single-click")
        self.cancel_pending_single_click()
        log_info("[TRAY] Calling on_double_click")
        self.on_double_click(event)
    else:
        log_info(f"[TRAY] Scheduling single-click with {self.double_click_window}s delay")
        self.pending_single_click_timer = self.icon.after(
            int(self.double_click_window * 1000),
            lambda: self._execute_single_click(event)
        )
    
    self.last_click_time = current_time

def _execute_single_click(self, event):
    """Execute single-click action (with logging)"""
    log_info("[TRAY] Executing delayed single-click action")
    self.on_single_click(event)
    log_info("[TRAY] Single-click action completed")
```

#### B. Dialog Lifecycle Logging
**File**: `main.py`, `show_quick_add_dialog` method

```python
def show_quick_add_dialog(self):
    """Show quick add expense dialog without opening main window"""
    try:
        log_info("[DIALOG] === Quick Add Dialog Creation Started ===")
        
        # Prevent multiple dialogs from opening
        if hasattr(self, '_quick_add_dialog_open') and self._quick_add_dialog_open:
            log_info("[DIALOG] Dialog already open, ignoring request")
            return
        
        log_info("[DIALOG] Setting dialog flag to True")
        self._quick_add_dialog_open = True
        
        # ... (existing dialog creation code) ...
        
        log_info(f"[DIALOG] Dialog created at position: {x}, {y}")
        
        # Before showing dialog
        log_info("[DIALOG] Calling deiconify() to show dialog")
        dialog.deiconify()
        
        log_info("[DIALOG] Setting focus to dialog")
        dialog.update()
        dialog.focus_force()
        amount_entry.focus_set()
        log_info("[DIALOG] Focus set to amount entry")
        
        # Delay FocusOut binding
        log_info("[DIALOG] Scheduling FocusOut binding with 100ms delay")
        dialog.after(100, lambda: self._bind_dialog_focus_out(dialog))
        
        log_info("[DIALOG] === Quick Add Dialog Creation Complete ===")
        
    except Exception as e:
        log_error(f"[DIALOG] ERROR in show_quick_add_dialog: {str(e)}")
        self._quick_add_dialog_open = False
        raise

def _bind_dialog_focus_out(self, dialog):
    """Bind FocusOut events with logging"""
    log_info("[DIALOG] Binding FocusOut events recursively")
    bind_focus_out_recursive(dialog)
    log_info("[DIALOG] FocusOut binding complete")
```

#### C. Focus Out Event Logging
**File**: `main.py`, within `show_quick_add_dialog`

```python
def on_focus_out(event):
    """Handle focus out event with delay to prevent accidental closing"""
    log_info(f"[DIALOG] FocusOut event triggered by widget: {event.widget}")
    log_info(f"[DIALOG] Scheduling focus check with 50ms delay")
    dialog.after(50, lambda: check_focus_and_close())

def check_focus_and_close():
    """Check if focus is truly outside dialog before closing"""
    log_info("[DIALOG] === Focus Check Started ===")
    
    # Check if dialog still exists
    if not dialog.winfo_exists():
        log_info("[DIALOG] Dialog no longer exists, aborting close check")
        return
    
    log_info("[DIALOG] Dialog exists, checking focus location")
    focused = dialog.focus_get()
    log_info(f"[DIALOG] Currently focused widget: {focused}")
    
    # Determine if focus is outside dialog
    focus_outside = True
    if focused:
        log_info(f"[DIALOG] Focused widget type: {type(focused)}")
        try:
            parent = focused
            while parent:
                log_info(f"[DIALOG] Checking parent: {parent}")
                if parent == dialog:
                    focus_outside = False
                    log_info("[DIALOG] Focus is inside dialog")
                    break
                parent = parent.master
        except Exception as e:
            log_error(f"[DIALOG] Error checking focus hierarchy: {str(e)}")
    
    if focus_outside:
        log_info("[DIALOG] Focus is outside dialog - DESTROYING")
        try:
            dialog.destroy()
            log_info("[DIALOG] Dialog destroyed successfully")
            self._quick_add_dialog_open = False
            log_info("[DIALOG] Dialog flag set to False")
        except Exception as e:
            log_error(f"[DIALOG] ERROR during dialog destruction: {str(e)}")
            self._quick_add_dialog_open = False
    else:
        log_info("[DIALOG] Focus still inside dialog - keeping open")
    
    log_info("[DIALOG] === Focus Check Complete ===")
```

#### D. Window Toggle Logging
**File**: `tray_icon.py`, `toggle_window` method

```python
def toggle_window(self, event):
    """Toggle main window visibility"""
    log_info("[WINDOW] === Toggle Window Called ===")
    
    if self.tracker.is_window_visible():
        log_info("[WINDOW] Window is visible, hiding it")
        self.tracker.hide_window()
        log_info("[WINDOW] Window hidden")
    else:
        log_info("[WINDOW] Window is hidden, showing it")
        self.tracker.show_window()
        log_info("[WINDOW] Window shown")
    
    log_info("[WINDOW] === Toggle Window Complete ===")
```

---

### Phase 2: Defensive Code (Implement After Patterns Identified)

Based on log analysis, implement appropriate fixes:

#### Option A: Prevent Tray Click During Dialog
```python
# In tray_icon.py, on_click method
def on_click(self, event):
    """Handle system tray icon click"""
    # Check if Quick Add dialog is open
    if hasattr(self.tracker, '_quick_add_dialog_open') and self.tracker._quick_add_dialog_open:
        log_info("[TRAY] Quick Add dialog open, ignoring tray click")
        return  # Ignore clicks while dialog is open
    
    # ... (existing click handling) ...
```

#### Option B: Cancel Pending Timers on Dialog Open
```python
# In main.py, show_quick_add_dialog
def show_quick_add_dialog(self):
    # Cancel any pending tray icon single-click timers
    if hasattr(self.tray_icon, 'pending_single_click_timer') and self.tray_icon.pending_single_click_timer:
        log_info("[DIALOG] Cancelling pending tray icon timer")
        self.tray_icon.icon.after_cancel(self.tray_icon.pending_single_click_timer)
        self.tray_icon.pending_single_click_timer = None
    
    # ... (rest of dialog creation) ...
```

#### Option C: Mutex Lock for Dialog Operations
```python
# Add to main.py class
import threading

class ExpenseTracker:
    def __init__(self, root):
        self.dialog_lock = threading.Lock()
        # ... (existing init) ...
    
    def show_quick_add_dialog(self):
        with self.dialog_lock:
            # ... (existing dialog code) ...
```

#### Option D: Strengthen Dialog Existence Checks
```python
def check_focus_and_close():
    """Check if focus is truly outside dialog before closing"""
    # Multiple existence checks before destruction
    try:
        if not dialog.winfo_exists():
            return
        
        # Additional check right before destroy
        if not dialog.winfo_exists():
            return
        
        # Proceed with focus check and potential destruction
        # ...
        
        if focus_outside:
            # Final existence check
            if dialog.winfo_exists():
                dialog.destroy()
                self._quick_add_dialog_open = False
    except tk.TclError as e:
        log_error(f"[DIALOG] TclError during close: {str(e)} - dialog may already be destroyed")
        self._quick_add_dialog_open = False
    except Exception as e:
        log_error(f"[DIALOG] Unexpected error during close: {str(e)}")
        self._quick_add_dialog_open = False
```

---

## Testing Protocol

### When to Implement Diagnostics
1. User reports crash pattern becomes more consistent
2. Multiple crashes occur in same session
3. Error logs show any related errors

### How to Test with Diagnostics
1. Enable all diagnostic logging
2. Attempt to reproduce crash scenarios:
   - Double-click tray icon rapidly
   - Open Quick Add, then single-click tray icon
   - Open Quick Add, wait, then single-click tray icon
   - Open Quick Add, interact with number pad, then click tray icon
3. Review `logs/errors_YYYY-MM-DD.txt` for event sequence
4. Identify pattern in logs leading to crash
5. Implement targeted defensive code based on pattern

### Log Analysis Checklist
- [ ] What was the last logged event before crash?
- [ ] Was FocusOut triggered?
- [ ] Was a tray click timer pending?
- [ ] Was the dialog in the process of being destroyed?
- [ ] Did window toggle get called?
- [ ] Were multiple FocusOut events fired?
- [ ] Was there a TclError (widget doesn't exist)?

---

## Implementation Instructions

### To Enable Diagnostics:
1. Uncomment logging statements in the code sections above
2. Rebuild application with `build_dev.bat`
3. Test and reproduce crash
4. Check `logs/errors_YYYY-MM-DD.txt`
5. Share log excerpt showing crash sequence

### To Implement Fixes:
1. Based on log analysis, choose appropriate Option (A, B, C, or D)
2. Implement the defensive code
3. Test thoroughly
4. If crash persists, combine multiple options
5. Document the fix in `AI_MEMORY.md` and `CHANGELOG.md`

---

## Status
- ✅ Diagnostic plan prepared
- ✅ Logging code ready to implement
- ⏳ Awaiting consistent crash pattern
- ⏳ Log analysis pending
- ⏳ Fix implementation pending

