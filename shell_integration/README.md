# Shell Integration

This directory contains shell integration scripts for automatically loading environment variables when you enter a directory with `.env` or `.envrc` files.

## Installation

### Bash

Add to your `~/.bashrc`:

```bash
source /path/to/dirdotenv/shell_integration/dirdotenv.bash
```

### Zsh

Add to your `~/.zshrc`:

```zsh
source /path/to/dirdotenv/shell_integration/dirdotenv.zsh
```

### Fish

Add to your `~/.config/fish/config.fish`:

```fish
source /path/to/dirdotenv/shell_integration/dirdotenv.fish
```

## How It Works

The shell integration scripts automatically detect when you change directories. When you enter a directory containing `.env` or `.envrc` files, the environment variables are automatically loaded into your shell session.

This provides a similar experience to `direnv`, where environment variables are automatically managed based on your current directory.

## Usage

Once installed, simply navigate to a directory with `.env` or `.envrc` files:

```bash
cd /path/to/project
# Environment variables are automatically loaded
echo $OPENAI_API_KEY  # Should display the value from .env or .envrc
```

When you leave the directory, the environment variables remain set in your current shell session. If you want fresh environment for each directory, you can open a new shell session or manually unset variables.

## Notes

- The integration requires the `dirdotenv` command to be available in your PATH
- Variables are loaded when entering a directory, not when files change
- If both `.env` and `.envrc` exist, variables from `.env` take precedence
