<template>
  <div class="sidebar-area">
    <!-- <div class="logo position-relative">
      <RouterLink
        to="/dashboard"
        class="d-block text-decoration-none position-relative"
      >
        <img src="@/assets/images/logo-icon.png" alt="logo-icon" />
        <span class="logo-text fw-bold text-dark" >Oju</span>
      </RouterLink>
      <button
        class="sidebar-burger-menu bg-transparent p-0 border-0 opacity-0 z-n1 position-absolute top-50 end-0 translate-middle-y"
        id="sidebar-burger-menu"
        @click="stateStoreInstance.onChange"
      >
        <i data-feather="x"></i>
      </button>
    </div> -->

    <div class="layout-menu menu-vertical menu hover-scroll-bar" style="margin-top: 50px;">
      <ul class="menu-inner">
        
        <li class="menu-item">
          <RouterLink to="/dashboard" class="menu-link">
            <span class="material-symbols-outlined menu-icon">dashboard</span>
            <span class="title">Dashboard</span>
          </RouterLink>
        </li>

        <li class="menu-item" v-if="hasPermission('entities_view')">
          <RouterLink to="/entities" class="menu-link">
            <span class="material-symbols-outlined menu-icon">note_stack</span>
            <span class="title">Entities</span>
          </RouterLink>
        </li>

        <li class="menu-item" v-if="hasPermission('alerts_view') && hasPermission('entities_view')">
          <RouterLink to="/history" class="menu-link">
            <span class="material-symbols-outlined menu-icon">notification_important</span>
            <span class="title">Alerts</span>
          </RouterLink>
        </li>

        <li class="menu-item" v-if="hasPermission('defacement_view') && hasPermission('entities_view')">
          <RouterLink to="/defacements/list" class="menu-link">
            <span class="material-symbols-outlined menu-icon">bug_report</span>
            <span class="title">Defacements</span>
          </RouterLink>
        </li>

       <li class="menu-item" v-if="hasPermission('cerb_scans_view')">
          <RouterLink to="/scans" class="menu-link">
            <span class="material-symbols-outlined menu-icon">find_in_page</span>
            <span class="title">Scan</span>
          </RouterLink>
        </li>

        <li class="menu-item" v-if="hasPermission('users_view')">
          <RouterLink to="/users" class="menu-link">
            <span class="material-symbols-outlined menu-icon">group</span>
            <span class="title">Users</span>
          </RouterLink>
        </li>

        <li class="menu-item" v-if="hasPermission('logs_view')">
          <RouterLink to="/logs" class="menu-link">
            <span class="material-symbols-outlined menu-icon">swap_vert</span>
            <span class="title">Logs</span>
          </RouterLink>
        </li>
        
        <li class="menu-item" :class="{ open: isOpen('focalPoint') }" v-if="hasAnyPermission(['focal_points_view', 'focal_functions_view'])">
          <a
            href="javascript:void(0);"
            class="menu-link menu-toggle active"
            @click="toggleMenu('focalPoint')"
          >
            <span class="material-symbols-outlined menu-icon">target</span>
            <span class="title">Focal </span>
          </a>
          <ul class="menu-sub" v-show="isOpen('focalPoint')">
            <li class="menu-item" v-if="hasPermission('focal_functions_view')">
              <RouterLink to="/focal/functions" class="menu-link">
                Functions
              </RouterLink>
            </li>
            <li class="menu-item" v-if="hasPermission('focal_points_view')">
              <RouterLink to="/focal/points" class="menu-link">
                Points
              </RouterLink>
            </li>
          </ul>
        </li>

        <li class="menu-item" :class="{ open: isOpen('config') }" v-if="hasAnyPermission(['roles_view', 'mail_settings_view', 'integrations_view', 'config_view'])">
          <a
            href="javascript:void(0);"
            class="menu-link menu-toggle active"
            @click="toggleMenu('config')"
          >
            <span class="material-symbols-outlined menu-icon">settings</span>
            <span class="title">Config</span>
          </a>
          <ul class="menu-sub" v-show="isOpen('config')">
            <li class="menu-item" v-if="hasPermission('roles_view')">
              <RouterLink to="/config/roles" class="menu-link"> Roles </RouterLink>
            </li>
            <li class="menu-item" v-if="hasPermission('mail_settings_view')">
              <RouterLink to="/config/mail-settings" class="menu-link">
                Email Settings
              </RouterLink>
            </li>
            <li class="menu-item" v-if="hasPermission('integrations_view')">
              <RouterLink to="/config/integrations" class="menu-link">
              Integration
              </RouterLink>
            </li>
            <li class="menu-item" v-if="hasPermission('config_view')">
              <RouterLink to="/config/general-settings" class="menu-link"> General Settings </RouterLink>
            </li>
            
          </ul>
        </li>

         <li class="menu-item" v-if="hasPermission('vendor_list_view')">
          <RouterLink to="/vendor" class="menu-link">
            <span class="material-symbols-outlined menu-icon">store</span>
            <span class="title">Vendor</span>
          </RouterLink>
         </li>

         <li class="menu-item" v-if="hasPermission('dashboard_carousel_view') && hasPermission('platforms_view ')">
          <RouterLink to="/dashboard/carousel" class="menu-link">
            <span class="material-symbols-outlined menu-icon">view_carousel</span>
            <span class="title">Carousel</span>
          </RouterLink>
         </li>
               <li class="menu-item">
          <RouterLink to="/authentication/logout" class="menu-link">
            <span class="material-symbols-outlined menu-icon">logout</span>
            <span class="title">Logout</span>
          </RouterLink>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted, computed } from "vue";
import { useAuthStore } from '@/stores/auth.store';
import {hasAnyPermission, hasPermission} from "@/utils/permissions";
import feather from "feather-icons";
import stateStore from "../../utils/store";

export default defineComponent({
  name: "LeftSidebar",
  setup() {
    const stateStoreInstance = stateStore;
    const authStore = useAuthStore();
    
    const openMenu = ref(null);

    const toggleMenu = (menu) => {
      openMenu.value = openMenu.value === menu ? null : menu;
    };

    const isOpen = (menu) => {
      return openMenu.value === menu;
    };
    
    const hasPermission = (permission) => {
      return authStore.hasPermission(permission);
    };

    onMounted(() => {
      feather.replace();
    });

    return {
      stateStoreInstance,
      toggleMenu,
      isOpen,
      hasPermission,
      hasAnyPermission,
    };
  },
});
</script>
