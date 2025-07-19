// src/services/user.service.ts
import api from '@/api';
import type { User } from '@/types/user.types';

export const UserService = {
  /**
   * Fetch the current user profile
   * @returns {Promise<User>} - A promise that resolves to the current user's profile
   */
  getCurrentUser(): Promise<User> {
    return api.get('/users/me/')
      .then(response => response.data)
      .catch(error => {
        throw error;
      });
  },
  /**
 * Update the current user's profile
 * @param userData Profile data to be updated
 */
updateUserProfile(userData: Partial<User>): Promise<User> {
    return api.put('/users/update_profile/', userData)
      .then(response => response.data)
      .catch(error => {
        throw error;
      });
  },
  /**
 * Change the password of the logged in user
 * @param passwordData Password change data
 */
changePassword(passwordData: { old_password: string, new_password: string }): Promise<any> {
    return api.post('/users/change_password/', passwordData)
      .then(response => response.data)
      .catch(error => {
        throw error;
      });
  },

  /**
   * Retrieves the list of users with pagination
   * @param page Page number
   * @param search Optional search term
   */
  getUsers(page = 1, search?: string): Promise<{ users: User[], count: number }> {
    const params: any = { page };
    if (search) params.search = search;

    return api.get('/users/', { params })
      .then(response => ({
        users: response.data.results || response.data,
        count: response.data.count || response.data.length
      }))
      .catch(error => {
        return { users: [], count: 0 };
      });
  },

  /**
   * Retrieves a user by their ID
   * @param id User ID
   */
  getUserById(id: string): Promise<User | null> {
    return api.get(`/users/${id}/`)
      .then(response => response.data)
      .catch(error => {
        throw error;
      });
  },

  /**
   * Create a new user
   * @param userData User data to create
   */
  createUser(userData: Partial<User>): Promise<User | null> {
    return api.post('/users/', userData)
      .then(response => response.data)
      .catch(error => {
        throw error;
      });
  },

  /**
   * Updates a user
   * @param id User ID
   * @param userData Updated data
   */
  updateUser(id: string, userData: Partial<User>): Promise<User | null> {
    return api.put(`/users/${id}/`, userData)
      .then(response => response.data)
      .catch(error => {
        throw error;
      });
  },

  /**
   * Deletes a user
   * @param id User ID
   */
  deleteUser(id: string): Promise<boolean> {
    return api.delete(`/users/${id}/`)
      .then(() => true)
      .catch(error => {
        throw error;
      });
  },

  /**
   * Change the active status of a user
   * @param id User ID
   */
  toggleUserActive(id: string): Promise<User | null> {
    return api.get(`/users/${id}/toggle_active/`)
      .then(response => response.data.success)
      .catch(error => {
        throw error;
      });
  },

  /**
   * Retrieves all available roles
   */
  getRoles(): Promise<any[]> {
    return api.get('/roles/')
      .then(response => response.data.results)
      .catch(error => {
        return [];
      });
  }
};