"""Collapsible date combobox widget with accordion-style month expansion."""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
from calendar import monthrange
import config


class CollapsibleDateCombobox:
    """Wrapper for ttk.Combobox with collapsible month functionality."""
    
    def __init__(self, parent, on_select_callback=None):
        """
        Initialize the collapsible date combobox.
        
        Args:
            parent: Tkinter parent widget
            on_select_callback: Optional callback(date_value, date_text) when date selected
        """
        self.parent = parent
        self.on_select = on_select_callback
        self.month_states = {}
        self.all_date_options = []
        self.dropdown_is_open = False
        self.last_valid_selection = None
        
        self.date_var = tk.StringVar()
        
        style = ttk.Style()
        style.map('DateCombo.TCombobox',
                  fieldbackground=[('readonly', config.Colors.DATE_BG)],
                  foreground=[('readonly', config.Colors.DATE_FG)],
                  selectbackground=[('readonly', config.Colors.DATE_BG)],
                  selectforeground=[('readonly', config.Colors.DATE_FG)])
        style.configure('DateCombo.TCombobox',
                       foreground=config.Colors.DATE_FG,
                       fieldbackground=config.Colors.DATE_BG)
        
        self.combo = ttk.Combobox(
            parent,
            textvariable=self.date_var,
            state="readonly",
            font=config.Fonts.LABEL,
            width=32,
            style='DateCombo.TCombobox'
        )
        
        self.generate_all_dates()
        self.update_visible_options()
        self.set_default_date()
        
        self.combo.bind('<<ComboboxSelected>>', self.on_selection)
        self.combo.bind('<Button-1>', self.on_dropdown_open)
        self.combo.bind('<FocusOut>', self.on_dropdown_close)
        self.combo.bind('<MouseWheel>', self.on_mousewheel)
        self.combo.bind('<Button-4>', self.on_mousewheel)
        self.combo.bind('<Button-5>', self.on_mousewheel)
    
    def generate_all_dates(self):
        """Generate date options for all 12 months of current year."""
        self.all_date_options = []
        today = datetime.now()
        current_month = today.month
        current_year = today.year
        
        for month_num in range(1, 13):
            target_month = month_num
            target_year = current_year
            first_day = datetime(target_year, target_month, 1)
            month_name = first_day.strftime("%B")
            month_key = f"{month_name}_{target_year}"
            last_day = monthrange(target_year, target_month)[1]
            
            is_current = (target_month == current_month)
            self.month_states[month_key] = is_current
            
            separator_text = f"{'▼' if is_current else '▶'} ─── {month_name} {target_year}"
            if is_current:
                separator_text += " (Current)"
            separator_text += " ───"
            
            self.all_date_options.append({
                'type': 'separator',
                'text': separator_text,
                'month_key': month_key
            })
            
            for day in range(1, last_day + 1):
                date_obj = datetime(target_year, target_month, day)
                display = f"{day} - {month_name} {target_year}"
                
                if date_obj.date() == today.date():
                    display += " (Today)"
                elif date_obj.date() > today.date():
                    display += " (Future)"
                
                self.all_date_options.append({
                    'type': 'date',
                    'text': display,
                    'value': date_obj.strftime("%Y-%m-%d"),
                    'month_key': month_key,
                    'is_today': date_obj.date() == today.date()
                })
    
    def update_visible_options(self):
        """Update combobox values based on collapsed/expanded state."""
        visible_options = []
        
        for option in self.all_date_options:
            if option['type'] == 'separator':
                expanded = self.month_states[option['month_key']]
                month_key_parts = option['month_key'].split('_')
                month_name = month_key_parts[0]
                year = month_key_parts[1]
                is_current = "(Current)" in option['text']
                
                separator_text = f"{'▼' if expanded else '▶'} ─── {month_name} {year}"
                if is_current:
                    separator_text += " (Current)"
                separator_text += " ───"
                
                visible_options.append(separator_text)
            elif option['type'] == 'date':
                if self.month_states.get(option['month_key'], False):
                    visible_options.append(option['text'])
        
        self.combo['values'] = visible_options
    
    def on_dropdown_open(self, event):
        """Track when dropdown opens"""
        self.dropdown_is_open = True
    
    def on_dropdown_close(self, event):
        """Track when dropdown closes"""
        self.dropdown_is_open = False
    
    def on_mousewheel(self, event):
        """Handle mousewheel scrolling to navigate dates. Auto-expands months as needed."""
        current_text = self.date_var.get()
        
        current_index = -1
        for i, option in enumerate(self.all_date_options):
            if option['type'] == 'date' and option['text'] == current_text:
                current_index = i
                break
        
        if current_index == -1:
            for i, option in enumerate(self.all_date_options):
                if option['type'] == 'date' and option.get('is_today'):
                    current_index = i
                    break
        
        if hasattr(event, 'delta'):
            direction = -1 if event.delta > 0 else 1
        else:
            direction = -1 if event.num == 4 else 1
        
        new_index = current_index + direction
        while 0 <= new_index < len(self.all_date_options):
            if self.all_date_options[new_index]['type'] == 'date':
                new_option = self.all_date_options[new_index]
                
                new_month_key = new_option['month_key']
                if not self.month_states.get(new_month_key, False):
                    for key in self.month_states:
                        self.month_states[key] = False
                    self.month_states[new_month_key] = True
                    self.update_visible_options()
                
                self.date_var.set(new_option['text'])
                self.last_valid_selection = new_option['text']
                
                if self.on_select:
                    self.on_select(new_option['value'], new_option['text'])
                
                break
            
            new_index += direction
        
        return "break"
    
    def on_selection(self, event):
        """Handle selection - toggle month if separator clicked, notify callback if date selected."""
        selected = self.date_var.get()
        
        if selected.startswith('▶') or selected.startswith('▼'):
            try:
                parts = selected.split('───')
                if len(parts) >= 2:
                    month_year_part = parts[1].strip()
                    month_year_part = month_year_part.replace('(Current)', '').strip()
                    month_year_split = month_year_part.split()
                    if len(month_year_split) >= 2:
                        month_name = month_year_split[0]
                        year = month_year_split[1]
                        month_key = f"{month_name}_{year}"
                        
                        if not self.month_states[month_key]:
                            for key in self.month_states:
                                self.month_states[key] = False
                            self.month_states[month_key] = True
                        
                        self.update_visible_options()
                        
                        first_date_in_month = None
                        for option in self.all_date_options:
                            if option['type'] == 'date' and option['month_key'] == month_key:
                                first_date_in_month = option['text']
                                break
                        
                        if first_date_in_month:
                            self.combo.set(first_date_in_month)
                            def restore_selection():
                                if self.last_valid_selection:
                                    self.combo.set(self.last_valid_selection)
                                else:
                                    self.combo.set(first_date_in_month)
                            self.combo.after(50, restore_selection)
                        else:
                            if self.last_valid_selection:
                                self.combo.set(self.last_valid_selection)
                            else:
                                self.combo.set('')
                        
                        self.combo.after(10, lambda: self.combo.event_generate('<Button-1>'))
                        
                        return
            except Exception as e:
                print(f"Error parsing separator: {e}")
        
        if selected and not selected.startswith('▶') and not selected.startswith('▼'):
            self.last_valid_selection = selected
            if self.on_select:
                for option in self.all_date_options:
                    if option['type'] == 'date' and option['text'] == selected:
                        self.on_select(option['value'], selected)
                        break
    
    def set_default_date(self):
        """Set default to today's date and remember it"""
        for option in self.all_date_options:
            if option['type'] == 'date' and option.get('is_today'):
                self.date_var.set(option['text'])
                self.last_valid_selection = option['text']
                break
    
    def get_selected_date(self):
        """Get selected date in YYYY-MM-DD format. Returns None if no valid date selected."""
        selected_text = self.date_var.get()
        for option in self.all_date_options:
            if option['type'] == 'date' and option['text'] == selected_text:
                return option['value']
        return None
    
    def set_date(self, date_str):
        """Set combobox to specific date (YYYY-MM-DD format)."""
        for option in self.all_date_options:
            if option['type'] == 'date' and option['value'] == date_str:
                self.date_var.set(option['text'])
                self.last_valid_selection = option['text']
                
                month_key = option['month_key']
                for key in self.month_states:
                    self.month_states[key] = (key == month_key)
                
                self.update_visible_options()
                break
    
    def grid(self, **kwargs):
        """Forward grid() to the underlying combobox"""
        self.combo.grid(**kwargs)
    
    def pack(self, **kwargs):
        """Forward pack() to the underlying combobox"""
        self.combo.pack(**kwargs)

