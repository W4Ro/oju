export interface Scan {
    id?: string;
    name: string;
    code: string;
    description: string;
    is_active: boolean;
    updated_at: string;
  }
  
  export interface ScanCriteria {
    scan?: number;
  }
  
  export interface DefacementScanCriteria extends ScanCriteria {
    acceptance_rate: number; 
    whitelisted_domains: WhitelistedDomain[];
  }
  
  export interface WhitelistedDomain {
    defacement_criteria?: number;
    domain: string;
  }
  
  export interface SSLScanCriteria extends ScanCriteria {
    check_ssl_error: boolean;
    check_ssl_expiry: boolean;
  }
  
  export interface WebsiteScanCriteria extends ScanCriteria {
    max_response_time_ms: number; 
  }
  
  export interface DomainScanCriteria extends ScanCriteria {
    check_whois: boolean;
    check_dns_servers: boolean;
    check_domain_expiry_error: boolean;
  }
  
  export interface ScanCriteriaResponse {
    scan: Scan;
    criteria: ScanCriteria;
  }
  
  export interface ToggleActiveResponse {
    name: string;
    is_active: boolean;
    success: boolean;
  }
  
  export interface DefacementCriteriaResponse {
    acceptance_rate: number;
    whitelisted_domains: string[];
    success: boolean;
  }
  
  export interface SSLCriteriaResponse {
    check_ssl_error?: boolean;
    check_ssl_expiry?: boolean;
    success: boolean;
  }
  
  export interface WebsiteCriteriaResponse {
    max_response_time_ms: number;
    success: boolean;
  }
  
  export interface DomainCriteriaResponse {
    check_whois?: boolean;
    check_dns_servers?: boolean;
    check_domain_expiry_error?: boolean;
    success: boolean;
  }