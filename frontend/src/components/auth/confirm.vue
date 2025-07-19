<template>
    <div class="confirm-mail-container">
      <div class="confirm-mail-wrapper">
        <div class="confirm-mail-content">
          <div class="confirm-mail-header">
            <h1 class="confirm-mail-title">Oju</h1>
            <p class="confirm-mail-subtitle">Secure Access Portal</p>
          </div>
  
          <div class="confirm-mail-body">
            <div class="logo-container">
              <img 
                src="@/assets/images/logo.svg" 
                alt="Oju Logo" 
                class="logo"
              />
            </div>
  
            <div class="message-icon-container">
              <i class="material-symbols-outlined message-icon">mark_email_read</i>
            </div>
  
            <h4 class="success-title">Success!</h4>
            
            <p class="success-message">
              An email has been sent to <strong>{{ userEmail }}</strong>. 
              Please check for an email from our company and click on the 
              included link to reset your password.
            </p>
  
            <RouterLink
              to="/authentication/login"
              class="confirm-mail-button"
            >
              <i class="material-symbols-outlined">check_circle</i>
              Confirm Mail
            </RouterLink>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script lang="ts">
    import { defineComponent, ref, onMounted } from "vue";
    import { useRoute } from "vue-router";

    export default defineComponent({
      name: "ConfirmMail",
      setup() {
        const route = useRoute();
        const userEmail = ref('');
        
        onMounted(() => {
          if (route.query.email && typeof route.query.email === 'string') {
            userEmail.value = route.query.email;
          } else {
            userEmail.value = "hello@oju.bj";
          }
        });
        
        return {
          userEmail
        };
      }
    });
  </script>
  
  <style scoped>
  
  .confirm-mail-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background-color: #0f1116;
    padding: 20px;
  }
  
  .confirm-mail-wrapper {
    width: 100%;
    max-width: 500px;
  }
  
  .confirm-mail-content {
    background-color: #1a1e24;
    border-radius: 12px;
    padding: 40px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
    text-align: center;
  }
  
  .confirm-mail-header {
    margin-bottom: 30px;
  }
  
  .confirm-mail-title {
    color: #fff;
    margin-bottom: 10px;
    font-size: 2.5rem;
    font-weight: 700;
    letter-spacing: -1px;
  }
  
  .confirm-mail-subtitle {
    color: rgba(255, 255, 255, 0.7);
    font-size: 1rem;
  }
  
  .logo-container {
    display: flex;
    justify-content: center;
    margin-bottom: 30px;
  }
  
  .logo {
    max-width: 150px;
    height: auto;
  }
  
  .message-icon-container {
    display: flex;
    justify-content: center;
    margin-bottom: 20px;
  }
  
  .message-icon {
    font-size: 5rem;
    color: #3b82f6;
  }
  
  .success-title {
    color: #fff;
    font-size: 1.5rem;
    margin-bottom: 15px;
  }
  
  .success-message {
    color: rgba(255, 255, 255, 0.7);
    margin-bottom: 30px;
    line-height: 1.6;
  }
  
  .success-message strong {
    color: #3b82f6;
  }
  
  .confirm-mail-button {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    padding: 15px;
    background-color: #3b82f6;
    color: white;
    text-decoration: none;
    border-radius: 8px;
    font-size: 1rem;
    transition: background-color 0.3s ease;
  }
  
  .confirm-mail-button:hover {
    background-color: #2563eb;
  }
  
  .confirm-mail-button i {
    margin-right: 10px;
  }
  
  @media (max-width: 480px) {
    .confirm-mail-wrapper {
      max-width: 100%;
      margin: 0 10px;
    }
  
    .confirm-mail-content {
      padding: 20px;
    }
  
    .logo {
      max-width: 120px;
    }
  
    .message-icon {
      font-size: 4rem;
    }
  }
  </style>