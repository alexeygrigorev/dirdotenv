"""Directory-aware environment variable loading with inheritance and cleanup."""

import os
import sys
from typing import Dict, Set, Tuple, Optional
from dirdotenv.parser import load_env


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


def compute_env_state(current_dir: str) -> str:
    """
    Compute a state string representing the current state of .env and .envrc files.
    
    This includes the directory path and modification times of all relevant env files
    from root to current directory.
    
    Args:
        current_dir: Current directory path
        
    Returns:
        State string that changes when files are added, removed, or modified
    """
    state_parts = []
    path = os.path.abspath(current_dir)
    
    # Collect all parent directories up to root
    check_paths = []
    while True:
        check_paths.append(path)
        parent = os.path.dirname(path)
        if parent == path:  # Reached root
            break
        path = parent
    
    # Reverse to go from root to current
    check_paths.reverse()
    
    # Check each directory for .env or .envrc files and record their state
    for directory in check_paths:
        for filename in ['.env', '.envrc']:
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                try:
                    mtime = os.path.getmtime(filepath)
                    state_parts.append(f"{filepath}:{mtime}")
                except (OSError, IOError):
                    # If we can't read the file, skip it
                    pass
    
    # Include the current directory in the state
    state_parts.insert(0, f"dir:{current_dir}")
    
    return ";".join(state_parts)


def has_state_changed(old_state: Optional[str], current_dir: str) -> bool:
    """
    Check if the environment state has changed.
    
    Args:
        old_state: Previous state string (None if first run)
        current_dir: Current directory path
        
    Returns:
        True if state has changed, False otherwise
    """
    if old_state is None:
        return True
    
    new_state = compute_env_state(current_dir)
    return old_state != new_state


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


def convert_windows_path_to_unix(path: str) -> str:
    """
    Convert Windows path to Unix-style path for MinGW/Git Bash.
    
    Examples:
        C:\\Users\\user\\project -> /c/Users/user/project
        C:/Users/user/project -> /c/Users/user/project
        relative\\path -> relative/path
    
    Args:
        path: Windows-style path
        
    Returns:
        Unix-style path
    """
    # Convert backslashes to forward slashes
    path = path.replace('\\', '/')
    
    # Convert Windows drive letter (C:/) to Unix style (/c/)
    if len(path) >= 2 and path[1] == ':':
        drive = path[0].lower()
        rest = path[2:] if len(path) > 2 else ''
        # Remove leading slash if present
        if rest.startswith('/'):
            rest = rest[1:]
        path = f'/{drive}/{rest}' if rest else f'/{drive}'
    
    return path


def is_windows_mingw() -> bool:
    """
    Check if we're running on Windows with MinGW/Git Bash.
    
    Returns:
        True if running on Windows with a Unix-like shell environment
    """
    # Check if we're on Windows
    if sys.platform != 'win32':
        return False
    
    # Check for common MinGW/Git Bash environment variables
    msystem = os.environ.get('MSYSTEM', '')
    if msystem:  # Git Bash sets MSYSTEM (MINGW64, MINGW32, MSYS, etc.)
        return True
    
    # Check if SHELL variable is set (common in Unix-like environments)
    shell = os.environ.get('SHELL', '')
    if 'bash' in shell.lower() or 'sh' in shell.lower():
        return True
    
    return False


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
    
    # Check if we need to convert paths for MinGW/Git Bash
    convert_paths = (shell in ['bash', 'zsh']) and is_windows_mingw()
    
    if shell in ['bash', 'zsh']:
        for key, value in env_vars.items():
            # Convert Windows paths to Unix-style for MinGW/Git Bash
            if convert_paths:
                value = convert_windows_path_to_unix(value)
            
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
