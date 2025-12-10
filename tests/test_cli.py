"""Tests for dirdotenv CLI."""

import os
import subprocess
import tempfile
import sys


def test_cli_with_env_file():
    """Test CLI with .env file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = os.path.join(tmpdir, '.env')
        with open(env_file, 'w') as f:
            f.write("OPENAI_API_KEY='my-key'\n")
            f.write('API_PORT=8080\n')
        
        result = subprocess.run(
            [sys.executable, '-m', 'dirdotenv', tmpdir, '--export'],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "export OPENAI_API_KEY='my-key'" in result.stdout
        assert "export API_PORT='8080'" in result.stdout


def test_cli_with_envrc_file():
    """Test CLI with .envrc file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        envrc_file = os.path.join(tmpdir, '.envrc')
        with open(envrc_file, 'w') as f:
            f.write("export OPENAI_API_KEY='my-key'\n")
            f.write('export API_PORT=8080\n')
        
        result = subprocess.run(
            [sys.executable, '-m', 'dirdotenv', tmpdir, '--export'],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "export OPENAI_API_KEY='my-key'" in result.stdout
        assert "export API_PORT='8080'" in result.stdout


def test_cli_exec():
    """Test CLI with --exec option."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = os.path.join(tmpdir, '.env')
        with open(env_file, 'w') as f:
            f.write("TEST_VAR='test-value'\n")
        
        # Use Python for cross-platform compatibility
        result = subprocess.run(
            [sys.executable, '-m', 'dirdotenv', tmpdir, '--exec', 
             sys.executable, '-c', 'import os; print(os.environ.get("TEST_VAR"))'],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert 'test-value' in result.stdout


def test_cli_empty_directory():
    """Test CLI with empty directory (should show help)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            [sys.executable, '-m', 'dirdotenv', tmpdir],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "usage:" in result.stdout or "usage:" in result.stderr


def test_cli_help():
    """Test CLI help output."""
    result = subprocess.run(
        [sys.executable, '-m', 'dirdotenv'],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    assert "usage:" in result.stdout or "usage:" in result.stderr
    assert "--export" in result.stdout or "--export" in result.stderr
