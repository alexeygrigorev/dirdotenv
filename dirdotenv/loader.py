"""Directory-aware environment variable loading with inheritance and cleanup."""

import os
from typing import Dict, Set, Tuple, Optional
from .parser import load_env


def find_env_files_in_tree(current_dir: str) -> list:
    """
    Find all directories with .env or .envrc files from current directory up to root.
    
    Returns list of directories from root to current, each containing env files.
    """
    directories = []
    path = os.path.abspath(current_dir)
    
    while True:
        if os.path.isfile(os.path.join(path, '.env')) or os.path.isfile(os.path.join(path, '.envrc')):
            directories.insert(0, path)  # Insert at beginning to go root->leaf
        
        parent = os.path.dirname(path)
        if parent == path:  # Reached root
            break
        path = parent
    
    return directories


def load_env_with_inheritance(current_dir: str) -> Tuple[Dict[str, str], list]:
    """
    Load environment variables with directory inheritance.
    
    Loads from root to current directory, allowing child directories to override parent values.
    
    Returns:
        Tuple of (env_vars dict, list of directory paths that were loaded)
    """
    directories = find_env_files_in_tree(current_dir)
    env_vars = {}
    
    # Load from root to current, allowing later directories to override
    for directory in directories:
        env_vars.update(load_env(directory))
    
    return env_vars, directories


def get_loaded_keys(old_vars: Dict[str, str], new_vars: Dict[str, str]) -> Set[str]:
    """
    Get keys that were added or modified.
    
    Args:
        old_vars: Previous environment variables
        new_vars: New environment variables
        
    Returns:
        Set of keys that were added or changed
    """
    changed_keys = set()
    
    for key, value in new_vars.items():
        if key not in old_vars or old_vars[key] != value:
            changed_keys.add(key)
    
    return changed_keys


def get_unloaded_keys(old_vars: Dict[str, str], new_vars: Dict[str, str]) -> Set[str]:
    """
    Get keys that should be unloaded (were in old but not in new).
    
    Args:
        old_vars: Previous environment variables
        new_vars: New environment variables
        
    Returns:
        Set of keys that should be unset
    """
    return set(old_vars.keys()) - set(new_vars.keys())


def format_export_commands(env_vars: Dict[str, str], shell: str = 'bash') -> str:
    """
    Format environment variable export commands for the specified shell.
    
    Args:
        env_vars: Dictionary of environment variables
        shell: Shell type (bash, zsh, fish, powershell)
        
    Returns:
        String containing export commands
    """
    lines = []
    
    if shell in ['bash', 'zsh']:
        for key, value in env_vars.items():
            escaped_value = value.replace("'", "'\\''")
            lines.append(f"export {key}='{escaped_value}'")
    elif shell == 'fish':
        for key, value in env_vars.items():
            escaped_value = value.replace("'", "\\'")
            lines.append(f"set -gx {key} '{escaped_value}'")
    elif shell == 'powershell':
        for key, value in env_vars.items():
            escaped_value = value.replace("'", "''")
            lines.append(f"$env:{key} = '{escaped_value}'")
    
    return '\n'.join(lines)


def format_unset_commands(keys: Set[str], shell: str = 'bash') -> str:
    """
    Format commands to unset environment variables for the specified shell.
    
    Args:
        keys: Set of variable names to unset
        shell: Shell type (bash, zsh, fish, powershell)
        
    Returns:
        String containing unset commands
    """
    lines = []
    
    if shell in ['bash', 'zsh']:
        for key in keys:
            lines.append(f"unset {key}")
    elif shell == 'fish':
        for key in keys:
            lines.append(f"set -e {key}")
    elif shell == 'powershell':
        for key in keys:
            lines.append(f"Remove-Item Env:{key} -ErrorAction SilentlyContinue")
    
    return '\n'.join(lines)


def format_message(message: str, shell: str = 'bash') -> str:
    """
    Format a message to display to the user for the specified shell.
    
    Args:
        message: Message to display
        shell: Shell type (bash, zsh, fish, powershell)
        
    Returns:
        String containing echo command
    """
    if shell in ['bash', 'zsh']:
        escaped = message.replace("'", "'\\''")
        return f"echo '{escaped}' >&2"
    elif shell == 'fish':
        escaped = message.replace("'", "\\'")
        return f"echo '{escaped}' >&2"
    elif shell == 'powershell':
        escaped = message.replace("'", "''")
        return f"Write-Host '{escaped}'"
    
    return ""
