import api from '@/api';
import type { Entity, FocalPoint } from '@/types/entity.types';

/**
 * Service for managing entities and their focal points
 */
const entityFocalService = {
  /**
   * Fetch all entities with their focal points
   * @returns {Promise<Entity[]>} - A promise that resolves an array of entities with their focal points
   * @param entityId - Entity ID to fetch focal points for
   */
  getEntityWithFocalPoints(entityId: string): Promise<FocalPoint[]> {
    return api.get(`/entities/${entityId}/focal_points/`)
      .then(response => response.data);
  },
};

export default entityFocalService;