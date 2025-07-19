import { jwtDecode } from 'jwt-decode';

interface DecodedToken {
  token_type: string;
  exp: number;
  iat: number;
  jti: string;
  user_id: string;
  role_id: string;
}

/**
 * Decode a JWT token
 */
export function decodeToken(token: string): DecodedToken | null {
  try {
    return jwtDecode(token);
  } catch (error) {
    return null;
  }
}

/**
 * Check if a token is expired
 */
export function isTokenExpired(token: string): boolean {
  const decoded = decodeToken(token);
  if (!decoded) return true;
  
  const currentTime = Date.now() / 1000;
  return decoded.exp < currentTime;
}

/**
 * Extract user ID from a token
 */
export function getUserIdFromToken(token: string): string | null {
  const decoded = decodeToken(token);
  return decoded ? decoded.user_id : null;
}

/**
 * Extract the role ID from a token
 */
export function getRoleIdFromToken(token: string): string | null {
  const decoded = decodeToken(token);
  return decoded ? decoded.role_id : null;
}

/**
 * Get the time remaining before expiration (in seconds)
 */
export function getTokenRemainingTime(token: string): number {
  const decoded = decodeToken(token);
  if (!decoded) return 0;
  
  const currentTime = Date.now() / 1000;
  return Math.max(0, decoded.exp - currentTime);
}