import os
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Poll, PollOption, Vote
from users.models import User
from .serializers import PollSerializer, PollOptionSerializer, VoteSerializer
from .permissions import IsOwnerOrAdmin, IsCreator, IsPollOwnerOrAdmin, AllowAny


# class ApiRootView(viewsets.ViewSet):
#     BASE_NAME = 'API Root'
#     BASE_URL = os.getenv('BASE_URL', 'https://liwomasjid.co.ke/')
#     """
#     API root view to list all available endpoints.
#     """
#     def list(self, request):
#         return Response({
#             'self': f'{self.BASE_URL}api/v1/',
#             'auth': f'{self.BASE_URL}api/v1/auth/',
#             'polls': f'{self.BASE_URL}api/v1/polls/',
#             'poll-options': f'{self.BASE_URL}api/v1/polls/{{poll_id}}/options/',
#             'votes': f'{self.BASE_URL}api/v1/polls/{{poll_id}}/votes/'
#         })
class PollViewSet(viewsets.ModelViewSet):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    
    def get_permissions(self):

        if  self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        elif self.action in ['create']:
            # print(f"Creating a poll isAuthenticated ${IsAuthenticated}")
            # permission_classes = [IsAuthenticated, IsCreator]
            permission_classes = [IsAuthenticated,]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        email = serializer.validated_data.get('user', {}).get('email', None)
        user_serializer = User.objects.filter(email=email).first() if email else None
        user_serializer = user_serializer if user_serializer else self.request.user
        # print(f"current user {user_serializer}")
        user = user_serializer if user_serializer else self.request.user
        # serializer.validated_data['user']
        # print(f"seralized data: {serializer.validated_data}")
        serializer.save(user=user)

class PollOptionViewSet(viewsets.ModelViewSet):
    serializer_class = PollOptionSerializer
    permission_classes = [IsAuthenticated, IsPollOwnerOrAdmin]
    
    def get_queryset(self):
        # return PollOption.objects.filter(poll_id=self.kwargs['poll_id'])
        poll_id = self.kwargs.get('id')
        if not poll_id:
            return PollOption.objects.none()
        return PollOption.objects.filter(poll_id=poll_id)

    def perform_create(self, serializer):
        poll = Poll.objects.get(id=self.kwargs['poll_id'])
        serializer.save(poll=poll)
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

class VoteViewSet(viewsets.ModelViewSet):
    serializer_class = VoteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Vote.objects.filter(option__poll_id=self.kwargs['poll_id'])
    
    def create(self, request, *args, **kwargs):
        poll_id = kwargs['poll_id']
        option_id = request.data.get('option_id')
        
        try:
            option = PollOption.objects.get(id=option_id, poll_id=poll_id)
            
            # Check for existing vote
            if Vote.objects.filter(
                user=request.user, 
                option__poll_id=poll_id
            ).exists():
                return Response(
                    {'error': 'You have already voted in this poll'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            Vote.objects.create(user=request.user, option=option)
            return Response({'status': 'Vote recorded'}, status=status.HTTP_201_CREATED)
        except PollOption.DoesNotExist:
            return Response({'error': 'Invalid option'}, status=status.HTTP_400_BAD_REQUEST)
