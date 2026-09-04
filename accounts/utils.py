"""
Utility functions for accounts app.
"""

from django.contrib.auth.models import User

from .models import LoginAttempt


def get_client_ip(request):
    """
    Extract client IP address from request.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_login_attempt(request, email, status, method='password', failed_reason=''):
    """
    Log login attempt for security and analytics.
    """
    user = None
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        pass
    
    LoginAttempt.objects.create(
        user=user,
        email=email,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        status=status,
        method=method,
        failed_reason=failed_reason
    )


def is_ip_blocked(ip_address, attempts_threshold=10, time_window_minutes=15):
    """
    Check if IP address is blocked due to failed login attempts.
    """
    from django.utils import timezone
    from datetime import timedelta
    
    time_threshold = timezone.now() - timedelta(minutes=time_window_minutes)
    
    failed_attempts = LoginAttempt.objects.filter(
        ip_address=ip_address,
        status='failed',
        timestamp__gte=time_threshold
    ).count()
    
    return failed_attempts >= attempts_threshold


def is_user_locked(user, attempts_threshold=5, time_window_minutes=15):
    """
    Check if user account is locked due to failed login attempts.
    """
    from django.utils import timezone
    from datetime import timedelta
    
    time_threshold = timezone.now() - timedelta(minutes=time_window_minutes)
    
    failed_attempts = LoginAttempt.objects.filter(
        user=user,
        status='failed',
        timestamp__gte=time_threshold
    ).count()
    
    return failed_attempts >= attempts_threshold
