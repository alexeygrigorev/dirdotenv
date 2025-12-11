_dirdotenv_load() {
    # Call dirdotenv load - it handles state tracking internally
    if command -v dirdotenv &> /dev/null; then
        local output
        if output=$(dirdotenv load --shell bash 2>&1); then
            eval "$output"
        fi
    fi
}

if [[ -z "$PROMPT_COMMAND" ]]; then
    PROMPT_COMMAND="_dirdotenv_load"
else
    PROMPT_COMMAND="${PROMPT_COMMAND};_dirdotenv_load"
fi
