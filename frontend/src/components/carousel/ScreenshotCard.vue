<template>
    <div class="screenshot-card" @click="openPlatform">
      <div class="screenshot-container">
        <img
          v-if="!loading && imageUrl && !hasError"
          :src="imageUrl"
          :alt="url"
          class="screenshot-image"
          @error="handleImageError"
        />
        <div v-else-if="loading" class="loading-spinner">
          <div class="spinner"></div>
          <p>Loading...</p>
        </div>
        <div v-else class="screenshot-error">
          <div class="error-content">
            <i class="bi bi-exclamation-triangle-fill"></i>
            <h5>Warning</h5>
            <p>This platform is experiencing a problem</p>
          </div>
        </div>
      </div>
      <div class="platform-url">{{ truncatedUrl }}</div>
    </div>
  </template>
  
  <script>
  import api from '@/api/index';
  
  export default {
    name: 'ScreenshotCard',
    
    props: {
      url: {
        type: String,
        required: true
      },
      screenshot_url: {
        type: String,
        default: null
      }
    },
    
    data() {
      return {
        hasError: false,
        imageUrl: null,
        loading: true
      };
    },
    
    computed: {
      truncatedUrl() {
        if (!this.url) return '';
        let displayUrl = this.url.replace(/^https?:\/\//, '');
        if (displayUrl.length > 25) {
          displayUrl = displayUrl.substring(0, 22) + '...';
        }
        
        return displayUrl;
      }
    },
    
    mounted() {
      if (this.screenshot_url) {
        this.loadImage();
      }else{
        this.loading = false;
        this.hasError = true; // No screenshot URL provided
      } 
    },
    
    methods: {
      openPlatform() {
        window.open(this.url, '_blank');
      },
      
      async loadImage() {
        if (!this.screenshot_url) {
          this.loading = false;
          this.hasError = true;
          return;
        }
        
        this.loading = true;
        
        try {
          const response = await api.get(this.screenshot_url, {
            responseType: 'blob',
            // headers: {
            //   'Cache-Control': 'max-age=3600' 
            // }
          });
          
          this.imageUrl = URL.createObjectURL(response.data);
          this.loading = false;
        } catch (error) {
          this.handleImageError();
          this.hasError = true;
          this.loading = false;
        }
      },
      
      handleImageError() {
        this.hasError = true;
      }
    },
    
    beforeUnmount() {
      if (this.imageUrl) {
        URL.revokeObjectURL(this.imageUrl);
      }
    }
  };
  </script>
  
  <style scoped>
  .loading-spinner {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
    position: absolute;
    top: 0;
    left: 0;
    background-color: rgba(248, 249, 250, 0.7);
  }
  
  .spinner {
    width: 40px;
    height: 40px;
    border: 4px solid rgba(13, 110, 253, 0.2);
    border-radius: 50%;
    border-top-color: #0d6efd;
    animation: spin 1s ease-in-out infinite;
  }
  
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
  
  .screenshot-card {
    background-color: #fff;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
    cursor: pointer;
    transition: transform 0.3s, box-shadow 0.3s;
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 100%;
    margin: 0;
    min-height: 200px;
  }
  
  .screenshot-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  }
  
  .screenshot-container {
    flex: 1;
    overflow: hidden;
    position: relative;
    background-color: #f8f9fa;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 150px; 
  }
  
  .screenshot-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: top center;
    transition: transform 0.5s ease;
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
  }
  
  .screenshot-card:hover .screenshot-image {
    transform: scale(1.05);
  }
  
  .screenshot-error {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: rgba(220, 53, 69, 0.15);
    padding: 0;
  }
  
  .error-content {
    text-align: center;
    padding: 20px; 
    background-color: rgba(220, 53, 69, 0.95);
    color: white;
    border-radius: 8px;
    width: 90%;
    box-shadow: 0 8px 15px rgba(0, 0, 0, 0.25);
    transform: scale(1);
    transition: transform 0.3s ease;
  }
  
  .screenshot-card:hover .error-content {
    transform: scale(1.05);
  }
  
  .screenshot-error i {
    font-size: 2.5rem; 
    margin-bottom: 10px;
    color: white;
  }
  
  .screenshot-error h5 {
    margin-bottom: 8px;
    font-weight: bold;
    font-size: 1.3rem; 
  }
  
  .screenshot-error p {
    margin: 0;
    font-size: 1rem;
  }
  
  .loading-spinner p {
    margin-top: 10px;
    color: #0d6efd;
    font-weight: 500;
    font-size: 0.9rem;
  }
  
  .platform-url {
    padding: 6px; 
    background-color: #f8f9fa;
    border-top: 1px solid #dee2e6;
    font-size: 0.85rem; 
    font-weight: 500;
    text-align: center;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    color: #0d6efd;
    height: 24px; 
    display: flex;
    align-items: center;
    justify-content: center;
  }
  </style>