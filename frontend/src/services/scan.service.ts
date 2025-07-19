import api from '@/api';
import {
  Scan,
  ScanCriteriaResponse,
  DefacementScanCriteria,
  DefacementCriteriaResponse,
  SSLCriteriaResponse,
  WebsiteCriteriaResponse,
  DomainCriteriaResponse,
  ToggleActiveResponse
} from '@/types/scan.types';

/**
 * Service for managing scans
 * @module ScanService
 */
export const ScanService = {
  /**
   * fetch all scans
   * @returns {Promise<Scan[]>} - A promise that resolves to an array of scans
   */
  async getScans(): Promise<Scan[]> {
    return api.get('/cerb_scans/scans/').then(response => response.data);
  },

  /**
   * Enable/disable a scan
   * @param scanCode - The code of the scan to enable/disable
   */
  async toggleScanActive(scanCode: string): Promise<ToggleActiveResponse> {
    return api.post(`/cerb_scans/scans/${scanCode}/toggle/`).then(response => response.data);
  },

  /**
   * gets the criteria for a specific scan
   * @param scanCode - The code of the scan to get criteria for
   */
  async getScanCriteria(scanCode: string): Promise<ScanCriteriaResponse> {
    return api.get(`/cerb_scans/scans/${scanCode}/criteria/`).then(response => response.data);
  },

  /**
   * Update the criteria for a specific scan
   * @param criteria - Criteria to update
   */
  async updateDefacementCriteria(criteria: DefacementScanCriteria): Promise<DefacementCriteriaResponse> {
    const payload = {
      acceptance_rate: criteria.acceptance_rate,
      whitelisted_domains: criteria.whitelisted_domains.map(item => item.domain)
    };
    return api.post('/cerb_scans/defacement-criteria/update/', payload).then(response => response.data);
  },

  /**
   * Enables/disables the defacement scan
   * @param enabled - Whether the scan should be enabled or disabled
   */
  async toggleSSLErrorCheck(enabled: boolean): Promise<SSLCriteriaResponse> {
    return api.post('/cerb_scans/ssl-criteria/toggle-ssl-error/', { check_ssl_error: enabled }).then(response => response.data);
  },

  /**
   * Enables/disables the SSL expiry check
   * @param enabled - Whether the check should be enabled or disabled
   */
  async toggleSSLExpiryCheck(enabled: boolean): Promise<SSLCriteriaResponse> {
    return api.post('/cerb_scans/ssl-criteria/toggle-ssl-expiry/', { check_ssl_expiry: enabled }).then(response => response.data);
  },

  /**
   * Update the maximum response time for the website scan
   * @param maxResponseTime - Maximum response time in ms
   */
  async updateMaxResponseTime(maxResponseTime: number): Promise<WebsiteCriteriaResponse> {
    return api.post('/cerb_scans/website-criteria/update-max-response-time/', { max_response_time_ms: maxResponseTime }).then(response => response.data);
  },

  /**
   * Enables/disables the website scan
   * @param enabled - Whether the scan should be enabled or disabled
   */
  async toggleWhoisCheck(enabled: boolean): Promise<DomainCriteriaResponse> {
    return api.post('/cerb_scans/domain-criteria/toggle-whois/', { check_whois: enabled }).then(response => response.data);
  },

  /**
   * Enables/disables the DNS servers check
   * @param enabled - Whether the check should be enabled or disabled
   */
  async toggleDNSServersCheck(enabled: boolean): Promise<DomainCriteriaResponse> {
    return api.post('/cerb_scans/domain-criteria/toggle-dns-servers/', { check_dns_servers: enabled }).then(response => response.data);
  },

  /**
   * Enables/disables the domain expiry check
   * @param enabled - Whether the check should be enabled or disabled
   */
  async toggleDomainExpiryCheck(enabled: boolean): Promise<DomainCriteriaResponse> {
    return api.post('/cerb_scans/domain-criteria/toggle-domain-expiry/', { check_domain_expiry_error: enabled }).then(response => response.data);
  }
};