import { defineStore } from 'pinia';
import logService from '@/services/logService';
import type { SystemLog, LogFilters, LogsResponse } from '@/types/logs.types';

export const useLogStore = defineStore('log', {
  state: () => ({
    logs: [] as SystemLog[],
    loading: false,
    error: null as string | null,
    filters: {
      start_date: '',
      end_date: '',
      start_time: '',
      end_time: '',
      name: '',
      details: '',
      search: '',
      ordering: '-created_at',
      page: 1
    } as LogFilters,
    totalItems: 0,
    perPage: 20,
    currentPage: 1,
    toast: {
      show: false,
      message: '',
      type: 'success' as 'success' | 'error' | 'warning',
      duration: 3000
    },
    nextPageUrl: null as string | null,
  }),

  getters: {
    formattedLogs: (state) => {
      return state.logs.map(log => ({
        ...log,
        date: log.created_at,
        title: log.username ? `Action by ${log.username}` : 'System action',
        description: typeof log.details === 'string' ? log.details : 
                     typeof log.details === 'object' ? JSON.stringify(log.details) : 
                     'No logs available',
        performed_by: log.username || 'Monitoring Sysem'
      }));
    },

    paginatedLogs: (state) => {
        const formattedLogs = state.logs.map(log => ({
          ...log,
          date: log.created_at,
          title: log.username ? `Action by ${log.username}` : 'System action',
          description: typeof log.details === 'string' ? log.details : 
                       typeof log.details === 'object' ? JSON.stringify(log.details) : 
                       'No details available',
          performed_by: log.username || 'Monitoring system'
        }));
        
        const start = (state.currentPage - 1) * state.perPage;
        const end = Math.min(start + state.perPage, formattedLogs.length);
        return formattedLogs.slice(start, end);
      }
  },

  actions: {
    showToast(message: string, type: 'success' | 'error' | 'warning' = 'success', duration = 3000) {
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

    fetchLogs(page = 1, resetList = true): Promise<LogsResponse> {
      this.loading = true;
      this.error = null;

      this.filters.page = page;
      
      if (resetList) {
        this.logs = [];
        this.currentPage = 1;
        this.nextPageUrl = null;
      }
      
      return logService.getLogs(this.filters)
        .then((response: LogsResponse) => {
          if (resetList) {
            this.logs = response.results;
          } else {
            const existingIds = new Set(this.logs.map(log => log.id));
            const newLogs = response.results.filter(log => !existingIds.has(log.id));
            this.logs = [...this.logs, ...newLogs];
          }
          
          this.totalItems = response.count;
          this.currentPage = page;
          this.nextPageUrl = response.next;
          return response;
        })
        .catch((error: any) => {
          const errorMessage = error.response?.data?.error || 'Error loading logs';
          this.error = errorMessage;
          this.showToast(errorMessage, 'error');
          throw error;
        })
        .finally(() => {
          this.loading = false;
        });
    },

    loadMoreLogs(): Promise<LogsResponse> {
        if (this.loading || !this.nextPageUrl) return Promise.reject(new Error('No additional data available'));
        
        const nextPage = this.currentPage + 1;
        return this.fetchLogs(nextPage, false);
    },
    
    hasMoreData(): boolean {
        return !!this.nextPageUrl;
      },

    updateFilters(newFilters: Partial<LogFilters>): Promise<LogsResponse> {
      this.filters = { ...this.filters, ...newFilters, page: 1 };
      
      return this.fetchLogs(1, true);
    },

    exportLogs(format: 'csv' | 'xlsx'): Promise<void> {
      this.loading = true;
      
      return logService.exportLogs(format, this.filters)
        .then((blob: Blob) => {
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = `logs_export.${format}`;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          window.URL.revokeObjectURL(url);
          
          this.showToast(`Export to format ${format.toUpperCase()} successful`, 'success');
        })
        .catch((error: any) => {
          const errorMessage = error.response?.data?.error || `Error exporting logs to format ${format}`;
          this.error = errorMessage;
          this.showToast(errorMessage, 'error');
          throw error;
        })
        .finally(() => {
          this.loading = false;
        });
    }
  }
});