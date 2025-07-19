import { defineStore } from 'pinia';
import api from '@/api';
import type { Entity, FocalPoint, FocalFunction } from '@/types/entity.types';
import entityFocalService from '@/services/EntityFocalService';

export const useFocalPointStore = defineStore('entityFocalPoint', {
  state: () => ({
    functions: [] as FocalFunction[],
    activeFocalPoints: [] as FocalPoint[],
    loading: false,
    error: null as string | null,
    entityData: null as { entity: Entity, focalPoints: FocalPoint[] } | null,
    focalPoints: [] as FocalPoint[]
  }),
  actions: {
    fetchFunctions(): Promise<FocalFunction[]> {
      this.loading = true;
      this.error = null;
     
      return api.get('/focal-points/function/')
        .then(response => {
          const data = response.data.results || response.data;
          this.functions = Array.isArray(data) ? data.filter(f => f !== null && f !== undefined) : [];
          return this.functions;
        })
        .catch((error: any) => {
          this.error = error.response?.data?.error || 'Error loading focal functions';
          return [] as FocalFunction[];
        })
        .finally(() => {
          this.loading = false;
        });
    },
    fetchActiveFocalPoints(): Promise<FocalPoint[]> {
      this.loading = true;
      this.error = null;
     
      return api.get('/focal-points/active/')
        .then(response => {
          this.activeFocalPoints = response.data;
          return this.activeFocalPoints;
        })
        .catch((error: any) => {
          this.error = error.response?.data?.error || 'Error loading active focal points';
          return [] as FocalPoint[];
        })
        .finally(() => {
          this.loading = false;
        });
    },
    fetchFocalPointsByFunction(functionId: string): Promise<FocalPoint[]> {
      this.loading = true;
      this.error = null;
     
      return api.get('/focal-points/by_function/', {
        params: { function_id: functionId }
      })
        .then(response => {
          return response.data;
        })
        .catch((error: any) => {
          this.error = error.response?.data?.error || 'Error loading focal points by function';
          return [] as FocalPoint[];
        })
        .finally(() => {
          this.loading = false;
        });
    },
    fetchEntityWithFocalPoints(entityId: string): Promise<FocalPoint[]> {
      this.loading = true;
      this.error = null;
     
      return entityFocalService.getEntityWithFocalPoints(entityId)
        .then(data => {
          this.focalPoints = data;
          return data;
        })
        .catch((err: any) => {
          this.error = err?.response?.data?.error || `Error loading entity focal points ${entityId}`;
          return [];
        })
        .finally(() => {
          this.loading = false;
        });
    }
  }
});
