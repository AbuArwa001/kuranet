"""
# kuranet/urls.py
This file contains the URL declarations for the Kuranet project.
It includes the admin interface and API endpoints.
"""
from django.contrib import admin
from django.urls import path,include
from django.views.generic import RedirectView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('', RedirectView.as_view(url='/api/v1/', permanent=False)),
    path('admin/', admin.site.urls),
    path('api/v1/', include('polls.urls')),
    path('api/v1/', include('users.urls')),
    path('api/v1/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
