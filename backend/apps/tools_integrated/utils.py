import logging
from functools import wraps
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def rate_limit_refresh(timeout_seconds=3600):
    """
    Decorator to limit the call of a function to once per hour
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            cache_key = f"refresh_cerebrate_ratelimit"
            last_call = cache.get(cache_key)
            
            if last_call:
                time_since_last_call = datetime.now() - datetime.fromisoformat(last_call)
                time_remaining = timeout_seconds - time_since_last_call.total_seconds()
                
                if time_remaining > 0:
                    minutes_remaining = int(time_remaining // 60)
                    seconds_remaining = int(time_remaining % 60)
                    
                    logger.warning(f"Rate limit hit for Cerebrate refresh. Next refresh available in {minutes_remaining}m {seconds_remaining}s")
                    
                    return Response({
                        "error": f"Please wait {minutes_remaining} minute(s) & {seconds_remaining} seconde(s) before refresh the page",
                        "next_refresh_available_in_seconds": int(time_remaining)
                    }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            cache.set(cache_key, datetime.now().isoformat(), timeout_seconds)
            logger.info("Cerebrate refresh initiated")
            
            return func(self, request, *args, **kwargs)
        return wrapper
    return decorator