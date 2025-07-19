<template>
  <div class="main-content-container overflow-hidden">
    <PageTitle pageTitle="Scans"/>
  </div>
  <div class="main-content-container overflow-hidden">
    
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Scan loading...</p>
    </div>
    
    <div class="row">
      <div :class="selectedScan ? 'col-lg-8' : 'col'">
        <div class="row">
          <div class="col-lg-6 col-md-6 mb-4" v-for="scan in scans" :key="scan.code">
            <div class="card bg-white border-0 rounded-3 p-4 py-lg-5 h-100">
              <div class="d-flex justify-content-between align-items-start mb-3">
                <div class="mb-3">
                  <img src="@/assets/images/user-77.gif" class="rounded-circle" style="width: 54px; height: 54px" alt="scan icon" />
                </div>
                <div class="form-check form-switch">
                  <input class="form-check-input" type="checkbox" v-model="scan.is_active" 
                         @change="updateScanStatus(scan)" 
                         :id="`scan-active-${scan.code}`"
                         :disabled="operationInProgress || !authStore.hasPermission('cerb_scans_toggle')">
                  <label class="form-check-label" :for="`scan-active-${scan.code}`">
                    {{ scan.is_active ? 'Active' : 'Inactive' }}
                  </label>
                </div>
              </div>
              
              <h3 class="mb-3">{{ scan.name }}</h3>
              <p class="mb-3">{{ scan.description }}</p>
              <p class="text-muted small">Updated at: {{ formatDate(scan.updated_at) }}</p>
              
              <div class="mt-auto pt-3">
                <button class="btn btn-primary py-2 px-4" 
                        @click="selectScan(scan)"
                        :disabled="operationInProgress">
                  Configure 
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="selectedScan" class="col-lg-4">
        <div class="card bg-white border-0 rounded-3 mb-4 position-sticky" style="top: 20px;">
          <div class="card-header bg-white d-flex justify-content-between align-items-center border-bottom">
            <h5 class="m-0">Configuration of {{ selectedScan.name }}</h5>
            <button type="button" class="btn-close" @click="closePanel" :disabled="criteriaLoading"></button>
          </div>
          
          <div v-if="criteriaLoading" class="card-body p-4 text-center">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2">Loading criteria...</p>
          </div>
          
          <div v-else-if="configError" class="card-body p-4">
            <div class="alert alert-danger" role="alert">
              <i class="bi bi-exclamation-triangle-fill me-2"></i>
              Error loading configuration.
              <button class="btn btn-sm btn-outline-danger ms-2" @click="reloadScanCriteria">Try again</button>
            </div>
          </div>
          
          <div v-else class="card-body p-4">
            <div v-if="selectedScan.code === 'defacement' && defacementCriteria">
              <div class="mb-4">
                <label for="acceptance-rate" class="form-label">Acceptance rate (0-5000)</label>
                <div class="d-flex align-items-center gap-2">
                  <input type="range" class="form-range" min="0" max="5000" step="10" 
                         id="acceptance-rate" 
                         v-model.number="defacementCriteria.acceptance_rate"
                         :disabled="!authStore.hasPermission('cerb_scans_manage')">
                  <span class="badge bg-primary">{{ defacementCriteria.acceptance_rate }}</span>
                </div>
              </div>
              
              <div class="mb-4">
                <label class="form-label">Authorized domains</label>
                <div class="multi-select-container mb-2">
                  <div class="form-control h-auto p-1 d-flex flex-wrap gap-1 select-with-tags">
                    <div v-for="(domain, index) in defacementCriteria.whitelisted_domains" :key="index" class="selected-tag" style="background-color: #e3f2fd; color: #0d6efd;">
                      {{ domain.domain }}
                      <button type="button" class="tag-remove" @click="removeDomain(index)">×</button>
                    </div>
                    <div class="flex-grow-1">
                      <input
                        type="text"
                        class="form-control border-0 bg-transparent p-1"
                        placeholder="Add domain..."
                        v-model="newDomain"
                        @keydown.enter.prevent="addDomain"
                        :disabled="!authStore.hasPermission('cerb_scans_manage')"
                      />
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="d-flex justify-content-end mt-4">
                <button class="btn btn-secondary me-2" @click="closePanel" :disabled="actionLoading">Close</button>
                <button class="btn btn-primary" @click="updateDefacementCriteria" :disabled="actionLoading || !authStore.hasPermission('cerb_scans_manage')">
                  <span v-if="actionLoading" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                  {{ actionLoading ? 'Saving...' : 'save' }}
                </button>
              </div>
            </div>
            
            <div v-if="selectedScan.code === 'ssl' && sslCriteria">
              <div class="mb-3">
                <div class="form-check">
                  <input class="form-check-input" type="checkbox" 
                         v-model="sslCriteria.check_ssl_error" 
                         id="check-ssl-error"
                         @change="toggleSSLErrorCheck"
                         :disabled="actionLoading || !authStore.hasPermission('cerb_scans_manage')">
                  <label class="form-check-label" for="check-ssl-error">
                    Check for SSL errors
                  </label>
                </div>
                <div v-if="checkErrorLoading" class="text-primary small mt-1">
                  <div class="spinner-border spinner-border-sm me-1" role="status"></div>
                  Update in progress...
                </div>
              </div>
              
              <div class="mb-3">
                <div class="form-check">
                  <input class="form-check-input" type="checkbox" 
                         v-model="sslCriteria.check_ssl_expiry" 
                         id="check-ssl-expiry"
                         @change="toggleSSLExpiryCheck"
                         :disabled="actionLoading || !authStore.hasPermission('cerb_scans_manage')">
                  <label class="form-check-label" for="check-ssl-expiry">
                    Check SSL certificate expiration
                  </label>
                </div>
                <div v-if="checkExpiryLoading" class="text-primary small mt-1">
                  <div class="spinner-border spinner-border-sm me-1" role="status"></div>
                  Update in progress...
                </div>
              </div>
            </div>
            
            <div v-if="selectedScan.code === 'website' && websiteCriteria">
              <div class="mb-4">
                <label for="max-response-time" class="form-label">Maximum response time (ms): {{ websiteCriteria.max_response_time_ms }}ms</label>
                <input type="range" class="form-range" min="1000" max="60000" step="100" 
                       id="max-response-time" 
                       v-model.number="websiteCriteria.max_response_time_ms"
                       :disabled="!authStore.hasPermission('cerb_scans_manage')">
              </div>
              
              <div class="d-flex justify-content-end mt-4">
                <button class="btn btn-secondary me-2" @click="closePanel" :disabled="actionLoading">Close</button>
                <button class="btn btn-primary" @click="updateMaxResponseTime" :disabled="actionLoading">
                  <span v-if="actionLoading" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                  {{ actionLoading ? 'Saving...' : 'save' }}
                </button>
              </div>
            </div>
            
            <div v-if="selectedScan.code === 'domain' && domainCriteria">
              <div class="mb-3">
                <div class="form-check">
                  <input class="form-check-input" type="checkbox" 
                         v-model="domainCriteria.check_whois" 
                         id="check-whois"
                         @change="toggleWhoisCheck"
                         :disabled="actionLoading || !authStore.hasPermission('cerb_scans_manage')">
                  <label class="form-check-label" for="check-whois">
                    Check WHOIS information
                  </label>
                </div>
                <div v-if="checkWhoisLoading" class="text-primary small mt-1">
                  <div class="spinner-border spinner-border-sm me-1" role="status"></div>
                  Update in progress...
                </div>
              </div>
              
              <div class="mb-3">
                <div class="form-check">
                  <input class="form-check-input" type="checkbox" 
                         v-model="domainCriteria.check_dns_servers" 
                         id="check-dns-servers"
                         @change="toggleDNSServersCheck"
                         :disabled="actionLoading || !authStore.hasPermission('cerb_scans_manage')">
                  <label class="form-check-label" for="check-dns-servers">
                    Check DNS servers
                  </label>
                </div>
                <div v-if="checkDNSLoading" class="text-primary small mt-1">
                  <div class="spinner-border spinner-border-sm me-1" role="status"></div>
                  Update in progress...
                </div>
              </div>
              
              <div class="mb-3">
                <div class="form-check">
                  <input class="form-check-input" type="checkbox" 
                         v-model="domainCriteria.check_domain_expiry_error" 
                         id="check-domain-expiry"
                         @change="toggleDomainExpiryCheck"
                         :disabled="actionLoading || !authStore.hasPermission('cerb_scans_manage')">
                  <label class="form-check-label" for="check-domain-expiry">
                    Check domain expiration
                  </label>
                </div>
                <div v-if="checkDomainExpiryLoading" class="text-primary small mt-1">
                  <div class="spinner-border spinner-border-sm me-1" role="status"></div>
                  Update in progress...
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <Toast 
    :show="scanStore.toast.show" 
    :message="scanStore.toast.message" 
    :type="scanStore.toast.type" 
    :autoClose="true"
    :duration="scanStore.toast.duration"
    @close="handleToastClose" 
  />
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import PageTitle from "@/components/Common/PageTitle.vue";
import Toast from "@/components/Common/Toast.vue";
import { Scan } from '@/types/scan.types';
import { useScanStore } from '@/stores/scan.store';
import { useAuthStore } from '@/stores/auth.store';
const authStore = useAuthStore();

const scanStore = useScanStore();

const newDomain = ref('');

const loading = computed(() => scanStore.loading);
const criteriaLoading = computed(() => scanStore.criteriaLoading);
const error = computed(() => scanStore.error);
const configError = computed(() => scanStore.configError);
const scans = computed(() => scanStore.scans);
const selectedScan = computed(() => scanStore.selectedScan);

const defacementCriteria = computed(() => scanStore.getDefacementCriteria);
const sslCriteria = computed(() => scanStore.getSSLCriteria);
const websiteCriteria = computed(() => scanStore.getWebsiteCriteria);
const domainCriteria = computed(() => scanStore.getDomainCriteria);

const actionLoading = ref(false);
const checkErrorLoading = ref(false);
const checkExpiryLoading = ref(false);
const checkWhoisLoading = ref(false);
const checkDNSLoading = ref(false);
const checkDomainExpiryLoading = ref(false);

const operationInProgress = computed(() => {
  return loading.value || criteriaLoading.value || actionLoading.value;
});

const formatDate = (dateString: string): string => {
  if (!dateString) return 'N/A';
  
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
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
    console.error("Date formatting error:", error);
    return 'Date invalide';
  }
};

const selectScan = async (scan: Scan) => {
  if (operationInProgress.value) return;
  
  try {
    await scanStore.selectScan(scan);
    newDomain.value = ''; 
  } catch (error) {
    console.error('Error while selecting scan:', error);
  }
};

const closePanel = () => {
  if (criteriaLoading.value || actionLoading.value) return;
  
  scanStore.clearSelectedScan();
  newDomain.value = '';
};

const reloadScanCriteria = async () => {
  if (!selectedScan.value) return;
  
  try {
    await scanStore.fetchScanCriteria(selectedScan.value.code);
  } catch (error) {
    console.error('Error reloading criteria:', error);
  }
};

const updateScanStatus = async (scan: Scan) => {
  if (operationInProgress.value) {
    if(!authStore.hasPermission('cerb_scans_toggle')) {
    scanStore.showToast('Permission denied to toggle scan', 'warning');
    return ;
  }
    scan.is_active = !scan.is_active;
    return;
  }
  
  try {
    await scanStore.toggleScanStatus(scan);
  } catch (error) {
    console.error('Error updating scan status:', error);
  }
};

const updateDefacementCriteria = async () => {
  if(!authStore.hasPermission('cerb_scans_manage')) {
    scanStore.showToast('Permission denied to update defacement criteria', 'warning');
    return ;
  }
  if (!defacementCriteria.value || actionLoading.value) return;
  
  actionLoading.value = true;
  
  try {
    await scanStore.updateDefacementCriteria();
    closePanel();
  } catch (error) {
    console.error('Error updating defacement criteria:', error);
  } finally {
    actionLoading.value = false;
  }
};

const addDomain = () => {
  if (!newDomain.value.trim()) return;
  if(!authStore.hasPermission('cerb_scans_manage')) return ;
  
  const domainRegex = /^([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$/;
  if (!domainRegex.test(newDomain.value.trim())) {
    scanStore.showToast('Invalid domain format', 'error');
    return;
  }
  
  scanStore.addWhitelistedDomain(newDomain.value.trim());
  newDomain.value = '';
};

const removeDomain = (index: number) => {
  if(!authStore.hasPermission('cerb_scans_manage')) return ;
  scanStore.removeWhitelistedDomain(index);
  
};

const toggleSSLErrorCheck = async () => {
  if (!sslCriteria.value || actionLoading.value || checkErrorLoading.value) return;
  if(!authStore.hasPermission('cerb_scans_manage')) {
    scanStore.showToast('Permission denied to toggle criteria', 'warning');
    return ;
  }
  checkErrorLoading.value = true;
  
  try {
    await scanStore.toggleSSLError(sslCriteria.value.check_ssl_error);
  } catch (error) {
    console.error('Error updating SSL error checking:', error);
    sslCriteria.value.check_ssl_error = !sslCriteria.value.check_ssl_error;
  } finally {
    checkErrorLoading.value = false;
  }
};

const toggleSSLExpiryCheck = async () => {
  if(!authStore.hasPermission('cerb_scans_manage')) {
    scanStore.showToast('Permission denied to toggle criteria', 'warning');
    return ;
  }
  if (!sslCriteria.value || actionLoading.value || checkExpiryLoading.value) return;
  
  checkExpiryLoading.value = true;
  
  try {
    await scanStore.toggleSSLExpiry(sslCriteria.value.check_ssl_expiry);
  } catch (error) {
    console.error('Error updating SSL expiration check:', error);
    sslCriteria.value.check_ssl_expiry = !sslCriteria.value.check_ssl_expiry;
  } finally {
    checkExpiryLoading.value = false;
  }
};

const updateMaxResponseTime = async () => {
  if(!authStore.hasPermission('cerb_scans_manage')) {
    scanStore.showToast('Permission denied to perform this action', 'warning');
    return ;
  }
  if (!websiteCriteria.value || actionLoading.value) return;
  
  actionLoading.value = true;
  
  try {
    await scanStore.updateMaxResponseTime(websiteCriteria.value.max_response_time_ms);
    closePanel();
  } catch (error) {
    console.error('Error updating maximum response time:', error);
  } finally {
    actionLoading.value = false;
  }
};

const toggleWhoisCheck = async () => {
  if(!authStore.hasPermission('cerb_scans_manage')) {
    scanStore.showToast('Permission denied to toggle criteria', 'warning');
    return ;
  }
  if (!domainCriteria.value || actionLoading.value || checkWhoisLoading.value) return;
  
  checkWhoisLoading.value = true;
  
  try {
    await scanStore.toggleWhoisCheck(domainCriteria.value.check_whois);
  } catch (error) {
    console.error('Error updating WHOIS verification:', error);
    domainCriteria.value.check_whois = !domainCriteria.value.check_whois;
  } finally {
    checkWhoisLoading.value = false;
  }
};

const toggleDNSServersCheck = async () => {
  if(!authStore.hasPermission('cerb_scans_manage')) {
    scanStore.showToast('Permission denied to toggle criteria', 'warning');
    return ;
  }
  if (!domainCriteria.value || actionLoading.value || checkDNSLoading.value) return;
  
  checkDNSLoading.value = true;
  
  try {
    await scanStore.toggleDNSServersCheck(domainCriteria.value.check_dns_servers);
  } catch (error) {
    console.error('Error updating DNS server verification:', error);
    domainCriteria.value.check_dns_servers = !domainCriteria.value.check_dns_servers;
  } finally {
    checkDNSLoading.value = false;
  }
};

const toggleDomainExpiryCheck = async () => {
  if(!authStore.hasPermission('cerb_scans_manage')) {
    scanStore.showToast('Permission denied to toggle criteria', 'warning');
    return ;
  }
  if (!domainCriteria.value || actionLoading.value || checkDomainExpiryLoading.value) return;
  
  checkDomainExpiryLoading.value = true;
  
  try {
    await scanStore.toggleDomainExpiryCheck(domainCriteria.value.check_domain_expiry_error);
  } catch (error) {
    console.error('Error updating domain expiration check:', error);
    domainCriteria.value.check_domain_expiry_error = !domainCriteria.value.check_domain_expiry_error;
  } finally {
    checkDomainExpiryLoading.value = false;
  }
};

const fetchScans = async () => {
  try {
    await scanStore.fetchScans();
  } catch (error) {
    console.error('Error loading scans:', error);
  }
};

const handleToastClose = () => {
  scanStore.toast.show = false;
};

onMounted(() => {
  fetchScans();
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

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>