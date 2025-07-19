import logging
from functools import wraps
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def rate_limit_mail_config(max_attempts=2, timeout_seconds=60):
    """
    Decorator to limit attempts to modify mail configuration

    Args:
        max_attempts (int): Maximum number of attempts allowed in the interval
        timeout_seconds (int): Interval in seconds for throttling
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            user_id = request.user.id if request.user.is_authenticated else 'anonymous'
            cache_key = f"mail_config_ratelimit_{user_id}"
            
            attempts = cache.get(cache_key, {"count": 0, "first_attempt": None})
            
            now = datetime.now()
            if attempts["count"] == 0:
                attempts = {
                    "count": 1,
                    "first_attempt": now.isoformat()
                }
                cache.set(cache_key, attempts, timeout_seconds)
                logger.info(f"Mail config update attempt from user {request.user.username}")
                return func(self, request, *args, **kwargs)
            
            time_since_first = now - datetime.fromisoformat(attempts["first_attempt"])
            time_remaining = timeout_seconds - time_since_first.total_seconds()
            
            if time_remaining <= 0:
                attempts = {
                    "count": 1,
                    "first_attempt": now.isoformat()
                }
                cache.set(cache_key, attempts, timeout_seconds)
                logger.info(f"Reset mail config attempts for user {request.user.username}")
                return func(self, request, *args, **kwargs)
            
            if attempts["count"] >= max_attempts:
                minutes_remaining = int(time_remaining // 60)
                seconds_remaining = int(time_remaining % 60)
                
                logger.warning(f"Rate limit exceeded for mail config from IP ")# {ip}")
                
                return Response({
                    "error": f"Too many attempts. Please wait {minutes_remaining} minute(s) and {seconds_remaining} second(s)",
                    "next_attempt_allowed_in_seconds": int(time_remaining)
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            

            attempts["count"] += 1
            cache.set(cache_key, attempts, timeout_seconds)
            
            logger.info(f"Mail config attempt {attempts['count']}/{max_attempts} from user {request.user.username}")
            return func(self, request, *args, **kwargs)
            
        return wrapper
    return decorator