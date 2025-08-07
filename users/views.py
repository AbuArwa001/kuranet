from rest_framework import viewsets, status, permissions
from users.permissions import IsOwnerOrAdmin, IsCreator, IsPollOwnerOrAdmin, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .models import User
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = []
    
    def get_permissions(self):
        if self.action in ['retrieve']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update']:
            return [IsOwnerOrAdmin()]
        elif self.action == 'list':
            return [permissions.IsAuthenticated()]
        elif self.action in ['destroy', 'deactivate']:
            return [IsOwnerOrAdmin()]
        return super().get_permissions()
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'status': 'user deactivated'}, status=status.HTTP_200_OK)

class AuthViewSet(viewsets.ViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            print(serializer.validated_data)
            user = serializer.save()
            return Response(user.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        # JWT is stateless, so client-side token invalidation
        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
