import { defineStore } from 'pinia';
import { ScanService } from '@/services/scan.service';
import {
  Scan,
  ScanCriteria,
  DefacementScanCriteria,
  SSLScanCriteria,
  WebsiteScanCriteria,
  DomainScanCriteria,
  WhitelistedDomain
} from '@/types/scan.types';

interface ScanState {
  scans: Scan[];
  selectedScan: Scan | null;
  criteria: {
    defacement: DefacementScanCriteria | null;
    ssl: SSLScanCriteria | null;
    website: WebsiteScanCriteria | null;
    domain: DomainScanCriteria | null;
  };
  loading: boolean;
  criteriaLoading: boolean;
  error: string | null;
  toast: {
    show: boolean;
    message: string;
    type: 'success' | 'error' | 'warning' | 'info';
    duration: number;
  };
}

export const useScanStore = defineStore('scan', {
  state: (): ScanState => ({
    scans: [],
    selectedScan: null,
    criteria: {
      defacement: null,
      ssl: null,
      website: null,
      domain: null
    },
    loading: false,
    criteriaLoading: false,
    error: null,
    toast: {
      show: false,
      message: '',
      type: 'success',
      duration: 3000
    }
  }),

  getters: {
    getDefacementCriteria: (state) => state.criteria.defacement,
    getSSLCriteria: (state) => state.criteria.ssl,
    getWebsiteCriteria: (state) => state.criteria.website,
    getDomainCriteria: (state) => state.criteria.domain,
    getCurrentCriteria: (state) => {
      if (!state.selectedScan) return null;
      
      switch (state.selectedScan.code) {
        case 'defacement':
          return state.criteria.defacement;
        case 'ssl':
          return state.criteria.ssl;
        case 'website':
          return state.criteria.website;
        case 'domain':
          return state.criteria.domain;
        default:
          return null;
      }
    }
  },

  actions: {
    /**
     * Show a toast message
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
     * Get all scans
     */
    async fetchScans() {
      this.loading = true;
      this.error = null;

      try {
        const response = await ScanService.getScans();
        this.scans = response;
        return response;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Returned an error while fetching scans';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Select a scan and fetch its criteria
     * @param scan - Scan object to select
     */
    async selectScan(scan: Scan) {
      this.selectedScan = scan;
      await this.fetchScanCriteria(scan.code);
    },

    /**
     * Get the criteria for a specific scan
     * @param scanCode - Code of the scan to get criteria for
     * @throws {Error} - If an error occurs while fetching the criteria
     */
    async fetchScanCriteria(scanCode: string) {
      this.criteriaLoading = true;
      this.error = null;

      try {
        const response = await ScanService.getScanCriteria(scanCode);
        const defacementCriteria = response.criteria as DefacementScanCriteria;
        switch (scanCode) {
          case 'defacement':
            
            if (!Array.isArray(defacementCriteria.whitelisted_domains)) {
              defacementCriteria.whitelisted_domains = [];
            }
            if (defacementCriteria.whitelisted_domains.length > 0 && typeof defacementCriteria.whitelisted_domains[0] === 'string') {
              defacementCriteria.whitelisted_domains = (defacementCriteria.whitelisted_domains as unknown as string[]).map(domain => ({
                domain
              }));
            }
            this.criteria.defacement = defacementCriteria;
            break;
          case 'ssl':
            this.criteria.ssl = response.criteria as SSLScanCriteria;
            break;
          case 'website':
            this.criteria.website = response.criteria as WebsiteScanCriteria;
            break;
          case 'domain':
            this.criteria.domain = response.criteria as DomainScanCriteria;
            break;
        }
        
        return response;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || `Error fetching criteria for ${scanCode}`;
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        throw error;
      } finally {
        this.criteriaLoading = false;
      }
    },

    /**
     * Enable/disable a scan
     * @param scan - Scan object to toggle
     * @throws {Error} - If an error occurs while toggling the scan status
     */
    async toggleScanStatus(scan: Scan) {
      this.loading = true;
      this.error = null;

      try {
        const response = await ScanService.toggleScanActive(scan.code);
        
        const index = this.scans.findIndex(s => s.code === scan.code);
        if (index !== -1) {
          this.scans[index].is_active = response.is_active;
          this.scans[index].updated_at = new Date().toISOString();
        }
        
        this.showToast(`Scan "${scan.name}" ${response.is_active ? 'enable' : 'disable'} with success.`, 'success');
        return response;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error toggling scan status';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        
        const index = this.scans.findIndex(s => s.code === scan.code);
        if (index !== -1) {
          this.scans[index].is_active = !scan.is_active;
        }
        
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Update the defacement criteria
     * @throws {Error} - If an error occurs while updating the criteria
     */
    async updateDefacementCriteria() {
      if (!this.criteria.defacement) return;
      
      if (!this.criteria.defacement.whitelisted_domains || this.criteria.defacement.whitelisted_domains.length === 0) {
        this.showToast('Please add at least one whitelisted domain', 'error');
        return false;
      }
      
      this.criteriaLoading = true;
      this.error = null;

      try {
        const response = await ScanService.updateDefacementCriteria(this.criteria.defacement);
        this.showToast('Defacement criteria updated successfully', 'success');
        return response;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error while updating defacement criteria';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        throw error;
      } finally {
        this.criteriaLoading = false;
      }
    },

    /**
     * Update the SSL criteria
     * @throws {Error} - If an error occurs while updating the criteria
     */
    async updateSSLCriteria() {
      if (!this.criteria.ssl) return;
      
      this.criteriaLoading = true;
      this.error = null;

      try {
        await ScanService.toggleSSLErrorCheck(this.criteria.ssl.check_ssl_error);
        
        await ScanService.toggleSSLExpiryCheck(this.criteria.ssl.check_ssl_expiry);
        
        this.showToast('SSl criteria updated successfully', 'success');
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error while updating SSL criteria';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        throw error;
      } finally {
        this.criteriaLoading = false;
      }
    },

    /**
     * Update the website criteria
     * @throws {Error} - If an error occurs while updating the criteria
     */
    async updateWebsiteCriteria() {
      if (!this.criteria.website) return;
      
      this.criteriaLoading = true;
      this.error = null;

      try {
        const response = await ScanService.updateMaxResponseTime(this.criteria.website.max_response_time_ms);
        this.showToast('Max response time updated successfully.', 'success');
        return response;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error while updating max response time';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        throw error;
      } finally {
        this.criteriaLoading = false;
      }
    },

    /**
     * Update the domain criteria
     * @throws {Error} - If an error occurs while updating the criteria
     */
    async updateDomainCriteria() {
      if (!this.criteria.domain) return;
      
      this.criteriaLoading = true;
      this.error = null;

      try {
        await ScanService.toggleWhoisCheck(this.criteria.domain.check_whois);
        
        await ScanService.toggleDNSServersCheck(this.criteria.domain.check_dns_servers);
        
        await ScanService.toggleDomainExpiryCheck(this.criteria.domain.check_domain_expiry_error);
        
        this.showToast('Domain criteria updated successfully', 'success');
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || 'Error while updating domain criteria';
        this.error = errorMessage;
        this.showToast(errorMessage, 'error');
        throw error;
      } finally {
        this.criteriaLoading = false;
      }
    },

    /**
     * Save the criteria for the selected scan
     * @throws {Error} - If an error occurs while saving the criteria
     */
    async saveCriteria() {
      if (!this.selectedScan) return;
      
      try {
        switch (this.selectedScan.code) {
          case 'defacement':
            await this.updateDefacementCriteria();
            break;
          case 'ssl':
            await this.updateSSLCriteria();
            break;
          case 'website':
            await this.updateWebsiteCriteria();
            break;
          case 'domain':
            await this.updateDomainCriteria();
            break;
          default:
            throw new Error(`Type error: ${this.selectedScan.code}`);
        }
        
        // Update the scan in the list
        const index = this.scans.findIndex(s => s.code === this.selectedScan!.code);
        if (index !== -1) {
          this.scans[index].updated_at = new Date().toISOString();
        }
        
        return true;
      } catch (error) {
        return false;
      }
    },

    /**
     * Adds a domain to the list of whitelisted domains
     * @throws {Error} - If an error occurs while adding the domain
     * @param domain - Domain to add
     */
    addWhitelistedDomain(domain: string) {
      if (!this.criteria.defacement) return;
      
      const exists = this.criteria.defacement.whitelisted_domains.some(
        item => item.domain.toLowerCase() === domain.toLowerCase()
      );
      
      if (!exists) {
        this.criteria.defacement.whitelisted_domains.push({
          domain
        });
      }
    },

    /**
     * Deletes a domain from the list of whitelisted domains
     * @throws {Error} - If an error occurs while deleting the domain
     * @param index - Index of the domain to delete
     */
    removeWhitelistedDomain(index: number) {
      if (!this.criteria.defacement) return;
      
      this.criteria.defacement.whitelisted_domains.splice(index, 1);
    },

    /**
     * Réinitialize the selected scan and its criteria
     * @throws {Error} - If an error occurs while clearing the selected scan
     */
    clearSelectedScan() {
      this.selectedScan = null;
      this.criteria.defacement = null;
      this.criteria.ssl = null;
      this.criteria.website = null;
      this.criteria.domain = null;
    },

    /**
     * Enables/disables the defacement scan
     * @param enabled - Whether the scan should be enabled or disabled
     */
async toggleSSLError(enabled: boolean) {
    try {
      const response = await ScanService.toggleSSLErrorCheck(enabled);
      this.showToast('SSL error checking status updated successfully', 'success');
      return response;
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || 'Error while updating SSL error checking status';
      this.error = errorMessage;
      this.showToast(errorMessage, 'error');
      throw error;
    }
  },
  
  /**
   * Enables/disables the SSL expiry check
   * @param enabled - Whether the check should be enabled or disabled
   */
  async toggleSSLExpiry(enabled: boolean) {
    try {
      const response = await ScanService.toggleSSLExpiryCheck(enabled);
      this.showToast('SSL expiry checking status updated successfully', 'success');
      return response;
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || 'Error while updating SSL expiry checking status';
      this.error = errorMessage;
      this.showToast(errorMessage, 'error');
      throw error;
    }
  },
  
  /**
   * Enables/disables the WHOIS check
   * @param enabled - Whether the check should be enabled or disabled
   */
  async toggleWhoisCheck(enabled: boolean) {
    try {
      const response = await ScanService.toggleWhoisCheck(enabled);
      this.showToast('WHOIS checking status updated successfully.', 'success');
      return response;
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || 'Error while updating WHOIS checking status';
      this.error = errorMessage;
      this.showToast(errorMessage, 'error');
      throw error;
    }
  },
  
  /**
   *Enables/disables the DNS servers check
   * @param enabled - Whether the check should be enabled or disabled
   */
  async toggleDNSServersCheck(enabled: boolean) {
    try {
      const response = await ScanService.toggleDNSServersCheck(enabled);
      this.showToast('DNS servers checking status updated successfully.', 'success');
      return response;
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || 'Error while updating DNS servers checking status';
      this.error = errorMessage;
      this.showToast(errorMessage, 'error');
      throw error;
    }
  },
  
  /**
   * Enables/disables the domain expiry check
   * @param enabled - Whether the check should be enabled or disabled
   */
  async toggleDomainExpiryCheck(enabled: boolean) {
    try {
      const response = await ScanService.toggleDomainExpiryCheck(enabled);
      this.showToast('Domain expiration checking status updated successfully.', 'success');
      return response;
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || 'Error while updating domain expiration checking status';
      this.error = errorMessage;
      this.showToast(errorMessage, 'error');
      throw error;
    }
  },
  
  /**
   * Update the maximum response time for the website scan
   * @param maxResponseTime - Maximum response time in ms
   */
  async updateMaxResponseTime(maxResponseTime: number) {
    try {
      const response = await ScanService.updateMaxResponseTime(maxResponseTime);
      this.showToast('Max response time updated successfully.', 'success');
      return response;
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || 'Error while updating max response time';
      this.error = errorMessage;
      this.showToast(errorMessage, 'error');
      throw error;
    }
  }
  }
});