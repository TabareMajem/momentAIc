import { create } from 'zustand';
import { api } from '../lib/api';

import type { Startup } from '../types';

interface StartupState {
    startups: Startup[];
    activeStartupId: string | null;
    isLoading: boolean;
    error: string | null;

    // Actions
    fetchStartups: () => Promise<void>;
    setActiveStartup: (id: string) => void;
    addStartup: (startup: Startup) => void;
    getActiveStartup: () => Startup | null;
}

export const useStartupStore = create<StartupState>((set, get) => ({
    startups: [],
    activeStartupId: null,
    isLoading: false,
    error: null,

    fetchStartups: async () => {
        set({ isLoading: true, error: null });
        try {
            const data = await api.getStartups();

            // Auto-select the first startup if none is selected
            const currentActiveId = get().activeStartupId;
            const newActiveId = (currentActiveId && data.some((s: Startup) => s.id === currentActiveId))
                ? currentActiveId
                : (data.length > 0 ? data[0].id : null);

            set({
                startups: data,
                activeStartupId: newActiveId,
                isLoading: false
            });
        } catch (error: any) {
            console.error("Failed to fetch startups:", error);
            set({ error: error.message || "Failed to load startups", isLoading: false });
        }
    },

    setActiveStartup: (id: string) => {
        set({ activeStartupId: id });
    },

    addStartup: (startup: Startup) => {
        set((state) => ({
            startups: [...state.startups, startup],
            activeStartupId: startup.id // Auto-select newly created startup
        }));
    },

    getActiveStartup: () => {
        const state = get();
        if (!state.activeStartupId) return null;
        return state.startups.find(s => s.id === state.activeStartupId) || null;
    }
}));
