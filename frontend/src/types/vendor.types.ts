export interface AVVendor {
    id: string;
    name: string;
    contact: string;
    comments: string | null;
    created_at: string;
    updated_at: string;
  }
  
  export interface VendorCreateData {
    name: string;
    contact: string;
    comments?: string;
  }
  
  export interface VendorUpdateData {
    name: string;
    contact: string;
    comments?: string;
  }
  
  export interface AVVendorResponse {
    count: number;
    next: string | null;
    previous: string | null;
    results: AVVendor[];
  }
  
  export interface ValidationErrors {
    name: string;
    contact: string;
    comments: string;
  }