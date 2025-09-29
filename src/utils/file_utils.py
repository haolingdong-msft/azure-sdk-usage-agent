"""
File reading utilities for the MCP server
"""
import os
import inspect
from pathlib import Path
from typing import Optional, Union


def read_file_content(
    file_path: Union[str, Path], 
    relative_to_file: Optional[Union[str, Path]] = None
) -> str:
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
        PermissionError: If file cannot be accessed due to permissions
    """
    try:
        # Convert to Path objects for easier manipulation
        file_path = Path(file_path)
        
        # Handle relative path case
        if relative_to_file and not file_path.is_absolute():
            base_dir = Path(relative_to_file).parent.resolve()
            full_path = base_dir / file_path
        else:
            full_path = file_path.resolve()
        
        # Basic security check - ensure the resolved path doesn't go outside expected boundaries
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {full_path}")
            
        if not full_path.is_file():
            raise IOError(f"Path is not a file: {full_path}")
            
        # Read file with better error handling
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
            
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {full_path}")
    except PermissionError:
        raise PermissionError(f"Permission denied reading file: {full_path}")
    except UnicodeDecodeError as e:
        raise IOError(f"Error decoding file {full_path}: {str(e)}")
    except IOError as e:
        raise IOError(f"Error reading file {full_path}: {str(e)}")


def read_relative_file(relative_path: Union[str, Path], caller_file: Optional[str] = None) -> str:
    """
    Read file content based on relative path from caller file
    
    Args:
        relative_path: Relative path to the file (e.g., '../templates/prompts/QueryTypeDecision.md')
        caller_file: The file from which this function is called. If None, uses the caller's file automatically
        
    Returns:
        File content as string
    """
    # Automatically detect caller file if not provided
    if caller_file is None:
        # Get the caller's frame
        frame = inspect.currentframe().f_back
        caller_file = frame.f_globals['__file__']
    
    return read_file_content(relative_path, relative_to_file=caller_file)


def read_prompt_file(relative_path: str, caller_file: str = None) -> str:
    """
    Read prompt file content based on relative path from caller file
    
    Args:
        relative_path: Relative path to the prompt file (e.g., '../templates/prompts/QueryTypeDecision.md')
        caller_file: The file from which this function is called (deprecated, will be auto-detected if None)
        
    Returns:
        File content as string
        
    Note:
        This function is kept for backward compatibility. Consider using read_relative_file instead.
    """
    return read_relative_file(relative_path, caller_file)


def load_and_format_prompt(table_name: str, user_question: str, caller_file: str = None) -> str:
    """
    Load prompt template for a specific table and format it with user question
    
    Args:
        table_name: Name of the table (used to find the corresponding .md file)
        user_question: User's question to embed in the prompt
        caller_file: The file from which this function is called (auto-detected if None)
        
    Returns:
        Formatted prompt string with user question embedded
        
    Example:
        prompt = load_and_format_prompt("AMEConciseSubReqCCIDCountByMonthProduct", "Show me the top products")
    """
    # Construct the relative path to the prompt file
    prompt_file_path = f"prompts/{table_name}.md"
    
    # Read the prompt template
    prompt_template = read_relative_file(prompt_file_path, caller_file)
    
    # Format the template with the user question
    formatted_prompt = prompt_template.format(user_question=user_question)
    
    return formatted_prompt
