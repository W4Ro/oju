<template>
  <div>
    <div class="row" v-if="!entityStore.loading || entityStore.entities.length > 0">
      <div v-for="(entity, index) in paginatedEntities" :key="`${entity.id}-${index}`" 
           class="col-xxl-3 col-lg-4 col-sm-6">
        <EntityCard 
          :entity="entity"
          @view-details="viewEntityDetails"
          @edit-entity="editEntity"
          @delete-entity="prepareDeleteEntity"
          @view-focal-points="viewFocalPoints"
        />
      </div>
      
      <div v-if="paginatedEntities.length === 0" class="col-12 text-center py-5">
        <div class="empty-state">
          <i class="ri-inbox-line fs-2 mb-3 text-muted"></i>
          <h4>No entities found</h4>
          <p class="text-muted" v-if="searchQuery">
            No results for "{{ searchQuery }}". Try different search terms.
          </p>
          <p class="text-muted" v-else>
            Start by adding a new entity
          </p>
          <button 
            v-if="!searchQuery && hasPermission('entities_create')"
            class="btn btn-primary mt-3"
            data-bs-toggle="modal"
            data-bs-target="#entityModal"
            @click="prepareNewEntity"
          >
            <i class="ri-add-line me-1"></i>
            Add a entity
          </button>
        </div>
      </div>
    </div>
    
    <div v-if="entityStore.loading && entityStore.entities.length === 0" class="row">
      <div class="col-12 text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-3">Loading entities...</p>
      </div>
    </div>

    <div v-if="filteredEntities && filteredEntities.length > 0" class="d-flex justify-content-between align-items-center mt-4 pagination-container">
      <div class="pagination-info">
        Showing  <span class="fw-medium">{{ paginationStart }}</span> à <span class="fw-medium">{{ paginationEnd }}</span> of <span class="fw-medium">{{ filteredEntities.length }}</span> entity(ies)
      </div>
      <nav aria-label="Pagination des entités">
        <ul class="pagination mb-0">
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <a class="page-link" href="#" @click.prevent="goToPage(currentPage - 1)">
              <i class="ri-arrow-left-s-line"></i>
            </a>
          </li>
          <li 
            v-for="page in displayedPages" 
            :key="page" 
            class="page-item" 
            :class="{ active: currentPage === page, 'page-separator': page === '...' }">
            <span v-if="page === '...'" class="page-link border-0 bg-transparent">...</span>
            <a v-else class="page-link" href="#" @click.prevent="goToPage(page)">
              {{ page }}
            </a>
          </li>
          <li class="page-item" :class="{ disabled: currentPage === totalPages }">
            <a class="page-link" href="#" @click.prevent="goToPage(currentPage + 1)">
              <i class="ri-arrow-right-s-line"></i>
            </a>
          </li>
        </ul>
      </nav>
    </div>
    <div v-if="entityStore.hasMoreData && filteredEntities && filteredEntities.length > 0" class="text-center mt-4">
      <button 
        class="btn btn-outline-primary" 
        @click="loadMoreEntities"
        :disabled="entityStore.loading"
      >
        <span v-if="entityStore.loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
        Load more entity
      </button>
    </div>

    <EntityForm
      :entity-to-edit="entityToEdit"
      :is-submitting="entityStore.isCreating || entityStore.isUpdating"
      @submit="handleEntitySubmit"
      @cancel="resetEntityForm"
    />

    <DeleteConfirmation
      :entity-name="entityToDelete?.name || ''"
      :is-deleting="entityStore.isDeleting"
      @confirm="confirmDeleteEntity"
    />

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
  </div>
</template>

<script>
import { defineComponent, ref, onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useEntityStore } from '@/stores/entityStore';
import EntityCard from '@/components/Entity/EntityCard.vue';
import EntityForm from '@/components/Entity/EntityForm.vue';
import DeleteConfirmation from '@/components/Entity/EntityDeleteConfirmation.vue';
import { Modal } from 'bootstrap';
import {hasPermission} from '@/utils/permissions';

export default defineComponent({
  name: 'EntityList',
  components: {
    EntityCard,
    EntityForm,
    DeleteConfirmation
  },
  props: {
    searchQuery: {
      type: String,
      default: ''
    }
  },
  setup(props) {
    const router = useRouter();
    const entityStore = useEntityStore();

    const entityToEdit = ref(null);
    const entityToDelete = ref(null);
    const itemsPerPage = ref(8);
    const currentPage = ref(1);

    let entityModal = null;
    let deleteModal = null;


    const filteredEntities = computed(() => {
  if (!entityStore.entities || entityStore.entities.length === 0) {
    return []; 
  }

  const sortedEntities = entityStore.sortedEntities;

  if (!props.searchQuery || props.searchQuery.trim() === '') {
    return sortedEntities;
  }
  
  const query = props.searchQuery.toLowerCase().trim();
  return sortedEntities.filter(entity =>
    entity.name.toLowerCase().includes(query) ||
    (entity.description && entity.description.toLowerCase().includes(query))
  );
});

    const totalPages = computed(() => {
      return Math.ceil(filteredEntities.value.length / itemsPerPage.value);
    });

    const paginatedEntities = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage.value;
      return filteredEntities.value.slice(start, start + itemsPerPage.value);
    });

    const paginationStart = computed(() => {
      return filteredEntities.value.length === 0 ? 0 : (currentPage.value - 1) * itemsPerPage.value + 1;
    });

    const paginationEnd = computed(() => {
      return Math.min(currentPage.value * itemsPerPage.value, filteredEntities.value.length);
    });

    const displayedPages = computed(() => {
      const pages = [];
      const maxPagesToShow = 5;
      const total = totalPages.value;
      if (total <= maxPagesToShow) {
        for (let i = 1; i <= total; i++) pages.push(i);
      } else {
        pages.push(1);
        let startPage = Math.max(2, currentPage.value - 1);
        let endPage = Math.min(total - 1, currentPage.value + 1);
        if (startPage > 2) pages.push("...");
        for (let i = startPage; i <= endPage; i++) pages.push(i);
        if (endPage < total - 1) pages.push("...");
        pages.push(total);
      }
      return pages;
    });

    const goToPage = (page) => {
      if (page >= 1 && page <= totalPages.value && page !== currentPage.value) {
        currentPage.value = page;
        if (page >= totalPages.value - 1 && entityStore.hasMoreData) {
          loadMoreEntities();
        }
      }
    };

    const loadMoreEntities = async () => {
      if (entityStore.loading || !entityStore.hasMoreData) return;
      
      await entityStore.loadMoreEntities();
    };

    watch(() => props.searchQuery, () => {
      currentPage.value = 1;
    });

    watch(filteredEntities, () => {
      if (currentPage.value > totalPages.value && totalPages.value > 0) {
        currentPage.value = 1;
      }
    });

    onMounted(async () => {
      if (entityStore.entities.length === 0 && !entityStore.loading) {
        await entityStore.fetchEntities();
      }
      entityModal = new Modal(document.getElementById('entityModal'));
      deleteModal = new Modal(document.getElementById('deleteModal'));
    });

    const prepareNewEntity = () => {
      entityToEdit.value = null;
      if (entityModal) entityModal.show();
    };

    const editEntity = (entity) => {
      entityToEdit.value = entity;
      if (entityModal) entityModal.show();
    };

    const prepareDeleteEntity = (entity) => {
      entityToDelete.value = entity;
      if (deleteModal) deleteModal.show();
    };

    const confirmDeleteEntity = async () => {
      if (!entityToDelete.value) return;
      try {
        await entityStore.deleteEntity(entityToDelete.value.id);
        if (deleteModal) deleteModal.hide();
        entityToDelete.value = null;
      } catch (error) {
        // The error is already handled in the store
      }
    };

    const handleEntitySubmit = async (formData) => {
      try {
        let success = false;
        
        if (entityToEdit.value) {
          const updated = await entityStore.updateEntity(entityToEdit.value.id, {
            name: formData.nom,
            description: formData.description,
            focal_points_ids: formData.pointsFocaux.map(pf => pf.id)
          });
          success = !!updated;
        } else {
          const created = await entityStore.createEntity({
            name: formData.nom,
            description: formData.description,
            focal_points_ids: formData.pointsFocaux.map(pf => pf.id)
          });
          success = !!created;
        }
        
        if (success && entityModal) {
          entityModal.hide();
          resetEntityForm();
        }
      } catch (error) {
        // The error is already handled in the store
      }
    };

    const resetEntityForm = () => {
      entityToEdit.value = null;
    };

    const viewEntityDetails = (entityId) => {
      router.push(`/entitie/details/${entityId}`);
    };

    const viewFocalPoints = (entityId) => {
      router.push(`/entities/focalpoints/${entityId}`);
    };

    return {
      entityStore,
      filteredEntities,
      paginatedEntities,
      entityToEdit,
      entityToDelete,
      itemsPerPage,
      currentPage,
      paginationStart,
      paginationEnd,
      totalPages,
      displayedPages,
      goToPage,
      prepareNewEntity,
      editEntity,
      prepareDeleteEntity,
      confirmDeleteEntity,
      handleEntitySubmit,
      resetEntityForm,
      viewEntityDetails,
      viewFocalPoints,
      loadMoreEntities,
      hasPermission
    };
  }
});
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.pagination-container {
  border-top: 1px solid #e9ecef;
  padding-top: 1rem;
}

.pagination-info {
  color: #6c757d;
  font-size: 0.875rem;
}

.page-item.active .page-link {
  background-color: #0d6efd;
  border-color: #0d6efd;
  color: white;
}

.page-item.disabled .page-link {
  color: #adb5bd;
  pointer-events: none;
}

.toast {
  min-width: 250px;
  transition: opacity 0.3s ease-in-out;
}

.toast.show {
  opacity: 1;
}
</style>