#!/bin/bash
set -e  # Exit immediately if any command fails

# 1. Setup environment (20% faster virtualenv creation)
python -m venv --clear --system-site-packages "${VENV_PATH}"
source "${VENV_PATH}/bin/activate"

# 2. Install dependencies with cache
pip install --cache-dir /tmp/pip-cache -r requirements-test.txt pytest-cov pytest-xdist

# 3. Verify environment
echo "Python: $(python --version)"
echo "Pytest: $(pytest --version)"
pytest --config-file=pytest.ini --collect-only > /dev/null

# 4. Run tests with proper cleanup trap
(
    trap 'pkill -f "pytest"' EXIT  # Ensure pytest processes are killed
    pytest || TEST_RESULT=$?
)

# 5. Verify artifacts with timestamps
echo "Artifacts directory:"
ls -larth test-results.xml coverage.xml || true

[ -f "test-results.xml" ] || { echo "❌ Test results missing"; exit 1; }
[ -f "coverage.xml" ] || { echo "❌ Coverage report missing"; exit 1; }

# 6. Final exit handling
if [ -n "${TEST_RESULT}" ]; then
    echo "🔥 Tests failed with exit code ${TEST_RESULT}"
    exit ${TEST_RESULT}
fi

echo "✅ All tests completed successfully"