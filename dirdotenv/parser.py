"""Parser for .env and .envrc files."""

import re
import os
from typing import Dict


def parse_env_file(filepath: str) -> Dict[str, str]:
    """
    Parse a .env file and return a dictionary of environment variables.
    
    Supports formats:
    - KEY=value
    - KEY='value'
    - KEY="value"
    
    Args:
        filepath: Path to the .env file
        
    Returns:
        Dictionary of environment variable key-value pairs
    """
    env_vars = {}
    
    if not os.path.exists(filepath):
        return env_vars
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Match KEY=value, KEY='value', or KEY="value"
            match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)=(.*)$', line)
            if match:
                key = match.group(1)
                value = match.group(2)
                
                # Remove quotes if present (only if balanced and matching)
                if len(value) >= 2:
                    if (value.startswith("'") and value.endswith("'")) or \
                       (value.startswith('"') and value.endswith('"')):
                        value = value[1:-1]
                
                env_vars[key] = value
    
    return env_vars


def parse_envrc_file(filepath: str) -> Dict[str, str]:
    """
    Parse a .envrc file and return a dictionary of environment variables.
    
    Supports formats:
    - export KEY=value
    - export KEY='value'
    - export KEY="value"
    
    Args:
        filepath: Path to the .envrc file
        
    Returns:
        Dictionary of environment variable key-value pairs
    """
    env_vars = {}
    
    if not os.path.exists(filepath):
        return env_vars
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Match export KEY=value, export KEY='value', or export KEY="value"
            match = re.match(r'^export\s+([A-Za-z_][A-Za-z0-9_]*)=(.*)$', line)
            if match:
                key = match.group(1)
                value = match.group(2)
                
                # Remove quotes if present (only if balanced and matching)
                if len(value) >= 2:
                    if (value.startswith("'") and value.endswith("'")) or \
                       (value.startswith('"') and value.endswith('"')):
                        value = value[1:-1]
                
                env_vars[key] = value
    
    return env_vars


def load_env(directory: str = '.') -> Dict[str, str]:
    """
    Load environment variables from .env and .envrc files in the specified directory.
    
    Priority (later overrides earlier):
    1. .envrc file
    2. .env file (takes precedence)
    
    Args:
        directory: Directory to search for .env and .envrc files (default: current directory)
        
    Returns:
        Dictionary of environment variable key-value pairs
    """
    env_vars = {}
    
    # Load .envrc file first
    envrc_file = os.path.join(directory, '.envrc')
    env_vars.update(parse_envrc_file(envrc_file))
    
    # Load .env file (overrides .envrc)
    env_file = os.path.join(directory, '.env')
    env_vars.update(parse_env_file(env_file))
    
    return env_vars
