<template>
  <div class="main-content-container">
    <PageTitle pageTitle="System Logs"/>

    <div class="card bg-white border-0 rounded-3 mb-4">
      <div class="card-body p-4">

        <div class="filters-section mb-4">
          <div class="row gx-3 gy-3 align-items-center">

            <div class="col-12 col-lg-5">
              <label class="form-label">Date range</label>
              <div class="row gx-2">
                <div class="col-6">
                  <div class="input-group">
                    <span class="input-group-text">From</span>
                    <input type="date" class="form-control" v-model="localFilters.start_date" />
                    <input type="time" class="form-control" v-model="localFilters.start_time" />
                  </div>
                </div>
                <div class="col-6">
                  <div class="input-group">
                    <span class="input-group-text">To</span>
                    <input type="date" class="form-control" v-model="localFilters.end_date" />
                    <input type="time" class="form-control" v-model="localFilters.end_time" />
                  </div>
                </div>
              </div>
            </div>

            <div class="col-12 col-lg-5">
              <label class="form-label">Filters</label>
              <div class="row gx-2">
                <div class="col-6">
                  <input
                    type="text"
                    class="form-control"
                    placeholder="Filter by name"
                    v-model="localFilters.name"
                  />
                </div>
                <div class="col-6">
                  <input
                    type="text"
                    class="form-control"
                    placeholder="General search"
                    v-model="localFilters.search"
                  />
                </div>
              </div>
            </div>

            
            <div class="col-12 col-lg-2 d-flex justify-content-center gap-2 align-self-end">
              <button class="btn btn-primary p-2" @click="applyFilters" title="Apply filters">
                <i data-feather="filter"></i>
              </button>
              <button class="btn btn-outline-secondary p-2" @click="resetFilters" title="Reset filters">
                <i data-feather="refresh-cw"></i>
              </button>
              <div v-if="hasPermission('logs_export')" class="dropdown">
                <button
                  class="btn btn-success p-2 dropdown-toggle"
                  type="button"
                  id="exportDropdown"
                  data-bs-toggle="dropdown"
                  aria-expanded="false"
                  title="Export logs"
                >
                  <i data-feather="download"></i>
                </button>
                <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="exportDropdown">
                  <li>
                    <a class="dropdown-item" href="#" @click.prevent="exportLogs('csv')">CSV</a>
                  </li>
                  <li>
                    <a class="dropdown-item" href="#" @click.prevent="exportLogs('xlsx')">Excel</a>
                  </li>
                </ul>
              </div>
            </div>

          </div>
        </div>

        <div v-if="loading" class="text-center my-5">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else-if="error" class="alert alert-danger my-4">
          {{ error }}
        </div>

        <div v-else-if="paginatedLogs.length === 0" class="alert alert-info my-4 text-center">
          <i data-feather="info" class="mb-2" style="width: 24px; height: 24px;"></i>
          <h5>No log found</h5>
          <p>No system logs match your search criteria. Try changing your filters or checking back later.</p>
          <button class="btn btn-outline-primary mt-2" @click="resetFilters">
            <i data-feather="refresh-cw" class="me-1"></i> Reset filters
          </button>
        </div>

        <template v-else>
          <div
            class="position-relative timeline-item"
            v-for="log in paginatedLogs"
            :key="log.id"
          >
            <div class="d-flex flex-column time-line-date">
              <span>{{ formatDateOnly(log.created_at) }}</span>
              <small class="text-muted">{{ formatTimeOnly(log.created_at) }}</small>
            </div>

            <div class="border-style-for-timeline">
              <p class="fs-13">{{ log.description }}</p>
              <p>By: <span class="text-primary">{{ log.performed_by }}</span></p>
            </div>
          </div>

          <div class="d-flex justify-content-end pt-4">
            <Pagination :total="totalItems" :perPage="perPage" v-model="currentPage" @page-changed="handlePageChange" />
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import feather from 'feather-icons';
import Pagination from '@/components/Common/Pagination.vue';
import PageTitle from '@/components/Common/PageTitle.vue';
import { useLogStore } from '@/stores/logStore';
import { hasPermission } from '@/utils/permissions';

interface LocalFilters {
  start_date: string;
  end_date: string;
  start_time: string;
  end_time: string;
  name: string;
  search: string;
}

const logStore = useLogStore();
const localFilters = ref<LocalFilters>({ start_date: '', end_date: '', start_time: '', end_time: '', name: '', search: '' });

const loading = computed(() => logStore.loading);
const error = computed(() => logStore.error);
const paginatedLogs = computed(() => logStore.paginatedLogs);
const totalItems = computed(() => logStore.totalItems);
const perPage = computed(() => logStore.perPage);
const currentPage = computed({ get: () => logStore.currentPage, set: (v: number) => (logStore.currentPage = v) });

function applyFilters() {
  logStore.updateFilters({
    start_date: localFilters.value.start_date,
    end_date: localFilters.value.end_date,
    start_time: localFilters.value.start_time,
    end_time: localFilters.value.end_time,
    name: localFilters.value.name,
    search: localFilters.value.search,
  });
}

function resetFilters() {
  localFilters.value = { start_date: '', end_date: '', start_time: '', end_time: '', name: '', search: '' };
  logStore.updateFilters({ start_date: '', end_date: '', start_time: '', end_time: '', name: '', details: '', search: '', ordering: '-created_at' });
}

function handlePageChange(page: number) {
  logStore.fetchLogs(page, false);
}

function exportLogs(format: 'csv' | 'xlsx') {
  logStore.exportLogs(format);
}

function formatDateOnly(dateStr: string): string {
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return dateStr;
  const day = date.getDate().toString().padStart(2, '0');
  const months = ['janv','févr','mars','avr','mai','juin','juil','août','sept','oct','nav','déc'];
  return `${day} ${months[date.getMonth()]} ${date.getFullYear()}`;
}

function formatTimeOnly(dateStr: string): string {
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return '';
  return `${date.getHours().toString().padStart(2,'0')}:${date.getMinutes().toString().padStart(2,'0')}:${date.getSeconds().toString().padStart(2,'0')}`;
}

onMounted(() => {
  logStore.fetchLogs();
  feather.replace();
  new MutationObserver(() => feather.replace()).observe(document.body, { childList: true, subtree: true });
});
</script>

