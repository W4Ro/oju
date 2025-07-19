<template>
  <div class="main-content-container overflow-hidden">
    <h2 class="fs-5 fw-semibold mb-6">Details of the defacement</h2>
    
    <div class="card bg-white border-0 rounded-3 mb-4">
      <div class="card-body p-4">
        <div v-if="isLoading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else-if="!defacementDetails" class="text-center py-5">
          <div class="alert alert-warning" role="alert">
            Unable to load defacement details.
          </div>
          <button class="btn btn-primary mt-3" @click="goBack">Back to list</button>
        </div>

        <div v-else>
          <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 showing-wrap border-bottom pb-3 mb-4">
            <h3 class="fs-16 fw-semibold mb-0">Defacement Information</h3>
            <div class="d-flex gap-2">
              <button
                class="btn btn-outline-secondary py-1 px-2 px-sm-4 fs-14 fw-medium rounded-3"
                @click="goBack"
              >
                <span class="py-sm-1 d-block">
                  <i class="ri-arrow-left-line me-1"></i>
                  <span>Back</span>
                </span>
              </button>
            </div>
          </div>

          <div class="row g-3 mb-4">
            <div class="col-md-6">
              <div class="p-3 border rounded-3 h-100">
                <div class="mb-2">
                  <span class="text-secondary fs-14">UUID :</span>
                  <span class="ms-2 small text-muted">{{ defacementDetails.id }}</span>
                </div>
                <div class="mb-2">
                  <span class="text-secondary fs-14">Scan date:</span>
                  <span class="ms-2">{{ formatDate(defacementDetails.date) }}</span>
                </div>
              </div>
            </div>
            <div class="col-md-6">
              <div class="p-3 border rounded-3 h-100">
                <div class="mb-2">
                  <span class="text-secondary fs-14">URL :</span>
                  <a :href="defacementDetails.platform_url" target="_blank" class="ms-2 text-break">
                    {{ defacementDetails.platform_url }}
                  </a>
                </div>
                <div class="mb-2">
                  <span class="text-secondary fs-14">Entity :</span>
                  <span class="ms-2">{{ defacementDetails.entity_name }}</span>
                </div>
                <div class="mb-2">
                  <span class="text-secondary fs-14">Status :</span>
                  <span
                    class="badge bg-opacity-10 p-2 fs-12 fw-normal ms-2"
                    :class="defacementDetails.is_defaced ? 'bg-danger text-danger' : 'bg-success text-success'"
                  >
                    {{ defacementDetails.is_defaced ? "Defaced" : "Safe" }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 showing-wrap border-bottom pb-3 mb-4">
            <h3 class="fs-16 fw-semibold mb-0">Comparison of structures</h3>
            <div v-if="defacementDetails.is_defaced && defacementStore.canManageDefacements">
              <button class="btn btn-danger py-1 px-2 px-sm-4 fs-14 fw-medium rounded-3" @click="openResetModal(defacementDetails)">
                <span class="py-sm-1 d-block">
                  <i class="ri-refresh-line me-1"></i>
                  <span>Reset to normal state</span>
                </span>
              </button>
            </div>
          </div>

          <div class="row g-3">
            <div class="col-md-6">
              <div class="border rounded-3 h-100">
                <div class="d-flex justify-content-between p-3 border-bottom">
                  <h4 class="fs-14 fw-semibold mb-0">Normal structure</h4>
                  <span class="badge bg-success text-white">Reference</span>
                </div>
                <div class="tree-container p-3">
                  <pre class="bg-light p-3 rounded-3 overflow-auto" style="max-height: 500px;">{{ prettyPrintJson(defacementDetails.normal_state_tree) }}</pre>
                </div>
              </div>
            </div>
            <div class="col-md-6">
              <div class="border rounded-3 h-100">
                <div class="d-flex justify-content-between p-3 border-bottom">
                  <h4 class="fs-14 fw-semibold mb-0">Current structure</h4>
                  <span 
                    class="badge text-white"
                    :class="defacementDetails.is_defaced ? 'bg-danger' : 'bg-success'"
                  >
                    {{ defacementDetails.is_defaced ? "Modified" : "Same" }}
                  </span>
                </div>
                <div class="tree-container p-3">
                  <pre 
                    class="p-3 rounded-3 overflow-auto" 
                    :class="defacementDetails.is_defaced ? 'bg-danger bg-opacity-10' : 'bg-light'"
                    style="max-height: 500px;"
                  >{{ prettyPrintJson(defacementDetails.last_state_tree) }}</pre>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>


  <Toast 
    :show="defacementStore.toast.show" 
    :message="defacementStore.toast.message" 
    :type="defacementStore.toast.type" 
    :autoClose="true"
    :duration="defacementStore.toast.duration"
    @close="handleToastClose" 
  />

  <ResetDefacementConfirmation
  :show="showResetModal"
  :platformUrl="defacementToReset?.platform_url"
  :isResetting="isLoading"
  @confirm="confirmReset"
  @cancel="showResetModal = false"
/>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { format, parseISO } from 'date-fns';
import Toast from "@/components/Common/Toast.vue";
import { useDefacementStore } from "@/stores/defacement.store";
import type { DefacementDetail } from "@/types/defacement.types";
import ResetDefacementConfirmation from "@/components/Defacement/ResetDefacementConfirmation.vue";

const showResetModal = ref(false);
const defacementToReset = ref<DefacementDetail | null>(null);

const route = useRoute();
const router = useRouter();
const defacementStore = useDefacementStore();

const defacementId = ref(route.params.id as string);
const defacementDetails = ref<DefacementDetail | null>(null);
const isLoading = ref(true);
const isRefreshing = ref(false);

const formatDate = (dateString: string) => {
  try {
    const options: Intl.DateTimeFormatOptions = { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString('fr-FR', options);
  } catch (e) {
    return dateString;
  }
};

const prettyPrintJson = (jsonString: string) => {
  try {
    const jsonObject = typeof jsonString === 'object' 
      ? jsonString
      : JSON.parse(jsonString);
    return JSON.stringify(jsonObject, null, 2);
  } catch (e) {
    return jsonString;
  }
};

const fetchDefacementDetails = async () => {
  isLoading.value = true;
  
  try {
    const details = await defacementStore.getDefacement(defacementId.value);
    defacementDetails.value = details;
  } catch (error) {
    defacementStore.showToast('Error fetching defacement details:', 'error');
  } finally {
    isLoading.value = false;
  }
};

const refreshDefacement = async () => {
  
  if (!defacementDetails.value) return;
  if (!defacementDetails.value.is_defaced) {
    defacementStore.showToast('This plateform is not defaced', 'error');
    return;
  }
  try {
    isRefreshing.value = true;
    
    const result = await defacementStore.resetDefacementState(defacementDetails.value.id);
    
    if (result) {
      await fetchDefacementDetails();
    }
    
  } catch (error) {
    console.error('error', error);
  } finally {
    isRefreshing.value = false;
  }
};

function openResetModal(item: DefacementDetail) {
  defacementToReset.value = item;
  showResetModal.value = true;
}

async function confirmReset() {
  if (!defacementToReset.value) return;
  showResetModal.value = false;
  await refreshDefacement();
  defacementToReset.value = null;
}


function handleToastClose() {
  defacementStore.toast.show = false;
}

const goBack = () => {
  router.push('/defacements/list');
};

onMounted(() => {
  fetchDefacementDetails();
});
</script>

<style scoped>
.tree-node.node-diff > .node-content {
  background-color: #fff4f4;
  border-left: 3px solid #ff5c5c;
}

.tree-node.node-diff > .node-content:hover {
  background-color: #ffeaea;
  box-shadow: 0 2px 4px rgba(255, 0, 0, 0.2);
}

.tree-container {
  max-height: 500px;
  background-color: #ffffff;
  padding: 15px;
}

.badge {
  font-weight: 500;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

pre {
  font-family: 'Fira Code', Consolas, Monaco, 'Andale Mono', monospace;
  font-size: 0.9rem;
  white-space: pre;             
  overflow-x: auto;         
}

</style>