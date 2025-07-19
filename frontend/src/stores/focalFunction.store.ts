import { defineStore } from 'pinia';
import { FocalFunction, FocalFunctionCreate, FocalFunctionUpdate } from '@/types/focalFunction.types';
import { FocalFunctionService } from '@/services/focalFunction.service';
import { useAuthStore } from '@/stores/auth.store';

interface FocalFunctionState {
  focalFunctions: FocalFunction[];
  totalFocalFunctions: number;
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
}

export const useFocalFunctionStore = defineStore('focalFunction', {
  state: (): FocalFunctionState => ({
    focalFunctions: [],
    totalFocalFunctions: 0,
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
    perPage: 10
  }),

  getters: {
    hasFocalFunctions: (state) => state.focalFunctions.length > 0,
    getFocalFunctionById: (state) => (id: string) => state.focalFunctions.find(func => func.id === id),
    canManageFocalFunctions: () => {
      const authStore = useAuthStore();
      return authStore.hasPermission('focal_functions_manage');
    },
    hasMoreData: (state) => !!state.nextPageUrl
  },

  actions: {
    /**
     * Generates a mapping between UUID and sequential ID for display
     */
    generateIdMapping() {
      this.idMapping.clear();
      this.focalFunctions.forEach((func, index) => {
        this.idMapping.set(func.id, index + 1);
        
        (func as any).displayId = index + 1;
      });
    },
    
    /**
     * Converts a sequential ID to a UUID
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
     * Converts a UUID to a sequential ID
     */
    getSequentialIdFromUuid(uuid: string): number | null {
      return this.idMapping.get(uuid) || null;
    },

    /**
     * Displays a notification toast
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
     * Retrieves the list of functions
     * @param page - Page number to load
     * @param resetList - If true, resets the existing list
     */
    async fetchFocalFunctions(page = 1, resetList = true) {
      this.loading = true;
      this.error = null;
      
      if (resetList) {
        this.focalFunctions = [];
        this.currentPage = 1;
        this.nextPageUrl = null;
      }
      
      try {
        const response = await FocalFunctionService.getFocalFunctions();
        
        if (resetList) {
          this.focalFunctions = response.results;
        } else {
          const existingIds = new Set(this.focalFunctions.map(func => func.id));
          const newFunctions = response.results.filter(func => !existingIds.has(func.id));
          this.focalFunctions = [...this.focalFunctions, ...newFunctions];
        }
        
        this.totalFocalFunctions = response.count;
        this.currentPage = page;
        this.nextPageUrl = response.next;
        
        this.generateIdMapping();
        
        if (this.focalFunctions.length === 0 && page === 1) {
          this.showToast('No function found', 'info');
        }
        
        return response;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error loading focal functions';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        return { results: [], count: 0, next: null, previous: null };
      } finally {
        this.loading = false;
      }
    },

    /**
     * Loads the next page of functions
     */
    async loadMoreFunctions() {
      if (this.loading || !this.nextPageUrl) {
        return Promise.reject(new Error('No more data to load or already loading'));
      }
      
      this.loading = true;
      
      try {
        const response = await FocalFunctionService.getNextPage(this.nextPageUrl);
        
        const existingIds = new Set(this.focalFunctions.map(func => func.id));
        const newFunctions = response.results.filter(func => !existingIds.has(func.id));
        this.focalFunctions = [...this.focalFunctions, ...newFunctions];
        
        this.nextPageUrl = response.next;
        this.currentPage += 1;
        
        this.generateIdMapping();
        
        return response;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error loading additional functions';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Retrieves the details of a function
     * @param id - Function ID
     */
    async getFocalFunction(id: string): Promise<FocalFunction | null> {
      this.loading = true;
      this.error = null;

      try {
        const focalFunction = await FocalFunctionService.getFocalFunction(id);
        return focalFunction;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error loading function details';
        this.showToast(errorMessage, 'error');
        return null;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Create a new function
     * @param data - Data of the function to be created
     */
    async createFocalFunction(data: FocalFunctionCreate): Promise<FocalFunction | null> {
      this.loading = true;
      this.error = null;
      
      try {
        const newFunction = await FocalFunctionService.createFocalFunction(data);
        this.focalFunctions.push(newFunction);
        this.totalFocalFunctions++;
        
        this.generateIdMapping();
        
        this.showToast('Function created successfully', 'success');
        return newFunction;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'error creating function';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        return null;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Updates an existing function
     * @param id - Function ID
     * @param data - Update data
     */
    async updateFocalFunction(id: string, data: FocalFunctionUpdate): Promise<FocalFunction | null> {
      this.loading = true;
      this.error = null;
      
      try {
        const updatedFunction = await FocalFunctionService.updateFocalFunction(id, data);
        
        const index = this.focalFunctions.findIndex(func => func.id === id);
        if (index !== -1) {
          const displayId = (this.focalFunctions[index] as any).displayId;
          this.focalFunctions[index] = updatedFunction;
          if (displayId) {
            (this.focalFunctions[index] as any).displayId = displayId;
          }
        }
        
        this.showToast('Function updated successfully.', 'success');
        return updatedFunction;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error updating function';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        return null;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Deletes a function
     * @param id - Function ID
     */
    async deleteFocalFunction(id: string): Promise<boolean> {
      this.loading = true;
      this.error = null;
      
      try {
        await FocalFunctionService.deleteFocalFunction(id);
        
        this.focalFunctions = this.focalFunctions.filter(func => func.id !== id);
        this.totalFocalFunctions--;
        
        this.generateIdMapping();
        
        this.showToast('Function deleted successfully', 'success');
        return true;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error deleting function';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        return false;
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * Filter functions by search term
     * @param searchTerm - Search term
     */
    filterFunctions(searchTerm: string): FocalFunction[] {
      if (!searchTerm.trim()) {
        return this.focalFunctions;
      }
      
      const term = searchTerm.toLowerCase();
      return this.focalFunctions.filter(func => 
        func.name.toLowerCase().includes(term)
      );
    }
  }
});