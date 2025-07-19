<template>
  <div class="card bg-white border-0 rounded-3 mb-4">
    <div class="card-body p-4 d-flex flex-column">
      <div class="d-flex justify-content-between align-items-center flex-wrap gap-3 mb-3 mb-lg-4">
        <h3 class="mb-0">Alerts Overview</h3>
      </div>
      
      <div v-if="isLoading" class="d-flex justify-content-center align-items-center" style="height: 260px">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      
      <div v-else-if="error" class="component-placeholder" style="height: 260px">
        Error loading alert data
      </div>
      
      <apexchart
        v-else-if="isClient && !isLoading"
        type="bar"
        height="360"
        :options="chartOptions"
        :series="chartSeries"
      ></apexchart>
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

const loadAlertData = async () => {
  if (!entityId.value) return;
  
  isLoading.value = true;
  error.value = null;
  
  try {
    const response = await entityStore.getEntityAlertsByType(entityId.value);
    alertData.value = response || {};
  } catch (err: any) {
    error.value = err.message || 'Failed to load alert data';
    entityStore.showToast(`Error loading alert data: ${error.value}`, 'error');
  } finally {
    isLoading.value = false;
  }
};

const chartSeries = computed(() => {
  if (!alertData.value || Object.keys(alertData.value).length === 0) {
    return [{
      name: "Alerts",
      data: []
    }];
  }
  
  return [{
    name: "Alerts",
    data: Object.values(alertData.value)
  }];
});

const chartOptions = computed(() => {
  const categories = Object.keys(alertData.value);
  
  return {
    chart: {
      type: "bar",
      height: 360,
      toolbar: {
        show: false,
      },
    },
    colors: ["#3584FC"],
    plotOptions: {
      bar: {
        horizontal: true,
        distributed: true, 
        barHeight: '60%', 
        borderRadius: 4,
      },
    },
    grid: {
      show: true,
      borderColor: "#ECEEF2",
    },
    dataLabels: {
      enabled: false,
    },
    xaxis: {
      categories: categories,
      axisTicks: {
        show: true,
        color: "#ECEEF2",
      },
      axisBorder: {
        show: true,
        color: "#ECEEF2",
      },
      labels: {
        show: true,
        style: {
          colors: "#8695AA",
          fontSize: "12px",
        },
      },
    },
    yaxis: {
      labels: {
        style: {
          colors: "#64748B",
          fontSize: "12px",
        },
      },
      axisBorder: {
        show: true,
        color: "#ECEEF2",
      },
      axisTicks: {
        show: true,
        color: "#ECEEF2",
      },
    },
  };
});

watch(entityId, () => {
  loadAlertData();
});

onMounted(() => {
  isClient.value = true;
  loadAlertData();
});
</script>