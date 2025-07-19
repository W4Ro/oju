<template>
  <div>
    <Toast
      :show="roleStore.toast.show"
      :message="roleStore.toast.message"
      :type="roleStore.toast.type"
      :autoClose="true"
      :duration="roleStore.toast.duration"
      @close="handleToastClose"
    />
    <div class="card bg-white border-0 rounded-3 shadow-sm">
      <div class="card-header bg-white p-4 border-0">
        <div class="d-flex align-items-center">
          <button 
            class="btn btn-icon btn-light rounded-circle me-3"
            @click="router.push('/config/roles')"
          >
            <i class="ri-arrow-left-line"></i>
          </button>
          <h3 class="fs-18 fw-semibold mb-0">{{ isEditing ? 'Edit the role' : 'Create new role' }}</h3>
        </div>
      </div>
      
      <div v-if="loading" class="card-body p-4 text-center">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2">{{ isEditing ? 'Loading role data...' : 'Form initialisation...' }}</p>
      </div>
      
      <div v-else class="card-body p-4">
        <form @submit.prevent="saveRole">
          <div class="row mb-5">
            <div class="col-12">
              <h4 class="fs-16 fw-semibold mb-4 pb-2 border-bottom">Role informations</h4>
              
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-4">
                    <label for="role-name" class="form-label text-secondary fs-14">Role Name*</label>
                    <input
                      type="text"
                      id="role-name"
                      v-model="roleData.name"
                      class="form-control h-55"
                      :class="{ 'is-invalid': errors.name }"
                      placeholder="Example: Admin"
                      required
                    />
                    <div class="text-danger small mt-1" v-if="errors.name">{{ errors.name }}</div>
                  </div>
                </div>
                
                <div class="col-md-6">
                  <div class="mb-4">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                      <label class="form-label text-secondary fs-14 mb-0">Role statut</label>
                      <div class="form-check form-switch">
                        <input 
                          class="form-check-input" 
                          type="checkbox" 
                          role="switch"
                          id="role-status" 
                          v-model="roleData.is_active"
                        />
                        <label class="form-check-label" for="role-status">
                          {{ roleData.is_active ? 'Active' : 'Inactive' }}
                        </label>
                      </div>
                    </div>
                    <div class="alert alert-light border p-2 mb-0 h-55 d-flex align-items-center">
                      <small>
                        <i class="ri-information-line me-1"></i>
                        If the role is inactive, it will not be available for assignment to users.
                      </small>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="row">
                <div class="col-12">
                  <div class="mb-2">
                    <label for="role-description" class="form-label text-secondary fs-14">Description</label>
                    <textarea
                      id="role-description"
                      v-model="roleData.description"
                      class="form-control"
                      placeholder="Give role description..."
                      rows="3"
                      required
                    ></textarea>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="row mb-5">
            <div class="col-12">
              <div class="d-flex justify-content-between align-items-center mb-4">
                <h4 class="fs-16 fw-semibold mb-0">Permissions</h4>
                
                <div class="d-flex align-items-center">
                  <div class="input-group border rounded overflow-hidden search-input me-3" style="width: 250px;">
                    <span class="input-group-text bg-transparent border-0 py-0">
                      <i class="ri-search-line"></i>
                    </span>
                    <input
                      type="text"
                      class="form-control bg-transparent border-0 py-2"
                      placeholder="Search permissions..."
                      v-model="searchQuery"
                    />
                    <span
                      v-if="searchQuery"
                      class="input-group-text bg-transparent border-0 py-0 cursor-pointer"
                      @click="searchQuery = ''"
                    >
                      <i class="ri-close-line"></i>
                    </span>
                  </div>
                  
                  <div class="dropdown">
                    <button class="btn btn-outline-secondary dropdown-toggle" type="button" id="bulkActionDropdown" data-bs-toggle="dropdown" aria-expanded="false">
                      Actions
                    </button>
                    <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="bulkActionDropdown">
                      <li><button class="dropdown-item" type="button" @click="selectAllPermissions"><i class="ri-checkbox-multiple-line me-2"></i>Select all</button></li>
                      <li><button class="dropdown-item" type="button" @click="deselectAllPermissions"><i class="ri-checkbox-multiple-blank-line me-2"></i>Deselect all</button></li>
                      <li><hr class="dropdown-divider"></li>
                      <li v-for="feature in Object.keys(groupedPermissions)" :key="feature">
                        <button class="dropdown-item" type="button" @click="toggleFeaturePermissions(feature)">
                          {{ isFeatureFullySelected(feature) ? 'Désélectionner' : 'Sélectionner' }} {{ formatFeatureName(feature) }}
                        </button>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
              
              <div class="permission-stats bg-light p-3 rounded-3 mb-4">
                <div class="d-flex justify-content-between align-items-center">
                  <span class="fs-14">
                    <strong>{{ selectedPermissions.length }}</strong> permission(s) select of <strong>{{ permissions.length }}</strong>
                  </span>
                  <div class="progress flex-grow-1 mx-3" style="height: 6px;">
                    <div 
                      class="progress-bar bg-primary" 
                      role="progressbar" 
                      :style="{ width: `${(selectedPermissions.length / permissions.length) * 100}%` }"
                    ></div>
                  </div>
                  <span class="text-primary fw-medium">{{ Math.round((selectedPermissions.length / permissions.length) * 100) }}%</span>
                </div>
              </div>

              <div class="row row-cols-1 row-cols-md-2 row-cols-xl-3 g-4">
                <div v-for="(permissionGroup, feature) in filteredPermissions" :key="feature" class="col">
                  <div class="card h-100 permission-group-card" :class="{ 'card-selected': isFeatureFullySelected(feature) }">
                    <div class="card-header bg-white d-flex justify-content-between align-items-center py-3">
                      <div class="d-flex align-items-center">
                        <i :class="['ri-shield-line fs-18 me-2', {'text-primary': isFeatureFullySelected(feature)}]"></i>
                        <h5 class="mb-0 fs-16 fw-semibold">{{ formatFeatureName(feature) }}</h5>
                      </div>
                      <div class="form-check">
                        <input 
                          class="form-check-input" 
                          type="checkbox" 
                          :id="`feature-${feature}`" 
                          :checked="isFeatureFullySelected(feature)"
                          @change="toggleFeaturePermissions(feature)"
                        />
                        <label class="form-check-label" :for="`feature-${feature}`"></label>
                      </div>
                    </div>
                    <div class="card-body p-0">
                      <div class="permissions-list">
                        <div 
                          v-for="permission in permissionGroup" 
                          :key="permission.id" 
                          class="permission-item p-3 border-top d-flex align-items-center"
                          :class="{ 'permission-selected': selectedPermissions.includes(permission.id) }"
                        >
                          <div class="form-check me-1 flex-shrink-0">
                            <input 
                              class="form-check-input" 
                              type="checkbox" 
                              :id="permission.permission_code" 
                              :value="permission.id" 
                              v-model="selectedPermissions"
                            />
                          </div>
                          <label class="ms-2 w-100 cursor-pointer" :for="permission.permission_code" :title="permission.description">
                            <div class="fw-medium">{{ formatPermissionName(permission.permission_name) }}</div>
                            <small class="text-muted text-truncate d-block">{{ permission.description }}</small>
                          </label>
                          <div class="ms-auto permission-info" data-bs-toggle="tooltip" :title="permission.permission_code">
                            <i class="ri-information-line text-muted"></i>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div class="card-footer bg-white py-2 text-center">
                      <small class="text-muted">{{ permissionGroup.length }} permission(s)</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="row">
            <div class="col-12">
              <div class="d-flex justify-content-end gap-3 mt-4 border-top pt-4">
                <button 
                  type="button" 
                  class="btn btn-outline-secondary fw-semibold py-2 px-4" 
                  @click="cancelEdition"
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  class="btn btn-primary text-white fw-semibold py-2 px-4"
                  :disabled="isSubmitting || (isEditing && !hasPermission('roles_edit')) || (!isEditing && !hasPermission('roles_create'))"
                >
                  <i class="ri-save-line me-1" v-if="!isSubmitting"></i>
                  <span v-if="isSubmitting">
                    <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Saving...
                  </span>
                  <span v-else>{{ isEditing ? 'Update' : 'Save' }}</span>
                </button>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, watch, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useRoleStore } from '@/stores/roleStore';
import Toast from "@/components/Common/Toast.vue";
import bootstrap from 'bootstrap/dist/js/bootstrap.bundle.min.js';
import {hasPermission} from '@/utils/permissions';

interface Permission {
  id: string;
  permission_name: string;
  permission_code: string;
  feature_name: string;
  description?: string;
}

interface Role {
  name: string;
  description: string;
  is_active: boolean;
  permissions: string[];
  permission_ids?: string[] | string;
}

export default defineComponent({
  name: 'RoleForm',
  components: {
    Toast
  },
  setup() {
    const route = useRoute();
    const router = useRouter();
    const roleStore = useRoleStore();

    const roleId = computed(() => route.params.id as string | string[]);
    const isEditing = computed(() => !!roleId.value);

    const permissions = ref<Permission[]>([]);
    const selectedPermissions = ref<string[]>([]);
    const roleData = ref<{
      name: string;
      description: string;
      is_active: boolean;
    }>({
      name: '',
      description: '',
      is_active: true
    });
    const errors = ref<Record<string, string>>({});
    const isSubmitting = ref(false);
    const searchQuery = ref('');
    const collapsedFeatures = ref<Record<string, boolean>>({});
    const loading = ref(true);

    const filteredPermissions = computed(() => {
      const query = searchQuery.value.toLowerCase();
      const grouped: Record<string, Permission[]> = {};
      
      Object.entries(groupedPermissions.value).forEach(([feature, permissionList]) => {
        if (!query) {
          grouped[feature] = permissionList;
          return;
        }
        
        const filteredList = permissionList.filter(permission => 
          permission.permission_name.toLowerCase().includes(query) || 
          (permission.description?.toLowerCase() || '').includes(query) ||
          permission.permission_code.toLowerCase().includes(query) ||
          feature.toLowerCase().includes(query)
        );
        
        if (filteredList.length > 0) {
          grouped[feature] = filteredList;
        }
      });
      
      return grouped;
    });

    const groupedPermissions = computed<Record<string, Permission[]>>(() => {
      const grouped: Record<string, Permission[]> = {};
      
      if (!permissions.value || !Array.isArray(permissions.value)) {
        return grouped;
      }
      
      permissions.value.forEach(permission => {
        if (!grouped[permission.feature_name]) {
          grouped[permission.feature_name] = [];
        }
        grouped[permission.feature_name].push(permission);
      });
      
      return grouped;
    });

    const isFeatureFullySelected = (feature: string): boolean => {
      const featurePermissions = groupedPermissions.value[feature] || [];
      const featurePermissionIds = featurePermissions.map(p => p.id);
      return featurePermissionIds.every(id => selectedPermissions.value.includes(id));
    };

    const formatFeatureName = (feature: string): string => {
      return feature
        .replace(/_/g, ' ')
        .split(' ')
        .map((word: string) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
    };

    const formatPermissionName = (permissionName: string): string => {
      return permissionName
        .replace(/_/g, ' ')
        .replace(/\b\w/g, (l: string) => l.toUpperCase());
    };

    const toggleFeaturePermissions = (feature: string): void => {
      const featurePermissions = groupedPermissions.value[feature] || [];
      const featurePermissionIds = featurePermissions.map(p => p.id);
      
      if (isFeatureFullySelected(feature)) {
        selectedPermissions.value = selectedPermissions.value.filter(id => !featurePermissionIds.includes(id));
      } else {
        const newSelected = [...selectedPermissions.value];
        featurePermissionIds.forEach(id => {
          if (!newSelected.includes(id)) {
            newSelected.push(id);
          }
        });
        selectedPermissions.value = newSelected;
      }
    };

    const selectAllPermissions = (): void => {
      selectedPermissions.value = permissions.value.map(p => p.id);
    };

    const deselectAllPermissions = (): void => {
      selectedPermissions.value = [];
    };

    const handleToastClose = (): void => {
      roleStore.toast.show = false;
    };

    const fetchPermissions = async (): Promise<void> => {
      try {
        permissions.value = await roleStore.fetchPermissions();
        
        const features = [...new Set(permissions.value.map(p => p.feature_name))];
        features.forEach(feature => {
          collapsedFeatures.value[feature] = true;
        });
      } catch (error) {
        roleStore.showToast('Error while loading permissions', 'error');
      }
    };
    
    const fetchRole = async (id: string): Promise<void> => {
      if (!id) return;
      
      try {
        const role = await roleStore.fetchRoleById(id);
        if (role) {
          roleData.value = {
            name: role.name,
            description: role.description || '',
            is_active: role.is_active
          };
          
          if (role.permission_ids) {
            const permissionArray = typeof role.permission_ids === 'string' 
              ? role.permission_ids.split(',')
              : role.permission_ids;
            
            selectedPermissions.value = permissionArray;
          } else {
            selectedPermissions.value = [];
          }
        }
      } catch (error: any) {
        roleStore.showToast(`Error while loading role: ${error.message}`, 'error');
      }
    };

    const saveRole = async (): Promise<void> => {
      errors.value = {};
      
      const name = roleData.value.name.trim();
      if (!name) {
        errors.value.name = 'Name is required';
        roleStore.showToast('Name is required', 'error');
        return;
      }
      if (name.length < 2 || name.length > 255) {
        errors.value.name = 'Name must be between 2 and 255 characters';
        roleStore.showToast(errors.value.name, 'error');
        return;
      }

      const description = roleData.value.description.trim();
      if (!description) {
        errors.value.description = 'Description is required';
        roleStore.showToast('Description is required', 'error');
        return;
      }
      if (description.length > 500) {
        errors.value.description = 'Description must not exceed 500 characters';
        roleStore.showToast(errors.value.description, 'error');
        return;
      }

      if (selectedPermissions.value.length === 0) {
        roleStore.showToast('Please select at least one permission', 'error');
        return;
      }
      
      isSubmitting.value = true;
      
      try {
        const payload: Partial<Role> = {
          ...roleData.value,
          permissions: selectedPermissions.value
        };
        
        let result;
        
        if (isEditing.value) {
          const id = Array.isArray(roleId.value) ? roleId.value[0] : roleId.value;
          result = await roleStore.updateRole(id, payload);
        } else {
          result = await roleStore.createRole(payload);
        }
        
        if (result) {
          router.push('/config/roles');
        }
      } catch (error: any) {
        
        if (error.response && error.response.data && error.response.data.errors) {
          errors.value = error.response.data.errors;
        }
      } finally {
        isSubmitting.value = false;
      }
    };

    const cancelEdition = (): void => {
      router.push('/config/roles');
    };

    watch(searchQuery, () => {
      Object.keys(groupedPermissions.value).forEach(feature => {
        if (searchQuery.value) {
          const hasMatch = groupedPermissions.value[feature].some(permission => 
            permission.permission_name.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
            (permission.description?.toLowerCase() || '').includes(searchQuery.value.toLowerCase()) ||
            permission.permission_code.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
            feature.toLowerCase().includes(searchQuery.value.toLowerCase())
          );
          
          if (hasMatch) {
            collapsedFeatures.value[feature] = false; 
          }
        }
      });
    });

    onMounted(async () => {
      loading.value = true;
      
      try {
        await fetchPermissions();
        
        if (isEditing.value) {
          const id = Array.isArray(roleId.value) ? roleId.value[0] : roleId.value;
          await fetchRole(id);
        } else {
          selectedPermissions.value = [];
        }
      } catch (error) {
        roleStore.showToast('Error while loading data', 'error');
      } finally {
        loading.value = false;
      }
      
      nextTick(() => {
        document.querySelectorAll('[data-bs-toggle="dropdown"]').forEach(dropdownToggle => {
          new bootstrap.Dropdown(dropdownToggle);
        });

        document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(tooltipEl => {
          new bootstrap.Tooltip(tooltipEl);
        });
      });
    });

    return {
      router,
      roleStore,
      roleId,
      isEditing,
      permissions,
      selectedPermissions,
      roleData,
      errors,
      isSubmitting,
      searchQuery,
      collapsedFeatures,
      filteredPermissions,
      groupedPermissions,
      loading,
      isFeatureFullySelected,
      formatFeatureName,
      formatPermissionName,
      toggleFeaturePermissions,
      selectAllPermissions,
      deselectAllPermissions,
      saveRole,
      cancelEdition,
      handleToastClose,
      hasPermission,
    };
  }
});
</script>

<style scoped>
.cursor-pointer {
  cursor: pointer;
}

.permission-group-card {
  transition: all 0.25s ease;
  border: 1px solid #e9ecef;
  border-radius: 0.5rem;
  overflow: hidden;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
}

.permission-group-card:hover {
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-3px);
}

.card-selected {
  border-color: #0d6efd !important;
  box-shadow: 0 6px 15px rgba(13, 110, 253, 0.15) !important;
}

.permissions-list {
  max-height: 250px;
  overflow-y: auto;
  scrollbar-width: thin;
}

.permissions-list::-webkit-scrollbar {
  width: 4px;
}

.permissions-list::-webkit-scrollbar-track {
  background: #f8f9fa;
}

.permissions-list::-webkit-scrollbar-thumb {
  background-color: #dee2e6;
  border-radius: 20px;
}

.permission-item {
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.permission-item:hover {
  background-color: #f8f9fa;
  z-index: 1;
}

.permission-item::after {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 3px;
  background-color: transparent;
  transition: background-color 0.2s ease;
}

.permission-item:hover::after {
  background-color: #0d6efd;
}

.permission-selected {
  background-color: #eef4ff !important;
}

.permission-selected::after {
  background-color: #0d6efd;
}

.permission-info {
  opacity: 0.5;
  transition: opacity 0.2s ease;
}

.permission-item:hover .permission-info {
  opacity: 1;
}

.permission-stats {
  border-left: 4px solid #0d6efd;
  background-color: #f8f9fa !important;
}

.form-check-input:checked {
  background-color: #0d6efd;
  border-color: #0d6efd;
}

.search-input {
  transition: all 0.3s ease;
}

.search-input:focus-within {
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.15);
}

.btn-icon {
  width: 40px;
  height: 40px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>