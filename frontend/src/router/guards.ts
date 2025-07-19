import { RouteLocationNormalized, NavigationGuardNext } from 'vue-router';
import { useAuthStore } from '@/stores/auth.store';

/**
 *Guard for verifying authentication and authorization
 */
export async function authGuard(
    to: RouteLocationNormalized,
    from: RouteLocationNormalized,
    next: NavigationGuardNext
  ) {
    const authStore = useAuthStore();

    if (to.name === '/authentication/logout') {
        await authStore.logout();
        return next({ 
            path: '/authentication/login',
            replace: true 
        });
    }
    
    if (to.matched.some(record => record.meta.requiresAuth)) {
      const isAuthenticated = await authStore.checkAuth();
      
      if (!isAuthenticated) {
        return next({
          path: '/authentication/login',
          query: { redirect: to.fullPath }
        });
      }
    }
    
    if (to.matched.some(record => record.meta.guest) && authStore.isAuthenticated) {
      return next({ path: '/dashboard' });
    }
    
    next();
  }

/**
 * Guard for verifying permissions
 */
export function permissionGuard(requiredPermissions: string[] = []) {
  return (
    to: RouteLocationNormalized, 
    from: RouteLocationNormalized, 
    next: NavigationGuardNext
  ) => {
    if (requiredPermissions.length === 0) {
      return next();
    }
    
    const authStore = useAuthStore();
    
    const hasAccess = requiredPermissions.every(permission => 
      authStore.hasPermission(permission)
    );
    
    if (!hasAccess) {
      return next({ name: 'forbidden' });
    }
    
    next();
  };
}