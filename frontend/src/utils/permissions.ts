import { useAuthStore } from '@/stores/auth.store';

/**
 * Checks if the user has a specific permission
 * @param permission Permission to check
 * @returns True if the user has permission, false otherwise
 */
export function hasPermission(permission: string): boolean {
  const authStore = useAuthStore();
  return authStore.hasPermission(permission);
}

/**
 * Checks if the user has at least one of the specified permissions
 * @param permissions List of permissions to check
 * @returns True if the user has at least one of the permissions, false otherwise
 */
export function hasAnyPermission(permissions: string[]): boolean {
  const authStore = useAuthStore();
  return authStore.hasAnyPermission(permissions);
}

/**
 * Checks if the user has all the specified permissions
 * @param permissions List of permissions to check
 * @returns True if the user has all permissions, false otherwise
 */
export function hasAllPermissions(permissions: string[]): boolean {
  const authStore = useAuthStore();
  return authStore.hasAllPermissions(permissions);
}

/**
 * Entity-related permissions
 */
export const ENTITY_PERMISSIONS = {
  CREATE: 'entities_create',
  EDIT: 'entities_edit',
  DELETE: 'entities_delete',
  VIEW: 'entities_view',
};

/**
 * Create a View directive to control display based on permissions
 */
export const permissionDirective = {
  mounted(el: HTMLElement, binding: any) {
    const { value, modifiers } = binding;
    
    if (Array.isArray(value)) {
      const hasAccess = modifiers.all 
        ? hasAllPermissions(value)
        : hasAnyPermission(value);
      
      if (!hasAccess) {
        el.parentNode?.removeChild(el);
      }
    } 
    else if (typeof value === 'string') {
      if (!hasPermission(value)) {
        el.parentNode?.removeChild(el);
      }
    }
  }
};