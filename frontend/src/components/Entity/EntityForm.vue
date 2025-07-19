<template>
  <div class="modal fade" id="entityModal" tabindex="-1" aria-labelledby="entityModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered modal-lg">
      <div class="modal-content">
        <div class="modal-header" :class="{'background-modal': !isEditing, 'bg-primary text-white': isEditing}">
          <h1 class="modal-title fs-5 mb-1" id="entityModalLabel">
            {{ isEditing ? 'Edit entity' : 'Add Entity' }}
          </h1>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" @click="resetForm"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <div class="form-group mb-3">
              <label class="form-label">Entity Name <span class="text-danger">*</span></label>
              <input
                type="text"
                class="form-control form-control-sm"
                v-model="formData.name"
                placeholder="Enter entity name"
                :class="{'is-invalid': validationErrors.name}"
              />
              <div class="invalid-feedback" v-if="validationErrors.name">
                {{ validationErrors.name }}
              </div>
            </div>
    
            <div class="form-group mb-3">
              <label class="form-label">Description <span class="text-danger">*</span></label>
              <textarea
                rows="2"
                class="form-control form-control-sm"
                v-model="formData.description"
                placeholder="Enter an description"
                :class="{'is-invalid': validationErrors.description}"
                maxlength="255"
              ></textarea>
              <div class="invalid-feedback" v-if="validationErrors.description">
                {{ validationErrors.description }}
              </div>
            </div>

            <div class="mb-3">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <label class="form-label mb-0">Focal Points</label>
                <button 
                  type="button"
                  class="btn btn-sm btn-outline-primary" 
                  @click="addAssociation"
                >
                  <i class="ri-add-line me-1"></i> Add
                </button>
              </div>
              
              <div v-if="formData.associations.length === 0" class="alert alert-light py-2 text-center">
                <small class="text-muted">No focal point found</small>
              </div>
              
              <div v-for="(assoc, index) in formData.associations" :key="index" class="association-row mb-2 p-2 border rounded">
                <div class="row g-2 align-items-end">
                  <div class="col-5">
                    <label class="form-label small text-muted mb-1">Function <span class="text-danger">*</span></label>
                    <select 
                      class="form-select form-select-sm"
                      v-model="assoc.function"
                      @change="onFunctionChange(assoc)"
                      :class="{'is-invalid': assoc.errors.function}"
                    >
                      <option value="" disabled>Select</option>
                      <option 
                        v-for="func in functions" 
                        :key="func ? func.id : 'null'" 
                        :value="func"
                      >
                        {{ func?.name }}
                      </option>
                    </select>
                    <div class="invalid-feedback" v-if="assoc.errors.function">
                      {{ assoc.errors.function }}
                    </div>
                  </div>
                  
                  <div class="col-5">
                    <label class="form-label small text-muted mb-1">Focal Point <span class="text-danger">*</span></label>
                    <select 
                      class="form-select form-select-sm"
                      v-model="assoc.focalPoint"
                      :disabled="!assoc.function || assoc.availableFocalPoints.length === 0"
                      @change="onFocalPointChange(assoc)"
                      :class="{'is-invalid': assoc.errors.focalPoint}"
                    >
                      <option value="" disabled>
                        {{ !assoc.function ? 'Sélect a function' : 
                           (assoc.availableFocalPoints.length === 0 ? 'No focal point available' : 'Select') 
                        }}
                      </option>
                      <option 
                        v-for="fp in assoc.availableFocalPoints" 
                        :key="fp.id" 
                        :value="fp"
                        :disabled="!fp.is_active"
                      >
                        {{ fp.full_name }} ({{ fp.is_active ? 'Enable' : 'Disable' }})
                      </option>
                    </select>
                    <div class="invalid-feedback" v-if="assoc.errors.focalPoint">
                      {{ assoc.errors.focalPoint }}
                    </div>
                  </div>
                  
                  <div class="col-2 text-end pb-1">
                    <button 
                      type="button" 
                      class="btn btn-sm btn-outline-danger btn-sm py-1"
                      @click="removeAssociation(index)"
                      title="Delete"
                    >
                      <i class="ri-delete-bin-line"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
  
            <div class="modal-footer">
              <button type="button" class="btn btn-sm btn-danger text-white" data-bs-dismiss="modal" @click="resetForm">Cancel</button>
              <button 
                type="submit" 
                class="btn btn-sm btn-primary text-white"
                :disabled="isSubmitting || !authStore.hasPermission('entities_edit')"
              >
                <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                {{ isEditing ? 'Update' : 'Submit' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent, ref, reactive, computed, watch, onMounted } from 'vue'
  import { useEntityStore } from '@/stores/entityStore'
  import { useFocalPointStore } from '@/stores/EntityFocalStore'
  import type { Entity, FocalPoint, FocalFunction } from '@/types/entity.types'
  import { useAuthStore } from '@/stores/auth.store';
  
  
  interface Association {
    function: FocalFunction | null
    focalPoint: FocalPoint | null
    availableFocalPoints: FocalPoint[]
    errors: {
      function: string
      focalPoint: string
    }
  }
  
  export default defineComponent({
    name: 'EntityForm',
    props: {
      entityToEdit: {
        type: Object as () => Entity | null,
        default: null
      }
    },
    setup(props, { emit }) {
      const entityStore = useEntityStore()
      const focalPointStore = useFocalPointStore()
      const authStore = useAuthStore();
  
      const functions = ref<FocalFunction[]>([])
      const allFocalPoints = ref<FocalPoint[]>([])
      const isSubmitting = ref(false)
      const isLoading = ref(true)
      

      const formData = reactive({
        name: '',
        description: '',
        associations: [] as Association[]
      })
  
      const validationErrors = reactive({
        name: '',
        description: ''
      })
  
      const isEditing = computed(() => !!props.entityToEdit)
      
       const closeModal = () => {
          const modalEl = document.getElementById('entityModal')!
          const bsModal = (window as any).bootstrap.Modal.getOrCreateInstance(modalEl)
          bsModal.hide()
          setTimeout(() => {
            document.querySelectorAll('.modal-backdrop').forEach(el => el.remove())
            document.body.classList.remove('modal-open')
            document.body.style.overflow = ''
            document.body.style.paddingRight = ''
          }, 0)
      }
  

      const loadInitialData = async () => {
          isLoading.value = true
          try {
            functions.value = await focalPointStore.fetchFunctions()
            allFocalPoints.value = await focalPointStore.fetchActiveFocalPoints()
          } catch (error) {
            console.error('Error loading initial data:', error)
            functions.value = []
            allFocalPoints.value = []
          } finally {
            isLoading.value = false
          }
        }
  
      const onFunctionChange = (assoc: Association) => {
        
        assoc.focalPoint = null
        
        if (assoc.function && assoc.function.id) {
          assoc.availableFocalPoints = allFocalPoints.value.filter(
            fp => fp.function === assoc.function?.id && fp.is_active
          )
        } else {
          assoc.availableFocalPoints = []
        }
  
        assoc.errors.function = assoc.function ? '' : 'Function is required'
      }
  
      const onFocalPointChange = (assoc: Association) => {
        assoc.errors.focalPoint = assoc.focalPoint ? '' : 'Focal point is required'
      }
  
      const addAssociation = () => {
        formData.associations.push({
          function: null,
          focalPoint: null,
          availableFocalPoints: [],
          errors: {
            function: '',
            focalPoint: ''
          }
        })
      }
  
      const removeAssociation = (index: number) => {
        formData.associations.splice(index, 1)
      }
  
      const validate = (): boolean => {
        let isValid = true
  
        validationErrors.name = ''
        validationErrors.description = ''
        formData.associations.forEach(assoc => {
          assoc.errors.function = ''
          assoc.errors.focalPoint = ''
        })
  
        if (!formData.name.trim()) {
          validationErrors.name = 'Entity name is required'
          isValid = false
        } else if (formData.name.length < 2 || formData.name.length > 255) {
          validationErrors.name = 'The name must be between 2 and 255 characters long'
          isValid = false
        }
  
        if (!formData.description || !formData.description.trim()) {
          validationErrors.description = 'The description is required'
          isValid = false
        } else if (formData.description.length > 254) {
          validationErrors.description = 'Description cannot exceed 254 characters'
          isValid = false
        }
  
        if (formData.associations.length === 0) {
          addAssociation()
          formData.associations[0].errors.function = 'At least one focal point is required'
          isValid = false
        } else {
          formData.associations.forEach(assoc => {
            if (!assoc.function) {
              assoc.errors.function = 'Function is required'
              isValid = false
            }
  
            if (!assoc.focalPoint) {
              assoc.errors.focalPoint = 'Focal point is required'
              isValid = false
            }
          })
        }
  
        return isValid
      }

      const handleSubmit = () => {
        if (!validate()) {
          return
        }
  
        isSubmitting.value = true
  
        const submissionData: Partial<Entity> = {
          name: formData.name.trim(),
          description: formData.description.trim(),
          focal_points_ids: formData.associations
            .map(assoc => assoc.focalPoint?.id)
            .filter(Boolean) as string[]
        }
  
        const submitPromise = props.entityToEdit
          ? entityStore.updateEntity(props.entityToEdit.id, submissionData)
          : entityStore.createEntity(submissionData)
  
        submitPromise
          .then(entity => {
            if (entity) {
              resetForm()
              
              closeModal()
            }
          })
          .catch(error => {
            entityStore.showToast('Error submitting entity', 'error')
          })
          .finally(() => {
            isSubmitting.value = false
          })
      }
  
      const resetForm = () => {
        formData.name = ''
        formData.description = ''
        formData.associations = []
        validationErrors.name = ''
        validationErrors.description = ''
  
        addAssociation()
  
        emit('cancel')
      }
  
      watch(() => props.entityToEdit, (newEntity) => {
        if (newEntity && !isLoading.value) {
          formData.name = newEntity.name || ''
          formData.description = newEntity.description || ''
          formData.associations = []
  
          if (newEntity.focal_points && newEntity.focal_points.length > 0) {
            newEntity.focal_points.forEach(fp => {
              const fpFunction = functions.value.find(f => f && f.id === fp.function)
              
              if (fpFunction) {
                const association: Association = {
                  function: fpFunction,
                  focalPoint: fp,
                  availableFocalPoints: allFocalPoints.value.filter(
                    availableFp => availableFp.function === fpFunction.id && availableFp.is_active
                  ),
                  errors: {
                    function: '',
                    focalPoint: ''
                  }
                }
                formData.associations.push(association)
              }
            })
          }
  
          if (formData.associations.length === 0) {
            addAssociation()
          }
        } else if (!newEntity) {
          resetForm()
        }
      }, { immediate: true })
  
      onMounted(loadInitialData)
  
      return {
        formData,
        validationErrors,
        functions,
        isEditing,
        isSubmitting,
        isLoading,
        addAssociation,
        removeAssociation,
        onFunctionChange,
        onFocalPointChange,
        handleSubmit,
        resetForm,
        validate,
        authStore
      }
    }
  })
  </script>
  
<style scoped>
.background-modal {
  background-color: #f8f9fa;
}

.modal-header {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.modal-footer {
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.form-control:focus, .form-select:focus {
  border-color: #1976d2;
  box-shadow: 0 0 0 0.2rem rgba(25, 118, 210, 0.25);
}

.invalid-feedback {
  display: block;
  font-size: 0.75rem;
}

.association-row {
  background-color: #f8f9fa;
  border-left: 3px solid #1976d2 !important;
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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
  font-size: 0.9rem;
}

.cursor-pointer {
  cursor: pointer;
}
</style>