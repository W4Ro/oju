import api from '@/api';
import type { AVVendor, VendorCreateData, VendorUpdateData, AVVendorResponse } from '@/types/vendor.types';

const vendorService = {
  /**
   * Retrieves the list of vendors
   * @param page Page number for pagination
   */
  getVendors(page = 1): Promise<AVVendorResponse> {
    return api.get('/vendor-list/', { params: { page } })
      .then(response => response.data)
      .catch(error => {
        throw error;
      });
  },

  /**
   * Retrieves a vendor by its ID
   * @param id Vendor ID
   */
  getVendorById(id: string): Promise<AVVendor> {
    return api.get(`/vendor-list/${id}/`)
      .then(response => response.data)
      .catch(error => {
        throw error;
      });
  },

  /**
   * Creates a new vendor
   * @param data Vendor data to create
   */
  createVendor(data: VendorCreateData): Promise<AVVendor> {
    return api.post('/vendor-list/', data)
      .then(response => response.data)
      .catch(error => {
        throw error;
      });
  },

  /**
   * Updates an existing vendor
   * @param id Vendor ID
   * @param data Updated data
   */
  updateVendor(id: string, data: VendorUpdateData): Promise<AVVendor> {
    return api.put(`/vendor-list/${id}/`, data)
      .then(response => response.data)
      .catch(error => {
        throw error;
      });
  },

  /**
   * Deletes a vendor
   * @param id Vendor ID
   */
  deleteVendor(id: string): Promise<boolean> {
    return api.delete(`/vendor-list/${id}/`)
      .then(() => true)
      .catch(error => {
        throw error;
      });
  }
};

export default vendorService;