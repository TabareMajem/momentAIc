import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// ============ FEATURE REGISTRY ============

export interface FeatureDefinition {
    id: string;
    name: string;
    description: string;
    href: string;
    icon: string;
    tier: 'essential' | 'growth' | 'godmode';
    category: 'core' | 'marketing' | 'operations' | 'intelligence' | 'agents';
    stageRecommended?: string[]; // Startup stages where this feature is recommended
}

export const FEATURE_REGISTRY: FeatureDefinition[] = [
    // ── Essential (always on) ──
    { id: 'dashboard', name: 'Command Center', description: 'Your AI team working in real-time', href: '/dashboard', icon: 'LayoutDashboard', tier: 'essential', category: 'core' },
    { id: 'vault', name: 'The Vault', description: 'AI-generated documents, contracts, and models', href: '/vault', icon: 'Shield', tier: 'essential', category: 'core' },
    { id: 'settings', name: 'Settings', description: 'Account, billing, and preferences', href: '/settings', icon: 'Settings', tier: 'essential', category: 'core' },

    // ── Growth (user-activatable) ──
    { id: 'campaigns', name: 'Campaign HQ', description: 'Launch and manage multi-channel campaigns', href: '/executor', icon: 'Zap', tier: 'growth', category: 'marketing', stageRecommended: ['idea', 'mvp', 'pmf'] },
    { id: 'war_room', name: 'War Room', description: 'Autonomous Board of Directors with AI debate', href: '/war-room', icon: 'Shield', tier: 'growth', category: 'operations', stageRecommended: ['pmf', 'scaling'] },
    { id: 'pulse', name: 'Business Pulse', description: 'Real-time heartbeat monitoring & KPIs', href: '/pulse', icon: 'Activity', tier: 'growth', category: 'operations', stageRecommended: ['mvp', 'pmf', 'scaling'] },
    { id: 'growth', name: 'Growth Engine', description: 'Automated lead gen, SEO, and outreach', href: '/growth', icon: 'TrendingUp', tier: 'growth', category: 'marketing', stageRecommended: ['mvp', 'pmf'] },
    { id: 'agent_forge', name: 'Agent Forge', description: 'Build, customize, and deploy AI agents', href: '/agent-forge', icon: 'Network', tier: 'growth', category: 'agents', stageRecommended: ['pmf', 'scaling'] },
    { id: 'agent_marketplace', name: 'Agent Marketplace', description: 'Discover and clone community AI agents', href: '/agent-marketplace', icon: 'Sparkles', tier: 'growth', category: 'agents', stageRecommended: ['idea', 'mvp', 'pmf', 'scaling'] },
    { id: 'characters', name: 'Character Factory', description: 'Create AI personas for content and outreach', href: '/characters', icon: 'Sparkles', tier: 'growth', category: 'agents', stageRecommended: ['idea', 'mvp'] },
    { id: 'research', name: 'Research Lab', description: 'Deep market intelligence and competitor analysis', href: '/research', icon: 'BookOpen', tier: 'growth', category: 'intelligence', stageRecommended: ['idea', 'mvp'] },

    // ── God Mode (advanced) ──
    { id: 'telemetry', name: 'Telemetry Core', description: 'Deep platform analytics and system health', href: '/telemetry', icon: 'BarChart2', tier: 'godmode', category: 'operations', stageRecommended: ['scaling', 'mature'] },
    { id: 'call_center', name: 'Call Center', description: 'AI-powered voice calls and phone outreach', href: '/call-center', icon: 'Phone', tier: 'godmode', category: 'marketing', stageRecommended: ['pmf', 'scaling'] },
    { id: 'viral_swarm', name: 'Viral Swarm', description: 'Coordinated multi-platform viral campaigns', href: '/viral-swarm', icon: 'Zap', tier: 'godmode', category: 'marketing', stageRecommended: ['pmf', 'scaling'] },
    { id: 'guerrilla', name: 'Guerrilla Warfare', description: 'Unconventional growth hacking strategies', href: '/guerrilla', icon: 'Target', tier: 'godmode', category: 'marketing', stageRecommended: ['mvp', 'pmf'] },
    { id: 'global_campaign', name: 'Global Campaign', description: 'Worldwide coordinated marketing operations', href: '/global-campaign', icon: 'Globe', tier: 'godmode', category: 'marketing', stageRecommended: ['scaling', 'mature'] },
    { id: 'integrations', name: 'Integrations', description: 'Connect third-party tools and APIs', href: '/integrations', icon: 'Plug', tier: 'godmode', category: 'operations', stageRecommended: ['pmf', 'scaling'] },
    { id: 'triggers', name: 'Triggers', description: 'Event-driven automation workflows', href: '/triggers', icon: 'Bell', tier: 'godmode', category: 'operations', stageRecommended: ['scaling', 'mature'] },
    { id: 'experiments', name: 'Experiments Lab', description: 'A/B testing and hypothesis validation', href: '/experiments', icon: 'FlaskConical', tier: 'godmode', category: 'intelligence', stageRecommended: ['pmf', 'scaling'] },
    { id: 'openclaw', name: 'OpenClaw Proxy', description: 'Direct AI model access and orchestration', href: '/openclaw', icon: 'Terminal', tier: 'godmode', category: 'agents', stageRecommended: ['scaling', 'mature'] },
    { id: 'ambassador', name: 'Revenue Program', description: 'Ambassador dashboard and referral commissions', href: '/ambassador', icon: 'DollarSign', tier: 'godmode', category: 'core', stageRecommended: ['pmf', 'scaling', 'mature'] },
];

const ESSENTIAL_IDS = FEATURE_REGISTRY.filter(f => f.tier === 'essential').map(f => f.id);

// Stage-based recommendations: returns top 3 features for the startup's current stage
export function getRecommendedFeatures(stage: string, enabledFeatures: string[]): FeatureDefinition[] {
    return FEATURE_REGISTRY
        .filter(f => f.tier !== 'essential')
        .filter(f => !enabledFeatures.includes(f.id))
        .filter(f => f.stageRecommended?.includes(stage))
        .slice(0, 3);
}

// ============ STORE ============

interface FeatureState {
    enabledFeatures: string[];
    toggleFeature: (id: string) => void;
    isEnabled: (id: string) => boolean;
    enableAll: () => void;
    resetToEssentials: () => void;
}

export const useFeatureStore = create<FeatureState>()(
    persist(
        (set, get) => ({
            enabledFeatures: [...ESSENTIAL_IDS],

            toggleFeature: (id: string) => {
                if (ESSENTIAL_IDS.includes(id)) return;
                set((state) => {
                    const isCurrentlyEnabled = state.enabledFeatures.includes(id);
                    return {
                        enabledFeatures: isCurrentlyEnabled
                            ? state.enabledFeatures.filter(f => f !== id)
                            : [...state.enabledFeatures, id]
                    };
                });
            },

            isEnabled: (id: string) => {
                return get().enabledFeatures.includes(id);
            },

            enableAll: () => {
                set({ enabledFeatures: FEATURE_REGISTRY.map(f => f.id) });
            },

            resetToEssentials: () => {
                set({ enabledFeatures: [...ESSENTIAL_IDS] });
            },
        }),
        { name: 'momentaic-features' }
    )
);
