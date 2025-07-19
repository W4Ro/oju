<template>
  <div class="main-content-container overflow-hidden">
    <PageTitle pageTitle="Entities" />
  </div>
  <div class="container-fluid">
    <div class="row page-header align-items-center mb-4">
      <div class="col-md-6 d-flex align-items-center">
        <button
          v-if="hasPermission('entities_create')"
          class="btn btn-outline-primary py-1 px-2 px-sm-4 fs-14 fw-medium rounded-3 hover-bg btn-add-entity"
          data-bs-toggle="modal"
          data-bs-target="#entityModal"
        >
          <span class="py-sm-1 d-block">
            <i class="ri-add-line me-1"></i>
            <span>Add entity</span>
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
              placeholder="Search"
              v-model="searchQuery"
              @input="handleSearchInput"
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
        <EntityList :search-query="searchQuery" />
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted, watch } from 'vue';
import EntityList from '@/components/Entity/EntityList.vue';
import PageTitle from "@/components/Common/PageTitle.vue";
import feather from 'feather-icons';
import { hasPermission } from '@/utils/permissions';
import { useEntityStore } from '@/stores/entityStore';
import { debounce } from 'lodash';

export default defineComponent({
  name: 'EntityIndex',
  components: {
    EntityList,
    PageTitle,
  },
  setup() {
    const searchQuery = ref('');
    const entityStore = useEntityStore();
    
    // const prepareNewEntity = () => {
    // };
    
    onMounted(() => {
      feather.replace();
      entityStore.fetchEntities(1, '');
    });
    
    const handleSearchInput = debounce(() => {
      entityStore.fetchEntities(1, searchQuery.value);
    }, 500);
    
    const clearSearch = () => {
      searchQuery.value = '';
      entityStore.fetchEntities(1, '');
    };
    
    return {
      searchQuery,
      // prepareNewEntity,
      hasPermission,
      handleSearchInput,
      clearSearch
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
.btn-add-entity {
  transition: all 0.3s ease;
}
.btn-add-entity:hover {
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
@media (max-width: 767.98px) {
  .search-input {
    max-width: 100%;
  }
}
</style>