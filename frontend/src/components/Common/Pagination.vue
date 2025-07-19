<template>
  <div
    class="d-flex justify-content-center justify-content-sm-between align-items-center text-center flex-wrap gap-2 showing-wrap"
  >
    <span class="fs-12 fw-medium">
      Showing {{ displayedItemsStart }}-{{ displayedItemsEnd }} of {{ total }} Results
    </span>
    <nav aria-label="Page navigation">
      <ul class="pagination mb-0 justify-content-center">
        <li class="page-item" :class="{ disabled: currentPage === 1 }">
          <a 
            class="page-link icon" 
            href="#" 
            aria-label="Previous"
            @click.prevent="onPageChange(currentPage - 1)"
          >
            <i class="material-symbols-outlined">keyboard_arrow_left</i>
          </a>
        </li>
        
        <li v-if="showFirstButton && currentPage > 3" class="page-item">
          <a 
            class="page-link" 
            href="#" 
            @click.prevent="onPageChange(1)"
          >
            1
          </a>
        </li>
        
        <li v-if="showFirstButton && currentPage > 4" class="page-item disabled">
          <span class="page-link">...</span>
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
            @click.prevent="onPageChange(page)"
          >
            {{ page }}
          </a>
        </li>
        
        <li v-if="showLastButton && currentPage < totalPages - 3" class="page-item disabled">
          <span class="page-link">...</span>
        </li>
        
        <li v-if="showLastButton && currentPage < totalPages - 2" class="page-item">
          <a 
            class="page-link" 
            href="#" 
            @click.prevent="onPageChange(totalPages)"
          >
            {{ totalPages }}
          </a>
        </li>
        
        <li class="page-item" :class="{ disabled: currentPage === totalPages }">
          <a 
            class="page-link icon" 
            href="#" 
            aria-label="Next"
            @click.prevent="onPageChange(currentPage + 1)"
          >
            <i class="material-symbols-outlined">keyboard_arrow_right</i>
          </a>
        </li>
      </ul>
    </nav>
  </div>
</template>

<script>
import { defineComponent, computed, ref, watch } from "vue";

export default defineComponent({
  name: "Pagination",
  props: {
    total: {
      type: Number,
      required: true,
    },
    perPage: {
      type: Number,
      default: 10
    },
    modelValue: {
      type: Number,
      default: 1
    },
    maxVisiblePages: {
      type: Number,
      default: 5
    },
    showEndButtons: {
      type: Boolean,
      default: true
    }
  },
  emits: ["update:modelValue", "page-change"],
  
  setup(props, { emit }) {
    const currentPage = ref(props.modelValue);
    
    watch(() => props.modelValue, (newVal) => {
      currentPage.value = newVal;
    });
    
    const totalPages = computed(() => {
      return Math.max(1, Math.ceil(props.total / props.perPage));
    });
    
    const displayedPages = computed(() => {
      if (totalPages.value <= props.maxVisiblePages) {
        return Array.from({ length: totalPages.value }, (_, i) => i + 1);
      }
      
      const halfVisible = Math.floor(props.maxVisiblePages / 2);
      let startPage = Math.max(1, currentPage.value - halfVisible);
      let endPage = Math.min(totalPages.value, startPage + props.maxVisiblePages - 1);
      
      if (endPage === totalPages.value) {
        startPage = Math.max(1, endPage - props.maxVisiblePages + 1);
      }
      
      return Array.from({ length: endPage - startPage + 1 }, (_, i) => startPage + i);
    });
    
    const showFirstButton = computed(() => {
      return props.showEndButtons && totalPages.value > props.maxVisiblePages;
    });
    
    const showLastButton = computed(() => {
      return props.showEndButtons && totalPages.value > props.maxVisiblePages;
    });
    
    const displayedItemsStart = computed(() => {
      return props.total === 0 ? 0 : (currentPage.value - 1) * props.perPage + 1;
    });
    
    const displayedItemsEnd = computed(() => {
      return Math.min(currentPage.value * props.perPage, props.total);
    });
    
    const onPageChange = (page) => {
      if (page < 1 || page > totalPages.value || page === currentPage.value) {
        return;
      }
      
      currentPage.value = page;
      emit("update:modelValue", page);
      emit("page-change", page);
    };
    
    return {
      currentPage,
      totalPages,
      displayedPages,
      showFirstButton,
      showLastButton,
      displayedItemsStart,
      displayedItemsEnd,
      onPageChange
    };
  }
});
</script>