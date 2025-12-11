"""
PowerShell integration tests for dirdotenv.

These tests mirror the bash/zsh/fish tests but run on Windows natively.
They test the hook + cd workflow using PowerShell.

Run with: pytest tests_integration/test_powershell.py -v
"""

import pytest
import subprocess
import sys
import shutil


def get_pwsh_path():
    """Find PowerShell Core executable."""
    pwsh = shutil.which("pwsh")
    if pwsh:
        return pwsh
    # Fallback to Windows PowerShell
    powershell = shutil.which("powershell")
    if powershell:
        return powershell
    return None


PWSH = get_pwsh_path()


def run_pwsh_script(script: str) -> subprocess.CompletedProcess:
    """Run a PowerShell script and return the result."""
    if not PWSH:
        pytest.skip("PowerShell not found")
    return subprocess.run(
        [PWSH, "-NoProfile", "-Command", script],
        capture_output=True,
        text=True,
        timeout=30,
    )


# ============== Fixtures ==============


@pytest.fixture
def test_env(tmp_path):
    """Basic test environment with single .envrc"""
    env_dir = tmp_path / "test_project"
    env_dir.mkdir()
    (env_dir / ".envrc").write_text("export TEST_VAR='hello_world'")
    return env_dir


@pytest.fixture
def nested_test_env(tmp_path):
    """Nested directories with parent/child .envrc files"""
    root_dir = tmp_path / "nested_project"
    root_dir.mkdir()
    (root_dir / ".envrc").write_text(
        "export ROOT_VAR='root_value'\nexport SHARED_VAR='root_shared'"
    )

    child_dir = root_dir / "child"
    child_dir.mkdir()
    (child_dir / ".envrc").write_text(
        "export CHILD_VAR='child_value'\nexport SHARED_VAR='child_shared'"
    )

    return root_dir, child_dir


@pytest.fixture
def dot_env_test_env(tmp_path):
    """Test environment with .env file instead of .envrc"""
    env_dir = tmp_path / "dotenv_project"
    env_dir.mkdir()
    (env_dir / ".env").write_text("DOTENV_VAR='dotenv_value'")
    return env_dir


# ============== Tests ==============


@pytest.mark.skipif(sys.platform != "win32", reason="Windows-only test")
def test_powershell_hook_output():
    """Test that dirdotenv hook powershell produces valid output."""
    result = subprocess.run(
        ["dirdotenv", "hook", "powershell"], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "_dirdotenv_load" in result.stdout
    assert "prompt" in result.stdout.lower()


@pytest.mark.skipif(sys.platform != "win32", reason="Windows-only test")
def test_powershell_load_command(test_env):
    """Test basic variable loading with dirdotenv load."""
    result = subprocess.run(
        ["dirdotenv", "load", "--shell", "powershell"],
        capture_output=True,
        text=True,
        cwd=str(test_env),
    )
    assert result.returncode == 0
    assert "TEST_VAR" in result.stdout
    assert "hello_world" in result.stdout


@pytest.mark.skipif(sys.platform != "win32", reason="Windows-only test")
def test_powershell_hook_and_cd(test_env):
    """Test hook integration with cd - variable should be set after cd."""
    script = f"""
        Invoke-Expression ((dirdotenv hook powershell) -join "`n")
        $before = $env:TEST_VAR
        Set-Location '{test_env}'
        _dirdotenv_load
        $after = $env:TEST_VAR
        Write-Output "BEFORE:$before"
        Write-Output "AFTER:$after"
    """
    result = run_pwsh_script(script)
    assert result.returncode == 0, f"stderr: {result.stderr}"
    assert "AFTER:hello_world" in result.stdout


@pytest.mark.skipif(sys.platform != "win32", reason="Windows-only test")
def test_powershell_hook_cd_out(test_env):
    """Test that variable is unset after cd out of directory."""
    parent = test_env.parent
    script = f"""
        Invoke-Expression ((dirdotenv hook powershell) -join "`n")
        Set-Location '{test_env}'
        _dirdotenv_load
        $inside = $env:TEST_VAR
        Set-Location '{parent}'
        _dirdotenv_load
        $outside = $env:TEST_VAR
        Write-Output "INSIDE:$inside"
        Write-Output "OUTSIDE:$outside"
    """
    result = run_pwsh_script(script)
    assert result.returncode == 0, f"stderr: {result.stderr}"
    assert "INSIDE:hello_world" in result.stdout
    lines = result.stdout.strip().split("\n")
    outside_line = [line for line in lines if line.startswith("OUTSIDE:")][0]
    assert outside_line == "OUTSIDE:" or "hello_world" not in outside_line


@pytest.mark.skipif(sys.platform != "win32", reason="Windows-only test")
def test_powershell_nested_inheritance(nested_test_env):
    """Test nested directory inheritance and override."""
    root_dir, child_dir = nested_test_env
    script = f"""
        Invoke-Expression ((dirdotenv hook powershell) -join "`n")
        Set-Location '{root_dir}'
        _dirdotenv_load
        $root_var_in_root = $env:ROOT_VAR
        $shared_in_root = $env:SHARED_VAR
        Set-Location '{child_dir}'
        _dirdotenv_load
        $root_var_in_child = $env:ROOT_VAR
        $child_var = $env:CHILD_VAR
        $shared_in_child = $env:SHARED_VAR
        Write-Output "ROOT_IN_ROOT:$root_var_in_root"
        Write-Output "SHARED_IN_ROOT:$shared_in_root"
        Write-Output "ROOT_IN_CHILD:$root_var_in_child"
        Write-Output "CHILD_VAR:$child_var"
        Write-Output "SHARED_IN_CHILD:$shared_in_child"
    """
    result = run_pwsh_script(script)
    assert result.returncode == 0, f"stderr: {result.stderr}"
    assert "ROOT_IN_ROOT:root_value" in result.stdout
    assert "SHARED_IN_ROOT:root_shared" in result.stdout
    assert "ROOT_IN_CHILD:root_value" in result.stdout
    assert "CHILD_VAR:child_value" in result.stdout
    assert "SHARED_IN_CHILD:child_shared" in result.stdout


@pytest.mark.skipif(sys.platform != "win32", reason="Windows-only test")
def test_powershell_dot_env_file(dot_env_test_env):
    """Test .env file loading."""
    result = subprocess.run(
        ["dirdotenv", "load", "--shell", "powershell"],
        capture_output=True,
        text=True,
        cwd=str(dot_env_test_env),
    )
    assert result.returncode == 0
    assert "DOTENV_VAR" in result.stdout
    assert "dotenv_value" in result.stdout


# ============== Interactive Tests (emulating real user behavior) ==============


@pytest.mark.skipif(sys.platform != "win32", reason="Windows-only test")
def test_powershell_interactive_cd(test_env):
    """Test real interactive behavior with pexpect - emulates user typing commands."""
    from pexpect import popen_spawn

    # Spawn interactive PowerShell
    child = popen_spawn.PopenSpawn(
        f"{PWSH} -NoProfile -NoLogo", encoding="utf-8", timeout=30
    )

    # Wait for prompt
    child.expect(r"PS .*>")

    # Source the hook
    child.sendline('Invoke-Expression ((dirdotenv hook powershell) -join "`n")')
    child.expect(r"PS .*>")

    # Check variable not set initially
    child.sendline('Write-Output "VAR:$env:TEST_VAR"')
    child.expect(r"PS .*>")
    assert "VAR:hello_world" not in child.before

    # cd into directory (prompt will trigger hook)
    child.sendline(f"cd '{test_env}'")
    child.expect(r"PS .*>")

    # Check variable is now set
    child.sendline('Write-Output "VAR:$env:TEST_VAR"')
    child.expect(r"PS .*>")
    assert "VAR:hello_world" in child.before

    # cd out
    child.sendline("cd ..")
    child.expect(r"PS .*>")

    # Check variable is unset
    child.sendline('Write-Output "VAR:$env:TEST_VAR"')
    child.expect(r"PS .*>")
    assert "VAR:hello_world" not in child.before

    child.sendline("exit")
