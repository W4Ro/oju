<template>
  <div class="card entity-card">
    <div class="card-body p-4">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <div class="d-flex align-items-center">
        </div>

        <div class="dropdown action-opt ms-2 position-relative top-3">
          <button
            class="p-0 border-0 bg-transparent"
            type="button"
            @click.stop="toggleDropdown"
            v-if="hasAnyPermission(['focal_points_view', 'entities_edit', 'entities_delete'])"
          >
            <i class="material-symbols-outlined fs-20 fw-bold text-body hover">
              more_horiz
            </i>
          </button>
          <ul class="dropdown-menu dropdown-menu-end bg-white border box-shadow" :class="{ 'show': isDropdownOpen }">
            <li v-if="hasPermission('focal_points_view')">
              <a class="dropdown-item" href="javascript:;" @click.stop="$emit('view-focal-points', entity.id)">
                <i class="ri-user-line me-2"></i>
                Focal points
              </a>
            </li>
            <li v-if="hasPermission('entities_edit')">
              <a class="dropdown-item" href="javascript:;" @click.stop="$emit('edit-entity', entity)">
                <i class="ri-edit-line me-2"></i>
                Edit
              </a>
            </li>
            <li v-if="hasPermission('entities_delete')">
              <a class="dropdown-item" href="javascript:;" @click.stop="$emit('delete-entity', entity)">
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
        {{ entity.name }}
      </span>
      <div class="description-container" @mouseenter="showTooltip = true" @mouseleave="showTooltip = false">
        <div class="description-wrapper">
          <span class="description-truncate">{{ entity.description }}</span>
        </div>
        <div class="custom-tooltip" v-if="shouldShowTooltip && showTooltip">
          {{ entity.description }}
        </div>
      </div>
      <ul class="ps-0 mb-4 list-unstyled">
        <li class="mb-2 pb-1">
          <span class="text-secondary fw-bold">Created at: </span>
          <span>{{ formatDate(entity.created_at)}}</span>
        </li>

        <li class="mb-2 pb-1">
          <span class="text-secondary fw-bold">Updated at: </span>
          <span>{{ formatDate(entity.updated_at) }}</span>
        </li>

        <li class="mb-2 pb-1">
          <span class="text-secondary fw-bold">Number of platforms: </span>
          <span>{{ entity.platforms_count }}</span>
        </li>
      </ul>
      <div class="pb-md-2">
        <div class="d-flex justify-content-between mb-2">
          <span class="fw-medium d-block">{{ entity.alerts_count || 0 }} cases</span>
          <span class="fw-medium d-block">{{ calculatePercentage(entity) }}%</span>
        </div>
        <div
          class="progress bg-primary bg-opacity-10"
          style="height: 4px"
          role="progressbar"
          aria-label="Primary example"
          :aria-valuenow="calculatePercentage(entity)"
          aria-valuemin="0"
          aria-valuemax="100"
        >
          <div
            class="progress-bar bg-primary"
            :style="{ width: calculatePercentage(entity) + '%', height: '4px' }"
          ></div>
        </div>
      </div>
      
      <button
        @click="$emit('view-details', entity.id)"
        class="btn btn-outline-primary fw-medium w-100 py-2 rounded-3"
      >
        view details
      </button>
    </div>
  </div>
</template>
  
<script>
  import { ref, onMounted, onBeforeUnmount, computed } from 'vue';
  import { hasPermission, hasAnyPermission } from '@/utils/permissions';
  
  
  export default {
    name: "EntityCard",
    props: {
      entity: {
        type: Object,
        required: true
      }
    },
    emits: ['view-details', 'view-focal-points', 'edit-entity', 'delete-entity'],
    setup(props) {
      const isDropdownOpen = ref(false);
      const showTooltip = ref(false);
      
      const shouldShowTooltip = computed(() => {
        if (!props.entity.description) return false;
        
        return props.entity.description.length > 100 || 
               props.entity.description.split('\n').length > 2;
      });

      const calculatePercentage = (entity) => {
      if (entity.alerts_resolution_percentage) {
        return parseFloat(entity.alerts_resolution_percentage);
      }
      
      return 0;
    };
      
      const toggleDropdown = (event) => {
        event.stopPropagation();
        isDropdownOpen.value = !isDropdownOpen.value;
      };
      
      const handleClickOutside = (event) => {
        if (isDropdownOpen.value && !event.target.closest('.dropdown')) {
          isDropdownOpen.value = false;
        }
      };
      
      onMounted(() => {
        document.addEventListener('click', handleClickOutside);
      });
      
      onBeforeUnmount(() => {
        document.removeEventListener('click', handleClickOutside);
      });
      
      return {
        isDropdownOpen,
      toggleDropdown,
      showTooltip,
      shouldShowTooltip,
      calculatePercentage,
      hasPermission,
      hasAnyPermission
      };
    },
    methods: {
      formatDate(dateString) {
        if (!dateString) return "";

        try {
          const date = new Date(dateString);
          if (isNaN(date.getTime())) {
            const parts = dateString.split("-");
            if (parts.length === 3) {
              const day = parts[0];
              const month = parts[1];
              const year = parts[2];

              const monthNames = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"];
              const monthIndex = parseInt(month) - 1;

              return `${day} ${monthNames[monthIndex]} ${year}`;
            }
            return dateString;
          }

          const day = date.getDate().toString().padStart(2, '0');
          const month = date.getMonth();
          const year = date.getFullYear();
          const hours = date.getHours().toString().padStart(2, '0');
          const minutes = date.getMinutes().toString().padStart(2, '0');

          const monthNames = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"];

          return `${day} ${monthNames[month]} ${year} at ${hours}:${minutes}`;
        } catch (error) {
          return dateString;
        }
    }
  }
};
  </script>
  
  <style scoped>
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
  </style>