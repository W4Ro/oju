import api from '@/api';
import { Integration, RTIR, Cerebrate, VirusTotal } from '@/types/integration.types';

/**
 * Service for managing integrations
 */
export const IntegrationService = {
  /**
   * Retrieves the list of available integrations
   */
  async getIntegrations(): Promise<Integration[]> {
    return api.get('/integrations/').then(response => response.data.results);
  },

  /**
   * Retrieves the RTIR configuration
   */
  async getRTIRConfig(): Promise<RTIR> {
    return api.get('/integrations/rtir/').then(response => response.data);
  },

  /**
   * Updates the RTIR configuration
   * @param data - RTIR configuration data
   */
  async updateRTIRConfig(data: RTIR): Promise<RTIR> {
    return api.put('/integrations/rtir/', data).then(response => response.data);
  },

  /**
   * Activates or deactivates the RTIR integration
   */
  async toggleRTIRStatus(): Promise<RTIR> {
    return api.post('/integrations/rtir/toggle/').then(response => response.data);
  },

  /**
   * Retrieves the Cerebrate configuration
   */
  async getCerebrateConfig(): Promise<Cerebrate> {
    return api.get('/integrations/cerebrate/').then(response => response.data);
  },

  /**
   * Updates the Cerebrate configuration
   * @param data - Cerebrate configuration data
   */
  async updateCerebrateConfig(data: Cerebrate): Promise<Cerebrate> {
    return api.put('/integrations/cerebrate/', data).then(response => response.data);
  },

  /**
   * Activates or deactivates the Cerebrate integration
   */
  async toggleCerebrateStatus(): Promise<Cerebrate> {
    return api.post('/integrations/cerebrate/toggle/').then(response => response.data);
  },

  /**
   * Refreshes Cerebrate data
   */
  async refreshCerebrate(): Promise<any> {
    return api.post('/integrations/cerebrate/refresh/').then(response => response.data);
  },

  /**
   * Retrieves the VirusTotal configuration
   */
  async getVirusTotalConfig(): Promise<VirusTotal> {
    return api.get('/integrations/vt/').then(response => response.data);
  },

  /**
   * Updates the VirusTotal configuration
   * @param data - VirusTotal configuration data
   */
  async updateVirusTotalConfig(data: VirusTotal): Promise<VirusTotal> {
    return api.put('/integrations/vt/', data).then(response => response.data);
  },

  /**
   * Activates or deactivates the VirusTotal integration
   */
  async toggleVirusTotalStatus(): Promise<VirusTotal> {
    return api.post('/integrations/vt/toggle/').then(response => response.data);
  }
};