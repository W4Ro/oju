import api from '@/api';
import type { Entity, FocalPoint } from '@/types/entity.types';

interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export const entityService = {
  /**
   * Get all entities with optional search and pagination
   * @param page Page number
   * @param search Search term
   * @param has_platforms Filter for entities with platforms
   */
  getEntities(page = 1, search?: string, has_platforms?: boolean): Promise<Entity[]> {
    const params: any = { page };
    if (search) params.search = search;
    if (has_platforms !== undefined) params.has_platforms = has_platforms;

    return api.get('/entities/', { params })
      .then(response => response.data)
      .catch(() => []);
  },

  /**
   * Get entity details by ID
   * @param id Entity ID
   */
  getEntityById(id: string): Promise<Entity | null> {
    return api.get(`/entities/${id}/`)
      .then(response => response.data)
      .catch(() => null);
  },

  /**
   * Get focal points for a specific entity
   * @param id Entity ID
   */
  getEntityFocalPoints(id: string): Promise<FocalPoint[]> {
    return api.get(`/entities/${id}/focal_points/`)
      .then(response => response.data)
      .catch(() => []);
  },

  /**
   * Get entity alert statistics
   * @param id Entity ID
   */
  getEntityAlertStats(id: string): Promise<any> {
    return api.get(`/entities/alert-stats/${id}/`)
      .then(response => response.data)
      .catch(() => null);
  },

  /**
   * Create a new entity
   * @param entityData Data for the new entity
   */
  createEntity(entityData: Partial<Entity>): Promise<Entity> {
    return api.post('/entities/', entityData)
      .then(response => response.data);
  },

  /**
   * Update an existing entity
   * @param id Entity ID
   * @param entityData Updated data for the entity
   */
  updateEntity(id: string, entityData: Partial<Entity>): Promise<Entity> {
    return api.put(`/entities/${id}/`, entityData)
      .then(response => response.data);
  },

  /**
   * Delete an entity
   * @param id Entity ID
   */
  deleteEntity(id: string): Promise<boolean> {
    return api.delete(`/entities/${id}/`)
      .then(() => true);
  },

  /**
   * Get alerts by status for a specific entity
   * @param id Entity ID
   */
  getEntityAlertsByStatus(id: string): Promise<any> {
    return api.get(`/entities/${id}/alerts_by_status/`)
      .then(response => response.data)
      .catch(() => null);
  },

  /**
   * Get alerts by type for a specific entity
   * @param id Entity ID
   */
  getEntityAlertsByType(id: string): Promise<any> {
    return api.get(`/entities/${id}/alerts_by_type/`)
      .then(response => response.data)
      .catch(() => null);
  },

  /**
 * Get all platforms for a specific entity
 * @param entityId Entity ID
 */
  fetchPlatforms(entityId: string): Promise<any[]> {
    return api.get('/entities/platforms/', { 
      params: { entity_id: entityId } 
    })
      .then(response => response.data)
      .catch(() => []);
  },

  /**
 * Create a new platform
 * @param platformData Data for the new platform
 */
  createPlatform(platformData: any): Promise<any> {
    return api.post('/entities/platforms/', platformData)
      .then(response => response.data);
  },

  /**
   * Update an existing platform
   * @param id Platform ID
   * @param platformData Data for the updated platform
   */
  updatePlatform(id: string, platformData: any): Promise<any> {
    return api.put(`/entities/platforms/${id}/`, platformData)
      .then(response => response.data);
  },

  /**
   * Delete a platform
   * @param id platform ID
   */
  deletePlatform(id: string): Promise<boolean> {
    return api.delete(`/entities/platforms/${id}/`)
      .then(() => true);
  },

  /**
   * Toggle the status of a platform
   * @param id Platform ID
   */
  togglePlatformStatus(id: string): Promise<any> {
    return api.post(`/entities/platforms/${id}/toggle_status/`)
      .then(response => response.data);
  },


  /**
   * Get the status details of an entity
   * @param id Entity ID
   */
  getEntityStatusDetails(id: string): Promise<any> {
    return api.get(`/entities/${id}/status_details/`)
      .then(response => response.data)
      .catch(() => null);
  }
};

export default entityService;