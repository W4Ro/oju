import { defineStore } from 'pinia';
import { Defacement, DefacementDetail, DefacementFilters, PaginatedDefacements } from '@/types/defacement.types';
import { DefacementService } from '@/services/defacement.service';
import { useAuthStore } from '@/stores/auth.store';

interface DefacementState {
  defacements: Defacement[];
  totalDefacements: number;
  loading: boolean;
  error: string | null;
  idMapping: Map<string, number>; // Map of defacement ID to display ID
  toast: {
    show: boolean;
    message: string;
    type: 'success' | 'error' | 'warning' | 'info';
    duration: number;
  };
  currentPage: number;
  nextPageUrl: string | null;
  perPage: number;
  currentFilters: DefacementFilters;
}

export const useDefacementStore = defineStore('defacement', {
  state: (): DefacementState => ({
    defacements: [],
    totalDefacements: 0,
    loading: false,
    error: null,
    idMapping: new Map(),
    toast: {
      show: false,
      message: '',
      type: 'success',
      duration: 3000
    },
    currentPage: 1,
    nextPageUrl: null,
    perPage: 10,
    currentFilters: {}
  }),

  getters: {
    hasDefacements: (state) => state.defacements.length > 0,
    getDefacementById: (state) => (id: string) => state.defacements.find(defacement => defacement.id === id),
    canManageDefacements: () => {
      const authStore = useAuthStore();
      return authStore.hasAllPermissions(['defacement_reset', 'entities_view']);
    },
    hasMoreData: (state) => !!state.nextPageUrl,
    countDefacedSites: (state) => state.defacements.filter(d => d.is_defaced).length,
    countHealthySites: (state) => state.defacements.filter(d => !d.is_defaced).length
  },

  actions: {
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
     * Fetch defacements from the API
     * @param page - Page number to load
     * @param resetList - if true, reset the list of defacements
     * @param filters - Filters to apply to the defacements
     */
    fetchDefacements(page = 1, resetList = true, filters: Partial<DefacementFilters> = {}) {
      this.loading = true;
      this.error = null;
    
      if (resetList) {
        this.defacements = [];
        this.currentPage = 1;
        this.nextPageUrl = null;
      }
    
      const params = { page, ...filters };
    
      return DefacementService.getFilteredDefacements(params)
        .then((response: PaginatedDefacements) => {
          if (resetList) {
            this.defacements = response.results;
          } else {
            const existingIds = new Set(this.defacements.map(defacement => defacement.id));
            const newDefacements = response.results.filter((defacement: Defacement) => !existingIds.has(defacement.id));
            this.defacements = [...this.defacements, ...newDefacements];
          }
    
          this.totalDefacements = response.count;
          this.currentPage = page;
          this.nextPageUrl = response.next;
          this.generateIdMapping();
    
          if (this.defacements.length === 0 && page === 1) {
            this.showToast('No defacement found.', 'info');
          }
    
          return response;
        })
        .catch((error: any) => {
          const errorMessage = error.response?.data?.error || 'Error retrieving defacements';
          this.error = errorMessage;
          this.showToast(errorMessage, 'error');
          return { results: [], count: 0, next: null, previous: null };
        })
        .finally(() => {
          this.loading = false;
        });
    },

    /**
     * Load more defacements from the next page
     * @param filters - Filters to apply to the defacements
     */
    loadMoreDefacements(filters: Partial<DefacementFilters> = {}) {
      if (this.loading || !this.nextPageUrl) {
        return Promise.reject(new Error('No additional data available'));
      }
    
      this.loading = true;
    
      return DefacementService.getNextPage(this.nextPageUrl)
        .then((response: PaginatedDefacements) => {
          const existingIds = new Set(this.defacements.map(defacement => defacement.id));
          const newDefacements = response.results.filter((defacement: Defacement) => !existingIds.has(defacement.id));
          this.defacements = [...this.defacements, ...newDefacements];
    
          this.nextPageUrl = response.next;
          this.currentPage += 1;
          this.generateIdMapping();
    
          return response;
        })
        .catch((error: any) => {
          const errorMessage = error.response?.data?.error || 'Error loading additional';
          this.error = errorMessage;
          this.showToast(errorMessage, 'error');
          throw error;
        })
        .finally(() => {
          this.loading = false;
        });
    },

    /**
     * Retrieves details of a defacement 
     * @param id - Defacement ID
     */
    getDefacement(id: string): Promise<DefacementDetail | null> {
      this.loading = true;
      this.error = null;

      return DefacementService.getDefacement(id)
        .then((defacement: DefacementDetail) => {
          return defacement;
        })
        .catch((error: any) => {
          const errorMessage = error.response?.data?.error || 'Error retrieving defacement details';
          this.showToast(errorMessage, 'error');
          return null;
        })
        .finally(() => {
          this.loading = false;
        });
    },

    /**
     * Resets a platform to normal state
     * @param id - UUID identifier of the defacement
     */
    resetDefacementState(id: string): Promise<boolean> {
        this.loading = true;
        
        return DefacementService.resetState(id)
          .then((response) => {
            const index = this.defacements.findIndex(defacement => defacement.id === id);
            if (index !== -1) {
              this.defacements[index].is_defaced = false;
            }
            
            this.showToast('Normal state reset successfully.', 'success');
            return true;
          })
          .catch((error) => {
            const errorMessage = error.response?.data?.error || 'Error resetting defacement state';
            this.error = errorMessage;
            this.showToast(errorMessage, 'error');
            return false;
          })
          .finally(() => {
            this.loading = false;
          });
      },
    
    /**
     * Generates a mapping between UUID and sequential ID for display
     */
    generateIdMapping() {
      this.idMapping.clear();
      this.defacements.forEach((defacement, index) => {
        this.idMapping.set(defacement.id, index + 1);
        defacement.displayId = index + 1;
      });
    },
    
    /**
     * Filters memory defacements according to specified criteria
     * @param filters - Filtering criteria
     */
    filterDefacements(filters: DefacementFilters): Defacement[] {
      return this.defacements.filter(defacement => {
        if (filters.searchTerm && 
            !this.matchesSearchTerm(defacement, filters.searchTerm)) {
          return false;
        }
        
        if (filters.is_defaced !== undefined && defacement.is_defaced !== filters.is_defaced) {
          return false;
        }
        
        if (filters.entity && 
            defacement.entity_name.toLowerCase() !== filters.entity.toLowerCase()) {
          return false;
        }
        
        if (filters.entity_name && 
            !defacement.entity_name.toLowerCase().includes(filters.entity_name.toLowerCase())) {
          return false;
        }
        
        if (filters.platform_url && 
            !defacement.platform_url.toLowerCase().includes(filters.platform_url.toLowerCase())) {
          return false;
        }
        
        if (filters.date_after) {
          const startDate = new Date(filters.date_after);
          const defacementDate = new Date(defacement.date);
          if (defacementDate < startDate) {
            return false;
          }
        }
        
        if (filters.date_before) {
          const endDate = new Date(filters.date_before);
          const defacementDate = new Date(defacement.date);
          if (defacementDate > endDate) {
            return false;
          }
        }
        
        return true;
      });
    },

    /**
     * Checks if a defacement matches the search term
     */
    matchesSearchTerm(defacement: Defacement, searchTerm: string): boolean {
      const term = searchTerm.toLowerCase();
      return (
        defacement.entity_name.toLowerCase().includes(term) ||
        defacement.platform_url.toLowerCase().includes(term) ||
        defacement.date.toLowerCase().includes(term)
      );
    },
    
    /**
     * Updates filters and reloads defacements
     */
    async updateFilters(newFilters: Partial<DefacementFilters>) {
      const filters = { ...newFilters, page: 1 };
      
      return this.fetchDefacements(1, true, filters);
    }
  }
});