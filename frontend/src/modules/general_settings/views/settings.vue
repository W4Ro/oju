<template>
  <PageTitle pageTitle="General Settings" subTitle="Config" />
  
  <div v-if="loading" class="text-center my-5">
    <div class="spinner-border text-primary" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
    <p class="mt-2">Loading general configurations...</p>
  </div>
  

  <div v-else-if="config" class="row">
    <div class="col-12">
      <div class="card bg-white border-0 rounded-3 mb-4">
        <div class="card-body p-4">
          <div class="d-flex justify-content-between align-items-center text-center flex-wrap gap-2 showing-wrap border-bottom pb-3 mb-4">
            <h3 class="fs-16 fw-semibold mb-0">General Configurations</h3>
          </div>

          <form @submit.prevent="saveConfig" class="row g-3">
            <div class="col-12 mb-3">
              <label class="form-label text-secondary fs-14">Email <span class="text-danger">*</span></label>
              <input
                type="email"
                class="form-control h-55"
                v-model="config.email"
                @blur="validateEmail"
                :class="{ 'is-invalid': validationErrors.email }"
                placeholder="admin@example.com"
                :disabled="!authStore.hasPermission('config_edit')"
              />
              <div class="text-danger small mt-1" v-if="validationErrors.email">{{ validationErrors.email }}</div>
            </div>

            <div class="col-12 mb-3">
              <label class="form-label text-secondary fs-14">Use Proxies</label>
              <div class="form-check">
                <input 
                  type="checkbox" 
                  class="form-check-input" 
                  id="use_proxy" 
                  v-model="useProxy"
                  @change="toggleProxyUsage"
                  :disabled="toggling.proxy || !authStore.hasPermission('config_toggle')"
                />
                <label class="form-check-label" for="use_proxy">
                  Enable proxy usage
                  <span v-if="toggling.proxy" class="spinner-border spinner-border-sm ms-2" role="status"></span>
                </label>
              </div>
              
              <div class="mt-3">
                <div class="multi-select-container">
                  <div class="form-control h-auto p-1 d-flex flex-wrap gap-1 select-with-tags" :class="{ 'is-invalid': validationErrors.proxy }">
                    <div v-for="proxy in selectedProxies" :key="proxy" class="selected-tag" style="background-color: #e3f2fd; color: #0d6efd;">
                      {{ proxy }}
                      <button type="button" class="tag-remove" @click="removeProxy(proxy)">×</button>
                    </div>
                    <div class="flex-grow-1">
                      <input
                        type="text"
                        class="form-control border-0 bg-transparent p-1"
                        v-model="proxyInput"
                        @keydown.enter.prevent="addProxy"
                        @blur="validateProxyInput"
                        placeholder="Add a proxy"
                        :disabled="!authStore.hasPermission('config_edit')"
                      />
                    </div>
                  </div>
                </div>
                <div class="text-danger small mt-1" v-if="validationErrors.proxy">{{ validationErrors.proxy }}</div>
                <div class="text-muted small mt-1">Format: ip:port or domain:port with optional username and password</div>
              </div>
            </div>
            
            <div class="col-12 mb-3">
              <label class="form-label text-secondary fs-14">DNS Servers <span class="text-danger">*</span></label>
              <div class="multi-select-container">
                <div class="form-control h-auto p-1 d-flex flex-wrap gap-1 select-with-tags" :class="{ 'is-invalid': validationErrors.dns }">
                  <div v-for="dns in selectedDnsServers" :key="dns" class="selected-tag" style="background-color: #f0f9ff; color: #0dcaf0;">
                    {{ dns }}
                    <button type="button" class="tag-remove" @click="removeDnsServer(dns)">×</button>
                  </div>
                  <div class="flex-grow-1">
                    <input
                      type="text"
                      class="form-control border-0 bg-transparent p-1"
                      v-model="dnsServerInput"
                      @keydown.enter.prevent="addDnsServer"
                      @input="filterDnsInput"
                      @blur="validateDnsInput"
                      placeholder="Add a DNS server (e.g., 8.8.8.8)"
                      :disabled="!authStore.hasPermission('config_edit')"
                    />
                  </div>
                </div>
              </div>
              <div class="text-danger small mt-1" v-if="validationErrors.dns">{{ validationErrors.dns }}</div>
              <div class="text-muted small mt-1">Format: IP addresses only (e.g., 8.8.8.8, 1.1.1.1)</div>
            </div>

            <div class="col-12 mb-3">
              <label class="form-label text-secondary fs-14">User-Agent <span class="text-danger">*</span></label>
              <input
                type="text"
                class="form-control h-55"
                v-model="config.user_agent"
                @blur="validateUserAgent"
                :class="{ 'is-invalid': validationErrors.userAgent }"
                placeholder="Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."
                :disabled="!authStore.hasPermission('config_edit')"
              />
              <div class="text-danger small mt-1" v-if="validationErrors.userAgent">{{ validationErrors.userAgent }}</div>
            </div>

            <div class="col-12 mb-3">
              <label class="form-label text-secondary fs-14">Max Worker ({{ config.max_worker }}) <span class="text-danger">*</span></label>
              <div class="d-flex align-items-center gap-3">
                <span class="text-muted">5</span>
                <input
                  type="range"
                  class="form-range flex-grow-1"
                  min="5"
                  max="30"
                  step="1"
                  v-model.number="config.max_worker"
                  :disabled="!authStore.hasPermission('config_edit')"
                />
                <span class="text-muted">30</span>
              </div>
            </div>

            <div class="col-12 mb-3">
              <label class="form-label text-secondary fs-14">Scan Frequency (seconds) <span class="text-danger">*</span></label>
              <input
                type="text"
                class="form-control h-55"
                v-model="scanFrequencyInput"
                @input="filterScanFrequency"
                @blur="validateScanFrequency"
                :class="{ 'is-invalid': validationErrors.scanFrequency }"
                placeholder="120-1000000"
                :disabled="!authStore.hasPermission('config_edit')"
              />
              <div class="text-danger small mt-1" v-if="validationErrors.scanFrequency">{{ validationErrors.scanFrequency }}</div>
            </div>

            <div class="col-12 mb-3" v-if="useProxy">
              <div class="form-check">
                <input 
                  type="checkbox" 
                  class="form-check-input" 
                  id="use_host_on_proxy_fail" 
                  v-model="config.use_host_on_proxy_fail"
                  @change="toggleHostOnProxyFail"
                  :disabled="toggling.host  || !authStore.hasPermission('config_toggle')"
                />
                <label class="form-check-label" for="use_host_on_proxy_fail">
                  Use host on proxy failure
                  <span v-if="toggling.host" class="spinner-border spinner-border-sm ms-2" role="status"></span>
                </label>
              </div>
            </div>

            <div class="col-12 mb-3">
              <div class="form-check">
                <input 
                  type="checkbox" 
                  class="form-check-input" 
                  id="receive_alert" 
                  v-model="config.receive_alert"
                  @change="toggleReceiveAlert"
                  :disabled="toggling.alert || !authStore.hasPermission('config_toggle')"
                />
                <label class="form-check-label" for="receive_alert">
                  Receive alerts
                  <span v-if="toggling.alert" class="spinner-border spinner-border-sm ms-2" role="status"></span>
                </label>
              </div>
            </div>

            <div class="col-12">
              <p class="text-muted small"><span class="text-danger">*</span> Required fields</p>
            </div>

            <div class="col-12 mt-4">
              <div class="d-flex flex-wrap gap-3 align-items-center">
                <button
                  class="btn btn-primary text-white fw-semibold py-2 px-4"
                  type="submit"
                  :disabled="!isFormValid || saving  || !authStore.hasPermission('config_edit')"
                >
                  <span v-if="saving" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                  {{ saving ? 'Saving...' : 'Update' }}
                </button>
                <button
                  class="btn btn-outline-secondary fw-semibold py-2 px-4"
                  type="button"
                  @click="resetForm"
                  :disabled="saving"
                >
                  Cancel
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
  
  <Toast 
    :show="configStore.toast.show" 
    :message="configStore.toast.message" 
    :type="configStore.toast.type" 
    :autoClose="true"
    :duration="configStore.toast.duration"
    @close="handleToastClose" 
  />
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import PageTitle from "@/components/Common/PageTitle.vue";
import Toast from "@/components/Common/Toast.vue";
import { useConfigStore } from '@/stores/config.store';
import { useAuthStore } from '@/stores/auth.store';

const authStore = useAuthStore();

const configStore = useConfigStore();

const proxyInput = ref('');
const dnsServerInput = ref('');
const scanFrequencyInput = ref('');
const useProxy = ref(false);

const config = computed(() => configStore.getConfig);
const loading = computed(() => configStore.isLoading);
const saving = computed(() => configStore.isSaving);
const toggling = computed(() => configStore.isToggling);
const error = computed(() => configStore.error);
const validationErrors = computed(() => configStore.validationErrors);
const isFormValid = computed(() => configStore.isFormValid);

const selectedProxies = computed(() => config.value?.proxy || []);
const selectedDnsServers = computed(() => config.value?.dns_server || []);

const filterDnsInput = () => {
  dnsServerInput.value = dnsServerInput.value.replace(/[^0-9.]/g, '');
};

const filterScanFrequency = () => {
  scanFrequencyInput.value = scanFrequencyInput.value.replace(/\D/g, '');
  if (config.value) {
    config.value.scan_frequency = parseInt(scanFrequencyInput.value, 10) || 0;
  }
  validateScanFrequency();
};

const toggleProxyUsage = async () => {
  if (toggling.value.proxy) {
    useProxy.value = config.value?.use_proxy || false;
    return;
  }

  if (!authStore.hasPermission('config_toggle')){
    configStore.showToast('Permission denied to perform this action', 'warning');
    return;
  }
  
  try {
    const response = await configStore.toggleProxy();
    
    useProxy.value = response.use_proxy;
    
  } catch (error) {
    useProxy.value = config.value?.use_proxy || false;
  }
};

const toggleHostOnProxyFail = async () => {
  if (!authStore.hasPermission('config_toggle')){
    configStore.showToast('Permission denied to perform this action', 'warning');
    return;
  }
  if (toggling.value.host || !config.value) return;

  
  
  const prevState = config.value.use_host_on_proxy_fail;
  
  try {
    await configStore.toggleHost();
  } catch (error) {
    if (config.value) config.value.use_host_on_proxy_fail = prevState;
  }
};

const toggleReceiveAlert = async () => {
  if (!authStore.hasPermission('config_toggle')){
    configStore.showToast('Permission denied to perform this action', 'warning');
    return;
  }
  if (toggling.value.alert || !config.value) return;

  
  const prevState = config.value.receive_alert;
  
  try {
    await configStore.toggleAlert();
  } catch (error) {
    if (config.value) config.value.receive_alert = prevState;
  }
};

const addProxy = () => {
  if (!authStore.hasPermission('config_edit')){
    configStore.showToast('Permission denied to perform this action', 'warning');
    return;
  }
  if (!proxyInput.value.trim() || !config.value) return;
  
  if (validateProxyInput()) {
    if (!config.value.proxy) {
      config.value.proxy = [];
    }
    
    if (!config.value.proxy.includes(proxyInput.value.trim())) {
      config.value.proxy.push(proxyInput.value.trim());
      configStore.validateProxies(config.value.proxy);
    }
    
    proxyInput.value = '';
  }
};

const removeProxy = (proxy: string) => {
  if (!authStore.hasPermission('config_edit')){
    configStore.showToast('Permission denied to perform this action', 'warning');
    return;
  }
  if (!config.value || !config.value.proxy) return;
  
  config.value.proxy = config.value.proxy.filter(p => p !== proxy);
  configStore.validateProxies(config.value.proxy);
};

const validateProxyInput = (): boolean => {
  const basicProxyPattern = /^(https?:\/\/)?([a-zA-Z0-9.-]+|\d{1,3}(?:\.\d{1,3}){3}):\d{1,5}$/;

  const authProxyPattern = /^(https?:\/\/)?([a-zA-Z0-9.-]+|\d{1,3}(?:\.\d{1,3}){3})(:\d{1,5})?$/; 
  
  if (proxyInput.value && !basicProxyPattern.test(proxyInput.value) && !authProxyPattern.test(proxyInput.value)) {
    configStore.validationErrors.proxy = 'Proxy format invalid. Use ip:port or domain:port with optional username and password';
    return false;
  }
  
  return true;
};

const addDnsServer = () => {
  if (!authStore.hasPermission('config_edit')){
    configStore.showToast('Permission denied to perform this action', 'warning');
    return;
  }
  if (!dnsServerInput.value.trim() || !config.value) return;
  
  if (validateDnsInput()) {
    if (!config.value.dns_server) {
      config.value.dns_server = [];
    }
    
    if (!config.value.dns_server.includes(dnsServerInput.value.trim())) {
      config.value.dns_server.push(dnsServerInput.value.trim());
      configStore.validateDns(config.value.dns_server);
    }
    
    dnsServerInput.value = '';
  }
};

const removeDnsServer = (dns: string) => {
  if (!authStore.hasPermission('config_edit')){
    configStore.showToast('Permission denied to perform this action', 'warning');
    return;
  }
  if (!config.value || !config.value.dns_server) return;
  
  config.value.dns_server = config.value.dns_server.filter(d => d !== dns);
  configStore.validateDns(config.value.dns_server);
};

const validateDnsInput = (): boolean => {
  const ipPattern = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
  
  if (dnsServerInput.value && !ipPattern.test(dnsServerInput.value)) {
    configStore.validationErrors.dns = 'Invalid DNS server format. Use IP addresses only (e.g 8.8.8.8),';
    return false;
  }
  
  configStore.validationErrors.dns = '';
  return true;
};

const validateEmail = () => {
  if (!config.value) return;
  configStore.validateEmail(config.value.email);
};

const validateUserAgent = () => {
  if (!config.value) return;
  configStore.validateUserAgent(config.value.user_agent);
};

const validateScanFrequency = () => {
  if (!config.value) return;
  configStore.validateScanFrequency(config.value.scan_frequency);
};

const initializeScanFrequency = () => {
  if (config.value) {
    scanFrequencyInput.value = config.value.scan_frequency.toString();
  }
};

const saveConfig = async () => {
  if (!authStore.hasPermission('config_edit')){
    configStore.showToast('Permission denied to perform this action', 'warning');
    return;
  }
  if (!config.value) return;
  
  validateEmail();
  validateUserAgent();
  validateScanFrequency();
  
  if (useProxy.value && config.value.proxy) {
    configStore.validateProxies(config.value.proxy);
  }
  
  if (config.value.dns_server) {
    configStore.validateDns(config.value.dns_server);
  }
  
  await configStore.updateConfig(config.value);
};

const resetForm = async () => {
  await configStore.resetForm();
  
  proxyInput.value = '';
  dnsServerInput.value = '';
  
  if (config.value) {
    useProxy.value = config.value.use_proxy;
    initializeScanFrequency();
  }
};

const handleToastClose = () => {
  configStore.toast.show = false;
};

onMounted(async () => {
  try {
    await configStore.fetchConfig();
    
    if (config.value) {
      useProxy.value = config.value.use_proxy;
      initializeScanFrequency();
    }
  } catch (error) {
    configStore.showToast('Failed to load configurations', 'error');
  }
});

watch(() => config.value?.scan_frequency, (newValue) => {
  if (newValue !== undefined) {
    scanFrequencyInput.value = newValue.toString();
  }
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

.text-danger {
  font-size: 0.875rem;
}

.form-label.text-secondary {
  font-weight: 500;
}

.form-check-input {
  cursor: pointer;
}

.btn-primary {
  background-color: #6366f1;
  border-color: #6366f1;
}

.btn-primary:hover {
  background-color: #4f46e5;
  border-color: #4f46e5;
}

.btn-primary:disabled {
  background-color: #a5b4fc;
  border-color: #a5b4fc;
}

.multi-select-container {
  position: relative;
}

.select-with-tags {
  min-height: 55px;
  overflow: hidden;
}

.selected-tag {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  margin-bottom: 2px;
  margin-top: 2px;
}

.tag-remove {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0 0 0 0.3rem;
  font-size: 1.1rem;
  line-height: 1;
  opacity: 0.7;
}

.tag-remove:hover {
  opacity: 1;
}

.form-range::-webkit-slider-thumb {
  background: #6366f1;
}

.form-range::-moz-range-thumb {
  background: #6366f1;
}

.form-range::-ms-thumb {
  background: #6366f1;
}
</style>