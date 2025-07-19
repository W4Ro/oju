<template>
    <div>
      <PageTitle pageTitle="Profil settings" subTitle="My account" />
      
      <div class="row">
        <div class="col-12">
          <SettingsMenu />
          
          <div class="card bg-white border-0 rounded-3 mb-4">
            <div class="card-body p-4">
              <div class="d-flex justify-content-between align-items-center text-center flex-wrap gap-2 showing-wrap border-bottom pb-3 mb-4">
                <h3 class="fs-16 fw-semibold mb-0">Personal informations</h3>
              </div>
              
              <div class="row">
                <div class="col-lg-3 col-md-4 mb-4 mb-md-0">
                  <div class="text-center">
                    <div class="position-relative d-inline-block">
                      <div class="avatar-container rounded-circle overflow-hidden" style="width: 150px; height: 150px; background-color: #e9ecef;">
                        <img
                          v-if="profileImage"
                          :src="profileImage"
                          alt="Profile Image"
                          class="img-fluid w-100 h-100 object-fit-cover"
                        />
                        <div v-else class="d-flex align-items-center justify-content-center h-100">
                          <i class="ri-user-fill fs-1 text-secondary"></i>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div class="col-lg-9 col-md-8">
                  <form @submit.prevent="updateProfile" class="row g-3">
                    <div class="col-md-6 mb-3">
                      <label for="full-name" class="form-label text-secondary fs-14">Full name<span class="text-danger">*</span></label>
                      <input
                        type="text"
                        class="form-control h-55"
                        id="full-name"
                        v-model="userData.nom_prenom"
                        :class="{ 'is-invalid': validation.nom_prenom }"
                        @blur="validateField('nom_prenom')"
                        @input="validateField('nom_prenom')"
                        placeholder="Full name"
                        required
                      />
                      <div v-if="validation.nom_prenom" class="text-danger small mt-1">
                        {{ validation.nom_prenom }}
                      </div>
                    </div>
                    
                    <div class="col-md-6 mb-3">
                      <label for="username" class="form-label text-secondary fs-14">Username <span class="text-danger">*</span></label>
                      <input
                        type="text"
                        class="form-control h-55"
                        id="username"
                        v-model="userData.username"
                        :class="{ 'is-invalid': validation.username }"
                        @blur="validateField('username')"
                        @input="validateField('username')"
                        placeholder="username"
                        required
                      />
                      <div v-if="validation.username" class="text-danger small mt-1">
                        {{ validation.username }}
                      </div>
                    </div>
                    
                    <div class="col-md-6 mb-3">
                      <label for="email" class="form-label text-secondary fs-14">Email <span class="text-danger">*</span></label>
                      <input
                        type="email"
                        class="form-control h-55"
                        id="email"
                        v-model="userData.email"
                        :class="{ 'is-invalid': validation.email }"
                        @blur="validateField('email')"
                        @input="validateField('email')"
                        placeholder="Email"
                        required
                      />
                      <div v-if="validation.email" class="text-danger small mt-1">
                        {{ validation.email }}
                      </div>
                    </div>
                    
                    <div class="col-md-6 mb-3">
                      <label for="role" class="form-label text-secondary fs-14">Role</label>
                      <input
                        type="text"
                        class="form-control h-55"
                        id="role"
                        v-model="userData.role_name"
                        disabled
                        title="The role cannot be changed from here"
                      />
                    </div>
                    
                    <div class="col-12 mb-3">
                      <label for="password" class="form-label text-secondary fs-14">Actual password<span class="text-danger">*</span></label>
                      <div class="input-group">
                        <input
                          :type="showPassword ? 'text' : 'password'"
                          class="form-control h-55"
                          id="password"
                          v-model="currentPassword"
                          :class="{ 'is-invalid': validation.currentPassword }"
                          @blur="validateField('currentPassword')"
                          @input="validateField('currentPassword')"
                          placeholder="Enter your current password"
                          required
                        />
                        <button 
                          class="btn btn-outline-secondary h-55 d-flex align-items-center justify-content-center"
                          type="button"
                          @click="showPassword = !showPassword"
                        >
                          <i class="material-symbols-outlined">{{ showPassword ? 'visibility_off' : 'visibility' }}</i>
                        </button>
                      </div>
                      <div v-if="validation.currentPassword" class="text-danger small mt-1">
                        {{ validation.currentPassword }}
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
                          {{ isSubmitting ? 'Updating...' : 'Update' }}
                        </button>
                      </div>
                    </div>
                  </form>
                </div>
              </div>
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
import { ref, computed, onMounted } from 'vue';
import SettingsMenu from '@/modules/settings/views/SettingsMenu.vue';
import PageTitle from "@/components/Common/PageTitle.vue";
import Toast from "@/components/Common/Toast.vue";
import { useUserStore } from '@/stores/user.store';
import { useAuthStore } from '@/stores/auth.store';

const userStore = useUserStore();
const authStore = useAuthStore();

const userData = ref({
  id: '',
  nom_prenom: '',
  username: '',
  email: '',
  role: '',
  role_name: '',
  profile_image: null
});

const currentPassword = ref('');
const showPassword = ref(false);
const isSubmitting = ref(false);
const profileImage = ref(null);
const originalUserData = ref({});

const validation = ref({
  nom_prenom: '',
  username: '',
  email: '',
  currentPassword: ''
});

const fetchUserProfile = async () => {
  try {
    isSubmitting.value = true;
    
    const profile = await userStore.fetchUserProfile();
    
    if (profile) {
      userData.value = {
        id: profile.id,
        nom_prenom: profile.nom_prenom, 
        username: profile.username,
        email: profile.email,
        role: profile.role,
        role_name: profile.role_name || 'Undefined',
        profile_image: profile.profile_image
      };
      
      originalUserData.value = { ...userData.value };
      
      if (profile.profile_image) {
        profileImage.value = profile.profile_image;
      }
    }
    
    validateAllFields();
    
  } catch (error) {
    userStore.showToast('Error retrieving user\'s informations', 'error');
  } finally {
    isSubmitting.value = false;
  }
};

const validateField = (field) => {
  switch (field) {
    case 'nom_prenom': { 
      if (!userData.value.nom_prenom || !userData.value.nom_prenom.trim()) {
        validation.value.nom_prenom = 'full name is required';
      } else {
        validation.value.nom_prenom = '';
      }
      break;
    }
      
    case 'username': {
      if (!userData.value.username || !userData.value.username.trim()) {
        validation.value.username = 'username is required';
      } else {
        validation.value.username = '';
      }
      break;
    }
      
    case 'email': {
      const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
      if (!userData.value.email || !userData.value.email.trim()) {
        validation.value.email = 'email is required';
      } else if (!emailRegex.test(userData.value.email)) {
        validation.value.email = 'enter a valid email address';
      } else {
        validation.value.email = '';
      }
      break;
    }
      
    case 'currentPassword': {
      if (!currentPassword.value || !currentPassword.value.trim()) {
        validation.value.currentPassword = 'Your current password is required';
      } else {
        validation.value.currentPassword = '';
      }
      break;
    }
  }
};

const validateAllFields = () => {
  validateField('nom_prenom');
  validateField('username');
  validateField('email');
  validateField('currentPassword');
};

const isFormValid = computed(() => {
  const hasChanges = userData.value.nom_prenom !== originalUserData.value.nom_prenom || 
                    userData.value.email !== originalUserData.value.email ||
                    userData.value.username !== originalUserData.value.username ||
                    profileImage.value !== originalUserData.value.profile_image;
  
  const requiredFieldsValid = 
    userData.value.nom_prenom && 
    userData.value.nom_prenom.trim() &&
    userData.value.username && 
    userData.value.username.trim() &&
    userData.value.email && 
    userData.value.email.trim() &&
    currentPassword.value && 
    currentPassword.value.trim();
  
  const noValidationErrors = 
    !validation.value.nom_prenom &&
    !validation.value.username &&
    !validation.value.email && 
    !validation.value.currentPassword;
  
  return hasChanges && requiredFieldsValid && noValidationErrors;
});

const removeProfileImage = () => {
  profileImage.value = null;
};

const resetForm = () => {
  userData.value = { ...originalUserData.value };
  currentPassword.value = '';
  
  if (originalUserData.value.profile_image) {
    profileImage.value = originalUserData.value.profile_image;
  } else {
    profileImage.value = null;
  }
  
  validation.value = {
    nom_prenom: '',
    username: '',
    email: '',
    currentPassword: ''
  };
};

const updateProfile = async () => {
  validateAllFields();
  
  if (!isFormValid.value) {
    return;
  }
  
  isSubmitting.value = true;
  
  try {
    const formData = {
      nom_prenom: userData.value.nom_prenom.trim(),
      username: userData.value.username.trim(),
      email: userData.value.email.trim(),
      current_password: currentPassword.value.trim()
    };
    
    await userStore.updateUserProfile(formData);
    
    originalUserData.value = { ...userData.value };
    
    currentPassword.value = '';
    
  } catch (error) {
    userStore.showToast(error.response?.data?.error || 'Error updating profile', 'error');
  } finally {
    isSubmitting.value = false;
  }
};

function handleToastClose() {
  userStore.toast.show = false;
}

onMounted(() => {
  fetchUserProfile();
});
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
  
  .avatar-container {
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    border: 2px solid #fff;
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
  
  .object-fit-cover {
    object-fit: cover;
  }
  </style>