import { defineStore } from 'pinia';
import entityService from '@/services/entityService';
import type { Entity, FocalPoint } from '@/types/entity.types';

export const useEntityStore = defineStore('entity', {
  state: () => ({
    entities: [] as Entity[],
    currentEntity: null as Entity | null,
    loading: false,
    error: null as string | null,
    isCreating: false,
    isUpdating: false,
    isDeleting: false,
    currentPage: 1,
    totalPages: 1,
    hasMoreData: true,
    searchQuery: '',
    toast: {
      show: false,
      message: '',
      type: 'success' as 'success' | 'error' | 'warning',
      duration: 3000
    }
  }),

  getters: {
    sortedEntities: (state) => {
      return [...state.entities].sort((a, b) => {
        const dateA = new Date(a.updated_at);
        const dateB = new Date(b.updated_at);
        return dateB.getTime() - dateA.getTime();
      });
    },

    getEntityById: (state) => (id: string) => {
      return state.entities.find(entity => entity.id === id) || null;
    },

    entityCount: (state) => {
      return state.entities.length;
    }
  },

  actions: {
    showToast(message: string, type: 'success' | 'error' | 'warning' = 'success', duration = 3000) {
      const safeMessage = message || 'An error has occured';
      this.toast = {
        show: true,
        message: safeMessage,
        type,
        duration
      };
      
      setTimeout(() => {
        this.toast.show = false;
      }, duration);
    },

    fetchEntities(page = 1, search = ''): Promise<Entity[]> {
      this.loading = true;
      this.error = null;
      
      if (page === 1 || search !== this.searchQuery) {
        this.entities = [];
        this.hasMoreData = true;
        this.searchQuery = search;
      }
      
      return entityService.getEntities(page, search)
        .then(entities => {
          if (entities.length === 0) {
            this.hasMoreData = false;
          } else {
            const existingIds = new Set(this.entities.map(e => e.id));
            const newEntities = entities.filter(e => !existingIds.has(e.id));
            this.entities = [...this.entities, ...newEntities];
            this.currentPage = page;
          }
          
          return this.entities;
        })
        .catch((error: any) => {
          const errorMessage = error.response?.data?.error || 'Error while loading entities';
          this.showToast(errorMessage, 'error');
          return [] as Entity[];
        })
        .finally(() => {
          this.loading = false;
        });
    },

    async getEntityAlertsByType(id: string): Promise<any> {
      try {
        const response = await entityService.getEntityAlertsByType(id);
        return response;
      } catch (error: any) {
        const message = error.response?.data?.error || `Error fetching alerts by type for entity ${id}`;
        this.showToast(message, 'error');
        throw error;
      }
    },

    async getEntityAlertsByStatus(id: string): Promise<any> {
      try {
        const response = await entityService.getEntityAlertsByStatus(id);
        return response;
      } catch (error: any) {
        const message = error.response?.data?.error || `Error fetching alerts by status for entity ${id}`;
        this.showToast(message, 'error');
        throw error;
      }
    },

    async getEntityStatusDetails(id: string): Promise<any> {
      try {
        const response = await entityService.getEntityStatusDetails(id);
        return response;
      } catch (error: any) {
        const message = error.response?.data?.error || `Error fetching status details for entity ${id}`;
        this.showToast(message, 'error');
        throw error;
      }
    },

    async loadMoreEntities() {
      if (!this.hasMoreData || this.loading) return;
      
      const nextPage = this.currentPage + 1;
      await this.fetchEntities(nextPage, this.searchQuery);
    },

    fetchEntityById(id: string): Promise<Entity | null> {
      this.loading = true;
      this.error = null;
      
      return entityService.getEntityById(id)
        .then(entity => {
          if (entity) {
            this.currentEntity = entity;
            
            const index = this.entities.findIndex(e => e.id === id);
            if (index !== -1) {
              this.entities[index] = entity;
            } else {
              this.entities.push(entity);
            }
          }
          
          return entity;
        })
        .catch((error: any) => {
          const errorMessage = error.response?.data?.error || `Error loading entity ${id}`;
          this.showToast(errorMessage, 'error');
          return null;
        })
        .finally(() => {
          this.loading = false;
        });
    },

    createEntity(entityData: Partial<Entity>): Promise<Entity | null> {
      this.isCreating = true;
      this.error = null;
      
      return entityService.createEntity(entityData)
        .then(createdEntity => {
          this.entities.unshift(createdEntity);
          this.showToast('Entity successfully created', 'success');
          return createdEntity;
        })
        .catch((error: any) => {
          const message = error.response?.data?.error || 'Error creating entity';
          this.error = message;
          this.showToast(message, 'error');
          return null;
        })
        .finally(() => {
          this.isCreating = false;
        });
    },

    updateEntity(id: string, entityData: Partial<Entity>): Promise<Entity | null> {
      this.isUpdating = true;
      this.error = null;
      
      return entityService.updateEntity(id, entityData)
        .then(updatedEntity => {
          const index = this.entities.findIndex(e => e.id === id);
          if (index !== -1) {
            this.entities[index] = updatedEntity;
          }
          
          this.showToast('Entity successfully updated', 'success');
          return updatedEntity;
        })
        .catch((error: any) => {
          const message = error.response?.data?.error || `Error updating entity ${id}`;
          this.error = message;
          this.showToast(message, 'error');
          return null;
        })
        .finally(() => {
          this.isUpdating = false;
        });
    },

    deleteEntity(id: string): Promise<boolean> {
      this.isDeleting = true;
      this.error = null;
      
      return entityService.deleteEntity(id)
        .then(success => {
          if (success) {
            this.entities = this.entities.filter(e => e.id !== id);
            this.showToast('Entity successfully deleted', 'success');
          }
          
          return success;
        })
        .catch((error: any) => {
          const message = error.response?.data?.error || `Error deleting entity ${id}`;
          this.error = message;
          this.showToast(message, 'error');
          return false;
        })
        .finally(() => {
          this.isDeleting = false;
        });
    },
    
    fetchPlatforms(entityId: string): Promise<any[]> {
      this.loading = true;
      this.error = null;
      
      return entityService.fetchPlatforms(entityId)
        .then(platforms => {
          return platforms;
        })
        .catch((error: any) => {
          const errorMessage = error.response?.data?.error || 'Error loading platforms';
          this.showToast(errorMessage, 'error');
          return [] as any[];
        })
        .finally(() => {
          this.loading = false;
        });
    },
    
    createPlatform(platformData: any): Promise<any> {
      this.loading = true;
      this.error = null;
      
      return entityService.createPlatform(platformData)
        .then(createdPlatform => {
          this.showToast('Platform successfully created', 'success');
          return createdPlatform;
        })
        .catch((error: any) => {
          const message = error.response?.data?.error || 'Error creating platform';
          this.showToast(message, 'error');
          throw error;
        })
        .finally(() => {
          this.loading = false;
        });
    },
    
    updatePlatform(id: string, platformData: any): Promise<any> {
      this.loading = true;
      this.error = null;
      
      return entityService.updatePlatform(id, platformData)
        .then(updatedPlatform => {
          this.showToast('Platform successfully udpdated', 'success');
          return updatedPlatform;
        })
        .catch((error: any) => {
          const message = error.response?.data?.error || `Error updating platform ${id}`;
          this.showToast(message, 'error');
          throw error;
        })
        .finally(() => {
          this.loading = false;
        });
    },
    
    deletePlatform(id: string): Promise<boolean> {
      this.loading = true;
      this.error = null;
      
      return entityService.deletePlatform(id)
        .then(success => {
          if (success) {
            this.showToast('Plateform successfully deleted', 'success');
          }
          return success;
        })
        .catch((error: any) => {
          const message = error.response?.data?.error || `Error deleting platform ${id}`;
          this.showToast(message, 'error');
          throw error;
        })
        .finally(() => {
          this.loading = false;
        });
    },
    
    togglePlatformStatus(id: string): Promise<any> {
      this.loading = true;
      this.error = null;
      
      return entityService.togglePlatformStatus(id)
        .then(updatedPlatform => {
          this.showToast('Platform status successfully updated', 'success');
          return updatedPlatform;
        })
        .catch((error: any) => {
          const message = error.response?.data?.error || `Error changing platform status ${id}`;
          this.showToast(message, 'error');
          throw error;
        })
        .finally(() => {
          this.loading = false;
        });
    }
  }
});