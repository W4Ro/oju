export interface FocalPoint {
    id: string;
    full_name: string;
    phone_numbers: string[];
    email: string;
    function_id: string;
    function_name: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
  }
  
  export interface PaginatedFocalPoints {
    count: number;
    next: string | null;
    previous: string | null;
    results: FocalPoint[];
  }
  
  export interface FocalPointCreate {
    full_name: string;
    phone_numbers: string[];
    email: string;
    function_id: string;
    is_active: boolean;
  }
  
  export interface FocalPointUpdate extends FocalPointCreate {
    id: string;
  }
  
  export interface FocalPointStatusUpdate {
    is_active: boolean;
  }
  
  export interface FocalPointFormErrors {
    full_name: string;
    email: string;
    function_id: string;
    phone: string[];
  }
  
  export interface PhoneInput {
    country: string;
    number: string;
    isValid: boolean;
  }