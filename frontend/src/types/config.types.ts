export interface Configuration {
    email: string;
    proxy: string[];
    user_agent: string;
    dns_server: string[];
    max_worker: number;
    use_proxy: boolean;
    use_host_on_proxy_fail: boolean;
    scan_frequency: number;
    receive_alert: boolean;
    last_updated?: string;
  }
  
  export interface ToggleProxyResponse {
    success: boolean;
    use_proxy: boolean;
  }
  
  export interface ToggleHostResponse {
    success: boolean;
    use_host_on_proxy_fail: boolean;
  }
  
  export interface ToggleAlertResponse {
    success: boolean;
    receive_alert: boolean;
  }