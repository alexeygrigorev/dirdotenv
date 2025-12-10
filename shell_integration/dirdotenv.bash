#!/bin/bash
# dirdotenv shell integration for bash
# Add this to your ~/.bashrc:
#   source /path/to/dirdotenv/shell_integration/dirdotenv.bash

# Store the original PROMPT_COMMAND
_dirdotenv_original_prompt_command="$PROMPT_COMMAND"

# Function to load environment variables from .env or .envrc
_dirdotenv_load() {
    # Check if we're in a different directory
    if [[ "$_dirdotenv_last_dir" != "$PWD" ]]; then
        _dirdotenv_last_dir="$PWD"
        
        # Check if .env or .envrc exists in current directory
        if [[ -f ".env" ]] || [[ -f ".envrc" ]]; then
            # Check if dirdotenv command is available
            if command -v dirdotenv &> /dev/null; then
                # Load the environment variables
                eval "$(dirdotenv)"
            fi
        fi
    fi
}

# Add our function to PROMPT_COMMAND
if [[ -z "$PROMPT_COMMAND" ]]; then
    PROMPT_COMMAND="_dirdotenv_load"
else
    PROMPT_COMMAND="${PROMPT_COMMAND};_dirdotenv_load"
fi
