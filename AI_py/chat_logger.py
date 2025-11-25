# AI_py/chat_logger.py
"""AI Chat session logger for debugging and analysis."""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional

class ChatLogger:
    """Logs AI chat sessions to file for debugging."""
    
    def __init__(self, log_dir: str = "logs"):
        """Initialize chat logger."""
        self.log_dir = log_dir
        self.session_file = None
        self.session_data = {
            'session_start': None,
            'session_end': None,
            'model': None,
            'conversations': []
        }
        
        # Create logs directory if it doesn't exist
        os.makedirs(self.log_dir, exist_ok=True)
    
    def start_session(self, model: str):
        """Start a new chat session."""
        timestamp = datetime.now()
        session_id = timestamp.strftime('%Y%m%d_%H%M%S')
        self.session_file = os.path.join(self.log_dir, f"ai_chat_{session_id}.json")
        
        self.session_data = {
            'session_start': timestamp.isoformat(),
            'session_end': None,
            'model': model,
            'conversations': []
        }
    
    def log_exchange(self, user_input: str, ai_response: str, 
                     intent: str, thinking_steps: List[str] = None,
                     expenses_added: int = 0, expenses_deleted: int = 0):
        """Log a single user-AI exchange."""
        exchange = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'ai_response': ai_response,
            'intent': intent,
            'thinking_steps': thinking_steps or [],
            'expenses_added': expenses_added,
            'expenses_deleted': expenses_deleted
        }
        
        self.session_data['conversations'].append(exchange)
        self._save_session()
    
    def end_session(self):
        """End the current chat session."""
        self.session_data['session_end'] = datetime.now().isoformat()
        self._save_session()
    
    def _save_session(self):
        """Save session data to file."""
        if self.session_file:
            try:
                with open(self.session_file, 'w', encoding='utf-8') as f:
                    json.dump(self.session_data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"Error saving chat log: {e}")
    
    def get_latest_log_path(self) -> Optional[str]:
        """Get path to the most recent chat log."""
        try:
            log_files = [f for f in os.listdir(self.log_dir) if f.startswith('ai_chat_') and f.endswith('.json')]
            if log_files:
                latest = max(log_files)
                return os.path.join(self.log_dir, latest)
        except Exception:
            pass
        return None

