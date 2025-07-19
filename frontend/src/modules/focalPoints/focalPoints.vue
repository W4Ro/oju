<template>
  <div class="main-content-container overflow-hidden">
    <PageTitle pageTitle="Points" subTitle="Focal" />
  </div>
  <div class="main-content-container overflow-hidden">
    <div class="card bg-white border-0 rounded-3 mb-4">
      <div class="card-body p-0">
        <div class="p-4">
          <div class="d-flex justify-content-between align-items-center flex-wrap gap-3">
            <form class="position-relative table-src-form me-0" @submit.prevent>
              <input
                type="text"
                class="form-control"
                placeholder="Search a focal point"
                v-model="searchTerm"
              />
              <i
                class="material-symbols-outlined position-absolute top-50 start-0 translate-middle-y"
              >
                search
              </i>
            </form>
            <button
              class="btn btn-outline-primary text-primary py-1 px-2 px-sm-4 fs-14 fw-medium rounded-3 hover-bg"
              @click="openSidePanel()"
              v-if="hasPermission('focal_points_create')"
            >
              <span class="py-sm-1 d-block">
                <i class="ri-add-line me-1"></i>
                <span>New focal point</span>
              </span>
            </button>
          </div>
        </div>

        <div class="default-table-area style-two padding-style">
          <div class="table-responsive">
            <table class="table align-middle">
              <thead>
                <tr>
                  <th scope="col">ID</th>
                  <th scope="col">Full name</th>
                  <th scope="col">Phone numbers</th>
                  <th scope="col">Email</th>
                  <th scope="col">Function</th>
                  <th scope="col">Status</th>
                  <th scope="col">Creation date</th>
                  <th scope="col">Last modified</th>
                  <th scope="col">Actions</th>
                </tr>
              </thead>
              <tbody v-if="loading">
                <tr>
                  <td colspan="9" class="text-center py-4">
                    <div class="spinner-border text-primary" role="status">
                      <span class="visually-hidden">Loading...</span>
                    </div>
                  </td>
                </tr>
              </tbody>
              <tbody v-else-if="paginatedFocalPoints.length">
                <tr v-for="point in paginatedFocalPoints" :key="point.id">
                  <td class="text-body">
                    {{ point.displayId || (focalPointStores.getSequentialIdFromUuid?.(point.id)) || point.id }}
                  </td>
                  <td>{{ point.full_name }}</td>
                  <td>
                    <div class="content-truncate" style="max-width: 150px;">
                      {{ point.phone_number.join(', ') }}
                      <div class="tooltip-content">{{ point.phone_number.join(', ') }}</div>
                    </div>
                  </td>
                  <td>{{ point.email }}</td>
                  <td>{{ point.function_name }}</td>
                  <td>
                    <span
                      class="badge bg-opacity-10 p-2 fs-12 fw-normal"
                      :class="point.is_active ? 'text-success' : 'text-danger'"
                    >
                      {{ point.is_active ? 'Active' : 'Inactive' }}
                    </span>
                  </td>
                  <td class="text-body">{{ formatDate(point.created_at) }}</td>
                  <td class="text-body">{{ formatDate(point.updated_at) }}</td>
                  <td>
                    <div class="d-flex align-items-center gap-1">
                      <button
                        v-if="hasPermission('focal_points_edit')"
                        class="ps-0 border-0 bg-transparent lh-1 position-relative top-2"
                        @click="openSidePanel(point)"
                      >
                        <i class="material-symbols-outlined fs-16 text-primary">edit</i>
                      </button>
                      <button
                        v-if="hasPermission('focal_points_toggle')"
                        class="ps-0 border-0 bg-transparent lh-1 position-relative top-2"
                        @click="toggleStatus(point)"
                        title="Change status"
                      >
                        <i
                          class="material-symbols-outlined fs-16"
                          :class="point.is_active ? 'text-success' : 'text-danger'"
                        >
                          {{ point.is_active ? 'toggle_on' : 'toggle_off' }}
                        </i>
                      </button>
                      <button
                        class="ps-0 border-0 bg-transparent lh-1 position-relative top-2"
                        @click="confirmDelete(point)"
                        v-if="hasPermission('focal_points_delete')"
                      >
                        <i class="material-symbols-outlined fs-16 text-danger">delete</i>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
              <tbody v-else>
                <tr>
                  <td colspan="9" class="text-center py-4">
                    No focal point found
                  </td>
                </tr>
              </tbody>
            </table>


            <div class="p-4">
              <Pagination 
                :total="totalFocalPoints" 
                :perPage="itemsPerPage" 
                v-model="currentPage" 
                @page-change="handlePageChange" 
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="offcanvas offcanvas-end" tabindex="-1" id="focalPointSidePanel" aria-labelledby="focalPointSidePanelLabel" ref="sidePanel">
      <div class="offcanvas-header border-bottom">
        <h5 class="offcanvas-title" id="focalPointSidePanelLabel">{{ isEditing ? 'Modify' : 'Create' }} a focal point</h5>
        <button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>
      </div>
      <div class="offcanvas-body">
        <form @submit.prevent="validateAndSave">
          <div class="mb-4">
            <label for="full-name" class="form-label fw-medium">Full name <span class="text-danger">*</span></label>
            <input 
              type="text" 
              class="form-control" 
              :class="{'is-invalid': errors.full_name}" 
              id="full-name" 
              v-model="focalPointForm.full_name" 
              @input="validateFullName" 
              required
            >
            <div class="invalid-feedback" v-if="errors.full_name">
              {{ errors.full_name }}
            </div>
          </div>
          
          <div class="mb-4">
            <label for="email" class="form-label fw-medium">Email <span class="text-danger">*</span></label>
            <input 
              type="email" 
              class="form-control" 
              :class="{'is-invalid': errors.email}" 
              id="email" 
              v-model="focalPointForm.email" 
              @input="validateEmail" 
              required
            >
            <div class="invalid-feedback" v-if="errors.email">
              {{ errors.email }}
            </div>
          </div>
          
          <div class="mb-4">
            <label for="function" class="form-label fw-medium">Function <span class="text-danger">*</span></label>
            <Multiselect
              v-model="focalPointForm.function"
              :options="functionOptions"
              label="label"
              track-by="value"
              :reduce="opt => opt.value"
              placeholder="Select a function"
              :class="{ 'is-invalid': errors.function_id }"
              @input="errors.function_id = ''"
            />
            <div class="invalid-feedback d-block" v-if="errors.function_id">
              {{ errors.function_id }}
            </div>
          </div> 
          
          <div class="mb-4">
            <label class="form-label fw-medium">Phone numbers</label>
            <div class="mb-3" v-for="(phone, index) in phoneInputs" :key="index">
              <div class="d-flex align-items-start gap-2">
                <div class="flex-grow-1">
                  <VueTelInput
                    v-model="phone.number"
                    :defaultCountry="phone.country"
                    @validate="(data) => updatePhoneValidity(index, data)"
                    :enabledFlags="true"
                    :disabledFetchingCountry="false"
                    :validCharactersOnly="false"
                    :mode="'international'"
                    :autoDefaultCountry="true"
                    :inputClasses="{'is-invalid': errors.phone && errors.phone[index]}"
                    :dropdownOptions="{ showDialCodeInSelection: true, showFlags: true }"
                    :ignoredCountries="[]"
                    :wrapperClasses="'vue-tel-input-custom'"
                  />
                  <div class="text-danger small mt-1" v-if="errors.phone && errors.phone[index]">
                    {{ errors.phone[index] }}
                  </div>
                </div>
                <button 
                  v-if="index > 0" 
                  type="button" 
                  class="btn btn-outline-danger d-flex align-items-center"
                  style="height: 38px; margin-top: 0;"
                  @click="removePhoneInput(index)"
                >
                  <i class="material-symbols-outlined">delete</i>
                </button>
              </div>
            </div>
            <button type="button" class="btn btn-outline-primary btn-sm mt-1" @click="addPhoneInput">
              <i class="material-symbols-outlined align-middle me-1">add</i> Add a number
            </button>
          </div>
          
          <div class="mb-4">
            <label class="form-label fw-medium">Status</label>
            <div class="form-check form-switch">
              <input class="form-check-input" type="checkbox" role="switch" id="status-switch" v-model="focalPointForm.is_active">
              <label class="form-check-label" for="status-switch">{{ focalPointForm.is_active ? 'Active' : 'Inactive' }}</label>
            </div>
          </div>
          
          <div class="d-flex justify-content-end gap-2 border-top pt-3 mt-4">
            <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="offcanvas">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="formHasErrors || isSubmitting">
              <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
              {{ isEditing ? 'Update' : 'Create' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div class="modal fade" id="deleteModal" tabindex="-1" aria-hidden="true" ref="deleteModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Confirm deletion</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to delete the focal point <strong>{{ focalPointToDelete?.full_name }}</strong> ?</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-danger" @click="deleteFocalPoint" :disabled="isSubmitting">
              <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <Toast 
      v-if="focalPointStores.toast"
      :show="focalPointStores.toast.show" 
      :message="focalPointStores.toast.message" 
      :type="focalPointStores.toast.type" 
      :autoClose="true"
      :duration="focalPointStores.toast.duration"
      @close="handleToastClose" 
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import { Modal, Offcanvas } from 'bootstrap';
import Multiselect from '@vueform/multiselect';
import { VueTelInput } from 'vue-tel-input';
import 'vue-tel-input/vue-tel-input.css';
import '@vueform/multiselect/themes/default.css';
import { FocalPoint, FocalPointCreate, FocalPointUpdate, FocalPointFormErrors, PhoneInput } from '@/types/focalPoint.types';
import { useFocalPointStores } from '@/stores/focalPoint.store';
import { useFocalFunctionStore } from '@/stores/focalFunction.store';
import PageTitle from "@/components/Common/PageTitle.vue";
import Pagination from "@/components/Common/Pagination.vue";
import Toast from "@/components/Common/Toast.vue";
import {hasPermission, hasAnyPermission} from "@/utils/permissions";



const focalPointStores = useFocalPointStores();
const focalFunctionStore = useFocalFunctionStore();

const route = useRoute();
const functionId = ref(route.params.id as string || null);

const searchTerm = ref('');

const currentPage = ref(1);
const itemsPerPage = ref(20);


const loading = computed(() => focalPointStores.loading || focalFunctionStore.loading);
const totalFocalPoints = computed(() => {
  return filteredFocalPoints.value ? filteredFocalPoints.value.length : 0;
});

const paginatedFocalPoints = computed(() => {
  if (!filteredFocalPoints.value) {
    return [];
  }
  
  const start = (currentPage.value - 1) * itemsPerPage.value;
  return filteredFocalPoints.value.slice(start, start + itemsPerPage.value);
});

const sidePanel = ref<HTMLElement | null>(null);
const deleteModal = ref<HTMLElement | null>(null);
const isEditing = ref(false);
const focalPointToDelete = ref<FocalPoint | null>(null);
const isSubmitting = ref(false);

const errors = ref<FocalPointFormErrors>({
  full_name: '',
  email: '',
  function_id: '',
  phone: []
});

const functionOptions = computed(() => {
  return focalFunctionStore.focalFunctions.map(func => ({
    label: func.name,
    value: func.id
  }));
});

const selectedFunction = ref<{label: string, value: string} | null>(null);

const focalPointForm = ref<FocalPointUpdate>({
  id: '',
  full_name: '',
  email: '',
  function_id: '',
  phone_number: [],
  is_active: true
});

const formHasErrors = computed(() => {
  if (errors.value.full_name || errors.value.email || errors.value.function) {
    return true;
  }
  
  if (errors.value.phone && errors.value.phone.some(error => error !== '')) {
    return true;
  }
  
  if (!focalPointForm.value.full_name || !focalPointForm.value.email || !focalPointForm.value.function) {
    return true;
  }
  
  return false;
});

const phoneInputs = ref<PhoneInput[]>([{ country: 'BJ', number: '', isValid: false }]);

const filteredFocalPoints = computed(() => {
  if (!Array.isArray(focalPointStores.focalPoints)) {
    return [];
  }
  
  if (!searchTerm.value.trim()) {
    return focalPointStores.focalPoints;
  }
  
  const term = searchTerm.value.toLowerCase();
  return focalPointStores.focalPoints.filter(point => 
    point.full_name.toLowerCase().includes(term) || 
    point.email.toLowerCase().includes(term) || 
    point.function_name.toLowerCase().includes(term) ||
    point.phone_number.some(phone => phone.toLowerCase().includes(term))
  );
});

const validateFullName = () => {
  const value = focalPointForm.value.full_name;
  
  if (!value.trim()) {
    errors.value.full_name = 'Full name is required';
  } else {
    errors.value.full_name = '';
  }
};

const validateEmail = () => {
  const value = focalPointForm.value.email;
  const validEmailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  
  if (!value.trim()) {
    errors.value.email = 'Email is required';
  } else if (!validEmailRegex.test(value)) {
    errors.value.email = 'Enter a valid email address';
  } else {
    errors.value.email = '';
  }
};


const validateFunction = () => {
  if (selectedFunction.value) {
    focalPointForm.value.function_id = selectedFunction.value.value;
    errors.value.function_id = '';
    return;
  }
  
  if (focalPointForm.value.function_id) {
    const foundFunction = functionOptions.value.find(
      option => option.value === focalPointForm.value.function_id
    );
    
    if (foundFunction) {
      selectedFunction.value = foundFunction;
      errors.value.function_id = '';
      return;
    }
  }
  
  errors.value.function_id = 'Function is required';
};

const toggleStatus = async (point: FocalPoint) => {
  try {
    await focalPointStores.toggleFocalPointStatus(point.id, !point.is_active);
  } catch (error) {
    console.error('Error switching status:', error);
  }
};

const handlePageChange = (page: number) => {
  currentPage.value = page;
};

const confirmDelete = (focalPoint: FocalPoint) => {
  focalPointToDelete.value = focalPoint;
  new Modal(deleteModal.value as HTMLElement).show();
};

const deleteFocalPoint = async () => {
  if (!focalPointToDelete.value) return;
  
  isSubmitting.value = true;
  try {
    await focalPointStores.deleteFocalPoint(focalPointToDelete.value.id);
    
    Modal.getInstance(deleteModal.value as HTMLElement)?.hide();
  } catch (error) {
    console.error('Error deleting focal point:', error);
  } finally {
    isSubmitting.value = false;
  }
};

const updatePhoneValidity = (index: number, event: any) => {
  if (!errors.value.phone) {
    errors.value.phone = Array(phoneInputs.value.length).fill('');
  }

  const isValid = event?.valid || false;

  const phoneValue = event?.number || phoneInputs.value[index].number || '';

  if (!phoneValue || phoneValue.trim() === '') {
    errors.value.phone[index] = '';
    phoneInputs.value[index].isValid = false;
    return;
  }

  if (!isValid) {
    errors.value.phone[index] = 'Invalid phone number';
    phoneInputs.value[index].isValid = false;
  } else {
    errors.value.phone[index] = '';
    phoneInputs.value[index].number = phoneValue;
    phoneInputs.value[index].isValid = true;
  }

  if (event?.country) {
    phoneInputs.value[index].country = event.country?.iso2 || 'BJ';
  }

  errors.value = { ...errors.value, phone: [...errors.value.phone] };
};

const addPhoneInput = () => {
  phoneInputs.value.push({ country: 'BJ', number: '', isValid: false });
  if (!errors.value.phone) {
    errors.value.phone = [];
  }
  errors.value.phone.push('');
  errors.value.phone = [...errors.value.phone];
};

const removePhoneInput = (index: number) => {
  phoneInputs.value.splice(index, 1);
  if (errors.value.phone) {
    errors.value.phone.splice(index, 1);
    errors.value.phone = [...errors.value.phone];
  }
};

const formatDate = (dateString: string) => {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
};


const openSidePanel = (focalPoint: FocalPoint | null = null) => {
  resetForm();
  
  if (focalPoint) {
    isEditing.value = true;
    focalPointForm.value = {
      id: focalPoint.id,
      full_name: focalPoint.full_name,
      email: focalPoint.email,
      function: focalPoint.function,
      function_id: focalPoint.function_id,
      phone_number: [],
      is_active: focalPoint.is_active
    };
    
    
    const functionOption = functionOptions.value.find(option => option.value === focalPoint.function);

    selectedFunction.value = functionOption || null;
    
    if (!functionOption && focalPoint.function) {
      const fetchFunction = async () => {
        try {
          const func = await focalFunctionStore.getFocalFunction(focalPoint.function);
          if (func) {
            const newOption = {
              label: func.name,
              value: func.id
            };
            
            selectedFunction.value = newOption;
          }
        } catch (error) {
          console.error('Error retrieving function:', error);
        }
      };
      
      fetchFunction();
    }
    
    phoneInputs.value = focalPoint.phone_number.map(phoneStr => {
      return { country: 'auto', number: phoneStr, isValid: true };
    });
    
    if (phoneInputs.value.length === 0) {
      phoneInputs.value = [{ country: 'BJ', number: '', isValid: false }];
    }
    
    errors.value.phone = Array(phoneInputs.value.length).fill('');
    
    validateFunction();
  } else {
    isEditing.value = false;
    
    if (functionId.value) {
      focalPointForm.value.function_id = functionId.value;
      focalPointForm.value.function = functionId.value;
      const functionOption = functionOptions.value.find(option => option.value === functionId.value);
      selectedFunction.value = functionOption || null;
      validateFunction();
    }
  }
  
  

  new Offcanvas(sidePanel.value as HTMLElement).show();
};

const resetForm = () => {
  focalPointForm.value = {
    id: '',
    full_name: '',
    email: '',
    function_id: functionId.value || '',
    function: functionId.value || '',
    phone_number: [],
    is_active: true
  };
  
  if (functionId.value) {
    const functionOption = functionOptions.value.find(option => option.value === functionId.value);
    selectedFunction.value = functionOption || null;
  } else {
    selectedFunction.value = null;
  }
  
  phoneInputs.value = [{ country: 'BJ', number: '', isValid: false }];
  
  errors.value = {
    full_name: '',
    email: '',
    function_id: '',
    phone: Array(phoneInputs.value.length).fill('')
  };
};

const validateAndSave = async () => {
  isSubmitting.value = true;
  
  validateFullName();
  validateEmail();
  validateFunction();
  
  if (formHasErrors.value) {
    isSubmitting.value = false;
    return;
  }
  
  await saveFocalPoint();
  
  isSubmitting.value = false;
};

const saveFocalPoint = async () => {
  try {
    const phoneNumbers = phoneInputs.value
      .filter(p => p.isValid && p.number.trim() !== '')
      .map(p => p.number);

    const focalPointData: FocalPointCreate | FocalPointUpdate = {
      ...focalPointForm.value,
      phone_number: phoneNumbers
    };

    if (isEditing.value) {
      await focalPointStores.updateFocalPoint(focalPointForm.value.id, focalPointData as FocalPointUpdate);
    } else {
      await focalPointStores.createFocalPoint(focalPointData as FocalPointCreate);
    }

    Offcanvas.getInstance(sidePanel.value as HTMLElement)?.hide();
  } catch (error) {
    console.error("Error saving focal point:", error);
  }
};

function handleToastClose() {
  focalPointStores.toast.show = false;
}
const fetchFocalPoints = async () => {
  try {
    await focalFunctionStore.fetchFocalFunctions();
    if (!functionId.value) {
      focalPointStores.functionId = null;
    }
    await focalPointStores.fetchFocalPoints(1, true, functionId.value || undefined);
  } catch (error) {
    console.error('Error loading focal points:', error);
  }
};
watch(() => route.params.id, () => {
  currentPage.value = 1
  fetchFocalPoints()
}, { immediate: true })

watch(() => route.fullPath, (newPath, oldPath) => {
  if (newPath === '/focal-points' && oldPath.includes('/focal-points/function/')) {
    functionId.value = null;
    fetchFocalPoints();
  }
});

watch(selectedFunction, (newValue) => {
  if (newValue) {
    focalPointForm.value.function_id = newValue.value;
    errors.value.function_id = ''; 
  } else {
    focalPointForm.value.function_id = '';
  }
  
  validateFunction();
}, { deep: true });

onMounted(() => {
  fetchFocalPoints();
});

watch(searchTerm, () => {
  currentPage.value = 1;
});
</script>

<style scoped>
.vue-tel-input {
  min-height: 38px;
}

.btn-outline-danger {
  height: 38px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.content-truncate {
  position: relative;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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

.offcanvas {
  width: 450px;
  max-width: 100%;
}

.offcanvas-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.offcanvas-title {
  font-weight: 600;
  color: #212529;
}

.offcanvas-body {
  padding: 1.5rem;
}

:deep(.multiselect) {
  min-height: 38px;
  border-radius: 0.375rem;
}

:deep(.multiselect-input) {
  padding: 0.375rem 0.75rem;
}

:deep(.multiselect-single-label) {
  padding: 0.375rem 0;
}

:deep(.multiselect-tags) {
  padding: 0.375rem 0;
}

:deep(.multiselect-tag) {
  background: #0d6efd;
  padding: 0.175rem 0.375rem;
}

:deep(.multiselect-options) {
  padding: 0;
  border-radius: 0.375rem;
  border-color: #dee2e6;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

:deep(.multiselect-option) {
  padding: 0.5rem 0.75rem;
}

:deep(.is-selected) {
  background: #0d6efd;
  color: white;
}

:deep(.is-pointed) {
  background: #e9ecef;
}

:deep(.multiselect.is-invalid) {
  border-color: #dc3545;
}

.form-label {
  font-weight: 500;
  color: #495057;
  margin-bottom: 0.5rem;
}

.invalid-feedback {
  font-size: 0.8rem;
}

.form-check-input:checked {
  background-color: #0d6efd;
  border-color: #0d6efd;
}

.form-switch .form-check-input {
  width: 2.5em;
  cursor: pointer;
}

.form-check-label {
  cursor: pointer;
}

.btn-primary {
  background-color: #0d6efd;
  border-color: #0d6efd;
}

.btn-outline-secondary {
  color: #6c757d;
  border-color: #6c757d;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
  border-width: 0.2em;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

.is-invalid {
  animation: shake 0.4s ease-in-out;
}

.badge.confirmed {
  background-color: rgba(25, 135, 84, 0.1);
  color: #198754;
}

.badge.rejected {
  background-color: rgba(108, 117, 125, 0.1);
  color: #6c757d;
}
</style>