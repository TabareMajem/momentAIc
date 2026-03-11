import { Terminal, Shield, Sparkles, Target, Zap } from 'lucide-react';

export interface TourStep {
    title: string;
    content: string;
    color?: string;
    icon?: any;
}

export interface TourConfig {
    id: string;
    title: string;
    steps: TourStep[];
}

export const TOURS: Record<string, TourConfig> = {
    dashboard_tour: {
        id: 'dashboard_tour',
        title: 'Mission Control',
        steps: [
            {
                title: 'Welcome to your Empire',
                content: 'This is Mission Control. From here, you monitor your autonomous workforce, orchestrate campaigns, and view real-time telemetry from your agents.',
                color: 'from-blue-500 to-cyan-500',
                icon: Terminal
            },
            {
                title: 'Morning Briefing',
                content: 'Every morning, your agents analyze the market, your ongoing campaigns, and your active experiments to give you a summarized, actionable brief right here.',
                color: 'from-emerald-500 to-teal-500',
                icon: Target
            },
            {
                title: 'Active Swarm',
                content: 'Keep an eye on the War Room widget. You can see precisely what each agent is doing in real-time. No black boxes. Pure execution.',
                color: 'from-purple-500 to-pink-500',
                icon: Zap
            }
        ]
    },
    ghost_board_tour: {
        id: 'ghost_board_tour',
        title: 'Ghost Board',
        steps: [
            {
                title: 'Summon the Legends',
                content: 'You are no longer building alone. The Ghost Board allows you to summon high-fidelity AI personas of legendary founders to review your strategy.',
                color: 'from-red-500 to-orange-500',
                icon: Shield
            },
            {
                title: 'Pitch Your Strategy',
                content: 'Drop your latest landing page, sales copy, or GTM plan into the center. The board will instantly rip it apart and rebuild it with elite insights.',
                color: 'from-purple-500 to-indigo-500',
                icon: Sparkles
            }
        ]
    },
    agent_market_tour: {
        id: 'agent_market_tour',
        title: 'Agent Marketplace',
        steps: [
            {
                title: 'Hire Your Team',
                content: 'Browse highly specialized agents. From cold email SDRs to Legal contract reviewers, you can deploy a full workforce in seconds.',
                color: 'from-cyan-500 to-blue-500',
                icon: Target
            },
            {
                title: 'Plug and Play',
                content: "Once hired, an agent connects to your startup's context automatically. They don't need onboarding. Just give them a task and watch them execute.",
                color: 'from-emerald-500 to-teal-500',
                icon: Zap
            }
        ]
    }
};
