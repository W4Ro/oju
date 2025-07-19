<template>
  <div class="main-content-container overflow-hidden">
    <PageTitle pageTitle="Vendor List" />
    
    <div v-if="toast.show" class="toast-container position-fixed top-0 end-0 p-3" style="z-index: 1050;">
      <div class="toast show" :class="{
        'bg-success text-white': toast.type === 'success',
        'bg-danger text-white': toast.type === 'error',
        'bg-warning': toast.type === 'warning'
      }">
        <div class="toast-header">
          <strong class="me-auto">Notification</strong>
          <button type="button" class="btn-close" @click="closeToast"></button>
        </div>
        <div class="toast-body">{{ toast.message }}</div>
      </div>
    </div>
  </div>
  
  <div class="main-content-container overflow-hidden">
    <div class="card bg-white border-0 rounded-3 mb-4">
      <div class="card-body p-0">
        <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 p-4">
          <form class="position-relative table-src-form me-0" @submit.prevent>
            <input
              type="text"
              class="form-control"
              placeholder="Search"
              v-model="searchTerm"
            />
            <i class="material-symbols-outlined position-absolute top-50 start-0 translate-middle-y">
              search
            </i>
          </form>
          <button
            class="btn btn-outline-primary py-1 px-2 px-sm-4 fs-14 fw-medium rounded-3 hover-bg"
            @click="showAddModal = true"
            v-if="hasPermission('vendor_list_create')"
          >
            <span class="py-sm-1 d-block">
              <i class="ri-add-line d-none d-sm-inline-block me-1"></i>
              <span>Add Vendor</span>
            </span>
          </button>
        </div>

        <div v-if="loading && !formattedVendors.length" class="text-center my-5">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>


        <div v-if="filteredItems.length === 0" class="alert alert-info mx-4 my-3">
          No vendors found.
        </div>

        <div v-else class="default-table-area style-two default-table-width">
          <div class="table-responsive">
            <table class="table align-middle">
              <thead>
                <tr>
                  <th scope="col">ID</th>
                  <th scope="col">Name</th>
                  <th scope="col">Contact</th>
                  <th scope="col">Comments</th>
                  <th scope="col">Creation Date</th>
                  <th scope="col">Last Updated</th>
                  <th scope="col">Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in paginatedItems" :key="item.id">
                  <td class="text-body">
                    {{ item.mappedId }}
                  </td>
                  <td>
                    <div class="d-flex align-items-center">
                      <div class="flex-grow-1 position-relative top-1">
                        <h6 class="mb-0 fs-14 fw-medium">
                          {{ item.user.name }}
                        </h6>
                      </div>
                    </div>
                  </td>
                  <td class="position-relative">
                    <div class="content-truncate">
                      {{ item.email }}
                      <div class="tooltip-content">{{ item.email }}</div>
                    </div>
                  </td>
                  <td class="text-body position-relative">
                    <div class="content-truncate">
                      {{ item.company }}
                      <div class="tooltip-content">{{ item.company }}</div>
                    </div>
                  </td>
                  <td class="text-body">
                    {{ formatDate(item.createdAt) }}
                  </td>
                  <td class="text-body">
                    {{ formatDate(item.updatedAt) }}
                  </td>
                  <td>
                    <div class="d-flex align-items-center gap-1">
                      <button
                        class="ps-0 border-0 bg-transparent lh-1 position-relative top-2"
                        @click="editItem(item)"
                      >
                        <i class="material-symbols-outlined fs-16 text-body">
                          edit
                        </i>
                      </button>
                      <button
                        v-if="canDelete"
                        class="ps-0 border-0 bg-transparent lh-1 position-relative top-2"
                        @click="confirmDelete(item)"
                      >
                        <i class="material-symbols-outlined fs-16 text-danger">
                          delete
                        </i>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <div class="p-4 pt-lg-4 d-flex flex-column align-items-center">
            <button 
              v-if="hasMoreData" 
              @click="loadMore" 
              class="btn btn-outline-primary mb-3"
              :disabled="loading"
            >
              <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
              Load More
            </button>
            <Pagination :total="totalItems" :perPage="perPage" v-model="currentPage" @change="handlePageChange" />
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" :class="{ 'show d-block': showAddModal }" tabindex="-1" style="background-color: rgba(0,0,0,0.5);" v-if="showAddModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-light">
            <h5 class="modal-title">Add Vendor</h5>
            <button type="button" class="btn-close" @click="cancelAdd"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="addItem">
              <div class="mb-3">
                <label for="name" class="form-label">Name <span class="text-danger">*</span></label>
                <input 
                  type="text" 
                  class="form-control form-control-sm" 
                  id="name" 
                  v-model="newItem.name" 
                  :class="{'is-invalid': validationErrors.name}"
                  placeholder="Enter vendor name"
                >
                <div class="invalid-feedback" v-if="validationErrors.name">
                  {{ validationErrors.name }}
                </div>
              </div>
              
              <div class="mb-3">
                <label for="contact" class="form-label">Contact <span class="text-danger">*</span></label>
                <input 
                  type="text" 
                  class="form-control form-control-sm" 
                  id="contact" 
                  v-model="newItem.contact"
                  :class="{'is-invalid': validationErrors.contact}"
                  placeholder="Enter contact"
                >
                <div class="invalid-feedback" v-if="validationErrors.contact">
                  {{ validationErrors.contact }}
                </div>
              </div>
              
              <div class="mb-3">
                <label for="comments" class="form-label">Comments <span class="text-danger">*</span></label>
                <textarea 
                  class="form-control form-control-sm" 
                  id="comments" 
                  v-model="newItem.comments" 
                  rows="3"
                  :class="{'is-invalid': validationErrors.comments}"
                  placeholder="Enter comments"
                ></textarea>
                <div class="invalid-feedback" v-if="validationErrors.comments">
                  {{ validationErrors.comments }}
                </div>
              </div>
              
              <div class="d-flex justify-content-end gap-2">
                <button type="button" class="btn btn-sm btn-secondary" @click="cancelAdd">Cancel</button>
                <button type="submit" class="btn btn-sm btn-primary" :disabled="isSubmitting || !hasPermission('vendor_list_create')">
                  <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-1" role="status"></span>
                  Save
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" :class="{ 'show d-block': showEditModal }" tabindex="-1" style="background-color: rgba(0,0,0,0.5);" v-if="showEditModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title">Edit Vendor</h5>
            <button type="button" class="btn-close btn-close-white" @click="cancelEdit"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="updateItem">
              <div class="mb-3">
                <label for="edit-name" class="form-label">Name <span class="text-danger">*</span></label>
                <input 
                  type="text" 
                  class="form-control form-control-sm" 
                  id="edit-name" 
                  v-model="editingItem.name" 
                  :class="{'is-invalid': validationErrors.name}"
                  placeholder="Enter vendor name"
                >
                <div class="invalid-feedback" v-if="validationErrors.name">
                  {{ validationErrors.name }}
                </div>
              </div>
              
              <div class="mb-3">
                <label for="edit-contact" class="form-label">Contact <span class="text-danger">*</span></label>
                <input 
                  type="text" 
                  class="form-control form-control-sm" 
                  id="edit-contact" 
                  v-model="editingItem.contact"
                  :class="{'is-invalid': validationErrors.contact}"
                  placeholder="Enter contact"
                >
                <div class="invalid-feedback" v-if="validationErrors.contact">
                  {{ validationErrors.contact }}
                </div>
              </div>
              
              <div class="mb-3">
                <label for="edit-comments" class="form-label">Comments <span class="text-danger">*</span></label>
                <textarea 
                  class="form-control form-control-sm" 
                  id="edit-comments" 
                  v-model="editingItem.comments" 
                  rows="3"
                  :class="{'is-invalid': validationErrors.comments}"
                  placeholder="Enter comments"
                ></textarea>
                <div class="invalid-feedback" v-if="validationErrors.comments">
                  {{ validationErrors.comments }}
                </div>
              </div>
              
              <div class="d-flex justify-content-end gap-2">
                <button type="button" class="btn btn-sm btn-secondary" @click="cancelEdit">Cancel</button>
                <button type="submit" class="btn btn-sm btn-primary" :disabled="isSubmitting || !hasPermission('vendor_list_edit')">
                  <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-1" role="status"></span>
                  Update
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" :class="{ 'show d-block': showDeleteModal }" tabindex="-1" style="background-color: rgba(0,0,0,0.5);" v-if="showDeleteModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-danger text-white">
            <h5 class="modal-title">Confirm Deletion</h5>
            <button type="button" class="btn-close btn-close-white" @click="showDeleteModal = false"></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to delete this vendor?</p>
            <p class="mb-0"><strong>Name:</strong> {{ itemToDelete?.user?.name || '' }}</p>
            <p class="mb-0"><strong>ID:</strong> {{ itemToDelete ? getVendorMappedId(itemToDelete) : '' }}</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-sm btn-secondary" @click="showDeleteModal = false">Cancel</button>
            <button type="button" class="btn btn-sm btn-danger" @click="deleteItem" :disabled="isSubmitting || !hasPermission('vendor_list_delete')">
              <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-1" role="status"></span>
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import Pagination from "@/components/Common/Pagination.vue";
import PageTitle from "@/components/Common/PageTitle.vue";
import feather from "feather-icons";
import { useVendorStore } from "@/stores/vendorStore";
import type { VendorCreateData, VendorUpdateData } from "@/types/vendor.types";
import {hasPermission, hasAnyPermission} from "@/utils/permissions";

const vendorStore = useVendorStore();

const searchTerm = ref("");
const showAddModal = ref(false);
const showEditModal = ref(false);
const showDeleteModal = ref(false);
const isSubmitting = ref(false);

const idMapping = ref(new Map<string, number>());
let nextMappedId = 1;

const getMappedId = (uuid: string): number => {
  if (!idMapping.value.has(uuid)) {
    idMapping.value.set(uuid, nextMappedId++);
  }
  return idMapping.value.get(uuid) || 0;
};

const getUuidFromMappedId = (mappedId: number): string | undefined => {
  for (const [uuid, id] of idMapping.value.entries()) {
    if (id === mappedId) {
      return uuid;
    }
  }
  return undefined;
};

const getVendorMappedId = (vendor: any): number => {
  return vendor ? getMappedId(vendor.id) : 0;
};

const loading = computed(() => vendorStore.loading);
const error = computed(() => vendorStore.error);
const formattedVendors = computed(() => {
  return vendorStore.formattedVendors.map((vendor: any) => ({
    ...vendor,
    mappedId: getMappedId(vendor.id)
  }));
});
const perPage = computed(() => vendorStore.perPage);
const totalItems = computed(() => vendorStore.totalItems);
const currentPage = computed({
  get: () => vendorStore.currentPage,
  set: (value) => { vendorStore.currentPage = value; }
});
const hasMoreData = computed(() => vendorStore.hasMoreData);
const toast = computed(() => vendorStore.toast);
const canEdit = computed(() => vendorStore.canEdit);
const canDelete = computed(() => vendorStore.canDelete);

const newItem = ref({
  name: "",
  contact: "",
  comments: ""
});

const validationErrors = ref({
  name: "",
  contact: "",
  comments: ""
});

const editingItem = ref({
  id: "",
  name: "",
  contact: "",
  comments: ""
});

const itemToDelete = ref<any>(null);

const filteredItems = computed(() => {
  if (!searchTerm.value.trim()) {
    return formattedVendors.value;
  }
  
  const term = searchTerm.value.toLowerCase();
  return formattedVendors.value.filter(
    (item: any) =>
      (item.mappedId && item.mappedId.toString().includes(term)) ||
      (item.user.name && item.user.name.toLowerCase().includes(term)) ||
      (item.email && item.email.toLowerCase().includes(term)) ||
      (item.company && item.company.toLowerCase().includes(term))
  );
});

const paginatedItems = computed(() => {
  const start = (currentPage.value - 1) * perPage.value;
  const end = start + perPage.value;
  return filteredItems.value.slice(start, end);
});

function validateForm(data: { name: string, contact: string, comments: string }): boolean {
  let isValid = true;
  
  validationErrors.value = {
    name: "",
    contact: "",
    comments: ""
  };
  
  if (!data.name || !data.name.trim()) {
    validationErrors.value.name = "Name is required";
    isValid = false;
  } else if (data.name.length < 3) {
    validationErrors.value.name = "Name cannot be less than 3 characters";
    isValid = false;
  } else if (data.name.length > 255) {
    validationErrors.value.name = "Name cannot exceed 255 characters";
    isValid = false;
  }
  
  if (!data.contact || !data.contact.trim()) {
    validationErrors.value.contact = "Contact is required";
    isValid = false;
  } else if (data.contact.length > 255) {
    validationErrors.value.contact = "Contact cannot exceed 255 characters";
    isValid = false;
  }
  
  if (!data.comments || !data.comments.trim()) {
    validationErrors.value.comments = "Comments are required";
    isValid = false;
  } else if (data.comments.length > 500) {
    validationErrors.value.comments = "Comments cannot exceed 500 characters";
    isValid = false;
  }
  
  return isValid;
}

function closeToast() {
  vendorStore.toast.show = false;
}

function editItem(item: any) {
  editingItem.value = {
    id: item.id,
    name: item.user.name,
    contact: item.email,
    comments: item.company
  };
  showEditModal.value = true;
}

function confirmDelete(item: any) {
  itemToDelete.value = item;
  showDeleteModal.value = true;
}

async function addItem() {
  if (!validateForm(newItem.value)) {
    return;
  }
  
  isSubmitting.value = true;
  
  try {
    const vendorData: VendorCreateData = {
      name: newItem.value.name.trim(),
      contact: newItem.value.contact.trim(),
      comments: newItem.value.comments.trim()
    };
    
    await vendorStore.createVendor(vendorData);
    
    cancelAdd();
  } catch (error) {
    console.error(':', error);
  } finally {
    isSubmitting.value = false;
  }
}

async function updateItem() {
  if (!validateForm(editingItem.value)) {
    return;
  }
  if (!canEdit.value) {
    return;
  }
  isSubmitting.value = true;
  
  try {
    const vendorData: VendorUpdateData = {
      name: editingItem.value.name.trim(),
      contact: editingItem.value.contact.trim(),
      comments: editingItem.value.comments.trim()
    };
    
    await vendorStore.updateVendor(editingItem.value.id, vendorData);
    
    cancelEdit();
  } catch (error) {
    console.error(':', error);
  } finally {
    isSubmitting.value = false;
  }
}

async function deleteItem() {
  isSubmitting.value = true;
  
  try {
    if (itemToDelete.value) {
      await vendorStore.deleteVendor(itemToDelete.value.id);
      itemToDelete.value = null;
    }
    
    showDeleteModal.value = false;
  } catch (error) {
    console.error(':', error);
  } finally {
    isSubmitting.value = false;
  }
}

function loadMore() {
  vendorStore.loadMoreVendors();
}

function handlePageChange(page: number) {
  currentPage.value = page;
}

function cancelAdd() {
  showAddModal.value = false;
  newItem.value = {
    name: "",
    contact: "",
    comments: ""
  };
  validationErrors.value = {
    name: "",
    contact: "",
    comments: ""
  };
}

function cancelEdit() {
  showEditModal.value = false;
  editingItem.value = {
    id: "",
    name: "",
    contact: "",
    comments: ""
  };
  validationErrors.value = {
    name: "",
    contact: "",
    comments: ""
  };
}

function formatDate(dateStr: string) {
  try {
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) {
      return dateStr;
    }

    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const year = date.getFullYear();
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');

    return `${day}/${month}/${year} ${hours}:${minutes}`;
  } catch (e) {
    console.error("Error formatting date:", e);
    return dateStr;
  }
}

onMounted(() => {
  vendorStore.fetchVendors();
  
  if (typeof feather !== 'undefined') {
    feather.replace();

    const observer = new MutationObserver(() => {
      feather.replace();
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }
});

watch(searchTerm, () => {
  currentPage.value = 1;
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

.invalid-feedback {
  display: block;
  font-size: 0.75rem;
}

.form-control:focus, .form-select:focus {
  border-color: #1976d2;
  box-shadow: 0 0 0 0.2rem rgba(25, 118, 210, 0.25);
}

.form-label {
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.form-control-sm, .form-select-sm, .btn-sm {
  font-size: 0.875rem;
  padding: 0.25rem 0.5rem;
}

.modal-content {
  border-radius: 0.5rem;
  overflow: hidden;
}

.modal-header {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.modal-footer {
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.bg-light {
  background-color: #f8f9fa;
}

.btn-close-white {
  filter: invert(1) grayscale(100%) brightness(200%);
}

.toast-container {
  z-index: 1100;
}
</style>