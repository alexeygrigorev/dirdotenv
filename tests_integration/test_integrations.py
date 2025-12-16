import pytest
import pexpect


# Test fixture to create a temporary directory with .envrc
@pytest.fixture
def test_env(tmp_path):
    env_dir = tmp_path / "test_project"
    env_dir.mkdir()

    env_file = env_dir / ".envrc"
    env_file.write_text("export TEST_VAR='hello_world'")

    return env_dir


def run_shell_test(
    shell_cmd, test_env_path, var_name="TEST_VAR", var_value="hello_world"
):
    """Run a test session in the specified shell."""

    # Spawn the shell
    child = pexpect.spawn(shell_cmd, encoding="utf-8")

    # Set a simple prompt to make matching easier
    p1 = "DIRENV_TEST_"
    p2 = "PROMPT> "
    prompt = p1 + p2

    # Wait for initial prompt to ensure shell is ready
    if "pwsh" in shell_cmd:
        child.expect(r"PS .*>")
        child.sendline(f"function prompt {{ '{prompt}' }}")
    elif "fish" in shell_cmd:
        # Fish might not show a prompt immediately or might show a welcome message
        # But usually it buffers input. Let's try to just send it.
        child.sendline(
            f"set P1 '{p1}'; set P2 '{p2}'; function fish_prompt; echo \"$P1$P2\"; end"
        )
    elif "bash" in shell_cmd:
        child.sendline("unset PROMPT_COMMAND")
        child.sendline(f"P1='{p1}'; P2='{p2}'; PS1=\"$P1$P2\"")
    elif "zsh" in shell_cmd:
        child.sendline("precmd() { }")  # Clear precmd
        child.sendline(f"P1='{p1}'; P2='{p2}'; PS1=\"$P1$P2\"")

    child.expect(prompt)

    # Source the hook
    if "fish" in shell_cmd:
        child.sendline("dirdotenv hook fish | source")
    elif "bash" in shell_cmd:
        child.sendline('eval "$(dirdotenv hook bash)"')
    elif "zsh" in shell_cmd:
        child.sendline('eval "$(dirdotenv hook zsh)"')
    elif "pwsh" in shell_cmd:
        child.sendline("Invoke-Expression (dirdotenv hook powershell)")

    child.expect(prompt)

    # Verify variable is NOT set initially
    child.sendline(f"echo ${var_name}")
    child.expect(prompt)
    if var_value in child.before:
        print(f"Variable already set in {shell_cmd}. Output: {child.before}")
        return False

    # cd into the directory
    child.sendline(f"cd {test_env_path}")
    child.expect(prompt)

    # Check if variable is set
    child.sendline(f"echo ${var_name}")
    child.expect(prompt)

    if var_value not in child.before:
        print(f"Failed to load variable in {shell_cmd}. Output: {child.before}")
        return False

    # cd out
    child.sendline("cd ..")
    child.expect(prompt)

    # Check if variable is unset
    child.sendline(f"echo ${var_name}")
    child.expect(prompt)
    if var_value in child.before:
        print(f"Failed to unload variable in {shell_cmd}. Output: {child.before}")
        return False

    return True


@pytest.mark.parametrize("shell", ["bash", "zsh", "fish"])
def test_shell_integration(shell, test_env):
    """Test dirdotenv integration in different shells."""
    assert run_shell_test(shell, test_env)


@pytest.fixture
def nested_test_env(tmp_path):
    root_dir = tmp_path / "nested_project"
    root_dir.mkdir()

    # Root .envrc
    (root_dir / ".envrc").write_text(
        "export ROOT_VAR='root_value'\nexport SHARED_VAR='root_shared'"
    )

    # Child directory
    child_dir = root_dir / "child"
    child_dir.mkdir()

    # Child .envrc
    (child_dir / ".envrc").write_text(
        "export CHILD_VAR='child_value'\nexport SHARED_VAR='child_shared'"
    )

    return root_dir, child_dir


@pytest.mark.parametrize("shell", ["bash", "zsh", "fish"])
def test_nested_inheritance(shell, nested_test_env):
    """Test subdirectory inheritance and overriding."""
    root_dir, child_dir = nested_test_env

    # Run test manually to handle complex navigation
    child = pexpect.spawn(shell, encoding="utf-8")

    p1 = "DIRENV_TEST_"
    p2 = "PROMPT> "
    prompt = p1 + p2

    if "bash" in shell:
        child.sendline("unset PROMPT_COMMAND")
        child.sendline(f"P1='{p1}'; P2='{p2}'; PS1=\"$P1$P2\"")
    elif "zsh" in shell:
        child.sendline("precmd() { }")
        child.sendline(f"P1='{p1}'; P2='{p2}'; PS1=\"$P1$P2\"")
    elif "fish" in shell:
        child.sendline(
            f"set P1 '{p1}'; set P2 '{p2}'; function fish_prompt; echo \"$P1$P2\"; end"
        )
    elif "pwsh" in shell:
        child.sendline(f"function prompt {{ '{prompt}' }}")

    child.expect(prompt)

    # Source hook
    if "fish" in shell:
        child.sendline("dirdotenv hook fish | source")
    elif "bash" in shell:
        child.sendline('eval "$(dirdotenv hook bash)"')
    elif "zsh" in shell:
        child.sendline('eval "$(dirdotenv hook zsh)"')
    elif "pwsh" in shell:
        child.sendline("Invoke-Expression (dirdotenv hook powershell)")

    child.expect(prompt)

    # 1. Enter root
    child.sendline(f"cd {root_dir}")
    child.expect(prompt)

    # Check root vars
    child.sendline("echo $ROOT_VAR")
    child.expect(prompt)
    assert "root_value" in child.before

    child.sendline("echo $SHARED_VAR")
    child.expect(prompt)
    assert "root_shared" in child.before

    # 2. Enter child
    child.sendline(f"cd {child_dir}")
    child.expect(prompt)

    # Check child vars (inherited and overridden)
    child.sendline("echo $ROOT_VAR")
    child.expect(prompt)
    assert "root_value" in child.before

    child.sendline("echo $CHILD_VAR")
    child.expect(prompt)
    assert "child_value" in child.before

    child.sendline("echo $SHARED_VAR")
    child.expect(prompt)
    assert "child_shared" in child.before

    # 3. Go back to root
    child.sendline("cd ..")
    child.expect(prompt)

    # Check vars restored
    child.sendline("echo $ROOT_VAR")
    child.expect(prompt)
    assert "root_value" in child.before

    child.sendline("echo $CHILD_VAR")
    child.expect(prompt)
    assert "child_value" not in child.before

    child.sendline("echo $SHARED_VAR")
    child.expect(prompt)
    assert "root_shared" in child.before

    # 4. Leave root
    child.sendline("cd ..")
    child.expect(prompt)

    # Check all unset
    child.sendline("echo $ROOT_VAR")
    child.expect(prompt)
    assert "root_value" not in child.before


@pytest.fixture
def dot_env_test_env(tmp_path):
    env_dir = tmp_path / "dotenv_project"
    env_dir.mkdir()
    (env_dir / ".env").write_text("DOTENV_VAR='dotenv_value'")
    return env_dir


@pytest.mark.parametrize("shell", ["bash", "zsh", "fish"])
def test_dot_env_file(shell, dot_env_test_env):
    """Test .env file loading."""
    assert run_shell_test(shell, dot_env_test_env, "DOTENV_VAR", "dotenv_value")


@pytest.fixture
def empty_dir_for_new_env(tmp_path):
    """Create an empty directory where we'll create a .env file during the test."""
    env_dir = tmp_path / "new_env_project"
    env_dir.mkdir()
    return env_dir


@pytest.mark.parametrize("shell", ["bash", "zsh", "fish"])
def test_new_env_file_detection(shell, empty_dir_for_new_env):
    """Test that newly created .env files are detected immediately without cd .. && cd -."""
    test_dir = empty_dir_for_new_env

    # Spawn the shell
    child = pexpect.spawn(shell, encoding="utf-8")

    # Set a simple prompt
    p1 = "DIRENV_TEST_"
    p2 = "PROMPT> "
    prompt = p1 + p2

    if "bash" in shell:
        child.sendline("unset PROMPT_COMMAND")
        child.sendline(f"P1='{p1}'; P2='{p2}'; PS1=\"$P1$P2\"")
    elif "zsh" in shell:
        # Don't override precmd - just set the prompt
        child.sendline(f"P1='{p1}'; P2='{p2}'; PS1=\"$P1$P2\"")
    elif "fish" in shell:
        child.sendline(
            f"set P1 '{p1}'; set P2 '{p2}'; function fish_prompt; echo \"$P1$P2\"; end"
        )

    child.expect(prompt)

    # Source the hook
    if "fish" in shell:
        child.sendline("dirdotenv hook fish | source")
    elif "bash" in shell:
        child.sendline('eval "$(dirdotenv hook bash)"')
    elif "zsh" in shell:
        child.sendline('eval "$(dirdotenv hook zsh)"')

    child.expect(prompt)

    # cd into the empty directory
    child.sendline(f"cd {test_dir}")
    child.expect(prompt)

    # Verify variable is NOT set yet
    child.sendline("echo $NEW_VAR")
    child.expect(prompt)
    if "new_value" in child.before:
        pytest.fail(f"Variable already set in {shell}. Output: {child.before}")

    # Create a new .env file while in the directory
    env_file = test_dir / ".env"
    env_file.write_text("NEW_VAR='new_value'")

    # Trigger a prompt (simulating user pressing enter or running any command)
    # For bash and zsh, this triggers the prompt hook
    # For fish, we need to manually call the load function since fish only checks on PWD change
    if "fish" in shell:
        child.sendline("_dirdotenv_load")
        child.expect(prompt)
    else:
        child.sendline("echo 'triggering check'")
        child.expect(prompt)

    # Now check if variable is loaded
    child.sendline("echo $NEW_VAR")
    child.expect(prompt)

    if "new_value" not in child.before:
        pytest.fail(
            f"Failed to load newly created .env in {shell}. Output: {child.before}"
        )


@pytest.mark.parametrize("shell", ["bash", "zsh", "fish"])
def test_uvx_hook_behavior(shell, test_env):
    """
    Test that the hook works when dirdotenv is invoked via 'uvx dirdotenv'.
    Start with mocking 'uvx' as a function/alias that calls dirdotenv.
    """
    # 1. Spawn shell
    child = pexpect.spawn(shell, encoding="utf-8")

    # Set a simple prompt
    p1 = "DIRENV_TEST_"
    p2 = "PROMPT> "
    prompt = p1 + p2

    if "bash" in shell:
        child.sendline("unset PROMPT_COMMAND")
        child.sendline(f"P1='{p1}'; P2='{p2}'; PS1=\"$P1$P2\"")

    elif "zsh" in shell:
        child.sendline("precmd() { }")
        child.sendline(f"P1='{p1}'; P2='{p2}'; PS1=\"$P1$P2\"")

    elif "fish" in shell:
        child.sendline(
            f"set P1 '{p1}'; set P2 '{p2}'; function fish_prompt; echo \"$P1$P2\"; end"
        )

    child.expect(prompt)

    # 2. Source the hook using 'uvx dirdotenv hook ...'
    # detecting it as 'uvx dirdotenv' automatically without --cmd override
    # logic will return 'uvx dirdotenv' because uvx wrapper uses uv tool run
    if "fish" in shell:
        child.sendline("uvx dirdotenv hook fish | source")
    elif "bash" in shell:
        child.sendline('eval "$(uvx dirdotenv hook bash)"')
    elif "zsh" in shell:
        child.sendline('eval "$(uvx dirdotenv hook zsh)"')

    child.expect(prompt)

    # 3. Test that it works
    # cd into directory
    child.sendline(f"cd {test_env}")
    child.expect(prompt)

    # Check variable
    child.sendline("echo $TEST_VAR")
    child.expect(prompt)

    if "hello_world" not in child.before:
        print(
            f"Failed to load variable with uvx hook in {shell}. Output: {child.before}"
        )
        return False

    return True
