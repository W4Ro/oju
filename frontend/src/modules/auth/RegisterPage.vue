<template>
  <Register />
</template>

<script lang="ts">
import { defineComponent, onBeforeUnmount, onMounted } from "vue";
import Register from "@/components/auth/register.vue";

export default defineComponent({
  name: "RegisterPage",
  components: {
    Register,
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
