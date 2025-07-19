<template>
  <ResetPassword />
</template>

<script lang="ts">
import { defineComponent, onBeforeUnmount, onMounted } from "vue";
import ResetPassword from "@/components/auth/ResetPassword.vue";

export default defineComponent({
  name: "ResetPasswordPage",
  components: {
    ResetPassword,
  },
  setup() {
    onMounted(() => {
      document.body.classList.add("bg-white");
    });

    onBeforeUnmount(() => {
      document.body.classList.remove("bg-white");
    });
  },
});
</script>
