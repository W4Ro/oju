import api from '@/api';
import type { Role, Permission, RoleCreate, RoleUpdate, PaginatedResponse } from '@/types/role.types';

const roleService = {
  /**
   * Get all roles with optional search and pagination
   * @param page Page number
   * @param search research term
   */
  getRoles(page = 1, search?: string): Promise<PaginatedResponse<Role>> {
    const params: any = { page };
    if (search) params.search = search;

    return api.get('/roles/', { params })
      .then(response => response.data)
      .catch(() => ({ count: 0, next: null, previous: null, results: [] }));
  },

  /**
   * Get role details by ID
   * @param id Role ID
   */
  getRoleById(id: string): Promise<Role | null> {
    return api.get(`/roles/${id}/`)
      .then(response => response.data)
      .catch(() => null);
  },

  /**
   * Get all permissions
   */
  getPermissions(): Promise<PaginatedResponse<Permission>> {
    return api.get('/roles/permissions/')
      .then(response => response.data)
      .catch(() => ({ count: 0, next: null, previous: null, results: [] }));
  },

  /**
   * Research roles by name
   * @param query Search term
   */
  searchRoles(query: string): Promise<Role[]> {
    return api.get(`/roles/search/`, { params: { query } })
      .then(response => response.data)
      .catch(() => []);
  },

  /**
   * Create a new role
   * @param roleData Data for the new role
   */
  createRole(roleData: RoleCreate): Promise<Role> {
    return api.post('/roles/', roleData)
      .then(response => response.data);
  },

  /**
   *Update an existing role
   * @param id role ID
   * @param roleData Data to update
   */
  updateRole(id: string, roleData: RoleUpdate): Promise<Role> {
    return api.put(`/roles/${id}/`, roleData)
      .then(response => response.data);
  },

  /**
   * Delete a role
   * @param id Role ID
   */
  deleteRole(id: string): Promise<boolean> {
    return api.delete(`/roles/${id}/`)
      .then(() => true);
  },

  /**
   * Toggle the status of a role (active/inactive)
   * @param id Role ID
   */
  toggleRoleStatus(id: string): Promise<{ success: boolean; is_active: boolean }> {
    return api.post(`/roles/${id}/toggle_status/`)
      .then(response => response.data);
  }
};

export default roleService;