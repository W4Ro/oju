import { defineStore } from 'pinia';
import { AuthService } from '@/services/auth.service';
import { UserService } from '@/services/user.service';
import { LoginCredentials, AuthResponse } from '@/types/auth.types';
import { User } from '@/types/user.types';
import router from '@/router';

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: User | null;
  permissions: string[];
  loading: boolean;
  error: string | null;
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    accessToken: localStorage.getItem('access_token'),
    refreshToken: localStorage.getItem('refresh_token'),
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    permissions: JSON.parse(localStorage.getItem('permissions') || '[]'),
    loading: false,
    error: null as string | null
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.accessToken && !!state.user,
    userPermissions: (state) => state.permissions,
    hasPermission: (state) => (permission: string) => state.permissions.includes(permission),
    hasAnyPermission: (state) => (permissions: string[]) => permissions.some(p => state.permissions.includes(p)),
    hasAllPermissions: (state) => (permissions: string[]) => permissions.every(p => state.permissions.includes(p))
  },
  
  actions: {
    /**
     * user login
     */
    async login(credentials: LoginCredentials) {
      try {
        this.loading = true;
        this.error = null;
        
        const authResponse: AuthResponse = await AuthService.login(credentials);
        
        localStorage.setItem('access_token', authResponse.access);
        localStorage.setItem('refresh_token', authResponse.refresh);
        localStorage.setItem('permissions', JSON.stringify(authResponse.permissions));
        
        this.accessToken = authResponse.access;
        this.refreshToken = authResponse.refresh;
        this.permissions = authResponse.permissions;
        
        await this.fetchCurrentUser();
        
        return true;
      } catch (error: any) {
        this.error = error.response?.data?.error || 'Error during login';
        return false;
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * fetch current user
     */
    async fetchCurrentUser() {
      try {
        this.loading = true;
        
        const user = await UserService.getCurrentUser();
        localStorage.setItem('user', JSON.stringify(user));
        this.user = user;
        localStorage.setItem('permissions', JSON.stringify(user.permissions));
        this.permissions = user.permissions || [];
        return user;
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * Refresh token
     */
    async refreshAccessToken() {
      if (!this.refreshToken) return false;
      
      try {
        const response = await AuthService.refreshToken(this.refreshToken);
        
        localStorage.setItem('access_token', response.access);
        this.accessToken = response.access;
        
        if (response.refresh) {
          localStorage.setItem('refresh_token', response.refresh);
          this.refreshToken = response.refresh;
        }
        
        if (response.permissions) {
          localStorage.setItem('permissions', JSON.stringify(response.permissions));
          this.permissions = response.permissions;
        }
        
        return true;
      } catch (error) {
        this.accessToken = null;
        this.refreshToken = null;
        this.user = null;
        this.permissions = [];
        return false;
      }
    },
    
    /**
     * Logout 
     */
    async logout() {
      try {
        if (this.accessToken) {
          await AuthService.logout();
        }
      } catch (error) {
        console.error('Error while logging out:', error);
      } finally {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        localStorage.removeItem('permissions');
        
        this.accessToken = null;
        this.refreshToken = null;
        this.user = null;
        this.permissions = [];
        
        router.push('/authentication/login');
      }
    },
    
    /**
     * Check if user is authenticated
     * @returns {boolean} true if authenticated, false otherwise
     */
    async checkAuth() {
      if (!this.accessToken) return false;
      
      try {
        await this.fetchCurrentUser();
        return true;
      } catch (error: any) {
        if (error.response?.status === 401) {
          const refreshed = await this.refreshAccessToken();
          if (refreshed) {
            try {
              await this.fetchCurrentUser();
              return true;
            } catch {
              return false;
            }
          }
        }
        return false;
      }
    },
    
    /**
     * new user registration
     * @param {Object} userData - User data for registration
     */
    async register(userData: any) {
      try {
        this.loading = true;
        this.error = null;
        
        const response = await AuthService.register(userData);
        return response;
      } catch (error: any) {
        this.error = error.response?.data?.error || 'Error during registration';
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * Ask for password reset
     * @param {string} email - User email for password reset
     */
    async requestPasswordReset(email: string) {
      try {
        this.loading = true;
        this.error = null;
        
        const response = await AuthService.requestPasswordReset({ email });
        return response;
      } catch (error: any) {
        this.error = error.response?.data?.error || 'Error while requesting password reset';
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * Confirm email address
     * @param {string} token - Confirmation token
     */
    async resetPassword(data: { token: string; password: string; confirm_password: string }) {
      try {
        this.loading = true;
        this.error = null;
        
        const response = await AuthService.resetPassword(data);
        return response;
      } catch (error: any) {
        this.error = error.response?.data?.error || 'Error resetting password';
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * Check if the reset token is valid
     * @param {string} token - Reset token
     */
    async verifyResetToken(token: string) {
      try {
        this.loading = true;
        const response = await AuthService.verifyResetToken({ token });
        return response;
      } catch (error: any) {
        this.error = error.response?.data?.error || 'Invalid reset token';
        throw error;
      } finally {
        this.loading = false;
      }
    }
  }
});