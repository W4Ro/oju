<template>
    <div class="card bg-white border-0 rounded-3 mb-4">
      <div class="card-body p-4">
        <div class="d-flex justify-content-between align-items-center flex-wrap gap-3 mb-3 mb-lg-4">
          <h3 class="mb-0">Alerts Timeline</h3>
          
          
        </div>
        
        <div v-if="isLoading" class="d-flex justify-content-center align-items-center" style="height: 400px">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        
        <div v-else-if="error" class="d-flex justify-content-center align-items-center component-placeholder" style="height: 400px">
          {{ error }}
        </div>
        
        <div v-else-if="!chartData.dates || chartData.dates.length === 0" class="d-flex justify-content-center align-items-center" style="height: 400px; color: #8695AA; font-style: italic;">
          No alerts data available
        </div>
        
        <div v-else style="margin-bottom: -20px; margin-left: -13px; margin-top: -8px">
          <apexchart 
            v-if="isClient" 
            type="line" 
            height="400" 
            :options="chartOptions" 
            :series="chartSeries"
          ></apexchart>
        </div>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, computed, onMounted, onBeforeUnmount, watch } from "vue";
  import api from '@/api/index';
  
  const isClient = ref(false);
  const isLoading = ref(true);
  const error = ref<string | null>(null);
  const isComponentMounted = ref(true);
  const chartData = ref<{dates: string[], counts: number[]}>({ dates: [], counts: [] });
  const selectedRange = ref('30d');
  

  
  const getFilteredData = () => {
    if (!chartData.value.dates.length) return { dates: [], counts: [] };
    
    const now = new Date();
    let startDate: Date;
    
    switch (selectedRange.value) {
      case '7d':
        startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        break;
      case '30d':
        startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        break;
      case '90d':
        startDate = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000);
        break;
      case '1y':
        startDate = new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000);
        break;
      default: // 'max'
        return chartData.value;
    }
    
    const startDateStr = startDate.toISOString().split('T')[0];
    const startIndex = chartData.value.dates.findIndex(date => date >= startDateStr);
    
    if (startIndex === -1) return chartData.value;
    
    return {
      dates: chartData.value.dates.slice(startIndex),
      counts: chartData.value.counts.slice(startIndex)
    };
  };
  
  const filteredData = computed(() => getFilteredData());
  
  const chartSeries = computed(() => [{
    name: "Daily Alerts",
    data: filteredData.value.counts
  }]);
  
  const chartOptions = computed(() => ({
    chart: {
      id: 'alertsTimelineChart',
      height: 400,
      type: "line",
      zoom: { 
        enabled: true,
        type: 'x',
        autoScaleYaxis: true
      },
      pan: {
        enabled: true,
        type: 'x'
      },
      toolbar: { 
        show: false,
        tools: {
          download: true,
          selection: true,
          zoom: true,
          zoomin: true,
          zoomout: true,
          pan: true,
          reset: true
        }
      },
      animations: {
        enabled: true,
        easing: 'easeinout',
        speed: 800
      }
    },
    dataLabels: { 
      enabled: false 
    },
    colors: ["#3584FC"],
    stroke: { 
      curve: "smooth", 
      width: 2 
    },
    grid: { 
      show: true, 
      borderColor: "#ECEEF2",
      strokeDashArray: 3
    },
    markers: { 
      size: 0,
      hover: { 
        size: 6,
        sizeOffset: 3
      } 
    },
    xaxis: {
      categories: filteredData.value.dates,
      type: 'datetime',
      labels: { 
        style: { 
          colors: "#8695AA", 
          fontSize: "12px" 
        },
        datetimeUTC: false
      },
      axisBorder: {
        show: true,
        color: "#ECEEF2"
      },
      axisTicks: {
        show: true,
        color: "#ECEEF2"
      }
    },
    yaxis: {
      labels: { 
        style: { 
          colors: "#64748B", 
          fontSize: "12px" 
        }, 
        formatter: (val: number) => Math.floor(val).toString()
      },
      min: 0,
      forceNiceScale: true
    },
    tooltip: {
      enabled: true,
      theme: 'light',
      x: {
        format: 'dd MMM yyyy'
      },
      y: {
        formatter: (val: number) => `${val} alert${val !== 1 ? 's' : ''}`
      },
      marker: {
        show: true
      }
    },
    responsive: [{
      breakpoint: 768,
      options: {
        chart: {
          height: 300
        },
        legend: {
          position: 'bottom'
        }
      }
    }]
  }));
  
  const setTimeRange = (range: string) => {
    selectedRange.value = range;
  };
  
  const loadData = async () => {
    try {
      if (!isComponentMounted.value) return;
      
      isLoading.value = true;
      error.value = null;
      
      const response = await api.get('/dashboard/alerts-timeline/');
      
      if (!isComponentMounted.value) return;
      
      chartData.value = response.data;
    } catch (err: any) {
      if (isComponentMounted.value) {
        error.value = "Unable to load timeline data";
        console.error('Timeline data error:', err);
      }
    } finally {
      if (isComponentMounted.value) {
        isLoading.value = false;
      }
    }
  };
  
  onMounted(() => {
    isClient.value = true;
    loadData();
  });
  
  onBeforeUnmount(() => {
    isComponentMounted.value = false;
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
  
  .btn-group .btn.active {
    background-color: #3584FC;
    border-color: #3584FC;
    color: white;
  }
  
  .btn-group .btn-outline-secondary {
    border-color: #d1d5db;
    color: #64748b;
    font-size: 0.875rem;
  }
  
  .btn-group .btn-outline-secondary:hover {
    background-color: #f8f9fa;
    border-color: #adb5bd;
  }
  </style>