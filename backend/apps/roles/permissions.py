from rest_framework import permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import RolePermission, Role
from .services import RolePermissionCache

class HasPermission(permissions.BasePermission):
    message = "Permission denied"
    def __init__(self, required_permission):
        self.required_permission = (
            required_permission.split(',')
            if isinstance(required_permission, str)
            else required_permission
            if isinstance(required_permission, list)
            else ['permission_dont_exist']
        )
        self.cache_service = RolePermissionCache()

    def has_permission(self, request, view):
        
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return False

            
            jwt_auth = JWTAuthentication()
            validated_token = jwt_auth.get_validated_token(auth_header.split(' ')[1])

            user = jwt_auth.get_user(validated_token)
            if not user.is_active:
                return False
            
            
            role_id = validated_token.get('role_id')
            if not role_id:
                return False
            
            return self.cache_service.has_permission(role_id, self.required_permission)

        except Exception:
            return False