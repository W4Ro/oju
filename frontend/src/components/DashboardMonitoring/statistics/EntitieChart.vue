<template>
  <div class="chart-container">
    <div v-if="isLoading" class="loading-overlay">Loading...</div>
    <apexchart
      v-if="isClient && !isLoading && chartData.length > 0 && hasNonZeroValues"
      type="area"
      height="325"
      :options="chartOptions"
      :series="[{ name: 'Total Entités', data: chartData }]"
    ></apexchart>
    <div v-else-if="!isLoading && (chartData.length === 0 || !hasNonZeroValues)" class="no-data">
      No data available.
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, defineProps } from "vue";

const props = defineProps({
  entitiesData: {
    type: Object,
    default: () => null
  },
  isLoading: {
    type: Boolean,
    default: false
  }
});

const isClient = ref(false);

const chartData = computed<number[]>(() => {
  return props.entitiesData?.data?.map(item => item.count) || []
})

const hasNonZeroValues = computed(() => {
  if (!chartData.value || chartData.value.length === 0) return false;
  return chartData.value.some(value => value > 0);
});

const categories = computed<string[]>(() => {
  if (!props.entitiesData?.data) return []
  return props.entitiesData.data.map(item => item.month)
});

const maxY = computed<number|undefined>(() => {
   if (chartData.value.length === 0) return undefined;
   const m = Math.max(...chartData.value);
   return m + Math.ceil(m * 0.1);
 });

const chartOptions = computed(() => ({
  chart: {
    type: "area",
    height: 325,
    zoom: { enabled: false },
    toolbar: { show: false },
  },
  colors: ["#605DFF", "#DDE4FF"],
  dataLabels: { enabled: false },
  stroke: {
    curve: "smooth",
    width: [2, 2, 0],
    dashArray: [0, 6, 0],
  },
  grid: { borderColor: "#ffffff" },
  fill: {
    type: "gradient",
    gradient: {
      stops: [0, 90, 100],
      shadeIntensity: 1,
      opacityFrom: 0,
      opacityTo: 0.5,
    },
  },
  xaxis: {
    categories:  categories.value,
    axisTicks: { show: false, color: "#B1BBC8" },
    axisBorder: { show: false, color: "#B1BBC8" },
    labels: {
      style: { colors: "#8695AA", fontSize: "12px" },
    },
  },
  yaxis: {
    min: 0,
    max: maxY.value,
    labels: {style: { colors: "#8695AA", fontSize: "12px" },
    formatter: (val: number) => {
     return val.toFixed(0);
    }},
  },
  legend: {
    show: true,
    position: "top",
    fontSize: "12px",
    horizontalAlign: "left",
    fontFamily: "Inter",
    fontWeight: 400,
    itemMargin: { horizontal: 8, vertical: 0 },
    labels: { colors: "#64748B" },
    markers: {
      width: 9, height: 9,
      offsetX: -2, offsetY: -0.5,
      radius: 2, shape: "diamond",
    },
  },
}));


onMounted(() => {
  isClient.value = true;
});
</script>

<style scoped>
.chart-container {
  position: relative;
  min-height: 325px;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.7);
  z-index: 10;
}

.no-data {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #8695AA;
  font-style: italic;
}
</style>