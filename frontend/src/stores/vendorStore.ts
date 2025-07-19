import { defineStore } from 'pinia';
import vendorService from '@/services/vendorService';
import type { AVVendor, VendorCreateData, VendorUpdateData } from '@/types/vendor.types';
import { useAuthStore } from '@/stores/auth.store';

export const useVendorStore = defineStore('vendor', {
  state: () => ({
    vendors: [] as AVVendor[],
    loading: false,
    error: null as string | null,
    currentPage: 1,
    totalItems: 0,
    perPage: 20,
    nextPageUrl: null as string | null,
    toast: {
      show: false,
      message: '',
      type: 'success' as 'success' | 'error' | 'warning',
      duration: 3000
    }
  }),

  getters: {
    canEdit(): boolean {
      const authStore = useAuthStore();
      return authStore.hasPermission('vendor_list_edit');
    },

    canDelete(): boolean {
      const authStore = useAuthStore();
      return authStore.hasPermission('vendor_list_delete');
    },

    formattedVendors(): any[] {
      return this.vendors.map(vendor => ({
        id: vendor.id,
        user: {
          name: vendor.name
        },
        email: vendor.contact,
        company: vendor.comments || '',
        createdAt: vendor.created_at,
        updatedAt: vendor.updated_at
      }));
    },

    hasMoreData(): boolean {
      return !!this.nextPageUrl;
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

    fetchVendors(page = 1, reset = true): Promise<AVVendor[]> {
      this.loading = true;
      this.error = null;
      
      if (reset) {
        this.vendors = [];
        this.currentPage = 1;
      }
      
      return vendorService.getVendors(page)
        .then(response => {
          if (reset) {
            this.vendors = response.results;
          } else {
            const existingIds = new Set(this.vendors.map(v => v.id));
            const newVendors = response.results.filter(v => !existingIds.has(v.id));
            this.vendors = [...this.vendors, ...newVendors];
          }
          
          this.totalItems = response.count;
          this.currentPage = page;
          this.nextPageUrl = response.next;
          return this.vendors;
        })
        .catch((error: any) => {
          const errorMessage = error.response?.data?.error || 'Error loading vendors';
          this.error = errorMessage;
          this.showToast(errorMessage, 'error');
          return [] as AVVendor[];
        })
        .finally(() => {
          this.loading = false;
        });
    },

    loadMoreVendors(): Promise<AVVendor[]> {
      if (this.loading || !this.hasMoreData) {
        return Promise.resolve([] as AVVendor[]);
      }
      
      const nextPage = this.currentPage + 1;
      return this.fetchVendors(nextPage, false);
    },

    createVendor(data: VendorCreateData): Promise<AVVendor | null> {
      this.loading = true;
      this.error = null;
      
      return vendorService.createVendor(data)
        .then(vendor => {
          this.vendors.unshift(vendor);
          this.totalItems++;
          this.showToast('Vendor created successfully', 'success');
          return vendor;
        })
        .catch((error: any) => {
          const errorMessage = error.response?.data?.error || 'Error creating vendor';
          this.error = errorMessage;
          this.showToast(errorMessage, 'error');
          return null;
        })
        .finally(() => {
          this.loading = false;
        });
    },

    updateVendor(id: string, data: VendorUpdateData): Promise<AVVendor | null> {
      this.loading = true;
      this.error = null;
      
      return vendorService.updateVendor(id, data)
        .then(updatedVendor => {
          const index = this.vendors.findIndex(v => v.id === id);
          if (index !== -1) {
            this.vendors[index] = updatedVendor;
          }
          
          this.showToast('Vendor updated successfully', 'success');
          return updatedVendor;
        })
        .catch((error: any) => {
          const errorMessage = error.response?.data?.error || `Error updating vendor ${id}`;
          this.error = errorMessage;
          this.showToast(errorMessage, 'error');
          return null;
        })
        .finally(() => {
          this.loading = false;
        });
    },

    deleteVendor(id: string): Promise<boolean> {
      this.loading = true;
      this.error = null;
      
      return vendorService.deleteVendor(id)
        .then(success => {
          if (success) {
            this.vendors = this.vendors.filter(v => v.id !== id);
            this.totalItems--;
            this.showToast('Vendor deleted successfully', 'success');
          }
          
          return success;
        })
        .catch((error: any) => {
          const errorMessage = error.response?.data?.error || `Error deleting vendor ${id}`;
          this.error = errorMessage;
          this.showToast(errorMessage, 'error');
          return false;
        })
        .finally(() => {
          this.loading = false;
        });
    }
  }
});