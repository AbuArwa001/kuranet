from django.urls import path
from .views import PollCreateView, PollListView, PollDetailView

urlpatterns = [
    path('polls/', PollListView.as_view(), name='poll-list'),
    path('polls/create/', PollCreateView.as_view(), name='poll-create'),
    path('polls/<int:pk>/', PollDetailView.as_view(), name='poll-detail'),
]
