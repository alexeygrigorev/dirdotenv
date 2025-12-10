#!/bin/zsh
# dirdotenv shell integration for zsh
# Add this to your ~/.zshrc:
#   source /path/to/dirdotenv/shell_integration/dirdotenv.zsh

# Function to load environment variables from .env or .envrc
_dirdotenv_load() {
    # Check if we're in a different directory
    if [[ "$_dirdotenv_last_dir" != "$PWD" ]]; then
        _dirdotenv_last_dir="$PWD"
        
        # Check if .env or .envrc exists in current directory
        if [[ -f ".env" ]] || [[ -f ".envrc" ]]; then
            # Check if dirdotenv command is available
            if command -v dirdotenv &> /dev/null; then
                # Load the environment variables with error handling
                local output
                if output=$(dirdotenv 2>&1); then
                    eval "$output"
                fi
            fi
        fi
    fi
}

# Use chpwd hook to detect directory changes
autoload -U add-zsh-hook
add-zsh-hook chpwd _dirdotenv_load

# Load on shell startup
_dirdotenv_load
