<template>
  <div class="main-content-container overflow-hidden">
    <PageTitle pageTitle="Integrated Tools" subTitle="Config" />
    
    <div v-if="isLoading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading integrated tools...</p>
    </div>
    
    <div v-else-if="hasError" class="alert alert-danger my-4" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      Error loading integrated tools. Please try again.
      <button class="btn btn-sm btn-outline-danger ms-3" @click="fetchTools">Retry</button>
    </div>
    
    <div v-else class="row">
      <div :class="selectedTool ? 'col-lg-8' : 'col'">
        <div class="row">
          <div v-if="!tools.length && !isLoading" class="col-12">
            <div class="alert alert-info">
              <i class="bi bi-info-circle me-2"></i>
              No integrated tools available.
            </div>
          </div>
          
          <div class="col-lg-6 col-md-6 mb-4" v-for="tool in tools" :key="tool.name">
            <div class="card bg-white border-0 rounded-3 p-4 py-lg-5 h-100">
              <div class="d-flex justify-content-between align-items-start mb-3">
                <div class="mb-3 position-relative">
                  <img :src="getToolIcon(tool.name)" class="rounded-circle" style="width: 54px; height: 54px" :alt="`${tool.name} icon`" />
                  <button v-if="tool.name === 'Cerebrate'" 
                    class="btn btn-sm btn-light rounded-circle position-absolute" 
                    style="bottom: 0; right: 0;"
                    @click="refreshTool(tool)"
                    :disabled="isRefreshing || operationInProgress || !authStore.hasPermission('integrations_edit')"
                    title="Refresh data">
                    <i class="bi" :class="isRefreshing ? 'bi-arrow-repeat spin' : 'bi-arrow-clockwise'"></i>
                  </button>
                </div>
                <div class="form-check form-switch">
                  <input class="form-check-input" type="checkbox"
                          :checked="tool.is_active" 
                         @change="updateToolStatus(tool)" 
                         :id="`tool-active-${tool.name}`"
                         :disabled="operationInProgress || !authStore.hasPermission('integrations_toggle')">
                  <label class="form-check-label" :for="`tool-active-${tool.name}`">
                    {{ tool.is_active ? 'Active' : 'Inactive' }}
                  </label>
                </div>
              </div>
              
              <h3 class="mb-3">{{ tool.name }}</h3>
              <p class="mb-3" style="white-space: pre-line">{{ tool.description || 'No description available.' }}</p>
              <p class="text-muted small">Last updated: {{ formatDate(tool.last_updated) }}</p>
              
              <div class="mt-auto pt-3">
                <button class="btn btn-primary py-2 px-4" 
                        @click="selectTool(tool)"
                        :disabled="operationInProgress">
                  Configure
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="selectedTool" class="col-lg-4">
        <div class="card bg-white border-0 rounded-3 mb-4 position-sticky" style="top: 20px;">
          <div class="card-header bg-white d-flex justify-content-between align-items-center border-bottom">
            <h5 class="m-0">Configuration of {{ selectedTool.name }}</h5>
            <button type="button" class="btn-close" @click="closePanel" :disabled="isSaving"></button>
          </div>
          
          <div v-if="isConfigLoading" class="card-body p-4 text-center">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2">Loading configuration...</p>
          </div>
          
          <div v-else-if="configError" class="card-body p-4">
            <div class="alert alert-danger" role="alert">
              <i class="bi bi-exclamation-triangle-fill me-2"></i>
              Error loading configuration.
              <button class="btn btn-sm btn-outline-danger ms-2" @click="reloadConfig">Retry</button>
            </div>
          </div>
          
          <div v-else class="card-body p-4">
            <div v-if="selectedTool.name === 'RTIR' && toolConfig">
              <div class="mb-4">
                <label class="form-label mb-2">URL</label>
                <input
                  type="url"
                  class="form-control"
                  v-model="toolConfig.url"
                  placeholder="https://rtir.example.com"
                  @blur="validateUrl('rtir')"
                  :disabled="isSaving || !authStore.hasPermission('integrations_edit')"
                />
                <div class="text-danger small mt-1" v-if="validation.rtir_url">{{ validation.rtir_url }}</div>
              </div>
              
              <div class="mb-4">
                <label class="form-label mb-2">Username</label>
                <input
                  type="text"
                  class="form-control"
                  v-model="toolConfig.username"
                  placeholder="admin"
                  :disabled="isSaving || !authStore.hasPermission('integrations_edit')"
                />
                <div class="text-danger small mt-1" v-if="validation.rtir_username">{{ validation.rtir_username }}</div>
              </div>
              
              <div class="mb-4">
                <label class="form-label mb-2">Password</label>
                <div class="input-group">
                  <input
                    :type="showPassword.rtir ? 'text' : 'password'"
                    class="form-control"
                    v-model="toolConfig.password"
                    placeholder="••••••••••"
                    :disabled="isSaving || !authStore.hasPermission('integrations_edit')"
                  />
                  <button 
                    class="btn btn-outline-secondary d-flex align-items-center justify-content-center"
                    type="button"
                    @click="showPassword.rtir = !showPassword.rtir"
                    :disabled="isSaving || !authStore.hasPermission('integrations_edit')"
                  >
                    <i class="bi" :class="showPassword.rtir ? 'bi-eye-slash-fill' : 'bi-eye-fill'"></i>
                  </button>
                </div>
                <div class="text-danger small mt-1" v-if="validation.rtir_password">{{ validation.rtir_password }}</div>
              </div>
            </div>
            
            <div v-if="selectedTool.name === 'Cerebrate' && toolConfig">
              <div class="mb-4">
                <label class="form-label mb-2">URL</label>
                <input
                  type="url"
                  class="form-control"
                  v-model="toolConfig.url"
                  placeholder="https://cerebrate.example.com"
                  @blur="validateUrl('cerebrate')"
                  :disabled="isSaving || !authStore.hasPermission('integrations_edit')"
                />
                <div class="text-danger small mt-1" v-if="validation.cerebrate_url">{{ validation.cerebrate_url }}</div>
              </div>
              
              <div class="mb-4">
                <label class="form-label mb-2">API Key</label>
                <div class="input-group">
                  <input
                    :type="showPassword.cerebrate ? 'text' : 'password'"
                    class="form-control"
                    v-model="toolConfig.api_key"
                    placeholder="Your API key"
                    :disabled="isSaving || !authStore.hasPermission('integrations_edit')"
                  />
                  <button 
                    class="btn btn-outline-secondary d-flex align-items-center justify-content-center"
                    type="button"
                    @click="showPassword.cerebrate = !showPassword.cerebrate"
                    :disabled="isSaving || !authStore.hasPermission('integrations_edit')"
                  >
                    <i class="bi" :class="showPassword.cerebrate ? 'bi-eye-slash-fill' : 'bi-eye-fill'"></i>
                  </button>
                </div>
                <div class="text-danger small mt-1" v-if="validation.cerebrate_api_key">{{ validation.cerebrate_api_key }}</div>
              </div>
              
              <div class="mb-4">
                <label class="form-label mb-2">Refresh Frequency</label>
                <select class="form-select" v-model="toolConfig.refresh_frequency" :disabled="isSaving || !authStore.hasPermission('integrations_edit')">
                  <option v-for="option in refreshFrequencyOptions" :key="option.value" :value="option.value">
                    {{ option.label }}
                  </option>
                </select>
                <div class="text-danger small mt-1" v-if="validation.cerebrate_refresh">{{ validation.cerebrate_refresh }}</div>
              </div>
            </div>

            <div v-if="selectedTool.name === 'VirusTotal' && toolConfig">
              <div class="mb-4">
                <label class="form-label mb-2">API Key</label>
                <div class="input-group">
                  <input
                    :type="showPassword.virustotal ? 'text' : 'password'"
                    class="form-control"
                    v-model="toolConfig.api_key"
                    placeholder="Your VirusTotal API key"
                    :disabled="isSaving || !authStore.hasPermission('integrations_edit')"
                  />
                  <button 
                    class="btn btn-outline-secondary d-flex align-items-center justify-content-center"
                    type="button"
                    @click="showPassword.virustotal = !showPassword.virustotal"
                    :disabled="isSaving || !authStore.hasPermission('integrations_edit')"
                  >
                    <i class="bi" :class="showPassword.virustotal ? 'bi-eye-slash-fill' : 'bi-eye-fill'"></i>
                  </button>
                </div>
                <div class="text-danger small mt-1" v-if="validation.virustotal_api_key">{{ validation.virustotal_api_key }}</div>
              </div>
              
              <div class="mb-4">
                <label class="form-label mb-2">Scan Period</label>
                <select class="form-select" v-model="toolConfig.scan_frequency" :disabled="isSaving || !authStore.hasPermission('integrations_edit')">
                  <option v-for="option in refreshFrequencyOptions" :key="option.value" :value="option.value">
                    {{ option.label }}
                  </option>
                </select>
                <div class="text-danger small mt-1" v-if="validation.virustotal_scan">{{ validation.virustotal_scan }}</div>
              </div>
            </div>

            <div class="d-flex justify-content-end mt-4">
              <button class="btn btn-secondary me-2" @click="closePanel" :disabled="isSaving">Cancel</button>
              <button class="btn btn-primary" @click="saveConfig" :disabled="isSaving || !authStore.hasPermission('integrations_edit')">
                <span v-if="isSaving" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                {{ isSaving ? 'Saving...' : 'Save' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <Toast 
      :show="integrationStore.toast.show"
      :message="integrationStore.toast.message"
      :type="integrationStore.toast.type"
      :autoClose="true"
      :duration="integrationStore.toast.duration"
      @close="handleToastClose"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from "vue";
import { useIntegrationStore } from "@/stores/integration.store";
import { REFRESH_FREQUENCY_OPTIONS } from "@/types/integration.types";
import PageTitle from "@/components/Common/PageTitle.vue";
import Toast from "@/components/Common/Toast.vue";
import { useAuthStore } from '@/stores/auth.store';
const authStore = useAuthStore();

const integrationStore = useIntegrationStore();

const tools = ref([]);
const selectedTool = ref(null);
const toolConfig = ref(null);
const isLoading = ref(false);
const isConfigLoading = ref(false);
const isSaving = ref(false);
const isRefreshing = ref(false);
const hasError = ref(false);
const configError = ref(false);

const operationInProgress = computed(() => {
  return isLoading.value || isConfigLoading.value || isSaving.value || isRefreshing.value;
});

const showPassword = reactive({
  rtir: false,
  cerebrate: false,
  virustotal: false
});

const validation = reactive({
  rtir_url: '',
  rtir_username: '',
  rtir_password: '',
  cerebrate_url: '',
  cerebrate_api_key: '',
  cerebrate_refresh: '',
  virustotal_api_key: '',
  virustotal_scan: ''
});

const refreshFrequencyOptions = REFRESH_FREQUENCY_OPTIONS;

function handleToastClose() {
  integrationStore.toast.show = false;
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  
  try {
    const date = new Date(dateString);
    if (isNaN(date) || !isFinite(date.getTime())) {
      return 'Date invalide';
    }
    
    return new Intl.DateTimeFormat('fr-FR', { 
      day: '2-digit', 
      month: '2-digit', 
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  } catch (error) {
    console.error("Erreur de formatage de date:", error);
    return 'Date invalide';
  }
};


const getToolIcon = (toolName) => {
  const defaultIcon = '#';
  
  const toolIcons = {
    "Cerebrate": 'data:image/png;base64,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',
    "RTIR": 'data:image/jpeg;base64,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',
    "VirusTotal": 'data:image/png;base64,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'
  }
  
  return toolIcons[toolName] || defaultIcon;
};

const fetchTools = async () => {
  if (isLoading.value) return;
  
  isLoading.value = true;
  hasError.value = false;
  
  try {
    await integrationStore.fetchIntegrations();
    tools.value = integrationStore.integrations;
  } catch (error) {
    hasError.value = true;
    integrationStore.showToast("Error loading tools integrated", "error");
  } finally {
    isLoading.value = false;
  }
};

const selectTool = async (tool) => {
  selectedTool.value = tool;
  
  toolConfig.value = null;
  configError.value = false;
  
  Object.keys(validation).forEach(key => validation[key] = '');
  
  await loadToolConfig(tool.name);
};

const loadToolConfig = async (toolName) => {
  isConfigLoading.value = true;
  configError.value = false;
  
  try {
    const config = await integrationStore.fetchIntegrationConfig(toolName);
    toolConfig.value = { ...config };
  } catch (error) {
    configError.value = true;
    integrationStore.showToast(`Error loading tools configuration ${toolName}`, "error");
  } finally {
    isConfigLoading.value = false;
  }
};

const reloadConfig = () => {
  if (selectedTool.value) {
    loadToolConfig(selectedTool.value.name);
  }
};

const closePanel = () => {
  if (isSaving.value) return;
  
  selectedTool.value = null;
  toolConfig.value = null;
  configError.value = false;
};

const updateToolStatus = async (tool) => {
  if (!authStore.hasPermission('integrations_toggle')) {
    integrationStore.showToast("Permission denied", "error");
    return;
  }
  if (operationInProgress.value) return ;
  const previousStatus = tool.is_active;
  isLoading.value = true;
  
  try {
    const response = await integrationStore.toggleIntegrationStatus(tool.name);
    if (response && typeof response.is_active !== "undefined") {
      tool.is_active = !previousStatus;
    }else tool.is_active = previousStatus;
  } catch (error) {
    tool.is_active = previousStatus;
    console.error(`Error toggling status for ${tool.name}:`, error);
  } finally {
    isLoading.value = false;
  }
};

const refreshTool = async (tool) => {
  if (!authStore.hasPermission('integrations_edit')) {
    integrationStore.showToast("Permission denied", "error");
    return;
  }
  if (isRefreshing.value || operationInProgress.value) return;
  
  isRefreshing.value = true;
  
  try {
    if (tool.name === 'Cerebrate') {
      await integrationStore.refreshCerebrate();
    }
  } catch (error) {
    integrationStore.showToast("Error refreshing tool", "error");
  } finally {
    isRefreshing.value = false;
  }
};

const validateUrl = (toolType) => {
  if (!toolConfig.value?.url) {
    validation[`${toolType}_url`] = "URL is required";
    return false;
  }
  
  try {
    const url = new URL(toolConfig.value.url);
    if (url.protocol !== 'http:' && url.protocol !== 'https:') {
      validation[`${toolType}_url`] = "URL must start with http:// or https://";
      return false;
    }
    validation[`${toolType}_url`] = '';
    return true;
  } catch (e) {
    validation[`${toolType}_url`] = "URL is invalid";
    return false;
  }
};

const validateRTIR = () => {
  let isValid = true;
  
  if (!validateUrl('rtir')) {
    isValid = false;
  }
  
  if (!toolConfig.value?.username) {
    validation.rtir_username = "username is required";
    isValid = false;
  } else {
    validation.rtir_username = "";
  }
  
  if (!toolConfig.value?.password && !toolConfig.value?.id) {
    validation.rtir_password = "Password is required";
    isValid = false;
  } else {
    validation.rtir_password = "";
  }
  
  return isValid;
};

const validateCerebrate = () => {
  let isValid = true;
  
  if (!validateUrl('cerebrate')) {
    isValid = false;
  }
  
  if (!toolConfig.value?.api_key) {
    validation.cerebrate_api_key = "API key is required";
    isValid = false;
  } else {
    validation.cerebrate_api_key = "";
  }
  
  if (!toolConfig.value?.refresh_frequency) {
    validation.cerebrate_refresh = "Refresh frequency is required";
    isValid = false;
  } else {
    validation.cerebrate_refresh = "";
  }
  
  return isValid;
};

const validateVirusTotal = () => {
  let isValid = true;
  
  if (!toolConfig.value?.api_key) {
    validation.virustotal_api_key = "API key is required";
    isValid = false;
  } else {
    validation.virustotal_api_key = "";
  }
  
  if (!toolConfig.value?.scan_frequency) {
    validation.virustotal_scan = "Frequency is required";
    isValid = false;
  } else {
    validation.virustotal_scan = "";
  }
  
  return isValid;
};

const saveConfig = async () => {
  if (!authStore.hasPermission('integrations_edit')) {
    integrationStore.showToast("Permission denied", "error");
    return;
  }
  if (!toolConfig.value || !selectedTool.value) {
    integrationStore.showToast("Configuration invalide", "error");
    return;
  }
  
  let isValid = false;
  
  if (selectedTool.value.name === 'RTIR') {
    isValid = validateRTIR();
  } else if (selectedTool.value.name === 'Cerebrate') {
    isValid = validateCerebrate();
  } else if (selectedTool.value.name === 'VirusTotal') {
    isValid = validateVirusTotal();
  }
  
  if (!isValid) {
    integrationStore.showToast("Fill all required field", "error");
    return;
  }
  
  isSaving.value = true;
  
  try {
    if (selectedTool.value.name === 'RTIR') {
      await integrationStore.updateRTIRConfig(toolConfig.value);
    } else if (selectedTool.value.name === 'Cerebrate') {
      await integrationStore.updateCerebrateConfig(toolConfig.value);
    } else if (selectedTool.value.name === 'VirusTotal') {
      await integrationStore.updateVirusTotalConfig(toolConfig.value);
    }

    integrationStore.showToast("Configuration saved successfully", "success");
    closePanel();
  } catch (error) {
    console.error(`Error saving ${selectedTool.value.name}:`, error);
  } finally {
    isSaving.value = false;
  }
};

onMounted(() => {
  fetchTools();
});
</script>

<style scoped>
.card {
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
}

.btn-light {
  background-color: #f8f9fa;
  border-color: #f8f9fa;
}

.btn-light:hover {
  background-color: #e2e6ea;
  border-color: #dae0e5;
}

.btn-outline-secondary .bi {
  font-size: 1.2rem;
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

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>