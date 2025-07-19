export interface FocalFunction {
    id: string;
    name: string;
    created_at: string;
    updated_at: string;
  }
  
  export interface PaginatedFocalFunctions {
    count: number;
    next: string | null;
    previous: string | null;
    results: FocalFunction[];
  }
  
  export interface FocalFunctionCreate {
    name: string;
  }
  
  export interface FocalFunctionUpdate {
    id: string;
    name: string;
  }