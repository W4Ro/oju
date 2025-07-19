export interface LoginCredentials {
    email: string;
    password: string;
  }
  
  export interface AuthTokens {
    access: string;
    refresh: string;
  }
  
  export interface AuthResponse extends AuthTokens {
    permissions: string[];
  }
  
  export interface ResetPasswordRequest {
    email: string;
  }
  
  export interface VerifyTokenRequest {
    token: string;
  }
  
  export interface ResetPasswordConfirm {
    token: string;
    password: string;
    confirm_password: string;
  }
  
  export interface RegisterRequest {
    username: string;
    email: string;
    password: string;
    confirm_password: string;
    nom_prenom: string;
  }