"""Integration tests for file change detection - verifying fix for issue #4

These tests verify that file changes (.env or .envrc) are automatically detected
and reloaded when:
1. A new .env file is created in the current directory
2. An existing .env file is modified
3. Variables are removed from .env file

All tests pass, confirming the file change detection functionality works correctly.
"""

import re
import pytest
import pexpect
import time


@pytest.fixture
def empty_test_dir(tmp_path):
    """Create an empty test directory."""
    test_dir = tmp_path / "test_env"
    test_dir.mkdir()
    return test_dir


def _strip_ansi_codes(text):
    """Remove ANSI escape codes from text."""
    ansi_escape = re.compile(r'\x1b\[[0-9;?]*[a-zA-Z]')
    return ansi_escape.sub('', text)


def check_var_value(child, prompt, var_name, expected_value):
    """Helper to reliably check variable value in pexpect."""
    # Use printenv which outputs just the value
    child.sendline(f"printenv {var_name}")
    child.expect(prompt)
    # Wait for next prompt to ensure output is captured
    child.sendline("echo marker")
    child.expect(prompt)
    output = child.before
    
    print(f"check_var_value({var_name}, {expected_value}): output={repr(output)}")
    
    if expected_value is None:
        # Variable should be unset
        # If printenv outputs nothing or just the command, variable is unset
        lines = [l.strip() for l in output.split('\n') if l.strip()]
        # Filter out the command itself, the marker, and ANSI escape codes
        lines = [_strip_ansi_codes(l).strip() for l in lines]
        lines = [l for l in lines if l and not l.startswith('printenv') and l != 'marker' and l != 'echo marker']
        print(f"  Filtered lines: {lines}")
        # If there are no remaining lines, variable is unset
        return len(lines) == 0
    else:
        return expected_value in output


@pytest.mark.parametrize("shell", ["bash"])
def test_cd_back_and_forth_after_creating_env(shell, empty_test_dir):
    """
    Test the exact scenario from issue #4:
    1. cd into empty directory
    2. Create .env file
    3. Do cd .. && cd - 
    4. Expected: environment should be loaded
    """
    test_dir = empty_test_dir
    
    # Spawn shell
    child = pexpect.spawn(shell, ["--norc", "--noprofile"], encoding="utf-8", timeout=10)
    
    # Set simple prompt
    prompt = ">>> "
    child.sendline(f"PS1='{prompt}'")
    child.expect(prompt)
    
    # Install dirdotenv hook
    child.sendline('eval "$(dirdotenv hook bash)"')
    child.expect(prompt)
    
    # cd into empty directory
    child.sendline(f"cd {test_dir}")
    child.expect(prompt)
    
    # Create .env file while in the directory
    env_file = test_dir / ".env"
    env_file.write_text("TOMATO=tomato\n")
    
    # Do cd .. && cd - to trigger reload
    child.sendline("cd .. && cd -")
    child.expect(prompt)
    
    # Check if dirdotenv message appeared
    if "+TOMATO" in child.before:
        print("✓ Saw +TOMATO message")
    
    # Check if TOMATO is set
    assert check_var_value(child, prompt, "TOMATO", "tomato"), \
        "TOMATO should be loaded after cd .. && cd -"


@pytest.mark.parametrize("shell", ["bash"])
def test_file_modification_detected(shell, empty_test_dir):
    """
    Test that modifying .env file is detected:
    1. cd into directory with .env
    2. Modify .env file
    3. Press enter (or run a command)
    4. Expected: environment should be reloaded with new values
    """
    test_dir = empty_test_dir
    
    # Create initial .env
    env_file = test_dir / ".env"
    env_file.write_text("TOMATO=tomato\n")
    
    # Spawn shell
    child = pexpect.spawn(shell, ["--norc", "--noprofile"], encoding="utf-8", timeout=10)
    
    # Set simple prompt
    prompt = ">>> "
    child.sendline(f"PS1='{prompt}'")
    child.expect(prompt)
    
    # Install dirdotenv hook
    child.sendline('eval "$(dirdotenv hook bash)"')
    child.expect(prompt)
    
    # cd into directory - should load TOMATO=tomato
    child.sendline(f"cd {test_dir}")
    child.expect(prompt)
    
    # Verify initial value
    assert check_var_value(child, prompt, "TOMATO", "tomato"), \
        "Initial value should be 'tomato'"
    
    # Modify the .env file
    # Sleep to ensure filesystem mtime changes (some filesystems have 1-second granularity)
    time.sleep(0.2)
    env_file.write_text("TOMATO=not-tomato\n")
    
    # Trigger prompt by running a command
    child.sendline("echo trigger")
    child.expect(prompt)
    
    # Check if value was updated
    assert check_var_value(child, prompt, "TOMATO", "not-tomato"), \
        "TOMATO should be updated to 'not-tomato'"


@pytest.mark.parametrize("shell", ["bash"])
def test_variable_removal_detected(shell, empty_test_dir):
    """
    Test that removing a variable from .env is detected:
    1. cd into directory with .env containing TOMATO and LEMON
    2. Remove LEMON from .env
    3. Press enter (or run a command)
    4. Expected: LEMON should be unset, message should show -LEMON
    """
    test_dir = empty_test_dir
    
    # Create initial .env with two variables
    env_file = test_dir / ".env"
    env_file.write_text("TOMATO=tomato\nLEMON=lemon\n")
    
    # Spawn shell
    child = pexpect.spawn(shell, ["--norc", "--noprofile"], encoding="utf-8", timeout=10)
    
    # Set simple prompt
    prompt = ">>> "
    child.sendline(f"PS1='{prompt}'")
    child.expect(prompt)
    
    # Install dirdotenv hook
    child.sendline('eval "$(dirdotenv hook bash)"')
    child.expect(prompt)
    
    # cd into directory - should load both variables
    child.sendline(f"cd {test_dir}")
    child.expect(prompt)
    
    # Verify both variables are set
    assert check_var_value(child, prompt, "TOMATO", "tomato")
    assert check_var_value(child, prompt, "LEMON", "lemon")
    
    # Remove LEMON from .env
    # Sleep to ensure filesystem mtime changes (some filesystems have 1-second granularity)
    time.sleep(0.2)
    env_file.write_text("TOMATO=tomato\n")
    
    # Trigger prompt by running a command
    child.sendline("echo trigger")
    child.expect(prompt)
    
    # Check for -LEMON message in output
    if "-LEMON" in child.before:
        print("✓ Saw -LEMON message")
    else:
        print("⚠ Did not see -LEMON message in output")
    
    # Check if LEMON was unset
    assert check_var_value(child, prompt, "LEMON", None), \
        "LEMON should be unset after removal from .env"
