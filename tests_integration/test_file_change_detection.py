"""Integration tests for file change detection - reproducing issue #4"""

import pytest
import pexpect
import time


@pytest.fixture
def empty_test_dir(tmp_path):
    """Create an empty test directory."""
    test_dir = tmp_path / "test_env"
    test_dir.mkdir()
    return test_dir


@pytest.mark.parametrize("shell", ["bash"])
def test_cd_back_and_forth_after_creating_env(shell, empty_test_dir):
    """
    Test the exact scenario from issue #4:
    1. cd into empty directory
    2. Create .env file
    3. Do cd .. && cd - 
    4. Expected: environment should be loaded
    
    This test currently FAILS - documenting the bug.
    """
    test_dir = empty_test_dir
    
    # Spawn shell
    child = pexpect.spawn(shell, encoding="utf-8", timeout=10)
    
    # Set simple prompt
    prompt = "TEST_PROMPT> "
    child.sendline(f"PS1='{prompt}'")
    child.sendline("unset PROMPT_COMMAND")  # Clear any existing prompt command
    child.expect(prompt)
    
    # Install dirdotenv hook
    child.sendline('eval "$(dirdotenv hook bash)"')
    child.expect(prompt)
    
    # Verify PROMPT_COMMAND was set
    child.sendline("echo PROMPT_COMMAND=$PROMPT_COMMAND")
    child.expect(prompt)
    print(f"PROMPT_COMMAND: {child.before}")
    
    # cd into empty directory
    child.sendline(f"cd {test_dir}")
    child.expect(prompt)
    
    # Create .env file while in the directory
    env_file = test_dir / ".env"
    env_file.write_text("TOMATO=tomato\n")
    
    # Do cd .. && cd - to try to trigger reload
    child.sendline("cd .. && cd -")
    child.expect(prompt)
    output_after_cd = child.before
    print(f"After cd .. && cd -: {repr(output_after_cd)}")
    
    # Check if TOMATO is set
    child.sendline("echo START:$TOMATO:END")
    idx = child.expect([prompt, pexpect.TIMEOUT], timeout=5)
    
    output = child.before
    print(f"Echo output (expect index={idx}): {repr(output)}")
    print(f"Echo output (after): {repr(child.after)}")
    
    # This is what we EXPECT - the variable should be loaded after returning to the directory
    # Look for START:tomato:END in the output
    if "START:tomato:END" not in output:
        print("TEST FAILED: TOMATO was not loaded")
        # Also check if it's START::END (empty variable)
        if "START::END" in output:
            print("Variable is empty!")
        print(f"Full buffer: {child.buffer}")
        pytest.fail(f"TOMATO should be loaded after cd .. && cd -. Echo output shows: {output}")


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
    child = pexpect.spawn(shell, encoding="utf-8", timeout=10)
    
    # Set simple prompt
    prompt = "TEST_PROMPT> "
    child.sendline(f"PS1='{prompt}'")
    child.sendline("unset PROMPT_COMMAND")
    child.expect(prompt)
    
    # Install dirdotenv hook
    child.sendline('eval "$(dirdotenv hook bash)"')
    child.expect(prompt)
    
    # cd into directory - should load TOMATO=tomato
    child.sendline(f"cd {test_dir}")
    child.expect(prompt)
    
    # Verify initial value
    child.sendline("echo TOMATO=$TOMATO")
    child.expect(prompt)
    assert "TOMATO=tomato" in child.before
    
    # Modify the .env file
    time.sleep(0.2)  # Ensure mtime changes
    env_file.write_text("TOMATO=not-tomato\n")
    
    # Trigger prompt by running a command
    child.sendline("echo 'trigger'")
    child.expect(prompt)
    
    # Check if value was updated
    child.sendline("echo TOMATO=$TOMATO")
    child.expect(prompt)
    
    output = child.before
    print(f"After modification: {output}")
    
    # This is what we EXPECT but currently FAILS
    if "TOMATO=not-tomato" not in output:
        pytest.fail(f"TOMATO should be updated after modification. Output: {output}")


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
    child = pexpect.spawn(shell, encoding="utf-8", timeout=10)
    
    # Set simple prompt
    prompt = "TEST_PROMPT> "
    child.sendline(f"PS1='{prompt}'")
    child.sendline("unset PROMPT_COMMAND")
    child.expect(prompt)
    
    # Install dirdotenv hook
    child.sendline('eval "$(dirdotenv hook bash)"')
    child.expect(prompt)
    
    # cd into directory - should load both variables
    child.sendline(f"cd {test_dir}")
    child.expect(prompt)
    
    # Verify both variables are set
    child.sendline("echo TOMATO=$TOMATO LEMON=$LEMON")
    child.expect(prompt)
    assert "TOMATO=tomato" in child.before
    assert "LEMON=lemon" in child.before
    
    # Remove LEMON from .env
    time.sleep(0.2)  # Ensure mtime changes
    env_file.write_text("TOMATO=tomato\n")
    
    # Trigger prompt by running a command
    child.sendline("echo 'trigger'")
    child.expect(prompt)
    
    # Check if LEMON was unset
    child.sendline("echo TOMATO=$TOMATO LEMON=$LEMON")
    child.expect(prompt)
    
    output = child.before
    print(f"After removing LEMON: {output}")
    
    # LEMON should be empty now
    if "LEMON=lemon" in output:
        pytest.fail(f"LEMON should be unset after removal. Output: {output}")
    
    # Should also see the -LEMON message in the output somewhere
    # Note: This might be in child.before from the previous expect
