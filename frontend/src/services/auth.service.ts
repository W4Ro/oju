import api from '@/api/index';
import { 
  LoginCredentials, 
  AuthResponse, 
  RegisterRequest, 
  ResetPasswordRequest,
  ResetPasswordConfirm,
  VerifyTokenRequest
} from '@/types/auth.types';

export const AuthService = {
  /**
   * Connect an user
   * @param credentials - The login credentials of the user
   */
  login(credentials: LoginCredentials): Promise<AuthResponse> {
    return api.post('/users/auth/login/', credentials)
      .then(response => response.data);
  },
  
  /**
   * Logout an user
   * @param refreshToken - The refresh token of the user
   */
  logout(): Promise<void> {
    const refreshToken = localStorage.getItem('refresh_token');
    return api.post('/users/auth/logout/', { refresh: refreshToken })
        .then(() => undefined);
  },
  
  /**
   * refresh the access token using the refresh token
   * @param refreshToken - The refresh token of the user
   */
  refreshToken(refreshToken: string): Promise<AuthResponse> {
    return api.post('/users/auth/refresh-token/', { refresh: refreshToken })
      .then(response => response.data);
  },
  
  /**
   * Register a new user
   * @param userData - The data of the user to register
   */
  register(userData: RegisterRequest): Promise<any> {
    return api.post('/users/auth/register/', userData)
      .then(response => response.data);
  },
  
  /**
   * Ask for a password reset
   * @param data - The data to send to the server
   */
  requestPasswordReset(data: ResetPasswordRequest): Promise<any> {
    return api.post('/users/password/reset/request/', data)
      .then(response => response.data);
  },
  
  /**
   * verify the password reset token
   * @param data - The data to send to the server
   */
  verifyResetToken(data: VerifyTokenRequest): Promise<any> {
    return api.get('/users/password/reset/verify/', { params: data })
      .then(response => response.data);
  },
  
  /**
   * Confirm the password reset
   * @param data - The data to send to the server
   */
  resetPassword(data: ResetPasswordConfirm): Promise<any> {
    return api.post('/users/password/reset/', data)
      .then(response => response.data);
  }
};