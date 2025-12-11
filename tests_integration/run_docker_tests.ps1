$ErrorActionPreference = "Stop"

Write-Host "Building Docker image..."
docker build --no-cache -t dirdotenv-test -f tests_integration/Dockerfile .

Write-Host "Running tests..."
docker run --rm dirdotenv-test bash -c "ls -la tests_integration && pytest tests_integration/test_integrations.py -v -s" > test_output.txt 2>&1
type test_output.txt
