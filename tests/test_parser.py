"""Tests for dirdotenv parser."""

import os
import tempfile

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


def test_parse_env_file_unbalanced_quotes():
    """Test parsing .env file with unbalanced quotes (should keep as-is)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = os.path.join(tmpdir, '.env')
        with open(env_file, 'w') as f:
            f.write('VALUE1="test\n')  # Missing closing quote
            f.write("VALUE2='test\n")  # Missing closing quote
            f.write('VALUE3="\n')      # Empty with single quote
        
        result = parse_env_file(env_file)
        # Should keep values as-is when quotes are unbalanced
        assert result == {
            'VALUE1': '"test',
            'VALUE2': "'test",
            'VALUE3': '"'
        }


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
        # .env should override .envrc for OPENAI_API_KEY
        assert result == {
            'OPENAI_API_KEY': 'env-key',  # overridden by .env
            'API_PORT': '8080',  # from .env
            'DATABASE_URL': 'postgres://localhost/mydb'  # from .envrc
        }


def test_load_env_empty_directory():
    """Test loading environment from directory with no env files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = load_env(tmpdir)
        assert result == {}
