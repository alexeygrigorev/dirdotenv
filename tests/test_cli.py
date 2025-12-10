"""Tests for dirdotenv CLI."""

import os
import subprocess
import tempfile
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_cli_with_env_file():
    """Test CLI with .env file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = os.path.join(tmpdir, '.env')
        with open(env_file, 'w') as f:
            f.write("OPENAI_API_KEY='my-key'\n")
            f.write('API_PORT=8080\n')
        
        result = subprocess.run(
            ['dirdotenv', tmpdir],
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
            ['dirdotenv', tmpdir],
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
        
        result = subprocess.run(
            ['dirdotenv', tmpdir, '--exec', 'sh', '-c', 'echo $TEST_VAR'],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert 'test-value' in result.stdout


def test_cli_empty_directory():
    """Test CLI with empty directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            ['dirdotenv', tmpdir],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "No environment variables found" in result.stderr


if __name__ == '__main__':
    # Run all tests
    test_functions = [
        test_cli_with_env_file,
        test_cli_with_envrc_file,
        test_cli_exec,
        test_cli_empty_directory,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            print(f"✓ {test_func.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_func.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__}: {type(e).__name__}: {e}")
            failed += 1
    
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
