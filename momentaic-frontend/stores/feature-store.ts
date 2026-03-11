import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// ============ FEATURE REGISTRY ============

export interface FeatureDefinition {
    id: string;
    name: string;
    description: string;
    href: string;
    icon: string;
    tier: 'essential' | 'lite' | 'growth' | 'godmode';
    category: 'core' | 'marketing' | 'operations' | 'intelligence' | 'agents';
    stageRecommended?: string[]; // Startup stages where this feature is recommended
    isNew?: boolean;
}

export const FEATURE_REGISTRY: FeatureDefinition[] = [
    // ── Essential (always on) ──
    { id: 'dashboard', name: 'Command Center', description: 'Your AI team working in real-time', href: '/dashboard', icon: 'LayoutDashboard', tier: 'essential', category: 'core' },
    { id: 'ghost_board', name: 'Ghost Board', description: 'Your daily synthetic co-founder brief', href: '/ghost-board', icon: 'Terminal', tier: 'essential', category: 'core' },
    { id: 'hitl', name: 'Action Queue', description: 'Review and approve autonomous agent proposals', href: '/hitl', icon: 'Zap', tier: 'essential', category: 'core' },
    { id: 'vault', name: 'The Vault', description: 'AI-generated documents, contracts, and models', href: '/vault', icon: 'Shield', tier: 'essential', category: 'core' },
    { id: 'settings', name: 'Settings', description: 'Account, billing, and preferences', href: '/settings', icon: 'Settings', tier: 'essential', category: 'core' },

    // ── Growth (user-activatable) ──
    { id: 'war_room', name: 'War Room', description: 'Autonomous Board of Directors with AI debate', href: '/war-room', icon: 'Shield', tier: 'growth', category: 'operations', stageRecommended: ['pmf', 'scaling'] },
    { id: 'pulse', name: 'Business Pulse', description: 'Real-time heartbeat monitoring & KPIs', href: '/pulse', icon: 'Activity', tier: 'growth', category: 'operations', stageRecommended: ['mvp', 'pmf', 'scaling'] },
    { id: 'growth', name: 'DeerFlow Growth Engine', description: 'Massive marketing campaigns & deal oracle', href: '/growth', icon: 'TrendingUp', tier: 'lite', category: 'marketing', stageRecommended: ['mvp', 'pmf'] },
    { id: 'agent_forge', name: 'Agent Forge', description: 'Build, customize, and deploy AI agents', href: '/agent-forge', icon: 'Network', tier: 'lite', category: 'agents', stageRecommended: ['pmf', 'scaling'] },
    { id: 'agent_marketplace', name: 'Agent Marketplace', description: 'Discover and clone community AI agents', href: '/agent-marketplace', icon: 'Sparkles', tier: 'growth', category: 'agents', stageRecommended: ['idea', 'mvp', 'pmf', 'scaling'] },
    { id: 'characters', name: 'Character Factory', description: 'Create AI personas for content and outreach', href: '/characters', icon: 'Sparkles', tier: 'growth', category: 'agents', stageRecommended: ['idea', 'mvp'] },
    { id: 'research', name: 'Research Lab', description: 'Deep market intelligence and competitor analysis', href: '/research', icon: 'BookOpen', tier: 'growth', category: 'intelligence', stageRecommended: ['idea', 'mvp'] },

    // ── God Mode (advanced) ──
    { id: 'telemetry', name: 'Telemetry Core', description: 'Deep platform analytics and system health', href: '/telemetry', icon: 'BarChart2', tier: 'godmode', category: 'operations', stageRecommended: ['scaling', 'mature'] },
    { id: 'viral_swarm', name: 'Viral Swarm', description: 'Coordinated multi-platform viral campaigns', href: '/viral-swarm', icon: 'Zap', tier: 'godmode', category: 'marketing', stageRecommended: ['pmf', 'scaling'] },
    { id: 'guerrilla', name: 'Guerrilla Warfare', description: 'Unconventional growth hacking strategies', href: '/guerrilla', icon: 'Target', tier: 'godmode', category: 'marketing', stageRecommended: ['mvp', 'pmf'] },
    { id: 'global_campaign', name: 'Global Campaign', description: 'Worldwide coordinated marketing operations', href: '/global-campaign', icon: 'Globe', tier: 'godmode', category: 'marketing', stageRecommended: ['scaling', 'mature'] },
    { id: 'integrations', name: 'Integrations', description: 'Connect third-party tools and APIs', href: '/integrations', icon: 'Plug', tier: 'godmode', category: 'operations', stageRecommended: ['pmf', 'scaling'] },
    { id: 'experiments', name: 'Experiments Lab', description: 'A/B testing and hypothesis validation', href: '/experiments', icon: 'FlaskConical', tier: 'godmode', category: 'intelligence', stageRecommended: ['pmf', 'scaling'] },
    { id: 'ambassador', name: 'Revenue Program', description: 'Ambassador dashboard and referral commissions', href: '/ambassador', icon: 'DollarSign', tier: 'godmode', category: 'core', stageRecommended: ['pmf', 'scaling', 'mature'] },
    {
        id: "gtm-command",
        name: "GTM Command Center",
        description: "Browser Prospector, Trust Architect, and Swarm Steer.",
        category: "operations",
        tier: "essential",
        href: "/gtm",
        icon: "Target",
        isNew: true
    },
    {
        id: "scraper_dashboard",
        name: "Influencer Scraper",
        description: "Stealth Target Extraction",
        href: "/scraper/onboarding",
        icon: "Bot",
        tier: "essential",
        category: "marketing",
        isNew: true
    },
    {
        id: "sniper_agent",
        name: "Sniper Agent",
        description: "Hyper-personalized LinkedIn Prospecting",
        href: "/sniper",
        icon: "Target",
        tier: "growth",
        category: "agents",
        isNew: true,
        stageRecommended: ['idea', 'mvp', 'pmf']
    },
    {
        id: "media_agent",
        name: "Media Agent",
        description: "AI Image, Video & Audio Studio",
        href: "/media",
        icon: "Film",
        tier: "growth",
        category: "agents",
        isNew: true,
        stageRecommended: ['mvp', 'pmf', 'scaling']
    },
    {
        id: "content_agent",
        name: "Content Agent",
        description: "Omnichannel Asset Generation",
        href: "/content",
        icon: "Sparkles",
        tier: "growth",
        category: "agents",
        isNew: true,
        stageRecommended: ['idea', 'mvp', 'pmf']
    },
    {
        id: "moby_agent",
        name: "Moby Agent",
        description: "DTC Market Intelligence",
        href: "/moby",
        icon: "BrainCircuit",
        tier: "growth",
        category: "agents",
        isNew: true,
        stageRecommended: ['scaling']
    },
    {
        id: "gatekeeper_agent",
        name: "Gatekeeper Agent",
        description: "Automated Inbound Triage",
        href: "/gatekeeper",
        icon: "ShieldAlert",
        tier: "growth",
        category: "agents",
        isNew: true,
        stageRecommended: ['scaling']
    },
    {
        id: "lemlist_agent",
        name: "Lemlist Agent",
        description: "Market Narrative Distortion",
        href: "/lemlist",
        icon: "Crosshair",
        tier: "growth",
        category: "agents",
        isNew: true,
        stageRecommended: ['scaling']
    },
    {
        id: "legal_agent",
        name: "Legal Eagle",
        description: "AI Contract Review",
        href: "/legal",
        icon: "Scale",
        tier: "growth",
        category: "agents",
        isNew: true,
        stageRecommended: ['scaling']
    },
    {
        id: "recruiting_agent",
        name: "HR Scout",
        description: "AI Resume Screening",
        href: "/recruiting",
        icon: "Briefcase",
        tier: "growth",
        category: "agents",
        isNew: true,
        stageRecommended: ['scaling']
    },
    {
        id: "support_agent",
        name: "Support Sage",
        description: "AI Customer Support",
        href: "/support-wizard",
        icon: "MessageSquare",
        tier: "growth",
        category: "agents",
        isNew: true,
        stageRecommended: ['scaling']
    },
    {
        id: "procurement_agent",
        name: "Agent J: The Auditor",
        description: "Invoice Anomaly Detection",
        href: "/procurement",
        icon: "DollarSign",
        tier: "growth",
        category: "agents",
        isNew: true,
        stageRecommended: ['scaling']
    },
    {
        id: "marketing_clay",
        name: "Agent F: Growth Engine",
        description: "Vertical Build Strategy",
        href: "/growth-engine",
        icon: "Database",
        tier: "growth",
        category: "agents",
        isNew: true,
        stageRecommended: ['scaling']
    },
    {
        id: "agent_hub",
        name: "Neuronal Hub",
        description: "Agent Directory",
        href: "/agent-hub",
        icon: "BrainCircuit",
        tier: "essential",
        category: "agents",
        isNew: false,
        stageRecommended: ['validating', 'scaling']
    },
    {
        id: "workflow_agent",
        name: "Agent E: Workflow Architect",
        description: "Autonomous Systems",
        href: "/workflow-architect",
        icon: "Workflow",
        tier: "growth",
        category: "agents",
        isNew: true,
        stageRecommended: ['scaling']
    },
    {
        id: "moby_autonomous",
        name: "Moby v4: Organism",
        description: "Autopilot Integration",
        href: "/moby",
        icon: "BrainCircuit",
        tier: "growth",
        category: "agents",
        isNew: true,
        stageRecommended: ['scaling']
    },
    {
        id: "admin_panel",
        name: "Admin Console",
        description: "System Management",
        href: "/admin",
        icon: "Shield",
        tier: "godmode",
        category: "core",
        isNew: false,
        stageRecommended: ['scaling']
    },
    {
        id: "settings",
        name: "Settings & API",
        description: "Configuration",
        href: "/settings",
        icon: "Settings",
        tier: "essential",
        category: "core",
        isNew: false,
        stageRecommended: ['validating', 'scaling']
    }
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
