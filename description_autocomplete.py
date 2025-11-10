"""Smart description suggestions based on expense history for auto-complete."""

import json
import os
from typing import List, Dict, Optional
from datetime import datetime
from settings_manager import get_settings_manager


class DescriptionHistory:
    """Manage description history for auto-complete suggestions."""
    
    def __init__(self, file_path="description_history.json"):
        """Initialize description history manager with file path."""
        self.file_path = file_path
        self.descriptions = []
        self.settings = get_settings_manager()
        self.load()
    
    def load(self):
        """Load description history from JSON file."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.descriptions = data.get('descriptions', [])
            except (json.JSONDecodeError, IOError):
                self.descriptions = []
        else:
            self.descriptions = []
    
    def save(self):
        """Save description history to JSON file."""
        try:
            data = {'descriptions': self.descriptions}
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError:
            pass
    
    def add_or_update(self, description: str, amount: float):
        """Add new description or update existing one with usage tracking."""
        normalized = description.strip()
        if not normalized:
            return
        
        existing = next(
            (d for d in self.descriptions if d['text'].lower() == normalized.lower()),
            None
        )
        
        if existing:
            existing['count'] += 1
            existing['last_used'] = datetime.now().strftime('%Y-%m-%d')
            existing['last_amount'] = amount
        else:
            self.descriptions.append({
                'text': normalized,
                'count': 1,
                'last_used': datetime.now().strftime('%Y-%m-%d'),
                'last_amount': amount
            })
        
        self.descriptions.sort(
            key=lambda x: (-x['count'], x['last_used']),
            reverse=False
        )
        
        current_count = None
        group_start = 0
        for i in range(len(self.descriptions)):
            desc = self.descriptions[i]
            if current_count is None:
                current_count = desc['count']
            elif desc['count'] != current_count:
                self.descriptions[group_start:i] = sorted(
                    self.descriptions[group_start:i],
                    key=lambda x: x['last_used'],
                    reverse=True
                )
                group_start = i
                current_count = desc['count']
        
        self.descriptions[group_start:] = sorted(
            self.descriptions[group_start:],
            key=lambda x: x['last_used'],
            reverse=True
        )
        
        # Keep only top N descriptions (limit memory usage)
        max_descriptions = self.settings.get(
            'AutoComplete', 'max_descriptions', 50, value_type=int
        )
        self.descriptions = self.descriptions[:max_descriptions]
        
        self.save()
    
    def get_suggestions(self, partial_text: str = "", limit: int = None) -> List[Dict]:
        """Get suggestions based on partial text input. Returns list sorted by usage count."""
        if limit is None:
            limit = self.settings.get(
                'AutoComplete', 'max_suggestions', 5, value_type=int
            )
        
        if not partial_text:
            # No text typed - return most frequently used descriptions
            return self.descriptions[:limit]
        
        # Case-insensitive prefix matching
        partial_lower = partial_text.lower().strip()
        matches = [
            d for d in self.descriptions
            if d['text'].lower().startswith(partial_lower)
        ]
        
        return matches[:limit]
    
    def should_show_on_focus(self) -> bool:
        """Check if auto-complete should show when field receives focus."""
        return self.settings.get(
            'AutoComplete', 'show_on_focus', True, value_type=bool
        )
    
    def get_min_chars(self) -> int:
        """Get minimum characters required before showing suggestions."""
        return self.settings.get(
            'AutoComplete', 'min_chars', 2, value_type=int
        )
    
    def clear_history(self):
        """Clear all description history (useful for privacy/reset)."""
        self.descriptions = []
        self.save()

