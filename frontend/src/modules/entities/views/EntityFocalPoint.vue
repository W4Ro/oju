<template>
    <div class="main-content-container overflow-hidden">
      <PageTitle pageTitle="FocalPoints" subTitle="Entity" />
      <div v-if="loading" class="text-center my-5">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      
      <EntityFocalPoint 
        :entityId="entityId"
        :users="formattedFocalPoints"
        :perPage="10"
        :error="error"
      />
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent, computed, onMounted, ref } from 'vue';
  import { useRoute } from 'vue-router';
  import { useFocalPointStore } from '@/stores/EntityFocalStore';
  import EntityFocalPoint from '@/components/Entity/EntityFocal.vue';
  import PageTitle from'@/components/Common/PageTitle.vue'
  
  export default defineComponent({
    name: 'EntityFocalPointPage',
    components: {
      PageTitle,
      EntityFocalPoint
    },
    setup() {
      const route = useRoute();
      const entityId = computed(() => route.params.id as string);
      const focalPointStore = useFocalPointStore();
      const loading = computed(() => focalPointStore.loading);
      const error = computed(() => focalPointStore.error);

     
      const formattedFocalPoints = computed(() => {
        const focalPoints = focalPointStore.focalPoints || [];
        
        return focalPoints.map(fp => ({
          id: fp.id,
          user: {
            name: fp.full_name
          },
          phoneNumbers: fp.phone_number || [],
          email: fp.email,
          role: fp.function_name,
          status: {
            active: fp.is_active,
            deactive: !fp.is_active
          }
        }));
      });
    
      onMounted(async () => {
         if (entityId.value) {
            await focalPointStore.fetchEntityWithFocalPoints(entityId.value);
           }  
      });
      
      return {
        entityId,
        formattedFocalPoints,
        loading,
        error
      };
    }
  });
  </script>