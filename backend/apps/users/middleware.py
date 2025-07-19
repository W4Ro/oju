from django.http import JsonResponse
from rest_framework import status
import logging
from typing import Tuple, Optional
from rest_framework_simplejwt.tokens import AccessToken
from django.utils import timezone
from .models import BlacklistedToken
import datetime
from django.core.cache import cache

# logger = logging.getLogger(__name__)
logger = logging.getLogger('django.request')

class TokenValidationMiddleware:
    """Middleware to validate JWT tokens"""
    PUBLIC_PATHS = {
        '/api/users/auth/login/',
        '/api/users/auth/register/',
        '/api/users/password/reset/request/',
        '/api/users/password/reset/verify/',
        '/api/users/password/reset/',
        '/api/users/auth/refresh-token/',
    }
    BLACKLIST_CACHE_TTL = 60 * 60 * 3
    def __init__(self, get_response):
        self.get_response = get_response

    def _is_token_blacklisted(self, token: str, user_id: str, iat_timestamp: float) -> bool:
        """Check if a token is blacklisted"""

        is_blacklisted = False

        cache_key = f"blacklist_{user_id}_{token}"
        cache_result = cache.get(cache_key)
        if cache_result:
            return True
        
        direct_blacklist_entry = BlacklistedToken.objects.filter(
            token=token,
            user_id=user_id
        ).exists()
        if direct_blacklist_entry:
            is_blacklisted = True
        else:
            all_blacklist_entry = BlacklistedToken.objects.filter(
                token='ALL',
                user_id=user_id
            ).order_by('-blacklisted_at').first()

            if all_blacklist_entry:
                iat_datetime = datetime.datetime.fromtimestamp(iat_timestamp, tz=timezone.get_current_timezone())

                is_blacklisted = all_blacklist_entry.blacklisted_at > iat_datetime
            
        cache.set(cache_key, is_blacklisted, self.BLACKLIST_CACHE_TTL)
        return is_blacklisted

    def _validate_token(self, token: str) -> Tuple[bool, Optional[str], Optional[dict]]:
        """Validate the JWT token"""
        """Returns a tuple (is_valid, error_message, token_data)"""
        try:
 
            token_obj = AccessToken(token)
            user_id = str(token_obj.get('user_id'))

            if 'exp' not in token_obj or token_obj['exp'] < timezone.now().timestamp():
                return False, "Token expired", None
            
            if 'iat' not in token_obj:
                return False, "Token invalide", None

            if self._is_token_blacklisted(token, user_id, token_obj['iat']):
                return False, "Token blacklisted", None
            
            return True, None, token_obj

        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return False, "Token invalide", None

    def log_request(self, request, response):
        """Log every HTTP request"""
        ip = self.get_client_ip(request)
        try:
            user = request.user if request.user.is_authenticated else "-"
        except Exception:
            user = "-"
        now = datetime.datetime.now().strftime('%d/%b/%Y:%H:%M:%S %z')
        method = request.method
        path = request.get_full_path()
        protocol = request.META.get("SERVER_PROTOCOL", "HTTP/1.1")
        status_code = response.status_code
        content_length = response.get("Content-Length", "-")
        referer = request.META.get("HTTP_REFERER", "-")
        user_agent = request.META.get("HTTP_USER_AGENT", "-")

        log_entry = f'{ip} - {user} [{now}] "{method} {path} {protocol}" {status_code} {content_length} "{referer}" "{user_agent}"'
        logger.info(log_entry)

    def get_client_ip(self, request):
        """Retrieves the client's IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def _check_rate_limit(self, request, user_id):
        """Simple rate limiting"""
        if not user_id:
            return False
            
        current_minute = int(timezone.now().timestamp() / 60)
        cache_key = f"ratelimit_{user_id}_{current_minute}"
        
        count = cache.get(cache_key, 0)
        if count >= 60:
            return True
            
        cache.set(cache_key, count + 1, 60)
        return False

    def __call__(self, request):
            
        try:
    
            if not request.path.startswith('/api/') or request.path in self.PUBLIC_PATHS:
                response = self.get_response(request)
                return response
            

            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                response = JsonResponse(
                    {'error': 'Auth token required'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
                return response

            token = auth_header.split(' ')[1]
            is_valid, error_message, token_data = self._validate_token(token)

            if not is_valid:
                response = JsonResponse(
                    {'error': error_message},
                    status=status.HTTP_401_UNAUTHORIZED
                )
                return response

            if self._check_rate_limit(request, token_data.get('user_id')):
                return JsonResponse(
                    {'error': 'Rate limit exceeded'}, 
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

            request.token_data = token_data

            response = self.get_response(request)
            self.log_request(request, response)
            return response
        except Exception as e:
            logger.error(f"Middleware error: {str(e)}", exc_info=True)
            response= JsonResponse(
                {'error': 'Server Error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            return response
        finally:
            if response:
                self.log_request(request, response)