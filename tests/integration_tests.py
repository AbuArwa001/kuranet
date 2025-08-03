"""
Integration tests for Kuranet Django application
These tests verify interactions between components and external services
"""

import os
import requests
import pytest
from datetime import datetime, timedelta
import unittest
from dotenv import load_dotenv
import uuid

# Load environment variables from .env file
load_dotenv()



# Configuration
BASE_URL = "http://localhost:8000"  # Must match your test server port
API_PREFIX = "/api/v1/"  # Your API version prefix

# Test user credentials (should match your test database)
username = f"testuser_{uuid.uuid4()}"  # Unique username for each test run
TEST_USER = {
    "username": username,
    "email": "test1@kuranet.com",
    "first_name": "Test",
    "last_name": "User",
    "password": "TestPass123!",
}

class IntegrationTest(unittest.TestCase):
    """Base class for integration tests"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        # Ensure the server is running before tests
        cls.server_url = f"{BASE_URL}{API_PREFIX}"
        response = requests.get(cls.server_url)
        assert response.status_code == 200, "Server is not running"

    @classmethod
    def tearDownClass(cls):
        """Clean up after tests"""
        pass  # Implement any necessary cleanup
    def test_user_registration(self):
        """Test user registration endpoint"""
        url = f"{BASE_URL}{API_PREFIX}auth/register/"
        response = requests.post(url, json=TEST_USER)
        assert response.status_code == 201, "User registration failed"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
    # Run tests with verbosity
    # pytest.main(["-v", "--disable-warnings", __file__])
    # Use --disable-warnings to suppress warnings during test runs
    # pytest.main(["-v", "--maxfail=1", __file__])