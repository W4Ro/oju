<template>
  <div class="card bg-white border-0 rounded-3 mb-4">
    <div class="card-body p-0">
      <div class="p-4">
        <h3 class="mb-0 fs-16 fw-semibold">Last 10 alerts</h3>
      </div>
      <div v-if="isLoading" class="p-4 text-center">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      
      <div v-else-if="error" class="p-4 text-center text-danger">
        {{ error }}
      </div>
      <div v-else-if="items.length === 0" class="no-data p-5 text-center">
        No alerts available.
      </div>
      <div v-else class="default-table-area style-two">
        <div class="table-responsive">
          <table class="table align-middle">
            <thead>
              <tr>
                <!-- <th scope="col">ID</th> -->
                <th scope="col">Entity</th>
                <th scope="col">URL</th>
                <th scope="col">Date</th>
                <th scope="col">Alert Type</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in items.slice(0, 10)" :key="item.id">
                <!-- <td class="text-body">
                  {{ item.id.substring(0, 8) }}...
                </td> -->
                <td>{{ item.ententy }}</td>
                <td>
                  <a 
                    :href="item.url" 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    class="text-body"
                  >
                    {{ item.url }}
                  </a>
                </td>
                <td class="text-body">
                  {{ item.created_at }}
                </td>
                <td>{{ item.case }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, onBeforeUnmount } from "vue";
import api from '@/api/index';

export default defineComponent({
  name: "LastAlerts",
  setup() {
    const items = ref([]);
    const isLoading = ref(true);
    const error = ref<string | null>(null);

    const loadAlerts = async () => {
      try {
        isLoading.value = true;
        error.value = null;
        
        const response = await api.get('/dashboard/recent-alerts/');
        
        items.value = response.data.map((item: any) => ({
          id: item.id,
          url: item.url,
          case: item.type,
          created_at: item.created_at,
          ententy: item.entity
        }));
        
      } catch (err) {
        error.value = "Unable to load data";
      } finally {
        isLoading.value = false;
      }
    };

    const REFRESH_INTERVAL = 60_000; 
    let intervalId: number;

    onMounted(() => {
      loadAlerts();
      intervalId = window.setInterval(loadAlerts, REFRESH_INTERVAL);
    });

     onBeforeUnmount(() => {
      clearInterval(intervalId);                     
    });

    return {
      items,
      isLoading,
      error
    };
  },
});
</script>

<style scoped>
.no-data {
  color: #8695AA;
  font-style: italic;
  min-height: 100px;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>