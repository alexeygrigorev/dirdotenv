#!/usr/bin/env fish
# dirdotenv shell integration for fish
# Add this to your ~/.config/fish/config.fish:
#   source /path/to/dirdotenv/shell_integration/dirdotenv.fish

# Function to load environment variables from .env or .envrc
function _dirdotenv_load --on-variable PWD
    # Check if .env or .envrc exists in current directory
    if test -f ".env" -o -f ".envrc"
        # Check if dirdotenv command is available
        if command -v dirdotenv > /dev/null 2>&1
            # Load the environment variables
            eval (dirdotenv --shell fish)
        end
    end
end

# Load on shell startup
_dirdotenv_load
