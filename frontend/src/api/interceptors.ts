import { AxiosInstance, AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios';
import { useAuthStore } from '@/stores/auth.store';
import router from '@/router';


function clearUserData(): void {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
  localStorage.removeItem('permissions');
}

export function setupInterceptors(api: AxiosInstance): void {
  api.interceptors.request.use(
    (config: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
      const token = localStorage.getItem('access_token');
      if (config.url?.includes('/refresh-token')) {
        return config;
      }
      
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      
      return config;
    },
    (error: AxiosError): Promise<AxiosError> => {
      return Promise.reject(error);
    }
  );
  
  api.interceptors.response.use(
    (response: AxiosResponse): AxiosResponse => {
      return response;
    },
    async (error: AxiosError): Promise<any> => {
      const originalRequest = error.config;
      
      if (!error.response) {
        return Promise.reject(error);
      }

      const isRefreshTokenRequest = originalRequest?.url?.includes('/refresh-token');
      
      
      if (
        error.response.status === 401 && 
        originalRequest && 
        !(originalRequest as any)._retry
      ) {
        (originalRequest as any)._retry = true;

        if (isRefreshTokenRequest) {
            const authStore = useAuthStore();
            authStore.logout();
            router.push('/authentication/login');
            return Promise.reject(error);
          }
        
        try {
          const authStore = useAuthStore();
          const refreshed = await authStore.refreshAccessToken();
          
          if (refreshed) {
            const token = localStorage.getItem('access_token');
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            
            return api(originalRequest);
          } else {
            clearUserData();
            router.push('/authentication/login');
            return Promise.reject(error);
          }
        } catch (refreshError) {
          clearUserData();
          router.push('/authentication/login');
          return Promise.reject(refreshError);
        }
      }
      
      return Promise.reject(error);
    }
  );
}