export interface FocalPoint {
    id: string
    full_name: string
    function: string  // Function ID
    function_name: string
    email: string
    phone_number: string[]
    is_active: boolean
    created_at: string
    updated_at: string
  }
  
  export interface FocalFunction {
    id: string
    name: string
    created_at: string
    updated_at: string
  }
  
  export interface Entity {
    id: string
    name: string
    description?: string
    created_at: string
    updated_at: string
    focal_points: FocalPoint[]
    focal_points_ids?: string[]
    platforms_count?: number
    alerts_count?: string
    alerts_resolution_percentage?: string
  }