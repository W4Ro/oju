<template>
    <div>
      
      <div class="card bg-white border-0 rounded-3 mb-4">
        <div class="card-body p-0">
          <div class="p-4">
            <div
              class="d-flex justify-content-between align-items-center flex-wrap gap-3"
            >
              <form class="position-relative table-src-form me-0" @submit.prevent>
                <input
                  type="text"
                  class="form-control"
                  placeholder="Rechercher"
                  v-model="searchTerm"
                />
                <i
                  class="material-symbols-outlined position-absolute top-50 start-0 translate-middle-y"
                >
                  search
                </i>
              </form>
            </div>
          </div>
  
          <div class="default-table-area style-two">
            <div class="table-responsive">
              <table class="table align-middle">
                <thead>
                  <tr>
                    <!-- <th scope="col">ID</th> -->
                    <th scope="col">Full Name</th>
                    <th scope="col">Phone Numbers</th>
                    <th scope="col">Email</th>
                    <th scope="col">Function</th>
                    <th scope="col">Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in paginatedItems" :key="item.id">
                    <!-- <td class="text-body">{{ item.id }}</td> -->
                    <td>{{ item.user.name }}</td>
                    <td>
                      <div class="phone-number-container">
                        {{ item.phoneNumbers.join(', ') }}
                        <div class="phone-tooltip">
                          <ul class="phone-list">
                            <li v-for="(phone, index) in item.phoneNumbers" :key="index">
                              {{ phone }}
                            </li>
                          </ul>
                        </div>
                      </div>
                    </td>
                    <td>{{ item.email }}</td>
                    <td class="text-body">{{ item.role }}</td>
                    <td>
                      <span
                        class="badge bg-opacity-10 p-2 fs-12 fw-normal"
                        :class="item.status.active ? 'bg-primary text-success' : 'bg-danger text-danger'"
                      >
                        {{ item.status.active ? 'Active' : 'Deactive' }}
                      </span>
                    </td>
                  </tr>
                  <tr v-if="paginatedItems.length === 0">
                    <td colspan="6" class="text-center py-4">
                      <span v-if="error">{{ error }}</span>
                      <span v-else>No Focal Point found</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
  
            <div class="p-4" v-if="filteredItems.length > 0">
              <div
                class="d-flex justify-content-center justify-content-sm-between align-items-center text-center flex-wrap gap-2 showing-wrap"
              >
                <span class="fs-12 fw-medium">
                  Showing {{ displayedItemsStart }}-{{ displayedItemsEnd }} of {{ filteredItems.length }} Results
                </span>
                <nav aria-label="Page navigation">
                  <ul class="pagination mb-0 justify-content-center">
                    <li class="page-item" :class="{ disabled: currentPage === 1 }">
                      <a 
                        class="page-link icon" 
                        href="#" 
                        aria-label="Previous"
                        @click.prevent="changePage(currentPage - 1)"
                      >
                        <i class="material-symbols-outlined">keyboard_arrow_left</i>
                      </a>
                    </li>
                    
                    <li 
                      v-for="page in displayedPages" 
                      :key="page"
                      class="page-item"
                    >
                      <a 
                        class="page-link" 
                        :class="{ active: page === currentPage }" 
                        href="#" 
                        @click.prevent="changePage(page)"
                      >
                        {{ page }}
                      </a>
                    </li>
                    
                    <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                      <a 
                        class="page-link icon" 
                        href="#" 
                        aria-label="Next"
                        @click.prevent="changePage(currentPage + 1)"
                      >
                        <i class="material-symbols-outlined">keyboard_arrow_right</i>
                      </a>
                    </li>
                  </ul>
                </nav>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: "EntityFocalPoint",
    props: {
      entityId: {
        type: [String, Number],
        default: ""
      },
      users: {
        type: Array,
        default: () => []
      },
      perPage: {
        type: Number,
        default: 10
      },
      error: {
        type: String,
        default: ""
      }
    },
    data() {
      return {
        searchTerm: "",
        currentPage: 1,        
      };
    },
    computed: {
      
      items() {
        return this.users;
      },
  
      
      filteredItems() {
        if (!this.searchTerm.trim()) {
          return this.items;
        }
        
        const term = this.searchTerm.toLowerCase().trim();
        return this.items.filter(
          (item) =>
            String(item.id).toLowerCase().includes(term) ||
            item.user.name.toLowerCase().includes(term) ||
            item.email.toLowerCase().includes(term) ||
            item.role.toLowerCase().includes(term) ||
            item.phoneNumbers.some((phone) =>
              phone.toLowerCase().includes(term)
            )
        );
      },
  
      totalPages() {
        return Math.max(1, Math.ceil(this.filteredItems.length / this.perPage));
      },
  
      displayedPages() {
        const maxVisiblePages = 5;
        
        if (this.totalPages <= maxVisiblePages) {
          return Array.from({ length: this.totalPages }, (_, i) => i + 1);
        }
        
        const halfVisible = Math.floor(maxVisiblePages / 2);
        let startPage = Math.max(1, this.currentPage - halfVisible);
        let endPage = Math.min(this.totalPages, startPage + maxVisiblePages - 1);
        
        if (endPage === this.totalPages) {
          startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }
        
        return Array.from({ length: endPage - startPage + 1 }, (_, i) => startPage + i);
      },
  
      displayedItemsStart() {
        if (this.filteredItems.length === 0) return 0;
        return (this.currentPage - 1) * this.perPage + 1;
      },
  
      displayedItemsEnd() {
        return Math.min(this.currentPage * this.perPage, this.filteredItems.length);
      },
  
      paginatedItems() {
        const startIndex = (this.currentPage - 1) * this.perPage;
        const endIndex = Math.min(startIndex + this.perPage, this.filteredItems.length);
        return this.filteredItems.slice(startIndex, endIndex);
      }
    },
    methods: {
      changePage(page) {
        if (page < 1 || page > this.totalPages) return;
        this.currentPage = page;
      }
    },
    watch: {
      searchTerm() {
        this.currentPage = 1;
      },
      users() {
        this.currentPage = 1;
      }
    }
  };
  </script>
  
  <style scoped>
  .phone-number-container {
    position: relative !important;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 150px;
    cursor: pointer;
  }
  
  .phone-tooltip {
    display: none;
    position: absolute;
    background-color: #fff;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 8px 12px;
    z-index: 1000 !important;
    left: 0;
    top: -10px;
    transform: translateY(-100%);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    min-width: 150px;
    max-width: 250px;
  }
  
  .phone-number-container:hover .phone-tooltip {
    display: block !important;
  }
  
  .phone-tooltip::after {
    content: '';
    position: absolute;
    bottom: -10px;
    left: 15px;
    border-width: 5px;
    border-style: solid;
    border-color: #ddd transparent transparent transparent;
  }
  
  .phone-list {
    list-style: none;
    margin: 0;
    padding: 0;
  }
  
  .phone-list li {
    padding: 4px 0;
    border-bottom: 1px solid #eee;
  }
  
  .phone-list li:last-child {
    border-bottom: none;
  }
  
  .badge {
    padding: 0.35em 0.65em;
    font-size: 0.75em;
    font-weight: 400;
    line-height: 1;
    text-align: center;
    white-space: nowrap;
    border-radius: 0.25rem;
  }
  
  .badge.bg-primary {
    color: #0d6efd;
    background-color: rgba(13, 110, 253, 0.1);
  }
  
  .badge.bg-danger {
    color: #dc3545;
    background-color: rgba(220, 53, 69, 0.1);
  }
  
  .pagination {
    display: flex;
    list-style: none;
    padding-left: 0;
    margin: 0;
  }
  
  .page-item {
    margin: 0 2px;
  }
  
  .page-link {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 6px 12px;
    border-radius: 4px;
    border: 1px solid #dee2e6;
    color: #0d6efd;
    text-decoration: none;
    background-color: #fff;
    min-width: 36px;
    min-height: 36px;
  }
  
  .page-link.active {
    background-color: #0d6efd;
    color: white;
    border-color: #0d6efd;
  }
  
  .page-item.disabled .page-link {
    color: #6c757d;
    pointer-events: none;
    background-color: #fff;
    border-color: #dee2e6;
  }
  
  .showing-wrap {
    color: #6c757d;
  }
  
  h4 {
    font-weight: 600;
    color: #333;
  }
  </style>