import { api } from '../../lib/api';

const VAPID_PUBLIC_KEY = "BL6DSnxXnfmlKHAeHaB7lXTT0ERXNfJJt6tJRQIY_8nRO0dtLo6yHMpXcM5eE_qX5PTPbjIsOD4yFklgc5exHv4"; // From step 2658

function urlBase64ToUint8Array(base64String: string) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/-/g, '+')
        .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

export const PushService = {
    async register() {
        if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
            console.warn('Push not supported');
            return false;
        }

        try {
            const registration = await navigator.serviceWorker.register('/sw.js');
            console.log('SW registered:', registration);

            const subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY)
            });

            // Send to backend
            const subJson = subscription.toJSON();
            await api.post('/notifications/subscribe', subJson);

            return true;
        } catch (error) {
            console.error('Push registration failed:', error);
            return false;
        }
    },

    async sendTest() {
        return api.post('/notifications/test-push', {});
    }
};
