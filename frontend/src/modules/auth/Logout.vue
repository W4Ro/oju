<template>
    <div class="logout-container">
      <div class="logout-content">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <h2 class="mt-3">Disconnecting...</h2>
        <p>You will be redirected to the login page.</p>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { onMounted } from 'vue';
  import { useRouter } from 'vue-router';
  import { useAuthStore } from '@/stores/auth.store';
  
  const router = useRouter();
  const authStore = useAuthStore();
  
  onMounted(async () => {
    try {
      await authStore.logout();
      
      setTimeout(() => {
        router.push('/authentication/login');
          }, 3000);
      
    } catch (error) {
        setTimeout(() => {
        router.push('/authentication/login');
          }, 3000);
    }
  });
  </script>
  
  <style scoped>
  .logout-container {
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: #f8f9fa;
  }
  
  .logout-content {
    text-align: center;
    padding: 2rem;
    max-width: 400px;
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  
  h2 {
    font-size: 1.5rem;
    margin-top: 1rem;
    color: #495057;
  }
  
  p {
    color: #6c757d;
  }
  </style>