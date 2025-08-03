from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, AuthViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'auth', AuthViewSet, basename='auth')

urlpatterns = [
    path('', include(router.urls)),
    
    # SimpleJWT endpoints
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Browsable API login/logout
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
