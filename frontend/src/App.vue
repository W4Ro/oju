<template>
  <div>
    <Preloader v-if="isLoading" />
    <LeftSidebar v-if="shouldShowSidebar && !isNotFound" />
    <div class="container-fluid">
      <div
        class="main-content d-flex flex-column"
        :class="{ 'p-0': shouldShowPaddingZero || isNotFound }"
      >
        <TopHeader v-if="shouldShowHeader && !isNotFound" />
        <router-view />
        <div class="flex-grow-1" v-if="shouldShowDiv && !isNotFound"></div>
        <MainFooter v-if="shouldShowFooter && !isNotFound" />
      </div>
    </div>
    
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, watchEffect, computed } from "vue";
import { useRoute } from "vue-router";
import stateStore from "./utils/store";
import Preloader from "./components/Layouts/Preloader.vue";
import LeftSidebar from "./components/Layouts/LeftSidebar.vue";
import TopHeader from "./components/Layouts/TopHeader/index.vue";
import MainFooter from "./components/Layouts/MainFooter.vue";

export default defineComponent({
  name: "App",
  components: {
    Preloader,
    LeftSidebar,
    TopHeader,
    MainFooter,
  },
  setup() {
    const isLoading = ref(true);
    const route = useRoute();
    const hiddenRoutes = [
      "/403",
      "/dashboard/carousel",
      "/authentication/login",
      "/authentication/register",
      "/authentication/reset-password",
      "/authentication/reset-password/:token",
      "/authentication/forget-password",
      "/authentication/logout",
      "/authentication/confirm-mail",
      "/carousel"
    ];

    const shouldShowSidebar = computed(() => {
      return !hiddenRoutes.some(hiddenRoute => 
        new RegExp(`^${hiddenRoute.replace(':token', '[^/]+')}$`).test(route.path)
      );
    });

    const shouldShowPaddingZero = computed(() => 
      hiddenRoutes.some(hiddenRoute => 
        new RegExp(`^${hiddenRoute.replace(':token', '[^/]+')}$`).test(route.path)
      )
    );

    const shouldShowHeader = computed(() => {
      return !hiddenRoutes.some(hiddenRoute => 
        new RegExp(`^${hiddenRoute.replace(':token', '[^/]+')}$`).test(route.path)
      );
    });

    const shouldShowDiv = computed(() => {
      return !hiddenRoutes.some(hiddenRoute => 
        new RegExp(`^${hiddenRoute.replace(':token', '[^/]+')}$`).test(route.path)
      );
    });

    const shouldShowFooter = computed(() => {
      return !hiddenRoutes.some(hiddenRoute => 
        new RegExp(`^${hiddenRoute.replace(':token', '[^/]+')}$`).test(route.path)
      );
    });

    const isNotFound = computed(() =>
      route.matched.some((record) => record.path === "/:pathMatch(.*)*")
    );

    onMounted(() => {
      setTimeout(() => {
        isLoading.value = false;
      }, 1000);
      
      watchEffect(() => {
        if (stateStore.open) {
          document.body.classList.remove("sidebar-show");
          document.body.classList.add("sidebar-hide");
        } else {
          document.body.classList.remove("sidebar-hide");
          document.body.classList.add("sidebar-show");
        }
      });
    });

    return {
      isLoading,
      shouldShowSidebar,
      shouldShowPaddingZero,
      shouldShowHeader,
      shouldShowDiv,
      shouldShowFooter,
      isNotFound,
    };
  },
});
</script>

<style lang="scss" scoped>
.padding-0 {
  .container-fluid {
    padding: 0;
  }
}
</style>
