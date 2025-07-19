import api from '@/api';
import type { LogFilters, SystemLog, LogsResponse } from '@/types/logs.types';

const logsService = {
  /**
   * Retrieves the list of system logs with filtering
   * @param filters Filters to apply
   */
  getLogs(filters: LogFilters = {}): Promise<LogsResponse> {
    const params: Record<string, any> = {};
    
    if (filters.start_date) {
      const startDateTime = filters.start_time 
        ? `${filters.start_date} ${filters.start_time}` 
        : filters.start_date;
      params.start_date = startDateTime;
    }
    
    if (filters.end_date) {
      const endDateTime = filters.end_time 
        ? `${filters.end_date} ${filters.end_time}` 
        : filters.end_date;
      params.end_date = endDateTime;
    }
    
    if (filters.name) params.name = filters.name;
    if (filters.details) params.details = filters.details;
    if (filters.search) params.search = filters.search;
    if (filters.ordering) params.ordering = filters.ordering;
    if (filters.page) params.page = filters.page;
    
    return api.get('/logs/', { params })
      .then(response => {
        return response.data;
      })
      .catch((error) => {
        
        throw error;
      });
  },

  /**
   * Retrieves details of a specific log
   * @param id Log ID
   */
  getLogById(id: string): Promise<SystemLog> {
    return api.get(`/logs/${id}/`)
      .then(response => response.data)
      .catch((error) => {
        throw error;
      });
  },

  /**
   * Exports logs in the requested format
   * @param format Export format (csv or xlsx)
   * @param filters Filters to apply
   */
  exportLogs(format: 'csv' | 'xlsx', filters: LogFilters = {}): Promise<Blob> {
    const params: Record<string, any> = { export_format: format };
    
    if (filters.start_date) params.start_date = filters.start_date;
    if (filters.end_date) params.end_date = filters.end_date;
    if (filters.name) params.name = filters.name;
    if (filters.details) params.details = filters.details;
    if (filters.search) params.search = filters.search;
    if (filters.ordering) params.ordering = filters.ordering;
    
    return api.get('/logs/export/', { 
      params,
      responseType: 'blob'
    })
      .then(response => {
        return response.data;
      })
      .catch((error) => {
        throw error;
      });
  }
};

export default logsService;