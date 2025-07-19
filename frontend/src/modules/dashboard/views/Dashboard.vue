<template>
  <Toast 
    :show="showToast"
    :message="toastMessage"
    :type="toastType"
    @close="closeToast"
  />

  <div v-if="isLoading" class="loading-container">
    <Preloader />
  </div>
  
  <div v-else-if="!hasRequiredPermissions" class="permission-error">
    <div class="error-container">
      <span class="material-symbols-outlined error-icon">error</span>
      <h2>Unauthorized access</h2>
      <p>You do not have required permissions to access the dashboard</p>
      <RouterLink to="authentication/logout" class="back-button">
        <span class="material-symbols-outlined">arrow_back</span>
        Logout
      </RouterLink>
    </div>
  </div>

  <div v-else class="main-content-container overflow-hidden">
    <div class="row equal-height-row g-3 mb-3">
      <div class="col-xxl-7 col-xl-7 col-lg-7">
        <div class="dashboard-card h-100">
          <Statistics v-if="permissions.statistics" />
          <div v-else class="component-placeholder">
            Statistiques unvailable
          </div>
        </div>
      </div>
      <div class="col-xxl-5 col-xl-5 col-lg-5">
        <div class="dashboard-card h-100">
          <TotalCase v-if="permissions.totalCase" />
          <div v-else class="component-placeholder">
            Alertes data unvailable
          </div>
        </div>
      </div>
    </div>
    
    <div class="row equal-height-row g-3 mb-3">
      <div class="col-xxl-6 col-xl-6 col-lg-6">
        <div class="dashboard-card h-100">
          <CaseByEntitie v-if="permissions.caseByEntity" />
          <div v-else class="component-placeholder">
            Statistiques per entity unvailable
          </div>
        </div>
      </div>
      <div class="col-xxl-6 col-xl-6 col-lg-6">
        <div class="dashboard-card h-100">
          <CaseByCategory v-if="permissions.caseByCategory" />
          <div v-else class="component-placeholder">
            Statistique per category unvailable
          </div>
        </div>
      </div>
    </div>
    
    <div class="row equal-height-row g-3 mb-3">
      <div class="col-xxl-6 col-xl-6 col-lg-6">
        <div class="dashboard-card h-100">
          <EntityCase v-if="permissions.entityCase" />
          <div v-else class="component-placeholder">
            Entity datas sunvailable
          </div>
        </div>
      </div>
      <div class="col-xxl-6 col-xl-6 col-lg-6">
        <div class="dashboard-card h-100">
          <LastAlerts v-if="permissions.lastAlerts" />
          <div v-else class="component-placeholder">
            Last alerts unvailable
          </div>
        </div>
      </div>
    </div>
    <div class="row equal-height-row g-3 mb-2">
      <div class="col-xxl-12 col-xl-12 col-lg-12">
        <div class="dashboard-card h-100">
          <AlertsTimeline v-if="permissions.alertsTimeline" />
          <div v-else class="component-placeholder">
            Alerts timeline unvailable
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { onMounted, onBeforeUnmount, ref, computed } from "vue";
  import { useAuthStore } from '@/stores/auth.store';
  import { useRouter } from 'vue-router';
  import Toast from '@/components/Common/Toast.vue';
  import Statistics from "@/components/DashboardMonitoring/statistics/Monitor.vue";
  import TotalCase from "@/components/DashboardMonitoring/TotalCaseChart.vue";
  import EntityCase from "@/components/DashboardMonitoring/EntityByCaseChart.vue";
  import CaseByEntitie from "@/components/DashboardMonitoring/CaseByEntitieChart.vue";
  import CaseByCategory from "@/components/DashboardMonitoring/CaseByCategory.vue";
  import LastAlerts from "@/components/DashboardMonitoring/lastAlerts.vue";
  import Preloader from "@/components/Layouts/Preloader.vue";
  import {hasPermission} from "@/utils/permissions";
  import AlertsTimeline from "@/components/DashboardMonitoring/AlertsTimeline.vue";

  const isLoading = ref(true);
  const authStore = useAuthStore();
  const router = useRouter();
  const showToast = ref(false);
  const toastMessage = ref('');
  const toastType = ref('error');
  const requiredPermissions = ['dashboard_view']

  const showNotification = (message, type = 'error') => {
    toastMessage.value = message;
    toastType.value = type;
    showToast.value = true;
  };
  
  const closeToast = () => {
    showToast.value = false;
  };
  const hasRequiredPermissions = computed(() => {
    return requiredPermissions.some(permission => 
      hasPermission(permission)
    );
  });

  const permissions = computed(() => ({
    statistics: hasPermission('dashboard_view'),
    totalCase: hasPermission('dashboard_view'),
    caseByEntity: hasPermission('dashboard_view') && hasPermission('entities_view'),
    caseByCategory: hasPermission('entities_view'),
    entityCase: hasPermission('dashboard_view') && hasPermission('entities_view'),
    lastAlerts: hasPermission('alerts_view') && hasPermission('dashboard_view') && hasPermission('entities_view'),
    alertsTimeline: hasPermission('dashboard_view'),
  }));

  const equalizeHeights = () => {
    const rows = document.querySelectorAll('.equal-height-row');
    rows.forEach(row => {
      const cards = row.querySelectorAll('.dashboard-card');
      cards.forEach(card => {
        (card as HTMLElement).style.height = 'auto';
      });
      
      let maxHeight = 0;
      cards.forEach(card => {
        const height = (card as HTMLElement).offsetHeight;
        maxHeight = Math.max(maxHeight, height);
      });
      
      if (maxHeight > 0) {
        cards.forEach(card => {
          (card as HTMLElement).style.height = `${maxHeight}px`;
        });
      }
    });
  };

  onMounted(async () => {
    document.body.classList.add("bg-white");
    try {
      await authStore.checkAuth();
      
      if (!hasRequiredPermissions.value) {
        showNotification('Access to dashboard refused: More permissions required', 'error');
      }
    } catch (error) {
      router.push('/authentication/login');
    } finally {
      isLoading.value = false;
    }
    
    setTimeout(equalizeHeights, 100);
    window.addEventListener('resize', equalizeHeights);
  });

  onBeforeUnmount(() => {
    document.body.classList.remove("bg-white");
    window.removeEventListener('resize', equalizeHeights);
  });
</script>

<style lang="scss">
  body {
    &.bg-white {
      .sidebar-area {
        border-right: var(--bs-border-width) var(--bs-border-style)
          var(--bs-border-color) !important;
      }
      .header-area {
        padding: 12px 0 !important;
        &.sticky {
          padding-left: 25px !important;
          padding-right: 25px !important;
        }
        &.mb-4 {
          margin-bottom: 0.5rem !important;
        }
      }
      .footer-area {
        border: var(--bs-border-width) var(--bs-border-style)
          var(--bs-border-color) !important;
      }
    }
  }

  .dashboard-card {
    position: relative;
    background-color: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    overflow: hidden;
    transition: all 0.3s ease;
    height: 100%;
    
    &:hover {
      transform: translateY(-3px);
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
      border-color: #d1d5db;
      
      &::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        border-radius: 8px;
        box-shadow: 0 0 0 2px rgba(96, 93, 255, 0.2);
        pointer-events: none;
      }
    }
    
    & > * {
      height: 100%;
      
      .card {
        margin-bottom: 0 !important;
        border: none !important;
        box-shadow: none !important;
      }
    }
  }
  .equal-height-row {
    display: flex;
    flex-wrap: wrap;
    
    & > [class*="col-"] {
      display: flex;
      flex-direction: column;
    }
  }

  .g-3 {
    --bs-gutter-x: 1rem;
    --bs-gutter-y: 1rem;
  }

  .mb-3 {
    margin-bottom: 1rem !important;
  }

  @media (max-width: 1199.98px) {
    .dashboard-card {
      margin-bottom: 1rem;
    }
  }
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