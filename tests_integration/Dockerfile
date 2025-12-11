FROM python:3.11-slim

# Install shells and dependencies
RUN apt-get update && apt-get install -y \
    bash \
    zsh \
    fish \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY . /app

# Install dirdotenv
RUN pip install .

# Install test dependencies
RUN pip install pytest pexpect

# Default command
CMD ["pytest", "tests_integration/test_integrations.py"]
