function _dirdotenv_load --on-variable PWD
    # Get current directory and file state
    set -l current_dir "$PWD"
    set -l env_state ""
    
    # Build a string representing the state of .env and .envrc files
    # We traverse from root to current directory to match the loader's behavior
    set -l path "$current_dir"
    set -l check_paths
    
    # Collect all parent directories up to root
    while true
        set check_paths $path $check_paths
        set -l parent (dirname "$path")
        if test "$parent" = "$path"
            break
        end
        set path $parent
    end
    
    # Check each directory for .env or .envrc files
    for dir in $check_paths
        if test -f "$dir/.env"
            set -l mtime (stat -c %Y "$dir/.env" 2>/dev/null; or stat -f %m "$dir/.env" 2>/dev/null)
            set env_state "$env_state$dir/.env:$mtime;"
        end
        if test -f "$dir/.envrc"
            set -l mtime (stat -c %Y "$dir/.envrc" 2>/dev/null; or stat -f %m "$dir/.envrc" 2>/dev/null)
            set env_state "$env_state$dir/.envrc:$mtime;"
        end
    end
    
    # Check if directory or env files changed
    if test "$_dirdotenv_last_dir" != "$current_dir"; or test "$_dirdotenv_last_state" != "$env_state"
        set -g _dirdotenv_last_dir $current_dir
        set -g _dirdotenv_last_state $env_state
        
        if command -v dirdotenv > /dev/null 2>&1
            set -l output (dirdotenv load --shell fish 2>&1)
            if test $status -eq 0
                eval (string join "; " $output)
            end
        end
    end
end

_dirdotenv_load
