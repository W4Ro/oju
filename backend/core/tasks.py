from celery import shared_task
import logging
from django.utils import timezone
from datetime import timedelta


logger = logging.getLogger(__name__)

@shared_task
def cleanup_blacklisted_tokens():
    """
    Task to clean expired blacklisted tokens and password reset requests
    """
    try:
        from apps.users.models import BlacklistedToken, PasswordReset
        cutoff_date = timezone.now() - timedelta(days=30)
        deleted_tokens = BlacklistedToken.objects.filter(
            blacklisted_at__lt=cutoff_date
        ).exclude(token='ALL').delete()[0]
        
        expired_resets = PasswordReset.objects.filter(
            expires_at__lt=timezone.now(),
            is_used=False
        ).delete()[0]
        
        return f"Cleaned up {deleted_tokens} blacklisted tokens and {expired_resets} password reset requests"
    except Exception as e:
        raise