import { defineStore } from 'pinia';
import { EmailService } from '@/services/email.service';
import { MailConfig } from '@/types/email.types';

interface EmailState {
  mailConfig: MailConfig | null;
  loading: boolean;
  updating: boolean;
  toggling: boolean;
  error: string | null;
  validationErrors: {
    smtp_server: string;
    smtp_port: string;
    email_host: string;
    email_password: string;
    default_sender_name: string;
    default_reply_to: string;
  };
  toast: {
    show: boolean;
    message: string;
    type: 'success' | 'error' | 'warning' | 'info';
    duration: number;
  };
  
}

export const useEmailStore = defineStore('email', {
  state: (): EmailState => ({
    mailConfig: null,
    loading: false,
    updating: false,
    toggling: false,
    error: null,
    validationErrors: {
        smtp_server: '',
        smtp_port: '',
        email_host: '',
        email_password: '',
        default_sender_name: '',
        default_reply_to: ''
    },
    toast: {
      show: false,
      message: '',
      type: 'success',
      duration: 3000
    }
  }),

  getters: {
    getMailConfig: (state) => state.mailConfig,
    isLoading: (state) => state.loading,
    isUpdating: (state) => state.updating,
    isToggling: (state) => state.toggling,
    hasError: (state) => !!state.error,
    hasValidationErrors: (state) => {
      return Object.values(state.validationErrors).some(error => !!error);
    },
    isFormValid: (state) => {
      if (!state.mailConfig) return false;

      const noValidationErrors = !Object.values(state.validationErrors).some(error => !!error);

      const requiredFieldsFilled = !!(
        state.mailConfig.smtp_server &&
        state.mailConfig.smtp_port &&
        state.mailConfig.email_host &&
        state.mailConfig.email_password &&
        state.mailConfig.default_sender_name
    );

      return noValidationErrors && requiredFieldsFilled;
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
     * Fetch the email configuration
     */
    async fetchMailConfig() {
      this.loading = true;
      this.error = null;

      try {
        const response = await EmailService.getMailConfig();
        this.mailConfig = response;
        if (!this.mailConfig.default_reply_to) {
          this.mailConfig.default_reply_to = this.mailConfig.email_host;
        }
        return response;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error loading email configuration';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Update the email configuration
     * @param config - Email configuration data
     */
    async updateMailConfig(config: MailConfig) {
      this.validateAllFields(config);
      
      if (this.hasValidationErrors) {
        this.showToast('Please correct the errors in the form', 'error');
        return false;
      }

      this.updating = true;
      this.error = null;

      try {
        const response = await EmailService.updateMailConfig(config);
        this.mailConfig = response;
        this.showToast('Email configuration updated successfully', 'success');
        return true;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error updating email configuration';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        return false;
      } finally {
        this.updating = false;
      }
    },

    /**
     * Toggle the active status of the email configuration
     * @returns {Promise<any>} - The response from the server
     */
    async toggleActiveStatus() {
      this.toggling = true;
      this.error = null;

      try {
        const response = await EmailService.toggleActiveStatus();
        
        if (this.mailConfig) {
          this.mailConfig.is_active = response.is_active;
        }
        
        const statusText = response.is_active ? 'activated' : 'deactivated';
        this.showToast(`Configuration email ${statusText} successfully`, 'success');
        
        return response;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error toggling email configuration status';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        throw error;
      } finally {
        this.toggling = false;
      }
    },
    
    /**
     * Reset the form to its initial state
     */
    resetForm() {
      return this.fetchMailConfig();
    },
    /**
     * Validate password
     * @param password - Password to validate
     */
    validatePassword(password: string) {
        if (!password) {
        this.validationErrors.email_password = 'password is required';
        } else {
        this.validationErrors.email_password = '';
        }
    },
    
    /**
     * Valide the sender name
     * @param name - Sender name to validate
     */
    validateSenderName(name: string) {
        if (!name) {
        this.validationErrors.default_sender_name = 'Sender name is required';
        } else {
        this.validationErrors.default_sender_name = '';
        }
    },

    /**
     * Validate all fields in the form
     */
    validateAllFields(config: MailConfig) {
        this.validateServer(config.smtp_server);
        this.validatePort(config.smtp_port);
        this.validateEmail(config.email_host);
        this.validatePassword(config.email_password);
        this.validateSenderName(config.default_sender_name);
        if (config.default_reply_to) {
          this.validateReplyTo(config.default_reply_to);
        }
      },

    /**
     * Validate the SMTP server address
     * @param server - SMTP server address to validate
     */
    validateServer(server: string) {
      const ipPattern = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
      const domainPattern = /^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
      
      if (!server) {
        this.validationErrors.smtp_server = 'SMTP server is required';
      } else if (!(ipPattern.test(server) || domainPattern.test(server))) {
        this.validationErrors.smtp_server = 'Enter a valid SMTP server address (IP or domain)';
      } else {
        this.validationErrors.smtp_server = '';
      }
    },

    /**
     * Validate the SMTP port
     */
    validatePort(port: number) {
      if (!port) {
        this.validationErrors.smtp_port = 'SMTP port is required';
      } else if (port < 1 || port > 65535) {
        this.validationErrors.smtp_port = 'Port must be between 1 and 65535';
      } else {
        this.validationErrors.smtp_port = '';
      }
    },

    /**
     * Validate the email address
     */
    validateEmail(email: string) {
      const emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
      
      if (!email) {
        this.validationErrors.email_host = 'Email address is required';
      } else if (!emailPattern.test(email)) {
        this.validationErrors.email_host = 'Please enter a valid email address';
      } else {
        this.validationErrors.email_host = '';
      }
    },

    /**
     * Validate the reply-to email address
     */
    validateReplyTo(email: string) {
      const emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
      
      if (!email) {
        this.validationErrors.default_reply_to = ''; 
      } else if (!emailPattern.test(email)) {
        this.validationErrors.default_reply_to = 'Please enter a valid reply-to email address';
      } else {
        this.validationErrors.default_reply_to = '';
      }
    }
  }
});