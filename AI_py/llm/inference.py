"""
Inference Engine

Handles LLM inference calls with proper error handling and response processing.
Separated from business logic for better testability.
"""

from typing import Dict, List, Optional
from llama_cpp import Llama

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from error_logger import log_info, log_warning, log_error, log_debug


class InferenceEngine:
    """Handles LLM inference operations."""
    
    def __init__(self, model: Llama):
        """
        Initialize inference engine with a model.
        
        Args:
            model: Loaded Llama model instance
        """
        self.model = model
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 512,
        temperature: float = 0.0,
        top_p: float = 0.1
    ) -> Dict:
        """
        Generate chat completion using the model.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 = deterministic)
            top_p: Nucleus sampling parameter
            
        Returns:
            Dict with 'choices' containing response
        """
        try:
            log_debug(f"[InferenceEngine] Generating completion with {len(messages)} messages, max_tokens={max_tokens}")
            response = self.model.create_chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p
            )
            return response
        except Exception as e:
            log_error(f"[InferenceEngine] Error during inference: {e}", e)
            raise
    
    def extract_response_text(self, response: Dict) -> Optional[str]:
        """
        Extract text content from model response.
        
        Args:
            response: Model response dict
            
        Returns:
            Extracted text content or None
        """
        try:
            if 'choices' in response and len(response['choices']) > 0:
                message = response['choices'][0].get('message', {})
                content = message.get('content', '').strip()
                return content if content else None
            return None
        except Exception as e:
            log_warning(f"[InferenceEngine] Error extracting response text: {e}")
            return None

