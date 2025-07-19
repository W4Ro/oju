<template>
  <div class="forgot-password-container">
    <div class="forgot-password-wrapper">
      <div class="forgot-password-content">
        <div class="forgot-password-header">
          <h1 class="forgot-password-title">Oju</h1>
          <p class="forgot-password-subtitle">Secure Access Portal</p>
        </div>

        <div class="forgot-password-description">
          <h3>Forgot your password?</h3>
          <p>
            Enter the email address you used when you joined and we'll send you
            instructions to reset your password.
          </p>
        </div>

        <div v-if="apiMessage" class="api-message" :class="{ 'success-message': isSuccess, 'error-message': !isSuccess }">
          {{ apiMessage }}
        </div>

        <form v-if="!isSuccess" @submit.prevent="sendResetInstructions" class="forgot-password-form">
          <div class="form-group">
            <label for="email">
              <i class="material-symbols-outlined">mail</i>
              Email Address
            </label>
            <div class="input-wrapper">
              <input 
                type="email" 
                id="email" 
                v-model="email"
                required 
                placeholder="example@oju.com"
                @input="validateEmail"
              />
              <span class="input-status" :class="emailStatus">
                <i class="material-symbols-outlined">
                  {{ emailIcon }}
                </i>
              </span>
            </div>
            <div v-if="emailError" class="error-message">
              {{ emailError }}
            </div>
          </div>

          <button 
            type="submit" 
            class="send-button"
            :disabled="!isFormValid || isLoading"
          >
            <template v-if="isLoading">
              <i class="material-symbols-outlined animate-spin">sync</i>
              Sending...
            </template>
            <template v-else>
              <i class="material-symbols-outlined">autorenew</i>
              Send Reset Instructions
            </template>
          </button>

          <div class="login-link">
            Back to 
            <RouterLink to="/authentication/login">
              Login
            </RouterLink>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth.store'; 

export default defineComponent({
  name: 'ForgetPassword',
  setup() {
    const router = useRouter();
    const authStore = useAuthStore(); 
    const email = ref('');
    const emailError = ref('');
    const isLoading = computed(() => authStore.loading);
    const apiMessage = computed(() => authStore.error);
    const isSuccess = ref(false);

    const validateEmail = () => {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!email.value.trim()) {
        emailError.value = 'Email is required';
      } else if (!emailRegex.test(email.value)) {
        emailError.value = 'Please enter a valid email address';
      } else {
        emailError.value = '';
      }
    };

    const sendResetInstructions = async () => {
      if (isFormValid.value) {
        try {
          const response = await authStore.requestPasswordReset(email.value);
          
          isSuccess.value = true;
          
          setTimeout(() => {
            router.push({
              path: '/authentication/confirm-mail',
              query: { email: email.value }
            });
          }, 1000);
          
        } catch (error) {
          isSuccess.value = false;
        }
      }
    };

    const emailStatus = computed(() => ({
      'is-valid': email.value && !emailError.value,
      'is-invalid': emailError.value
    }));

    const emailIcon = computed(() => 
      emailError.value ? 'error' : 'check_circle'
    );

    const isFormValid = computed(() => 
      email.value && !emailError.value
    );

    return {
      email,
      emailError,
      validateEmail,
      sendResetInstructions,
      emailStatus,
      emailIcon,
      isFormValid,
      isLoading,
      apiMessage,
      isSuccess
    };
  }
});
</script>
<style scoped>


.forgot-password-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #0f1116;
  padding: 20px;
}

.forgot-password-wrapper {
  width: 100%;
  max-width: 500px;
}

.forgot-password-content {
  background-color: #1a1e24;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.forgot-password-header {
  text-align: center;
  margin-bottom: 20px;
}

.forgot-password-title {
  color: #fff;
  margin-bottom: 10px;
  font-size: 2.5rem;
  font-weight: 700;
  letter-spacing: -1px;
}

.forgot-password-subtitle {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1rem;
}

.forgot-password-description {
  text-align: center;
  margin-bottom: 30px;
}

.forgot-password-description h3 {
  color: #fff;
  margin-bottom: 15px;
  font-size: 1.5rem;
}

.forgot-password-description p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1rem;
  line-height: 1.5;
}

.form-group {
  margin-bottom: 25px;
}

.form-group label {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

.form-group label i {
  margin-right: 8px;
  color: rgba(255, 255, 255, 0.5);
}

.input-wrapper {
  position: relative;
  width: 100%;
}

.input-wrapper input {
  width: 100%;
  padding: 15px 12px 15px 40px;
  background-color: #2c3240;
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 1rem;
  transition: box-shadow 0.3s ease;
}

.input-wrapper input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.input-wrapper input:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
}

.input-status {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
}

.input-status.is-valid i {
  color: #10b981;
}

.input-status.is-invalid i {
  color: #ef4444; 
}

.error-message {
  color: #ef4444;
  font-size: 0.8rem;
  margin-top: 5px;
}

.send-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 15px;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin-bottom: 20px;
}

.send-button:hover:not(:disabled) {
  background-color: #2563eb;
}

.send-button:disabled {
  background-color: rgba(59, 130, 246, 0.5);
  cursor: not-allowed;
}

.send-button i {
  margin-right: 8px;
}

.login-link {
  text-align: center;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

.login-link a {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
}

@media (max-width: 480px) {
  .forgot-password-wrapper {
    max-width: 100%;
    margin: 0 10px;
  }

  .forgot-password-content {
    padding: 20px;
  }
}

.error-message {
  color: #ef4444;
  font-size: 0.8rem;
  margin-top: 5px;
}

.api-message {
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 20px;
  text-align: center;
}

.success-message {
  background-color: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.api-message:not(.success-message) {
  background-color: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>