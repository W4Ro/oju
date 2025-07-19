<template>
  <div class="card custom-shadow rounded-3 bg-white border mb-4">
    <div class="custom-padding-30">
      <div
        class="d-flex justify-content-between align-items-center flex-wrap gap-3 pb-4"
      >
        <h3 class="mb-0 fw-semibold">Statistiques</h3>
      </div>

      <div id="nav-tab" class="call-overview-tabs" role="tablist">
        <div class="row justify-content-center">
          <div class="col-md-6 col-sm-6">
            <div
              class="card bg-primary bg-opacity-10 border-0 rounded-3 p-4 mb-4 calls-card active"
              id="nav-total-calls-tab"
              data-bs-toggle="tab"
              data-bs-target="#nav-total-calls"
              type="button"
              role="tab"
              aria-controls="nav-total-calls"
              aria-selected="true"
            >
              <div class="d-flex align-items-center mb-3">
                <div class="flex-grow-1 me-3">
                  <span class="text-body d-block mb-1">Total Entities</span>
                  <h3 class="fs-24 fw-semibold text-secondary">{{ totalData.entities || 0 }}</h3>
                </div>

                <div class="flex-shrink-0">
                  <img
                    src="@/assets/images/icon-resigned.svg"
                    alt="total-calls"
                  />
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-6 col-sm-12">
            <div
              class="card bg-dangers border-0 rounded-3 p-4 mb-4 calls-card"
              id="nav-missed-calls-tab"
              data-bs-toggle="tab"
              data-bs-target="#nav-missed-calls"
              type="button"
              role="tab"
              aria-controls="nav-missed-calls"
              aria-selected="false"
              style="background-color: #fff5ed"
            >
              <div class="d-flex align-items-center mb-3">
                <div class="flex-grow-1 me-3">
                  <span class="text-body d-block mb-1">Total Sites</span>
                  <h3 class="fs-24 fw-semibold text-secondary">{{ totalData.sites || 0 }}</h3>
                </div>

                <div class="flex-shrink-0">
                  <img
                    src="@/assets/images/icon-resigned.svg"
                    alt="missed-calls"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="tab-content" id="nav-tabContent">
        <div
          class="tab-pane fade show active"
          id="nav-total-calls"
          role="tabpanel"
          aria-labelledby="nav-total-calls-tab"
          tabindex="0"
        >
          <div style="margin: -24px -10px -26px -18px">
            <TotalEntities :entities-data="entitiesData" :is-loading="isLoadingEntities" />
          </div>
        </div>
        <div
          class="tab-pane fade"
          id="nav-missed-calls"
          role="tabpanel"
          aria-labelledby="nav-missed-calls-tab"
          tabindex="0"
        >
          <div style="margin: -24px -10px -26px -18px">
            <TotalSites :sites-data="sitesData" :is-loading="isLoadingSites"  />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import {ref, onMounted, reactive } from "vue";
  import TotalEntities from "./EntitieChart.vue";
  import TotalSites from "./SitesChart.vue";
  import api from '@/api/index';

  const totalData = reactive({
    entities: 0,
    sites: 0
  });
  const entitiesData = ref(null);
  const sitesData = ref(null);

  const isLoadingTotals = ref(true);
  const isLoadingEntities = ref(true);
  const isLoadingSites = ref(true);

  const loadTotals = async () => {
    try {
      isLoadingTotals.value = true;
      const response = await api.get('/dashboard/total');
      totalData.entities = response.data.total_entities || 0;
      totalData.sites = response.data.total_platforms || 0;
    } catch (error) {
      console.error("Error while loading data");
    } finally {
      isLoadingTotals.value = false;
    }
  };
  const loadEntitiesData = async () => {
    try {
      isLoadingEntities.value = true;
      const response = await api.get('/dashboard/entity-statistics');
      entitiesData.value = response.data;
    } catch (error) {
      console.error("Error while loading data");
    } finally {
      isLoadingEntities.value = false;
    }
  };

  const loadSitesData = async () => {
    try {
      isLoadingSites.value = true;
      const response = await api.get('/dashboard/platform-statistics');
      sitesData.value = response.data;
    } catch (error) {
      console.error("Error while loading data");
    } finally {
      isLoadingSites.value = false;
    }
  };

  onMounted(() => {
    loadTotals();
    loadEntitiesData();
    loadSitesData();
  });
</script>

<style scoped>
.row.justify-content-center {
  display: flex;
  flex-wrap: wrap;
}

.col-md-6 {
  flex: 0 0 auto;
  width: 50%;
  max-width: 50%;
}

@media (max-width: 767.98px) {
  .col-md-6.col-sm-6 {
    width: 50%;
  }
  
  .col-md-6.col-sm-12 {
    width: 100%;
  }
}
</style>