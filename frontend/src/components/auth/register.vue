<template>
  <div class="register-container">
    <div class="register-wrapper">
      <div class="register-content">
        <div class="register-header">
          <h1 class="register-title">Oju</h1>
          <p class="register-subtitle">Secure Access Portal</p>
        </div>

        <div v-if="apiError" class="api-error-message">
          {{ apiError }}
        </div>
        <div v-else-if="successMessage" class="success-message">
          {{ successMessage }}
        </div>
        <form @submit.prevent="handleRegister" class="register-form">
          <div class="form-group">
            <label for="username">
              <i class="material-symbols-outlined">person</i>
              Username
            </label>
            <div class="input-wrapper">
              <input 
                type="text" 
                id="username" 
                v-model="username"
                required 
                placeholder="Choose a username"
                @input="validateUsername"
              />
              <span class="input-status" :class="usernameStatus">
                <i class="material-symbols-outlined">
                  {{ usernameIcon }}
                </i>
              </span>
            </div>
            <div v-if="usernameError" class="error-message">
              {{ usernameError }}
            </div>
          </div>

          <div class="form-group">
            <label for="nom_prenom">
              <i class="material-symbols-outlined">badge</i>
              Full Name
            </label>
            <div class="input-wrapper">
              <input 
                type="text" 
                id="nom_prenom" 
                v-model="nom_prenom"
                required 
                placeholder="Enter your full name"
                @input="validateNomPrenom"
              />
              <span class="input-status" :class="nom_prenomStatus">
                <i class="material-symbols-outlined">
                  {{ nom_prenomIcon }}
                </i>
              </span>
            </div>
              <div v-if="nom_prenomError" class="error-message">
                {{ nom_prenomError }}
              </div>
          </div>

          <div class="form-group">
            <label for="email">
              <i class="material-symbols-outlined">mail</i>
              Email
            </label>
            <div class="input-wrapper">
              <input 
                type="email" 
                id="email" 
                v-model="email"
                required 
                placeholder="example@trezo.com"
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

          <div class="form-group">
            <label for="password">
              <i class="material-symbols-outlined">lock</i>
              Password
            </label>
            <div class="input-wrapper">
              <input 
                :type="showPassword ? 'text' : 'password'" 
                id="password"
                v-model="password"
                required 
                placeholder="Type password"
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
              <span class="input-status" :class="passwordStatus">
                <i class="material-symbols-outlined">
                  {{ passwordIcon }}
                </i>
              </span>
            </div>
            <div class="password-strength">
              <div class="strength-bar" :class="passwordStrengthClass"></div>
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
                placeholder="Confirm password"
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
              <span class="input-status" :class="confirmPasswordStatus">
                <i class="material-symbols-outlined">
                  {{ confirmPasswordIcon }}
                </i>
              </span>
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
                <i class="material-symbols-outlined">person_4</i>
                Register
              </template>
            </button>
            <button 
              type="button" 
              class="reset-button"
              @click="resetForm"
            >
              <i class="material-symbols-outlined">restart_alt</i>
              Reset
            </button>
          </div>

          <div class="terms-text">
            <p>
              By confirming your email, you agree to our
              <RouterLink to="#">
                Terms of Service
              </RouterLink>
              and that you have read and understood our
              <RouterLink to="#">
                Privacy Policy
              </RouterLink>.
            </p>
            <p>
              Already have an account? 
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
import { defineComponent, ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth.store';

export default defineComponent({
  name: 'Register',
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();

    const username = ref('');
    const nom_prenom = ref('');
    const email = ref('');
    const password = ref('');
    const confirmPassword = ref('');

    const showPassword = ref(false);
    const showConfirmPassword = ref(false);

    const usernameError = ref('');
    const nom_prenomError = ref('');
    const emailError = ref('');
    const passwordError = ref('');
    const confirmPasswordError = ref('');
    const successMessage = ref('');


    const isLoading = computed(() => authStore.loading);
    const apiError = computed(() => authStore.error);

    const validateUsername = () => {
      if (username.value.length < 3 || username.value.length > 30) {
        usernameError.value = 'Username must be between 3 and 30 characters';
      } else {
        usernameError.value = '';
      }
    };

    const validateNomPrenom = () => {
      
      if (nom_prenom.value.length < 5 || nom_prenom.value.length > 255) {
        nom_prenomError.value = 'Full name must be between 5 and 255 characters';
      } else {
        nom_prenomError.value = '';
      }
    };

    const validateEmail = () => {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email.value)) {
        emailError.value = 'Please enter a valid email address';
      } else {
        emailError.value = '';
      }
    };

    const validatePassword = () => {
      const hasLowercase = /[a-z]/.test(password.value);
      const hasUppercase = /[A-Z]/.test(password.value);
      const hasNumber = /[0-9]/.test(password.value);
      const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password.value);

      if (password.value.length < 8 ) {
        passwordError.value = 'Password must 8 characters long or higher';
      } else if (!hasLowercase || !hasUppercase || !hasNumber || !hasSpecialChar) {
        passwordError.value = 'Password must include lowercase, uppercase, number, and special character';
      } else {
        passwordError.value = '';
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

    const resetForm = () => {
      username.value = '';
      nom_prenom.value = '';
      email.value = '';
      password.value = '';
      confirmPassword.value = '';
      usernameError.value = '';
      emailError.value = '';
      passwordError.value = '';
      confirmPasswordError.value = '';
    };

    const handleRegister = async () => {
      if (isFormValid.value) {
        try {
          const success = await authStore.register({
            username: username.value,
            email: email.value,
            nom_prenom: nom_prenom.value,
            password: password.value,
            confirm_password: confirmPassword.value 
          });

          if (success) {
            successMessage.value = 'Your account has been created, plz contact admin to enable it';
            await new Promise(resolve => setTimeout(resolve, 5000));
            resetForm();
            router.push({
              path: '/authentication/login'
            });
          }
        } catch (error) {
          console.error('Registration error', error);
        }
      }
    };

    const usernameStatus = computed(() => ({
      'is-valid': username.value && !usernameError.value,
      'is-invalid': usernameError.value
    }));

    const nom_prenomStatus = computed(() => ({
      'is-valid': nom_prenom.value && !nom_prenomError.value,
      'is-invalid': nom_prenomError.value
    }));

    const emailStatus = computed(() => ({
      'is-valid': email.value && !emailError.value,
      'is-invalid': emailError.value
    }));

    const passwordStatus = computed(() => ({
      'is-valid': password.value && !passwordError.value,
      'is-invalid': passwordError.value
    }));

    const confirmPasswordStatus = computed(() => ({
      'is-valid': confirmPassword.value && !confirmPasswordError.value,
      'is-invalid': confirmPasswordError.value
    }));

    const usernameIcon = computed(() => 
      usernameError.value ? 'error' : 'check_circle'
    );

    const nom_prenomIcon = computed(() => 
      nom_prenomError.value ? 'error' : 'check_circle'
    );

    const emailIcon = computed(() => 
      emailError.value ? 'error' : 'check_circle'
    );

    const passwordIcon = computed(() => 
      passwordError.value ? 'error' : 'check_circle'
    );

    const confirmPasswordIcon = computed(() => 
      confirmPasswordError.value ? 'error' : 'check_circle'
    );

    const passwordStrengthClass = computed(() => {
      if (!password.value) return '';
      const hasLowercase = /[a-z]/.test(password.value);
      const hasUppercase = /[A-Z]/.test(password.value);
      const hasNumber = /[0-9]/.test(password.value);
      const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password.value);

      const strengthCount = 
        [hasLowercase, hasUppercase, hasNumber, hasSpecialChar]
        .filter(Boolean).length;

      switch (strengthCount) {
        case 1: return 'strength-weak';
        case 2: return 'strength-fair';
        case 3: return 'strength-good';
        case 4: return 'strength-strong';
        default: return '';
      }
    });

    const isFormValid = computed(() => {
      return username.value && 
             nom_prenom.value && 
             email.value && 
             password.value && 
             confirmPassword.value &&
             !usernameError.value &&
             !nom_prenomError.value &&
             !emailError.value &&
             !passwordError.value &&
             !confirmPasswordError.value;
    });

    return {
      username,
      nom_prenom,
      email,
      password,
      confirmPassword,
      showPassword,
      showConfirmPassword,
      usernameError,
      emailError,
      passwordError,
      confirmPasswordError,
      nom_prenomError,
      validateUsername,
      validateEmail,
      validatePassword,
      validateNomPrenom,
      validateConfirmPassword,
      togglePasswordVisibility,
      toggleConfirmPasswordVisibility,
      resetForm,
      handleRegister,
      usernameStatus,
      emailStatus,
      passwordStatus,
      confirmPasswordStatus,
      nom_prenomStatus,
      nom_prenomIcon,
      usernameIcon,
      emailIcon,
      passwordIcon,
      confirmPasswordIcon,
      passwordStrengthClass,
      isFormValid,
      isLoading,
      apiError,
      successMessage
    };
  }
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

.social-login-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-bottom: 20px;
}

.social-login-button {
  background-color: #2c3240;
  border: none;
  border-radius: 8px;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.social-login-button:hover {
  background-color: #3a4150;
}

.social-login-button img {
  width: 24px;
  height: 24px;
}

.social-divider {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.social-divider::before,
.social-divider::after {
  content: '';
  flex-grow: 1;
  height: 1px;
  background-color: #2c3240;
}

.social-divider span {
  margin: 0 10px;
  color: rgba(255, 255, 255, 0.5);
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

.password-strength {
  height: 4px;
  width: 100%;
  background-color: #2c3240;
  margin-top: 5px;
  border-radius: 2px;
  overflow: hidden;
}

.strength-bar {
  height: 100%;
  width: 0;
  transition: width 0.3s ease;
}

.strength-weak {
  background-color: #ef4444;
  width: 25%;
}

.strength-fair {
  background-color: #f59e0b;
  width: 50%;
}

.strength-good {
  background-color: #10b981;
  width: 75%;
}

.strength-strong {
  background-color: #3b82f6;
  width: 100%;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.register-button,
.reset-button {
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
}

.register-button {
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

.reset-button {
  background-color: #2c3240;
  color: rgba(255, 255, 255, 0.7);
}

.reset-button:hover {
  background-color: #3a4150;
}

.register-button i,
.reset-button i {
  margin-right: 8px;
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

@media (max-width: 480px) {
  .register-wrapper {
    max-width: 100%;
    margin: 0 10px;
  }

  .register-content {
    padding: 20px;
  }

  .social-login-buttons {
    gap: 10px;
  }

  .social-login-button {
    width: 45px;
    height: 45px;
  }
  
}
</style>