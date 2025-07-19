<template>
    <div class="main-content-container overflow-hidden">
        <PageTitle pageTitle="Users"/>
        <Compose />
    </div>
    <div class="main-content-container overflow-hidden">
        
        <div class="card bg-white border-0 rounded-3 mb-4">
            <div class="card-body p-0">
                <div class="filter-section p-4">
                     <div class="d-flex justify-content-between align-items-center mb-4">
                          <RouterLink
                            v-if="authStore.hasPermission('users_create')"
                            to="/users/add"
                            class="btn btn-outline-primary"
                          >
                            <i class="ri-add-line me-1"></i> Add user
                          </RouterLink>

                          <div class="d-flex gap-2 align-items-center">
                            <div class="input-group">
                              <span class="input-group-text">
                                <i class="material-symbols-outlined">search</i>
                              </span>
                              <input
                                type="text"
                                class="form-control"
                                placeholder="Search by name, username or email"
                                v-model="filters.searchTerm"
                              />
                            </div>
                            <button
                              class="btn btn-outline-primary"
                              @click="showAdvancedFilters = !showAdvancedFilters"
                            >
                              {{ showAdvancedFilters ? 'Hide filters' : 'More filters' }}
                            </button>
                          </div>
                    </div>
                    
                    <div v-if="showAdvancedFilters" class="advanced-filters mb-3">
                        <div class="row g-3">
                            <div class="col-md-4">
                                <label class="form-label">Status</label>
                                <select class="form-select" v-model="filters.status">
                                    <option value="">All status</option>
                                    <option value="true">Active</option>
                                    <option value="false">Inactive</option>
                                </select>
                            </div>
  
                            <div class="col-md-4">
                                <label class="form-label">Role</label>
                                <select class="form-select" v-model="filters.role">
                                    <option value="">All roles</option>
                                    <option v-for="role in userStore.availableRoles" :key="role.id" :value="role.name">
                                        {{ role.name }}
                                    </option>
                                </select>
                            </div>
  
                            <div class="col-md-4">
                                <label class="form-label">Tri</label>
                                <select class="form-select" v-model="filters.ordering">
                                    <option value="created_at">Sort by creation date</option>
                                    <option value="updated_at">Sort by date updated</option>
                                    <option value="role">Sort by role</option>
                                    <option value="is_active">Sort by status</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </div>
  
                <div class="default-table-area style-two default-table-width">
                    <div class="table-responsive">
                        <table class="table align-middle">
                            <thead>
                                <tr>
                                    <th scope="col" style="width: 5%">ID</th>
                                    <th scope="col" style="width: 15%">Full name</th>
                                    <th scope="col" style="width: 15%">Username</th>
                                    <th scope="col" style="width: 15%">Email</th>
                                    <th scope="col" style="width: 10%">Role</th>
                                    <th scope="col" style="width: 10%">Status</th>
                                    <th scope="col" style="width: 10%">Creation date</th>
                                    <th scope="col" style="width: 10%">Update date</th>
                                    <th scope="col" style="width: 10%" v-if="authStore.hasAnyPermission(['users_edit', 'users_delete', 'users_toggle'])">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="user in paginatedUsers" :key="user.id">
                                    <td class="text-body">{{ userStore.getUserDisplayId(user.id) }}</td>
                                    <td>
                                        <div class="content-truncate" style="max-width: 150px;">
                                            {{ user.nom_prenom }}
                                            <div class="tooltip-content">{{ user.nom_prenom }}</div>
                                        </div>
                                    </td>
                                    <td>
                                        <div class="content-truncate" style="max-width: 150px;">
                                            {{ user.username }}
                                            <div class="tooltip-content">{{ user.username }}</div>
                                        </div>
                                    </td>
                                    <td>
                                        <div class="content-truncate" style="max-width: 150px;">
                                            {{ user.email }}
                                            <div class="tooltip-content">{{ user.email }}</div>
                                        </div>
                                    </td>
                                    <td>{{ user.role_name || 'Undefined' }}</td>
                                    <td>
                                        <span :class="getStatusBadgeClass(user.is_active)" class="badge p-2 fs-12 fw-normal">
                                            {{ user.is_active ? 'Active' : 'Inactive' }}
                                        </span>
                                    </td>
                                    <td>{{ formatDate(user.created_at) }}</td>
                                    <td>{{ formatDate(user.updated_at) }}</td>
                                    <td v-if="authStore?.user?.id !== user.id">
                                        <div class="d-flex align-items-center gap-2">
                                            <RouterLink 
                                              v-if="authStore.hasPermission('users_edit') && authStore?.user?.id !== user.id"
                                              :to="`/users/edit/${user.id}`" 
                                              class="ps-0 border-0 bg-transparent lh-1 position-relative"
                                            >
                                                <i class="material-symbols-outlined fs-16 text-primary">
                                                    edit
                                                </i>
                                            </RouterLink>
                                            
                                            <button 
                                              v-if="authStore.hasPermission('users_toggle') && authStore?.user?.id !== user.id"
                                              class="ps-0 border-0 bg-transparent lh-1 position-relative" 
                                              @click="toggleUserStatus(user)"
                                              :title="user.is_active ? 'Deactivate user' : 'Activate user'"
                                            >
                                                <i class="material-symbols-outlined fs-16" :class="user.is_active ? 'text-success' : 'text-danger'">
                                                    {{ user.is_active ? 'toggle_on' : 'toggle_off' }}
                                                </i>
                                            </button>
                                            
                                            <button 
                                              v-if="authStore.hasPermission('users_delete') "
                                              class="ps-0 border-0 bg-transparent lh-1 position-relative" 
                                              @click="confirmDelete(user)"
                                            >
                                                <i class="material-symbols-outlined fs-16 text-danger">
                                                    delete
                                                </i>
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                                <tr v-if="userStore.loading">
                                    <td colspan="9" class="text-center py-4">
                                        <div class="spinner-border text-primary" role="status">
                                            <span class="visually-hidden">Loading...</span>
                                        </div>
                                    </td>
                                </tr>
                                <tr v-else-if="filteredUsers.length === 0">
                                    <td colspan="9" class="text-center py-4">
                                      No users found
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
  
                    <div class="p-4 pt-lg-4">
                        <Pagination :total="totalUsers" v-model="currentPage" :per-page="itemsPerPage" @page-change="onPageChange"/>
                    </div>
                </div>
            </div>
        </div>
    </div>
  
    <div class="modal fade" :class="{ 'show d-block': showDeleteModal }" tabindex="-1" style="background-color: rgba(0,0,0,0.5);" v-if="showDeleteModal">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Confirm deletion</h5>
                    <button type="button" class="btn-close" @click="showDeleteModal = false"></button>
                </div>
                <div class="modal-body" v-if="userToDelete">
                    <p>Are you sure you want to delete the user <strong>{{ userToDelete.nom_prenom }}</strong> ?</p>
                    <p class="text-danger">This action is irreversible.</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" @click="showDeleteModal = false">Cancel</button>
                    <button type="button" class="btn btn-danger" @click="deleteUser">Delete</button>
                </div>
            </div>
        </div>
    </div>
    <Toast 
        :show="userStore.toast.show" 
        :message="userStore.toast.message" 
        :type="userStore.toast.type" 
        :autoClose="true"
        :duration="userStore.toast.duration"
        @close="handleToastClose" 
  />
  </template>
  
  <script setup lang="ts">
  import { ref, computed, onMounted, watch } from "vue";
  import { useRouter } from 'vue-router';
  import Pagination from "@/components/Common/Pagination.vue";
  import PageTitle from "@/components/Common/PageTitle.vue";
  import { useUserStore } from '@/stores/user.store';
  import { useAuthStore } from '@/stores/auth.store';
  import Toast from "@/components/Common/Toast.vue";
  
  const router = useRouter();
  const userStore = useUserStore();
  const authStore = useAuthStore();
  
  const showAdvancedFilters = ref(false);
  
  const showDeleteModal = ref(false);
  const userToDelete = ref(null);
  
  const currentPage = ref(1);
  const itemsPerPage = ref(15);
  
  const filters = ref({
    searchTerm: "",
    status: "",
    role: "",
    ordering: "created_at"
  });
  
  watch(filters, (newFilters) => {
    userStore.filters = newFilters;
  }, { deep: true });
  
  function resetFilters() {
    userStore.resetFilters();
    filters.value = { ...userStore.filters };
    currentPage.value = 1;
  }
  function handleToastClose() {
  userStore.toast.show = false;
}
  function applyFilters() {
  try {
    userStore.filters = { 
      searchTerm: filters.value.searchTerm || '',
      status: filters.value.status || '',
      role: filters.value.role || '',
      ordering: filters.value.ordering || 'created_at'
    };
    
    currentPage.value = 1;
  } catch (error) {
    console.error('Error applying filters:', error);
  }
}
  

  function onPageChange(page) {
    currentPage.value = page;
    

    const startIndex = (page - 1) * itemsPerPage.value;
    if (startIndex + itemsPerPage.value > userStore.users.length && userStore.hasMoreData) {
      userStore.loadMoreUsers();
    }
  }
  

  const filteredUsers = computed(() => userStore.filteredUsers);
  
 const sortedUsers = computed(() => {
  const arr = [...filteredUsers.value];
  const field = filters.value.ordering;
  arr.sort((a, b) => {
    switch (field) {
      case 'created_at':
      case 'updated_at':
        return new Date(a[field]).getTime() - new Date(b[field]).getTime();
      case 'role':
        return (a.role_name || '').localeCompare(b.role_name || '');
      case 'is_active':
        return (a.is_active === b.is_active)
          ? 0
          : a.is_active
            ? -1
            : 1;
      default:
        return 0;
    }
  });
  return arr;
});

const totalUsers = computed(() => sortedUsers.value.length);

const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value;
  return sortedUsers.value.slice(start, start + itemsPerPage.value);
});
  
  function formatDate(dateString) {
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
  

  function getStatusBadgeClass(isActive) {
    return isActive 
        ? "bg-success bg-opacity-10 text-success" 
        : "bg-danger bg-opacity-10 text-danger";
  }
  

  async function toggleUserStatus(user) {
    try {
      await userStore.toggleUserStatus(user.id);
    } catch (error) {
      console.error('Error switching status:', error);
    }
  }
  

  function confirmDelete(user) {
    userToDelete.value = user;
    showDeleteModal.value = true;
  }
  

  async function deleteUser() {
    if (!userToDelete.value) return;
    
    try {
      const success = await userStore.deleteUser(userToDelete.value.id);
      
      if (success) {
        showDeleteModal.value = false;
        userToDelete.value = null;
      }
    } catch (error) {
      console.error('Error deleting user:', error);
    } finally {
      showDeleteModal.value = false;
    }
  }
  

  onMounted(async () => {
    await userStore.fetchRoles();
    await userStore.fetchUsers();
  });
  </script>
  <style scoped>

  .align-items-end-md {
    display: flex;
    align-items: end;
  }
  
  .content-truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 150px;
  position: relative;
  cursor: pointer;
  transition: max-width 0.3s ease;
}
.content-truncate:hover {
  max-width: 300px;
  z-index: 10;
  background-color: #f8f9fa;
  border-radius: 4px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  padding: 4px;
  margin: -4px;
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
    margin-top: 10px;
  }
  

  .material-symbols-outlined {
    cursor: pointer;
    transition: opacity 0.2s ease;
  }
  
  .material-symbols-outlined:hover {
    opacity: 0.7;
  }
  

  .hover-bg:hover {
    background-color: rgba(var(--bs-primary-rgb), 0.1);
  }
  

  .btn-outline-primary {
    transition: all 0.3s ease;
  }
  
  .btn-outline-primary:hover {
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  }
  </style>