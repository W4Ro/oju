<template>
    <div class="main-content-container overflow-hidden">
      <PageTitle pageTitle="Alerts Histories" />
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
                  <button v-if="showAdvancedFilters" type="button" class="btn btn-primary" @click="applyFilters">Filter</button>
                  <button v-if="showAdvancedFilters" type="button" class="btn btn-outline-secondary" @click="resetFilters">Reset</button>
                  <button type="button" class="btn btn-outline-primary" @click="showAdvancedFilters = !showAdvancedFilters">
                    {{ showAdvancedFilters ? 'Hide advanced filters' : 'Show advanced filters' }}
                  </button>
                </div>
              </div>
            </div>
            
            <div v-if="showAdvancedFilters" class="advanced-filters mb-3">
              <div class="row g-3">
                <div class="col-md-3">
                  <label class="form-label">Status</label>
                  <select class="form-select" v-model="filters.status">
                    <option value="">All statuts</option>
                    <option value="New">New</option>
                    <option value="In progress">In Progress</option>
                    <option value="Resolved">Resolved</option>
                    <option value="False positive">False Positive</option>
                  </select>
                </div>
  
                <div class="col-md-3">
                  <label class="form-label">Alert type</label>
                  <select class="form-select" v-model="filters.alertType">
                    <option value="">All types</option>
                    <option v-for="type in alertTypes" :key="type.value" :value="type.display">
                      {{ type.display }}
                    </option>
                  </select>
                </div>
  
                <div class="col-md-3">
                  <label class="form-label">Entity</label>
                  <input type="text" class="form-control" placeholder="Entity" v-model="filters.entity" />
                </div>
  
                <div class="col-md-3">
                  <label class="form-label">Plateform</label>
                  <input type="text" class="form-control" placeholder="Plateform" v-model="filters.platform" />
                </div>
  
                <div class="col-md-3">
                  <label class="form-label">Start date</label>
                  <input type="datetime-local" class="form-control" v-model="filters.dateStart" />
                </div>
  
                <div class="col-md-3">
                  <label class="form-label">End date</label>
                  <input type="datetime-local" class="form-control" v-model="filters.dateEnd" />
                </div>
  
                <div class="col-md-3">
                  <label class="form-label">Details</label>
                  <input type="text" class="form-control" placeholder="Detail" v-model="filters.detail" />
                </div>
  
                <div class="col-md-3">
                  <label class="form-label">Sort</label>
                  <select class="form-select" v-model="filters.ordering">
                    <option value="date">Sort by date</option>
                    <option value="entity_name">Sort by entity</option>
                    <option value="platform_url">Sort by platform</option>
                    <option value="alert_type_display">Sort by alert type</option>
                    <option value="status_display">Sort by status</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
  
          <div class="default-table-area style-two default-table-width">
            <div v-if="loading" class="d-flex justify-content-center my-5">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
  
            <div v-else-if="error" class="alert alert-danger m-4">
              {{ error }}
            </div>
  
            <div v-else-if="paginatedItems.length === 0" class="alert alert-info m-4">
              No alerts found.
            </div>
  
            <div v-else class="table-responsive">
              <table class="table align-middle">
                <thead>
                  <tr>
                    <th scope="col" style="width: 5%">ID</th>
                    <th scope="col" style="width: 15%">Date</th>
                    <th scope="col" style="width: 20%">Entity</th>
                    <th scope="col" style="width: 25%">Plateform URL</th>
                    <th scope="col" style="width: 15%">Alert type</th>
                    <th scope="col" style="width: 10%">Status</th>
                    <th scope="col" style="width: 10%">Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in paginatedItems" :key="item.id">
                    <td class="text-body">{{ item.displayId }}</td>
                    <td>
                      <div class="content-truncate">
                        {{ formatDate(item.date) }}
                        <div class="tooltip-content">{{ formatDate(item.date) }}</div>
                      </div>
                    </td>
                    <td>
                      <div class="content-truncate" style="max-width: 200px;">
                        {{ item.entity_name }}
                        <div class="tooltip-content">{{ item.entity_name }}</div>
                      </div>
                    </td>
                    <td class="text-body">
                      <div class="content-truncate" style="max-width: 250px;">
                        <a :href="item.platform_url" target="_blank" rel="noopener noreferrer">{{ item.platform_url }}</a>
                        <div class="tooltip-content">{{ item.platform_url }}</div>
                      </div>
                    </td>
                    <td class="text-body">
                      <div class="content-truncate">
                        {{ item.alert_type_display }}
                        <div class="tooltip-content">{{ item.alert_type_display }}</div>
                      </div>
                    </td>
                    <td>
                      <select 
                        class="form-select form-select-sm" 
                        v-model="item.status_display" 
                        @change="updateStatus(item)"
                        :class="getStatusSelectClass(item.status_display)"
                        :disabled="!canManageAlerts"
                      >
                        <option value="New">New</option>
                        <option value="In progress">In Progress</option>
                        <option value="Resolved">Resolved</option>
                        <option value="False positive">False Positive</option>
                      </select>
                    </td>
                    <td>
                      <div class="d-flex align-items-center gap-2">
                        <button class="ps-0 border-0 bg-transparent lh-1 position-relative" 
                               @click="showDetails(item)">
                          <i class="material-symbols-outlined fs-16 text-primary">
                            visibility
                          </i>
                        </button>
                        <button class="ps-0 border-0 bg-transparent lh-1 position-relative" 
                               @click="goToEmailingPage(item.id)">
                          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16"
                              viewBox="0 0 24 24" fill="none" stroke="currentColor"
                              stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                              class="lucide lucide-mail text-success">
                              <rect width="20" height="16" x="2" y="4" rx="2" />
                              <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
                          </svg>
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
                      Display of {{ (currentPage - 1) * perPage + 1 }} à {{ Math.min(currentPage * perPage, filteredItems.length) }} on {{ totalItems }} results
                    </div>
                    <Pagination 
                    :total="totalItems" 
                    :perPage="perPage" 
                    v-model="currentPage" 
                    @page-change="handlePageChange" 
                    />
                    <button 
                    v-if="hasMoreData && filteredItems.length < totalItems" 
                    class="btn btn-outline-primary" 
                    @click="loadMoreData"
                    :disabled="loading"
                    >
                    <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                    Load more data
                    </button>
                </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  
    <div class="modal fade" :class="{ 'show d-block': showModal }" tabindex="-1" style="background-color: rgba(0,0,0,0.5);" v-if="showModal">
        <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Alert Details</h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body" v-if="selectedItem">
            <div class="mb-3">
              <strong>Entity:</strong> 
              <p>{{ selectedItem.entity_name }}</p>
            </div>
            <div class="mb-3">
              <strong>Plateform URL:</strong> 
              <p><a :href="selectedItem.platform_url" target="_blank" rel="noopener noreferrer">{{ selectedItem.platform_url }}</a></p>
            </div>
            <div class="mb-3">
              <strong>Alert Type:</strong> 
              <p>{{ selectedItem.alert_type_display }}</p>
            </div>
            <div class="mb-3">
              <strong>Date:</strong> 
              <p>{{ formatDate(selectedItem.date) }}</p>
            </div>
            <div class="mb-3">
              <strong>Update:</strong> 
              <p>{{ formatDate(selectedItem.updated_at) }}</p>
            </div>
            <div class="mb-3">
              <strong>Status:</strong> 
              <p>
                <span :class="getStatusBadgeClass(selectedItem.status_display)" class="badge p-2 fs-12 fw-normal">
                  {{ selectedItem.status_display }}
                </span>
              </p>
            </div>
            <div class="mb-3">
              <strong>Details:</strong> 
              <p style="white-space: pre-line;">{{ selectedItem.details }}</p>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeModal">Close</button>
          </div>
        </div>
      </div>
    </div>
  
    <Toast 
      :show="alertStore.toast.show" 
      :message="alertStore.toast.message" 
      :type="alertStore.toast.type" 
      :autoClose="true"
      :duration="alertStore.toast.duration"
      @close="handleToastClose" 
    />
  </template>
  
  <script setup lang="ts">
  import { ref, computed, onMounted, watch } from "vue";
  import { useRouter } from 'vue-router';
  import Pagination from "@/components/Common/Pagination.vue";
  import PageTitle from "@/components/Common/PageTitle.vue";
  import Toast from "@/components/Common/Toast.vue";
  import { useAlertStore, AlertFilters } from '@/stores/alert.store';
  import { Alert, ALERT_TYPES } from '@/types/alert.types';
  
  const router = useRouter();
  const alertStore = useAlertStore();
  
  const alertTypes = ref(ALERT_TYPES);
  
  const showAdvancedFilters = ref(false);
  const hasMoreData = computed(() => alertStore.hasMoreData);
  const totalItems = computed(() => alertStore.totalAlerts);
  
  const showModal = ref(false);
  const selectedItem = ref<Alert | null>(null);
  
  const loading = computed(() => alertStore.loading);
  const error = computed(() => alertStore.error);
  
  const canManageAlerts = computed(() => alertStore.canManageAlerts);
  
  const filters = ref<AlertFilters>({
    searchTerm: "",
    status: "",
    alertType: "",
    entity: "",
    platform: "",
    dateStart: "",
    dateEnd: "",
    detail: "",
    ordering: "date"
  });
  
  function resetFilters() {
    filters.value = {
      searchTerm: "",
      status: "",
      alertType: "",
      entity: "",
      platform: "",
      dateStart: "",
      dateEnd: "",
      detail: "",
      ordering: "date"
    };
    currentPage.value = 1;
  }
  
  async function applyFilters() {
    currentPage.value = 1; 
    // await alertStore.updateFilters(filters.value);
  }
  
  const filteredItems = computed(() => {
    return alertStore.filterAlerts(filters.value);
  });
  
  const sortedItems = computed(() => {
    return alertStore.sortAlerts(filteredItems.value, filters.value.ordering);
  });
  
  const perPage = ref(12);
  const currentPage = ref(1);
  
  
  const paginatedItems = computed(() => {
    const start = (currentPage.value - 1) * perPage.value;
    const end = start + perPage.value;
    return sortedItems.value.slice(start, end);
  });
  
  function formatDate(dateString: string): string {
    if (!dateString) return '';
    const options: Intl.DateTimeFormatOptions = { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString('fr-FR', options);
  }
  
  function getStatusBadgeClass(status: string): string {
    switch (status) {
      case "New":
        return "bg-warning bg-opacity-10 text-warning";
      case "In progress":
        return "bg-primary bg-opacity-10 text-primary";
      case "Resolved":
        return "bg-success bg-opacity-10 text-success";
      case "False positive":
        return "bg-secondary bg-opacity-10 text-secondary";
      default:
        return "bg-secondary bg-opacity-10 text-secondary";
    }
  }
  
  function getStatusSelectClass(status: string): string {
    switch (status) {
      case "New":
        return "status-new";
      case "In progress":
        return "status-inprogress";
      case "Resolved":
        return "status-resolved";
      case "False positive":
        return "status-falsepositive";
      default:
        return "";
    }
  }
  
  async function updateStatus(item: Alert) {
    try {
      await alertStore.updateAlertStatus(item.id, item.status_display);
    } catch (error: any) {
      console.error('Error updating status', error);
    }
  }
  async function loadMoreData() {
    try {
        await alertStore.loadMoreAlerts({});
    } catch (error) {
        console.error('Error', error);
    }
    }
function handlePageChange(newPage: number) {
  currentPage.value = newPage;
  
  const currentLoaded = alertStore.alerts.length;
  const neededItems = newPage * perPage.value;
  if (neededItems > currentLoaded && hasMoreData.value) {
    loadMoreData();
  }
}
  
  function showDetails(item: Alert) {
    selectedItem.value = item;
    showModal.value = true;
  }
  
  function goToEmailingPage(alertId: string) {
    router.push({ name: 'emailing', params: { id: alertId } });
  }
  
  function closeModal() {
    showModal.value = false;
    selectedItem.value = null;
  }
  
  function handleToastClose() {
    alertStore.toast.show = false;
  }
  
  onMounted(async () => {
    try {
      await alertStore.fetchAlerts();
    } catch (error: any) {
      console.error('Error loading alerts:', error);
    }
  });
  
  watch([
    () => filters.value.searchTerm, 
    () => filters.value.status, 
    () => filters.value.alertType,
    () => filters.value.entity,
    () => filters.value.platform,
    () => filters.value.dateStart,
    () => filters.value.dateEnd,
    () => filters.value.detail
  ], () => {
    applyFilters();
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
  
  .modal.show {
    display: block;
  }
  
  .advanced-filters {
    background-color: #f8f9fa;
    border-radius: 4px;
    padding: 15px;
    border: 1px solid #e9ecef;
  }
  
  .form-select-sm {
    min-width: 120px;
  }
  
  .status-new {
    border-color: #ffc107;
    color: #856404;
    background-color: #fff3cd;
  }
  
  .status-inprogress {
    border-color: #007bff;
    color: #004085;
    background-color: #cce5ff;
  }
  
  .status-resolved {
    border-color: #28a745;
    color: #155724;
    background-color: #d4edda;
  }
  
  .status-falsepositive {
    border-color: #6c757d;
    color: #383d41;
    background-color: #e2e3e5;
  }
  </style>