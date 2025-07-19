import { defineStore } from 'pinia';
import { UserService } from '@/services/user.service';
import type { User, UserFilters } from '@/types/user.types';

interface UserState {
  users: User[];
  currentUser: User | null;
  loading: boolean;
  error: string | null;
  totalUsers: number;
  currentPage: number;
  hasMoreData: boolean;
  userIdMap: Map<string, number>;
  nextNumericId: number;
  availableRoles: any[];
  filters: UserFilters;
  toast: {
    show: boolean;
    message: string;
    type: 'success' | 'error' | 'warning' | 'info';
    duration: number;
  };
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    users: [],
    currentUser: null,
    loading: false,
    error: null,
    totalUsers: 0,
    currentPage: 1,
    hasMoreData: true,
    userIdMap: new Map<string, number>(),
    nextNumericId: 1,
    availableRoles: [],
    filters: {
      searchTerm: "",
      status: "",
      role: "",
      ordering: "created_at",
    },
    toast: {
        show: false,
        message: '',
        type: 'success',
        duration: 3000
      }
  }),

  getters: {
    filteredUsers: (state) => {
      return state.users.filter(user => {
        if (state.filters.searchTerm) {
          const term = state.filters.searchTerm.toLowerCase();
          const matchesSearch = user.nom_prenom.toLowerCase().includes(term) || 
                             user.username.toLowerCase().includes(term) || 
                             user.email.toLowerCase().includes(term);
          if (!matchesSearch) return false;
        }
        
        if (state.filters.status !== "") {
          const activeStatus = state.filters.status === "true";
          if (user.is_active !== activeStatus) return false;
        }
        
        if (state.filters.role && state.filters.role !== "") {
            const userRole = user.role_name || user.role;
            if (!userRole || userRole !== state.filters.role) return false;
        }
        
        return true;
      });
    },

    paginatedUsers: (state) => (page: number, itemsPerPage: number) => {
      const start = (page - 1) * itemsPerPage;
      const end = start + itemsPerPage;
      return useUserStore().filteredUsers.slice(start, end);
    },

    getUserDisplayId: (state) => (uuid: string) => {
      if (!state.userIdMap.has(uuid)) {
        state.userIdMap.set(uuid, state.nextNumericId++);
      }
      return state.userIdMap.get(uuid);
    }
  },

  actions: {
    resetFilters() {
      this.filters = {
        searchTerm: "",
        status: "",
        role: "",
        ordering: "created_at"
      };
    },
    /**
   * Display a toast message
   * @param message - Message to display
   */
  showToast(message: string, type: 'success' | 'error' | 'warning' | 'info' = 'success', duration = 3000) {
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

    /**
     * Loads users from the API
     */
    async fetchUsers(page = 1) {
      this.loading = true;
      this.error = null;
      
      try {
        if (page === 1) {
          this.userIdMap.clear();
          this.nextNumericId = 1;
        }
        
        const result = await UserService.getUsers(page);
        
        if (page === 1) {
          this.users = result.users;
        } else {
          this.users = [...this.users, ...result.users];
        }
        
        this.totalUsers = result.count;
        this.currentPage = page;
        this.hasMoreData = (this.users.length < this.totalUsers);
        
        result.users.forEach(user => {
          if (!this.userIdMap.has(user.id)) {
            this.userIdMap.set(user.id, this.nextNumericId++);
          }
        });
        
        return result.users;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error loading users';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        return [];
      } finally {
        this.loading = false;
      }
    },

    /**
     * Load more users when scrolling
     * @returns {Promise<User[]>} - Returns the next page of users
     */
    async loadMoreUsers() {
      if (!this.hasMoreData || this.loading) return [];
      
      const nextPage = this.currentPage + 1;
      return this.fetchUsers(nextPage);
    },

    /**
     * Fetches available roles from the API
     * @returns {Promise<any[]>} - Returns the list of available roles
     */
    async fetchRoles() {
      this.loading = true;
      
      return UserService.getRoles()
        .then(roles => {
          this.availableRoles = roles;
          return roles;
        })
        .catch((error: any) => {
          this.error = error.response?.data?.error || 'Error loading roles';
          return [];
        })
        .finally(() => {
          this.loading = false;
        });
    },

    /**
     * Fetches a user by ID from the API
     * @param id - User ID
     */
    async fetchUserById(id: string) {
      this.loading = true;
      this.error = null;
      
      return UserService.getUserById(id)
        .then(user => {
          if (user) {
            this.currentUser = user;
            
            const index = this.users.findIndex(u => u.id === id);
            if (index !== -1) {
              this.users[index] = user;
            } else {
              this.users.push(user);
            }
          }
          
          return user;
        })
        .catch((error: any) => {
          const errorMessage = error.response?.data?.error || `Error loading user ${id}`;
          this.error = errorMessage;
          this.showToast(errorMessage, 'error');
          return null;
        })
        .finally(() => {
          this.loading = false;
        });
    },

    /**
     * Deletes a user by ID from the API
     * @param id - User ID
     */
    async deleteUser(id: string) {
      this.loading = true;
      this.error = null;
      
      return UserService.deleteUser(id)
        .then(success => {
          if (success) {
            this.users = this.users.filter(u => u.id !== id);
            this.totalUsers--;
          }
          this.showToast(
            `User with ID: ${id} has been successfully deleted.`, 
            'success'
          );
          return success;
        })
        .catch((error: any) => {
          const errorMessage = error.response?.data?.error || `Error deleting user ${id}`;
          this.error = errorMessage;
          this.showToast(errorMessage, 'error');
          return false;
        })
        .finally(() => {
          this.loading = false;
        });
    },

    /**
     * Toggles a user's status
     */
    async toggleUserStatus(id: string) {
      this.loading = true;
      this.error = null;

      const userIndex = this.users.findIndex(u => u.id === id);
        if (userIndex === -1) {
        this.showToast(`User not found`, 'error');
        this.loading = false;
        return null;
        }
        const user = this.users[userIndex];
        const newStatus = !user.is_active;
      return UserService.toggleUserActive(id)
        .then(updatedUser => {
            if (updatedUser) {
                this.users[userIndex] = {
                  ...this.users[userIndex],
                  ...updatedUser,
                  is_active: newStatus 
                };
                
                this.showToast(
                  `The status of ${this.users[userIndex].nom_prenom} has been successfully ${newStatus ? 'activated' : 'disabled'}.`, 
                  'success'
                );
                return this.users[userIndex];
              } else {
                throw new Error("Status update failed");
              }
        })
        .catch((error: any) => {
            const errorMessage = error.response?.data?.error || `Error changing status: ${error.message || error}`;
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        return null;
        })
        .finally(() => {
          this.loading = false;
        });
    },
    /**
 * Update existing user data
 * @param id User ID
 * @param userData Updated data
 */
async updateUser(id: string, userData: Partial<User>) {
    this.loading = true;
    this.error = null;
    
    return UserService.updateUser(id, userData)
      .then(updatedUser => {
        if (updatedUser) {
          const index = this.users.findIndex(u => u.id === id);
          if (index !== -1) {
            this.users[index] = updatedUser;
          } else {
            this.users.push(updatedUser);
          }
          
          this.showToast(`L'user ${updatedUser.nom_prenom} has been successfully updated.`, 'success');
        }
        
        return updatedUser;
      })
      .catch((error: any) => {
        const errorMessage = error.response?.data?.error || `Error updating user ${id}`;
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        return null;
      })
      .finally(() => {
        this.loading = false;
      });
  },
  /**
 * Create a new user
 * @param userData User data to create
 */
async createUser(userData: Partial<User>) {
    this.loading = true;
    this.error = null;
    
    return UserService.createUser(userData)
      .then(createdUser => {
        if (createdUser) {
          this.users.unshift(createdUser);
          this.showToast(`User ${createdUser.nom_prenom} was successfully created.`, 'success');
        }
        
        return createdUser;
      })
      .catch((error: any) => {
        const errorMessage = error.response?.data?.error || 'Error creating user';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        return null;
      })
      .finally(() => {
        this.loading = false;
      });
  },
  /**
 * Retrieves the profile of the logged in user
 */
async fetchUserProfile() {
    this.loading = true;
    this.error = null;
    
    try {
      const profile = await UserService.getCurrentUser();
      this.currentUser = profile;
      return profile;
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || 'Error retrieving profile';
      this.error = errorMessage;
      this.showToast(errorMessage, 'error');
      throw error;
    } finally {
      this.loading = false;
    }
  },
  
  /**
   *Updates the user's profile
   * @param userData Profile data to be updated
   */
  async updateUserProfile(userData: Partial<User>) {
    this.loading = true;
    this.error = null;
    
    try {
      const updatedProfile = await UserService.updateUserProfile(userData);
      
      if (updatedProfile) {
        this.currentUser = updatedProfile;
        
        const index = this.users.findIndex(u => u.id === updatedProfile.id);
        if (index !== -1) {
          this.users[index] = updatedProfile;
        }
        
        this.showToast('Profile successfully updated', 'success');
      }
      
      return updatedProfile;
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || 'Error updating profile';
      this.error = errorMessage;
      this.showToast(errorMessage, 'error');
      throw error;
    } finally {
      this.loading = false;
    }
  },
  /**
     * Change the user's password
     * @param passwordData Password change data
     */
    async changePassword(passwordData: { old_password: string, new_password: string }) {
        this.loading = true;
        this.error = null;
        
        try {
        const response = await UserService.changePassword(passwordData);
        this.showToast('Password changed successfully', 'success');
        return response;
        } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error changing password';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        throw error;
        } finally {
        this.loading = false;
        }
    }
  }
});