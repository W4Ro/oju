export interface Integration {
    name: string;
    description: string;
    last_updated: string;
    is_active: boolean;
  }
  
  export interface IntegrationResponse {
    count: number;
    next: string | null;
    previous: string | null;
    results: Integration[];
  }
  
  export interface RTIR {
    url: string;
    username: string;
    password?: string;
    is_active: boolean;
    updated_at: string;
  }
  
  export interface Cerebrate {
    url: string;
    api_key: string;
    is_active: boolean;
    refresh_frequency: number;
    refresh_frequency_display?: string;
    updated_at: string;
  }
  
  export interface VirusTotal {
    api_key: string;
    is_active: boolean;
    scan_frequency: number;
    scan_frequency_display?: string;
    updated_at: string;
  }
  
  export interface RefreshFrequencyOption {
    value: number;
    label: string;
  }
  
  export const REFRESH_FREQUENCY_OPTIONS: RefreshFrequencyOption[] = [
    { value: 86400, label: '1 day' },
    { value: 172800, label: '2 days' },
    { value: 259200, label: '3 days' },
    { value: 345600, label: '4 days' },
    { value: 432000, label: '5 days' },
    { value: 518400, label: '6 days' },
    { value: 604800, label: '7 days' }
  ];