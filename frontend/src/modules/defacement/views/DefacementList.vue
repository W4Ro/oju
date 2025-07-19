<template>
  <div class="main-content-container overflow-hidden">
    <PageTitle pageTitle="Defacements" />
  </div>
  <div class="main-content-container overflow-hidden">
    <div class="card bg-white border-0 rounded-3 mb-4">
      <div class="card-body p-0">
        <div class="filter-section p-4">
          <div class="row mb-3">
            <div class="col-md-4">
              <div class="position-relative table-src-form">
                <input type="text" class="form-control" placeholder="Search" v-model="filters.searchTerm" />
                <i class="material-symbols-outlined position-absolute top-50 start-0 translate-middle-y">
                  search
                </i>
              </div>
            </div>
            
            <div class="col-md-8 d-flex justify-content-end">
              <div class="d-flex gap-2">
                <button v-if="showAdvancedFilters" type="button" class="btn btn-primary" @click="applyFilters">Filtrer</button>
                <button v-if="showAdvancedFilters" type="button" class="btn btn-outline-secondary" @click="resetFilters">Reset</button>
                <button type="button" class="btn btn-outline-primary" @click="showAdvancedFilters = !showAdvancedFilters">
                  {{ showAdvancedFilters ? 'Hide advanced filters' : 'Display advanced filters' }}
                </button>
              </div>
            </div>
          </div>
          
          <div v-if="showAdvancedFilters" class="advanced-filters mb-3">
            <div class="row g-3">
              <div class="col-md-3">
                <label class="form-label">State</label>
                <select class="form-select" v-model="filters.is_defaced">
                  <option :value="undefined">All states</option>
                  <option :value="true">Defaced</option>
                  <option :value="false">Safe</option>
                </select>
              </div>

              <div class="col-md-3">
                <label class="form-label">Entity</label>
                <input type="text" class="form-control" placeholder="Entity" v-model="filters.entity_name" />
              </div>

              <div class="col-md-3">
                <label class="form-label">Plateform</label>
                <input type="text" class="form-control" placeholder="Plateform" v-model="filters.platform_url" />
              </div>

              <div class="col-md-3">
                <label class="form-label">Sorting</label>
                <select class="form-select" v-model="filters.ordering">
                  <option value="date">Sort by date</option>
                  <option value="entity_name">Sort by entity</option>
                  <option value="platform_url">Sort by plateform</option>
                  <option value="is_defaced">Sort by status</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <div class="default-table-area style-two default-table-width">
          <div v-if="isLoading" class="d-flex justify-content-center my-5">
            <div class="spinner-border" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>

          <div v-else-if="error" class="alert alert-danger m-4">
            {{ error }}
          </div>

          <div v-else-if="paginatedItems.length === 0" class="alert alert-info m-4">
            No defacement found.
          </div>

          <div v-else class="table-responsive">
            <table class="table align-middle">
              <thead>
                <tr>
                  <th scope="col" style="width: 5%">ID</th>
                  <th scope="col" style="width: 20%">URL</th>
                  <th scope="col" style="width: 25%">Entity Name</th>
                  <th scope="col" style="width: 15%">Last scan date</th>
                  <th scope="col" style="width: 15%">Status</th>
                  <th scope="col" style="width: 10%">Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in paginatedItems" :key="item.id">
                  <td class="text-body">
                    {{ item.displayId || '' }}
                  </td>
                  <td>
                    <div class="content-truncate" style="max-width: 200px;">
                      <a :href="item.platform_url" class="text-body" target="_blank">
                        {{ item.platform_url }}
                      </a>
                      <div class="tooltip-content">{{ item.platform_url }}</div>
                    </div>
                  </td>
                  <td>
                    <div class="content-truncate" style="max-width: 250px;">
                      {{ item.entity_name }}
                      <div class="tooltip-content">{{ item.entity_name }}</div>
                    </div>
                  </td>
                  <td class="text-body">
                    <div class="content-truncate">
                      {{ formatDate(item.date) }}
                      <div class="tooltip-content">{{ formatDate(item.date) }}</div>
                    </div>
                  </td>
                  <td>
                    <span
                      class="badge bg-opacity-10 p-2 fs-12 fw-normal"
                      :class="item.is_defaced ? 'bg-danger text-danger' : 'bg-success text-success'"
                    >
                      {{ item.is_defaced ? "Defaced" : "Safe" }}
                    </span>
                  </td>
                  <td>
                    <div class="d-flex align-items-center gap-1">
                      <button
                        class="ps-0 border-0 bg-transparent lh-1 position-relative top-2"
                        @click="viewDefacementDetails(item)"
                        title="See details"
                      >
                        <i class="material-symbols-outlined fs-16 text-body">visibility</i>
                      </button>
                      <button
                        @click="openResetModal(item)"
                        class="ps-0 border-0 bg-transparent lh-1"
                        title="Réinitialiser l'état normal"
                        v-if="item.is_defaced && defacementStore.canManageDefacements"
                      >
                      <i class="material-symbols-outlined fs-16 text-primary">refresh</i>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="p-4 pt-lg-4">
            <div class="d-flex justify-content-between align-items-center">
              <div v-if="filteredItems.length > 0">
                Display of {{ (currentPage - 1) * perPage + 1 }} à {{ Math.min(currentPage * perPage, filteredItems.length) }} sur {{ totalItems }} results
              </div>
              <Pagination 
                :total="totalItems" 
                :perPage="perPage" 
                v-model="currentPage" 
                @page-change="handlePageChange" 
              />
              <button 
                v-if="defacementStore.hasMoreData && filteredItems.length < totalItems" 
                class="btn btn-outline-primary" 
                @click="loadMoreData"
                :disabled="isLoading"
              >
                <span v-if="isLoading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                Load more data
              </button>
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
import { ref, computed, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import PageTitle from "@/components/Common/PageTitle.vue";
import Pagination from "@/components/Common/Pagination.vue";
import Toast from "@/components/Common/Toast.vue";
import { useDefacementStore } from "@/stores/defacement.store";
import type { Defacement, DefacementFilters } from "@/types/defacement.types";
import ResetDefacementConfirmation from "@/components/Defacement/ResetDefacementConfirmation.vue"

const router = useRouter();
const defacementStore = useDefacementStore();

const showResetModal = ref(false);
const defacementToReset = ref<Defacement | null>(null);

const currentPage = ref(1);
const perPage = ref(10);
const showAdvancedFilters = ref(false);

const filters = ref<DefacementFilters>({
  searchTerm: '',
  is_defaced: undefined,
  entity_name: '',
  platform_url: '',
  ordering: 'date'
});

const isLoading = computed(() => defacementStore.loading);
const error = computed(() => defacementStore.error);
const totalItems = computed(() => sortedItems.value.length);

function resetFilters() {
  filters.value = {
    searchTerm: '',
    is_defaced: undefined,
    entity_name: '',
    platform_url: '',
    ordering: 'date'
  };
  currentPage.value = 1;
}

function applyFilters() {
  currentPage.value = 1;
}

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

const filteredItems = computed(() => {
  return defacementStore.filterDefacements(filters.value);
});

const sortedItems = computed(() => {
  const arr = [...filteredItems.value];
  switch (filters.value.ordering) {
    case 'date':
      arr.sort((a, b) =>
        new Date(a.date).getTime() - new Date(b.date).getTime()
      );
      break;
    case 'entity_name':
      arr.sort((a, b) => a.entity_name.localeCompare(b.entity_name));
      break;
    case 'platform_url':
      arr.sort((a, b) => a.platform_url.localeCompare(b.platform_url));
      break;
    case 'is_defaced':
      arr.sort((a, b) =>
        a.is_defaced === b.is_defaced
          ? 0
          : a.is_defaced
            ? -1
            : 1
      );
      break;
    default:
      break;
  }
  return arr;
});

const paginatedItems = computed(() => {
  const start = (currentPage.value - 1) * perPage.value;
  return sortedItems.value.slice(start, start + perPage.value);
});

async function loadMoreData() {
  try {
    await defacementStore.loadMoreDefacements();
  } catch (error) {
    console.error('Error loading additional data:', error);
  }
}

function handlePageChange(newPage: number) {
  currentPage.value = newPage;
  
  const currentLoaded = defacementStore.defacements.length;
  const neededItems = newPage * perPage.value;
  if (neededItems > currentLoaded && defacementStore.hasMoreData) {
    loadMoreData();
  }
}

function handleToastClose() {
  defacementStore.toast.show = false;
}

const viewDefacementDetails = (item: Defacement) => {
  router.push(`/defacements/details/${item.id}`);
};

function openResetModal(item: Defacement) {
  defacementToReset.value = item;
  showResetModal.value = true;
}

async function confirmReset() {
  if (!defacementToReset.value) return;
  await defacementStore.resetDefacementState(defacementToReset.value.id);
  showResetModal.value = false;
  defacementToReset.value = null;
}

watch([
  () => filters.value.searchTerm,
  () => filters.value.is_defaced,
  () => filters.value.entity_name,
  () => filters.value.platform_url,
  () => filters.value.ordering
], () => {
  applyFilters();
});

onMounted(() => {
  defacementStore.fetchDefacements();
});
</script>

<style scoped>
.content-truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 150px;
  position: relative;
  cursor: pointer;
}

.tooltip-content {
  display: none;
  position: absolute;
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  padding: 8px 12px;
  border-radius: 4px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.15);
  z-index: 1000;
  width: auto;
  min-width: 150px;
  max-width: 300px;
  left: 0;
  top: -5px;
  transform: translateY(-100%);
  white-space: normal;
  word-break: break-word;
}

.content-truncate:hover .tooltip-content {
  display: block;
}

.tooltip-content::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 20px;
  border-width: 5px;
  border-style: solid;
  border-color: #dee2e6 transparent transparent transparent;
}

.advanced-filters {
  background-color: #f8f9fa;
  border-radius: 4px;
  padding: 15px;
  border: 1px solid #e9ecef;
}

.table-src-form {
  min-width: 250px;
}

.table-src-form input {
  padding-left: 40px;
  height: 42px;
}

.table-src-form i {
  left: 15px;
  opacity: 0.5;
}

.badge {
  font-weight: 500;
}

button.bg-transparent {
  transition: transform 0.2s;
}

button.bg-transparent:hover {
  transform: scale(1.2);
}
</style>