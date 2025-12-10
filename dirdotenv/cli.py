"""CLI interface for dirdotenv."""

import sys
import os
import argparse
from .parser import load_env


def get_bash_hook():
    """Return bash/zsh hook code."""
    return '''_dirdotenv_load() {
    if [[ "$_dirdotenv_last_dir" != "$PWD" ]]; then
        _dirdotenv_last_dir="$PWD"
        if [[ -f ".env" ]] || [[ -f ".envrc" ]]; then
            if command -v dirdotenv &> /dev/null; then
                local output
                if output=$(dirdotenv 2>&1); then
                    eval "$output"
                fi
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
    if [[ "$_dirdotenv_last_dir" != "$PWD" ]]; then
        _dirdotenv_last_dir="$PWD"
        if [[ -f ".env" ]] || [[ -f ".envrc" ]]; then
            if command -v dirdotenv &> /dev/null; then
                local output
                if output=$(dirdotenv 2>&1); then
                    eval "$output"
                fi
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
    if test -f ".env" -o -f ".envrc"
        if command -v dirdotenv > /dev/null 2>&1
            set -l output (dirdotenv --shell fish 2>&1)
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
    if ($global:_dirdotenv_last_dir -ne $currentDir) {
        $global:_dirdotenv_last_dir = $currentDir
        if ((Test-Path ".env") -or (Test-Path ".envrc")) {
            if (Get-Command dirdotenv -ErrorAction SilentlyContinue) {
                $output = dirdotenv --shell powershell 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Invoke-Expression $output
                }
            }
        }
    }
}

$global:_dirdotenv_prompt_old = $function:prompt
function global:prompt {
    _dirdotenv_load
    & $global:_dirdotenv_prompt_old
}
'''


def main():
    """Main entry point for the dirdotenv CLI."""
    parser = argparse.ArgumentParser(
        description='Load environment variables from .env and .envrc files',
        prog='dirdotenv'
    )
    
    # Check if first argument is 'hook' to handle subcommand
    if len(sys.argv) > 1 and sys.argv[1] == 'hook':
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        hook_parser = subparsers.add_parser('hook', help='Output shell hook code')
        hook_parser.add_argument(
            'shell',
            choices=['bash', 'zsh', 'fish', 'powershell'],
            help='Shell to generate hook for'
        )
        args = parser.parse_args()
        
        # Handle hook command
        if args.shell == 'bash':
            print(get_bash_hook())
        elif args.shell == 'zsh':
            print(get_zsh_hook())
        elif args.shell == 'fish':
            print(get_fish_hook())
        elif args.shell == 'powershell':
            print(get_powershell_hook())
        return 0
    
    # Default behavior (load env vars)
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
    
    # Load environment variables
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
    elif args.shell == 'powershell':
        for key, value in env_vars.items():
            # Escape for PowerShell
            escaped_value = value.replace("'", "''")
            print(f"$env:{key} = '{escaped_value}'")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
