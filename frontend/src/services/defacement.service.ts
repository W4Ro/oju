import api from '@/api';
import { DefacementDetail, PaginatedDefacements } from '@/types/defacement.types';

/**
 * Service for managing defacements
 * This service provides methods to interact with the defacement API endpoints.
 */
export const DefacementService = {
  /**
   * Retrieve the list of defacements
   * @returns {Promise<PaginatedDefacements>} - A promise that resolves to the paginated defacements data
   */
  async getDefacements(): Promise<PaginatedDefacements> {
    return api.get('/defacements/').then(response => response.data);
  },

  /**
   * Retrieve a specific defacement by its ID
   * @param id - The ID of the defacement to retrieve
   */
  async getDefacement(id: string): Promise<DefacementDetail> {
    return api.get(`/defacements/${id}/`).then(response => response.data);
  },

  /**
   * Retrieve defacements with filtering options
   * @param nextUrl - URL complète de la page suivante
   */
  async getNextPage(nextUrl: string): Promise<PaginatedDefacements> {
    return api.get(nextUrl).then(response => response.data);
  },

  /**
   * Reset the state of a defacement
   * @param id - Identifiant UUID du défacement
   */
  async resetState(id: string): Promise<any> {
    return api.post(`/defacements/${id}/reset_state/`).then(response => response.data);
  },

  /**
   * Reset defacement state
   * Filters are applied directly in the store for client-side filtering
   * but this method allows to obtain initial filtered data if necessary
   * @param params - Filter settings
   */
  async getFilteredDefacements(params: Record<string, any> = {}): Promise<PaginatedDefacements> {
    return api.get('/defacements/', { params }).then(response => response.data);
  }
};