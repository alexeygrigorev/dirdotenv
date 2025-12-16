function _dirdotenv_load --on-variable PWD
    # Call dirdotenv load - it handles state tracking internally
    set -l cmd "{{cmd}}"
    
    # We execute the command directly to support complex commands like "uvx dirdotenv"
    set -l output (eval $cmd load --shell fish 2>&1)
    if test $status -eq 0
        eval (string join "; " $output)
    end
end

_dirdotenv_load
