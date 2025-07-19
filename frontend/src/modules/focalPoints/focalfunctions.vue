<template>
  <div class="main-content-container overflow-hidden">
    <PageTitle pageTitle="Functions" subTitle="Focal" />
  </div>
  <div class="main-content-container overflow-hidden">

    <div class="card bg-white border-0 rounded-3 mb-4">
      <div class="card-body p-0">
        <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 p-4">
          <form class="position-relative table-src-form me-0" @submit.prevent>
            <input
              type="text"
              class="form-control"
              placeholder="Seach"
              v-model="searchTerm"
            />
            <i class="material-symbols-outlined position-absolute top-50 start-0 translate-middle-y">
              search
            </i>
          </form>
          <button
            class="btn btn-outline-primary py-1 px-2 px-sm-4 fs-14 fw-medium rounded-3 hover-bg"
            @click="openCreateModal"
            v-if="hasPermission('focal_functions_create')"
          >
            <span class="py-sm-1 d-block">
              <i class="ri-add-line d-none d-sm-inline-block me-1"></i>
              <span>New function</span>
            </span>
          </button>
        </div>

        <div class="default-table-area style-two default-table-width">
          <div class="table-responsive">
            <table class="table align-middle">
              <thead>
                <tr>
                  <th scope="col">ID</th>
                  <th scope="col">Function name</th>
                  <th scope="col">Creation date</th>
                  <th scope="col">Last modified</th>
                  <th scope="col">Action</th>
                </tr>
              </thead>
              <tbody v-if="!loading && focalFunctionStore.hasFocalFunctions">
                <tr v-for="func in paginatedFunctions" :key="func.id">
                  <td class="text-body">{{ focalFunctionStore.getSequentialIdFromUuid(func.id) || func.id }}</td>
                  <td>{{ func.name }}</td>
                  <td class="text-body">{{ formatDate(func.created_at) }}</td>
                  <td class="text-body">{{ formatDate(func.updated_at) }}</td>
                  <td v-if="hasAnyPermission(['focal_functions_edit', 'focal_functions_delete', 'focal_points_view'])">
                    <div class="d-flex align-items-center gap-1">
                      <button
                        class="ps-0 border-0 bg-transparent lh-1 position-relative top-2"
                        @click="editFunction(func)"
                        v-if="hasPermission('focal_functions_edit')"
                      >
                        <i class="material-symbols-outlined fs-16 text-body">edit</i>
                      </button>
                      <button
                        class="ps-0 border-0 bg-transparent lh-1 position-relative top-2"
                        @click="confirmDelete(func)"
                        v-if="hasPermission('focal_functions_delete')"
                      >
                        <i class="material-symbols-outlined fs-16 text-danger">delete</i>
                      </button>
                      <router-link
                        :to="{ name: 'focalPoints', params: { id: func.id } }"
                        class="ps-0 border-0 bg-transparent lh-1 position-relative top-2"
                        v-if="hasPermission('focal_points_view')"
                      >
                        <i class="material-symbols-outlined fs-16 text-primary">people</i>
                      </router-link>
                    </div>
                  </td>
                </tr>
              </tbody>
              <tbody v-else-if="loading">
                <tr>
                  <td colspan="5" class="text-center py-4">
                    <div class="spinner-border text-primary" role="status">
                      <span class="visually-hidden">Loading...</span>
                    </div>
                  </td>
                </tr>
              </tbody>
              <tbody v-else>
                <tr>
                  <td colspan="5" class="text-center py-4">
                    No function found
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="p-4 pt-lg-4">
            <Pagination 
              :total="totalFunctions" 
              :perPage="itemsPerPage" 
              v-model="currentPage" 
            />
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="functionModal" tabindex="-1" aria-hidden="true" ref="functionModal" v-if="hasPermission('focal_functions_create') || hasPermission('focal_functions_edit')">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title fs-5">{{ isEditing ? 'Modify' : 'Create' }} a function</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveFunction">
              <div class="mb-3">
                <label for="function-name" class="form-label">Name of the function</label>
                <input
                  type="text"
                  class="form-control"
                  id="function-name"
                  v-model="functionForm.name"
                  required
                />
              </div>
              <div class="d-flex justify-content-end gap-2">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="submit" class="btn btn-primary" :disabled="loading">
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                  {{ isEditing ? 'Update' : 'Create' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="deleteModal" tabindex="-1" aria-hidden="true" ref="deleteModal" v-if="hasPermission('focal_functions_delete')">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title fs-5" id="deleteModalLabel">Confirm deletion</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p>
              Are you sure you want to delete the function
              <strong>{{ functionToDelete?.name }}</strong> ?
            </p>
            <p class="text-danger">
              This action is irreversible and will also delete all focal points associated with this function.
            </p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-danger" @click="deleteFunction" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <Toast 
      :show="focalFunctionStore.toast.show" 
      :message="focalFunctionStore.toast.message" 
      :type="focalFunctionStore.toast.type" 
      :autoClose="true"
      :duration="focalFunctionStore.toast.duration"
      @close="handleToastClose" 
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { Modal } from 'bootstrap';
import { FocalFunction } from '@/types/focalFunction.types';
import { useFocalFunctionStore } from '@/stores/focalFunction.store';
import Pagination from "@/components/Common/Pagination.vue";
import PageTitle from "@/components/Common/PageTitle.vue";
import Toast from "@/components/Common/Toast.vue";
import {hasPermission, hasAnyPermission} from "@/utils/permissions";

const focalFunctionStore = useFocalFunctionStore();

const loading = computed(() => focalFunctionStore.loading);
const error = computed(() => focalFunctionStore.error);

const currentPage = ref(1);
const itemsPerPage = ref(10);

const searchTerm = ref('');

const functionModal = ref<HTMLElement | null>(null);
const deleteModal = ref<HTMLElement | null>(null);
const functionToDelete = ref<FocalFunction | null>(null);
const isEditing = ref(false);
const functionForm = ref({ id: '', name: '' });

const filteredFunctions = computed(() => {
  return focalFunctionStore.filterFunctions(searchTerm.value);
});

const totalFunctions = computed(() => filteredFunctions.value.length);

const paginatedFunctions = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value;
  const end = start + itemsPerPage.value;
  return filteredFunctions.value.slice(start, end);
});

function formatDate(dateString: string) {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
}

function openCreateModal() {
  isEditing.value = false;
  functionForm.value = { id: '', name: '' };
  
  const modalInstance = new Modal(functionModal.value as HTMLElement);
  modalInstance.show();
}

function editFunction(func: FocalFunction) {
  isEditing.value = true;
  functionForm.value = { id: func.id, name: func.name };
  
  const modalInstance = new Modal(functionModal.value as HTMLElement);
  modalInstance.show();
}

function confirmDelete(func: FocalFunction) {
  functionToDelete.value = func;
  
  const modalInstance = new Modal(deleteModal.value as HTMLElement);
  modalInstance.show();
}

async function saveFunction() {
  try {
    if (isEditing.value) {
      await focalFunctionStore.updateFocalFunction(
        functionForm.value.id, 
        { id: functionForm.value.id, name: functionForm.value.name }
      );
    } else {
      await focalFunctionStore.createFocalFunction({ name: functionForm.value.name });
    }
    
    Modal.getInstance(functionModal.value as HTMLElement)?.hide();
  } catch (error) {
    console.error("Error saving function:", error);
  }
}

async function deleteFunction() {
  if (!functionToDelete.value) return;
  
  try {
    await focalFunctionStore.deleteFocalFunction(functionToDelete.value.id);
    
    Modal.getInstance(deleteModal.value as HTMLElement)?.hide();
  } catch (error) {
    console.error("Error deleting function:", error);
  }
}

function handleToastClose() {
  focalFunctionStore.toast.show = false;
}

watch(searchTerm, () => {
  currentPage.value = 1;
});

onMounted(async () => {
  await focalFunctionStore.fetchFocalFunctions();
});
</script>