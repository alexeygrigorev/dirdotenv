"""Tests for directory-aware environment loading with inheritance."""

import os
import tempfile

from dirdotenv.loader import (
    find_env_files_in_tree,
    load_env_with_inheritance,
    get_loaded_keys,
    get_unloaded_keys,
    format_export_commands,
    format_unset_commands,
    format_message,
    compute_env_state,
    has_state_changed,
)


def test_find_env_files_in_tree_single_dir():
    """Test finding env files in a single directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create .env file
        env_file = os.path.join(tmpdir, '.env')
        with open(env_file, 'w') as f:
            f.write("TEST=value\n")
        
        result = find_env_files_in_tree(tmpdir)
        assert len(result) == 1
        assert tmpdir in result


def test_find_env_files_in_tree_nested():
    """Test finding env files in nested directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create parent .env
        parent_env = os.path.join(tmpdir, '.env')
        with open(parent_env, 'w') as f:
            f.write("PARENT=value\n")
        
        # Create child directory with .env
        child_dir = os.path.join(tmpdir, 'child')
        os.makedirs(child_dir)
        child_env = os.path.join(child_dir, '.env')
        with open(child_env, 'w') as f:
            f.write("CHILD=value\n")
        
        result = find_env_files_in_tree(child_dir)
        assert len(result) == 2
        assert tmpdir == result[0]  # Parent first
        assert child_dir == result[1]  # Child second


def test_find_env_files_in_tree_no_files():
    """Test finding env files when none exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = find_env_files_in_tree(tmpdir)
        assert len(result) == 0


def test_load_env_with_inheritance_single_dir():
    """Test loading from single directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = os.path.join(tmpdir, '.env')
        with open(env_file, 'w') as f:
            f.write("KEY1=value1\n")
            f.write("KEY2=value2\n")
        
        env_vars, dirs = load_env_with_inheritance(tmpdir)
        assert env_vars == {'KEY1': 'value1', 'KEY2': 'value2'}
        assert len(dirs) == 1


def test_load_env_with_inheritance_parent_child():
    """Test loading with parent and child directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Parent .env
        parent_env = os.path.join(tmpdir, '.env')
        with open(parent_env, 'w') as f:
            f.write("PARENT_KEY=parent_value\n")
            f.write("SHARED_KEY=parent_value\n")
        
        # Child .env
        child_dir = os.path.join(tmpdir, 'child')
        os.makedirs(child_dir)
        child_env = os.path.join(child_dir, '.env')
        with open(child_env, 'w') as f:
            f.write("CHILD_KEY=child_value\n")
            f.write("SHARED_KEY=child_value\n")  # Override parent
        
        env_vars, dirs = load_env_with_inheritance(child_dir)
        assert env_vars['PARENT_KEY'] == 'parent_value'
        assert env_vars['CHILD_KEY'] == 'child_value'
        assert env_vars['SHARED_KEY'] == 'child_value'  # Child overrides parent
        assert len(dirs) == 2


def test_load_env_with_inheritance_grandparent():
    """Test loading with grandparent, parent, and child directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Grandparent .env
        grandparent_env = os.path.join(tmpdir, '.env')
        with open(grandparent_env, 'w') as f:
            f.write("GRAND=grand_value\n")
            f.write("OVERRIDE=grand_value\n")
        
        # Parent .env
        parent_dir = os.path.join(tmpdir, 'parent')
        os.makedirs(parent_dir)
        parent_env = os.path.join(parent_dir, '.env')
        with open(parent_env, 'w') as f:
            f.write("PARENT=parent_value\n")
            f.write("OVERRIDE=parent_value\n")
        
        # Child .env
        child_dir = os.path.join(parent_dir, 'child')
        os.makedirs(child_dir)
        child_env = os.path.join(child_dir, '.env')
        with open(child_env, 'w') as f:
            f.write("CHILD=child_value\n")
            f.write("OVERRIDE=child_value\n")
        
        env_vars, dirs = load_env_with_inheritance(child_dir)
        assert env_vars['GRAND'] == 'grand_value'
        assert env_vars['PARENT'] == 'parent_value'
        assert env_vars['CHILD'] == 'child_value'
        assert env_vars['OVERRIDE'] == 'child_value'  # Child wins
        assert len(dirs) == 3


def test_load_env_with_inheritance_subdirectory_no_env():
    """Test subdirectory without .env inherits from parent."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Parent .env
        parent_env = os.path.join(tmpdir, '.env')
        with open(parent_env, 'w') as f:
            f.write("PARENT_KEY=parent_value\n")
        
        # Child directory without .env
        child_dir = os.path.join(tmpdir, 'child')
        os.makedirs(child_dir)
        
        env_vars, dirs = load_env_with_inheritance(child_dir)
        assert env_vars == {'PARENT_KEY': 'parent_value'}
        assert len(dirs) == 1  # Only parent has env file


def test_get_loaded_keys():
    """Test identifying loaded/changed keys."""
    old_vars = {'KEY1': 'old_value', 'KEY2': 'value2'}
    new_vars = {'KEY1': 'new_value', 'KEY2': 'value2', 'KEY3': 'value3'}
    
    loaded = get_loaded_keys(old_vars, new_vars)
    assert 'KEY1' in loaded  # Changed
    assert 'KEY2' not in loaded  # Unchanged
    assert 'KEY3' in loaded  # New


def test_get_unloaded_keys():
    """Test identifying unloaded keys."""
    old_vars = {'KEY1': 'value1', 'KEY2': 'value2', 'KEY3': 'value3'}
    new_vars = {'KEY1': 'value1', 'KEY3': 'value3'}
    
    unloaded = get_unloaded_keys(old_vars, new_vars)
    assert 'KEY2' in unloaded
    assert 'KEY1' not in unloaded
    assert 'KEY3' not in unloaded


def test_format_export_commands_bash():
    """Test formatting export commands for bash."""
    env_vars = {'KEY1': 'value1', 'KEY2': "value's"}
    result = format_export_commands(env_vars, 'bash')
    assert "export KEY1='value1'" in result
    assert "export KEY2='value'\\''s'" in result


def test_format_export_commands_fish():
    """Test formatting export commands for fish."""
    env_vars = {'KEY1': 'value1'}
    result = format_export_commands(env_vars, 'fish')
    assert "set -gx KEY1 'value1'" in result


def test_format_export_commands_powershell():
    """Test formatting export commands for PowerShell."""
    env_vars = {'KEY1': 'value1', 'KEY2': "value's"}
    result = format_export_commands(env_vars, 'powershell')
    assert "$env:KEY1 = 'value1'" in result
    assert "$env:KEY2 = 'value''s'" in result


def test_format_unset_commands_bash():
    """Test formatting unset commands for bash."""
    keys = {'KEY1', 'KEY2'}
    result = format_unset_commands(keys, 'bash')
    assert 'unset KEY1' in result
    assert 'unset KEY2' in result


def test_format_unset_commands_fish():
    """Test formatting unset commands for fish."""
    keys = {'KEY1'}
    result = format_unset_commands(keys, 'fish')
    assert 'set -e KEY1' in result


def test_format_unset_commands_powershell():
    """Test formatting unset commands for PowerShell."""
    keys = {'KEY1'}
    result = format_unset_commands(keys, 'powershell')
    assert 'Remove-Item Env:KEY1' in result


def test_format_message_bash():
    """Test formatting messages for bash."""
    result = format_message('test message', 'bash')
    assert "echo 'test message' >&2" in result


def test_format_message_powershell():
    """Test formatting messages for PowerShell."""
    result = format_message('test message', 'powershell')
    assert "Write-Host 'test message'" in result


def test_compute_env_state_no_files():
    """Test computing state when no .env files exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        state = compute_env_state(tmpdir)
        # Should contain directory but no file entries
        assert f"dir:{tmpdir}" in state
        assert ".env" not in state
        assert ".envrc" not in state


def test_compute_env_state_with_env_file():
    """Test computing state with a .env file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = os.path.join(tmpdir, '.env')
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write("TEST=value\n")
        
        state = compute_env_state(tmpdir)
        assert f"dir:{tmpdir}" in state
        assert ".env" in state
        # State should include modification time
        assert ":" in state


def test_compute_env_state_with_both_files():
    """Test computing state with both .env and .envrc files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = os.path.join(tmpdir, '.env')
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write("TEST1=value1\n")
        
        envrc_file = os.path.join(tmpdir, '.envrc')
        with open(envrc_file, 'w', encoding='utf-8') as f:
            f.write("export TEST2=value2\n")
        
        state = compute_env_state(tmpdir)
        assert ".env" in state
        assert ".envrc" in state


def test_compute_env_state_nested():
    """Test computing state with nested directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Parent .env
        parent_env = os.path.join(tmpdir, '.env')
        with open(parent_env, 'w', encoding='utf-8') as f:
            f.write("PARENT=value\n")
        
        # Child directory with .env
        child_dir = os.path.join(tmpdir, 'child')
        os.makedirs(child_dir)
        child_env = os.path.join(child_dir, '.env')
        with open(child_env, 'w', encoding='utf-8') as f:
            f.write("CHILD=value\n")
        
        state = compute_env_state(child_dir)
        # Should include both parent and child .env files
        assert parent_env in state
        assert child_env in state


def test_has_state_changed_none_state():
    """Test state change detection with no previous state."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # First time should always detect change
        assert has_state_changed(None, tmpdir) is True


def test_has_state_changed_same_state():
    """Test state change detection with unchanged state."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = os.path.join(tmpdir, '.env')
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write("TEST=value\n")
        
        # Get initial state
        state1 = compute_env_state(tmpdir)
        
        # Check again without changes
        assert has_state_changed(state1, tmpdir) is False


def test_has_state_changed_new_file():
    """Test state change detection when a new file is created."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Get initial state with no files
        state1 = compute_env_state(tmpdir)
        
        # Create a new .env file
        env_file = os.path.join(tmpdir, '.env')
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write("NEW_VAR=value\n")
        
        # Should detect the change
        assert has_state_changed(state1, tmpdir) is True


def test_has_state_changed_modified_file():
    """Test state change detection when a file is modified."""
    import time
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = os.path.join(tmpdir, '.env')
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write("TEST=value1\n")
        
        # Get initial state
        state1 = compute_env_state(tmpdir)
        
        # Wait a bit to ensure mtime changes
        time.sleep(0.01)
        
        # Modify the file
        with open(env_file, 'a', encoding='utf-8') as f:
            f.write("TEST2=value2\n")
        
        # Should detect the change
        assert has_state_changed(state1, tmpdir) is True


def test_has_state_changed_directory_change():
    """Test state change detection when changing directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        dir1 = os.path.join(tmpdir, 'dir1')
        dir2 = os.path.join(tmpdir, 'dir2')
        os.makedirs(dir1)
        os.makedirs(dir2)
        
        # Get state for dir1
        state1 = compute_env_state(dir1)
        
        # Check state for dir2 (different directory)
        assert has_state_changed(state1, dir2) is True


def test_new_env_file_detection():
    """Test that newly created .env files are detected immediately.
    
    This test reproduces the issue where:
    - User enters a directory
    - Creates a new .env file
    - File should be discovered immediately without cd .. && cd -
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # First load: no .env file exists
        env_vars_1, dirs_1 = load_env_with_inheritance(tmpdir)
        assert len(env_vars_1) == 0
        assert len(dirs_1) == 0
        
        # Create a new .env file (simulating user creating it in current directory)
        env_file = os.path.join(tmpdir, '.env')
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write("NEW_VAR=new_value\n")
        
        # Second load: should detect the new file immediately
        env_vars_2, dirs_2 = load_env_with_inheritance(tmpdir)
        assert len(env_vars_2) == 1
        assert env_vars_2['NEW_VAR'] == 'new_value'
        assert len(dirs_2) == 1
        assert tmpdir in dirs_2


def test_modified_env_file_detection():
    """Test that modifications to existing .env files are detected.
    
    This test ensures that when a .env file is modified,
    the changes are picked up immediately.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create initial .env file
        env_file = os.path.join(tmpdir, '.env')
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write("VAR1=value1\n")
        
        # First load
        env_vars_1, dirs_1 = load_env_with_inheritance(tmpdir)
        assert env_vars_1['VAR1'] == 'value1'
        assert 'VAR2' not in env_vars_1
        
        # Modify the .env file (add a new variable)
        with open(env_file, 'a', encoding='utf-8') as f:
            f.write("VAR2=value2\n")
        
        # Second load: should detect the change
        env_vars_2, dirs_2 = load_env_with_inheritance(tmpdir)
        assert env_vars_2['VAR1'] == 'value1'
        assert env_vars_2['VAR2'] == 'value2'
