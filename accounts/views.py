"""
Views for accounts app.
"""

from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import UserProfile, OAuthToken, LoginAttempt
from .serializers import (
    UserSerializer,
    UserDetailSerializer,
    UserProfileSerializer,
    OAuthTokenSerializer,
    RegistrationSerializer
)
from .utils import get_client_ip


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User model."""
    
    queryset = User.objects.select_related('profile').all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update':
            return UserDetailSerializer
        return UserSerializer
    
    def get_queryset(self):
        """Return filtered queryset."""
        if self.request.user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(id=self.request.user.id)
    
    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        """Get current user profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(
        detail=False,
        methods=['post'],
        permission_classes=[AllowAny]
    )
    def register(self, request):
        """Register new user."""
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_serializer = UserSerializer(user)
            return Response(
                user_serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for UserProfile model."""
    
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return filtered queryset."""
        if self.request.user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(user=self.request.user)
    
    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        """Get current user profile."""
        try:
            profile = request.user.profile
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response(
                {'detail': 'Profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )


class OAuthTokenViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for OAuthToken model (read-only)."""
    
    queryset = OAuthToken.objects.all()
    serializer_class = OAuthTokenSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return filtered queryset."""
        if self.request.user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(user=self.request.user)
    
    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def providers(self, request):
        """Get list of connected OAuth providers."""
        tokens = self.get_queryset()
        providers = tokens.values_list('provider', flat=True).distinct()
        return Response({'providers': list(providers)})
