_dirdotenv_load() {
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
