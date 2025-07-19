import api from '@/api';
import { FocalPoint, PaginatedFocalPoints, FocalPointCreate, FocalPointUpdate, FocalPointStatusUpdate } from '@/types/focalPoint.types';

/**
 * Service for managing focal points
 */
export const FocalPointService = {
  /**
   * Retrieves a list of focal points
   */
  async getFocalPoints(params: Record<string, any> = {}): Promise<PaginatedFocalPoints> {
    return api.get('/focal-points/', { params }).then(response => response.data);
  },

  /**
   * Retrieves focal points by function
   * @param functionId - fonction ID
   */
  async getFocalPointsByFunction(functionId: string, params: Record<string, any> = {}): Promise<PaginatedFocalPoints> {
    return api.get(`/focal-points/by_function/`, { 
      params: { ...params, function_id: functionId } 
    }).then(response => response.data);
  },

  /**
   * Retrieves a focal point by ID
   * @param id - Focal Point ID
   */
  async getFocalPoint(id: string): Promise<FocalPoint> {
    return api.get(`/focal-points/${id}/`).then(response => response.data);
  },

  /**
   * Gets the next page of focal points
   * @param nextUrl - URL for the next page
   */
  async getNextPage(nextUrl: string): Promise<PaginatedFocalPoints> {
    return api.get(nextUrl).then(response => response.data);
  },

  /**
   * Create a new focal point
   * @param data - Data for the focal point to be created
   */
  async createFocalPoint(data: FocalPointCreate): Promise<FocalPoint> {
    return api.post('/focal-points/', data).then(response => response.data);
  },

  /**
   * Update an existing focal point
   * @param id - Focal Point ID
   * @param data - Update data for the focal point
   */
  async updateFocalPoint(id: string, data: FocalPointUpdate): Promise<FocalPoint> {
    return api.put(`/focal-points/${id}/`, data).then(response => response.data);
  },

  /**
   * Change the status of a focal point
   * This method toggles the active status of a focal point.
   * @param id - Focal Point ID
   * @param data - Status update data
   */
  async toggleFocalPointStatus(id: string, data: FocalPointStatusUpdate): Promise<{ success: boolean; is_active: boolean }> {
    return api.post(`/focal-points/${id}/toggle_status/`, data).then(response => response.data);
  },

  /**
   * Delete a focal point
   * @param id - Focal Point ID
   */
  async deleteFocalPoint(id: string): Promise<void> {
    return api.delete(`/focal-points/${id}/`).then(response => response.data);
  },

  /**
   * Search for focal points
   * This method allows searching for focal points based on a query string.
   * @param query - Query string to search for focal points
   */
  async searchFocalPoints(query: string): Promise<PaginatedFocalPoints> {
    return api.get('/focal-points/search/', { 
      params: { query } 
    }).then(response => response.data);
  },

  /**
   * Get active focal points
   * This method retrieves a list of active focal points.
   */
  async getActiveFocalPoints(): Promise<PaginatedFocalPoints> {
    return api.get('/focal-points/active/').then(response => response.data);
  }
};