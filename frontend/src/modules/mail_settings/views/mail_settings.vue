<template>
  <PageTitle pageTitle="Email Settings" subTitle="Config" />
  
  <div v-if="loading" class="text-center my-5">
    <div class="spinner-border text-primary" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
    <p class="mt-2">Loading mail settings...</p>
  </div>

  <div v-else-if="mailConfig" class="row">
    <div class="col-12">
      <div class="card bg-white border-0 rounded-3 mb-4">
        <div class="card-body p-4">
          <div class="d-flex justify-content-between align-items-center text-center flex-wrap gap-2 showing-wrap border-bottom pb-3 mb-4">
            <h3 class="fs-16 fw-semibold mb-0">Email Settings Configuration</h3>
          </div>

          <form @submit.prevent="updateConfig" class="row g-3">
            <div class="col-12 mb-3">
              <div class="d-flex align-items-center">
                <div class="form-check form-switch">
                  <input 
                    type="checkbox" 
                    class="form-check-input" 
                    id="is_active" 
                    v-model="isActive"
                    @change="toggleActiveStatus"
                    :disabled="toggling || !hasPermission('mail_settings_toggle')"
                  />
                  <label class="form-check-label form-label fw-semibold" for="is_active">
                    Configuration {{ isActive ? 'active' : 'inactive' }}
                    <span v-if="toggling" class="spinner-border spinner-border-sm ms-2" role="status"></span>
                  </label>
                </div>
              </div>
            </div>

            <div  class="col-12">
              <div class="row g-3">
                <div class="col-12 mb-3">
                  <label class="form-label text-secondary fs-14">SMTP Server & Port<span class="text-danger">*</span></label>
                  <div class="input-group">
                    <input
                      type="text"
                      class="form-control h-55"
                      v-model="mailConfig.smtp_server"
                      @input="filterServerInput"
                      @blur="validateServer"
                      :class="{ 'is-invalid': validationErrors.smtp_server }"
                      placeholder="IP Address or Domain Name"
                      :disabled="!hasPermission('mail_settings_edit')"
                    />
                    <span class="input-group-text h-55">:</span>
                    <input
                      type="text"
                      class="form-control h-55"
                      style="max-width: 150px;"
                      v-model="portInput"
                      @input="filterPortInput"
                      @blur="validatePort"
                      :class="{ 'is-invalid': validationErrors.smtp_port }"
                      placeholder="Port"
                      :disabled="!hasPermission('mail_settings_edit')"
                    />
                  </div>
                  <div class="d-flex mt-1">
                    <div v-if="validationErrors.smtp_server" class="invalid-feedback d-block me-3">
                      {{ validationErrors.smtp_server }}
                    </div>
                    <div v-if="validationErrors.smtp_port" class="invalid-feedback d-block">
                      {{ validationErrors.smtp_port }}
                    </div>
                  </div>
                </div>

                <div class="col-12 mb-3">
                  <label class="form-label text-secondary fs-14">Security Configuration</label>
                  <div class="d-flex gap-4">
                    <div class="form-check">
                      <input 
                        type="checkbox" 
                        class="form-check-input" 
                        id="use_tls" 
                        v-model="mailConfig.use_tls"
                        :disabled="mailConfig.use_ssl || !hasPermission('mail_settings_edit')"
                        @change="handleTLSToggle"
                      />
                      <label class="form-check-label" for="use_tls">Use TLS</label>
                    </div>
                    
                    <div class="form-check">
                      <input 
                        type="checkbox" 
                        class="form-check-input" 
                        id="use_ssl" 
                        v-model="mailConfig.use_ssl"
                        :disabled="mailConfig.use_tls || !hasPermission('mail_settings_edit')"
                        @change="handleSSLToggle"
                      />
                      <label class="form-check-label" for="use_ssl">Use SSL</label>
                    </div>
                  </div>
                </div>

                <div class="col-12 mb-3">
                  <label class="form-label text-secondary fs-14">Email host <span class="text-danger">*</span></label>
                  <input
                    type="email"
                    class="form-control h-55"
                    v-model="mailConfig.email_host"
                    @blur="validateEmail"
                    @input="updateReplyTo"
                    :class="{ 'is-invalid': validationErrors.email_host }"
                    placeholder="email@oju.com"
                    :disabled="!hasPermission('mail_settings_edit')"
                  />
                  <div v-if="validationErrors.email_host" class="invalid-feedback">
                    {{ validationErrors.email_host }}
                  </div>
                </div>

                <div class="col-12 mb-3">
                  <label class="form-label text-secondary fs-14">Email password <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <input
                      :type="showPassword ? 'text' : 'password'"
                      class="form-control h-55"
                      v-model="mailConfig.email_password"
                      @blur="validatePassword"
                      :class="{ 'is-invalid': validationErrors.email_password }"
                      placeholder="Password"
                      :disabled="!hasPermission('mail_settings_edit')"
                    />
                    <button 
                      class="btn btn-outline-secondary h-55 d-flex align-items-center justify-content-center"
                      type="button"
                      @click="showPassword = !showPassword"
                    >
                      <i class="bi" :class="showPassword ? 'bi-eye-slash-fill' : 'bi-eye-fill'"></i>
                    </button>
                  </div>
                  <div v-if="validationErrors.email_password" class="invalid-feedback">
                    {{ validationErrors.email_password }}
                  </div>
                </div>

                <div class="col-12 mb-3">
                  <label class="form-label text-secondary fs-14">Default sender name <span class="text-danger">*</span></label>
                  <input
                    type="text"
                    class="form-control h-55"
                    v-model="mailConfig.default_sender_name"
                    @blur="validateSenderName"
                    :class="{ 'is-invalid': validationErrors.default_sender_name }"
                    placeholder="Sender Name"
                    :disabled="!hasPermission('mail_settings_edit')"
                  />
                  <div v-if="validationErrors.default_sender_name" class="invalid-feedback">
                    {{ validationErrors.default_sender_name }}
                  </div>
                </div>

                <div class="col-12 mb-3">
                  <label class="form-label text-secondary fs-14">Default reply-to email</label>
                  <input
                    type="email"
                    class="form-control h-55"
                    v-model="mailConfig.default_reply_to"
                    @blur="validateReplyTo"
                    :class="{ 'is-invalid': validationErrors.default_reply_to }"
                    placeholder="reply@example.com"
                    :disabled="!hasPermission('mail_settings_edit')"
                  />
                  <div v-if="validationErrors.default_reply_to" class="invalid-feedback">
                    {{ validationErrors.default_reply_to }}
                  </div>
                </div>

                <div class="col-12">
                  <p class="text-muted small"><span class="text-danger">*</span> Required areas</p>
                </div>
              </div>
            </div>

            <div class="col-12 mt-4">
              <div class="d-flex flex-wrap gap-3 align-items-center">
                <button
                  class="btn btn-primary text-white fw-semibold py-2 px-4"
                  type="submit"
                  :disabled="!isFormValid || updating || !hasPermission('mail_settings_edit')"
                >
                  <span v-if="updating" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                  {{ updating ? 'Updating in progress...' : 'Update the configuration' }}
                </button>
                <button
                  class="btn btn-outline-secondary fw-semibold py-2 px-4"
                  type="button"
                  @click="resetForm"
                  :disabled="updating || !hasPermission('mail_settings_edit')"
                >
                  Annuler
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
  
  <Toast 
    :show="emailStore.toast.show" 
    :message="emailStore.toast.message" 
    :type="emailStore.toast.type" 
    :autoClose="true"
    :duration="emailStore.toast.duration"
    @close="handleToastClose" 
  />
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import PageTitle from "@/components/Common/PageTitle.vue";
import Toast from "@/components/Common/Toast.vue";
import { useEmailStore } from '@/stores/email.store';
import { useAuthStore } from '@/stores/auth.store';
import {hasPermission} from '@/utils/permissions';

const authStore = useAuthStore();

const emailStore = useEmailStore();

const portInput = ref('25');
const showPassword = ref(false);
const isActive = ref(false); 

const mailConfig = computed(() => emailStore.getMailConfig);
const loading = computed(() => emailStore.isLoading);
const updating = computed(() => emailStore.isUpdating);
const toggling = computed(() => emailStore.isToggling);
const error = computed(() => emailStore.error);
const validationErrors = computed(() => emailStore.validationErrors);
const isFormValid = computed(() => emailStore.isFormValid);

const filterServerInput = () => {
  if (!mailConfig.value) return;
  
  const validChars = /[^a-zA-Z0-9.-]/g;
  mailConfig.value.smtp_server = mailConfig.value.smtp_server.replace(validChars, '');
  emailStore.validateServer(mailConfig.value.smtp_server);
};

const filterPortInput = () => {
  portInput.value = portInput.value.replace(/\D/g, '');
    
  const portNum = parseInt(portInput.value, 10);
  if (portNum > 65535) {
    portInput.value = '65535';
  }
    
  if (mailConfig.value) {
    mailConfig.value.smtp_port = portInput.value ? parseInt(portInput.value, 10) : 0;
    emailStore.validatePort(mailConfig.value.smtp_port);
  }
};

const handleTLSToggle = () => {
  if (mailConfig.value?.use_tls) {
    mailConfig.value.use_ssl = false;
  }
};

const handleSSLToggle = () => {
  if (mailConfig.value?.use_ssl) {
    mailConfig.value.use_tls = false;
  }
};

const updateReplyTo = () => {
  if (!mailConfig.value) return;
  
  if (!mailConfig.value.default_reply_to || 
      mailConfig.value.default_reply_to === mailConfig.value.email_host) {
    mailConfig.value.default_reply_to = mailConfig.value.email_host;
  }
};

const validateServer = () => {
  if (!mailConfig.value) return;
  emailStore.validateServer(mailConfig.value.smtp_server);
};

const validatePort = () => {
  if (!mailConfig.value) return;
  emailStore.validatePort(mailConfig.value.smtp_port);
};

const validateEmail = () => {
  if (!mailConfig.value) return;
  emailStore.validateEmail(mailConfig.value.email_host);
};

const validatePassword = () => {
  if (!mailConfig.value) return;
  emailStore.validatePassword(mailConfig.value.email_password);
};

const validateSenderName = () => {
  if (!mailConfig.value) return;
  emailStore.validateSenderName(mailConfig.value.default_sender_name);
};

const validateReplyTo = () => {
  if (!mailConfig.value || !mailConfig.value.default_reply_to) return;
  emailStore.validateReplyTo(mailConfig.value.default_reply_to);
};

const toggleActiveStatus = async () => {
  if ( !authStore.hasPermission('mail_settings_toggle')){
    emailStore.showToast('Permission denied to perform this action', 'error');
    return;
  }
  if (toggling.value) {
    isActive.value = mailConfig.value?.is_active || false;
    return;
  }
  
  const previousState = mailConfig.value?.is_active || false;
  
  try {
    const response = await emailStore.toggleActiveStatus();
    
    isActive.value = response.is_active;
    
  } catch (error) {
    isActive.value = previousState;
  }
};

const resetForm = () => {
  emailStore.resetForm();
};

const updateConfig = async () => {
  if ( !authStore.hasPermission('mail_settings_edit')){
    emailStore.showToast('Permission denied to perform this action', 'error');
    return;
  }
  if (updating.value || !mailConfig.value) return;
  
  try {
    emailStore.validateAllFields(mailConfig.value);
    
    if (!isFormValid.value) {
      emailStore.showToast('Change the error in the form', 'error');
      return;
    }
    
    const success = await emailStore.updateMailConfig(mailConfig.value);
    
  } catch (error) {
    console.error(':', error);
  }
};

const fetchConfig = async () => {
  try {
    await emailStore.fetchMailConfig();
    if (mailConfig.value) {
      portInput.value = mailConfig.value.smtp_port.toString();
      isActive.value = mailConfig.value.is_active;
    }
  } catch (error) {
    console.error(':', error);
  }
};

const handleToastClose = () => {
  emailStore.toast.show = false;
};

watch(() => mailConfig.value?.smtp_port, (newVal) => {
  if (newVal !== undefined) {
    portInput.value = newVal.toString();
  }
});

watch(() => mailConfig.value?.is_active, (newVal) => {
  if (newVal !== undefined) {
    isActive.value = newVal;
  }
});

onMounted(() => {
  fetchConfig();
});
</script>

<style scoped>
.h-55 {
  height: 55px;
}

input:disabled, 
button:disabled,
.form-control:disabled,
.btn:disabled {
  opacity: 0.65 !important;
  cursor: not-allowed !important;
  background-color: #f5f5f5 !important;
  border-color: #ddd !important;
  color: #777 !important;
  pointer-events: none !important;
}

.form-disabled {
  opacity: 0.8;
  cursor: not-allowed;
  background-color: #f8f9fa;
  border-radius: 4px;
  padding: 15px;
  border: 1px solid #eee;
}

.invalid-feedback {
  display: block;
  width: 100%;
  margin-top: 0.25rem;
  font-size: 80%;
  color: #dc3545;
}

.is-invalid {
  border-color: #dc3545;
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

.input-group .input-group-text {
  display: flex;
  align-items: center;
  padding: 0.375rem 0.75rem;
  font-weight: 500;
}

.btn-outline-secondary .bi {
  font-size: 1.2rem;
}
</style>