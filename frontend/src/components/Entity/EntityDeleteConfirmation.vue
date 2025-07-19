<template>
    <div class="modal fade" id="deleteModal" tabindex="-1" aria-labelledby="deleteModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header bg-danger text-white">
            <h3 class="modal-title fs-5 mb-1 text-center text-white" id="deleteModalLabel">
              Delete confirmation
            </h3>
            <button type="button" class="btn-close text-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p class="mb-1">Do you realy want to delete this entity ?</p>
            <p class="mb-2"><strong>{{ entityName }}</strong></p>
            <div class="alert alert-warning">
              <i class="ri-alert-line me-2"></i>
              This action is irreversible
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">No</button>
            <button 
              type="button" 
              class="btn btn-danger text-white" 
              @click="confirmDelete"
              :disabled="isDeleting"
            >
              <span v-if="isDeleting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              Yes, Delete!!!
            </button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'DeleteConfirmation',
    props: {
      entityName: {
        type: String,
        default: 'Entity'
      },
      isDeleting: {
        type: Boolean,
        default: false
      }
    },
    emits: ['confirm'],
    methods: {
      confirmDelete() {
        this.$emit('confirm');
      }
    }
  };
  </script>