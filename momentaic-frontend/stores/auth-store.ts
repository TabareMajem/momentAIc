
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { api } from '../lib/api';
import type { User, SubscriptionTier } from '../types';

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => void;
  loadUser: () => Promise<void>;
  
  // Business Logic Actions
  deductCredits: (amount: number) => boolean;
  upgradeTier: (tier: SubscriptionTier) => void;
  getStartupLimit: () => number;
}

const TIER_LIMITS = {
  starter: 1,
  growth: 3,
  god_mode: 999
};

const TIER_CREDITS = {
  starter: 50,
  growth: 500,
  god_mode: 999999
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isLoading: false,
      isAuthenticated: false,
      
      login: async (email, password) => {
        set({ isLoading: true });
        try {
          await api.login(email, password);
          await get().loadUser();
        } catch (error) {
          console.error('Login failed', error);
          throw error;
        } finally {
          set({ isLoading: false });
        }
      },

      signup: async (email, password, fullName) => {
        set({ isLoading: true });
        try {
          await api.signup(email, password, fullName);
          await api.login(email, password);
          await get().loadUser();
        } catch (error) {
          console.error('Signup failed', error);
          throw error;
        } finally {
          set({ isLoading: false });
        }
      },

      logout: () => {
        api.logout();
        set({ user: null, isAuthenticated: false });
      },

      loadUser: async () => {
        set({ isLoading: true });
        try {
          const user = await api.getMe();
          // Initialize credits if missing in mock
          if (user.credits === undefined) {
             user.credits = TIER_CREDITS[user.subscription_tier];
          }
          set({ user, isAuthenticated: true });
        } catch (error) {
           set({ user: null, isAuthenticated: false });
           api.logout();
        } finally {
          set({ isLoading: false });
        }
      },

      deductCredits: (amount: number) => {
        const { user } = get();
        if (!user) return false;
        
        // God Mode has infinite credits
        if (user.subscription_tier === 'god_mode') return true;

        if (user.credits < amount) {
          return false;
        }

        set({ user: { ...user, credits: user.credits - amount } });
        return true;
      },

      upgradeTier: (tier: SubscriptionTier) => {
        const { user } = get();
        if (user) {
          set({ 
            user: { 
              ...user, 
              subscription_tier: tier,
              credits: TIER_CREDITS[tier] // Reset credits on upgrade
            } 
          });
        }
      },

      getStartupLimit: () => {
        const { user } = get();
        if (!user) return 0;
        return TIER_LIMITS[user.subscription_tier];
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
);
