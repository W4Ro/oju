import { createApp } from "vue";
import { createPinia } from 'pinia';
import App from "./App.vue";
import router from "./router/index";
import { createBootstrap } from "bootstrap-vue-next";
import VueApexCharts from "vue3-apexcharts";
import { QuillEditor } from "@vueup/vue-quill";
import { permissionDirective } from './utils/permissions';

import "@vueup/vue-quill/dist/vue-quill.snow.css";
import "@vueup/vue-quill/dist/vue-quill.bubble.css";
import "bootstrap/dist/css/bootstrap.css";
import 'bootstrap-icons/font/bootstrap-icons.css';
import "bootstrap-vue-next/dist/bootstrap-vue-next.css";
import "swiper/css";
import "swiper/css/bundle";
import "swiper/css/pagination";
import "swiper/css/navigation";

import "./assets/css/remixicon.css";
import "./assets/css/sidebar-menu.css";
import "./assets/css/simplebar.css";
import "./assets/scss/style.css";
import "./assets/css/style.css"

const app   = createApp(App);
const pinia = createPinia();

app.use(pinia);     
app.use(router);

app.use(createBootstrap());
app.use(VueApexCharts);
app.component("QuillEditor", QuillEditor);
app.directive("permission", permissionDirective);
app.mount("#app");