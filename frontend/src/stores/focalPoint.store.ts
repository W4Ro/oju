import { defineStore } from 'pinia';
import { FocalPoint, FocalPointCreate, FocalPointUpdate } from '@/types/focalPoint.types';
import { FocalPointService } from '@/services/focalPoint.service';
import { useAuthStore } from '@/stores/auth.store';

interface FocalPointState {
  focalPoints: FocalPoint[];
  totalFocalPoints: number;
  loading: boolean;
  error: string | null;
  idMapping: Map<string, number>;
  toast: {
    show: boolean;
    message: string;
    type: 'success' | 'error' | 'warning' | 'info';
    duration: number;
  };
  currentPage: number;
  nextPageUrl: string | null;
  perPage: number;
  functionId: string | null; 
}

export const useFocalPointStores = defineStore('focalPoint', {
  state: (): FocalPointState => ({
    focalPoints: [],
    totalFocalPoints: 0,
    loading: false,
    error: null,
    idMapping: new Map<string, number>(), 
    toast: {
      show: false,
      message: '',
      type: 'success',
      duration: 3000
    },
    currentPage: 1,
    nextPageUrl: null,
    perPage: 20,
    functionId: null
  }),

  getters: {
    hasFocalPoints: (state) => Array.isArray(state.focalPoints) && state.focalPoints.length > 0,
    getFocalPointById: (state) => (id: string) => {
        if (!Array.isArray(state.focalPoints)) return null;
        return state.focalPoints.find(point => point.id === id);
      },
    canManageFocalPoints: () => {
      const authStore = useAuthStore();
      return authStore.hasPermission('focal_points_manage');
    },
    hasMoreData: (state) => !!state.nextPageUrl,
    activeFocalPoints: (state) => {
        if (!Array.isArray(state.focalPoints)) return [];
        return state.focalPoints.filter(point => point.is_active);
      },
      inactiveFocalPoints: (state) => {
        if (!Array.isArray(state.focalPoints)) return [];
        return state.focalPoints.filter(point => !point.is_active);
      }
  },

  actions: {
    /**
     * Generate a mapping between UUID and sequential ID for display
     * This method clears the existing mapping and creates a new one based on the current focal points.
     */
    generateIdMapping() {
        this.idMapping.clear();
        
        if (!this.focalPoints || !Array.isArray(this.focalPoints)) {
          this.focalPoints = [];
          return; 
        }
        
        this.focalPoints.forEach((point, index) => {
          this.idMapping.set(point.id, index + 1);
          
          (point as any).displayId = index + 1;
        });
      },
    
    /**
     * convert a sequential ID to a UUID
     */
    getUuidFromSequentialId(sequentialId: number): string | null {
      for (const [uuid, id] of this.idMapping.entries()) {
        if (id === sequentialId) {
          return uuid;
        }
      }
      return null;
    },
    
    /**
     * Convert a UUID to a sequential ID
     * @param uuid - UUID to convert
     */
    getSequentialIdFromUuid(uuid: string): number | null {
      return this.idMapping.get(uuid) || null;
    },

    /**
     * Show a toast message
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
     * Gets the list of focal points
     * @param page - Page number to load
     * @param resetList - if true, resets the existing list
     * @param functionId - ID of the function to filter (optional)
     */
    async fetchFocalPoints(page = 1, resetList = true, functionId?: string) {
        this.loading = true;
        this.error = null;
        
        if (resetList) {
          this.focalPoints = [];
          this.currentPage = 1;
          this.nextPageUrl = null;
        }
        
        if (functionId) {
          this.functionId = functionId;
        }
        
        try {
          let results = [];
          let count = 0;
          let nextUrl = null;
          
          if (this.functionId) {
            const response = await FocalPointService.getFocalPointsByFunction(this.functionId, { page });
            results = Array.isArray(response) ? response : [];
            count = results.length;
            nextUrl = null; 
          } else {
            const response = await FocalPointService.getFocalPoints({ page });
            results = response.results || [];
            count = response.count || 0;
            nextUrl = response.next;
          }
          
          if (resetList) {
            this.focalPoints = results;
          } else {
            if (!Array.isArray(this.focalPoints)) {
              this.focalPoints = [];
            }
            
            const existingIds = new Set(this.focalPoints.map(point => point.id));
            const newPoints = results.filter(point => !existingIds.has(point.id));
            this.focalPoints = [...this.focalPoints, ...newPoints];
          }
          
          this.totalFocalPoints = count;
          this.currentPage = page;
          this.nextPageUrl = nextUrl;
          
          if (Array.isArray(this.focalPoints)) {
            this.generateIdMapping();
          }
          
          if (this.focalPoints.length === 0 && page === 1) {
            this.showToast('No focal point found', 'info');
          }
          
          return { results, count, next: nextUrl, previous: null };
        } catch (error: any) {
          const errorMessage = error.response?.data?.error || 'Error loading focal points';
          this.error = errorMessage;
          this.showToast(errorMessage, 'error');
          
          if (!Array.isArray(this.focalPoints)) {
            this.focalPoints = [];
          }
          
          return { results: [], count: 0, next: null, previous: null };
        } finally {
          this.loading = false;
        }
      },

    /**
     * load more focal points
     */
    async loadMoreFocalPoints() {
      if (this.loading || !this.nextPageUrl) {
        return Promise.reject(new Error('No more data available'));
      }
      
      this.loading = true;
      
      try {
        const response = await FocalPointService.getNextPage(this.nextPageUrl);
        
        const existingIds = new Set(this.focalPoints.map(point => point.id));
        const newPoints = response.results.filter(point => !existingIds.has(point.id));
        this.focalPoints = [...this.focalPoints, ...newPoints];
        
        this.nextPageUrl = response.next;
        this.currentPage += 1;
        
        this.generateIdMapping();
        
        return response;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error loading more focal points';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Gets the details of a focal point
     * @param id - id of the focal point
     * @returns FocalPoint | null
     */
    async getFocalPoint(id: string): Promise<FocalPoint | null> {
      this.loading = true;
      this.error = null;

      try {
        const focalPoint = await FocalPointService.getFocalPoint(id);
        return focalPoint;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error loading focal point details';
        this.showToast(errorMessage, 'error');
        return null;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Create a new focal point
     * @param data - Data for the new focal point
     */
    async createFocalPoint(data: FocalPointCreate): Promise<FocalPoint | null> {
      this.loading = true;
      this.error = null;
      
      try {
        const newPoint = await FocalPointService.createFocalPoint(data);
        this.focalPoints.push(newPoint);
        this.totalFocalPoints++;
        
        this.generateIdMapping();
        
        this.showToast('Focal point created successfully', 'success');
        return newPoint;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error during focal point creation';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        return null;
      } finally {
        this.loading = false;
      }
    },

    /**
     * update an existing focal point
     * @param id - ID of the focal point
     * @param data - update data
     */
    async updateFocalPoint(id: string, data: FocalPointUpdate): Promise<FocalPoint | null> {
      this.loading = true;
      this.error = null;
      
      try {
        const updatedPoint = await FocalPointService.updateFocalPoint(id, data);
        
        const index = this.focalPoints.findIndex(point => point.id === id);
        if (index !== -1) {
          const displayId = (this.focalPoints[index] as any).displayId;
          this.focalPoints[index] = updatedPoint;
          if (displayId) {
            (this.focalPoints[index] as any).displayId = displayId;
          }
        }
        
        this.showToast('Focal point updated successfuly.', 'success');
        return updatedPoint;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error during focal point update';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        return null;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Change the status of a focal point (active/inactive)
     * @param id - ID of the focal point
     * @param isActive - New status (true for active, false for inactive)
     */
    async toggleFocalPointStatus(id: string, isActive: boolean): Promise<boolean> {
      this.loading = true;
      this.error = null;
      
      try {
        const result = await FocalPointService.toggleFocalPointStatus(id, { is_active: isActive });
        
        const index = this.focalPoints.findIndex(point => point.id === id);
        if (index !== -1) {
          this.focalPoints[index].is_active = result.is_active;
        }
        
        const statusText = result.is_active ? 'activated' : 'deactivated';
        this.showToast(`Point focal ${statusText} successfully.`, 'success');
        return true;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error during focal point status change';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        return false;
      } finally {
        this.loading = false;
      }
    },

    /**
     * delete a focal point
     * @param id - ID of the focal point
     */
    async deleteFocalPoint(id: string): Promise<boolean> {
      this.loading = true;
      this.error = null;
      
      try {
        await FocalPointService.deleteFocalPoint(id);
        
        this.focalPoints = this.focalPoints.filter(point => point.id !== id);
        this.totalFocalPoints--;
        
        this.generateIdMapping();
        
        this.showToast('Focal point deleted successfully', 'success');
        return true;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error during focal point deletion';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        return false;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Search for focal points by a search term
     * @param page - Page number to load
     * @param query - Recherch term
     */
    async searchFocalPoints(query: string): Promise<FocalPoint[]> {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await FocalPointService.searchFocalPoints(query);
        return response.results;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error during focal point search';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        return [];
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * Filer focal points by a search term
     * @param searchTerm - Research term
     */
    filterFocalPoints(searchTerm: string): FocalPoint[] {
      if (!searchTerm.trim()) {
        return this.focalPoints;
      }
      
      const term = searchTerm.toLowerCase();
      return this.focalPoints.filter(point => 
        point.full_name.toLowerCase().includes(term) || 
        point.email.toLowerCase().includes(term) || 
        point.function_name.toLowerCase().includes(term) ||
        point.phone_numbers.some(phone => phone.toLowerCase().includes(term))
      );
    }
  }
});