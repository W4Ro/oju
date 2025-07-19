<template>
  <div class="card bg-white border-0 rounded-3 mb-4">
    <div class="card-body p-4">
      <div class="d-flex justify-content-between align-items-center flex-wrap gap-3 mb-3 mb-lg-4">
        <h3 class="mb-0">Most impacted Entities</h3>
        
        <div v-if="!isLoading && !error && allEntities.length > 0" class="dropdown entity-selector" >
          <button class="btn btn-outline-secondary dropdown-toggle" type="button" id="entityDropdown" data-bs-toggle="dropdown" aria-expanded="false" >
            {{ selectedEntities.length === allEntities.length ? 'All entities' : 
            selectedEntities.length === 1 ? selectedEntities[0] : 
            `${selectedEntities.length} entités sélectionnées` }}
          </button>
          <ul class="dropdown-menu dropdown-menu-end py-2" aria-labelledby="entityDropdown">
            <li class="px-3 pb-2 border-bottom">
              <div class="form-check">
                <input class="form-check-input" type="checkbox" id="select-all" v-model="selectAll" @change="toggleAllEntities">
                <label class="form-check-label fw-semibold" for="select-all">
                  Show all
                </label>
              </div>
            </li>
            <li v-for="entity in allEntities" :key="entity" class="px-3 py-1">
              <div class="form-check">
                <input class="form-check-input" type="checkbox" :id="`entity-${entity}`" 
                       :value="entity" v-model="selectedEntities"
                       @change="checkSelection">
                <label class="form-check-label" :for="`entity-${entity}`">
                  {{ entity }}
                </label>
              </div>
            </li>
          </ul>
        </div>
      </div>
      <div v-if="isLoading" class="loading-indicator">Loading...</div>
      <div v-else-if="error" class="error-message">{{ error }}</div>
      <div v-else-if="filteredData.length === 0 || !casesData.length" class="no-data">
        No data available.
      </div>
      <div v-else style="margin-bottom: -20px; margin-left: -13px; margin-top: -8px">
        <apexchart 
          v-if="isClient" 
          type="line" 
          height="366" 
          :options="chartOptions" 
          :series="filteredData"
        ></apexchart>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, watch, onBeforeUnmount} from "vue";
import api from '@/api/index';

export default defineComponent({
  name: "EntityCasesChart",
  setup() {
    const isClient = ref(false);
    const isLoading = ref(true);
    const error = ref<string | null>(null);
    const isComponentMounted = ref(true);
    
    const allEntities = ref([]);
    const selectedEntities = ref<string[]>([]);
    const selectAll = ref(true);
    const casesData = ref<Array<{name: string, [key: string]: any}>>([]);
    const categories = ref([]);
    const colors = ref([]);
    
    const toggleAllEntities = () => {
      if (selectAll.value) {
        selectedEntities.value = [...allEntities.value];
      } else {
        selectedEntities.value = [];
        if (selectedEntities.value.length === 0) {
          selectedEntities.value = [allEntities.value[0]];
          selectAll.value = false;
        }
      }
    };
    
    const checkSelection = () => {
      selectAll.value = selectedEntities.value.length === allEntities.value.length;
      
      if (selectedEntities.value.length === 0) {
        selectedEntities.value = [allEntities.value[0]];
      }
    };

    const filteredData = computed(() => {
      return casesData.value.filter(entity => selectedEntities.value.includes(entity.name));
    });

    const chartOptions = ref({
      chart: {
        id: 'entitiesChart',
        height: 366,
        type: "line",
        zoom: { enabled: false },
        toolbar: { 
          show: false,
        },
      },
      dataLabels: { enabled: false },
      colors: colors,
      stroke: { curve: "smooth", width: 2 },
      grid: { show: true, borderColor: "#ECEEF2" },
      markers: { size: 4, hover: { size: 5 } },
      xaxis: {
        categories: categories,
        labels: { style: { colors: "#8695AA", fontSize: "12px" } },
      },
      yaxis: {
        labels: { style: { colors: "#64748B", fontSize: "12px" }, 
        formatter: (val: number) => {
        return val.toFixed(0);
      }},
      },
      legend: { position: "top", horizontalAlign: "left", labels: { colors: "#64748B" } },
    });

    const loadData = async () => {
      try {
        if (!isComponentMounted.value) return;
        
        isLoading.value = true;
        error.value = null;
        
        const response = await api.get('/dashboard/most-impacted-entities/');
        
        if (!isComponentMounted.value) return;
        
        const data = response.data;
        
        casesData.value = data.entities;
        categories.value = data.categories;
        colors.value = data.colors;
        
        allEntities.value = data.entities.map((entity: any) => entity.name);
        selectedEntities.value = [...allEntities.value];
        
        const nonReactiveOptions = JSON.parse(JSON.stringify({
          ...chartOptions.value,
          xaxis: {
            ...chartOptions.value.xaxis,
            categories: data.categories
          },
          colors: data.colors
        }));
    
        chartOptions.value = nonReactiveOptions;
      } catch (err) {
        if (isComponentMounted.value) {
          error.value = "Unable to load data";
          console.error(err);
        }
      } finally {
        if (isComponentMounted.value) {
          isLoading.value = false;
        }
      }
    };

    watch(selectedEntities, (newVal) => {
      if (newVal.length === 0) {
        selectedEntities.value = [allEntities.value[0]];
        selectAll.value = false;
      } else if (newVal.length === allEntities.value.length) {
        selectAll.value = true;
      } else {
        selectAll.value = false;
      }
    });

    onMounted(() => {
      isClient.value = true;
      loadData();
    });

    onBeforeUnmount(() => {
      isComponentMounted.value = false;
    });

    return {
      isClient,
      isLoading,
      error,
      allEntities,
      selectedEntities,
      selectAll,
      toggleAllEntities,
      checkSelection,
      casesData,
      filteredData,
      chartOptions,
    };
  },
});
</script>

<style scoped>
.entity-selector .dropdown-toggle {
  min-width: 180px;
  background-color: white;
  border-color: #d1d5db;
  color: #64748b;
  font-size: 0.875rem;
  text-align: left;
}

.entity-selector .dropdown-toggle::after {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
}

.entity-selector .dropdown-menu {
  min-width: 220px;
  max-height: 300px;
  overflow-y: auto;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  border-color: #e5e7eb;
}

.dropdown-menu .form-check {
  padding-left: 1.75rem;
}

.dropdown-menu .form-check-input {
  margin-left: -1.75rem;
}

.form-check-label {
  cursor: pointer;
  user-select: none;
}

.no-data {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 366px;
  color: #8695AA;
  font-style: italic;
}
</style>