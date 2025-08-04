"""
Pytest configuration for kuranet project.

This module configures pytest for Django testing, including:
- Django settings configuration
- Static directory creation
- Database access for all tests

This file is automatically loaded by pytest when running tests.
"""

import pytest
import os
from django.conf import settings


def pytest_configure():
    """Configure pytest for Django."""
    # Create static directory if it doesn't exist
    static_dir = os.path.join(settings.BASE_DIR, "static")
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    # Set Django settings module if not already set
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kuranet.settings")


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Enable database access for all tests.

    This fixture is automatically applied to all tests, allowing them
    to access the database without explicitly requesting the 'db' fixture.
    
    """
    pass
