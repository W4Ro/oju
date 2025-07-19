<template>
  <div v-if="show">
    <div class="modal-backdrop fade show"></div>
    <div class="modal fade show d-block" tabindex="-1" aria-labelledby="resetDefacementLabel" aria-modal="true" role="dialog">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header bg-warning text-dark">
            <h3 class="modal-title fs-5 mb-1 text-center" id="resetDefacementLabel">
              Confirm Reset
            </h3>
            <button type="button" class="btn-close" @click="closeModal" aria-label="Fermer"></button>
          </div>
          <div class="modal-body">
            <p class="mb-1">Do you really want to reset to normal?</p>
            <p class="mb-2"><strong>{{ platformUrl }}</strong></p>
            <div class="alert alert-warning">
              <i class="ri-alert-line me-2"></i>
              This action is irreversible.
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeModal">Non</button>
            <button
              type="button"
              class="btn btn-warning text-dark"
              @click="confirmReset"
              :disabled="isResetting"
            >
              <span v-if="isResetting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              Yes, reset.
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  platformUrl: {
    type: String,
    default: ''
  },
  isResetting: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['confirm', 'cancel']);

function confirmReset() {
  emit('confirm');
}

function closeModal() {
  emit('cancel');
}
</script>
