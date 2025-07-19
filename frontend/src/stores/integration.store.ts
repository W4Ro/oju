import { defineStore } from 'pinia';
import { Integration, RTIR, Cerebrate, VirusTotal } from '@/types/integration.types';
import { IntegrationService } from '@/services/integration.service';

interface IntegrationState {
  integrations: Integration[];
  rtirConfig: RTIR | null;
  cerebrateConfig: Cerebrate | null;
  virusTotalConfig: VirusTotal | null;
  loading: boolean;
  configLoading: boolean;
  error: string | null;
  toast: {
    show: boolean;
    message: string;
    type: 'success' | 'error' | 'warning' | 'info';
    duration: number;
  };
}

export const useIntegrationStore = defineStore('integration', {
  state: (): IntegrationState => ({
    integrations: [],
    rtirConfig: null,
    cerebrateConfig: null,
    virusTotalConfig: null,
    loading: false,
    configLoading: false,
    error: null,
    toast: {
      show: false,
      message: '',
      type: 'success',
      duration: 3000
    }
  }),

  getters: {
    hasIntegrations: (state) => state.integrations.length > 0,
    getRTIRConfig: (state) => state.rtirConfig,
    getCerebrateConfig: (state) => state.cerebrateConfig,
    getVirusTotalConfig: (state) => state.virusTotalConfig
  },

  actions: {
    /**
     * Show a toast message
     * @param message - Message to display
     */
    showToast(message: string, type: 'success' | 'error' | 'warning' | 'info' = 'success', duration = 3000) {
      const safeMessage = message || 'Error occurred';
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
     * Get the list of integrations
     */
    async fetchIntegrations() {
      this.loading = true;
      this.error = null;

      try {
        const response = await IntegrationService.getIntegrations();
        this.integrations = response;
        return response;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error loading integrations';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Get the configuration of RTIR
     */
    async fetchRTIRConfig() {
      this.configLoading = true;
      this.error = null;

      try {
        const response = await IntegrationService.getRTIRConfig();
        this.rtirConfig = response;
        return response;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error loading RTIR configuration';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        throw error;
      } finally {
        this.configLoading = false;
      }
    },

    /**
     * Update the configuration of RTIR
     * @param data - RTIR configuration data
     */
    async updateRTIRConfig(data: RTIR) {
      this.configLoading = true;
      this.error = null;

      try {
        const response = await IntegrationService.updateRTIRConfig(data);
        this.rtirConfig = response;
        this.showToast('RTIR configuration updated successfully', 'success');
        return response;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error updating RTIR configuration';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        throw error;
      } finally {
        this.configLoading = false;
      }
    },

    /**
     * Toggle the status of RTIR integration
     */
    async toggleRTIRStatus() {
      this.loading = true;
      this.error = null;

      try {
        const response = await IntegrationService.toggleRTIRStatus();
        this.rtirConfig = response;
        
        const rtirIndex = this.integrations.findIndex(i => i.name === 'RTIR');
        if (rtirIndex !== -1) {
          this.integrations[rtirIndex].is_active = response.is_active;
          this.integrations[rtirIndex].last_updated = response.updated_at;
        }
        
        this.showToast(`RTIR ${response.is_active ? 'activated' : 'deactivated'} successfully`, 'success');
        return response;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error changing RTIR status';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Get the configuration of Cerebrate
     */
    async fetchCerebrateConfig() {
      this.configLoading = true;
      this.error = null;

      try {
        const response = await IntegrationService.getCerebrateConfig();
        this.cerebrateConfig = response;
        return response;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error loading Cerebrate configuration';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        throw error;
      } finally {
        this.configLoading = false;
      }
    },

    /**
     * Update the configuration of Cerebrate
     * @param data - Cerebrate configuration data
     */
    async updateCerebrateConfig(data: Cerebrate) {
      this.configLoading = true;
      this.error = null;

      try {
        const response = await IntegrationService.updateCerebrateConfig(data);
        this.cerebrateConfig = response;
        this.showToast('Cerebrate configuration updated successfully', 'success');
        return response;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error updating Cerebrate configuration';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        throw error;
      } finally {
        this.configLoading = false;
      }
    },

    /**
     * Toggle the status of Cerebrate integration
     */
    async toggleCerebrateStatus() {
      this.loading = true;
      this.error = null;

      try {
        const response = await IntegrationService.toggleCerebrateStatus();
        this.cerebrateConfig = response;
        
        const cerebrateIndex = this.integrations.findIndex(i => i.name === 'Cerebrate');
        if (cerebrateIndex !== -1) {
          this.integrations[cerebrateIndex].is_active = response.is_active;
          this.integrations[cerebrateIndex].last_updated = response.updated_at;
        }
        
        this.showToast(`Cerebrate ${response.is_active ? 'activated' : 'deactivated'} successfully`, 'success');
        return response;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error changing Cerebrate status';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Refresh Cerebrate data
     */
    async refreshCerebrate() {
      this.loading = true;
      this.error = null;

      try {
        const response = await IntegrationService.refreshCerebrate();
        
        const cerebrateIndex = this.integrations.findIndex(i => i.name === 'Cerebrate');
        if (cerebrateIndex !== -1) {
          this.integrations[cerebrateIndex].last_updated = new Date().toISOString();
        }
        
        this.showToast('Cerebrate data refreshed successfully', 'success');
        return response;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error refreshing Cerebrate data';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Get the configuration of VirusTotal
     */
    async fetchVirusTotalConfig() {
      this.configLoading = true;
      this.error = null;

      try {
        const response = await IntegrationService.getVirusTotalConfig();
        this.virusTotalConfig = response;
        return response;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error loading VirusTotal configuration';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        throw error;
      } finally {
        this.configLoading = false;
      }
    },

    /**
     * Update the configuration of VirusTotal
     * @param data - VirusTotal configuration data
     */
    async updateVirusTotalConfig(data: VirusTotal) {
      this.configLoading = true;
      this.error = null;

      try {
        const response = await IntegrationService.updateVirusTotalConfig(data);
        this.virusTotalConfig = response;
        this.showToast('VirusTotal configuration updated successfully', 'success');
        return response;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error updating VirusTotal configuration';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        throw error;
      } finally {
        this.configLoading = false;
      }
    },

    /**
     * Toggle the status of VirusTotal integration
     */
    async toggleVirusTotalStatus() {
      this.loading = true;
      this.error = null;

      try {
        const response = await IntegrationService.toggleVirusTotalStatus();
        this.virusTotalConfig = response;
        
        const vtIndex = this.integrations.findIndex(i => i.name === 'VirusTotal');
        if (vtIndex !== -1) {
          this.integrations[vtIndex].is_active = response.is_active;
          this.integrations[vtIndex].last_updated = response.updated_at;
        }
        
        this.showToast(`VirusTotal ${response.is_active ? 'activated' : 'deactivated'} successfully`, 'success');
        return response;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error changing VirusTotal status';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Get the configuration of a specific integration
     * @param integrationName - Name of the integration
     */
    async fetchIntegrationConfig(integrationName: string) {
      switch (integrationName) {
        case 'RTIR':
          return this.fetchRTIRConfig();
        case 'Cerebrate':
          return this.fetchCerebrateConfig();
        case 'VirusTotal':
          return this.fetchVirusTotalConfig();
        default:
          throw new Error(`Unsupported configuration for ${integrationName}`);
      }
    },

    /**
     * Toggle the status of a specific integration
     * @param integrationName - Name of the integration
     */
    async toggleIntegrationStatus(integrationName: string) {
      switch (integrationName) {
        case 'RTIR':
          return this.toggleRTIRStatus();
        case 'Cerebrate':
          return this.toggleCerebrateStatus();
        case 'VirusTotal':
          return this.toggleVirusTotalStatus();
        default:
          throw new Error(`Unsupported integration: ${integrationName}`);
      }
    }
  }
});