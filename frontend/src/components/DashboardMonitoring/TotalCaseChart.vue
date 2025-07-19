<template>
  <div class="card bg-white border-0 rounded-3 mb-4 h-100">
    <div class="card-body p-4 d-flex flex-column">
      <!-- Titre -->
      <div class="d-flex justify-content-between align-items-center gap-2 pb-3 mb-3 border-bottom">
        <h3 class="fs-16 fw-semibold mb-0">{{ titles[currentView] }}</h3>
      </div>

      <!-- Chart + navigation côte à côte -->
      <div class="d-flex flex-grow-1 align-items-center justify-content-center chart-nav-container">
        <button
          class="btn btn-outline-secondary nav-btn"
          :disabled="currentView === 0"
          @click="currentView--"
        >
          <i class="material-symbols-outlined">chevron_left</i>
        </button>

        <div class="donut-chart-container flex-grow-1 d-flex align-items-center justify-content-center">
          <apexchart
            v-if="isClient"
            :key="currentView"
            type="donut"
            height="320"
            :options="currentOptions"
            :series="currentSeries"
          />
        </div>

        <button
          class="btn btn-outline-secondary nav-btn"
          :disabled="currentView === 1"
          @click="currentView++"
        >
          <i class="material-symbols-outlined">chevron_right</i>
        </button>
      </div>

      <div class="categories-legend mt-3">
        <div
          v-for="(count, i) in currentSeries"
          :key="i"
          class="legend-item d-flex flex-column align-items-center text-center me-3"
        >
          <span
            class="category-color-indicator mb-1"
            :style="{ backgroundColor: currentColors[i] }"
          />
          <span class="category-name mb-1" :title="currentLabels[i]">
            {{ currentLabels[i] }}
          </span>
          <span class="fs-5 fw-semibold">{{ count }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import api from '@/api/index';

const isClient = ref(false);

const currentView = ref(0);
const titles = [
  "Today's alerts per categories",
  "Today's alerts by status"
];

const catLabels = ref<string[]>([]);
const catSeries = ref<number[]>([]);
const catColors = ref<string[]>([]);

const statLabels = ref<string[]>([]);
const statSeries = ref<number[]>([]);
const statColors = ref<string[]>([]);

const viewIds = ['alertsByCat', 'alertsByStatus'];

const catTotal = computed(() => catSeries.value.reduce((a, b) => a + b, 0));
const statTotal = computed(() => statSeries.value.reduce((a, b) => a + b, 0));

const catOptions = computed(() => ({
  chart: { id: viewIds[0], type: 'donut' },
  labels: catLabels.value,
  colors: catColors.value,
  plotOptions: {
    pie: {
      donut: {
        size: '70%',
        labels: {
          show: true,
          total: {
            show: true,
            label: 'Total',
            formatter: () => String(catTotal.value)
          }
        }
      }
    }
  },
  dataLabels: { enabled: false },
  tooltip: { y: { formatter: (v: number) => `${v} alertes` } },
  legend: { show: false }
}));

const statOptions = computed(() => ({
  chart: { id: viewIds[1], type: 'donut' },
  labels: statLabels.value,
  colors: statColors.value,
  plotOptions: {
    pie: {
      donut: {
        size: '70%',
        labels: {
          show: true,
          total: {
            show: true,
            label: 'Total',
            formatter: () => String(statTotal.value)
          }
        }
      }
    }
  },
  dataLabels: { enabled: false },
  tooltip: { y: { formatter: (v: number) => `${v} alertes` } },
  legend: { show: false }
}));

const currentSeries = computed(() =>
  currentView.value === 0 ? catSeries.value : statSeries.value
);
const currentLabels = computed(() =>
  currentView.value === 0 ? catLabels.value : statLabels.value
);
const currentColors = computed(() =>
  currentView.value === 0 ? catColors.value : statColors.value
);
const currentOptions = computed(() =>
  currentView.value === 0 ? catOptions.value : statOptions.value
);

const handleResize = () => {
  const id = viewIds[currentView.value];
  window.ApexCharts?.exec(id, 'resize');
};

async function fetchCat() {
  try {
    const { data } = await api.get('/dashboard/alerts-by-category/');
    catLabels.value = data.labels;
    catSeries.value = data.data;
    catColors.value = data.colors;
    window.ApexCharts?.exec(viewIds[0], 'updateOptions', {
      labels: data.labels,
      colors: data.colors
    });
    window.ApexCharts?.exec(viewIds[0], 'updateSeries', data.data);
  } catch (e) {
    console.error('fetchCat error', e);
  }
}
async function fetchStat() {
  try {
    const { data } = await api.get('/dashboard/alerts-by-status/');
    statLabels.value = data.labels;
    statSeries.value = data.data;
    statColors.value = data.colors;
    window.ApexCharts?.exec(viewIds[1], 'updateOptions', {
      labels: data.labels,
      colors: data.colors
    });
    window.ApexCharts?.exec(viewIds[1], 'updateSeries', data.data);
  } catch (e) {
    console.error('fetchStat error', e);
  }
}

const REFRESH = 60_000;
let intervalId: number;

onMounted(() => {
  isClient.value = true;
  fetchCat().then(fetchStat);
  intervalId = window.setInterval(() => {
    fetchCat();
    fetchStat();
  }, REFRESH);
  window.addEventListener('resize', handleResize);
});

onBeforeUnmount(() => {
  window.clearInterval(intervalId);
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
.h-100 { height: 100%; }
.fs-16 { font-size: 1rem !important; }
.border-bottom { border-bottom: 1px solid #e5e7eb !important; }

.chart-nav-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}
.nav-btn {
  flex: 0 0 auto;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.donut-chart-container {
  min-width: 320px;
  position: relative;
}

.categories-legend {
  display: flex;
  overflow-x: auto;
  padding-bottom: 0.5rem;
}
.legend-item {
  flex: 0 0 auto;
  margin-right: 1rem;
}
.category-color-indicator {
  width: 12px; height: 12px; border-radius: 3px; display: block;
}
.category-name {
  font-size: 0.875rem;
  white-space: normal;
  overflow: visible;
  text-overflow: unset;
}
</style>
