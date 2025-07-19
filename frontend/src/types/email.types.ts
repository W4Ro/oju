export interface MailConfig {
    smtp_server: string;
    smtp_port: number;
    use_tls: boolean;
    use_ssl: boolean;
    email_host: string;
    email_password: string;
    default_sender_name: string;
    default_reply_to?: string;
    is_active: boolean;
    created_at?: string;
    updated_at?: string;
  }
  
  export interface ToggleActiveResponse {
    message: string;
    is_active: boolean;
  }