$ErrorActionPreference = "Stop"

Write-Host "Building Docker image..."
docker build -t dirdotenv-test -f tests_integration/Dockerfile .

Write-Host "Running tests..."
docker run --rm dirdotenv-test pytest tests_integration/test_integrations.py -v -s

docker run --rm dirdotenv-test pytest tests_integration/test_file_change_detection.py -v -s