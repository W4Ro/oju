<template>
  <div class="card bg-white border-0 rounded-3 mb-4 stats-box">
    <div class="card-body p-4 d-flex flex-column">
      <div class="d-flex justify-content-between flex-wrap gap-2 pb-3 mb-3 border-bottom">
        <h3 class="fs-16 fw-semibold mb-0">Case by categories</h3>
      </div>
      
      <div class="chart-container">
        <apexchart
          v-if="isClient"
          type="bar"
          height="400"
          :options="chartOptions"
          :series="caseData"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue';
import api from '@/api/index';

const isClient = ref(false);

const caseData = ref<Array<{ name: string; data: number[] }>>([]);

const chartOptions = ref<any>({
  chart: {
    id: 'categoriesChart',
    type: 'bar',
    height: 400,
    toolbar: { show: false },
    animations: {
      enabled: true,
      easing: 'easeinout',
      speed: 800,
    },
  },
  colors: [],           
  plotOptions: {
    bar: {
      columnWidth: '55%',
      distributed: true,
      borderRadius: 4,
      dataLabels: { position: 'top' },
    },
  },
  dataLabels: { enabled: false },
  xaxis: {
    categories: [],     
    labels: {
      style: {
        colors: [],      
        fontSize: '12px',
        fontWeight: 500,
      },
    },
    axisBorder: { show: false },
    axisTicks: { show: false },
  },
  yaxis: {
    labels: {
      style: {colors: '#64748B',fontSize: '12px',},
      formatter: (val: number) => {
        return val.toFixed(0);
      }
    },
    min: 0,
    tickAmount: 4,
  },
  grid: {
    borderColor: '#f1f1f1',
    strokeDashArray: 4,
    yaxis: { lines: { show: true } },
    xaxis: { lines: { show: false } },
  },
  tooltip: {
    y: { formatter: (val: number) => `${val} cas` },
    style: { fontSize: '12px', fontFamily: 'inherit' },
  },
  responsive: [
    {
      breakpoint: 576,
      options: {
        plotOptions: { bar: { columnWidth: '70%' } },
        xaxis: {
          labels: { rotate: -45, style: { fontSize: '10px' } },
        },
      },
    },
  ],
});


const handleResize = () => {
  window.ApexCharts?.exec('categoriesChart', 'resize');
};


const fetchData = async () => {
  try {
    const res = await api.get('/dashboard/cases-by-category/');
    const json = res.data;

    
    caseData.value = [
      { name: json.name, data: json.data }
    ];

    
    chartOptions.value = JSON.parse(JSON.stringify({
      ...chartOptions.value,
      colors: json.colors,
      xaxis: {
        ...chartOptions.value.xaxis,
        categories: json.categories,
        labels: {
          style: {
            ...chartOptions.value.xaxis.labels.style,
            colors: json.colors
          }
        }
      }
    }));

    
    window.ApexCharts?.exec('categoriesChart', 'updateOptions', {
      colors: json.colors,
      xaxis: {
        categories: json.categories,
        labels: { style: { colors: json.colors } }
      }
    });
    window.ApexCharts?.exec('categoriesChart', 'updateSeries', caseData.value);
  } catch (err) {
    console.error('Erreur fetch cases-by-category:', err);
  }
};

const REFRESH_INTERVAL = 60_000;
let intervalId: number;

onMounted(() => {
  isClient.value = true;
  fetchData();
  intervalId = window.setInterval(fetchData, REFRESH_INTERVAL);
  window.addEventListener('resize', handleResize);
});

onBeforeUnmount(() => {
  clearInterval(intervalId);
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
.stats-box {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chart-container {
  flex: 1;
  min-height: 400px;
  display: flex;
  flex-direction: column;
}

.chart-container > div {
  flex: 1;
}

.fs-16 {
  font-size: 1rem !important;
}

.border-bottom {
  border-bottom: 1px solid #e5e7eb !important;
}
</style>
