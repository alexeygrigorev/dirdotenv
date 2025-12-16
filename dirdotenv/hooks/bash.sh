_dirdotenv_load() {
    # Call dirdotenv load - it handles state tracking internally
    # We use the captured command (e.g. 'dirdotenv', 'uvx dirdotenv', '/path/to/dirdotenv')
    local cmd="{{cmd}}"

    local output
    if output=$($cmd load --shell bash 2>&1); then
        eval "$output"
    fi
}

if [[ -z "$PROMPT_COMMAND" ]]; then
    PROMPT_COMMAND="_dirdotenv_load"
else
    PROMPT_COMMAND="${PROMPT_COMMAND};_dirdotenv_load"
fi
