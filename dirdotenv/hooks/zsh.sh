_dirdotenv_load() {
    # Call dirdotenv load - it handles state tracking internally
    if command -v dirdotenv &> /dev/null; then
        local output
        if output=$(dirdotenv load --shell zsh 2>&1); then
            eval "$output"
        fi
    fi
}

autoload -U add-zsh-hook
add-zsh-hook chpwd _dirdotenv_load
_dirdotenv_load
