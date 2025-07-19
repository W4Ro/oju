<template>
  <div class="card bg-white border-0 rounded-3 mb-4">
    <div class="card-body p-0">
      <div class="p-4">
        <div
          class="d-flex justify-content-between align-items-center flex-wrap gap-3"
        >
          <h3 class="mb-0">Platforms</h3>
          <form class="position-relative table-src-form me-0" @submit.prevent>
            <input
              type="text"
              class="form-control"
              placeholder="Search"
              v-model="searchTerm"
            />
            <i
              class="material-symbols-outlined position-absolute top-50 start-0 translate-middle-y"
            >
              search
            </i>
          </form>
        </div>
      </div>

      <div v-if="isLoading" class="p-4 text-center">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <div v-else class="default-table-area style-two">
        <div class="table-responsive">
          <table class="table align-middle">
            <thead>
              <tr>
                <th scope="col">
                  <div class="form-check">
                    <label
                      class="position-relative top-2 ms-1"
                      for="flexCheckDefault7"
                    >
                      ID
                    </label>
                  </div>
                </th>
                <th scope="col">URL</th>
                <th scope="col">Number of alerts</th>
                <th scope="col">Creation date</th>
                <th scope="col">Last updated</th>
                <th scope="col">Status</th>
                <th scope="col" v-if="hasAnyPermission(['platforms_edit', 'platforms_delete', 'platforms_toggle'])">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in paginatedItems" :key="item.id">
                <td class="text-body">
                  <div class="form-check">
                    <label
                      class="position-relative top-2 ms-1"
                      for="flexCheckDefault12"
                    >
                      {{ item.mappedId }}
                    </label>
                  </div>
                </td>
                <td>
                  <a
                    :href="item.url"
                    target="_blank"
                    class="text-body"
                  >
                    {{ item.url }}
                  </a>
                </td>
                <td>{{ item.alerts_count || 0 }}</td>
                <td class="text-body">
                  {{ formatDate(item.created_at) }}
                </td>
                <td class="text-body">
                  {{ formatDate(item.updated_at) }}
                </td>
                <td>
                  <span
                    class="badge bg-opacity-10 p-2 fs-12 fw-normal"
                    :class="item.is_active ? 'bg-success text-success' : 'bg-danger text-danger'"
                  >
                    {{ item.is_active ? "Active" : "Desactivate" }}
                  </span>
                </td>
                <td v-if="hasPermission('platforms_edit') || hasPermission('platforms_delete') || hasPermission('platforms_toggle')">
                  <div class="d-flex align-items-center gap-1">
                    <button
                      class="ps-0 border-0 bg-transparent lh-1 position-relative top-2"
                      data-bs-toggle="modal"
                      data-bs-target="#platformUpdateModal"
                      @click="openEditModal(item)"
                      v-if="hasPermission('platforms_edit')"
                    >
                      <i class="material-symbols-outlined fs-16 text-body">
                        edit
                      </i>
                    </button>
                    <button 
                      v-if="hasPermission('platforms_toggle')"
                      class="ps-0 border-0 bg-transparent lh-1 position-relative top-2"
                      @click="confirmTogglePlatform(item)"
                      :title="item.is_active ? 'Disable the platform' : 'Enable the plateform'"
                    >
                      <i class="material-symbols-outlined fs-16" :class="item.is_active ? 'text-success' : 'text-danger'">
                        {{ item.is_active ? 'toggle_on' : 'toggle_off' }}
                      </i>
                    </button>
                    <button
                      v-if="hasPermission('platforms_delete')"
                      class="ps-0 border-0 bg-transparent lh-1 position-relative top-2"
                      data-bs-toggle="modal"
                      data-bs-target="#deleteModal"
                      @click="platformToDelete = item"
                    >
                      <i class="material-symbols-outlined fs-16 text-danger">
                        delete
                      </i>
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="paginatedItems.length === 0">
                <td :colspan="hasManagePermission ? 7 : 6" class="text-center py-4">
                  <i class="ri-inbox-line fs-2 mb-3 text-muted d-block"></i>
                  <span class="text-muted">No platform found</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="p-4 d-flex justify-content-between align-items-center flex-wrap">
          <div
            class="d-flex justify-content-center justify-content-sm-between align-items-center text-center flex-wrap gap-2 showing-wrap"
          >
            <span class="fs-12 fw-medium">
              Showing {{ displayedItemsStart }}-{{ displayedItemsEnd }} of {{ filteredItems.length }} Results
            </span>
          </div>
          
          <nav aria-label="Page navigation" v-if="totalPages > 1">
            <ul class="pagination mb-0 justify-content-center">
              
              <li class="page-item" :class="{ disabled: currentPage === 1 }">
                <a 
                  class="page-link icon" 
                  href="#" 
                  aria-label="Previous"
                  @click.prevent="changePage(currentPage - 1)"
                >
                  <i class="material-symbols-outlined">keyboard_arrow_left</i>
                </a>
              </li>
              
              <li 
                v-for="page in displayedPages" 
                :key="page"
                class="page-item"
              >
                <a 
                  class="page-link" 
                  :class="{ active: page === currentPage }" 
                  href="#" 
                  @click.prevent="changePage(page)"
                >
                  {{ page }}
                </a>
              </li>
              
              <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                <a 
                  class="page-link icon" 
                  href="#" 
                  aria-label="Next"
                  @click.prevent="changePage(currentPage + 1)"
                >
                  <i class="material-symbols-outlined">keyboard_arrow_right</i>
                </a>
              </li>
            </ul>
          </nav>
          
          <button
            v-if="hasPermission('platforms_create')"
            class="btn btn-outline-primary py-1 px-2 px-sm-4 fs-14 fw-medium rounded-3 hover-bg"
            data-bs-toggle="modal"
            data-bs-target="#platformModal"
          >
            <span class="py-sm-1 d-block">
              <i class="ri-add-line me-1"></i>
              <span>Add platform</span>
            </span>
          </button>
        </div>
      </div>
    </div>
  </div>

  <div
    class="modal fade"
    id="platformModal"
    tabindex="-1"
    aria-labelledby="platformModalLabel"
    aria-hidden="true"
    v-if="hasPermission('platforms_create')"
  >
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header bg-primary text-white">
          <h1
            class="modal-title fs-5 mb-1 text-center text-white"
            id="platformModalLabel"
          >
            Add platform
          </h1>
          <button
            type="button"
            class="btn-close text-white"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="createPlatform">
            <div class="form-group mb-4">
              <label class="label">Platform URL <span class="text-danger">*</span></label>
              <input
                type="text"
                class="form-control text-dark"
                placeholder="Enter platform URL"
                v-model="newPlatform.url"
                :class="{'is-invalid': validationErrors.url}"
              />
              <div class="invalid-feedback" v-if="validationErrors.url">
                {{ validationErrors.url }}
              </div>
            </div>

            <div class="form-group mb-4">
              <label class="label text-secondary">Active</label>
              <div class="form-group position-relative">
                <select 
                  class="form-select form-control h-60" 
                  v-model="newPlatform.is_active"
                >
                  <option :value="true" class="text-dark">Yes</option>
                  <option :value="false" class="text-dark">No</option>
                </select>
              </div>
            </div>

            <div class="modal-footer">
              <button
                type="button"
                class="btn btn-danger text-white"
                data-bs-dismiss="modal"
              >
                Cancel
              </button>
              <button 
                v-if="hasPermission('platforms_create')"
                type="submit" 
                class="btn btn-primary text-white"
                :disabled="isSubmitting"
              >
                <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                Submit
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>

  <div
    class="modal fade"
    id="platformUpdateModal"
    tabindex="-1"
    aria-labelledby="platformUpdateModalLabel"
    aria-hidden="true"
    v-if="hasPermission('platforms_edit')"
  >
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header bg-primary text-white">
          <h1
            class="modal-title fs-5 mb-1 text-center text-white"
            id="platformUpdateModalLabel"
          >
            Edit platform
          </h1>
          <button
            type="button"
            class="btn-close text-white"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="updatePlatform">
            <div class="form-group mb-4">
              <label class="label">Platform URL <span class="text-danger">*</span></label>
              <input
                v-model="editPlatform.url"
                type="text"
                class="form-control text-dark"
                placeholder="Enter platform URL"
                :class="{'is-invalid': validationErrors.editUrl}"
              />
              <div class="invalid-feedback" v-if="validationErrors.editUrl">
                {{ validationErrors.editUrl }}
              </div>
            </div>

            <div class="form-group mb-4">
              <label class="label text-secondary">Active</label>
              <div class="form-group position-relative">
                <select v-model="editPlatform.is_active" class="form-select form-control h-60">
                  <option :value="true" class="text-dark">Yes</option>
                  <option :value="false" class="text-dark">No</option>
                </select>
              </div>
            </div>

            <div class="modal-footer">
              <button
                type="button"
                class="btn btn-danger text-white"
                data-bs-dismiss="modal"
              >
                Cancel
              </button>
              <button 
                type="submit" 
                class="btn btn-primary text-white"
                :disabled="isSubmitting"
              >
                <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                Edit
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>

  <div
    class="modal fade"
    id="deleteModal"
    tabindex="-1"
    aria-labelledby="deleteModalLabel"
    aria-hidden="true"
    v-if="hasPermission('platforms_delete')"
  >
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header bg-danger text-white">
          <h3
            class="modal-title fs-5 mb-1 text-center text-white"
            id="deleteModalLabel"
          >
            Delete confirmation
          </h3>
          <button
            type="button"
            class="btn-close text-white"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>
        <div class="modal-body">
          <p>Do you really want to delete this platform?</p>
          <div v-if="platformToDelete" class="alert alert-warning">
            <strong>ID:</strong> {{ platformToDelete.mappedId }}<br>
            <strong>URL:</strong> {{ platformToDelete.url }}
          </div>
          <span class="d-block mt-2 text-danger fw-bold">This action is irreversible</span>
        </div>
        <div class="modal-footer">
          <button
            type="button"
            class="btn btn-secondary"
            data-bs-dismiss="modal"
          >
            Non
          </button>
          <button 
            type="button" 
            class="btn btn-danger text-white"
            @click="deletePlatform"
            :disabled="isSubmitting"
          >
            <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
            Oui
          </button>
        </div>
      </div>
    </div>
  </div>
  <div class="modal fade" id="toggleModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header" :class="platformToToggle && platformToToggle.is_active ? 'bg-danger text-white' : 'bg-success text-white'">
          <h3 class="modal-title fs-5 mb-1 text-center text-white">
            {{ platformToToggle && platformToToggle.is_active ? 'Deactivate' : 'Activate' }}  plateform
          </h3>
          <button type="button" class="btn-close text-white" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <p>
            Are you sure you want to
            {{ platformToToggle && platformToToggle.is_active ? 'deactivate' : 'activate' }} 
            this plateform ?
          </p>
          <div v-if="platformToToggle" class="alert alert-info">
            <strong>ID:</strong> {{ platformToToggle.mappedId }}<br>
            <strong>URL:</strong> {{ platformToToggle.url }}
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
            Cancel
          </button>
          <button 
            type="button" 
            :class="platformToToggle && platformToToggle.is_active ? 'btn-danger' : 'btn-success'"
            class="btn text-white"
            @click="togglePlatformStatus"
            :disabled="isSubmitting"
          >
            <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
            Confirm
          </button>
        </div>
      </div>
    </div>
  </div>
  <div 
      class="toast position-fixed top-0 end-0 m-3" 
      :class="{ 'show': entityStore.toast.show, 
                'bg-success text-white': entityStore.toast.type === 'success',
                'bg-danger text-white': entityStore.toast.type === 'error',
                'bg-warning': entityStore.toast.type === 'warning' }"
      role="alert" 
      aria-live="assertive" 
      aria-atomic="true"
      style="z-index: 9999;"
    >
      <div class="d-flex">
        <div class="toast-body">
          {{ entityStore.toast.message }}
        </div>
        <button type="button" class="btn-close me-2 m-auto" @click="entityStore.toast.show = false"></button>
      </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth.store';
import { useEntityStore } from '@/stores/entityStore';
import { Modal } from 'bootstrap';
import { hasPermission, hasAnyPermission } from '@/utils/permissions';

interface Platform {
  id: string;
  url: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  alerts_count?: number;
}

interface PlatformWithMappedId extends Platform {
  mappedId: number;
}

const route = useRoute();
const authStore = useAuthStore();
const entityStore = useEntityStore();

const entityId = computed(() => route.params.id as string);

const platforms = ref<PlatformWithMappedId[]>([]);
const isLoading = ref(true);
const isSubmitting = ref(false);
const searchTerm = ref("");
const currentPage = ref(1);
const itemsPerPage = ref(5);
const validationErrors = ref({
  url: '',
  editUrl: ''
});

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

const hasManagePermission = computed(() => {
  return authStore.hasPermission('entities_manage_platforms');
});

const newPlatform = ref({
  url: '',
  is_active: true
});

const editPlatform = ref({
  id: '',
  url: '',
  is_active: true
});

const platformToDelete = ref<PlatformWithMappedId | null>(null);

const platformToToggle = ref<PlatformWithMappedId | null>(null);

let toggleModal = null;
let deleteModal = null;
let platformModal = null;
let platformUpdateModal = null;
const cleanupModal = () => {
  document.body.classList.remove('modal-open');
  document.body.style.overflow = '';
  document.body.style.paddingRight = '';
  document.querySelectorAll('.modal-backdrop').forEach(b => b.remove());
};

const initModals = () => {
  toggleModal = new Modal(document.getElementById('toggleModal'));
  deleteModal = new Modal(document.getElementById('deleteModal'));
  platformModal = new Modal(document.getElementById('platformModal'));
  platformUpdateModal = new Modal(document.getElementById('platformUpdateModal'));
  document.getElementById('platformModal')?.addEventListener('hidden.bs.modal', cleanupModal);
  document.getElementById('platformUpdateModal')?.addEventListener('hidden.bs.modal', cleanupModal);
  document.getElementById('deleteModal')?.addEventListener('hidden.bs.modal', cleanupModal);
  document.getElementById('toggleModal')?.addEventListener('hidden.bs.modal', cleanupModal);
};

const filteredItems = computed(() => {
  if (!searchTerm.value) return platforms.value;
  
  const term = searchTerm.value.toLowerCase();
  return platforms.value.filter(platform => 
    platform.url.toLowerCase().includes(term)
  );
});

const totalPages = computed(() => {
  return Math.ceil(filteredItems.value.length / itemsPerPage.value);
});

const paginatedItems = computed(() => {
  const startIndex = (currentPage.value - 1) * itemsPerPage.value;
  const endIndex = startIndex + itemsPerPage.value;
  return filteredItems.value.slice(startIndex, endIndex);
});

const displayedPages = computed(() => {
  const maxVisiblePages = 5;
  
  if (totalPages.value <= maxVisiblePages) {
    return Array.from({ length: totalPages.value }, (_, i) => i + 1);
  }
  
  const halfVisible = Math.floor(maxVisiblePages / 2);
  let startPage = Math.max(1, currentPage.value - halfVisible);
  let endPage = Math.min(totalPages.value, startPage + maxVisiblePages - 1);
  
  if (endPage === totalPages.value) {
    startPage = Math.max(1, endPage - maxVisiblePages + 1);
  }
  
  return Array.from({ length: endPage - startPage + 1 }, (_, i) => startPage + i);
});

const displayedItemsStart = computed(() => {
  if (filteredItems.value.length === 0) return 0;
  return (currentPage.value - 1) * itemsPerPage.value + 1;
});

const displayedItemsEnd = computed(() => {
  return Math.min(currentPage.value * itemsPerPage.value, filteredItems.value.length);
});

const changePage = (page: number) => {
  if (page < 1 || page > totalPages.value) return;
  currentPage.value = page;
};

const formatDate = (dateString: string) => {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('fr-FR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(date);
};

const validateUrl = (url: string): boolean => {
  const urlRegex = /^(https?:\/\/)([\w.-]+)\.([a-z]{2,})(:\d{1,5})?(\/.*)?$/i;
  
  if (!url) {
    return false;
  }
  
  if (url.length > 200) {
    return false;
  }
  
  return urlRegex.test(url);
};

const loadPlatforms = () => {
  isLoading.value = true;
  
  entityStore.fetchPlatforms(entityId.value)
    .then(data => {
      // idMapping.value.clear();
      // nextMappedId = 1;

      platforms.value = data.map((platform: Platform) => ({
        ...platform,
        mappedId: getMappedId(platform.id)
      }));
    })
    .catch(error => {
      entityStore.showToast('Error loading platforms', 'error');
    })
    .finally(() => {
      isLoading.value = false;
    });
};

const openEditModal = (platform: PlatformWithMappedId) => {
  editPlatform.value = { 
    id: platform.id, 
    url: platform.url,
    is_active: platform.is_active
  };
  validationErrors.value.editUrl = '';
};

const confirmTogglePlatform = (platform: PlatformWithMappedId) => {
  platformToToggle.value = platform;
  toggleModal.show();
};

const togglePlatformStatus = () => {
  if (!platformToToggle.value) return;
  
  isSubmitting.value = true;
  
  entityStore.togglePlatformStatus(platformToToggle.value.id)
    .then(() => {
      toggleModal.hide();
      cleanupModal();
      
      loadPlatforms();
      entityStore.showToast(`Plateforme ${platformToToggle.value.is_active ? 'deactivated' : 'activated'} successfully `, 'success');
     
    })
    .catch(error => {
      if (error.response?.data?.error) {
        entityStore.showToast(error.response.data.error, 'error');
      } else {
        entityStore.showToast('Error while changing platform status', 'error');
      }
    })
    .finally(() => {
      isSubmitting.value = false;
    });
};

const createPlatform = () => {
  validationErrors.value.url = '';
  
  if (!newPlatform.value.url) {
    validationErrors.value.url = 'URL is required';
    return;
  }
  
  if (!validateUrl(newPlatform.value.url)) {
    validationErrors.value.url = 'URL is not valid';
    return;
  }
  
  isSubmitting.value = true;
  
  const platformData = {
    url: newPlatform.value.url,
    is_active: newPlatform.value.is_active,
    entity: entityId.value
  };
  
  entityStore.createPlatform(platformData)
    .then(() => {
      entityStore.showToast('Plateform created successfully', 'success');
      
      newPlatform.value = {
        url: '',
        is_active: true
      };
      
      platformModal.hide();
      cleanupModal();
      
      loadPlatforms();
    })
    .catch(error => {
      if (error.response?.data?.error) {
        validationErrors.value.url = error.response.data.error;
        entityStore.showToast(error.response.data.error, 'error');
      } else {
        entityStore.showToast('Error while creating platform', 'error');
      }
    })
    .finally(() => {
      isSubmitting.value = false;
    });
};

const updatePlatform = () => {
  validationErrors.value.editUrl = '';
  
  if (!editPlatform.value.url) {
    validationErrors.value.editUrl = 'URL is required';
    return;
  }
  
  if (!validateUrl(editPlatform.value.url)) {
    validationErrors.value.editUrl = 'URL is not valid';
    return;
  }
  
  isSubmitting.value = true;
  
  const platformData = {
    url: editPlatform.value.url,
    is_active: editPlatform.value.is_active,
    entity: entityId.value
  };
  
  entityStore.updatePlatform(editPlatform.value.id, platformData)
    .then(() => {
      entityStore.showToast('Platform updated successfully', 'success');
      
      platformUpdateModal.hide();
      cleanupModal();
      
      loadPlatforms();
    })
    .catch(error => {
      if (error.response && error.response?.data?.error) {
        validationErrors.value.editUrl = error.response.data.error;
        entityStore.showToast(error.response.data.error, 'error');
      } else {
        entityStore.showToast('Errror while updating platform', 'error');
      }
    })
    .finally(() => {
      isSubmitting.value = false;
    });
};

const deletePlatform = () => {
  if (!platformToDelete.value) return;
  
  isSubmitting.value = true;
  
  entityStore.deletePlatform(platformToDelete.value.id)
    .then(() => {
      entityStore.showToast('Platform deleted successfuly', 'success');
      
      deleteModal.hide();
      cleanupModal();
      
      loadPlatforms();
    })
    .catch(error => {
      if (error.response?.data?.error) {
        entityStore.showToast(error.response.data.error, 'error');
      } else {
        entityStore.showToast('Error while deleting platform', 'error');
      }
    })
    .finally(() => {
      isSubmitting.value = false;
    });
};

watch(entityId, () => {
  if (entityId.value) {
    loadPlatforms();
  }
});

onMounted(() => {
  if (entityId.value) {
    loadPlatforms();
  }
  
  initModals();
});
</script>

<style scoped>
.table-src-form {
  position: relative;
}

.table-src-form input {
  padding-left: 2.5rem;
  border-radius: 0.375rem;
  border: 1px solid #dee2e6;
}

.table-src-form i {
  left: 0.75rem;
  color: #6c757d;
}

.default-table-area {
  --bs-table-hover-bg: rgba(0, 0, 0, 0.02);
}

.table {
  margin-bottom: 0;
}

.table th {
  font-weight: 600;
  color: #495057;
  border-bottom-width: 1px;
  padding: 0.75rem 1rem;
}

.table td {
  color: #6c757d;
  padding: 0.75rem 1rem;
  border-color: #f8f9fa;
}

.pagination {
  margin-bottom: 0;
}

.pagination .page-item .page-link {
  border-radius: 0.25rem;
  margin: 0 0.125rem;
  color: #6c757d;
}

.pagination .page-item .page-link.active {
  background-color: #0d6efd;
  border-color: #0d6efd;
  color: white;
}

.invalid-feedback {
  display: block;
  font-size: 0.75rem;
}
</style>