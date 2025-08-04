from django.urls import include, path
from .views import PollViewSet

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"polls", PollViewSet, basename="poll")

urlpatterns = [
    path("", include(router.urls)),
]
