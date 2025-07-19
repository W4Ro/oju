<template>
  <div class="row">
    <div class="col-12">
      <div class="card bg-white border-0 rounded-3 mb-4">
        <div v-if="alertDetails" class="alert alert-info m-0 border-0 rounded-0 rounded-top-3 p-3" style="background-color: #e3f2fd;">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <strong>Alert #{{ alertDetails.displayId || alertId }}</strong> : {{ alertDetails.alert_type_display }}
              <div class="small">{{ alertDetails.entity_name }} - <a :href="alertDetails.platform_url" target="_blank">{{ alertDetails.platform_url }}</a></div>
            </div>
            <span :class="getStatusBadgeClass(alertDetails.status_display)" class="badge px-3 py-1 rounded-pill">
              {{ alertDetails.status_display }}
            </span>
          </div>
        </div>
        
        <div class="card-body p-4">
          <div
            class="d-flex justify-content-between align-items-center text-center flex-wrap gap-2 showing-wrap border-bottom pb-3 mb-4"
          >
            <h3 class="fs-16 fw-semibold mb-0">New message</h3>
            <div class="d-flex position-relative top-3">
              <button
                class="pe-0 border-0 bg-transparent ms-2"
                v-b-tooltip.hover.top="'Réinitialiser'"
                @click="resetForm"
              >
                <i class="material-symbols-outlined fs-20 text-body hover">
                  delete
                </i>
              </button>
            </div>
          </div>

          <div v-if="loading" class="text-center my-5">
            <div class="spinner-border" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>

          <form v-else @submit.prevent="sendEmail">
            <div class="row">
              <div class="col-lg-12 mb-4">
                <label class="form-label text-secondary fs-14">Recipients <span class="text-danger">*</span></label>
                <div class="multi-select-container">
                  <div class="form-control h-auto p-1 d-flex flex-wrap gap-1 select-with-tags">
                    <div v-for="email in selectedToEmails" :key="'to-' + email" class="selected-tag" style="background-color: #e3f2fd; color: #0d6efd;">
                      {{ email }}
                      <button type="button" class="tag-remove" @click="removeEmail(email, 'to')">×</button>
                    </div>
                    <div class="flex-grow-1">
                      <div class="d-flex">
                        <select
                          class="form-select form-control border-0 bg-transparent p-1"
                          @change="$event.target.value && addEmail($event.target.value, 'to'); $event.target.value = ''"
                        >
                          <option value="">Select a recipient...</option>
                          <option 
                            v-for="email in getAvailableEmails('to')" 
                            :key="email" 
                            :value="email"
                          >
                            {{ email }}
                          </option>
                        </select>
                        <div class="input-group input-group-sm" style="width: auto;">
                          <input
                            type="email"
                            class="form-control border-0 bg-transparent"
                            placeholder="Add manually..."
                            v-model="manualEmail"
                            @keydown.enter.prevent="addManualEmail('to')"
                          />
                          <button 
                            type="button" 
                            class="btn btn-sm btn-outline-primary border-0"
                            @click="addManualEmail('to')"
                          >
                            +
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="col-lg-12 mb-4">
                <label class="form-label text-secondary fs-14">Cc</label>
                <div class="multi-select-container">
                  <div class="form-control h-auto p-1 d-flex flex-wrap gap-1 select-with-tags">
                    <div v-for="email in selectedCcEmails" :key="'cc-' + email" class="selected-tag" style="background-color: #f0f9ff; color: #0dcaf0;">
                      {{ email }}
                      <button type="button" class="tag-remove" @click="removeEmail(email, 'cc')">×</button>
                    </div>
                    <div class="flex-grow-1">
                      <div class="d-flex">
                        <select
                          class="form-select form-control border-0 bg-transparent p-1"
                          @change="$event.target.value && addEmail($event.target.value, 'cc'); $event.target.value = ''"
                        >
                          <option value="">Add as Cc...</option>
                          <option 
                            v-for="email in getAvailableEmails('cc')" 
                            :key="email" 
                            :value="email"
                          >
                            {{ email }}
                          </option>
                        </select>
                        <div class="input-group input-group-sm" style="width: auto;">
                          <input
                            type="email"
                            class="form-control border-0 bg-transparent"
                            placeholder="Add manually..."
                            v-model="manualCcEmail"
                            @keydown.enter.prevent="addManualEmail('cc')"
                          />
                          <button 
                            type="button" 
                            class="btn btn-sm btn-outline-primary border-0"
                            @click="addManualEmail('cc')"
                          >
                            +
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="col-lg-12 mb-4">
                <label class="form-label text-secondary fs-14">Bcc</label>
                <div class="multi-select-container">
                  <div class="form-control h-auto p-1 d-flex flex-wrap gap-1 select-with-tags">
                    <div v-for="email in selectedBccEmails" :key="'bcc-' + email" class="selected-tag" style="background-color: #f8f9fa; color: #6c757d;">
                      {{ email }}
                      <button type="button" class="tag-remove" @click="removeEmail(email, 'bcc')">×</button>
                    </div>
                    <div class="flex-grow-1">
                      <div class="d-flex">
                        <select
                          class="form-select form-control border-0 bg-transparent p-1"
                          @change="$event.target.value && addEmail($event.target.value, 'bcc'); $event.target.value = ''"
                        >
                          <option value="">Add in Bcc...</option>
                          <option 
                            v-for="email in getAvailableEmails('bcc')" 
                            :key="email" 
                            :value="email"
                          >
                            {{ email }}
                          </option>
                        </select>
                        <div class="input-group input-group-sm" style="width: auto;">
                          <input
                            type="email"
                            class="form-control border-0 bg-transparent"
                            placeholder="Add manually..."
                            v-model="manualBccEmail"
                            @keydown.enter.prevent="addManualEmail('bcc')"
                          />
                          <button 
                            type="button" 
                            class="btn btn-sm btn-outline-primary border-0"
                            @click="addManualEmail('bcc')"
                          >
                            +
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="col-lg-12 mb-4">
                <label class="form-label text-secondary fs-14">Subject <span class="text-danger">*</span></label>
                <input
                  type="text"
                  class="form-control h-55"
                  v-model="subject"
                  placeholder="Subject of the email..."
                  required
                />
              </div>
              
              <div class="col-lg-12 mb-4">
                <label class="form-label text-secondary fs-14">Message <span class="text-danger">*</span></label>
                <div 
                  class="rich-text-editor border rounded"
                  @dragover.prevent="showDropZone = true"
                  @dragleave.prevent="showDropZone = false"
                  @drop="handleFileDrop"
                  :class="{ 'drop-zone-active': showDropZone }"
                >
                  <div class="editor-toolbar p-2 border-bottom d-flex flex-wrap gap-1 bg-light">
                    <button type="button" class="btn btn-light btn-sm" title="Gras" @click="formatText('bold')">
                      <i class="bi bi-type-bold"></i>
                    </button>
                    <button type="button" class="btn btn-light btn-sm" title="Italique" @click="formatText('italic')">
                      <i class="bi bi-type-italic"></i>
                    </button>
                    <button type="button" class="btn btn-light btn-sm" title="Souligné" @click="formatText('underline')">
                      <i class="bi bi-type-underline"></i>
                    </button>
                    <button type="button" class="btn btn-light btn-sm" title="Barré" @click="formatText('strikeThrough')">
                      <i class="bi bi-type-strikethrough"></i>
                    </button>
                    <div class="vr mx-1"></div>
                    <button type="button" class="btn btn-light btn-sm" title="Code" @click="formatText('formatBlock', 'pre')">
                      <i class="bi bi-code"></i>
                    </button>
                    <button type="button" class="btn btn-light btn-sm" title="Citation" @click="formatText('formatBlock', 'blockquote')">
                      <i class="bi bi-blockquote-left"></i>
                    </button>
                    <div class="vr mx-1"></div>
                    <button type="button" class="btn btn-light btn-sm" title="Liste à puces" @click="formatText('insertUnorderedList')">
                      <i class="bi bi-list-ul"></i>
                    </button>
                    <button type="button" class="btn btn-light btn-sm" title="Liste numérotée" @click="formatText('insertOrderedList')">
                      <i class="bi bi-list-ol"></i>
                    </button>
                    <div class="vr mx-1"></div>
                    <div class="dropdown d-inline-block">
                      <button type="button" class="btn btn-light btn-sm"
                      title="Titre"
                      @click="toggleHeadingDropdown">
                          <span>Heading</span>
                          <i class="bi bi-caret-down-fill"></i>
                      </button>
                      <div v-if="showHeadingDropdown" class="heading-dropdown position-absolute bg-white border shadow-sm p-1" style="z-index: 1000">
                          <button type="button" class="dropdown-item" @click="formatText('formatBlock', 'h1')">Header 1</button>
                          <button type="button" class="dropdown-item" @click="formatText('formatBlock', 'h2')">Header 2</button>
                          <button type="button" class="dropdown-item" @click="formatText('formatBlock', 'h3')">header 3</button>
                          <button type="button" class="dropdown-item" @click="formatText('formatBlock', 'h4')">Header 4</button>
                          <button type="button" class="dropdown-item" @click="formatText('formatBlock', 'h5')">Header 5</button>
                          <button type="button" class="dropdown-item" @click="formatText('formatBlock', 'h6')">Header 6</button>
                      </div>
                  </div>
                    <button type="button" class="btn btn-light btn-sm" title="Lien" @click="insertLink">
                      <i class="bi bi-link"></i>
                    </button>
                    <button type="button" class="btn btn-light btn-sm" title="Image" @click="insertImage">
                      <i class="bi bi-image"></i>
                    </button>
                  </div>
                  
                  <div
                    ref="editor"
                    class="editor-content p-3"
                    contenteditable="true"
                    style="min-height: 285px; overflow-y: auto;"
                    @input="updateMessageBody"
                  ></div>
                </div>
              </div>

              <div class="col-lg-12 mb-4">
                <div class="d-flex align-items-center">
                  <label class="form-label text-secondary fs-14 mb-0 me-3">Attachment</label>
                  <input
                    type="file"
                    class="d-none"
                    ref="fileInput"
                    @change="handleFileSelect"
                  />
                  <button 
                    type="button" 
                    class="btn btn-outline-secondary btn-sm"
                    @click="$refs.fileInput.click()"
                  >
                    <i class="bi bi-paperclip"></i>
                    Choose a file
                  </button>
                  <div v-if="attachmentError" class="text-danger ms-3">
                    {{ attachmentError }}
                  </div>
                </div>

                <div v-if="attachment" class="mt-3 p-3 border rounded bg-light">
                  <div class="d-flex justify-content-between align-items-center">
                    <div>
                      <i class="bi bi-file-earmark"></i>
                      <span>{{ attachment.name }}</span>
                      <small class="text-muted ms-2">{{ formatFileSize(attachment.size) }}</small>
                    </div>
                    <button 
                      type="button" 
                      class="btn btn-sm text-danger"
                      @click="removeAttachment"
                    >
                      <i class="bi bi-x-lg"></i>
                    </button>
                  </div>
                </div>
              </div>

              <div class="col-lg-12">
                <div class="d-flex flex-wrap gap-3 align-items-center">
                  <button
                    class="btn btn-primary text-white fw-semibold py-2 px-4"
                    type="submit"
                    :disabled="!isFormValid || sending"
                    :v-if="!canSendMail"
                  >
                    <span v-if="sending" class="spinner-border spinner-border-sm me-2" role="status"></span>
                    Send Email
                  </button>
                  <button
                    class="btn btn-outline-secondary fw-semibold py-2 px-4"
                    type="button"
                    @click="cancel"
                    :disabled="sending"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>

    <Toast 
      :show="alertStore.toast.show" 
      :message="alertStore.toast.message" 
      :type="alertStore.toast.type" 
      :autoClose="true"
      :duration="alertStore.toast.duration"
      @close="handleToastClose" 
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from "vue";
import { useRoute, useRouter } from "vue-router";
import Toast from "@/components/Common/Toast.vue";
import { useAlertStore } from '@/stores/alert.store';
import type { Alert, EmailAttachment } from '@/types/alert.types';
import { useAuthStore } from '@/stores/auth.store';

const route = useRoute();
const router = useRouter();
const alertStore = useAlertStore();
const fileInput = ref<HTMLInputElement | null>(null);
const editor = ref<HTMLDivElement | null>(null);

const alertId = ref<string>(route.params.id as string || '');
const authStore = useAuthStore();
const loading = ref(false);
const sending = ref(false);
const successMessage = ref<string | null>(null);
const redirecting = ref(false);

const showHeadingDropdown = ref(false);

const alertDetails = ref<Alert | null>(null);

const availableEmails = ref<string[]>([]);
const selectedToEmails = ref<string[]>([]);
const selectedCcEmails = ref<string[]>([]);
const selectedBccEmails = ref<string[]>([]);
const manualEmail = ref('');
const manualCcEmail = ref('');
const manualBccEmail = ref('');

const subject = ref('');
const messageBody = ref('');

const attachment = ref<File | null>(null);
const attachmentError = ref('');
const showDropZone = ref(false);

const isFormValid = computed(() => {
  return selectedToEmails.value.length > 0 && subject.value.trim() !== '' && messageBody.value.trim() !== '';
});
const canSendMail = computed(() => {
  return authStore.hasPermission('alerts_send_email');
});

function handleToastClose() {
  alertStore.toast.show = false;
}

function formatFileSize(size: number): string {
  if (size < 1024) {
    return `${size} octets`;
  } else if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(2)} Ko`;
  } else {
    return `${(size / (1024 * 1024)).toFixed(2)} Mo`;
  }
}

const getAvailableEmails = (section: 'to' | 'cc' | 'bcc') => {
  return availableEmails.value.filter(email => {
    if (section !== 'to' && selectedToEmails.value.includes(email)) return false;
    if (section !== 'cc' && selectedCcEmails.value.includes(email)) return false;
    if (section !== 'bcc' && selectedBccEmails.value.includes(email)) return false;
    return true;
  });
};

const addEmail = (email: string, section: 'to' | 'cc' | 'bcc') => {
  if (!email.trim()) return;
  
  if (section === 'to' && !selectedToEmails.value.includes(email)) {
    selectedToEmails.value.push(email);
  } else if (section === 'cc' && !selectedCcEmails.value.includes(email)) {
    selectedCcEmails.value.push(email);
  } else if (section === 'bcc' && !selectedBccEmails.value.includes(email)) {
    selectedBccEmails.value.push(email);
  }
};

const addManualEmail = (section: 'to' | 'cc' | 'bcc') => {
  const emailValue = section === 'to' ? manualEmail.value :
                    section === 'cc' ? manualCcEmail.value : manualBccEmail.value;
  
  if (!emailValue.trim()) return;
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(emailValue)) {
    alertStore.showToast('Enter valid email address', 'error');
    return;
  }
  
  addEmail(emailValue, section);
  
  if (section === 'to') manualEmail.value = '';
  else if (section === 'cc') manualCcEmail.value = '';
  else if (section === 'bcc') manualBccEmail.value = '';
};

const removeEmail = (email: string, section: 'to' | 'cc' | 'bcc') => {
  if (section === 'to') {
    selectedToEmails.value = selectedToEmails.value.filter(e => e !== email);
  } else if (section === 'cc') {
    selectedCcEmails.value = selectedCcEmails.value.filter(e => e !== email);
  } else if (section === 'bcc') {
    selectedBccEmails.value = selectedBccEmails.value.filter(e => e !== email);
  }
};

const handleFileDrop = (event: DragEvent) => {
  event.preventDefault();
  showDropZone.value = false;
  
  if (event.dataTransfer?.files.length) {
    const file = event.dataTransfer.files[0];
    validateAndSetFile(file);
  }
};

const handleFileSelect = (event: Event) => {
  const input = event.target as HTMLInputElement;
  if (input.files?.length) {
    const file = input.files[0];
    validateAndSetFile(file);
  }
};

const validateAndSetFile = (file: File) => {
  attachmentError.value = '';
  
  const maxSize = 6 * 1024 * 1024; 
  if (file.size > maxSize) {
    attachmentError.value = `The file size must not exceed ${formatFileSize(maxSize)}`;
    return;
  }
  
  attachment.value = file;
};

const removeAttachment = () => {
  attachment.value = null;
  if (fileInput.value) {
    fileInput.value.value = '';
  }
  attachmentError.value = '';
};

const formatText = (command: string, value: string | null = null) => {
  document.execCommand(command, false, value);
  showHeadingDropdown.value = false;
  editor.value?.focus();
  updateMessageBody();
};

const toggleHeadingDropdown = () => {
  showHeadingDropdown.value = !showHeadingDropdown.value;
};

const insertLink = () => {
  const url = prompt('Enter the URL of the link :', 'http://');
  if (url) {
    formatText('createLink', url);
  }
};

const insertImage = () => {
  const url = prompt('Enter the image URL :', 'http://');
  if (url) {
    formatText('insertImage', url);
  }
};

const updateMessageBody = () => {
  if (editor.value) {
    messageBody.value = editor.value.innerHTML;
  }
};

const fileToBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      const result = reader.result as string;
      const base64Content = result.split(',')[1];
      resolve(base64Content);
    };
    reader.onerror = error => reject(error);
  });
};

const resetForm = () => {
  selectedToEmails.value = [];
  selectedCcEmails.value = [];
  selectedBccEmails.value = [];
  subject.value = '';
  if (editor.value) {
    editor.value.innerHTML = '';
  }
  messageBody.value = '';
  removeAttachment();
};

function getStatusBadgeClass(status: string): string {
  switch (status) {
    case "New":
      return "bg-warning text-dark";
    case "In progress":
      return "bg-primary text-white";
    case "Resolved":
      return "bg-success text-white";
    case "False positive":
      return "bg-secondary text-white";
    default:
      return "bg-secondary text-white";
  }
}

const sendEmail = async () => {
  if (!isFormValid.value) {
    alertStore.showToast('Please fill all required fields', 'error');
    return;
  }
  if(!canSendMail.value) {
    alertStore.showToast('You do not have permission to send emails', 'error');
    return;
  }
  
  sending.value = true;
  
  try {
    let attachments: EmailAttachment[] = [];
    
    if (attachment.value) {
      try {
        const base64Content = await fileToBase64(attachment.value);
        attachments.push({
          filename: attachment.value.name,
          content: base64Content,
          content_type: attachment.value.type
        });
      } catch (error) {
        console.error('Error converting file:', error);
        alertStore.showToast('Error processing attachment.', 'error');
        sending.value = false;
        return;
      }
    }
    
    const payload = {
      to: selectedToEmails.value[0], 
      cc: selectedCcEmails.value,
      bcc: selectedBccEmails.value,
      subject: subject.value,
      body: messageBody.value,
      attachments: attachments.length > 0 ? attachments : undefined
    };
    
    const response = await alertStore.sendEmail(alertId.value, payload);
    
    if (response) {
      successMessage.value = 'Email sent successfully !';
      alertStore.showToast(response?.message || 'Email sending attempting, check logs for any issues', 'success', 5000);
      
      redirecting.value = true;
      setTimeout(() => {
        router.go(-1);
      }, 5000);
    }
  } catch (error: any) {
    console.error('Error sending email:', error);
    alertStore.showToast(error.response?.data?.error || 'Error sending email', 'error');
  } finally {
    sending.value = false;
  }
};

const cancel = () => {
  router.go(-1);
};

const closeHeadingDropdown = (event: MouseEvent) => {
  if (showHeadingDropdown.value && !(event.target as HTMLElement).closest('.btn-light')) {
    showHeadingDropdown.value = false;
  }
};

const loadInitialData = async () => {
  if (!alertId.value) {
    alertStore.showToast('Alert ID not specified', 'error');
    return;
  }
  
  loading.value = true;
  
  try {
    const alert = await alertStore.getAlert(alertId.value) as Alert;
    if (alert) {
      alertDetails.value = alert;
    }
    
    const emailTemplate = await alertStore.fetchAlertEmail(alertId.value);
    
    if (emailTemplate) {
      availableEmails.value = emailTemplate.focal_points_emails || [];
      
      if (emailTemplate.subject) {
        subject.value = emailTemplate.subject;
      }
      if (emailTemplate.template) {
        await nextTick(); 
        
        setTimeout(() => {
          if (editor.value) {
            editor.value.innerHTML = emailTemplate.template;
            
            messageBody.value = emailTemplate.template;
            
          } else {
            console.error('Publisher reference not available');
          }
        }, 100); 
      }
    }
  } catch (error: any) {
    console.error('Error loading data:', error);
    alertStore.showToast(
      error.message || 'Error loading alert data',
      'error'
    );
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  document.addEventListener('click', closeHeadingDropdown);
  loadInitialData();
});

onBeforeUnmount(() => {
  document.removeEventListener('click', closeHeadingDropdown);
});
</script>

<style scoped>
.text-editor {
  min-height: 285px;
}

.multi-select-container {
  position: relative;
}

.select-with-tags {
  min-height: 55px;
  overflow: hidden;
}

.selected-tag {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  margin-bottom: 2px;
  margin-top: 2px;
}

.tag-remove {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0 0 0 0.3rem;
  font-size: 1.1rem;
  line-height: 1;
  opacity: 0.7;
}

.tag-remove:hover {
  opacity: 1;
}

.rich-text-editor {
  display: flex;
  flex-direction: column;
}

.editor-toolbar {
  border-top-left-radius: 0.375rem;
  border-top-right-radius: 0.375rem;
  background-color: #f0f0f0 !important;
  padding: 8px !important;
}

.editor-toolbar .btn {
  margin-right: 5px;
  background-color: white;
  border: 1px solid #dee2e6;
}

.editor-content {
  border-bottom-left-radius: 0.375rem;
  border-bottom-right-radius: 0.375rem;
  outline: none;
}

.heading-dropdown {
  border-radius: 0.25rem;
}

.dropdown-item {
  border: none;
  background: none;
  display: block;
  width: 100%;
  padding: 0.25rem 1rem;
  clear: both;
  text-align: inherit;
  white-space: nowrap;
  border-radius: 0;
}

.dropdown-item:hover {
  background-color: #f8f9fa;
}

.drop-zone-active {
  background-color: rgba(13, 110, 253, 0.05);
  border-color: #0d6efd !important;
}

@media only screen and (max-width: 767px) {
  .editor-content {
    min-height: 190px;
  }
}

@media only screen and (min-width: 768px) and (max-width: 991px) {
  .editor-content {
    min-height: 200px;
  }
}

@media only screen and (min-width: 992px) and (max-width: 1199px) {
  .editor-content {
    min-height: 176px;
  }
}

@media only screen and (min-width: 1200px) and (max-width: 1399px) {
  .editor-content {
    min-height: 176px;
  }
}
</style>