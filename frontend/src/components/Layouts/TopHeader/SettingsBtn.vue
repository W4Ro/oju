<template>
  <button
    class="theme-settings-btn p-0 border-0 bg-transparent"
    type="button"
    data-bs-toggle="offcanvas"
    data-bs-target="#settingsSidebar"
    aria-controls="settingsSidebar"
  >
    <i class="material-symbols-outlined"> settings </i>
  </button>
</template>

<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({
  name: "SettingsBtn",
});
</script>
