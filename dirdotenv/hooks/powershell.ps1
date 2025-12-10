function global:_dirdotenv_load {
    $currentDir = Get-Location
    
    # Track directory changes
    if ($global:_dirdotenv_last_dir -ne $currentDir.Path) {
        $global:_dirdotenv_last_dir = $currentDir.Path
        
        if (Get-Command dirdotenv -ErrorAction SilentlyContinue) {
            $output = dirdotenv load --shell powershell 2>&1
            if ($LASTEXITCODE -eq 0) {
                Invoke-Expression $output
            }
        }
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
    } else {
        "PS $($executionContext.SessionState.Path.CurrentLocation)$('>' * ($nestedPromptLevel + 1)) "
    }
}
