from django.core.cache import cache
from django.conf import settings
from .models import Role, RolePermission
import logging

logger = logging.getLogger(__name__)

class RolePermissionCache:
    """
    Service to manage the cache of roles and permissions
    """
    def __init__(self):
        self.cache_timeout = 3600

    def _build_role_cache_key(self, role_id):
        """Builds the cache key for a role"""
        return f"role_permissions_{role_id}"

    def _build_role_status_cache_key(self, role_id):
        """Builds the cache key for a role's status"""
        return f"role_active_{role_id}"

    def get_role_permissions(self, role_id):
        """
        Retrieves a role's permissions from the cache or database
        """
        cache_key = self._build_role_cache_key(role_id)
        
        
        permissions = cache.get(cache_key)
        
        if permissions is None:
            logger.debug(f"Cache miss for role {role_id}, fetching from database")
            try:
                
                role = Role.objects.filter(id=role_id).first()
                if not role:
                    logger.warning(f"Role {role_id} not found")
                    return None

                permissions = set(RolePermission.objects.filter(
                    role_id=role_id
                ).values_list('permission__permission_code', flat=True))

                cache.set(cache_key, permissions, self.cache_timeout)
                logger.info(f"Cache created for role {role_id} with {len(permissions)} permissions")
                
                status_cache_key = self._build_role_status_cache_key(role_id)
                cache.set(status_cache_key, role.is_active, self.cache_timeout)
                
            except Exception as e:
                logger.error(f"Error building cache for role {role_id}: {str(e)}")
                return None

        return permissions

    def is_role_active(self, role_id):
        """
        Checks if a role is active from the cache or database
        """
        cache_key = self._build_role_status_cache_key(role_id)
        
        is_active = cache.get(cache_key)
        
        if is_active is None:
            logger.debug(f"Status cache miss for role {role_id}, fetching from database")
            try:
                role = Role.objects.filter(id=role_id).first()
                if not role:
                    logger.warning(f"Role {role_id} not found when checking status")
                    return False
                    
                is_active = role.is_active
                cache.set(cache_key, is_active, self.cache_timeout)
                logger.info(f"Status cache created for role {role_id}: {is_active}")
                
            except Exception as e:
                logger.error(f"Error checking role status for {role_id}: {str(e)}")
                return False

        return is_active

    def invalidate_role_cache(self, role_id):
        """
        Invalidates the cache for a specific role
        """
        try:
            perm_cache_key = self._build_role_cache_key(role_id)
            status_cache_key = self._build_role_status_cache_key(role_id)
            
            cache.delete(perm_cache_key)
            cache.delete(status_cache_key)
            
            logger.info(f"Cache invalidated for role {role_id}")
            return True
        except Exception as e:
            logger.error(f"Error invalidating cache for role {role_id}: {str(e)}")
            return False

    def has_permission(self, role_id, required_permissions):
        """
        Checks if a role has the required permissions
        """
        try:
            
            if not self.is_role_active(role_id):
                logger.warning(f"Role {role_id} is inactive")
                return False

            role_permissions = self.get_role_permissions(role_id)
            if role_permissions is None:
                logger.warning(f"Could not get permissions for role {role_id}")
                return False

            
            if isinstance(required_permissions, str):
                required_permissions = [required_permissions]

            has_all_permissions = all(
                perm in role_permissions 
                for perm in required_permissions
            )
            
            logger.debug(
                f"Permission check for role {role_id}: "
                f"required={required_permissions}, "
                f"has_all={has_all_permissions}"
            )
            
            return has_all_permissions

        except Exception as e:
            logger.error(f"Error checking permissions for role {role_id}: {str(e)}")
            return False