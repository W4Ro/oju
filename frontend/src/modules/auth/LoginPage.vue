<template>
  <Login />
</template>

<script lang="ts">
import { defineComponent, onMounted, onBeforeUnmount } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth.store";
import Login from "@/components/auth/login.vue";

export default defineComponent({
  name: "LoginPage",
  components: {
    Login,
  },
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();
    onMounted(async () => {
      document.body.classList.add("bg-white");
      const isAuthenticated = await authStore.checkAuth();
      if (isAuthenticated) {
        router.push('/dashboard');
      }
    });

    onBeforeUnmount(() => {
      document.body.classList.remove("bg-white");
    });
  },
});
</script>
