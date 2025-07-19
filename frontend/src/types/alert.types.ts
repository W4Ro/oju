export interface Alert {
    id: string;
    displayId?: number;
    date: string;
    entity: string;
    entity_name: string;
    platform: string;
    platform_url: string;
    alert_type: string;
    alert_type_display: string;
    status: string;
    status_display: string;
    details: string;
    updated_at: string;
  }
  
  export interface AlertStatusUpdate {
    status: string;
  }
  
  export interface PaginatedAlerts {
    count: number;
    next: string | null;
    previous: string | null;
    results: Alert[];
  }

  export interface AlertEmail{
    template: string;
    focal_points_emails: string[];
    subject: string;
  }

  export interface EmailAttachment {
    filename: string;
    content: string;
    content_type?: string;
  }

  export interface AlertSendEmail{
    to: string;
    subject: string;
    body: string;
    bcc?: string[];
    cc?: string[];
    attachments?: EmailAttachment[];
  }
  
  export const STATUS_MAPPING: Record<string, string> = {
    'new': 'New',
    'in_progress': 'In progress',
    'resolved': 'Resolved',
    'false_positive': 'False positive'
  };
  
  export const REVERSE_STATUS_MAPPING: Record<string, string> = {
    'New': 'new',
    'In progress': 'in_progress',
    'Resolved': 'resolved',
    'False positive': 'false_positive'
  };
  
  export const ALERT_TYPES = [
    { value: 'ssl', display: 'SSL Problem' },
    { value: 'ssl_expiredSoon', display: 'SSL Certificate expires soon' },
    { value: 'domain_unvailable', display: 'Domain availability issue' },
    { value: 'domain_expiredSoon', display: 'The domain expires soon' },
    { value: 'defacement', display: 'Defacement' },
    { value: 'availability', display: 'Availability problem' },
    { value: 'vt', display: 'Flaged on VirusTotal' },
    { value: 'other', display: 'Other' }
  ];