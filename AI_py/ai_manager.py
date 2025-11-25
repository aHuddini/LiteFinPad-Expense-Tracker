# AI_py/ai_manager.py
"""
AI feature lifecycle and availability management.

IMPORTANT: Direct Inference (100% OFFLINE)
------------------------------------------
We use llama-cpp-python for direct model inference - no server required!
The model runs in-process with the application.
This is 100% OFFLINE - no data leaves your machine, no internet required.
All AI processing happens locally on your computer.

The model file (GGUF format) can be:
- Downloaded from HuggingFace
- Found in Ollama's blob storage (if Ollama was previously used)
- Bundled with the application
"""

import subprocess
import os
import sys
from typing import Optional
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from error_logger import log_info, log_warning, log_error, log_debug
from settings_manager import get_settings_manager

class AIManager:
    """Manages AI feature availability and configuration."""
    
    def __init__(self, expense_tracker):
        """Initialize AI manager."""
        self.expense_tracker = expense_tracker
        self.settings = get_settings_manager()
        self._available = None  # Cache availability check
        self._model_cache = {}  # Cache for multiple model checks
        self._installed_models_list = None  # Cache full list of installed models
    
    def is_available(self) -> bool:
        """
        Check if llama-cpp-python is available and model file exists.
        
        Note: Direct inference - no server required. Model runs in-process.
        This is 100% offline - no data leaves your machine.
        """
        if self._available is not None:
            return self._available
        
        # Check if llama-cpp-python is available
        try:
            from llama_cpp import Llama
        except ImportError:
            self._available = False
            log_warning("llama-cpp-python not installed - run: pip install llama-cpp-python")
            return False
        
        # Check if model file exists
        model_path = self._find_model_file()
        preferred_model = self.get_preferred_model()
        if model_path:
            self._available = True
            log_info(f"AI features enabled - {preferred_model} model file found: {model_path}")
        else:
            self._available = False
            log_warning(f"{preferred_model} model file not found. Please ensure model is available.")
        
        return self._available
    
    def _find_model_file(self) -> Optional[str]:
        """Find the GGUF model file (from Ollama blobs or local directory)."""
        # Get preferred model from settings
        preferred_model = self.get_preferred_model()
        
        # Model file mapping and size ranges
        model_configs = {
            'smollm:360m': {'filename': 'smollm-360m.gguf', 'size_min': 200, 'size_max': 250},
            'qwen:0.5b': {'filename': 'qwen-0.5b.gguf', 'size_min': 280, 'size_max': 400},
            'tinyllama': {'filename': 'tinyllama.gguf', 'size_min': 600, 'size_max': 700}
        }
        
        config = model_configs.get(preferred_model, model_configs['smollm:360m'])
        
        # Check local models directory first
        local_model = f"./models/{config['filename']}"
        if os.path.exists(local_model):
            log_info(f"[AI] Found local model: {local_model}")
            return os.path.abspath(local_model)
        
        # Check Ollama blobs directory
        home = os.path.expanduser("~")
        ollama_models_path = os.path.join(home, ".ollama", "models")
        blobs_path = os.path.join(ollama_models_path, "blobs")
        
        if os.path.exists(blobs_path):
            # Find model blob by size
            for file in os.listdir(blobs_path):
                file_path = os.path.join(blobs_path, file)
                if os.path.isfile(file_path):
                    size_mb = os.path.getsize(file_path) / (1024 * 1024)
                    if config['size_min'] < size_mb < config['size_max']:
                        log_info(f"[AI] Found model blob for {preferred_model}: {file} ({size_mb:.1f} MB)")
                        return file_path
        
        log_warning(f"[AI] Model file not found for {preferred_model}. Expected size: {config['size_min']}-{config['size_max']}MB")
        return None
    
    def _get_installed_models(self) -> list:
        """
        Get list of available model files.
        
        Checks for model files in local directory or Ollama blobs.
        No server required - checks local file system.
        """
        if self._installed_models_list is not None:
            return self._installed_models_list
        
        if not self.is_available():
            return []
        
        self._installed_models_list = []
        
        # Check local models directory
        local_models_dir = "./models"
        if os.path.exists(local_models_dir):
            for file in os.listdir(local_models_dir):
                if file.endswith('.gguf'):
                    self._installed_models_list.append(file.replace('.gguf', ''))
        
        # Check Ollama blobs directory
        home = os.path.expanduser("~")
        ollama_models_path = os.path.join(home, ".ollama", "models")
        blobs_path = os.path.join(ollama_models_path, "blobs")
        
        if os.path.exists(blobs_path):
            # Count model blobs by size
            for file in os.listdir(blobs_path):
                file_path = os.path.join(blobs_path, file)
                if os.path.isfile(file_path):
                    size_mb = os.path.getsize(file_path) / (1024 * 1024)
                    if 200 < size_mb < 250:  # ~220MB model (SmolLM 360M)
                        self._installed_models_list.append('smollm:360m')
                        break
        
        log_debug(f"[AI] Found {len(self._installed_models_list)} available models: {self._installed_models_list}")
        return self._installed_models_list
    
    def is_model_installed(self, model_name: str = 'smollm:360m') -> bool:
        """
        Check if specific model file is available.
        
        Args:
            model_name: Model name to check (e.g., 'smollm:360m', 'tinyllama')
        
        Returns:
            True if model file is available, False otherwise
        """
        if not self.is_available():
            return False
        
        # Check cache first
        if model_name in self._model_cache:
            return self._model_cache[model_name]
        
        # Check if model file exists
        model_path = self._find_model_file()
        is_installed = model_path is not None
        
        # Cache result
        self._model_cache[model_name] = is_installed
        
        if is_installed:
            log_debug(f"Model '{model_name}' is available at: {model_path}")
        else:
            log_debug(f"Model '{model_name}' is not available")
        
        return is_installed
    
    def can_use_ai_chat(self) -> bool:
        """
        Check if AI Chat feature can be used (llama-cpp-python + model file available).
        
        This is the PRIMARY check - verifies:
        1. llama-cpp-python is installed
        2. Required model file is available locally
        
        Returns:
            True if llama-cpp-python is available AND model file exists
        """
        if not self.is_available():
            return False
        
        # Check if the required model exists locally
        model_name = self.get_preferred_model()
        model_installed = self.is_model_installed(model_name)
        
        if not model_installed:
            log_debug(f"Model '{model_name}' not found - model file not available")
        
        return model_installed
    
    def get_preferred_model(self) -> str:
        """
        Get preferred model from settings, fallback to smollm:360m.
        
        Returns:
            Model name string (e.g., 'smollm:360m')
        """
        model = self.settings.get(
            'AI',
            'preferred_model',
            default='smollm:360m',  # SmolLM 360M - fastest for proof-of-concept
            value_type=str
        )
        return model
    
    def get_installed_models(self) -> list:
        """
        Get list of all installed Ollama models.
        
        Returns:
            List of model name strings
        """
        return self._get_installed_models()
    
    def get_recommended_models(self) -> list:
        """
        Get list of recommended models with descriptions.
        
        Returns:
            List of dicts with model information
        """
        return [
            {
                'name': 'smollm:360m',
                'size': '220MB',
                'ram': '1-2GB',
                'speed': '40-60 tokens/sec',
                'strength': 'Fast common-sense extraction, low latency',
                'best_for': 'Quick queries, casual chats'
            },
            {
                'name': 'tinyllama',
                'size': '635MB',
                'ram': '2-4GB',
                'speed': '25-45 tokens/sec',
                'strength': 'Reliable math/sums, edge-device friendly',
                'best_for': 'Numerical accuracy, expense totals'
            },
            {
                'name': 'qwen:0.5b',
                'size': '300MB',
                'ram': '1GB',
                'speed': '35-55 tokens/sec',
                'strength': 'Precise extractions, category breakdowns',
                'best_for': 'Structured data analysis, JSON parsing'
            }
        ]
    
    def clear_cache(self):
        """Clear cached availability and model checks. Useful after installing Ollama or models."""
        log_debug("Clearing AI manager cache")
        self._available = None
        self._model_cache = {}
        self._installed_models_list = None
    
    def refresh(self):
        """Refresh availability and model checks. Alias for clear_cache()."""
        self.clear_cache()

