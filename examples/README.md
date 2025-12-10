# dirdotenv Examples

This directory contains example files showing how to use dirdotenv.

## Files

- `.env.example` - Example .env file format
- `.envrc.example` - Example .envrc file format
- `demo.py` - Python script demonstrating environment variable usage

## Usage

1. Copy the example file you want to use:
   ```bash
   cp examples/.env.example .env
   # or
   cp examples/.envrc.example .envrc
   ```

2. Load the environment variables:
   ```bash
   # Print export commands
   dirdotenv
   
   # Load into current shell
   eval "$(dirdotenv)"
   
   # Execute a command with the environment
   dirdotenv --exec python examples/demo.py
   ```
