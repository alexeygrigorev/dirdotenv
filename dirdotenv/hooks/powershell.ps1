function global:_dirdotenv_load {
    # Call dirdotenv load - it handles state tracking internally
    $cmd = "{{cmd}}"
    # Execute the command. Note: if cmd is complex, proper parsing might be needed, 
    # but generic invocation of string in expression works for simple cases.
    # For "uvx dirdotenv load ...", it needs to be executed as a command.
    
    # Using Invoke-Expression for the command execution to handle space-separated arguments in cmd
    $output = (Invoke-Expression "$cmd load --shell powershell 2>&1") -join "`n"
    if ($LASTEXITCODE -eq 0 -and $output) {
        Invoke-Expression $output
    }
}

# Store original prompt function if it exists
if (Test-Path function:prompt) {
    $global:_dirdotenv_prompt_old = Get-Content function:prompt
}

function global:prompt {
    _dirdotenv_load
    if ($global:_dirdotenv_prompt_old) {
        Invoke-Command -ScriptBlock ([ScriptBlock]::Create($global:_dirdotenv_prompt_old))
    }
    else {
        "PS $($executionContext.SessionState.Path.CurrentLocation)$('>' * ($nestedPromptLevel + 1)) "
    }
}
