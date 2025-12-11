function _dirdotenv_load --on-variable PWD
    # Track directory changes
    if test "$_dirdotenv_last_dir" != "$PWD"
        set -g _dirdotenv_last_dir $PWD
        
        if command -v dirdotenv > /dev/null 2>&1
            set -l output (dirdotenv load --shell fish 2>&1)
            if test $status -eq 0
                eval (string join "; " $output)
            end
        end
    end
end

_dirdotenv_load
