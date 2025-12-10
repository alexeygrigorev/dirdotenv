"""Tests for dirdotenv parser."""

import os
import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dirdotenv.parser import parse_env_file, parse_envrc_file, load_env


def test_parse_env_file_simple():
    """Test parsing a simple .env file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = os.path.join(tmpdir, '.env')
        with open(env_file, 'w') as f:
            f.write("OPENAI_API_KEY='my-key'\n")
        
        result = parse_env_file(env_file)
        assert result == {'OPENAI_API_KEY': 'my-key'}


def test_parse_env_file_double_quotes():
    """Test parsing .env file with double quotes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = os.path.join(tmpdir, '.env')
        with open(env_file, 'w') as f:
            f.write('DATABASE_URL="postgres://localhost/mydb"\n')
        
        result = parse_env_file(env_file)
        assert result == {'DATABASE_URL': 'postgres://localhost/mydb'}


def test_parse_env_file_no_quotes():
    """Test parsing .env file without quotes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = os.path.join(tmpdir, '.env')
        with open(env_file, 'w') as f:
            f.write('API_PORT=8080\n')
        
        result = parse_env_file(env_file)
        assert result == {'API_PORT': '8080'}


def test_parse_env_file_multiple_vars():
    """Test parsing .env file with multiple variables."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = os.path.join(tmpdir, '.env')
        with open(env_file, 'w') as f:
            f.write("OPENAI_API_KEY='my-key'\n")
            f.write('DATABASE_URL="postgres://localhost/mydb"\n')
            f.write('API_PORT=8080\n')
        
        result = parse_env_file(env_file)
        assert result == {
            'OPENAI_API_KEY': 'my-key',
            'DATABASE_URL': 'postgres://localhost/mydb',
            'API_PORT': '8080'
        }


def test_parse_env_file_comments():
    """Test parsing .env file with comments."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = os.path.join(tmpdir, '.env')
        with open(env_file, 'w') as f:
            f.write("# This is a comment\n")
            f.write("OPENAI_API_KEY='my-key'\n")
            f.write("\n")
            f.write("# Another comment\n")
            f.write('API_PORT=8080\n')
        
        result = parse_env_file(env_file)
        assert result == {
            'OPENAI_API_KEY': 'my-key',
            'API_PORT': '8080'
        }


def test_parse_env_file_missing():
    """Test parsing a non-existent .env file."""
    result = parse_env_file('/nonexistent/path/.env')
    assert result == {}


def test_parse_envrc_file_simple():
    """Test parsing a simple .envrc file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        envrc_file = os.path.join(tmpdir, '.envrc')
        with open(envrc_file, 'w') as f:
            f.write("export OPENAI_API_KEY='my-key'\n")
        
        result = parse_envrc_file(envrc_file)
        assert result == {'OPENAI_API_KEY': 'my-key'}


def test_parse_envrc_file_double_quotes():
    """Test parsing .envrc file with double quotes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        envrc_file = os.path.join(tmpdir, '.envrc')
        with open(envrc_file, 'w') as f:
            f.write('export DATABASE_URL="postgres://localhost/mydb"\n')
        
        result = parse_envrc_file(envrc_file)
        assert result == {'DATABASE_URL': 'postgres://localhost/mydb'}


def test_parse_envrc_file_no_quotes():
    """Test parsing .envrc file without quotes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        envrc_file = os.path.join(tmpdir, '.envrc')
        with open(envrc_file, 'w') as f:
            f.write('export API_PORT=8080\n')
        
        result = parse_envrc_file(envrc_file)
        assert result == {'API_PORT': '8080'}


def test_parse_envrc_file_multiple_vars():
    """Test parsing .envrc file with multiple variables."""
    with tempfile.TemporaryDirectory() as tmpdir:
        envrc_file = os.path.join(tmpdir, '.envrc')
        with open(envrc_file, 'w') as f:
            f.write("export OPENAI_API_KEY='my-key'\n")
            f.write('export DATABASE_URL="postgres://localhost/mydb"\n')
            f.write('export API_PORT=8080\n')
        
        result = parse_envrc_file(envrc_file)
        assert result == {
            'OPENAI_API_KEY': 'my-key',
            'DATABASE_URL': 'postgres://localhost/mydb',
            'API_PORT': '8080'
        }


def test_parse_envrc_file_comments():
    """Test parsing .envrc file with comments."""
    with tempfile.TemporaryDirectory() as tmpdir:
        envrc_file = os.path.join(tmpdir, '.envrc')
        with open(envrc_file, 'w') as f:
            f.write("# This is a comment\n")
            f.write("export OPENAI_API_KEY='my-key'\n")
            f.write("\n")
            f.write("# Another comment\n")
            f.write('export API_PORT=8080\n')
        
        result = parse_envrc_file(envrc_file)
        assert result == {
            'OPENAI_API_KEY': 'my-key',
            'API_PORT': '8080'
        }


def test_parse_envrc_file_missing():
    """Test parsing a non-existent .envrc file."""
    result = parse_envrc_file('/nonexistent/path/.envrc')
    assert result == {}


def test_load_env_with_env_file():
    """Test loading environment from .env file only."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = os.path.join(tmpdir, '.env')
        with open(env_file, 'w') as f:
            f.write("OPENAI_API_KEY='my-key'\n")
            f.write('API_PORT=8080\n')
        
        result = load_env(tmpdir)
        assert result == {
            'OPENAI_API_KEY': 'my-key',
            'API_PORT': '8080'
        }


def test_load_env_with_envrc_file():
    """Test loading environment from .envrc file only."""
    with tempfile.TemporaryDirectory() as tmpdir:
        envrc_file = os.path.join(tmpdir, '.envrc')
        with open(envrc_file, 'w') as f:
            f.write("export OPENAI_API_KEY='my-key'\n")
            f.write('export API_PORT=8080\n')
        
        result = load_env(tmpdir)
        assert result == {
            'OPENAI_API_KEY': 'my-key',
            'API_PORT': '8080'
        }


def test_load_env_with_both_files():
    """Test loading environment from both .env and .envrc files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create .env file
        env_file = os.path.join(tmpdir, '.env')
        with open(env_file, 'w') as f:
            f.write("OPENAI_API_KEY='env-key'\n")
            f.write('API_PORT=8080\n')
        
        # Create .envrc file
        envrc_file = os.path.join(tmpdir, '.envrc')
        with open(envrc_file, 'w') as f:
            f.write("export OPENAI_API_KEY='envrc-key'\n")
            f.write('export DATABASE_URL="postgres://localhost/mydb"\n')
        
        result = load_env(tmpdir)
        # .envrc should override .env for OPENAI_API_KEY
        assert result == {
            'OPENAI_API_KEY': 'envrc-key',  # overridden by .envrc
            'API_PORT': '8080',  # from .env
            'DATABASE_URL': 'postgres://localhost/mydb'  # from .envrc
        }


def test_load_env_empty_directory():
    """Test loading environment from directory with no env files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = load_env(tmpdir)
        assert result == {}


if __name__ == '__main__':
    # Run all tests
    test_functions = [
        test_parse_env_file_simple,
        test_parse_env_file_double_quotes,
        test_parse_env_file_no_quotes,
        test_parse_env_file_multiple_vars,
        test_parse_env_file_comments,
        test_parse_env_file_missing,
        test_parse_envrc_file_simple,
        test_parse_envrc_file_double_quotes,
        test_parse_envrc_file_no_quotes,
        test_parse_envrc_file_multiple_vars,
        test_parse_envrc_file_comments,
        test_parse_envrc_file_missing,
        test_load_env_with_env_file,
        test_load_env_with_envrc_file,
        test_load_env_with_both_files,
        test_load_env_empty_directory,
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
