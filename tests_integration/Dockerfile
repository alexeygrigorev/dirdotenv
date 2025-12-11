FROM python:3.11-slim-bookworm

# Install shells and dependencies
RUN apt-get update && apt-get install -y \
    bash \
    zsh \
    fish \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install PowerShell
RUN wget -q "https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb" && \
    dpkg -i packages-microsoft-prod.deb && \
    rm packages-microsoft-prod.deb && \
    apt-get update && \
    apt-get install -y powershell

WORKDIR /app

# Copy project files
COPY . /app

# Debug: Check file size during build
RUN ls -la tests_integration/test_integrations.py

# Install dirdotenv
RUN pip install .

# Install test dependencies
RUN pip install pytest pexpect

# Default command
CMD ["pytest", "tests_integration/test_integrations.py"]
