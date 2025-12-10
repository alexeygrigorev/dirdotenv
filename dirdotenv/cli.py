"""CLI interface for dirdotenv."""

import sys
import os
import argparse
from .parser import load_env


def main():
    """Main entry point for the dirdotenv CLI."""
    parser = argparse.ArgumentParser(
        description='Load environment variables from .env and .envrc files',
        prog='dirdotenv'
    )
    parser.add_argument(
        'directory',
        nargs='?',
        default='.',
        help='Directory containing .env or .envrc files (default: current directory)'
    )
    parser.add_argument(
        '--shell',
        choices=['bash', 'zsh', 'fish'],
        default='bash',
        help='Shell format for export commands (default: bash)'
    )
    parser.add_argument(
        '--exec',
        dest='command',
        nargs=argparse.REMAINDER,
        help='Execute command with loaded environment variables'
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    env_vars = load_env(args.directory)
    
    if not env_vars:
        print("No environment variables found in .env or .envrc files", file=sys.stderr)
        return 0
    
    # If --exec is specified, execute the command with the loaded environment
    if args.command:
        # Merge with current environment
        new_env = os.environ.copy()
        new_env.update(env_vars)
        
        # Execute the command
        import subprocess
        try:
            result = subprocess.run(args.command, env=new_env)
            return result.returncode
        except FileNotFoundError:
            print(f"Command not found: {args.command[0]}", file=sys.stderr)
            return 127
    
    # Otherwise, output shell commands to source
    if args.shell in ['bash', 'zsh']:
        for key, value in env_vars.items():
            # Escape single quotes in value
            escaped_value = value.replace("'", "'\\''")
            print(f"export {key}='{escaped_value}'")
    elif args.shell == 'fish':
        for key, value in env_vars.items():
            # Escape single quotes in value for fish
            escaped_value = value.replace("'", "\\'")
            print(f"set -gx {key} '{escaped_value}'")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
