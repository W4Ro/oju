<template>
  <div class="container-fluid pt-4">
    <div class="d-flex justify-content-between align-items-center flex-wrap gap-3 mb-4 mt-3">
      <h2 class="mb-0 fs-5 fw-semibold">Filter cases per entity</h2>
      
      <div v-if="!isLoading && !error && entityNames.length > 0" class="dropdown entity-selector">
        <button class="btn btn-outline-secondary dropdown-toggle" type="button" id="entityDropdown" data-bs-toggle="dropdown" aria-expanded="false">
          {{ selectedEntreprise }}
        </button>
        <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="entityDropdown">
          <li v-for="entreprise in entityNames" :key="entreprise">
            <a 
              class="dropdown-item" 
              href="#" 
              @click.prevent="selectedEntreprise = entreprise"
              :class="{ 'active': entreprise === selectedEntreprise }"
            >
              {{ entreprise }}
            </a>
          </li>
        </ul>
      </div>
    </div>

    <div class="card bg-white border-0 rounded-3 mb-4 custom-shadow">
      <div class="card-body p-4">
        <div class="d-flex justify-content-between align-items-center flex-wrap gap-3 pb-3 mb-4 border-bottom">
          <h3 class="mb-0 fs-16 fw-semibold" v-if="selectedEntreprise">Cases - {{ selectedEntreprise }}</h3>
        </div>
        <div v-if="isLoading" class="loading-indicator">Loading...</div>
        <div v-else-if="error" class="error-message">{{ error }}</div>
        <div v-else-if="entityNames.length === 0" class="no-data">No data available.</div>
        <div v-else ref="attackChart" style="width: 100%; height: 400px" class="mx-auto"></div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, ref, watch, onBeforeUnmount } from "vue";
import * as echarts from "echarts";
import api from '@/api/index';

type EntityData = { value: number; name: string }[];

export default defineComponent({
  name: "MonitoringAttaques",
  setup() {
    const attackChart = ref<HTMLDivElement | null>(null);
    let chartInstance: echarts.ECharts | null = null;
    const isLoading = ref(true);
    const error = ref<string | null>(null);
    const isComponentMounted = ref(true);

    const attackData = ref<Record<string, { value: number; name: string }[]>>({});
    const entityNames = ref<string[]>([]);
    const selectedEntreprise = ref('');
    const chartData = ref<{ value: number; name: string }[]>([]);

    const loadData = async () => {
      try {
        if (!isComponentMounted.value) return;
        
        isLoading.value = true;
        error.value = null;
        
        const response = await api.get('/dashboard/entity-cases-by-category/');
        
        if (!isComponentMounted.value) return;
        
        const data = response.data;
        
        attackData.value = data.entities;
        entityNames.value = Object.keys(data.entities);
        
        if (entityNames.value.length > 0) {
          selectedEntreprise.value = entityNames.value[0];
          chartData.value = attackData.value[selectedEntreprise.value];
        }
        
      } catch (err) {
        if (isComponentMounted.value) {
          error.value = "Unable to load data";
          console.error(err);
        }
      } finally {
        if (isComponentMounted.value) {
          isLoading.value = false;
          if (chartInstance) {
            updateChart();
          }
        }
      }
    };

    const initChart = () => {
      if (attackChart.value && isComponentMounted.value) {
        chartInstance = echarts.init(attackChart.value);
        updateChart();
        
        window.addEventListener('resize', handleResize);
      }
    };
    
    const handleResize = () => {
      if (chartInstance && isComponentMounted.value) {
        chartInstance.resize();
      }
    };

    const updateChart = () => {
      if (chartInstance && !isLoading.value && selectedEntreprise.value && isComponentMounted.value) {
        const options = {
          tooltip: { 
            trigger: "item",
            formatter: '{a} <br/>{b}: {c} ({d}%)'
          },
          legend: {
            bottom: "0",
            left: "center",
            itemWidth: 10,
            itemHeight: 10,
            textStyle: { fontSize: 12, color: "#64748B" },
          },
          color: ["#605DFF", "#FE7A36", "#20C997", "#3B82F6"],
          series: [
            {
              name: "issues",
              type: "pie",
              radius: ["40%", "70%"],
              avoidLabelOverlap: true,
              itemStyle: {
                borderRadius: 6,
                borderColor: '#fff',
                borderWidth: 2
              },
              label: {
                show: false,
                position: 'center'
              },
              emphasis: {
                label: {
                  show: true,
                  fontSize: 16,
                  fontWeight: 'bold'
                },
                itemStyle: {
                  shadowBlur: 10,
                  shadowOffsetX: 0,
                  shadowColor: "rgba(0, 0, 0, 0.5)",
                },
              },
              labelLine: {
                show: false
              },
              data: chartData.value,
            },
          ],
        };
        chartInstance.setOption(options);
      }
    };

    watch(selectedEntreprise, (newValue: string) => {
      if (attackData.value && newValue && isComponentMounted.value) {
        chartData.value = attackData.value[newValue];
        updateChart();
      }
    });

    onMounted(() => {
      loadData().then(() => {
        initChart();
      });
    });
    
    onBeforeUnmount(() => {
      isComponentMounted.value = false;
      
      window.removeEventListener('resize', handleResize);
      
      if (chartInstance) {
        chartInstance.dispose();
        chartInstance = null;
      }
    });

    return {
      attackChart,
      selectedEntreprise,
      entityNames,
      isLoading,
      error
    };
  },
});
</script>

<style scoped>
.container-fluid {
  padding-top: 2rem;
}

.mt-3 {
  margin-top: 1.5rem !important;
}

.entity-selector .dropdown-toggle {
  min-width: 200px;
  background-color: white;
  border-color: #d1d5db;
  color: #64748b;
  font-size: 0.875rem;
  text-align: left;
  padding: 0.5rem 1rem;
}

.entity-selector .dropdown-toggle::after {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
}

.entity-selector .dropdown-menu {
  min-width: 200px;
  max-height: 300px;
  overflow-y: auto;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  border-color: #e5e7eb;
}

.dropdown-item {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  color: #64748b;
}

.dropdown-item:hover {
  background-color: #f3f4f6;
  color: #1f2937;
}

.no-data {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
  color: #8695AA;
  font-style: italic;
}

.loading-indicator, .error-message {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
  color: #8695AA;
}

.dropdown-item.active {
  background-color: #eef2ff;
  color: #605dff;
}

.custom-shadow {
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
}

h2.fs-5 {
  font-size: 1.25rem !important;
  color: #111827;
}

.fs-16 {
  font-size: 1rem !important;
}

.border-bottom {
  border-bottom: 1px solid #e5e7eb !important;
}
</style>