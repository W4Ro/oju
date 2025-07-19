export interface SystemLog {
    id: string;
    username: string;
    details: any; 
    created_at: string;
    title?: string; 
    description?: string; 
    performed_by?: string; 
    date?: string; 
  }
  
  export interface LogFilters {
    start_date?: string;
    end_date?: string;
    start_time?: string;
    end_time?: string;
    name?: string;
    details?: string;
    search?: string;
    ordering?: string;
    page?: number;
  }
  
  export interface ExportOptions {
    format: 'csv' | 'xlsx';
    filters: LogFilters;
  }
  
  export interface LogsResponse {
    count: number;
    next: string | null;
    previous: string | null;
    results: SystemLog[];
  }