from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.decorators import method_decorator
from .models import Role, RolePermission

def has_permission(permission_code):
    """
    Decorator to check if user has specific permission
    Usage: @has_permission('agents_create')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            try:
                # Validate JWT token
                auth_header = request.headers.get('Authorization', '')
                if not auth_header.startswith('Bearer '):
                    return Response(
                        {"error": "Invalid authentication header"},
                        status=status.HTTP_401_UNAUTHORIZED
                    )

                # Get and validate token
                jwt_auth = JWTAuthentication()
                validated_token = jwt_auth.get_validated_token(auth_header.split(' ')[1])
                user = jwt_auth.get_user(validated_token)

                # Check if user is active
                if not user.is_active:
                    return Response(
                        {"error": "User account is inactive"},
                        status=status.HTTP_403_FORBIDDEN
                    )

                # Get role ID from token
                role_id = validated_token.get('role_id')
                if not role_id:
                    return Response(
                        {"error": "No role assigned"},
                        status=status.HTTP_403_FORBIDDEN
                    )

                # Check permissions
                has_perm = RolePermission.objects.filter(
                    role_id=role_id,
                    permission__permission_code=permission_code
                ).exists()

                if not has_perm:
                    return Response(
                        {"error": "Permission denied"},
                        status=status.HTTP_403_FORBIDDEN
                    )

                return view_func(request, *args, **kwargs)

            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_401_UNAUTHORIZED
                )

        return wrapper
    return decorator
