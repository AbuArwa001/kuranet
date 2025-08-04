# users/models.py
"""
Custom user models for the kuranet application.

This module defines a custom User model that extends Django's AbstractBaseUser
to provide application-specific user functionality.
"""

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


class UserManager(BaseUserManager):
    """
    Custom manager for the User model.
    
    Provides methods for creating regular users and superusers with
    username-based authentication instead of email.
    """
    
    def create_user(self, username, password=None, **extra_fields):
        """
        Create and return a regular user with the given username and password.
        
        Args:
            username (str): The username for the user
            password (str, optional): The user's password
            **extra_fields: Additional fields for the user
            
        Returns:
            User: The created user instance
            
        Raises:
            ValueError: If username is not provided
        """

        if not username:
            raise ValueError("The Username field is required")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        """
        Create and return a superuser with the given username and password.
        
        Args:
            username (str): The username for the superuser
            password (str, optional): The superuser's password
            **extra_fields: Additional fields for the user
            
        Returns:
            User: The created superuser instance
        """

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model for kuranet application.
    
    Uses username for authentication instead of email. Extends Django's
    AbstractBaseUser to provide custom user functionality while maintaining
    compatibility with Django's permission system.
    
    Attributes:
        username: Unique identifier for login (required)
        first_name: User's first name (optional)
        last_name: User's last name (optional)
        email: User's email address (required for registration)
        date_joined: Timestamp when user account was created
        is_staff: Whether user can access admin interface
        is_active: Whether user account is active
    """

    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(max_length=254, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # Custom manager
    objects = UserManager()

    # Authentication configuration
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        """Return string representation of the user."""
        return self.username

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
