export interface Defacement {
    id: string; 
    date: string; 
    entity_name: string; 
    platform_url: string; 
    is_defaced: boolean; 
    displayId?: number; 
  }
  
  export interface DefacementDetail extends Defacement {
    last_state_tree: string; 
    normal_state_tree: string; 
    details: string; 
  }
  
  export interface PaginatedDefacements {
    count: number;
    next: string | null;
    previous: string | null;
    results: Defacement[];
  }
  
  export interface DefacementStateReset {
    id: string;
  }
  
  export const DEFACEMENT_STATUS_MAPPING = {
    true: 'Defaced',
    false: 'Safe'
  };
  
  export interface DefacementFilters {
    searchTerm?: string; 
    is_defaced?: boolean; 
    entity?: string; 
    platform?: string; 
    date_after?: string; 
    date_before?: string; 
    entity_name?: string; 
    platform_url?: string; 
    page?: number; 
  }