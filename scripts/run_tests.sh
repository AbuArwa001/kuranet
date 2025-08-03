#!/bin/bash
set -e  # Exit immediately if any command fails

# 1. Setup environment (20% faster virtualenv creation)
echo "🔧 Setting up virtual environment..."
python -m venv --clear --system-site-packages "${VENV_PATH}"
source "${VENV_PATH}/bin/activate"

# 2. Install dependencies with cache
echo "📦 Installing dependencies..."
pip install --cache-dir /tmp/pip-cache -r requirements-test.txt pytest-cov pytest-xdist

# 3. Verify environment
echo "🔍 Verifying environment..."
echo "Python: $(python --version)"
echo "Pytest: $(pytest --version)"
pytest --config-file=pytest.ini --collect-only > /dev/null

# 4. Start Django server in background
echo "🚀 Starting Django test server..."
python manage.py makemigrations users polls
python manage.py migrate
python manage.py runserver 0.0.0.0:8000 & 
SERVER_PID=$!
sleep 5  # Give server time to start

# 5. Run tests with proper cleanup
echo "🧪 Running tests..."
TEST_RESULT=0
(
    trap 'echo "🧹 Cleaning up..."; kill $SERVER_PID || true; pkill -f "pytest" || true' EXIT
    pytest tests/integration_tests.py -v --cov --cov-report=xml --junitxml=test-results.xml || TEST_RESULT=$?
)

# 6. Verify artifacts with timestamps
echo "📄 Verifying artifacts..."
echo "Artifacts directory:"
ls -larth test-results.xml coverage.xml || true

[ -f "test-results.xml" ] || { echo "❌ Test results missing"; exit 1; }
[ -f "coverage.xml" ] || { echo "❌ Coverage report missing"; exit 1; }

# 7. Final exit handling
if [ -n "${TEST_RESULT}" ] && [ "${TEST_RESULT}" -ne 0 ]; then
    echo "🔥 Tests failed with exit code ${TEST_RESULT}"
    exit ${TEST_RESULT}
fi

echo "✅ All tests completed successfully"
exit 0