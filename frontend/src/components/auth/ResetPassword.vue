<template>
  <div class="register-container">
    <div class="register-wrapper">
      <div class="register-content">
        <div class="register-header">
           <h1 class="register-title">Oju</h1>
          <p class="register-subtitle">Secure Access Portal</p>
          <h3 class="register-title">Reset Password</h3>
          <p class="register-subtitle">Enter your new password</p>
        </div>

        <div v-if="apiError" class="api-error-message">
          {{ apiError }}*
        </div>

        <div v-if="successMessage" class="success-message">
          {{ successMessage }}
        </div>

        <form v-if="!successMessage" @submit.prevent="handleResetPassword" class="register-form">
          <div class="form-group">
            <label for="password">
              <i class="material-symbols-outlined">lock</i>
              New Password
            </label>
            <div class="input-wrapper">
              <input 
                :type="showPassword ? 'text' : 'password'" 
                id="password" 
                v-model="password"
                required 
                placeholder="Enter new password"
                @input="validatePassword"
              />
              <button 
                type="button" 
                class="password-toggle"
                @click="togglePasswordVisibility"
              >
                <i class="material-symbols-outlined">
                  {{ showPassword ? 'visibility_off' : 'visibility' }}
                </i>
              </button>
            </div>
            <div v-if="passwordError" class="error-message">
              {{ passwordError }}
            </div>
          </div>

          <div class="form-group">
            <label for="confirmPassword">
              <i class="material-symbols-outlined">verified</i>
              Confirm Password
            </label>
            <div class="input-wrapper">
              <input 
                :type="showConfirmPassword ? 'text' : 'password'" 
                id="confirmPassword" 
                v-model="confirmPassword"
                required 
                placeholder="Confirm new password"
                @input="validateConfirmPassword"
              />
              <button 
                type="button" 
                class="password-toggle"
                @click="toggleConfirmPasswordVisibility"
              >
                <i class="material-symbols-outlined">
                  {{ showConfirmPassword ? 'visibility_off' : 'visibility' }}
                </i>
              </button>
            </div>
            <div v-if="confirmPasswordError" class="error-message">
              {{ confirmPasswordError }}
            </div>
          </div>

          <div class="form-actions">
            <button 
              type="submit" 
              class="register-button"
              :disabled="!isFormValid || isLoading"
            >
              <template v-if="isLoading">
                <i class="material-symbols-outlined animate-spin">sync</i>
                Processing...
              </template>
              <template v-else>
                <i class="material-symbols-outlined">lock_reset</i>
                Reset Password
              </template>
            </button>
          </div>

          <div class="terms-text">
            <p>
              Remember your password? 
              <RouterLink to="/authentication/login">
                Log In
              </RouterLink>
            </p>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
  
<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth.store';

export default defineComponent({
  name: 'ResetPasswordPage',
  setup() {
    const route = useRoute();
    const router = useRouter();
    const authStore = useAuthStore();

    const password = ref('');
    const confirmPassword = ref('');
    const showPassword = ref(false);
    const showConfirmPassword = ref(false);
    const passwordError = ref('');
    const confirmPasswordError = ref('');
    const token = ref('');
    const tokenValid = ref(false);

    const isLoading = computed(() => authStore.loading);
    const apiError = computed(() => authStore.error);
    const successMessage = ref('');
  
    onMounted(async () => {
        if (route.params.token && typeof route.params.token === 'string') {
          token.value = route.params.token;
          
          try {
            const response = await authStore.verifyResetToken(token.value);
            if (response.is_valid) {
              tokenValid.value = true;
            } else {
              authStore.error = response.message || 'Invalid reset token';
              setTimeout(() => {
                router.push('/authentication/forget-password');
                authStore.error = '';
              }, 5000);
            }
          } catch (error: any) {
            authStore.error = error.response?.data?.error || 'Invalid or expired token';
            setTimeout(() => {
              router.push('/authentication/forget-password');
              authStore.error = '';
            }, 5000);
          }
        } else {
          authStore.error = 'No reset token provided';
          setTimeout(() => {
            router.push('/authentication/forget-password');
            authStore.error = '';
          }, 3000);
        }
    });

    const validatePassword = () => {
      const hasLowercase = /[a-z]/.test(password.value);
      const hasUppercase = /[A-Z]/.test(password.value);
      const hasNumber = /[0-9]/.test(password.value);
      const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password.value);

      if (password.value.length < 8) {
        passwordError.value = 'Password must be at least 8 characters long';
      } else if (!hasLowercase || !hasUppercase || !hasNumber || !hasSpecialChar) {
        passwordError.value = 'Password must include lowercase, uppercase, number, and special character';
      } else {
        passwordError.value = '';
      }
      if (confirmPassword.value) {
        validateConfirmPassword();
      }
    };
  
    const validateConfirmPassword = () => {
      if (confirmPassword.value !== password.value) {
        confirmPasswordError.value = 'Passwords do not match';
      } else {
        confirmPasswordError.value = '';
      }
    };
  
    const togglePasswordVisibility = () => {
      showPassword.value = !showPassword.value;
    };
  
    const toggleConfirmPasswordVisibility = () => {
      showConfirmPassword.value = !showConfirmPassword.value;
    };
  
    const isFormValid = computed(() => {
      return password.value &&
             confirmPassword.value &&
             !passwordError.value &&
             !confirmPasswordError.value &&
             tokenValid.value;
    });
  
    const handleResetPassword = async() => {
      if (isFormValid.value) {
        try {
          const response = await authStore.resetPassword({
            token: token.value,
            password: password.value,
            confirm_password: confirmPassword.value
          });
          
          successMessage.value = 'Password reset successfully';
          
          setTimeout(() => {
            router.push('/authentication/login');
          }, 3000);
          
        } catch (error) {
          console.error('Error resetting password:', error);
        }
      }
    };
  
    return {
      password,
      confirmPassword,
      showPassword,
      showConfirmPassword,
      passwordError,
      confirmPasswordError,
      apiError,
      successMessage,
      isLoading,
      validatePassword,
      validateConfirmPassword,
      togglePasswordVisibility,
      toggleConfirmPasswordVisibility,
      isFormValid,
      handleResetPassword,
    };
  },
});
</script>
  
  <style scoped>
  .api-error-message {
    background-color: rgba(239, 68, 68, 0.2);
    color: #ef4444;
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 20px;
    text-align: center;
  }

  .success-message {
    background-color: rgba(16, 185, 129, 0.2);
    color: #10b981;
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 20px;
    text-align: center;
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
  .register-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background-color: #0f1116;
    padding: 20px;
  }
  
  .register-wrapper {
    width: 100%;
    max-width: 450px;
  }
  
  .register-content {
    background-color: #1a1e24;
    border-radius: 12px;
    padding: 40px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  }
  
  .register-header {
    text-align: center;
    margin-bottom: 30px;
  }
  
  .register-title {
    color: #fff;
    margin-bottom: 10px;
    font-size: 2.5rem;
    font-weight: 700;
    letter-spacing: -1px;
  }
  
  .register-subtitle {
    color: rgba(255, 255, 255, 0.7);
    font-size: 1rem;
  }
  
  .form-group {
    margin-bottom: 20px;
    position: relative;
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
  }
  
  .input-wrapper input {
    width: 100%;
    padding: 12px;
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
  
  .password-toggle {
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    color: rgba(255, 255, 255, 0.5);
    cursor: pointer;
  }
  
  .error-message {
    color: #ef4444;
    font-size: 0.8rem;
    margin-top: 5px;
  }
  
  .form-actions {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
  }
  
  .register-button {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    padding: 12px;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.3s ease;
    background-color: #3b82f6;
    color: white;
  }
  
  .register-button:hover:not(:disabled) {
    background-color: #2563eb;
  }
  
  .register-button:disabled {
    background-color: rgba(59, 130, 246, 0.5);
    cursor: not-allowed;
  }
  
  .terms-text {
    margin-top: 20px;
    color: rgba(255, 255, 255, 0.7);
    font-size: 0.8rem;
    text-align: center;
  }
  
  .terms-text a {
    color: #3b82f6;
    text-decoration: none;
    font-weight: 500;
  }
  </style>
  