<template>
  <div class="login-container">
    <div class="login-wrapper">
      <div class="login-content">
        <div class="login-header">
          <h1 class="login-title">Oju</h1>
          <p class="login-subtitle">Secure Access Portal</p>
        </div>

        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <div v-if="error" class="error-message">
              {{ error }}
            </div>
            <label for="email">
              <i class="material-symbols-outlined">mail</i>
              Email
            </label>
            <div class="input-wrapper">
              <i class="material-symbols-outlined input-icon">alternate_email</i>
              <input 
                type="email" 
                id="email" 
                v-model="email"
                required 
                placeholder="Enter your email"
              />
            </div>
          </div>

          <div class="form-group">
            <label for="password">
              <i class="material-symbols-outlined">lock</i>
              Password
            </label>
            <div class="input-wrapper">
              <i class="material-symbols-outlined input-icon">key</i>
              <input 
                :type="showPassword ? 'text' : 'password'" 
                id="password"
                v-model="password"
                required 
                placeholder="Enter your password"
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
          </div>

          <div class="form-actions">
            <RouterLink 
              to="/authentication/forget-password" 
              class="forgot-password"
            >
              <i class="material-symbols-outlined">help</i>
              Forgot Password?
            </RouterLink>
          </div>

          <button 
            type="submit" 
            class="login-button"
            :disabled="isLoading"
          >
            <i v-if="!isLoading" class="material-symbols-outlined">login</i>
            <svg v-else class="spinner" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 50 50">
              <circle class="path" cx="25" cy="25" r="20" fill="none" stroke-width="5"></circle>
            </svg>
            <span class="button-text">
              {{ isLoading ? 'Signing In...' : 'Sign In' }}
            </span>
          </button>

        </form>

        <div class="register-link">
          Don't have an account? 
          <RouterLink to="/authentication/register">
            Register
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth.store';

export default defineComponent({
  name: 'Login',
  setup() {
    const router = useRouter();
    const route = useRoute();
    const authStore = useAuthStore();

    const email = ref('');
    const password = ref('');
    const showPassword = ref(false);

    const validationError = ref<string | null>(null);

    const isLoading = computed(() => authStore.loading);

    const error = computed(() => authStore.error || validationError.value);

    const validateForm = () => {
      validationError.value = null;
      
      if (!email.value.trim()) {
        validationError.value = 'Username is required';
        return false;
      }
      
      if (!password.value) {
        validationError.value = 'Password is required';
        return false;
      }
      
      if (email.value.includes('@')) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email.value)) {
          validationError.value = 'Please enter a valid email address';
          return false;
        }
      }
      
      return true;
    };

    const handleLogin = async () => {
      if (!validateForm()) {
        return;
      }
      try {
        const success = await authStore.login({
          email: email.value,
          password: password.value
        });
        if (success) {
          let redirectPath = '/dashboard';
          
          if (route.query.redirect) {
            const redirectUrl = route.query.redirect.toString();
            if (redirectUrl.startsWith('/') && !redirectUrl.includes('//')) {
              redirectPath = redirectUrl;
            }
          }
          router.push(redirectPath);
        }
      } catch (error) {
        console.error('Login failed', error);
      }
    };

    const togglePasswordVisibility = () => {
      showPassword.value = !showPassword.value;
    };

    return {
      email,
      error,
      password,
      showPassword,
      isLoading,
      handleLogin,
      togglePasswordVisibility
    };
  }
});
</script>

<style scoped>
.error-message {
  background-color: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 20px;
  text-align: center;
}
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #121212 0%, #1f2937 100%);
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.login-container::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background-image: 
    radial-gradient(rgba(31, 41, 55, 0.1) 8%, transparent 8%),
    radial-gradient(rgba(31, 41, 55, 0.1) 8%, transparent 8%);
  background-position: 0 0, 50px 50px;
  background-size: 100px 100px;
  opacity: 0.3;
  z-index: 1;
}

.login-wrapper {
  width: 100%;
  max-width: 400px;
  position: relative;
  z-index: 2;
}

.login-content {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 40px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.125);
  box-shadow: 
    0 10px 25px rgba(0, 0, 0, 0.1),
    0 20px 50px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-title {
  color: #fff;
  margin-bottom: 10px;
  font-size: 2.5rem;
  font-weight: 700;
  letter-spacing: -1px;
}

.login-subtitle {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1rem;
}

.login-form {
  display: flex;
  flex-direction: column;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.form-group label i {
  margin-right: 8px;
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.6);
}

.input-wrapper {
  position: relative;
}

.input-wrapper input {
  width: 100%;
  padding: 12px 12px 12px 40px;
  background-color: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: white;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.input-wrapper input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.input-wrapper input:focus {
  outline: none;
  border-color: rgba(59, 130, 246, 0.7);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

.input-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255, 255, 255, 0.5);
  font-size: 1.2rem;
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

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}

.forgot-password {
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
}

.forgot-password i {
  margin-right: 4px;
  font-size: 1rem;
}

.login-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 12px;
  background-color: rgba(59, 130, 246, 0.7);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.login-button i {
  margin-right: 8px;
}

.login-button:hover:not(:disabled) {
  background-color: rgba(59, 130, 246, 0.9);
}

.login-button:disabled {
  background-color: rgba(128, 128, 128, 0.5);
  cursor: not-allowed;
}

.register-link {
  text-align: center;
  margin-top: 20px;
  color: rgba(255, 255, 255, 0.7);
}

.register-link a {
  color: rgba(59, 130, 246, 0.7);
  text-decoration: none;
  font-weight: 500;
}
.spinner {
  animation: spin 1s linear infinite;
  width: 20px;
  height: 20px;
  margin-right: 8px;
}

.spinner .path {
  stroke: white;
  stroke-linecap: round;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.button-text {
  display: inline-block;
}

</style>