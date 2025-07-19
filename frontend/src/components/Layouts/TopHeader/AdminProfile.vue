<template>
  <div class="dropdown admin-profile">
    <div
      class="d-xxl-flex align-items-center bg-transparent border-0 text-start p-0 cursor dropdown-toggle"
      data-bs-toggle="dropdown"
      aria-expanded="false"
    >
      <div class="flex-shrink-0">
        <img
          class="rounded-circle wh-40 administrator"
          src="@/assets/images/profileimge.png"
          alt="admin"
          style="width: 30px; height: 30px"
        />
      </div>
      <div class="flex-grow-1 ms-2">
        <div class="d-flex align-items-center justify-content-between">
          <div class="d-none d-xxl-block">
            <div class="d-flex align-content-center">
              <h3>{{user?.username || 'User'}}</h3>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="dropdown-menu border-0 bg-white dropdown-menu-end">
      <div class="d-flex align-items-center info">
        <div class="flex-shrink-0">
          <img
            class="rounded-circle wh-30 administrator"
            src="@/assets/images/profileimge.png"
            alt="admin"
          />
        </div>
        <div class="flex-grow-1 ms-2">
          <h3 class="fw-medium">{{user?.nom_prenom || 'User'}}</h3>
          <span class="fs-12">{{user?.role_name}}</span>
        </div>
      </div>

      <ul class="admin-link ps-0 mb-0 list-unstyled">
        <li>
          <RouterLink
            class="dropdown-item d-flex align-items-center text-body"
            to="/settings/myaccount-settings"
          >
            <i class="material-symbols-outlined">account_circle</i>
            <span class="ms-2">My profile</span>
          </RouterLink>
        </li>
        
      </ul>

      <ul class="admin-link ps-0 mb-0 list-unstyled">
        
        <li>
          <RouterLink
            class="dropdown-item d-flex align-items-center text-body"
            to="/authentication/logout"
          >
            <i class="material-symbols-outlined">logout</i>
            <span class="ms-2">Logout</span>
          </RouterLink>
        </li>
      </ul>
    </div>
  </div>
</template>


<script>
import { defineComponent, computed } from 'vue';
import { useAuthStore } from '@/stores/auth.store';

export default defineComponent({
  name: "AdminProfile",
  setup() {
    const authStore = useAuthStore();
    
    const user = computed(() => authStore.user);
    
    return {
      user
    };
  }
});
</script>
