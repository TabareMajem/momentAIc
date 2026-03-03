import { create } from 'zustand';

interface NotificationState {
    isSupported: boolean;
    isSubscribed: boolean;
    subscribe: () => Promise<boolean>;
    checkStatus: () => void;
}

export const useNotificationStore = create<NotificationState>((set) => ({
    isSupported: 'Notification' in window,
    isSubscribed: false,
    subscribe: async () => {
        if (!('Notification' in window)) return false;

        try {
            const permission = await Notification.requestPermission();
            if (permission === 'granted') {
                set({ isSubscribed: true });
                return true;
            }
            return false;
        } catch (error) {
            console.error('Failed to subscribe to push notifications:', error);
            return false;
        }
    },
    checkStatus: () => {
        if (!('Notification' in window)) return;
        set({ isSubscribed: Notification.permission === 'granted' });
    }
}));
