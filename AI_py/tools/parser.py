# AI_py/tool_parser.py
"""
Tool call parser for AI function calling.

Parses function calls from AI responses using special markers.
Based on chatllm.cpp tool calling implementation.
"""

import json
import re
from typing import Optional, Tuple

# Function call markers (using simpler ASCII markers for better compatibility)
FN_NAME = '[FUNCTION]'
FN_ARGS = '[ARGS]'
FN_RESULT = '[RESULT]'
FN_RETURN = '[RETURN]'

# Alternative markers (Unicode symbols from chatllm.cpp - may work better with some models)
FN_NAME_UNICODE = '✿FUNCTION✿'
FN_ARGS_UNICODE = '✿ARGS✿'
FN_RESULT_UNICODE = '✿RESULT✿'
FN_RETURN_UNICODE = '✿RETURN✿'

def parse_function_call(response: str) -> Optional[Tuple[str, dict]]:
    """
    Parse function call from AI response.
    
    Expected format:
    [FUNCTION]: tool_name
    [ARGS]: {"param": "value"}
    
    Returns:
        Tuple of (tool_name, args_dict) if found, None otherwise
    """
    # Try ASCII markers first
    tool_name, args = _parse_with_markers(response, FN_NAME, FN_ARGS)
    if tool_name is not None:  # Check if tool_name exists (args can be empty dict {})
        return tool_name, args
    
    # Try Unicode markers as fallback
    tool_name, args = _parse_with_markers(response, FN_NAME_UNICODE, FN_ARGS_UNICODE)
    if tool_name is not None:  # Check if tool_name exists (args can be empty dict {})
        return tool_name, args
    
    return None

def _parse_with_markers(response: str, name_marker: str, args_marker: str) -> Tuple[Optional[str], Optional[dict]]:
    """Parse function call using specific markers."""
    try:
        lines = response.split('\n')
        tool_name = None
        args_start_idx = None
        
        # Find function name
        for i, line in enumerate(lines):
            if name_marker in line:
                # Extract tool name after marker
                parts = line.split(name_marker, 1)
                if len(parts) > 1:
                    tool_name = parts[1].strip().strip(':').strip()
                    break
        
        if not tool_name:
            return None, None
        
        # Find args section
        for i, line in enumerate(lines):
            if args_marker in line:
                args_start_idx = i
                break
        
        if args_start_idx is None:
            # If no [ARGS] marker found, but we have a tool name, return it with empty args
            # This handles cases where AI only provides [FUNCTION] without [ARGS]
            if tool_name:
                return tool_name, {}
            return None, None
        
        # Extract JSON args - first try same line, then multi-line
        args_line = lines[args_start_idx]
        args_str = None
        
        # Try to extract args from the same line as [ARGS] marker
        if args_marker in args_line:
            parts = args_line.split(args_marker, 1)
            if len(parts) > 1:
                same_line_content = parts[1].strip().strip(':').strip()
                if same_line_content:
                    # Check if it's valid JSON on the same line
                    if same_line_content.startswith('{') or same_line_content.startswith('['):
                        args_str = same_line_content
                    elif same_line_content == '{}' or same_line_content == '[]':
                        args_str = same_line_content
        
        # If same-line extraction didn't work, try multi-line
        if not args_str:
            args_lines = []
            for i in range(args_start_idx + 1, len(lines)):
                line = lines[i].strip()
                # Stop at next marker or empty line after JSON
                if line.startswith('[') or line.startswith('✿'):
                    # Check if it's another marker
                    if any(marker in line for marker in [FN_NAME, FN_ARGS, FN_RESULT, FN_RETURN, 
                                                          FN_NAME_UNICODE, FN_ARGS_UNICODE, 
                                                          FN_RESULT_UNICODE, FN_RETURN_UNICODE]):
                        break
                args_lines.append(line)
            
            args_str = '\n'.join(args_lines).strip()
        
        # Remove trailing markers if present
        for marker in [FN_RESULT, FN_RETURN, FN_RESULT_UNICODE, FN_RETURN_UNICODE]:
            if args_str.endswith(marker):
                args_str = args_str[:-len(marker)].strip()
        
        # Try to parse as JSON
        if args_str:
            # Handle case where args might be empty (no parameters)
            if args_str == '{}' or args_str == '':
                return tool_name, {}
            
            # Try to find JSON object in the string
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', args_str)
            if json_match:
                args_str = json_match.group(0)
            
            try:
                args = json.loads(args_str)
                return tool_name, args
            except json.JSONDecodeError:
                # Try to fix common JSON issues
                # Remove trailing commas
                args_str = re.sub(r',\s*}', '}', args_str)
                args_str = re.sub(r',\s*]', ']', args_str)
                try:
                    args = json.loads(args_str)
                    return tool_name, args
                except:
                    pass
        
        # If no args found, return empty dict
        return tool_name, {}
        
    except Exception as e:
        from error_logger import log_debug
        log_debug(f"[ToolParser] Error parsing function call: {e}")
        return None, None

def has_function_call(response: str) -> bool:
    """Check if response contains a function call."""
    # Quick check for function markers before full parsing
    if FN_NAME in response or FN_NAME_UNICODE in response:
        # If we see the marker, try to parse it
        result = parse_function_call(response)
        return result is not None
    return False

def extract_final_answer(response: str) -> Optional[str]:
    """
    Extract final answer after function call.
    
    Looks for [RETURN] marker or text after [RESULT] marker.
    """
    # Try to find return marker
    return_markers = [FN_RETURN, FN_RETURN_UNICODE]
    for marker in return_markers:
        if marker in response:
            parts = response.split(marker, 1)
            if len(parts) > 1:
                answer = parts[1].strip().strip(':').strip()
                if answer:
                    return answer
    
    # Try to find result marker and extract text after it
    result_markers = [FN_RESULT, FN_RESULT_UNICODE]
    for marker in result_markers:
        if marker in response:
            parts = response.split(marker, 1)
            if len(parts) > 1:
                # Get text after result, but before next marker
                text = parts[1]
                # Remove any trailing markers
                for m in [FN_RETURN, FN_RETURN_UNICODE]:
                    if m in text:
                        text = text.split(m)[0]
                answer = text.strip().strip(':').strip()
                if answer:
                    return answer
    
    return None

