<template>
    <div class="screenshot-carousel">
      <div v-if="loading && !error && !platforms.length" class="loading-container">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p>Loading platforms...</p>
      </div>
      
      <div v-else-if="error" class="error-container">
        <div class="alert alert-danger" role="alert">
          <i class="bi bi-exclamation-triangle-fill me-2"></i>
          Error loading data. Please try again later.
        </div>
      </div>
      
      <div v-else-if="!platforms.length" class="empty-container">
        <div class="alert alert-info" role="alert">
          <i class="bi bi-info-circle-fill me-2"></i>
          No platforms available at the moment.
        </div>
      </div>
      
      <div v-else class="carousel-container">
        <button 
          class="nav-button prev-button" 
          @click="goToPrevPage" 
          :disabled="currentPageIndex === 0"
          aria-label="Previous page"
        >
          <i class="bi bi-chevron-left"></i>
        </button>
        
        <div class="screenshot-grid" :class="[`slide-${slideDirection}`]">
          <div 
            v-for="platform in currentPagePlatforms" 
            :key="platform.url"
            class="screenshot-grid-cell"
          >
            <ScreenshotCard
              :url="platform.url"
              :screenshot_url="platform.screenshot_url"
            />
          </div>
        </div>
        
        <button 
          class="nav-button next-button" 
          @click="goToNextPage" 
          :disabled="currentPageIndex === totalPages - 1"
          aria-label="Next page"
        >
          <i class="bi bi-chevron-right"></i>
        </button>
        
        <div class="carousel-indicators">
          <span 
            v-for="index in totalPages" 
            :key="index - 1" 
            class="indicator" 
            :class="{ active: index - 1 === currentPageIndex }"
            @click="goToPage(index - 1)"
            :aria-label="`Go to page ${index}`"
            role="button"
            tabindex="0"
          ></span>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue';
  import ScreenshotCard from './ScreenshotCard.vue';
  import api from '@/api/index';
  
  const platforms = ref([]);
  const loading = ref(true);
  const error = ref(false);
  const currentPageIndex = ref(0);
  const slideDirection = ref('right');
  const rotationInterval = ref(null);
  const reloadInterval = ref(null);
  
  const getItemsPerPage = () => {
    const width = window.innerWidth;
    if (width < 768) return 1;
    if (width < 1200) return 4;
    return 6;
  };
  
  const itemsPerPage = ref(getItemsPerPage());
  
  const loadData = async () => {
    try {
      loading.value = true;
      error.value = false;
      
      const response = await api.get('/dashboard/urls-screenshots/');
      platforms.value = response.data;
      
      if (currentPageIndex.value >= totalPages.value) {
        currentPageIndex.value = Math.max(0, totalPages.value - 1);
      }
    } catch (err) {
      error.value = true;
    } finally {
      loading.value = false;
    }
  };
  
  const totalPages = computed(() => {
    if (!platforms.value.length) return 0;
    return Math.ceil(platforms.value.length / itemsPerPage.value);
  });
  
  const currentPagePlatforms = computed(() => {
    const startIndex = currentPageIndex.value * itemsPerPage.value;
    const endIndex = startIndex + itemsPerPage.value;
    return platforms.value.slice(startIndex, endIndex);
  });
  
  const goToPage = (index) => {
    if (index >= 0 && index < totalPages.value) {
      slideDirection.value = index > currentPageIndex.value ? 'right' : 'left';
      currentPageIndex.value = index;
      resetRotationTimer();
    }
  };
  
  const goToNextPage = async () => {
    if (currentPageIndex.value < totalPages.value - 1) {
      slideDirection.value = 'right';
      currentPageIndex.value++;
    } else {
      slideDirection.value = 'right';
      currentPageIndex.value = 0; 
    }

    if (currentPageIndex.value === totalPages.value - 2) {
      await loadData();
    }
    resetRotationTimer();
  };
  
  const goToPrevPage = () => {
    if (currentPageIndex.value > 0) {
      slideDirection.value = 'left';
      currentPageIndex.value--;
    } else {
      slideDirection.value = 'left';
      currentPageIndex.value = totalPages.value - 1; 
    }
    resetRotationTimer();
  };
  
  const startRotationTimer = () => {
    if (totalPages.value > 1) {
      if (rotationInterval.value) clearInterval(rotationInterval.value);
      rotationInterval.value = setInterval(() => {
        goToNextPage();
      }, 20000); 
    }
  };
  
  const resetRotationTimer = () => {
    if (rotationInterval.value) {
      clearInterval(rotationInterval.value);
      startRotationTimer();
    }
  };
  
  const handleResize = () => {
    const newItemsPerPage = getItemsPerPage();
    
    if (itemsPerPage.value !== newItemsPerPage) {
      const oldItemsPerPage = itemsPerPage.value;
      itemsPerPage.value = newItemsPerPage;
      
      if (platforms.value.length > 0) {
        const firstVisibleItemIndex = currentPageIndex.value * oldItemsPerPage;
        currentPageIndex.value = Math.floor(firstVisibleItemIndex / newItemsPerPage);
      }
    }
  };
  
  const handleKeydown = (e) => {
    if (e.key === 'ArrowLeft') {
      goToPrevPage();
    } else if (e.key === 'ArrowRight') {
      goToNextPage();
    }
  };

  
  onMounted(async () => {
    await loadData();
    
    startRotationTimer();
    
    reloadInterval.value = setInterval(() => {
      loadData();
    }, 15 * 60 * 1000);
    
    window.addEventListener('resize', handleResize);
    window.addEventListener('keydown', handleKeydown);
  });
  
  onBeforeUnmount(() => {
    if (rotationInterval.value) {
      clearInterval(rotationInterval.value);
    }
    
    if (reloadInterval.value) {
      clearInterval(reloadInterval.value);
    }
    
    window.removeEventListener('resize', handleResize);
    window.removeEventListener('keydown', handleKeydown);
  });
  
  watch(platforms, () => {
    resetRotationTimer();
  });
  </script>
  
  <style scoped>
  .screenshot-carousel {
    width: 100vw;
    height: 100vh;
    margin: 0;
    padding: 0;
    overflow: hidden;
    position: fixed;
    top: 0;
    left: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #f8f9fa;
    z-index: 1000;
  }
  
  .loading-container,
  .error-container,
  .empty-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 50vh;
    text-align: center;
    width: 100%;
  }
  
  .carousel-container {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
    position: relative;
  }
  
  .carousel-container:hover .carousel-indicators {
    opacity: 0.6; 
  }
  
  .nav-button {
    position: absolute;
    background-color: rgba(13, 110, 253, 0.8);
    color: white;
    border: none;
    border-radius: 50%;
    width: 50px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s;
    font-size: 1.2rem;
    z-index: 100;
    outline: none;
  }
  
  .prev-button {
    left: 20px;
  }
  
  .next-button {
    right: 20px;
  }
  
  .nav-button:hover:not(:disabled) {
    background-color: rgba(11, 94, 215, 1);
    transform: scale(1.1);
  }
  
  .nav-button:focus {
    box-shadow: 0 0 0 4px rgba(13, 110, 253, 0.3);
  }
  
  .nav-button:disabled {
    opacity: 0.3;
    cursor: not-allowed;
  }
  
  .carousel-indicators {
    position: absolute;
    bottom: 2px;
    left: 0;
    right: 0;
    display: flex;
    justify-content: center;
    gap: 10px;
    z-index: 10;
    opacity: 0.2;
    transition: opacity 0.3s;
    padding: 10px 0;
  }
  
  .indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #dee2e6;
    cursor: pointer;
    transition: all 0.3s;
  }
  
  .indicator.active {
    background-color: #0d6efd;
    transform: scale(1.2);
  }
  
  .indicator:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.3);
  }
  
  .screenshot-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 5px;
    width: 100%;
    height: 100vh;
    padding: 5px;
    box-sizing: border-box;
    margin: 0 auto;
    align-items: start;
  }
  
  .screenshot-grid-cell {
    width: 100%;
    aspect-ratio: 16/9;
    min-height: 0;
    height: 100%;
    display: flex;
    align-items: center;  
    justify-content: center;  
    overflow: hidden; 
    transition: opacity 0.8s cubic-bezier(0.25, 1, 0.5, 1), transform 0.8s cubic-bezier(0.25, 1, 0.5, 1);
  }

  .screenshot-grid-cell :deep(img) {
  width: 100%;
  height: 100%;
  object-fit: cover;  
  max-width: 100%;
}
  
  .slide-right .screenshot-grid-cell {
    animation: slide-in-right 0.8s cubic-bezier(0.25, 1, 0.5, 1);
  }
  
  .slide-left .screenshot-grid-cell {
    animation: slide-in-left 0.8s cubic-bezier(0.25, 1, 0.5, 1);
  }
  
  @keyframes slide-in-right {
    from {
      opacity: 0;
      transform: translateX(100px) scale(0.95);
    }
    to {
      opacity: 1;
      transform: translateX(0) scale(1);
    }
  }
  
  @keyframes slide-in-left {
    from {
      opacity: 0;
      transform: translateX(-100px) scale(0.95);
    }
    to {
      opacity: 1;
      transform: translateX(0) scale(1);
    }
  }
  
  @media (max-width: 1200px) {
    .screenshot-grid {
      grid-template-columns: repeat(2, 1fr);
      gap: 5px;
    }
  }
  
  @keyframes fade-out {
    from {
      opacity: 1;
    }
    to {
      opacity: 0;
    }
  }

  @media (max-width: 768px) {
    .screenshot-grid {
      grid-template-columns: 1fr;
      gap: 5px;
    }
    
    .nav-button {
      width: 40px;
      height: 40px;
      font-size: 1rem;
    }
    
    .prev-button {
      left: 10px;
    }
    
    .next-button {
      right: 10px;
    }
    
    .screenshot-grid-cell {
      min-height: 200px;
      animation: fade-out 0.5s ease-in-out, slide-in-right 0.8s cubic-bezier(0.25, 1, 0.5, 1);
    }
  }
  </style>