<template>
  <div class="light-dark">
    <button
      class="switch-toggle settings-btn dark-btn p-0 bg-transparent"
      @click="toggleTheme"
    >
      <span>
        <i class="material-symbols-outlined">{{ icon }}</i>
      </span>
    </button>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from "vue";

export default defineComponent({
  name: "DarkSwitchBtn",
  setup() {
    const icon = ref("light_mode");

    const toggleTheme = () => {
      const body = document.body;
      const darkThemeClass = "dark-theme";

      if (body.classList.contains(darkThemeClass)) {
        body.classList.remove(darkThemeClass);
        icon.value = "light_mode";
        localStorage.setItem("theme", "light");
      } else {
        body.classList.add(darkThemeClass);
        icon.value = "dark_mode";
        localStorage.setItem("theme", "dark");
      }
    };

    onMounted(() => {
      const savedTheme = localStorage.getItem("theme");
      if (savedTheme === "dark") {
        document.body.classList.add("dark-theme");
        icon.value = "dark_mode";
      }
    });

    return {
      icon,
      toggleTheme,
    };
  },
});
</script>
