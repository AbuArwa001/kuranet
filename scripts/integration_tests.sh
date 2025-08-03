#!/bin/bash
set -e  # Exit immediately if any command fails

# Setup environment
python -m venv ~/kuranet/.venv
source ~/kuranet/.venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install pytest pytest-django pytest-cov

# Run tests with coverage
pytest tests/integration_tests.py \
    --cov=. \
    --cov-report=xml:coverage.xml \
    --cov-fail-under=80 \
    --junitxml=test-results.xml