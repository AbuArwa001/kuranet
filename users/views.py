from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .models import User
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    # @action(detail=False, methods=['post'])
    # def register(self, request):
    #     serializer = UserSerializer(data=request.data)
    #     if serializer.is_valid():
    #         user = serializer.save()
    #         return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="register")
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def logout(self, request):
        # Optional: JWT doesn't manage logout server-side.
        return Response({"message": "Logged out."}, status=status.HTTP_200_OK)
