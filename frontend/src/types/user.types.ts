export interface User {
    id: string;
    nom_prenom: string;
    username: string;
    email: string;
    role: string | null;
    role_name: string | null;
    is_active: boolean;
    created_at: string;
    updated_at: string;
    permissions?: string[];
  }
  
  export interface UserFilters {
    searchTerm: string;
    status: string;
    role: string;
    ordering: string;
  }
  