from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PollViewSet, PollOptionViewSet, VoteViewSet

# Create a router for polls
polls_router = DefaultRouter()
polls_router.register(r'', PollViewSet, basename='poll')

urlpatterns = [
    # Poll endpoints: /api/v1/polls/
    # path('', ApiRootView.as_view({'get': 'list'}), name='api-root'),
    path("", include(polls_router.urls)),

    # Nested options: /api/v1/polls/<poll_id>/options/
    path(
        '<int:poll_id>/options/',
        PollOptionViewSet.as_view({
            'get': 'list',
            'post': 'create'
        }),
        name='poll-options'
    ),
    
    # Single option: /api/v1/polls/<poll_id>/options/<id>/
    path(
        '<int:poll_id>/options/<int:pk>/',
        PollOptionViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy'
        }),
        name='poll-option-detail'
    ),
    
    # Voting endpoints: /api/v1/polls/<poll_id>/votes/
    path(
        '<int:poll_id>/votes/',
        VoteViewSet.as_view({
            'get': 'list',
            'post': 'create'
        }),
        name='poll-votes'
    ),
]
