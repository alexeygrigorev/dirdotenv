function _dirdotenv_load --on-variable PWD
    # Call dirdotenv load - it handles state tracking internally
    if command -v dirdotenv > /dev/null 2>&1
        set -l output (dirdotenv load --shell fish 2>&1)
        if test $status -eq 0
            eval (string join "; " $output)
        end
    end
end

_dirdotenv_load
