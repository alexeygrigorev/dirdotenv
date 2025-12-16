"""CLI interface for dirdotenv."""

import sys
import os
import argparse
from dirdotenv.parser import load_env
from dirdotenv.loader import (
    load_env_with_inheritance,
    get_loaded_keys,
    get_unloaded_keys,
    format_export_commands,
    format_unset_commands,
    format_message,
    compute_env_state,
    has_state_changed,
)
from dirdotenv.hooks import get_hook
from dirdotenv.__version__ import __version__


def get_invocation_command():
    """Determine how dirdotenv was invoked."""
    # Check for python -m dirdotenv usage
    if sys.argv[0].endswith("__main__.py"):
        return f"{sys.executable} -m dirdotenv"

    # Check for uvx / uv tool run usage
    # Heuristic: executable path contains uv/tools directory structure
    # This covers the case when running via `uvx dirdotenv`
    executable_path = sys.executable.replace(os.sep, "/")
    if "/uv/tools/" in executable_path or "/.uv/tools/" in executable_path:
        return "uvx dirdotenv"

    # Default to dirdotenv (assumed to be in PATH)
    # If the user invoked it via absolute path but not managed by uv,
    # we could theoretically return sys.argv[0], but 'dirdotenv' is safer/cleaner
    # for most installations unless explicitly requested otherwise.
    return "dirdotenv"


def load_command(args):
    """Handle the load command with inheritance and cleanup."""
    shell = args.shell
    current_dir = os.getcwd()

    # Get previous state from environment
    old_state = os.environ.get("_DIRDOTENV_STATE", None)

    # Check if state has changed (directory or files)
    if not has_state_changed(old_state, current_dir):
        # No changes detected, output nothing
        return 0

    # Compute new state
    new_state = compute_env_state(current_dir)

    # Load with inheritance
    new_vars, loaded_dirs = load_env_with_inheritance(current_dir)

    # Get previously loaded vars from environment variable
    old_keys_str = os.environ.get("_DIRDOTENV_KEYS", "")
    old_keys = set(old_keys_str.split(":")) if old_keys_str else set()

    # Build old vars dict from current environment
    old_vars = {key: os.environ.get(key, "") for key in old_keys if key in os.environ}

    output_lines = []

    # Determine what changed
    loaded_keys = get_loaded_keys(old_vars, new_vars)
    unloaded_keys = get_unloaded_keys(old_vars, new_vars)

    # Unset variables that should be removed
    if unloaded_keys:
        output_lines.append(format_unset_commands(unloaded_keys, shell))
        # Format unloaded keys with - prefix like direnv
        unloaded_msg = " ".join(f"-{key}" for key in sorted(unloaded_keys))
        output_lines.append(format_message(f"dirdotenv: {unloaded_msg}", shell))

    # Export new/changed variables
    if new_vars:
        output_lines.append(format_export_commands(new_vars, shell))

        # Store the keys we're managing
        all_keys = ":".join(sorted(new_vars.keys()))
        if shell in ["bash", "zsh"]:
            output_lines.append(f"export _DIRDOTENV_KEYS='{all_keys}'")
        elif shell == "fish":
            output_lines.append(f"set -gx _DIRDOTENV_KEYS '{all_keys}'")
        elif shell == "powershell":
            output_lines.append(f"$env:_DIRDOTENV_KEYS = '{all_keys}'")

        # Show what was loaded with + prefix like direnv
        if loaded_keys:
            loaded_msg = " ".join(f"+{key}" for key in sorted(loaded_keys))
            output_lines.append(format_message(f"dirdotenv: {loaded_msg}", shell))
    elif old_keys:
        # Clear the tracking variable if nothing is loaded anymore
        if shell in ["bash", "zsh"]:
            output_lines.append("unset _DIRDOTENV_KEYS")
        elif shell == "fish":
            output_lines.append("set -e _DIRDOTENV_KEYS")
        elif shell == "powershell":
            output_lines.append(
                "Remove-Item Env:_DIRDOTENV_KEYS -ErrorAction SilentlyContinue"
            )

    # Store the new state
    if shell in ["bash", "zsh"]:
        # Escape single quotes in the state string for shell
        escaped_state = new_state.replace("'", "'\\''")
        output_lines.append(f"export _DIRDOTENV_STATE='{escaped_state}'")
    elif shell == "fish":
        escaped_state = new_state.replace("'", "\\'")
        output_lines.append(f"set -gx _DIRDOTENV_STATE '{escaped_state}'")
    elif shell == "powershell":
        escaped_state = new_state.replace("'", "''")
        output_lines.append(f"$env:_DIRDOTENV_STATE = '{escaped_state}'")

    print("\n".join(output_lines))
    return 0


def main():
    """Main entry point for the dirdotenv CLI."""
    parser = argparse.ArgumentParser(
        description="Load environment variables from .env and .envrc files",
        prog="dirdotenv",
        epilog="""
Examples:
  # Show help
  dirdotenv
  
  # Export variables for current directory
  eval "$(dirdotenv --export)"
  
  # Execute command with loaded variables
  dirdotenv --exec python script.py
  
  # Setup shell integration (automatic loading on cd)
  eval "$(dirdotenv hook bash)"     # for bash
  eval "$(dirdotenv hook zsh)"      # for zsh
  dirdotenv hook fish | source      # for fish
  
For more information, see: https://github.com/alexeygrigorev/dirdotenv
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    # Check if first argument is a known subcommand
    if len(sys.argv) > 1 and sys.argv[1] in ["hook", "load"]:
        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Hook subcommand
        hook_parser = subparsers.add_parser(
            "hook",
            help="Output shell hook code for automatic environment loading",
            description="Generate shell integration code for automatic loading of environment variables when changing directories (like direnv).",
        )
        hook_parser.add_argument(
            "shell",
            choices=["bash", "zsh", "fish", "powershell"],
            help="Shell to generate hook for (bash, zsh, fish, or powershell)",
        )
        hook_parser.add_argument(
            "--cmd",
            default=None,
            help="Explicitly specify the dirdotenv command to use in the hook (overrides detection)",
        )

        # Load subcommand (used internally by hooks)
        load_parser = subparsers.add_parser(
            "load", help="Load environment with inheritance (used by hooks)"
        )
        load_parser.add_argument(
            "--shell",
            choices=["bash", "zsh", "fish", "powershell"],
            default="bash",
            help="Shell format for export commands",
        )

        args = parser.parse_args()

        # Handle hook command
        if args.command == "hook":
            cmd = args.cmd or get_invocation_command()
            print(get_hook(args.shell, cmd))
            return 0

        # Handle load command
        if args.command == "load":
            return load_command(args)

    # Add arguments for default behavior
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory containing .env or .envrc files (default: current directory)",
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Export environment variables (outputs shell commands)",
    )
    parser.add_argument(
        "--shell",
        choices=["bash", "zsh", "fish", "powershell"],
        default="bash",
        help="Shell format for export commands (default: bash)",
    )
    parser.add_argument(
        "--exec",
        dest="exec_command",
        nargs=argparse.REMAINDER,
        help="Execute command with loaded environment variables",
    )

    args = parser.parse_args()

    # If no --export and no --exec, show help
    if not args.export and not args.exec_command:
        parser.print_help()
        return 0

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

    # If --export is specified, output shell commands to source
    if args.export:
        print(format_export_commands(env_vars, args.shell))

    return 0


if __name__ == "__main__":
    sys.exit(main())
