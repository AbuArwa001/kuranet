"""
# kuranet/urls.py
This file contains the URL declarations for the Kuranet project.
It includes the admin interface and API endpoints.
"""


# kuranet/urls.py
from django.urls import path, include
from django.contrib import admin
from django.views.generic import RedirectView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Remove drf_yasg imports and replace with drf_spectacular
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('', include([
        path('polls/', include('polls.urls')),
        path('users/', include('users.urls')),
        path('auth/', include([
            path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
            path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        ])),
    ])),
    
    # Documentation - updated to use drf_spectacular
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/doc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Redirect from root to Swagger
    path('', RedirectView.as_view(url='/swagger/', permanent=False)),
]
