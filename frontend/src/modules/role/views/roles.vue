<template>
  <div class="main-content-container overflow-hidden">
    <PageTitle pageTitle="Roles" subTitle="Config" />
    <Toast
      :show="roleStore.toast.show"
      :message="roleStore.toast.message"
      :type="roleStore.toast.type"
      :autoClose="true"
      :duration="roleStore.toast.duration"
      @close="handleToastClose"
    />
  </div>
  <div class="container-fluid">
    <div class="row page-header align-items-center mb-4">
      <div class="col-md-6 d-flex align-items-center">
        <button
          class="btn btn-outline-primary py-1 px-2 px-sm-4 fs-14 fw-medium rounded-3 hover-bg btn-add-role"
          @click="prepareNewRole"
          v-if="hasPermission('roles_create')"
        >
          <span class="py-sm-1 d-block">
            <i class="ri-add-line me-1"></i>
            <span>Add role</span>
          </span>
        </button>
      </div>
      <div class="col-md-6">
        <div class="float-md-end mt-md-0 mt-3">
          <div class="input-group border rounded overflow-hidden search-input">
            <span class="input-group-text bg-transparent border-0">
              <i data-feather="search"></i>
            </span>
            <input
              type="text"
              class="form-control bg-transparent border-0"
              placeholder="Research role..."
              v-model="searchQuery"
              @input="handleSearch"
            />
            <span
              v-if="searchQuery"
              class="input-group-text bg-transparent border-0 cursor-pointer"
              @click="clearSearch"
            >
              <i class="ri-close-line"></i>
            </span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="card bg-white border-0 rounded-3 mb-4">
      <div class="card-body p-4">
        <div v-if="roleStore.loading && !hasFetchedInitialData" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2">Loading roles...</p>
        </div>

        <div v-else-if="roles.length === 0 && !roleStore.loading" class="empty-state-container">
          <div class="text-center py-5">
            <div class="empty-state-icon mb-4">
              <i class="ri-shield-user-line fs-1 text-muted"></i>
            </div>
            <h4 class="fs-16 fw-semibold">No role exists</h4>
            <p class="text-muted mb-4">You have not yet created any roles. Roles allow you to define user permissions on the platform..</p>
            <button
              class="btn btn-primary text-white fw-semibold py-2 px-4 mx-auto"
              data-bs-toggle="modal"
              data-bs-target="#roleModal"
              @click="prepareNewRole"
              v-if="hasPermission('roles_create')"
            >
              <i class="ri-add-line me-1"></i>
              Create your first role
            </button>
          </div>
        </div>

        <div v-else>
          <div class="row justify-content-start">
            <div class="col-xxl-3 col-lg-4 col-sm-6" v-for="role in paginatedRoles" :key="role.id">
              <div class="card entity-card">
                <div class="card-body p-4">
                  <div class="d-flex justify-content-between align-items-center mb-3">
                    <div class="d-flex align-items-center">
                    </div>
      
                    <div class="dropdown action-opt ms-2 position-relative top-3">
                      <button
                        class="p-0 border-0 bg-transparent"
                        type="button"
                        @click.stop="toggleDropdown(role.id)"
                      >
                        <i class="material-symbols-outlined fs-20 fw-bold text-body hover">
                          more_horiz
                        </i>
                      </button>
                      <ul class="dropdown-menu dropdown-menu-end bg-white border box-shadow" :class="{ 'show': activeDropdown === role.id }">
                        <li>
                          <a class="dropdown-item" href="javascript:;" @click.stop="viewRoleDetails(role)">
                            <i class="ri-eye-line me-2"></i>
                            Détails
                          </a>
                        </li>
                        <li v-if="hasPermission('roles_edit')">
                          <a class="dropdown-item" href="javascript:;" @click.stop="editRole(role)">
                            <i class="ri-edit-line me-2"></i>
                            Edit
                          </a>
                        </li>
                        <li v-if="hasPermission('roles_delete')">
                          <a class="dropdown-item" href="javascript:;" @click.stop="deleteRole(role.id)">
                            <i class="ri-delete-bin-line me-2"></i>
                            Delete
                          </a>
                        </li>
                      </ul>
                    </div>
                  </div>
                  <span
                    class="d-block py-2 px-3 text-center rounded-pill fw-medium text-secondary mb-3 bg-for-dark-mode"
                    style="background-color: #daebff"
                  >
                    {{ role.name }}
                  </span>
                  <div class="description-container" @mouseenter="showTooltip = role.id" @mouseleave="showTooltip = null">
                    <div class="description-wrapper">
                      <span class="description-truncate">{{ role.description }}</span>
                    </div>
                    <div class="custom-tooltip" v-if="shouldShowTooltip(role) && showTooltip === role.id">
                      {{ role.description }}
                    </div>
                  </div>
                  <ul class="ps-0 mb-4 list-unstyled">
                    <li class="mb-2 pb-1">
                      <span class="text-secondary fw-bold">Creation date: </span>
                      <span>{{ formatDate(role.created_at) }}</span>
                    </li>
      
                    <li class="mb-2 pb-1">
                      <span class="text-secondary fw-bold">Last update: </span>
                      <span>{{ formatDate(role.updated_at) }}</span>
                    </li>
      
                    <li class="mb-2 pb-1">
                      <span class="text-secondary fw-bold">Status: </span>
                      <span :class="role.is_active ? 'text-success' : 'text-danger'">
                        {{ role.is_active ? 'Active' : 'Inactive' }}
                      </span>
                    </li>
                  </ul>
                  
                  <div class="d-flex align-items-center justify-content-between mb-4">
                    <span class="text-secondary fw-medium me-2">Toggle:</span>
                    <div class="form-check form-switch">
                      <input class="form-check-input" type="checkbox" :id="`role-status-${role.id}`" 
                        :checked="role.is_active" @change="toggleRoleStatus(role)" :disabled="!hasPermission('roles_toggle')"
                        />
                      <label class="form-check-label" :for="`role-status-${role.id}`">
                        {{role.is_active ? 'Active' : 'Inactive'}}
                      </label>
                    </div>
                  </div>
                  
                  <button
                    @click="viewRoleDetails(role)"
                    class="btn btn-outline-primary fw-medium w-100 py-2 rounded-3"
                  >
                    View Details
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <div v-if="roleStore.loading && hasFetchedInitialData" class="text-center py-3">
            <div class="spinner-border spinner-border-sm text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <span class="ms-2">Loading more roles...</span>
          </div>
          
          <div v-if="filteredRoles.length > 0" class="d-flex justify-content-between align-items-center mt-4 pagination-container">
            <div class="pagination-info">
              Show  <span class="fw-medium">{{ paginationStart }}</span> to <span class="fw-medium">{{ paginationEnd }}</span> of <span class="fw-medium">{{ filteredRoles.length }}</span> role(s)
            </div>
            <nav aria-label="Pagination des rôles">
              <ul class="pagination mb-0">
                <li class="page-item" :class="{ disabled: currentPage === 1 }">
                  <a class="page-link" href="#" @click.prevent="goToPage(currentPage - 1)" aria-label="Previous">
                    <span aria-hidden="true"><i class="ri-arrow-left-s-line"></i></span>
                  </a>
                </li>
                <li v-for="page in displayedPages" :key="page" class="page-item" :class="{ active: currentPage === page, 'page-separator': page === '...' }">
                  <template v-if="page === '...'">
                    <span class="page-link border-0 bg-transparent">...</span>
                  </template>
                  <a v-else class="page-link" href="#" @click.prevent="goToPage(page)">{{ page }}</a>
                </li>
                <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                  <a class="page-link" href="#" @click.prevent="goToPage(currentPage + 1)" aria-label="Next">
                    <span aria-hidden="true"><i class="ri-arrow-right-s-line"></i></span>
                  </a>
                </li>
              </ul>
            </nav>
          </div>
          
          <div v-if="roles.length > 0 && filteredRoles.length === 0" class="empty-search-results text-center my-5">
            <i class="ri-search-line fs-1 text-muted mb-3 d-block"></i>
            <h4 class="fs-16 fw-semibold">No result found</h4>
            <p class="text-muted">No roles match your search."{{ searchQuery }}"</p>
            <button class="btn btn-outline-secondary" @click="clearSearch">
              Delete the research
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <div class="modal fade" id="deleteRoleModal" tabindex="-1" aria-labelledby="deleteRoleModalLabel" aria-hidden="true" v-if="hasPermission('roles_delete')">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="deleteRoleModalLabel">Confirm deletion</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            Are you sure you want to delete this role? This action is irreversible.
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline-secondary fw-semibold py-2 px-4" data-bs-dismiss="modal">Cancel</button>
            <button 
              type="button" 
              class="btn btn-danger text-white fw-semibold py-2 px-4" 
              @click="confirmDeleteRole"
              :disabled="roleStore.isDeleting"
            >
              <span v-if="roleStore.isDeleting">
                <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                Deleting...
              </span>
              <span v-else>Delete</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, computed, onMounted, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useRoleStore } from '@/stores/roleStore';
import PageTitle from "@/components/Common/PageTitle.vue";
import Toast from "@/components/Common/Toast.vue";
import feather from 'feather-icons';
import { Modal } from 'bootstrap';
import {hasPermission} from '@/utils/permissions';

export default defineComponent({
  name: 'RolesIndex',
  components: {
    PageTitle,
    Toast
  },
  setup() {
    const router = useRouter();
    const roleStore = useRoleStore();
    const searchQuery = ref('');
    const showTooltip = ref(null);
    const activeDropdown = ref(null);
    const roleIdToDelete = ref(null);
    const currentPage = ref(1);
    const itemsPerPage = ref(12); 
    const hasFetchedInitialData = ref(false);
    const searchTimeout = ref(null);
    
    const roles = computed(() => roleStore.roles);
    
    const filteredRoles = computed(() => {
      if (!searchQuery.value) return roles.value;
      
      const query = searchQuery.value.toLowerCase();
      return roles.value.filter(role => 
        role.name.toLowerCase().includes(query) || 
        (role.description && role.description.toLowerCase().includes(query))
      );
    });

    const totalPages = computed(() => {
      return Math.ceil(filteredRoles.value.length / itemsPerPage.value);
    });

    const paginatedRoles = computed(() => {
      const startIndex = (currentPage.value - 1) * itemsPerPage.value;
      const endIndex = startIndex + itemsPerPage.value;
      return filteredRoles.value.slice(startIndex, endIndex);
    });

    const paginationStart = computed(() => {
      if (filteredRoles.value.length === 0) return 0;
      return (currentPage.value - 1) * itemsPerPage.value + 1;
    });

    const paginationEnd = computed(() => {
      if (filteredRoles.value.length === 0) return 0;
      return Math.min(currentPage.value * itemsPerPage.value, filteredRoles.value.length);
    });

    const displayedPages = computed(() => {
      const pages = [];
      const maxPagesToShow = 5;
      
      if (totalPages.value <= maxPagesToShow) {
        for (let i = 1; i <= totalPages.value; i++) {
          pages.push(i);
        }
      } else {
        pages.push(1);
        
        let startPage = Math.max(2, currentPage.value - 1);
        let endPage = Math.min(totalPages.value - 1, currentPage.value + 1);
        
        if (startPage === 2) endPage = Math.min(totalPages.value - 1, 4);
        if (endPage === totalPages.value - 1) startPage = Math.max(2, totalPages.value - 3);
        
        if (startPage > 2) pages.push('...');
        
        for (let i = startPage; i <= endPage; i++) {
          pages.push(i);
        }
        
        if (endPage < totalPages.value - 1) pages.push('...');
        
        pages.push(totalPages.value);
      }
      
      return pages;
    });

    const goToPage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page;
      }
    };

    const handleSearch = () => {
      if (searchTimeout.value) {
        clearTimeout(searchTimeout.value);
      }
      
      searchTimeout.value = setTimeout(() => {
        currentPage.value = 1;
        roleStore.searchRoles(searchQuery.value);
      }, 300);
    };

    const clearSearch = () => {
      searchQuery.value = '';
      fetchRoles();
    };

    const shouldShowTooltip = (role) => {
      if (!role.description) return false;
      return role.description.length > 100 || role.description.split('\n').length > 2;
    };

    const toggleDropdown = (roleId) => {
      if (activeDropdown.value === roleId) {
        activeDropdown.value = null;
      } else {
        activeDropdown.value = roleId;
      }
    };

    const handleClickOutside = (event) => {
      if (activeDropdown.value !== null && !event.target.closest('.dropdown')) {
        activeDropdown.value = null;
      }
    };

    const formatDate = (dateString) => {
      if (!dateString) return "";
      
      try {
        const date = new Date(dateString);
        
        if (isNaN(date.getTime())) {
          return dateString;
        }
        
        const day = date.getDate().toString().padStart(2, '0');
        const monthIndex = date.getMonth();
        const year = date.getFullYear();
        
        const monthNames = ["jan", "fév", "mar", "avr", "mai", "juin", "juil", "août", "sep", "oct", "nov", "déc"];
        
        return `${day} ${monthNames[monthIndex]} ${year}`;
      } catch (error) {
        return dateString;
      }
    };

    const toggleRoleStatus = async (role) => {
      if (!hasPermission('roles_toggle')) {
        roleStore.showToast("Permission denied", "error");
        return;
      }
      const previousStatus = role.is_active;
      try {
        const response = await roleStore.toggleRoleStatus(role.id);
        if (response && typeof response.is_active !== "undefined") {
          role.is_active = response.is_active;
        } else role.is_active = previousStatus;
      } catch (error) {
        role.is_active = previousStatus;
        roleStore.showToast("Error updating role status", "error");
      }
    };

    const prepareNewRole = () => {
      router.push('/config/roles-create');
    };

    const viewRoleDetails = (role) => {
      router.push(`/config/roles-edit/${role.id}`);
    };

    const editRole = (role) => {
      router.push(`/config/roles-edit/${role.id}`);
    };

    const deleteRole = (id) => {
      roleIdToDelete.value = id;
      const modalElement = document.getElementById('deleteRoleModal');
      if (modalElement) {
        const modal = new Modal(modalElement);
        modal.show();
      }
    };

    const confirmDeleteRole = async () => {
      if (!hasPermission('roles_delete')) {
        roleStore.showToast("Permission denied", "error");
        return;
      }
      if (!roleIdToDelete.value) return;
      
      try {
        const success = await roleStore.deleteRole(roleIdToDelete.value);
        
        if (success) {
          const modalElement = document.getElementById('deleteRoleModal');
          if (modalElement) {
            const modal = Modal.getInstance(modalElement);
            if (modal) modal.hide();
          }
          
          roleIdToDelete.value = null;
        }
      } catch (error) {
        roleStore.showToast("Error deleting role", "error");
      }
    };

    const handleToastClose = () => {
      roleStore.toast.show = false;
    };

    const fetchRoles = async () => {
      try {
        await roleStore.fetchRoles();
        hasFetchedInitialData.value = true;
      } catch (error) {
        roleStore.showToast("Error loading roles", "error");
      }
    };

    watch(searchQuery, () => {
      currentPage.value = 1;
    });

    onMounted(async () => {
      nextTick(() => {
        feather.replace();
      });
      
      await fetchRoles();
      
      document.addEventListener('click', handleClickOutside);
      
      if ('IntersectionObserver' in window) {
        const options = {
          root: null,
          rootMargin: '0px',
          threshold: 0.5,
        };
        
        const observer = new IntersectionObserver((entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting && roleStore.hasMoreData && !roleStore.loading) {
              roleStore.loadMoreRoles();
            }
          });
        }, options);
        
        const loadMoreTrigger = document.getElementById('load-more-trigger');
        if (loadMoreTrigger) {
          observer.observe(loadMoreTrigger);
        }
      }
      
      return () => {
        document.removeEventListener('click', handleClickOutside);
      };
    });

    return {
      roleStore,
      searchQuery,
      roles,
      filteredRoles,
      paginatedRoles,
      currentPage,
      totalPages,
      paginationStart,
      paginationEnd,
      displayedPages,
      goToPage,
      showTooltip,
      activeDropdown,
      roleIdToDelete,
      shouldShowTooltip,
      toggleDropdown,
      formatDate,
      toggleRoleStatus,
      prepareNewRole,
      viewRoleDetails,
      editRole,
      deleteRole,
      confirmDeleteRole,
      handleSearch,
      clearSearch,
      handleToastClose,
      hasFetchedInitialData,
      hasPermission,
    };
  }
});
  </script>
  
  <style scoped>
  .page-header {
    margin-bottom: 1.5rem;
  }
  
  .hover-bg:hover {
    background-color: rgba(var(--bs-primary-rgb), 0.1);
  }
  
  .btn-add-role {
    transition: all 0.3s ease;
  }
  
  .btn-add-role:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }
  
  .search-input {
    max-width: 300px;
    margin-left: auto;
  }
  
  .cursor-pointer {
    cursor: pointer;
  }
  
  .entity-card {
    height: 450px;
    display: flex;
    flex-direction: column;
    background-color: white;
    border-radius: 0.75rem;
    border: 1px solid #e0e0e0 !important;
    transition: all 0.3s ease;
    margin-bottom: 1rem;
  }
  
  .entity-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
    border-color: #d0d0d0 !important;
  }
  
  .card-body {
    display: flex;
    flex-direction: column;
    flex: 1;
  }
  
  .description-container {
    height: 48px; 
    margin-bottom: 1rem;
    position: relative;
    overflow: visible;
  }
  
  .description-wrapper {
    height: 100%;
    overflow: hidden;
  }
  
  .description-truncate {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-overflow: ellipsis;
    word-break: break-word;
  }
  
  .custom-tooltip {
    position: absolute;
    z-index: 1000;
    background-color: white;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    padding: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    width: 100%;
    max-height: 300px;
    overflow-y: auto;
    top: 105%;
    left: 0;
    font-size: 0.9rem;
    line-height: 1.5;
    animation: fadeIn 0.2s ease-in-out;
    word-break: break-word;
  }
  
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  .dropdown-menu {
    display: none;
  }
  
  .dropdown-menu.show {
    display: block;
    z-index: 1050;
  }
  
  .dropdown {
    z-index: 100;
  }
  
  .hover:hover {
    cursor: pointer;
    opacity: 0.7;
  }
  
  .dropdown-item {
    padding: 0.5rem 1rem;
    display: flex;
    align-items: center;
  }
  
  .dropdown-item:hover {
    background-color: rgba(0, 0, 0, 0.05);
  }
  
  .empty-state-container {
    padding: 2rem 0;
  }
  
  .empty-state-icon {
    background-color: #f8f9fa;
    width: 80px;
    height: 80px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto;
  }
  
  .pagination-container {
    border-top: 1px solid #e9ecef;
    padding-top: 1rem;
  }
  
  .pagination {
    margin-bottom: 0;
  }
  
  .page-link {
    color: #6c757d;
    border-color: #dee2e6;
    padding: 0.375rem 0.75rem;
  }
  
  .page-item.active .page-link {
    background-color: #0d6efd;
    border-color: #0d6efd;
    color: white;
  }
  
  .page-item.disabled .page-link {
    color: #adb5bd;
  }
  
  .page-separator {
    pointer-events: none;
  }
  
  .pagination-info {
    color: #6c757d;
    font-size: 0.875rem;
  }
  
  .col-xxl-3.col-lg-4.col-sm-6 {
    display: flex;
  }
  
  .col-xxl-3.col-lg-4.col-sm-6 > .card {
    width: 100%;
  }
  
  @media (max-width: 767.98px) {
    .search-input {
      max-width: 100%;
    }
    
    .pagination-container {
      flex-direction: column;
      gap: 1rem;
    }
  }
  </style>