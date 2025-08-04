"""
# kuranet/urls.py
This file contains the URL declarations for the Kuranet project.
It includes the admin interface and API endpoints.
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

SchemaView = get_schema_view(
    openapi.Info(
        title="Kuranet API",
        default_version="v1",
        description="API documentation for Kuranet App",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="support@kuranet.dev"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("", RedirectView.as_view(url="/api/v1/", permanent=False)),
    path("admin/", admin.site.urls),
    path("api/v1/", include("polls.urls")),
    path("api/v1/", include("users.urls")),
    path("api/v1/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path(
        "api/v1/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"
    ),
    # Swagger and ReDoc endpoints
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        SchemaView.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "swagger/",
        SchemaView.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", SchemaView.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
