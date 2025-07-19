import { reactive } from "vue";

interface StateStore {
  open: boolean;
  settings: boolean;
  task: boolean;
  label: boolean;
  card: boolean;
  onChange: () => void;
  settingsBtn: () => void;
  taskModal: () => void;
  labelModal: () => void;
  cardModal: () => void;
}

const stateStore: StateStore = reactive({
  open: false,
  settings: false,
  task: false,
  label: false,
  card: false,
  onChange() {
    stateStore.open = !stateStore.open;
  },
  settingsBtn() {
    stateStore.settings = !stateStore.settings;
  },
  taskModal() {
    stateStore.task = !stateStore.task;
  },
  labelModal() {
    stateStore.label = !stateStore.label;
  },
  cardModal() {
    stateStore.card = !stateStore.card;
  },
});

export default stateStore;
