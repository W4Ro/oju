import api from '@/api';
import { Configuration, ToggleProxyResponse, ToggleHostResponse, ToggleAlertResponse } from '@/types/config.types';

/**
 * Service for managing general configurations
 */
export const ConfigService = {
  /**
   * Retrieves general configurations
   */
  async getConfig(): Promise<Configuration> {
    return api.get('/config/').then(response => response.data.results[0]);
  },

  /**
   * Updates general configurations
   * @param config - Configuration data
   */
  async updateConfig(config: Configuration): Promise<Configuration> {
    return api.put('/config/', config).then(response => response.data);
  },

  /**
   * Toggles the use of proxies
   */
  async toggleProxy(): Promise<ToggleProxyResponse> {
    return api.post('/config/toggle-proxy/').then(response => response.data);
  },

  /**
   * Toggles the use of the host when the proxy fails
   */
  async toggleHost(): Promise<ToggleHostResponse> {
    return api.post('/config/toggle-host/').then(response => response.data);
  },

  /**
   * Toggles the reception of alerts
   */
  async toggleAlert(): Promise<ToggleAlertResponse> {
    return api.post('/config/toggle-alert/').then(response => response.data);
  }
};