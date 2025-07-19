<template>
  <div class="card bg-white border-0 rounded-3 mb-4">
    <div v-if="isLoading" class="card-body p-4 d-flex justify-content-center align-items-center" style="min-height: 300px;">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    
    <div v-else-if="error" class="card-body p-4 d-flex justify-content-center align-items-center component-placeholder" style="min-height: 300px;">
      Error loading entity details
    </div>
    
    <div v-else class="card-body p-4" style="padding-bottom: 0 !important">
      <div class="mb-3 mb-lg-4">
        <h3 class="mb-0">{{ entityDetails?.name || 'Entity Details' }}</h3>
      </div>
      <div class="row">
        <div class="col-xxl-6 col-xl-6 col-sm-6">
          <div
            class="card bg-primary bg-opacity-10 border-primary border-opacity-10 rounded-3 mb-4 stats-box style-three"
          >
            <div class="card-body p-4">
              <div class="d-flex align-items-center mb-35">
                <div class="flex-shrink-0">
                  <i class="material-symbols-outlined fs-40 text-primary">
                    folder_open
                  </i>
                </div>
                <div class="flex-grow-1 ms-2">
                  <span>Total Cases</span>
                  <h3 class="fs-20 mt-1 mb-0">{{ statusDetails?.total_alerts || 0 }}</h3>
                </div>
              </div>
              <div
                class="d-flex justify-content-between flex-wrap gap-2 align-items-center"
              >
                <span class="fs-12">Saved this month</span>
                <span 
                  class="count fw-medium ms-0" 
                  :class="getSavedPercentageClass(statusDetails?.stats?.saved_this_month_percentage)"
                >
                  {{ formatPercentage(statusDetails?.stats?.saved_this_month_percentage) }}
                </span>
              </div>
            </div>
          </div>
        </div>
        <div class="col-xxl-6 col-xl-6 col-sm-6">
          <div
            class="card bg-danger bg-opacity-10 border-danger border-opacity-10 rounded-3 mb-4 stats-box style-three"
          >
            <div class="card-body p-4">
              <div class="d-flex align-items-center mb-35">
                <div class="flex-shrink-0">
                  <i class="material-symbols-outlined fs-40 text-danger">stacks</i>
                </div>
                <div class="flex-grow-1 ms-2">
                  <span>Open Cases</span>
                  <h3 class="fs-20 mt-1 mb-0">{{ statusDetails?.open_alerts || 0 }}</h3>
                </div>
              </div>
              <div
                class="d-flex justify-content-between flex-wrap gap-2 align-items-center"
              >
                <span class="fs-12">This month</span>
                <span 
                  class="count fw-medium ms-0" 
                  :class="getOpenPercentageClass(statusDetails?.stats?.open_this_month_percentage)"
                >
                  {{ formatPercentage(statusDetails?.stats?.open_this_month_percentage) }}
                </span>
              </div>
            </div>
          </div>
        </div>
        <div class="col-xxl-6 col-xl-6 col-sm-6">
          <div
            class="card bg-success bg-opacity-10 border-success border-opacity-10 rounded-3 mb-4 stats-box style-three"
          >
            <div class="card-body p-4">
              <div class="d-flex align-items-center mb-35">
                <div class="flex-shrink-0">
                  <i class="material-symbols-outlined fs-40 text-success">
                    assignment_turned_in
                  </i>
                </div>
                <div class="flex-grow-1 ms-2">
                  <span>Cases finished</span>
                  <h3 class="fs-20 mt-1 mb-0">{{ statusDetails?.closed_alerts || 0 }}</h3>
                </div>
              </div>
              <div
                class="d-flex justify-content-between flex-wrap gap-2 align-items-center"
              >
                <span class="fs-12">Worked on this month</span>
                <span 
                  class="count fw-medium ms-0" 
                  :class="getWorkedPercentageClass(statusDetails?.stats?.worked_on_this_month_percentage)"
                >
                  {{ formatPercentage(statusDetails?.stats?.worked_on_this_month_percentage) }}
                </span>
              </div>
            </div>
          </div>
        </div>
        <div class="col-xxl-6 col-xl-6 col-sm-6">
          <div
            class="card bg-primary-div bg-opacity-10 border-primary-div border-opacity-10 rounded-3 mb-4 stats-box style-three"
          >
            <RouterLink :to="focalPointLink" class="text-decoration-none">
              <div class="card-body p-4">
                <div class="d-flex align-items-center mb-4">
                  <div class="flex-shrink-0">
                    <i class="material-symbols-outlined fs-40 text-white">
                      group
                    </i>
                  </div>
                  <div class="flex-grow-1 ms-2">
                    <span class="text-white">Focal Point</span>
                    <h3 class="fs-20 mt-1 mb-0 text-white">{{ focalPointsCount > 0 ? focalPointsCount : 0 }}{{ focalPointsCount > 0 ? '+' : '' }}</h3>
                  </div>
                </div>
                <div
                  class="d-flex justify-content-between flex-wrap gap-2 align-items-center"
                >
                  <span class="fs-12 text-white">Focal Points</span>
                  <ul class="ps-0 mb-0 list-unstyled d-flex align-items-center">
                    <li v-if="focalPointsCount === 0" class="text-white fs-12">
                      No focal points assigned
                    </li>
                    
                    <li v-for="(focalPoint, index) in displayedFocalPoints" :key="index" :class="index > 0 ? 'ms-m-15' : ''">
                      <RouterLink to="#">
                        <img
                          :src="getPlaceholderImage(index)"
                          class="wh-34 lh-34 rounded-circle border border-1 border-color-white"
                          :alt="focalPoint.full_name || 'User'"
                        />
                      </RouterLink>
                    </li>
                    
                    <li v-if="remainingFocalPointsCount > 0" class="ms-m-15">
                      <RouterLink
                        to="#"
                        class="wh-34 lh-34 rounded-circle bg-primary d-block text-center text-decoration-none text-white fs-12 fw-medium border border-1 border-color-white"
                      >
                        +{{ remainingFocalPointsCount }}
                      </RouterLink>
                    </li>
                  </ul>
                </div>
              </div>
            </RouterLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { useRoute } from 'vue-router';
import { useEntityStore } from '@/stores/entityStore';
import { hasPermission } from '@/utils/permissions';

const route = useRoute();
const entityStore = useEntityStore();
const entityId = computed(() => route.params.id as string);

const isLoading = ref(true);
const error = ref(null);
const entityDetails = ref(null);
const statusDetails = ref(null);
const focalPoints = ref([]);

const focalPointsCount = computed(() => focalPoints.value.length);

const MAX_VISIBLE_FOCAL_POINTS = 3;

const displayedFocalPoints = computed(() => {
  return focalPoints.value.slice(0, MAX_VISIBLE_FOCAL_POINTS);
});

const remainingFocalPointsCount = computed(() => {
  return Math.max(0, focalPointsCount.value - MAX_VISIBLE_FOCAL_POINTS);
});

const focalPointLink = computed(() => {
  if (hasPermission('focal_points_view')) {
    return `/entities/focalpoints/${entityId.value}`;
  }
  return '#';
});

const formatPercentage = (value) => {
  if (value === undefined || value === null) return '0%';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(2)}%`;
};

const getSavedPercentageClass = (value) => {
  if (value === undefined || value === null) return '';
  return value >= 0 ? 'up' : 'down';
};

const getOpenPercentageClass = (value) => {
  if (value === undefined || value === null) return '';
  return value >= 0 ? 'down' : 'up';
};

const getWorkedPercentageClass = (value) => {
  if (value === undefined || value === null) return '';
  return value >= 0 ? 'up' : 'down';
};

const getPlaceholderImage = (index) => {
  const placeholders = [
    require('@/assets/images/user-16.jpg'),
    require('@/assets/images/user-17.jpg'),
    require('@/assets/images/user-18.jpg')
  ];
  
  return placeholders[index % placeholders.length];
};

const loadEntityDetails = async () => {
  if (!entityId.value) return;
  
  isLoading.value = true;
  error.value = null;
  
  try {
    const entity = await entityStore.fetchEntityById(entityId.value);
    entityDetails.value = entity;
    
    if (entity && entity.focal_points) {
      focalPoints.value = entity.focal_points;
    }
    
    const stats = await entityStore.getEntityStatusDetails(entityId.value);
    statusDetails.value = stats;
  } catch (err) {
    error.value = err.message || 'Failed to load entity details';
    entityStore.showToast(`Error loading entity details: ${error.value}`, 'error');
  } finally {
    isLoading.value = false;
  }
};

watch(entityId, () => {
  loadEntityDetails();
});

onMounted(() => {
  loadEntityDetails();
});
</script>

<style scoped>
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

.mb-35 {
  margin-bottom: 2.188rem;
}

.fs-40 {
  font-size: 2.5rem !important;
}

.wh-34 {
  width: 34px;
  height: 34px;
}

.lh-34 {
  line-height: 34px;
}

.ms-m-15 {
  margin-left: -15px;
}

.bg-primary-div {
  background-color: #605DFF !important;
}

.border-primary-div {
  border-color: #605DFF !important;
}

.fs-12 {
  font-size: 0.75rem !important;
}

.fs-20 {
  font-size: 1.25rem !important;
}

.count.up {
  color: #5bc86d;
}

.count.down {
  color: #f75252;
}

.border-color-white {
  border-color: #fff !important;
}
</style>