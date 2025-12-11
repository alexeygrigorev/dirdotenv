function global:_dirdotenv_load {
    $currentDir = Get-Location
    $envState = ""
    
    # Build a string representing the state of .env and .envrc files
    # We traverse from root to current directory to match the loader's behavior
    $path = $currentDir.Path
    $checkPaths = @()
    
    # Collect all parent directories up to root
    while ($true) {
        $checkPaths = @($path) + $checkPaths
        $parent = Split-Path -Parent $path
        if ([string]::IsNullOrEmpty($parent) -or $parent -eq $path) {
            break
        }
        $path = $parent
    }
    
    # Check each directory for .env or .envrc files
    foreach ($dir in $checkPaths) {
        $envFile = Join-Path $dir ".env"
        if (Test-Path $envFile) {
            $mtime = (Get-Item $envFile).LastWriteTime.ToFileTime()
            $envState += "$envFile`:$mtime;"
        }
        $envrcFile = Join-Path $dir ".envrc"
        if (Test-Path $envrcFile) {
            $mtime = (Get-Item $envrcFile).LastWriteTime.ToFileTime()
            $envState += "$envrcFile`:$mtime;"
        }
    }
    
    # Check if directory or env files changed
    if ($global:_dirdotenv_last_dir -ne $currentDir.Path -or $global:_dirdotenv_last_state -ne $envState) {
        $global:_dirdotenv_last_dir = $currentDir.Path
        $global:_dirdotenv_last_state = $envState
        
        if (Get-Command dirdotenv -ErrorAction SilentlyContinue) {
            $output = (dirdotenv load --shell powershell 2>&1) -join "`n"
            if ($LASTEXITCODE -eq 0 -and $output) {
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
    }
    else {
        "PS $($executionContext.SessionState.Path.CurrentLocation)$('>' * ($nestedPromptLevel + 1)) "
    }
}
