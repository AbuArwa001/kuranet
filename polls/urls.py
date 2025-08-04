"""
URL configuration for the polls application.

Defines API endpoints for polls using Django REST Framework ViewSets.
"""

from django.urls import include, path
from .views import PollViewSet

from rest_framework.routers import DefaultRouter

# DRF router for automatic URL generation
router = DefaultRouter()
router.register(r"polls", PollViewSet, basename="poll")

urlpatterns = [
    path("", include(router.urls)),
]
