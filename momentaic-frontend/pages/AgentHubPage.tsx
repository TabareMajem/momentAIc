import React from 'react';
import AgentHub from '../components/yokaizen/AgentHub';
import { useNavigate } from 'react-router-dom';
import { AgentType } from '../types';

export default function AgentHubPage() {
    const navigate = useNavigate();

    const handleSelectAgent = (agent: AgentType) => {
        // Simple routing mapping for agents
        const agentRoutes: Record<string, string> = {
            [AgentType.SNIPER]: '/sniper',
            [AgentType.CONTENT_CLAY]: '/growth-engine',
            [AgentType.VIRAL]: '/viral-growth',
            [AgentType.MOBY_DTC]: '/moby',
            [AgentType.GATEKEEPER]: '/gatekeeper',
            [AgentType.MEDIA]: '/media',
            [AgentType.WORKFLOW]: '/workflow-architect',
            [AgentType.RECRUITING]: '/recruiting',
            [AgentType.LEGAL]: '/legal',
            [AgentType.SUPPORT]: '/support',
            [AgentType.PROCUREMENT]: '/procurement',
        };

        const route = agentRoutes[agent];
        if (route) {
            navigate(route);
        } else {
            console.warn(`No route configured for agent type: ${agent}`);
        }
    };

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <AgentHub onSelectAgent={handleSelectAgent} />
        </div>
    );
}
