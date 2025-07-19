<template>
  <div class="card bg-white border-0 rounded-3 mb-4">
    <div class="card-body p-4 d-flex flex-column">
      <div class="d-flex justify-content-between align-items-center flex-wrap gap-3 pb-3 mb-3 border-bottom">
        <h3 class="fs-16 fw-semibold mb-0">Entity issues state</h3>
      </div>
      
      <div v-if="isLoading" class="donut-chart-container flex-grow-1 d-flex flex-column align-items-center justify-content-center">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      
      <div v-else-if="error" class="donut-chart-container flex-grow-1 d-flex flex-column align-items-center justify-content-center">
        <div class="component-placeholder">
          Error loading alert data
        </div>
      </div>
      
      <div v-else class="donut-chart-container flex-grow-1 d-flex flex-column align-items-center justify-content-center">
        <div class="donut-wrapper">
          <div v-if="noData" class="no-data-overlay">
            <div class="no-data-message">
              <i class="material-symbols-outlined text-secondary mb-2 fs-40">data_array</i>
              <p>No alerts data available</p>
            </div>
          </div>
          <apexchart
            v-if="isClient"
            type="pie"
            height="320"
            :options="chartOptions"
            :series="chartSeries"
          ></apexchart>
        </div>
      </div>
      
      <div v-if="!noData" class="row categories-legend g-3 mt-2">
        <div class="col-6 col-md-4 col-lg-3" v-for="(label, index) in chartOptions.labels" :key="index" 
             v-show="chartSeries[index] > 0">
          <div class="d-flex align-items-center">
            <span class="category-color-indicator me-2" :style="{ backgroundColor: chartOptions.colors[index] }"></span>
            <span class="category-name text-secondary">{{ label }}</span>
          </div>
          <h4 class="fs-5 fw-semibold mb-0 mt-1">{{ chartSeries[index] }}</h4>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { useRoute } from 'vue-router';
import { useEntityStore } from '@/stores/entityStore';

const route = useRoute();
const entityStore = useEntityStore();
const entityId = computed(() => route.params.id as string);

const isClient = ref(false);
const isLoading = ref(true);
const error = ref(null);
const alertData = ref({});

const noData = computed(() => {
  return !alertData.value || 
         Object.keys(alertData.value).length === 0 || 
         Object.values(alertData.value).every(val => val === 0 || val === null || val === undefined);
});

const chartSeries = computed(() => {
  if (noData.value) {
    return [1]; 
  }
  
  return Object.values(alertData.value);
});

const total = computed(() => {
  if (noData.value) return 0;
  return chartSeries.value.reduce((a, b) => a + b, 0);
});

const chartOptions = computed(() => {
  const statusLabels = noData.value ? ['No Data'] : Object.keys(alertData.value);
  
  const colors = noData.value ? 
    ["#E2E8F0"] : 
    ["#37D80A", "#605DFF", "#AD63F6", "#FD5812"];
  
  return {
    chart: {
      height: 320,
      type: "pie",
      animations: {
        speed: 800,
        animateGradually: {
          enabled: true,
          delay: 150
        },
        dynamicAnimation: {
          enabled: true,
          speed: 350
        }
      },
      dropShadow: {
        enabled: !noData.value,
        top: 0,
        left: 0,
        blur: 3,
        opacity: 0.1
      }
    },
    labels: statusLabels,
    colors: colors,
    dataLabels: {
      enabled: false
    },
    plotOptions: {
      pie: {
        expandOnClick: false,
        donut: {
          size: '70%',
          background: 'transparent',
          labels: {
            show: true,
            name: {
              show: false
            },
            value: {
              show: false
            },
            total: {
              show: true,
              label: noData.value ? 'No Data' : 'Total',
              color: '#64748B',
              fontSize: '14px',
              fontWeight: 600,
              formatter: function () {
                return noData.value ? '0' : total.value.toString();
              }
            }
          }
        }
      }
    },
    stroke: {
      width: 2,
      colors: ["#ffffff"]
    },
    legend: {
      show: false
    },
    tooltip: {
      enabled: !noData.value,
      fillSeriesColor: false,
      style: {
        fontSize: '12px'
      },
      y: {
        formatter: function(value: number) {
          return noData.value ? 'No data' : value + " issues";
        }
      }
    },
    states: {
      hover: {
        filter: {
          type: 'darken',
          value: 0.9
        }
      },
      active: {
        filter: {
          type: 'darken',
          value: 0.4
        }
      }
    }
  };
});

const loadAlertStatusData = async () => {
  if (!entityId.value) return;
  
  isLoading.value = true;
  error.value = null;
  
  try {
    const response = await entityStore.getEntityAlertsByStatus(entityId.value);
    alertData.value = response || {};
  } catch (err: any) {
    error.value = err.message || 'Failed to load alert status data';
    entityStore.showToast(`Error loading alert status data: ${error.value}`, 'error');
  } finally {
    isLoading.value = false;
  }
};

watch(entityId, () => {
  loadAlertStatusData();
});

onMounted(() => {
  isClient.value = true;
  loadAlertStatusData();
});
</script>

<style scoped>
.h-100 {
  height: 100%;
}

.fs-16 {
  font-size: 1rem !important;
}

.border-bottom {
  border-bottom: 1px solid #e5e7eb !important;
}

.donut-chart-container {
  min-height: 320px;
  position: relative;
}

.donut-wrapper {
  width: 100%;
  max-width: 400px;
  position: relative;
}

.no-data-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 5;
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
}

.no-data-message {
  text-align: center;
  color: #64748B;
}

.no-data-message i {
  display: block;
  margin-bottom: 8px;
}

.no-data-message p {
  margin: 0;
  font-size: 14px;
}

.category-color-indicator {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

.categories-legend {
  margin-top: 1rem;
}

.category-name {
  font-size: 0.875rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
  display: inline-block;
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

.fs-40 {
  font-size: 2.5rem !important;
}

@media (max-width: 576px) {
  .categories-legend .col-6 {
    margin-bottom: 0.75rem;
  }
  
  .fs-5 {
    font-size: 1.1rem !important;
  }
}
</style>