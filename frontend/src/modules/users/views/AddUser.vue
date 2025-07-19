<template>
  <div>
    <PageTitle :pageTitle="isEditMode ? 'Edit user' : 'Add a user'" subTitle="Management" />
    
    <div class="row">
      <div class="col-12">
        <div class="card bg-white border-0 rounded-3 mb-4">
          <div class="card-body p-4">
            <div class="d-flex justify-content-between align-items-center text-center flex-wrap gap-2 showing-wrap border-bottom pb-3 mb-4">
              <h3 class="fs-16 fw-semibold mb-0">{{ isEditMode ? 'Edit user information' : 'Create a new user' }}</h3>
            </div>
  
            <form @submit.prevent="submitForm" class="row g-3">
              <div class="col-md-6 mb-3">
                <label for="full-name" class="form-label text-secondary fs-14">Full name<span class="text-danger">*</span></label>
                <input
                  type="text"
                  class="form-control h-55"
                  id="full-name"
                  v-model="userData.nom_prenom"
                  :class="{ 'is-invalid': validation.nom_prenom }"
                  @blur="validateFullName"
                  placeholder="Full name"
                  required
                />
                <div v-if="validation.nom_prenom" class="invalid-feedback">
                  {{ validation.nom_prenom }}
                </div>
              </div>
  
              <div class="col-md-6 mb-3">
                <label for="username" class="form-label text-secondary fs-14">Username<span class="text-danger">*</span></label>
                <input
                  type="text"
                  class="form-control h-55"
                  id="username"
                  v-model="userData.username"
                  :class="{ 'is-invalid': validation.username }"
                  @blur="validateUsername"
                  placeholder="Username"
                  required
                />
                <div v-if="validation.username" class="invalid-feedback">
                  {{ validation.username }}
                </div>
              </div>
  
              <div class="col-md-6 mb-3">
                <label for="email" class="form-label text-secondary fs-14">Email<span class="text-danger">*</span></label>
                <input
                  type="email"
                  class="form-control h-55"
                  id="email"
                  v-model="userData.email"
                  :class="{ 'is-invalid': validation.email }"
                  @blur="validateEmail"
                  placeholder="user@domaine.com"
                  required
                />
                <div v-if="validation.email" class="invalid-feedback">
                  {{ validation.email }}
                </div>
              </div>
  
              <div class="col-md-6 mb-3">
                <label for="role" class="form-label text-secondary fs-14">Role<span class="text-danger">*</span></label>
                <select
                  class="form-select h-55"
                  id="role"
                  v-model="selectedRoleId"
                  :class="{ 'is-invalid': validation.role, 'bg-light': !canManageRoles }"
                  @change="validateRole"
                  required
                  :disabled="!canManageRoles"
                >
                  <option value="" disabled selected>Select a role</option>
                  <option v-for="role in availableRoles" :key="role.id" :value="role.id">
                    {{ role.name }}
                  </option>
                </select>
                <div v-if="validation.role" class="invalid-feedback">
                  {{ validation.role }}
                </div>
                <small v-if="!canManageRoles" class="text-muted">
                  You do not have the necessary permissions to manage roles.
                </small>
              </div>
  
              <div class="col-12 mb-3">
                <div class="d-flex align-items-center">
                  <div class="form-check form-switch">
                    <input 
                      type="checkbox" 
                      class="form-check-input" 
                      id="is_active" 
                      v-model="userData.is_active"
                    />
                    <label class="form-check-label form-label fw-semibold" for="is_active">
                      {{ userData.is_active ? 'Active' : 'Inactive' }} Account
                    </label>
                  </div>
                </div>
                <small class="text-muted">An inactive account cannot log in to the platform.</small>
              </div>
  
              <div class="col-12 mb-3">
                <div class="border rounded p-3 bg-light">
                  <h4 class="fs-16 fw-semibold mb-3">
                    {{ isEditMode ? 'Administrator authentication' : 'Set password' }}
                  </h4>
                  <p class="text-muted mb-3">
                    {{ isEditMode 
                      ? 'Please enter your administrator password to confirm changes.' 
                      : 'Set a password for this new user. The password must contain at least 8 characters with lowercase letters, uppercase letters, numbers, and special characters.' }}
                  </p>
                  
                  <div class="mb-3">
                    <label for="password" class="form-label text-secondary fs-14">
                      {{ isEditMode ? 'Your administrator password' : 'User password' }}<span class="text-danger">*</span>
                    </label>
                    <div class="input-group">
                      <input
                        :type="showPassword ? 'text' : 'password'"
                        class="form-control h-55"
                        id="password"
                        v-model="userData.password"
                        :class="{ 'is-invalid': validation.password }"
                        @blur="validatePassword"
                        placeholder="Password"
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
                    <div v-if="validation.password" class="invalid-feedback d-block">
                      {{ validation.password }}
                    </div>
                  </div>
                  
                  <div v-if="!isEditMode" class="mb-3">
                    <label for="password-confirm" class="form-label text-secondary fs-14">Confirm password<span class="text-danger">*</span></label>
                    <div class="input-group">
                      <input
                        :type="showConfirmPassword ? 'text' : 'password'"
                        class="form-control h-55"
                        id="password-confirm"
                        v-model="passwordConfirm"
                        :class="{ 'is-invalid': validation.passwordConfirm }"
                        @blur="validatePasswordConfirm"
                        placeholder="Confirm password"
                        required
                      />
                      <button 
                        class="btn btn-outline-secondary h-55 d-flex align-items-center justify-content-center"
                        type="button"
                        @click="showConfirmPassword = !showConfirmPassword"
                      >
                        <i class="material-symbols-outlined">{{ showConfirmPassword ? 'visibility_off' : 'visibility' }}</i>
                      </button>
                    </div>
                    <div v-if="validation.passwordConfirm" class="invalid-feedback d-block">
                      {{ validation.passwordConfirm }}
                    </div>
                  </div>
                  
                  <div v-if="!isEditMode && userData.password" class="password-strength mb-3">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                      <small>Password strength:</small>
                      <small>{{ passwordStrengthText }}</small>
                    </div>
                    <div class="progress" style="height: 6px;">
                      <div 
                        class="progress-bar" 
                        :class="passwordStrengthClass"
                        role="progressbar" 
                        :style="{ width: `${passwordStrength}%` }"
                        :aria-valuenow="passwordStrength" 
                        aria-valuemin="0" 
                        aria-valuemax="100"
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
  
              <div class="col-12 mt-4">
                <div class="d-flex flex-wrap gap-3 align-items-center">
                  <button
                    v-if="canAddOrEditUser"
                    class="btn btn-primary text-white fw-semibold py-2 px-4"
                    type="submit"
                    :disabled="isSubmitting || !isFormValid"
                  >
                    {{ isSubmitting ? 'Processing in progress...' : (isEditMode ? 'Edit user' : 'Create user') }}
                  </button>
                  <button
                    class="btn btn-outline-secondary fw-semibold py-2 px-4"
                    type="button"
                    @click="cancelForm"
                  >
                    Cancel
                  </button>
                </div>
                <div v-if="!canAddOrEditUser" class="mt-2 text-danger">
                  You do not have the necessary permissions to modify users.
                </div>
              </div>
            </form>
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import PageTitle from "@/components/Common/PageTitle.vue";
import Toast from "@/components/Common/Toast.vue";
import { useUserStore } from '@/stores/user.store';
import { useAuthStore } from '@/stores/auth.store';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const authStore = useAuthStore();

const canEditUser = computed(() => authStore.hasPermission('users_edit'));
const canManageRoles = computed(() => authStore.hasPermission('users_manage_roles')); 
const canAddOrEditUser = computed(() => authStore.hasAnyPermission(['users_create', 'users_edit']));

const isEditMode = computed(() => route.path.includes('/edit/'));
const userId = computed(() => {
  const parts = route.path.split('/');
  return parts[parts.length - 1];
});

const userData = ref({
  id: '',
  nom_prenom: '',
  username: '',
  email: '',
  role: '',
  is_active: true,
  password: ''
});

const selectedRoleId = ref(''); 
const passwordConfirm = ref(''); 
const showPassword = ref(false);
const showConfirmPassword = ref(false);
const isSubmitting = ref(false);

const validation = ref({
  nom_prenom: '',
  username: '',
  email: '',
  role: '',
  password: '',
  passwordConfirm: ''
});

const availableRoles = ref([]);

const fetchRoles = async () => {
  try {
    isSubmitting.value = true;
    availableRoles.value = await userStore.fetchRoles();
  } catch (error) {
    userStore.showToast('Error retrieving roles', 'error');
  } finally {
    isSubmitting.value = false;
  }
};

const fetchUserData = async () => {
  if (!isEditMode.value) return;
  
  try {
    isSubmitting.value = true;
    const user = await userStore.fetchUserById(userId.value);
    
    if (user) {
      userData.value = {
        id: user.id,
        nom_prenom: user.nom_prenom,
        username: user.username,
        email: user.email,
        role: user.role,
        is_active: user.is_active,
        password: '' 
      };
      
      selectedRoleId.value = user.role;
    } else {
      userStore.showToast('User not found', 'error');
      router.push('/users');
    }
  } catch (error) {
    userStore.showToast('Error retrieving user data', 'error');
  } finally {
    isSubmitting.value = false;
  }
};

const validateFullName = () => {
  if (!userData.value.nom_prenom.trim()) {
    validation.value.nom_prenom = 'Full name is required';
  } else if (userData.value.nom_prenom.length <5){
    validation.value.nom_prenom = 'Username must contain at least 5 characters';
  } else if (userData.value.nom_prenom.length >255){
    validation.value.nom_prenom = 'Username must be 255 characters or less';
  } else{
    validation.value.nom_prenom = '';
  }
};

const validateUsername = () => {
  if (!userData.value.username.trim()) {
    validation.value.username = 'Username is required';
  } else if (userData.value.username.length < 3) {
    validation.value.username = 'Username must contain at least 3 characters';
  } else {
    validation.value.username = '';
  }
};

const validateEmail = () => {
  const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
  
  if (!userData.value.email.trim()) {
    validation.value.email = 'email is required';
  } else if (!emailRegex.test(userData.value.email)) {
    validation.value.email = 'Please enter a valid email address';
  } else {
    validation.value.email = '';
  }
};

const validateRole = () => {
  if (!selectedRoleId.value) {
    validation.value.role = 'Please select a role';
  } else {
    validation.value.role = '';
    userData.value.role = selectedRoleId.value;
  }
};

const validatePassword = () => {
  if (!userData.value.password) {
    validation.value.password = 'Password is required';
    return;
  }
  
  if (!isEditMode.value) {
    const hasMinLength = userData.value.password.length >= 8;
    const hasLowerCase = /[a-z]/.test(userData.value.password);
    const hasUpperCase = /[A-Z]/.test(userData.value.password);
    const hasDigit = /\d/.test(userData.value.password);
    const hasSpecialChar = /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(userData.value.password);
    
    if (!hasMinLength) {
      validation.value.password = 'Password must contain at least 8 characters';
    } else if (!(hasLowerCase && hasUpperCase && hasDigit && hasSpecialChar)) {
      validation.value.password = 'Password must contain at least one lowercase letter, one uppercase letter, one number, and one special character';
    } else {
      validation.value.password = '';
    }
  } else {
    validation.value.password = '';
  }
};

const validatePasswordConfirm = () => {
  if (!passwordConfirm.value) {
    validation.value.passwordConfirm = 'Please confirm password';
  } else if (passwordConfirm.value !== userData.value.password) {
    validation.value.passwordConfirm = 'Passwords do not match';
  } else {
    validation.value.passwordConfirm = '';
  }
};

const passwordStrength = computed(() => {
  if (!userData.value.password) return 0;
  
  let strength = 0;
  
  if (userData.value.password.length >= 8) strength += 25;
  
  if (/[a-z]/.test(userData.value.password)) strength += 25;
  
  if (/[A-Z]/.test(userData.value.password)) strength += 25;
  
  if (/\d/.test(userData.value.password)) strength += 12.5;
  
  if (/[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(userData.value.password)) strength += 12.5;
  
  return strength;
});

const passwordStrengthText = computed(() => {
  const strength = passwordStrength.value;
  
  if (strength < 25) return 'Very weak';
  if (strength < 50) return 'Weak';
  if (strength < 75) return 'Medium';
  if (strength < 100) return 'Strong';
  return 'Very strong';
});

const passwordStrengthClass = computed(() => {
  const strength = passwordStrength.value;
  
  if (strength < 25) return 'bg-danger';
  if (strength < 50) return 'bg-warning';
  if (strength < 75) return 'bg-info';
  return 'bg-success';
});

const isFormValid = computed(() => {
  const requiredFieldsValid = 
    userData.value.nom_prenom && 
    userData.value.username && 
    userData.value.email &&
    selectedRoleId.value && 
    userData.value.password;
  
  const noValidationErrors = 
    !validation.value.nom_prenom && 
    !validation.value.username && 
    !validation.value.email && 
    !validation.value.role && 
    !validation.value.password;
  
  if (!isEditMode.value) {
    return requiredFieldsValid && 
           noValidationErrors && 
           passwordConfirm.value && 
           !validation.value.passwordConfirm;
  }
  
  return requiredFieldsValid && noValidationErrors;
});

const submitForm = async () => {
  validateFullName();
  validateUsername();
  validateEmail();
  validateRole();
  validatePassword();
  
  if (!isEditMode.value) {
    validatePasswordConfirm();
  }
  
  if (!isFormValid.value) {
    userStore.showToast('Please correct the errors in the form', 'error');
    return;
  }
  
  isSubmitting.value = true;
  
  try {
    const formData = {
      nom_prenom: userData.value.nom_prenom,
      username: userData.value.username,
      email: userData.value.email,
      role: selectedRoleId.value,
      is_active: userData.value.is_active,
      password: userData.value.password,
      current_password: isEditMode.value ? userData.value.password : undefined,
      
    };
    
    if (isEditMode.value) {
      const updatedUser = await userStore.updateUser(userId.value, formData);
      if (updatedUser) {
        userStore.showToast('User updated successfully', 'success');
        router.push('/users');
      }
    } else {
      formData.confirm_password = passwordConfirm.value;
      const newUser = await userStore.createUser(formData);
      if (newUser) {
        userStore.showToast('User created successfully', 'success');
        router.push('/users');
      }
    }
  } catch (error) {
    userStore.showToast('Error submitting form', 'error');
  } finally {
    isSubmitting.value = false;
  }
};

function handleToastClose() {
  userStore.toast.show = false;
}

const cancelForm = () => {
  router.push('/users');
};

onMounted(async () => {
  await fetchRoles();
  
  if (isEditMode.value) {
    await fetchUserData();
  }
});

watch(selectedRoleId, (newValue) => {
  if (newValue) {
    userData.value.role = newValue;
  }
});
</script>

<style scoped>
.h-55 {
  height: 55px;
}

.is-invalid {
  border-color: #dc3545;
  padding-right: calc(1.5em + 0.75rem);
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 12 12' width='12' height='12' fill='none' stroke='%23dc3545'%3e%3ccircle cx='6' cy='6' r='4.5'/%3e%3cpath stroke-linejoin='round' d='M5.8 3.6h.4L6 6.5z'/%3e%3ccircle cx='6' cy='8.2' r='.6' fill='%23dc3545' stroke='none'/%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right calc(0.375em + 0.1875rem) center;
  background-size: calc(0.75em + 0.375rem) calc(0.75em + 0.375rem);
}

.invalid-feedback {
  display: block;
  width: 100%;
  margin-top: 0.25rem;
  font-size: 80%;
  color: #dc3545;
}

.form-label {
  font-weight: 500;
  color: #495057;
  margin-bottom: 0.5rem;
}

.form-switch .form-check-input {
  width: 3em;
  height: 1.5em;
  cursor: pointer;
}

.form-switch .form-check-input:checked {
  background-color: #0d6efd;
  border-color: #0d6efd;
}

.btn-primary {
  background-color: #0d6efd;
  border-color: #0d6efd;
}

.btn-outline-secondary {
  color: #6c757d;
  border-color: #6c757d;
}

.btn:disabled {
  cursor: not-allowed;
  opacity: 0.65;
}

.password-strength {
  margin-top: 15px;
}

.password-strength .progress {
  height: 6px;
  margin-top: 5px;
}
</style>