<template>
  <button
    class="fullscreen-btn bg-transparent p-0 border-0"
    @click="toggleFullscreen"
  >
    <i class="material-symbols-outlined text-body">fullscreen</i>
  </button>
</template>

<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({
  name: "ToggleFullscreenBtn",
  methods: {
    toggleFullscreen() {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const element = document.documentElement as any;
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const doc = document as any;

      if (!doc.fullscreenElement) {
        // Enter fullscreen mode
        if (element.requestFullscreen) {
          element.requestFullscreen();
        } else if (element.webkitRequestFullscreen) {
          element.webkitRequestFullscreen();
        }
      } else {
        // Exit fullscreen mode
        if (doc.exitFullscreen) {
          doc.exitFullscreen();
        } else if (doc.webkitExitFullscreen) {
          doc.webkitExitFullscreen();
        }
      }
    },
  },
});
</script>
