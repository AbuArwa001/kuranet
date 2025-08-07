"""
# kuranet/urls.py
This file contains the URL declarations for the Kuranet project.
It includes the admin interface and API endpoints.
"""


from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import path, include, re_path
from django.contrib import admin
from django.views.generic import RedirectView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

schema_view = get_schema_view(
    openapi.Info(
        title="Kuranet API",
        default_version="v1",
        description="API documentation",
        terms_of_service="https://liwomasjid.co.ke/terms/",
        contact=openapi.Contact(email="contact@liwomasjid.co.ke"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/v1/', include([
        path('polls/', include('polls.urls')),
        path('users/', include('users.urls')),
        path('auth/', include([
            path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
            path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        ])),
    ])),
    
    # Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', RedirectView.as_view(url='/swagger/', permanent=False)),
]
