"""
File reading utilities for the MCP server
"""
import os
from typing import Optional


def read_file_content(file_path: str, relative_to_file: Optional[str] = None) -> str:
    """
    Read content from a file with support for both absolute and relative paths
    
    Args:
        file_path: Path to the file to read (can be absolute or relative)
        relative_to_file: If provided, treat file_path as relative to this file's directory
        
    Returns:
        File content as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        IOError: If file cannot be read
    """
    try:
        # Handle relative path case
        if relative_to_file and not os.path.isabs(file_path):
            base_dir = os.path.dirname(os.path.abspath(relative_to_file))
            full_path = os.path.join(base_dir, file_path)
        else:
            full_path = file_path
            
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
            
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {full_path}")
    except IOError as e:
        raise IOError(f"Error reading file {full_path}: {str(e)}")


def read_prompt_file(relative_path: str, caller_file: str = __file__) -> str:
    """
    Read prompt file content based on relative path from caller file
    
    Args:
        relative_path: Relative path to the prompt file (e.g., '../../reference/prompt/QueryTypeDecision.md')
        caller_file: The file from which this function is called (default: this file)
        
    Returns:
        File content as string
    """
    return read_file_content(relative_path, relative_to_file=caller_file)
