"""
URL configuration for accounts app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, UserProfileViewSet, OAuthTokenViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'profiles', UserProfileViewSet, basename='profile')
router.register(r'oauth-tokens', OAuthTokenViewSet, basename='oauth-token')

urlpatterns = [
    path('', include(router.urls)),
]
