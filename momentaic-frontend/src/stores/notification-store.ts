import { create } from 'zustand';
import { PushService } from '../services/PushService';

interface NotificationState {
    isSupported: boolean;
    permission: NotificationPermission;
    isSubscribed: boolean;
    checkStatus: () => Promise<void>;
    subscribe: () => Promise<boolean>;
    sendTest: () => Promise<void>;
}

export const useNotificationStore = create<NotificationState>((set, get) => ({
    isSupported: 'serviceWorker' in navigator && 'PushManager' in window,
    permission: 'default',
    isSubscribed: false,

    checkStatus: async () => {
        if (!get().isSupported) return;

        set({ permission: Notification.permission });

        // Check if service worker has subscription
        const registration = await navigator.serviceWorker.getRegistration();
        if (registration) {
            const sub = await registration.pushManager.getSubscription();
            set({ isSubscribed: !!sub });
        }
    },

    subscribe: async () => {
        const success = await PushService.register();
        if (success) {
            await get().checkStatus();
        }
        return success;
    },

    sendTest: async () => {
        await PushService.sendTest();
    }
}));
