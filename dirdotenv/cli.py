"""CLI interface for dirdotenv."""

import sys
import os
import argparse
from .parser import load_env
from .loader import (
    load_env_with_inheritance,
    find_env_files_in_tree,
    get_loaded_keys,
    get_unloaded_keys,
    format_export_commands,
    format_unset_commands,
    format_message
)


def get_bash_hook():
    """Return bash/zsh hook code."""
    return '''_dirdotenv_load() {
    # Track directory changes
    if [[ "$_dirdotenv_last_dir" != "$PWD" ]]; then
        _dirdotenv_last_dir="$PWD"
        
        # Check if we have env files or need to clean up
        if command -v dirdotenv &> /dev/null; then
            local output
            if output=$(dirdotenv load --shell bash 2>&1); then
                eval "$output"
            fi
        fi
    fi
}

if [[ -z "$PROMPT_COMMAND" ]]; then
    PROMPT_COMMAND="_dirdotenv_load"
else
    PROMPT_COMMAND="${PROMPT_COMMAND};_dirdotenv_load"
fi
'''


def get_zsh_hook():
    """Return zsh hook code."""
    return '''_dirdotenv_load() {
    # Track directory changes
    if [[ "$_dirdotenv_last_dir" != "$PWD" ]]; then
        _dirdotenv_last_dir="$PWD"
        
        # Check if we have env files or need to clean up
        if command -v dirdotenv &> /dev/null; then
            local output
            if output=$(dirdotenv load --shell zsh 2>&1); then
                eval "$output"
            fi
        fi
    fi
}

autoload -U add-zsh-hook
add-zsh-hook chpwd _dirdotenv_load
_dirdotenv_load
'''


def get_fish_hook():
    """Return fish hook code."""
    return '''function _dirdotenv_load --on-variable PWD
    # Track directory changes
    if test "$_dirdotenv_last_dir" != "$PWD"
        set -g _dirdotenv_last_dir $PWD
        
        if command -v dirdotenv > /dev/null 2>&1
            set -l output (dirdotenv load --shell fish 2>&1)
            if test $status -eq 0
                eval $output
            end
        end
    end
end

_dirdotenv_load
'''


def get_powershell_hook():
    """Return PowerShell hook code."""
    return '''function global:_dirdotenv_load {
    $currentDir = Get-Location
    
    # Track directory changes
    if ($global:_dirdotenv_last_dir -ne $currentDir.Path) {
        $global:_dirdotenv_last_dir = $currentDir.Path
        
        if (Get-Command dirdotenv -ErrorAction SilentlyContinue) {
            $output = dirdotenv load --shell powershell 2>&1
            if ($LASTEXITCODE -eq 0) {
                Invoke-Expression $output
            }
        }
    }
}

# Store original prompt function if it exists
if (Test-Path function:prompt) {
    $global:_dirdotenv_prompt_old = Get-Content function:prompt
}

function global:prompt {
    _dirdotenv_load
    if ($global:_dirdotenv_prompt_old) {
        Invoke-Command -ScriptBlock ([ScriptBlock]::Create($global:_dirdotenv_prompt_old))
    } else {
        "PS $($executionContext.SessionState.Path.CurrentLocation)$('>' * ($nestedPromptLevel + 1)) "
    }
}
'''


def load_command(args):
    """Handle the load command with inheritance and cleanup."""
    shell = args.shell
    current_dir = os.getcwd()
    
    # Load with inheritance
    new_vars, loaded_dirs = load_env_with_inheritance(current_dir)
    
    # Get previously loaded vars from environment variable
    old_keys_str = os.environ.get('_DIRDOTENV_KEYS', '')
    old_keys = set(old_keys_str.split(':')) if old_keys_str else set()
    
    # Build old vars dict from current environment
    old_vars = {key: os.environ.get(key, '') for key in old_keys if key in os.environ}
    
    output_lines = []
    
    # Determine what changed
    loaded_keys = get_loaded_keys(old_vars, new_vars)
    unloaded_keys = get_unloaded_keys(old_vars, new_vars)
    
    # Unset variables that should be removed
    if unloaded_keys:
        output_lines.append(format_unset_commands(unloaded_keys, shell))
        output_lines.append(format_message(f"dirdotenv: unloaded {' '.join(sorted(unloaded_keys))}", shell))
    
    # Export new/changed variables
    if new_vars:
        output_lines.append(format_export_commands(new_vars, shell))
        
        # Store the keys we're managing
        all_keys = ':'.join(sorted(new_vars.keys()))
        if shell in ['bash', 'zsh']:
            output_lines.append(f"export _DIRDOTENV_KEYS='{all_keys}'")
        elif shell == 'fish':
            output_lines.append(f"set -gx _DIRDOTENV_KEYS '{all_keys}'")
        elif shell == 'powershell':
            output_lines.append(f"$env:_DIRDOTENV_KEYS = '{all_keys}'")
        
        # Show what was loaded
        if loaded_keys:
            output_lines.append(format_message(f"dirdotenv: loaded {' '.join(sorted(loaded_keys))}", shell))
    elif old_keys:
        # Clear the tracking variable if nothing is loaded anymore
        if shell in ['bash', 'zsh']:
            output_lines.append("unset _DIRDOTENV_KEYS")
        elif shell == 'fish':
            output_lines.append("set -e _DIRDOTENV_KEYS")
        elif shell == 'powershell':
            output_lines.append("Remove-Item Env:_DIRDOTENV_KEYS -ErrorAction SilentlyContinue")
    
    print('\n'.join(output_lines))
    return 0


def main():
    """Main entry point for the dirdotenv CLI."""
    parser = argparse.ArgumentParser(
        description='Load environment variables from .env and .envrc files',
        prog='dirdotenv'
    )
    
    # Check if first argument is a known subcommand
    if len(sys.argv) > 1 and sys.argv[1] in ['hook', 'load']:
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Hook subcommand
        hook_parser = subparsers.add_parser('hook', help='Output shell hook code')
        hook_parser.add_argument(
            'shell',
            choices=['bash', 'zsh', 'fish', 'powershell'],
            help='Shell to generate hook for'
        )
        
        # Load subcommand (used internally by hooks)
        load_parser = subparsers.add_parser('load', help='Load environment with inheritance (used by hooks)')
        load_parser.add_argument(
            '--shell',
            choices=['bash', 'zsh', 'fish', 'powershell'],
            default='bash',
            help='Shell format for export commands'
        )
        
        args = parser.parse_args()
        
        # Handle hook command
        if args.command == 'hook':
            if args.shell == 'bash':
                print(get_bash_hook())
            elif args.shell == 'zsh':
                print(get_zsh_hook())
            elif args.shell == 'fish':
                print(get_fish_hook())
            elif args.shell == 'powershell':
                print(get_powershell_hook())
            return 0
        
        # Handle load command
        if args.command == 'load':
            return load_command(args)
    
    # Default behavior (load env vars without inheritance - backward compatible)
    parser.add_argument(
        'directory',
        nargs='?',
        default='.',
        help='Directory containing .env or .envrc files (default: current directory)'
    )
    parser.add_argument(
        '--shell',
        choices=['bash', 'zsh', 'fish', 'powershell'],
        default='bash',
        help='Shell format for export commands (default: bash)'
    )
    parser.add_argument(
        '--exec',
        dest='exec_command',
        nargs=argparse.REMAINDER,
        help='Execute command with loaded environment variables'
    )
    
    args = parser.parse_args()
    
    # Load environment variables (single directory, no inheritance)
    env_vars = load_env(args.directory)
    
    if not env_vars:
        print("No environment variables found in .env or .envrc files", file=sys.stderr)
        return 0
    
    # If --exec is specified, execute the command with the loaded environment
    if args.exec_command:
        # Merge with current environment
        new_env = os.environ.copy()
        new_env.update(env_vars)
        
        # Execute the command
        import subprocess
        try:
            result = subprocess.run(args.exec_command, env=new_env)
            return result.returncode
        except FileNotFoundError:
            print(f"Command not found: {args.exec_command[0]}", file=sys.stderr)
            return 127
    
    # Otherwise, output shell commands to source
    print(format_export_commands(env_vars, args.shell))
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
