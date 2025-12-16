_dirdotenv_load() {
    # Call dirdotenv load - it handles state tracking internally
    local cmd="{{cmd}}"

    local output
    if output=$($cmd load --shell zsh 2>&1); then
        eval "$output"
    fi
}

autoload -U add-zsh-hook
add-zsh-hook precmd _dirdotenv_load
_dirdotenv_load
