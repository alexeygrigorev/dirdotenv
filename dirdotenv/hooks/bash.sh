_dirdotenv_load() {
    # Get current directory and file state
    local current_dir="$PWD"
    local env_state=""
    
    # Build a string representing the state of .env and .envrc files
    # We traverse from root to current directory to match the loader's behavior
    local path="$current_dir"
    local check_paths=()
    
    # Collect all parent directories up to root
    while true; do
        check_paths=("$path" "${check_paths[@]}")
        local parent=$(dirname "$path")
        if [[ "$parent" == "$path" ]]; then
            break
        fi
        path="$parent"
    done
    
    # Check each directory for .env or .envrc files
    for dir in "${check_paths[@]}"; do
        if [[ -f "$dir/.env" ]]; then
            env_state="${env_state}${dir}/.env:$(stat -c %Y "$dir/.env" 2>/dev/null || stat -f %m "$dir/.env" 2>/dev/null);"
        fi
        if [[ -f "$dir/.envrc" ]]; then
            env_state="${env_state}${dir}/.envrc:$(stat -c %Y "$dir/.envrc" 2>/dev/null || stat -f %m "$dir/.envrc" 2>/dev/null);"
        fi
    done
    
    # Check if directory or env files changed
    if [[ "$_dirdotenv_last_dir" != "$current_dir" ]] || [[ "$_dirdotenv_last_state" != "$env_state" ]]; then
        _dirdotenv_last_dir="$current_dir"
        _dirdotenv_last_state="$env_state"
        
        # Load environment with dirdotenv
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
