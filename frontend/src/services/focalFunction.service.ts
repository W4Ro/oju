import api from '@/api';
import { FocalFunction, PaginatedFocalFunctions, FocalFunctionCreate, FocalFunctionUpdate } from '@/types/focalFunction.types';

/**
 * Service for the management of focal point functions
 */
export const FocalFunctionService = {
  /**
   * Retrieves the list of functions
   */
  async getFocalFunctions(): Promise<PaginatedFocalFunctions> {
    return api.get('/focal-points/function/').then(response => response.data);
  },

  /**
   * Retrieves details of a specific function
   * @param id - Function ID
   */
  async getFocalFunction(id: string): Promise<FocalFunction> {
    return api.get(`/focal-points/function/${id}/`).then(response => response.data);
  },

  /**
   * Retrieves the next page from a URL
   * @param nextUrl - Full URL of the next page
   */
  async getNextPage(nextUrl: string): Promise<PaginatedFocalFunctions> {
    return api.get(nextUrl).then(response => response.data);
  },

  /**
   * Create a new function
   * @param data - Data of the function to be created
   */
  async createFocalFunction(data: FocalFunctionCreate): Promise<FocalFunction> {
    return api.post('/focal-points/function/', data).then(response => response.data);
  },

  /**
   * Updates an existing function
   * @param id - Function ID
   * @param data - Update data
   */
  async updateFocalFunction(id: string, data: FocalFunctionUpdate): Promise<FocalFunction> {
    return api.put(`/focal-points/function/${id}/`, data).then(response => response.data);
  },

  /**
   * Deletes a function
   * @param id - Function ID
   */
  async deleteFocalFunction(id: string): Promise<void> {
    return api.delete(`/focal-points/function/${id}/`).then(response => response.data);
  }
};

