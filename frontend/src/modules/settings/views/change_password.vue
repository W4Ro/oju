<template>
  <div>
    <PageTitle pageTitle="Profil settings" subTitle="My account" />
    
    <div class="row">
      <div class="col-12">
        <SettingsMenu />
        
        <div class="card bg-white border-0 rounded-3 mb-4">
          <div class="card-body p-4">
            <div class="d-flex justify-content-between align-items-center text-center flex-wrap gap-2 showing-wrap border-bottom pb-3 mb-4">
              <h3 class="fs-16 fw-semibold mb-0">Change password</h3>
            </div>
            
            <form @submit.prevent="changePassword">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="old-password" class="form-label text-secondary fs-14">Old password<span class="text-danger">*</span></label>
                  <div class="input-group">
                    <input
                      :type="showOldPassword ? 'text' : 'password'"
                      id="old-password"
                      class="form-control h-55"
                      v-model="passwordData.oldPassword"
                      :class="{ 'is-invalid': validation.oldPassword }"
                      @input="validateField('oldPassword')"
                      @blur="validateField('oldPassword')"
                      placeholder="Enter your old password"
                    />
                    <button 
                      class="btn btn-outline-secondary h-55 d-flex align-items-center justify-content-center"
                      type="button"
                      @click="showOldPassword = !showOldPassword"
                    >
                      <i class="material-symbols-outlined">{{ showOldPassword ? 'visibility_off' : 'visibility' }}</i>
                    </button>
                  </div>
                  <div v-if="validation.oldPassword" class="text-danger small mt-1">
                    {{ validation.oldPassword }}
                  </div>
                </div>
                
                <div class="col-md-6 mb-3">
                  <label for="new-password" class="form-label text-secondary fs-14">New password <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <input
                      :type="showNewPassword ? 'text' : 'password'"
                      id="new-password"
                      class="form-control h-55"
                      v-model="passwordData.newPassword"
                      :class="{ 'is-invalid': validation.newPassword }"
                      @input="validateField('newPassword')"
                      @blur="validateField('newPassword')"
                      placeholder="Create a new password"
                    />
                    <button 
                      class="btn btn-outline-secondary h-55 d-flex align-items-center justify-content-center"
                      type="button"
                      @click="showNewPassword = !showNewPassword"
                    >
                      <i class="material-symbols-outlined">{{ showNewPassword ? 'visibility_off' : 'visibility' }}</i>
                    </button>
                  </div>
                  <div v-if="validation.newPassword" class="text-danger small mt-1">
                    {{ validation.newPassword }}
                  </div>
                </div>
                
                <div class="col-md-12 mb-3">
                  <label for="confirm-password" class="form-label text-secondary fs-14">Confirm the password <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <input
                      :type="showConfirmPassword ? 'text' : 'password'"
                      id="confirm-password"
                      class="form-control h-55"
                      v-model="passwordData.confirmPassword"
                      :class="{ 'is-invalid': validation.confirmPassword }"
                      @input="validateField('confirmPassword')"
                      @blur="validateField('confirmPassword')"
                      placeholder="Confirm your new password"
                    />
                    <button 
                      class="btn btn-outline-secondary h-55 d-flex align-items-center justify-content-center"
                      type="button"
                      @click="showConfirmPassword = !showConfirmPassword"
                    >
                      <i class="material-symbols-outlined">{{ showConfirmPassword ? 'visibility_off' : 'visibility' }}</i>
                    </button>
                  </div>
                  <div v-if="validation.confirmPassword" class="text-danger small mt-1">
                    {{ validation.confirmPassword }}
                  </div>
                </div>
                
                <div class="col-md-12 mb-4">
                  <div class="password-strength mt-2">
                    <p class="fs-14 text-secondary mb-2">Password requirements :</p>
                    <div class="d-flex flex-wrap gap-3">
                      <div class="d-flex align-items-center gap-2">
                        <i :class="hasMinLength ? 'ri-checkbox-circle-fill text-success' : 'ri-checkbox-blank-circle-line text-secondary'"></i>
                        <small>at least 8 characters</small>
                      </div>
                      <div class="d-flex align-items-center gap-2">
                        <i :class="hasUppercase ? 'ri-checkbox-circle-fill text-success' : 'ri-checkbox-blank-circle-line text-secondary'"></i>
                        <small>at least one uppercase</small>
                      </div>
                      <div class="d-flex align-items-center gap-2">
                        <i :class="hasLowercase ? 'ri-checkbox-circle-fill text-success' : 'ri-checkbox-blank-circle-line text-secondary'"></i>
                        <small>at least one lowercase</small>
                      </div>
                      <div class="d-flex align-items-center gap-2">
                        <i :class="hasNumber ? 'ri-checkbox-circle-fill text-success' : 'ri-checkbox-blank-circle-line text-secondary'"></i>
                        <small>at least one number</small>
                      </div>
                      <div class="d-flex align-items-center gap-2">
                        <i :class="hasSpecialChar ? 'ri-checkbox-circle-fill text-success' : 'ri-checkbox-blank-circle-line text-secondary'"></i>
                        <small>at least one special character</small>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div class="col-12 mt-4">
                  <div class="d-flex flex-wrap gap-3 align-items-center justify-content-end">
                    
                    <button
                      class="btn btn-outline-secondary fw-semibold py-2 px-4"
                      type="button"
                      @click="resetForm"
                      :disabled="isSubmitting"
                    >
                      Cancel
                    </button>
                    <button
                      class="btn btn-primary text-white fw-semibold py-2 px-4"
                      type="submit"
                      :disabled="isSubmitting || !isFormValid"
                    >
                      <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      {{ isSubmitting ? 'Updating...' : 'Change password' }}
                    </button>
                  </div>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
  <Toast 
    :show="userStore.toast.show" 
    :message="userStore.toast.message" 
    :type="userStore.toast.type" 
    :autoClose="true"
    :duration="userStore.toast.duration"
    @close="handleToastClose" 
  />
</template>

<script setup>
import { ref, computed } from "vue";
import SettingsMenu from "@/modules/settings/views/SettingsMenu.vue";
import PageTitle from "@/components/Common/PageTitle.vue";
import Toast from "@/components/Common/Toast.vue";
import { useUserStore } from '@/stores/user.store';

const userStore = useUserStore();

const passwordData = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
});

const showOldPassword = ref(false);
const showNewPassword = ref(false);
const showConfirmPassword = ref(false);

const isSubmitting = ref(false);

const validation = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
});

const hasMinLength = computed(() => passwordData.value.newPassword.length >= 8);
const hasUppercase = computed(() => /[A-Z]/.test(passwordData.value.newPassword));
const hasLowercase = computed(() => /[a-z]/.test(passwordData.value.newPassword));
const hasNumber = computed(() => /[0-9]/.test(passwordData.value.newPassword));
const hasSpecialChar = computed(() => /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(passwordData.value.newPassword));

const isPasswordStrong = computed(() => {
  return hasMinLength.value && 
         hasUppercase.value && 
         hasLowercase.value && 
         hasNumber.value && 
         hasSpecialChar.value;
});

const isFormValid = computed(() => {
  return passwordData.value.oldPassword.trim() !== '' && 
         isPasswordStrong.value && 
         passwordData.value.newPassword === passwordData.value.confirmPassword;
});

const validateField = (field) => {
  switch (field) {
    case 'oldPassword': {
      if (!passwordData.value.oldPassword.trim()) {
        validation.value.oldPassword = 'Actual password is required';
      } else {
        validation.value.oldPassword = '';
      }
      break;
    }
      
    case 'newPassword': {
      if (!passwordData.value.newPassword) {
        validation.value.newPassword = 'New password is required';
      } else if (!isPasswordStrong.value) {
        validation.value.newPassword = 'The password must contain at least 8 characters, including uppercase, lowercase, number, and special character';
      } else {
        validation.value.newPassword = '';
      }
      
      if (passwordData.value.confirmPassword) {
        validateField('confirmPassword');
      }
      
      break;
    }
      
    case 'confirmPassword': {
      if (!passwordData.value.confirmPassword) {
        validation.value.confirmPassword = 'Confirm password is required';
      } else if (passwordData.value.newPassword !== passwordData.value.confirmPassword) {
        validation.value.confirmPassword = 'Password confirmation does not match the new password';
      } else {
        validation.value.confirmPassword = '';
      }
      break;
    }
  }
};

const validateAllFields = () => {
  validateField('oldPassword');
  validateField('newPassword');
  validateField('confirmPassword');
};

const resetForm = () => {
  passwordData.value = {
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  };
  
  validation.value = {
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  };
};

function handleToastClose() {
  userStore.toast.show = false;
}

const changePassword = async () => {
  validateAllFields();
  
  if (!isFormValid.value) {
    return;
  }
  
  isSubmitting.value = true;
  
  try {
    const formData = {
      old_password: passwordData.value.oldPassword,
      new_password: passwordData.value.newPassword,
      confirm_password: passwordData.value.confirmPassword 
    };
    
    await userStore.changePassword(formData);
    
    resetForm();
    
  } catch (error) {
    console.error(':', error);
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.h-55 {
  height: 55px;
}

.is-invalid {
  border-color: #dc3545;
}

.form-label {
  font-weight: 500;
  color: #495057;
  margin-bottom: 0.5rem;
}

.btn-primary {
  background-color: #605dff;
  border-color: #605dff;
}

.btn-outline-secondary {
  color: #6c757d;
  border-color: #6c757d;
}

input:disabled {
  background-color: #f8f9fa;
  cursor: not-allowed;
}

.btn:disabled {
  cursor: not-allowed;
  opacity: 0.65;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
  border-width: 0.2em;
}
</style>