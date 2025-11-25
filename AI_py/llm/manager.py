"""
LLM Model Manager

Handles model loading, caching, and lifecycle management.
Separated from query logic for better maintainability.
"""

import os
from typing import Optional
from llama_cpp import Llama

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from error_logger import log_info, log_warning, log_error, log_debug
from settings_manager import get_settings_manager


class LLMManager:
    """Manages LLM model loading and lifecycle."""
    
    def __init__(self):
        """Initialize LLM manager."""
        self.model_path: Optional[str] = None
        self.model: Optional[Llama] = None
        self.settings = get_settings_manager()
        self._available = None  # Cache availability check
    
    def is_available(self) -> bool:
        """Check if llama-cpp-python is available and model file exists."""
        if self._available is not None:
            return self._available
        
        # Check if llama-cpp-python is available
        try:
            from llama_cpp import Llama
        except ImportError:
            self._available = False
            log_warning("llama-cpp-python not installed. Install with: pip install llama-cpp-python")
            return False
        
        # Find model file
        self.model_path = self._find_model_file()
        if self.model_path:
            preferred_model = self.get_preferred_model()
            log_info(f"[LLMManager] Found model file for {preferred_model}: {self.model_path}")
            self._available = True
            return True
        else:
            preferred_model = self.get_preferred_model()
            log_warning(f"{preferred_model} model file not found. Please ensure model is available.")
            self._available = False
            return False
    
    def get_model(self) -> Llama:
        """
        Get or load the LLM model (lazy loading).
        
        Returns:
            Llama: The loaded model instance
            
        Raises:
            RuntimeError: If model cannot be loaded
        """
        if self.model is not None:
            return self.model
        
        if not self.is_available():
            error_msg = "llama-cpp-python not available. Please install: pip install llama-cpp-python"
            log_error(error_msg)
            raise RuntimeError(error_msg)
        
        if not self.model_path:
            # Try to find the model file again (in case it was added after initialization)
            self.model_path = self._find_model_file()
            if not self.model_path:
                preferred_model = self.get_preferred_model()
                error_msg = f"Model file not found for {preferred_model}. Please ensure model is available in ./models/ or Ollama blobs directory."
                log_error(error_msg)
                raise RuntimeError(error_msg)
        
        try:
            log_debug(f"[LLMManager] Loading model from: {self.model_path}")
            log_info(f"[LLMManager] Loading model (this may take a few seconds on first use)...")
            # SmolLM2 supports 8192 context window, use it for better performance
            # For smaller models, this will be capped at their training limit
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=8192,  # Context window (SmolLM2 supports 8192)
                n_threads=4,  # CPU threads
                verbose=False
            )
            log_info("[LLMManager] Model loaded successfully")
            return self.model
        except Exception as e:
            error_msg = f"Error loading model from {self.model_path}: {e}"
            log_error(error_msg, e)
            raise RuntimeError(error_msg)
    
    def _find_model_file(self) -> Optional[str]:
        """Find the GGUF model file (from Ollama blobs or local directory)."""
        preferred_model = self.get_preferred_model()
        
        # Model file mapping and size ranges
        model_configs = {
            'smollm:360m': {'filename': 'smollm-360m.gguf', 'size_min': 200, 'size_max': 250},
            'qwen:0.5b': {'filename': 'qwen-0.5b.gguf', 'size_min': 280, 'size_max': 400},
            'tinyllama': {'filename': 'tinyllama.gguf', 'size_min': 600, 'size_max': 700},
            'gemma:1b': {'filename': 'gemma-1b-it-q4_k_m.gguf', 'size_min': 1600, 'size_max': 1800},
            'gemma:1b-q8': {'filename': 'gemma-1b-it-q8_0.gguf', 'size_min': 3200, 'size_max': 3500},
            'smollm2:1.7b': {'filename': 'SmolLM2-1.7B-Instruct-Q4_K_M.gguf', 'size_min': 1900, 'size_max': 2100},
            'smollm2:1.7b-q8': {'filename': 'SmolLM2-1.7B-Instruct-Q8_0.gguf', 'size_min': 3800, 'size_max': 4200}
        }
        
        config = model_configs.get(preferred_model, model_configs['smollm:360m'])
        
        # Check local models directory first
        local_model = f"./models/{config['filename']}"
        if os.path.exists(local_model):
            log_info(f"[LLMManager] Found local model: {local_model}")
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
                        log_info(f"[LLMManager] Found model blob for {preferred_model}: {file} ({size_mb:.1f} MB)")
                        return file_path
        
        log_warning(f"[LLMManager] Model file not found for {preferred_model}. Expected size: {config['size_min']}-{config['size_max']}MB")
        return None
    
    def get_preferred_model(self) -> str:
        """Get preferred model from settings."""
        # Try both keys for compatibility (settings.get requires section and key)
        model = self.settings.get('AI', 'ai_model') or self.settings.get('AI', 'preferred_model')
        return model if model else 'qwen:0.5b'
    
    def get_model_name(self) -> str:
        """Get the name of the currently loaded or preferred model."""
        return self.get_preferred_model()

