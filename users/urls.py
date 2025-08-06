from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserViewSet, AuthViewSet
from rest_framework.routers import DefaultRouter

users_router = DefaultRouter()
users_router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    # Authentication endpoints
    # path('auth/register/', AuthViewSet.as_view({'post': 'register'}), name='register'),
    path('auth/register/', UserViewSet.as_view({'post': 'create'}), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', AuthViewSet.as_view({'post': 'logout'}), name='logout'),
    path('users/', UserViewSet.as_view({
        'get': 'list',
    }), name='user-list'),
    
    # path('', include(users_router.urls)),
    # User management endpoints
    path('users/<int:pk>/', UserViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='user-detail'),
    
    # User activation endpoint
    path('users/<int:pk>/deactivate/', UserViewSet.as_view({
        'post': 'deactivate'
    }), name='user-deactivate'),
]
