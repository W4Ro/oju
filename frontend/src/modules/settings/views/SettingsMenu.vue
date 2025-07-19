<template>
    <ul class="ps-0 mb-4 list-unstyled d-flex flex-wrap gap-2 gap-lg-3">
      <li>
        <RouterLink
          to="/settings/myaccount-settings"
          class="btn btn-primary border border-primary bg-transparent text-primary py-2 px-3 fw-semibold"
        >
          Account settings
        </RouterLink>
      </li>
      <li>
        <RouterLink
          to="/settings/change-mypassword"
          class="btn btn-primary border border-primary bg-transparent text-primary py-2 px-3 fw-semibold"
        >
          Change password
        </RouterLink>
      </li>
    </ul>
  </template>
  
  <script setup lang="ts">
  import { defineComponent } from "vue";
  
  defineComponent({
    name: "SettingsMenu",
  });
  </script>
  
  <style scoped>
  ul li .bg-transparent.router-link-active {
    color: #fff !important;
    background-color: #605dff !important;
  }
  </style>