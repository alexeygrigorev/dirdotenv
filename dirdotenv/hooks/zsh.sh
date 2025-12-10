_dirdotenv_load() {
    # Track directory changes
    if [[ "$_dirdotenv_last_dir" != "$PWD" ]]; then
        _dirdotenv_last_dir="$PWD"
        
        # Check if we have env files or need to clean up
        if command -v dirdotenv &> /dev/null; then
            local output
            if output=$(dirdotenv load --shell zsh 2>&1); then
                eval "$output"
            fi
        fi
    fi
}

autoload -U add-zsh-hook
add-zsh-hook chpwd _dirdotenv_load
_dirdotenv_load
