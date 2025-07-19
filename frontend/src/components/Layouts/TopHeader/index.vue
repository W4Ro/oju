<template>
  <header
    :class="[
      'header-area bg-white mb-4 rounded-bottom-15',
      { sticky: isSticky },
    ]"
  >
    <div class="row align-items-center">
      <div class="col-lg-4 col-sm-6">
        <div class="left-header-content">
          <ul
            class="d-flex align-items-center ps-0 mb-0 list-unstyled justify-content-center justify-content-sm-start"
          >
            <li>
              <button
                class="header-burger-menu bg-transparent p-0 border-0"
                :class="[
                  'header-burger-menu bg-transparent p-0 border-0',
                  { active: stateStoreInstance.open },
                ]"
                @click="stateStoreInstance.onChange"
              >
                <span class="material-symbols-outlined">{{ stateStoreInstance.open ? 'chevron_right' : 'chevron_left' }}</span>
              </button>
            </li>
          </ul>
        </div>
      </div>

      <div class="col-lg-8 col-sm-6">
        <div class="right-header-content mt-2 mt-sm-0">
          <ul
            class="d-flex align-items-center justify-content-center justify-content-sm-end ps-0 mb-0 list-unstyled"
          >
            <li class="header-right-item">
              <DarkSwtichBtn />
            </li>
            <li class="header-right-item">
              <ToggleFullscreenBtn />
            </li>
            <li class="header-right-item">
              <AdminProfile />
            </li>
          </ul>
        </div>
      </div>
    </div>
  </header>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from "vue";
import stateStore from "../../../utils/store";

import DarkSwtichBtn from "./DarkSwtichBtn.vue";
import ToggleFullscreenBtn from "./ToggleFullscreenBtn.vue";
import AdminProfile from "./AdminProfile.vue";
import SettingsBtn from "./SettingsBtn.vue";

export default defineComponent({
  name: "TopHeader",
  components: {
    DarkSwtichBtn,
    ToggleFullscreenBtn,
    AdminProfile,
  },
  setup() {
    const stateStoreInstance = stateStore;
    const isSticky = ref(false);

    onMounted(() => {
      window.addEventListener("scroll", () => {
        let scrollPos = window.scrollY;
        isSticky.value = scrollPos >= 100;
      });
    });

    return {
      isSticky,
      stateStoreInstance,
    };
  },
});
</script>
