import pytest
import pexpect
import os
import sys


# Test fixture to create a temporary directory with .envrc
@pytest.fixture
def test_env(tmp_path):
    env_dir = tmp_path / "test_project"
    env_dir.mkdir()

    env_file = env_dir / ".envrc"
    env_file.write_text("export TEST_VAR='hello_world'")

    return env_dir


def run_shell_test(shell_cmd, test_env_path):
    """Run a test session in the specified shell."""

    # Spawn the shell
    child = pexpect.spawn(shell_cmd, encoding="utf-8")

    # Set a simple prompt to make matching easier
    p1 = "DIRENV_TEST_"
    p2 = "PROMPT> "
    prompt = p1 + p2

    # Clear existing prompt command and set prompt
    # We use variables to avoid the full prompt string appearing in the command echo
    if "bash" in shell_cmd:
        child.sendline("unset PROMPT_COMMAND")
        child.sendline(f"P1='{p1}'; P2='{p2}'; PS1=\"$P1$P2\"")
    elif "zsh" in shell_cmd:
        child.sendline("precmd() { }")  # Clear precmd
        child.sendline(f"P1='{p1}'; P2='{p2}'; PS1=\"$P1$P2\"")
    elif "fish" in shell_cmd:
        child.sendline(
            f"set P1 '{p1}'; set P2 '{p2}'; function fish_prompt; echo \"$P1$P2\"; end"
        )

    child.expect(prompt)

    # Source the hook
    if "fish" in shell_cmd:
        child.sendline("dirdotenv hook fish | source")
    elif "bash" in shell_cmd:
        child.sendline('eval "$(dirdotenv hook bash)"')
    elif "zsh" in shell_cmd:
        child.sendline('eval "$(dirdotenv hook zsh)"')

    child.expect(prompt)

    # Verify variable is NOT set initially
    child.sendline("echo $TEST_VAR")
    child.expect(prompt)
    if "hello_world" in child.before:
        print(f"Variable already set in {shell_cmd}. Output: {child.before}")
        return False

    # cd into the directory
    child.sendline(f"cd {test_env_path}")
    child.expect(prompt)

    # Check if variable is set
    child.sendline("echo $TEST_VAR")
    child.expect(prompt)

    if "hello_world" not in child.before:
        print(f"Failed to load variable in {shell_cmd}. Output: {child.before}")
        return False

    # cd out
    child.sendline("cd ..")
    child.expect(prompt)

    # Check if variable is unset
    child.sendline("echo $TEST_VAR")
    child.expect(prompt)
    if "hello_world" in child.before:
        print(f"Failed to unload variable in {shell_cmd}. Output: {child.before}")
        return False

    return True


@pytest.mark.parametrize("shell", ["bash", "zsh", "fish"])
def test_shell_integration(shell, test_env):
    """Test dirdotenv integration in different shells."""
    assert run_shell_test(shell, test_env)
