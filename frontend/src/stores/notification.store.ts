import { defineStore } from 'pinia';

interface Notification {
  id: number;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
}

export const useNotificationStore = defineStore('notification', {
  state: () => ({
    notifications: [] as Notification[],
    counter: 0
  }),
  
  actions: {
    show(notification: Omit<Notification, 'id'>) {
      const id = ++this.counter;
      this.notifications.push({
        id,
        ...notification
      });
      
      return id;
    },
    
    success(message: string, duration?: number) {
      return this.show({ message, type: 'success', duration });
    },
    
    error(message: string, duration?: number) {
      return this.show({ message, type: 'error', duration });
    },
    
    warning(message: string, duration?: number) {
      return this.show({ message, type: 'warning', duration });
    },
    
    info(message: string, duration?: number) {
      return this.show({ message, type: 'info', duration });
    },
    
    remove(id: number) {
      const index = this.notifications.findIndex(n => n.id === id);
      if (index !== -1) {
        this.notifications.splice(index, 1);
      }
    }
  }
});