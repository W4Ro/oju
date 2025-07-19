<template>
  <ConfirmMail />
</template>

<script lang="ts">
import { defineComponent } from "vue";
import ConfirmMail from "@/components/auth/confirm.vue";

export default defineComponent({
  name: "ConfirmMailPage",
  components: {
    ConfirmMail,
  },
});
</script>
