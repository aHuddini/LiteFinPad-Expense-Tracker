"""
Temporary File Manager for AI Processing

Provides utilities for creating temporary files in test_data/temp_AI
for AI debugging, sketching responses, and intermediate processing.
"""

import os
import json
from typing import Optional, Dict, Any
from datetime import datetime

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from error_logger import log_debug, log_warning


class TempFileManager:
    """Manages temporary files for AI processing in test_data/temp_AI."""
    
    TEMP_DIR = os.path.join("test_data", "temp_AI")
    
    @staticmethod
    def ensure_temp_dir() -> bool:
        """Ensure temp_AI directory exists. Returns True if successful."""
        try:
            os.makedirs(TempFileManager.TEMP_DIR, exist_ok=True)
            return True
        except Exception as e:
            log_warning(f"[TempFileManager] Failed to create temp directory: {e}")
            return False
    
    @staticmethod
    def write_temp_file(filename: str, content: Any, format: str = "json") -> Optional[str]:
        """
        Write a temporary file for AI processing.
        
        Args:
            filename: Name of the file (without extension)
            content: Content to write (dict for JSON, str for text)
            format: File format ("json" or "txt")
            
        Returns:
            Full path to the file, or None if failed
        """
        if not TempFileManager.ensure_temp_dir():
            return None
        
        # Add timestamp to filename to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = filename.replace(" ", "_").replace("/", "_")
        full_filename = f"{safe_filename}_{timestamp}.{format}"
        filepath = os.path.join(TempFileManager.TEMP_DIR, full_filename)
        
        try:
            if format == "json":
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(content, f, indent=2, ensure_ascii=False)
            else:  # txt
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(str(content))
            
            log_debug(f"[TempFileManager] Wrote temp file: {filepath}")
            return filepath
        except Exception as e:
            log_warning(f"[TempFileManager] Failed to write temp file {filepath}: {e}")
            return None
    
    @staticmethod
    def write_ai_sketch(query: str, response: str, metadata: Optional[Dict] = None) -> Optional[str]:
        """
        Write an AI response sketch for debugging.
        
        Args:
            query: User query
            response: AI response
            metadata: Optional metadata (intent, thinking_steps, etc.)
            
        Returns:
            Full path to the file, or None if failed
        """
        sketch = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response,
            "metadata": metadata or {}
        }
        
        result = TempFileManager.write_temp_file("ai_sketch", sketch, format="json")
        
        # Clean up old files after writing (1 day retention)
        TempFileManager.cleanup_old_files(max_age_days=1)
        
        return result
    
    @staticmethod
    def write_processing_steps(steps: list, query: str) -> Optional[str]:
        """
        Write AI processing steps for debugging.
        
        Args:
            steps: List of processing steps
            query: User query
            
        Returns:
            Full path to the file, or None if failed
        """
        content = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "steps": steps
        }
        
        result = TempFileManager.write_temp_file("processing_steps", content, format="json")
        
        # Clean up old files after writing (1 day retention)
        TempFileManager.cleanup_old_files(max_age_days=1)
        
        return result
    
    @staticmethod
    def cleanup_old_files(max_age_days: int = 1) -> int:
        """
        Clean up old temporary files.
        
        Args:
            max_age_days: Maximum age in days (default: 1)
            
        Returns:
            Number of files deleted
        """
        if not os.path.exists(TempFileManager.TEMP_DIR):
            return 0
        
        deleted_count = 0
        cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
        
        try:
            for filename in os.listdir(TempFileManager.TEMP_DIR):
                filepath = os.path.join(TempFileManager.TEMP_DIR, filename)
                if os.path.isfile(filepath):
                    file_time = os.path.getmtime(filepath)
                    if file_time < cutoff_time:
                        os.remove(filepath)
                        deleted_count += 1
                        log_debug(f"[TempFileManager] Deleted old temp file: {filename}")
        except Exception as e:
            log_warning(f"[TempFileManager] Error cleaning up temp files: {e}")
        
        return deleted_count

