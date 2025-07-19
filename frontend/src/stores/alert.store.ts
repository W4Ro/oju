import { defineStore } from 'pinia';
import { Alert, STATUS_MAPPING, REVERSE_STATUS_MAPPING, AlertEmail, AlertSendEmail } from '@/types/alert.types';
import { AlertService } from '@/services/alert.service';
import { useAuthStore } from '@/stores/auth.store';

interface AlertState {
  alerts: Alert[];
  totalAlerts: number;
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
  sending: boolean;
}

interface AlertEmailState {
    sending: boolean;
    successMessage: string | null;
    error: string | null;
  }
  
export interface AlertFilters {
  searchTerm: string;
  status: string;
  alertType: string;
  entity: string;
  platform: string;
  dateStart: string;
  dateEnd: string;
  detail: string;
  ordering: string;
  page?: number;
}

export const useAlertStore = defineStore('alert', {
  state: (): AlertState => ({
    alerts: [],
    totalAlerts: 0,
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
    perPage: 20,
    sending: false
  }),

  getters: {
    hasAlerts: (state) => state.alerts.length > 0,
    getAlertById: (state) => (id: string) => state.alerts.find(alert => alert.id === id),
    canManageAlerts: () => {
      const authStore = useAuthStore();
      return authStore.hasAllPermissions(['alerts_manage', 'entities_view']);
    },
    hasMoreData: (state) => !!state.nextPageUrl
  },

  actions: {
    /**
     * Display a toast message
     * @param message - Message to display
     */
    showToast(message: string, type: 'success' | 'error' | 'warning' | 'info' = 'success', duration = 3000) {
      const safeMessage = message || 'An error has occurred';
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
     * Fetch alerts from the API
     * @param page - Page number to load
     * @param resetList - If true, resets the existing list
     */
    fetchAlerts(page = 1, resetList = true, filters: Partial<AlertFilters> = {}) {
        this.loading = true;
        this.error = null;
      
        if (resetList) {
          this.alerts = [];
          this.currentPage = 1;
          this.nextPageUrl = null;
        }
      
        const params = { page, ...filters };
      
        return AlertService.getFilteredAlerts(params)
          .then((response: any) => {
            if (resetList) {
              this.alerts = response.results;
            } else {
              const existingIds = new Set(this.alerts.map(alert => alert.id));
              const newAlerts = response.results.filter((alert: Alert) => !existingIds.has(alert.id));
              this.alerts = [...this.alerts, ...newAlerts];
            }
      
            this.totalAlerts = response.count;
            this.currentPage = page;
            this.nextPageUrl = response.next;
            this.generateIdMapping();
      
            if (this.alerts.length === 0 && page === 1) {
              this.showToast('No alerts found.', 'info');
            }
      
            return response;
          })
          .catch((error: any) => {
            const errorMessage = error.response?.data?.error || 'Error retrieving alerts';
            this.error = errorMessage;
            this.showToast(errorMessage, 'error');
            return { results: [], count: 0, next: null, previous: null };
          })
          .finally(() => {
            this.loading = false;
          });
      },

    /**
     * Load more alerts from the next page
     * @param filters - Optional filters to apply
     */
    loadMoreAlerts(filters: Partial<AlertFilters> = {}) {
        if (this.loading || !this.nextPageUrl) {
          return Promise.reject(new Error('No additional data available'));
        }
      
        this.loading = true;
      
        return AlertService.getNextPage(this.nextPageUrl)
          .then((response: any) => {
            const existingIds = new Set(this.alerts.map(alert => alert.id));
            const newAlerts = response.results.filter((alert: Alert) => !existingIds.has(alert.id));
            this.alerts = [...this.alerts, ...newAlerts];
      
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

      fetchAlertEmail(id: string): Promise<AlertEmail | any[]> {
        this.loading = true;
        this.error = null;
        
        return AlertService.getAlertEmail(id)
          .then((template: AlertEmail) => {
            return template;
          })
          .catch((error: any) => {
            const errorMessage = error.response?.data?.error || 'Error loading template';
            this.showToast(errorMessage, 'error');
            return [] as any[];
          })
          .finally(() => {
            this.loading = false;
          });
      },

      getAlert(id: string): Promise<Alert | any []>{
        this.loading = true;
        this.error = null;

        return AlertService.getAlert(id)
        .then((alert: Alert) => {
            return alert;
        })
        .catch((error: any) => {
            const errorMessage = error.response?.data?.error || 'Error while loading alert details';
            this.showToast(errorMessage, 'error');
            return [];
        })
        .finally(() => {
            this.loading = false;
        })
      },

    sendEmail(alertId: string, payload: AlertSendEmail): Promise<any> {
        this.sending = true;
        this.error = null;
  
        return AlertService.sendAlertEmail(alertId, payload)
          .then((response: any ) => {
            return response;
          })
          .catch((err: any) => {
            const errorMessage = err.response?.data?.error || 'Error while loading alert details';
            this.showToast(errorMessage, 'error');
            return null;
          })
          .finally(() => {
            this.sending = false;
          });
      },
    
    /**
     * Generates a mapping between UUID and sequential ID for display
     */
    generateIdMapping() {
      this.idMapping.clear();
      this.alerts.forEach((alert, index) => {
        this.idMapping.set(alert.id, index + 1);
        alert.displayId = index + 1;
      });
    },
    
    /**
     * Filters alerts in memory according to specified criteria
     * @param filters - Filtering criteria
     */
    filterAlerts(filters: AlertFilters): Alert[] {
      return this.alerts.filter(alert => {
        if (filters.searchTerm && 
            !JSON.stringify(alert).toLowerCase().includes(filters.searchTerm.toLowerCase())) {
          return false;
        }
        
        if (filters.status && alert.status_display !== filters.status) {
          return false;
        }
        
        if (filters.alertType && alert.alert_type_display !== filters.alertType) {
          return false;
        }
        
        if (filters.entity && 
            !alert.entity_name.toLowerCase().includes(filters.entity.toLowerCase())) {
          return false;
        }
        
        if (filters.platform && 
            !alert.platform_url.toLowerCase().includes(filters.platform.toLowerCase())) {
          return false;
        }
        
        if (filters.detail && 
            !alert.details.toLowerCase().includes(filters.detail.toLowerCase())) {
          return false;
        }
        
        if (filters.dateStart) {
          const startDate = new Date(filters.dateStart);
          const alertDate = new Date(alert.date);
          if (alertDate < startDate) {
            return false;
          }
        }
        
        if (filters.dateEnd) {
          const endDate = new Date(filters.dateEnd);
          const alertDate = new Date(alert.date);
          if (alertDate > endDate) {
            return false;
          }
        }
        
        return true;
      });
    },
    
    /**
     * Sorts alerts according to the specified criteria
     * @param alerts - Alerts to sort
     * @param orderBy - Sorting criteria
     */
    sortAlerts(alerts: Alert[], orderBy: string): Alert[] {
      return [...alerts].sort((a, b) => {
        if (orderBy === 'date') {
          return new Date(b.date).getTime() - new Date(a.date).getTime(); 
        }
        const aValue = a[orderBy as keyof Alert];
        const bValue = b[orderBy as keyof Alert];
        if (aValue === undefined && bValue === undefined) return 0;
        if (aValue === undefined) return 1; 
        if (bValue === undefined) return -1;
        if (typeof aValue === 'string' && typeof bValue === 'string') {
            return aValue.localeCompare(bValue);
          }
        if (aValue < bValue) return -1;
        if (aValue > bValue) return 1;
        return 0;
      });
    },
    
    /**
     * Updates the status of an alert
     * @param alertId - Alert ID
     * @param newStatus - New status
     */
    updateAlertStatus(alertId: string, newStatus: string) {
        this.loading = true;
      
        const apiStatus = REVERSE_STATUS_MAPPING[newStatus];
      
        return AlertService.updateAlertStatus(alertId, { status: apiStatus })
          .then((updatedAlert: any) => {
            const index = this.alerts.findIndex(alert => alert.id === alertId);
            if (index !== -1) {
              this.alerts[index] = {
                ...updatedAlert,
                status_display: STATUS_MAPPING[updatedAlert.status],
                displayId: this.idMapping.get(alertId)
              };
            }
      
            const displayId = this.idMapping.get(alertId) || '';
            this.showToast(`The alert status #${displayId} has been successfully updated.`, 'success');
            return updatedAlert;
          })
          .catch((error: any) => {
            const errorMessage = error.response?.data?.error|| 'Error updating status';
            this.error = errorMessage;
            this.showToast(error, 'error'); 
            throw error;
          })
          .finally(() => {
            this.loading = false;
          });
      },

    /**
     * Updating filters and reloading alerts
     */
    async updateFilters(newFilters: Partial<AlertFilters>) {
        const filters = { ...newFilters, page: 1 };
        
        return this.fetchAlerts(1, true, filters);
      }
  }
});