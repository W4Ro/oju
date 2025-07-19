<template>
  <div
    class="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-4"
  >
    <h3 class="mb-0">{{ pageTitle }}</h3>

    <nav style="--bs-breadcrumb-divider: '>'" aria-label="breadcrumb">
      <ol class="breadcrumb align-items-center mb-0 lh-1">
        <li class="breadcrumb-item">
          <RouterLink
            to="/dashboard"
            class="d-flex align-items-center text-decoration-none"
          >
            <i class="ri-home-4-line fs-18 text-primary me-1"></i>
            <span class="text-secondary fw-medium hover">Dashboard</span>
          </RouterLink>
        </li>
        <li class="breadcrumb-item active" aria-current="page" v-if="subTitle">
          <span class="fw-medium">{{ subTitle }}</span>
        </li>
        <li class="breadcrumb-item active" aria-current="page">
          <span class="fw-medium">{{ pageTitle }}</span>
        </li>
      </ol>
    </nav>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({
  name: "PageTitle",
  props: ["pageTitle", "subTitle"],
});
</script>
