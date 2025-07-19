from rest_framework_simplejwt.tokens import RefreshToken
from .models import Permission, RolePermission
from django.db import transaction

def get_tokens_for_user(user):
    """Generate JWT tokens with role information"""
    refresh = RefreshToken.for_user(user)
    
    # Add role information to the token
    if user.role:
        refresh['role_id'] = str(user.role.id)
        refresh['role_name'] = user.role.name
    
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def add_custom_permission(feature_name, permission_name, description=None):
    """
    Add a new custom permission
    
    Args:
        feature_name (str): Name of the feature (e.g., 'agents')
        permission_name (str): Name of the permission (e.g., 'export')
        description (str, optional): Description of the permission
    
    Returns:
        Permission: The created permission object
    """
    permission_code = f"{feature_name}_{permission_name}"
    
    with transaction.atomic():
        permission, created = Permission.objects.get_or_create(
            feature_name=feature_name,
            permission_name=permission_name,
            permission_code=permission_code,
            defaults={
                'description': description or f"Can {permission_name} {feature_name}"
            }
        )
        
        # Optionally add this permission to super admin role
        from .models import Role
        try:
            super_admin = Role.objects.get(name='Super Admin')
            RolePermission.objects.get_or_create(
                role=super_admin,
                permission=permission
            )
        except Role.DoesNotExist:
            pass
        
        return permission

def add_permissions_to_role(role, permission_codes):
    """
    Add multiple permissions to a role
    
    Args:
        role: Role object
        permission_codes (list): List of permission codes to add
    """
    with transaction.atomic():
        permissions = Permission.objects.filter(permission_code__in=permission_codes)
        for permission in permissions:
            RolePermission.objects.get_or_create(
                role=role,
                permission=permission
            )

# Usage examples:
"""
# Add a new permission
new_perm = add_custom_permission(
    'agents',
    'export',
    'Can export agents data'
)

# Add permissions to a role
add_permissions_to_role(
    role,
    ['agents_export', 'agents_import']
)
"""