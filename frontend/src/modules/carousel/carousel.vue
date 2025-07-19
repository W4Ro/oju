<template>
  <div class="platforms-showcase">
    <ScreenshotCarousel />
  </div>
</template>

<script setup>
import ScreenshotCarousel from '@/components/carousel/ScreenshotCarousel.vue';
</script>

<style scoped>
.platforms-showcase {
  padding: 0;
  margin: 0;
  height: 100vh;
  width: 100vw;
  background-color: #f8f9fa;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  position: fixed;
  top: 0;
  left: 0;
}
</style>