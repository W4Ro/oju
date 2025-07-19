import api from '@/api';
import { MailConfig, ToggleActiveResponse } from '@/types/email.types';

/**
 * Service for managing email configurations
 */
export const EmailService = {
  /**
   * Get the email configuration
   */
  async getMailConfig(): Promise<MailConfig> {
    return api.get('/mail-settings/').then(response => response.data);
  },

  /**
   * update the email configuration
   * @param config - Email configuration data
   */
  async updateMailConfig(config: MailConfig): Promise<MailConfig> {
    return api.put('/mail-settings/', config).then(response => response.data);
  },

  /**
   * Toggle the active status of the email configuration
   */
  async toggleActiveStatus(): Promise<ToggleActiveResponse> {
    return api.post('/mail-settings/toggle_active/').then(response => response.data);
  }
};