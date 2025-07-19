import { defineStore } from 'pinia';
import { ConfigService } from '@/services/config.service';
import { Configuration } from '@/types/config.types';

interface ConfigState {
  config: Configuration | null;
  loading: boolean;
  saving: boolean;
  toggling: {
    proxy: boolean;
    host: boolean;
    alert: boolean;
  };
  error: string | null;
  validationErrors: {
    email: string;
    proxy: string;
    dns: string;
    scanFrequency: string;
    userAgent: string;
  };
  toast: {
    show: boolean;
    message: string;
    type: 'success' | 'error' | 'warning' | 'info';
    duration: number;
  };
}

export const useConfigStore = defineStore('config', {
  state: (): ConfigState => ({
    config: null,
    loading: false,
    saving: false,
    toggling: {
      proxy: false,
      host: false,
      alert: false
    },
    error: null,
    validationErrors: {
      email: '',
      proxy: '',
      dns: '',
      scanFrequency: '',
      userAgent: ''
    },
    toast: {
      show: false,
      message: '',
      type: 'success',
      duration: 3000
    }
  }),

  getters: {
    getConfig: (state) => state.config,
    isLoading: (state) => state.loading,
    isSaving: (state) => state.saving,
    isToggling: (state) => state.toggling,
    hasError: (state) => !!state.error,
    hasValidationErrors: (state) => {
      return Object.values(state.validationErrors).some(error => !!error);
    },
    isFormValid: (state) => {
      if (!state.config) return false;

      const noValidationErrors = !Object.values(state.validationErrors).some(error => !!error);

      const requiredFieldsFilled = !!(
        state.config.email &&
        state.config.user_agent &&
        state.config.max_worker >= 5 &&
        state.config.max_worker <= 30 &&
        state.config.scan_frequency >= 120 &&
        state.config.scan_frequency <= 1000000
      );

      const requiredArraysValid = !state.config.use_proxy || (state.config.proxy && state.config.proxy.length > 0);

      return noValidationErrors && requiredFieldsFilled && requiredArraysValid;
    }
  },

  actions: {
    /**
     * Show a toast message
     * @param message - Message to display
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
     * Fetch the general configurations
     */
    async fetchConfig() {
      this.loading = true;
      this.error = null;

      try {
        const response = await ConfigService.getConfig();
        this.config = response;
        return response;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error loading configurations';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * update the general configurations
     * @param config - Configuration data to update
     */
    async updateConfig(config: Configuration) {
      this.validateAllFields(config);
      
      if (this.hasValidationErrors) {
        this.showToast('Please correct the errors in the form', 'error');
        return false;
      }

      this.saving = true;
      this.error = null;

      try {
        const response = await ConfigService.updateConfig(config);
        this.config = response;
        this.showToast('Configurations updated successfully', 'success');
        return true;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error updating configurations';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        return false;
      } finally {
        this.saving = false;
      }
    },

    /**
     * toggle the use of proxies
     */
    async toggleProxy() {
      this.toggling.proxy = true;
      this.error = null;

      try {
        const response = await ConfigService.toggleProxy();
        
        if (this.config) {
          this.config.use_proxy = response.use_proxy;
        }
        
        const statusText = response.use_proxy ? 'activated' : 'desactivated';
        this.showToast(`Proxy using ${statusText} successfully`, 'success');
        
        return response;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error during proxy status change';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        throw error;
      } finally {
        this.toggling.proxy = false;
      }
    },

    /**
     * Toogle the use of the host when the proxy fails
     * @returns {Promise<any>} - The response from the server
     */
    async toggleHost() {
      this.toggling.host = true;
      this.error = null;

      try {
        const response = await ConfigService.toggleHost();
        
        if (this.config) {
          this.config.use_host_on_proxy_fail = response.use_host_on_proxy_fail;
        }
        
        const statusText = response.use_host_on_proxy_fail ? 'activated' : 'deactivated';
        this.showToast(`Using host on proxy fail ${statusText} successfully`, 'success');
        
        return response;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error during host status change';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        throw error;
      } finally {
        this.toggling.host = false;
      }
    },

    /**
     * Toggle the reception of alerts
     */
    async toggleAlert() {
      this.toggling.alert = true;
      this.error = null;

      try {
        const response = await ConfigService.toggleAlert();
        
        if (this.config) {
          this.config.receive_alert = response.receive_alert;
        }
        
        const statusText = response.receive_alert ? 'activated' : 'deactivated';
        this.showToast(`ALert reception ${statusText} successfully`, 'success');
        
        return response;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error during alert status change';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        throw error;
      } finally {
        this.toggling.alert = false;
      }
    },
    
    /**
     * Réinitialise the  form 
     */
    resetForm() {
      return this.fetchConfig();
    },

    /**
     * validate all fields of the configuration
     */
    validateAllFields(config: Configuration) {
      this.validateEmail(config.email);
      if (config.use_proxy && config.proxy) {
        this.validateProxies(config.proxy);
      }
      if (config.dns_server) {
        this.validateDns(config.dns_server);
      }
      this.validateScanFrequency(config.scan_frequency);
      this.validateUserAgent(config.user_agent);
    },

    /**
     * Validate email
     * @param email - Email to validate
     */
    validateEmail(email: string) {
      const emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
      
      if (!email) {
        this.validationErrors.email = 'email is required';
      } else if (!emailPattern.test(email)) {
        this.validationErrors.email = 'Envalid email format';
      } else {
        this.validationErrors.email = '';
      }
    },

    /**
     * Validate the proxies
     * @param proxies - Proxies to validate
     */
    validateProxies(proxies: string[]) {
      if (this.config?.use_proxy && (!proxies || proxies.length === 0)) {
        this.validationErrors.proxy = 'At least one proxy is required';
      } else {
        this.validationErrors.proxy = '';
      }
    },

    /**
     * Valide DNS servers
     * @param dnsServers - DNS servers to validate
     */
    validateDns(dnsServers: string[]) {
      if (!dnsServers || dnsServers.length === 0) {
        this.validationErrors.dns = 'At least one DNS server is required';
      } else {
        this.validationErrors.dns = '';
      }
    },

    /**
     * Valide frequency of scan
     * @param frequency - Frequency of scan to validate
     */
    validateScanFrequency(frequency: number) {
      if (!frequency) {
        this.validationErrors.scanFrequency = 'frequency is required';
      } else if (frequency < 120 || frequency > 1000000) {
        this.validationErrors.scanFrequency = 'Frequency must be between 120 and 1000000 seconds';
      } else {
        this.validationErrors.scanFrequency = '';
      }
    },

    /**
     * Validate user agent
     */
    validateUserAgent(userAgent: string) {
      if (!userAgent) {
        this.validationErrors.userAgent = 'user agent is required';
      } else {
        this.validationErrors.userAgent = '';
      }
    }
  }
});