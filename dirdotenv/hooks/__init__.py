"""Hook files for shell integration."""

from pathlib import Path


def get_hook(shell: str, cmd: str) -> str:
    """
    Get shell hook code for the specified shell.

    Args:
        shell: Shell type (bash, zsh, fish, powershell)
        cmd: Command to use for invoking dirdotenv (e.g. "dirdotenv", "uvx dirdotenv")

    Returns:
        String containing the hook code for the shell

    Raises:
        ValueError: If shell is not supported
    """
    # Map shell names to hook file names
    hook_files = {
        "bash": "bash.sh",
        "zsh": "zsh.sh",
        "fish": "fish.fish",
        "powershell": "powershell.ps1",
    }

    if shell not in hook_files:
        raise ValueError(
            f"Unsupported shell: {shell}. Supported shells: {', '.join(hook_files.keys())}"
        )

    # Get the path to the hooks directory (this file is in hooks/)
    hooks_dir = Path(__file__).parent
    hook_file = hooks_dir / hook_files[shell]

    # Read and return the hook content
    try:
        content = hook_file.read_text(encoding="utf-8")
        return content.replace("{{cmd}}", cmd)
    except FileNotFoundError:
        raise FileNotFoundError(f"Hook file not found: {hook_file}")


__all__ = ["get_hook"]
