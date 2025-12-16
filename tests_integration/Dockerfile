FROM python:3.11-slim-bookworm

# Install shells and dependencies
RUN apt-get update && apt-get install -y \
    bash \
    zsh \
    fish \
# Install uv directly from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy project files
COPY . /app

# Install dirdotenv via pip for standard usage
RUN pip install .

# Install dirdotenv as a tool using uv, so 'uvx dirdotenv' works with the local version
# We set UV_PYTHON to system python to avoid downloading python versions
ENV UV_PYTHON=python3.11
RUN uv tool install . --force

# Install test dependencies
RUN pip install pytest pexpect

# Default command
CMD ["pytest", "tests_integration/test_integrations.py"]
