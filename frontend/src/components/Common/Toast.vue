<template>
    <div 
      class="toast position-fixed top-0 end-0 m-3" 
      :class="{ 
        'show': show, 
        'bg-success text-white': type === 'success',
        'bg-danger text-white': type === 'error',
        'bg-warning': type === 'warning',
        'bg-info text-white': type === 'info'
      }"
      role="alert" 
      aria-live="assertive" 
      aria-atomic="true"
      style="z-index: 9999;"
    >
      <div class="d-flex">
        <div class="toast-body d-flex align-items-center">
          <i 
            class="me-2" 
            :class="{
              'ri-check-line': type === 'success',
              'ri-error-warning-line': type === 'error',
              'ri-alert-line': type === 'warning',
              'ri-information-line': type === 'info'
            }"
          ></i>
          {{ message }}
        </div>
        <button type="button" class="btn-close me-2 m-auto" @click="$emit('close')"></button>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'Toast',
    props: {
      show: {
        type: Boolean,
        default: false
      },
      message: {
        type: String,
        default: ''
      },
      type: {
        type: String,
        default: 'success',
        validator: (value) => {
          return ['success', 'error', 'warning', 'info'].includes(value);
        }
      },
      autoClose: {
        type: Boolean,
        default: true
      },
      duration: {
        type: Number,
        default: 3000
      }
    },
    emits: ['close'],
    watch: {
      show(newValue) {
        if (newValue && this.autoClose) {
          setTimeout(() => {
            this.$emit('close');
          }, this.duration);
        }
      }
    }
  };
  </script>
  
  <style scoped>
  .toast {
    min-width: 280px;
    box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
    border: none;
    animation: toast-in 0.3s ease-out;
  }
  
  @keyframes toast-in {
    from {
      transform: translateY(-100%);
      opacity: 0;
    }
    to {
      transform: translateY(0);
      opacity: 1;
    }
  }
  
  .toast.show {
    display: block;
    opacity: 1;
  }
  
  .toast-body {
    padding: 0.75rem 1rem;
    font-size: 0.9rem;
  }
  
  .btn-close {
    align-self: center;
    opacity: 0.8;
  }
  
  .btn-close:hover {
    opacity: 1;
  }
  </style>