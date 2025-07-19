import api from '@/api';
import { Alert, PaginatedAlerts, AlertStatusUpdate, AlertEmail, AlertSendEmail } from '@/types/alert.types';

/**
 * Service for managing alerts
 */
export const AlertService = {
  /**
   * Fetches the list of alerts
   * @returns {Promise<PaginatedAlerts>} - A promise that resolves to the paginated alerts data
   */
  async getAlerts(): Promise<PaginatedAlerts> {
    return api.get('/alerts/').then(response => response.data);
  },

  /**
   * Fetches details of a specific alert by its ID
   * @param id - The ID of the alert to retrieve
   */
  async getAlert(id: string): Promise<Alert> {
    return api.get(`/alerts/${id}/`).then(response => response.data);
  },

  async getNextPage(nextUrl: string): Promise<any> {
    const response = await api.get(nextUrl);
    return response.data;
  },

  async getAlertEmail(id: string): Promise<AlertEmail>{
    return api.get(`/emailing/emailing/${id}/`).then(response => response.data);
  },

  /**
   * Send an email about an alert
   * @param alertId - ID of the alert concerned
   * @param payload - Email data (recipient, subject, body, etc.)
   */
  async sendAlertEmail(alertId: string, payload: AlertSendEmail): Promise<{ message: string; email_log_id?: string }> {
    return api.post(`/emailing/alerts/${alertId}/send-email/`, payload)
      .then(response => response.data);
  },
  

  /**
   * Updates the status of an alert
   * @param id - Alert ID
   * @param data - Update data (status)
   */
  async updateAlertStatus(id: string, data: AlertStatusUpdate): Promise<Alert> {
    return api.put(`/alerts/${id}/`, data).then(response => response.data);
  },

  /**
   * Retrieves alerts with filtering
   * Filters are applied directly in the store for client-side filtering
   * but this method allows to obtain initial filtered data if necessary
   * @param params -Filter settings
   */
  async getFilteredAlerts(params: Record<string, any> = {}): Promise<PaginatedAlerts> {
    return api.get('/alerts/', { params }).then(response => response.data);
  }
};