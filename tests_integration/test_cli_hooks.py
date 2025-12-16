import sys
import pytest
from unittest.mock import patch
from dirdotenv.cli import get_invocation_command


class TestInvocationCommand:
    def test_default_invocation(self):
        """Test simple dirdotenv invocation."""
        with patch.object(
            sys, "argv", ["/usr/bin/dirdotenv", "hook", "bash"]
        ), patch.object(sys, "executable", "/usr/bin/python3"):
            cmd = get_invocation_command()
            assert cmd == "dirdotenv"

    def test_python_module_invocation(self):
        """Test python -m dirdotenv invocation."""
        mock_executable = "/usr/bin/python3"
        with patch.object(
            sys, "argv", ["/path/to/__main__.py", "hook", "bash"]
        ), patch.object(sys, "executable", mock_executable):
            cmd = get_invocation_command()
            # Expect full path to python executable + -m dirdotenv
            assert cmd == f"{mock_executable} -m dirdotenv"

    def test_uvx_invocation(self):
        """Test invocation via uvx / uv tool run."""
        # Mock executable path to simulate uv tool environment
        # e.g. /home/user/.uv/tools/dirdotenv/bin/python
        mock_uv_executable = "/home/user/.uv/tools/dirdotenv/bin/python"

        with patch.object(
            sys,
            "argv",
            ["/home/user/.uv/tools/dirdotenv/bin/dirdotenv", "hook", "bash"],
        ), patch.object(sys, "executable", mock_uv_executable):
            cmd = get_invocation_command()
            assert cmd == "uvx dirdotenv"

    def test_uv_tools_invocation_windows(self):
        """Test invocation via uvx on Windows."""
        mock_executable = (
            "C:/Users/user/AppData/Local/uv/tools/dirdotenv/Scripts/python.exe"
        )

        with patch.object(sys, "argv", ["..."]), patch.object(
            sys, "executable", mock_executable
        ):
            cmd = get_invocation_command()
            assert cmd == "uvx dirdotenv"

    def test_absolute_path_invocation(self):
        """Test invocation via explicit path (not uv managed)."""
        # Should fallback to "dirdotenv" if not python -m and not uv managed
        with patch.object(
            sys, "argv", ["/opt/custom/bin/dirdotenv", "hook", "bash"]
        ), patch.object(sys, "executable", "/opt/custom/bin/python"):
            cmd = get_invocation_command()
            assert cmd == "dirdotenv"
