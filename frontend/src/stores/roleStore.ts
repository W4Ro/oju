import { defineStore } from 'pinia';
import roleService from '@/services/roleService';
import type { Role, Permission } from '@/types/role.types';

export const useRoleStore = defineStore('role', {
  state: () => ({
    roles: [] as Role[],
    currentRole: null as Role | null,
    permissions: [] as Permission[],
    loading: false,
    error: null as string | null,
    isCreating: false,
    isUpdating: false,
    isDeleting: false,
    currentPage: 1,
    totalPages: 1,
    hasMoreData: true,
    searchQuery: '',
    toast: {
      show: false,
      message: '',
      type: 'success' as 'success' | 'error' | 'warning',
      duration: 3000
    }
  }),

  getters: {
    sortedRoles: (state) => {
      return [...state.roles].sort((a, b) => {
        const dateA = new Date(a.updated_at);
        const dateB = new Date(b.updated_at);
        return dateB.getTime() - dateA.getTime();
      });
    },

    getRoleById: (state) => (id: string) => {
      return state.roles.find(role => role.id === id) || null;
    },

    roleCount: (state) => {
      return state.roles.length;
    }
  },

  actions: {
    showToast(message: string, type: 'success' | 'error' | 'warning' = 'success', duration = 3000) {
      const safeMessage = message || 'An error occurred';
      this.toast = {
        show: true,
        message: safeMessage,
        type,
        duration
      };
      
      setTimeout(() => {
        this.toast.show = false;
      }, duration);
    },

fetchRoles(page = 1, search = ''): Promise<Role[]> {
    this.loading = true;
    this.error = null;
    
    if (page === 1 || search !== this.searchQuery) {
      this.roles = [];
      this.hasMoreData = true;
      this.searchQuery = search;
    }
    
    return roleService.getRoles(page, search)
      .then(response => {
        const { count, next, results } = response;
        
        this.totalPages = Math.ceil(count / 10); 
        this.hasMoreData = !!next;
        
        if (results.length === 0) {
          this.hasMoreData = false;
        } else {
          const existingIds = new Set(this.roles.map(r => r.id));
          const newRoles = results.filter((r: Role) => !existingIds.has(r.id));
          this.roles = [...this.roles, ...newRoles];
          this.currentPage = page;
        }
        
        return this.roles;
      })
      .catch((error: any) => {
        const errorMessage = error.response?.data?.error || 'Error loading roles';
        this.showToast(errorMessage, 'error');
        return [] as Role[];
      })
      .finally(() => {
        this.loading = false;
      });
  },

    async loadMoreRoles() {
      if (!this.hasMoreData || this.loading) return;
      
      const nextPage = this.currentPage + 1;
      await this.fetchRoles(nextPage, this.searchQuery);
    },

    fetchRoleById(id: string): Promise<Role | null> {
      this.loading = true;
      this.error = null;
      
      return roleService.getRoleById(id)
        .then(role => {
          if (role) {
            this.currentRole = role;
            
            const index = this.roles.findIndex(r => r.id === id);
            if (index !== -1) {
              this.roles[index] = role;
            } else {
              this.roles.push(role);
            }
          }
          
          return role;
        })
        .catch((error: any) => {
          const errorMessage = error.response?.data?.error || `Error while loading role with id: ${id}`;
          this.showToast(errorMessage, 'error');
          return null;
        })
        .finally(() => {
          this.loading = false;
        });
    },

    fetchPermissions(): Promise<Permission[]> {
        this.loading = true;
        this.error = null;
        
        return roleService.getPermissions()
          .then(response => {
            const { results } = response;
            
            this.permissions = Array.isArray(results) ? results : [];
            return this.permissions;
          })
          .catch((error: any) => {
            const errorMessage = error.response?.data?.error || 'Error loading permissions';
            this.showToast(errorMessage, 'error');
            this.permissions = [];
            return [] as Permission[];
          })
          .finally(() => {
            this.loading = false;
          });
      },

    searchRoles(query: string): Promise<Role[]> {
      this.loading = true;
      this.error = null;
      
      return roleService.searchRoles(query)
        .then(roles => {
          if (roles.length > 0) {
            this.roles = roles;
          }
          return roles;
        })
        .catch((error: any) => {
          const errorMessage = error.response?.data?.error || 'Error loading roles';
          this.showToast(errorMessage, 'error');
          return [] as Role[];
        })
        .finally(() => {
          this.loading = false;
        });
    },

    createRole(roleData: Partial<Role>): Promise<Role | null> {
      this.isCreating = true;
      this.error = null;
      
      return roleService.createRole({
        name: roleData.name || '',
        description: roleData.description,
        is_active: roleData.is_active || false,
        permissions: roleData.permissions || []
      })
        .then(createdRole => {
          this.roles.unshift(createdRole);
          this.showToast('Role created successfully', 'success');
          return createdRole;
        })
        .catch((error: any) => {
          const message = error.response?.data?.error || 'Error creating role';
          this.error = message;
          this.showToast(message, 'error');
          return null;
        })
        .finally(() => {
          this.isCreating = false;
        });
    },

    updateRole(id: string, roleData: Partial<Role>): Promise<Role | null> {
      this.isUpdating = true;
      this.error = null;
      
      return roleService.updateRole(id, {
        name: roleData.name || '',
        description: roleData.description,
        is_active: roleData.is_active || false,
        permissions: roleData.permissions || []
      })
        .then(updatedRole => {
          const index = this.roles.findIndex(r => r.id === id);
          if (index !== -1) {
            this.roles[index] = updatedRole;
          }
          
          this.showToast('Role updated successfully', 'success');
          return updatedRole;
        })
        .catch((error: any) => {
          const message = error.response?.data?.error || `Error updating role ${id}`;
          this.error = message;
          this.showToast(message, 'error');
          return null;
        })
        .finally(() => {
          this.isUpdating = false;
        });
    },

    deleteRole(id: string): Promise<boolean> {
      this.isDeleting = true;
      this.error = null;
      
      return roleService.deleteRole(id)
        .then(success => {
          if (success) {
            this.roles = this.roles.filter(r => r.id !== id);
            this.showToast('Role deleted successfully', 'success');
          }
          
          return success;
        })
        .catch((error: any) => {
          const message = error.response?.data?.error || `Error deleting role with id: ${id}`;
          this.error = message;
          this.showToast(message, 'error');
          return false;
        })
        .finally(() => {
          this.isDeleting = false;
        });
    },

    toggleRoleStatus(id: string): Promise<boolean> {
      this.loading = true;
      this.error = null;
      
      return roleService.toggleRoleStatus(id)
        .then(response => {
          if (response.success) {
            const index = this.roles.findIndex(r => r.id === id);
            if (index !== -1) {
              this.roles[index].is_active = response.is_active;
            }
            
            this.showToast(`Role status ${response.is_active ? 'activated' : 'deactivated'} successfully`, 'success');
          }
          return response.success;
        })
        .catch((error: any) => {
          const message = error.response?.data?.error || `Error while updating role ${id} status`;
          this.showToast(message, 'error');
          return false;
        })
        .finally(() => {
          this.loading = false;
        });
    }
  }
});