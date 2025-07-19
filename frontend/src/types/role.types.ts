export interface Role {
    id: string;
    name: string;
    description?: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
    permission_ids?: string[] | string;
    permissions: string[];
    total_permissions?: number;
  }
  
  export interface Permission {
    id: string;
    feature_name: string;
    permission_name: string;
    permission_code: string;
    description?: string;
  }
  
  export interface RoleCreate {
    name: string;
    description?: string;
    is_active: boolean;
    permissions: string[];
  }
  
  export interface RoleUpdate {
    name: string;
    description?: string;
    is_active: boolean;
    permissions: string[];
  }

export interface PaginatedResponse<T> {
    count: number;
    next: string | null;
    previous: string | null;
    results: T[];
  }