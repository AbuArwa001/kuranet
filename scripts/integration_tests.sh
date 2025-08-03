#!/bin/bash
set -e  # Exit immediately if any command fails

# Configuration
VENV_PATH=~/kuranet/.venv
TEST_BASE_URL="http://localhost:8000"
MAX_WAIT_SECONDS=30
RETRY_INTERVAL=2

# Setup environment
python -m venv $VENV_PATH
source $VENV_PATH/bin/activate

# Install system dependencies (including curl if needed)
if ! command -v curl &> /dev/null; then
    echo "Installing curl..."
    apt-get update && apt-get install -y curl  # For Debian/Ubuntu
    # Or for Alpine: apk add curl
    # Or for CentOS: yum install curl
fi

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install pytest pytest-django pytest-cov pytest-xdist requests

# Start Django server in background
echo "Starting Django development server..."
python manage.py makemigrations users polls
python manage.py migrate
python manage.py runserver 0.0.0.0:8000 > /dev/null 2>&1 &
SERVER_PID=$!

# Function to check server status using Python requests as fallback
check_server() {
    # Try curl first if available
    if command -v curl &> /dev/null; then
        curl -s "$TEST_BASE_URL" > /dev/null
        return $?
    else
        # Fallback to Python requests
        python -c "import requests; exit(0 if requests.get('$TEST_BASE_URL', timeout=2).status_code == 200 else 1)"
        return $?
    fi
}

# Wait for server to become available
echo "Waiting for server to start..."
attempt=0
while [ $attempt -lt $((MAX_WAIT_SECONDS/RETRY_INTERVAL)) ]; do
    if check_server; then
        echo "Server is running at $TEST_BASE_URL"
        break
    fi
    sleep $RETRY_INTERVAL
    attempt=$((attempt+1))
done

if [ $attempt -eq $((MAX_WAIT_SECONDS/RETRY_INTERVAL)) ]; then
    echo "Error: Server did not start within $MAX_WAIT_SECONDS seconds"
    kill $SERVER_PID
    exit 1
fi

# Run tests with coverage
echo "Running integration tests..."
# pytest tests/integration_tests.py \
#     --cov=. \
#     --cov-report=xml:coverage.xml \
#     --cov-fail-under=80 \
#     --junitxml=test-results.xml \
#     -v \
#     --durations=10
pytest tests/ \
    --cov=. \
    --cov-report=xml:coverage.xml \
    --cov-config=.coveragerc \
    --cov-fail-under=80 \
    --junitxml=test-results.xml \
    -v
# Capture test exit code
TEST_EXIT_CODE=$?

# Clean up
echo "Stopping Django server..."
kill $SERVER_PID
wait $SERVER_PID 2>/dev/null

exit $TEST_EXIT_CODE

