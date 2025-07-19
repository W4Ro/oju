<template>
  <div v-if="isLoading" class="loading-container">
    <Preloader />
  </div>
  
  <div v-else-if="!hasEntityViewPermission" class="permission-error">
    <div class="error-container">
      <span class="material-symbols-outlined error-icon">error</span>
      <h2>Unauthorized access</h2>
      <p>You do not have permission to view entity details</p>
      <RouterLink to="/dashboard" class="back-button">
        <span class="material-symbols-outlined">arrow_back</span>
        Return to Dashboard
      </RouterLink>
    </div>
  </div>

  <div v-else class="main-content-container overflow-hidden">
    <PageTitle pageTitle="Details" subTitle="Entity" />
    
    <div>
      <div class="row d-flex">
        <div class="col-lg-6 col-md-6 d-flex">
          <EntityOverview v-if="hasEntityViewPermission" class="flex-fill"/>
          <div v-else class="component-placeholder flex-fill">
            Entity overview unavailable
          </div>
        </div>
        <div class="col-lg-6 col-md-6 d-flex">
          <EntityChart v-if="hasEntityViewPermission" class="flex-fill" />
          <div v-else class="component-placeholder flex-fill">
            Entity chart unavailable
          </div>
        </div>
      </div>
      <div class="row justify-content-center">
        <div class="col-lg-12 col-md-6">
          <EntityPlateform v-if="hasPlateformViewPermission" />
          <div v-else class="component-placeholder">
            Entity platform data unavailable
          </div>
        </div>
        <div class="col-lg-12 col-md-6">
          <EntityIssueschart v-if="hasEntityViewPermission" />
          <div v-else class="component-placeholder">
            Entity issues chart unavailable
          </div>
        </div>
      </div>
    </div>
  </div>
  
</template>
  
<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth.store';
import { useEntityStore } from '@/stores/entityStore';
import EntityChart from "@/components/Entity/EntityChart.vue";
import EntityOverview from "@/components/Entity/EntityOverview.vue";
import EntityPlateform from "@/components/Entity/EntityPlateform.vue";
import EntityIssueschart from "@/components/Entity/EntityIssuesChart.vue";
import PageTitle from "@/components/Common/PageTitle.vue";
import Preloader from "@/components/Layouts/Preloader.vue";

export default defineComponent({
  name: "EntitieDetails",
  components: {
    EntityChart,
    EntityOverview,
    EntityPlateform,
    EntityIssueschart,
    PageTitle,
    Preloader
  },
  setup() {
    const isLoading = ref(true);
    const authStore = useAuthStore();
    const entityStore = useEntityStore();
    const router = useRouter();

    const hasEntityViewPermission = computed(() => {
      return authStore.hasPermission('entities_view');
    });
    const hasPlateformViewPermission = computed(() => {
      return authStore.hasPermission('platforms_view');
    });

    onMounted(async () => {
      try {
        await authStore.checkAuth();
        
        if (!hasEntityViewPermission.value) {
          entityStore.showToast('You do not have permission to view entity details', 'error');
          
          setTimeout(() => {
            router.push('/dashboard');
          }, 5000);
        }
      } catch (error) {
        router.push('/authentication/login');
      } finally {
        isLoading.value = false;
      }
    });

    return {
      isLoading,
      hasEntityViewPermission,
      hasPlateformViewPermission,
      authStore,
    };
  }
});
</script>
  
  <style lang="scss" scoped>
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

.permission-error {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

.error-container {
  text-align: center;
  padding: 2rem;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  max-width: 500px;
}

.error-icon {
  font-size: 4rem;
  color: #ef4444;
  margin-bottom: 1rem;
}

.back-button {
  display: inline-flex;
  align-items: center;
  margin-top: 1.5rem;
  padding: 0.5rem 1rem;
  background-color: #3b82f6;
  color: white;
  border-radius: 6px;
  text-decoration: none;
  transition: background-color 0.3s;
  
  &:hover {
    background-color: #2563eb;
  }
  
  .material-symbols-outlined {
    margin-right: 0.5rem;
  }
}

.component-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  padding: 2rem;
  background-color: rgba(243, 244, 246, 0.5);
  color: #6b7280;
  font-style: italic;
  text-align: center;
  border-radius: 6px;
}
</style>