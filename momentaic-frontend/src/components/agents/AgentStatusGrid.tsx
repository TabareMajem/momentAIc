import React from 'react';
import { AgentStatus } from '../../hooks/useAgentStream';
import {
    Cpu,
    Search,
    Activity,
    Clock,
    AlertCircle,
    CheckCircle,
    Brain,
    MessageSquare,
    TrendingUp,
    DollarSign,
    Briefcase
} from 'lucide-react';

interface AgentStatusGridProps {
    statuses: Record<string, AgentStatus>;
    allAgents?: string[]; // List of expected agents to show even if offline
}

const DEFAULT_AGENTS = [
    'FinanceCFOAgent',
    'GrowthHackerAgent',
    'SDRAgent',
    'CustomerSuccessAgent',
    'ContentAgent',
    'DealmakerAgent'
];

export const AgentStatusGrid: React.FC<AgentStatusGridProps> = ({
    statuses,
    allAgents = DEFAULT_AGENTS
}) => {
    // Merge known active statuses with expected agents
    const mergedAgents = [...new Set([...Object.keys(statuses), ...allAgents])];

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'idle': return 'bg-gray-800 border-gray-700 text-gray-400';
            case 'scanning': return 'bg-blue-900/20 border-blue-800 text-blue-400';
            case 'executing': return 'bg-emerald-900/20 border-emerald-800 text-emerald-400';
            case 'waiting_approval': return 'bg-yellow-900/20 border-yellow-800 text-yellow-400';
            case 'error': return 'bg-red-900/20 border-red-800 text-red-400';
            default: return 'bg-gray-800 border-gray-700 text-gray-500';
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'idle': return <Cpu size={14} />;
            case 'scanning': return <Search size={14} className="animate-pulse" />;
            case 'executing': return <Activity size={14} className="animate-pulse" />;
            case 'waiting_approval': return <Clock size={14} />;
            case 'error': return <AlertCircle size={14} />;
            default: return <Cpu size={14} />;
        }
    };

    const getStatusLabel = (status: string) => {
        switch (status) {
            case 'idle': return 'Standing By';
            case 'scanning': return 'Scanning Data';
            case 'executing': return 'Executing Action';
            case 'waiting_approval': return 'Needs Approval';
            case 'error': return 'Error State';
            default: return 'Offline';
        }
    };

    const getAgentIcon = (agentName: string) => {
        const name = agentName.toLowerCase();
        if (name.includes('sdr') || name.includes('sales')) return <MessageSquare size={20} />;
        if (name.includes('growth') || name.includes('content')) return <TrendingUp size={20} />;
        if (name.includes('finance') || name.includes('cfo')) return <DollarSign size={20} />;
        if (name.includes('success') || name.includes('support')) return <CheckCircle size={20} />;
        if (name.includes('strategy') || name.includes('deal')) return <Briefcase size={20} />;
        return <Brain size={20} />;
    };

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {mergedAgents.map(agentName => {
                const status = statuses[agentName] || {
                    agent: agentName,
                    status: 'idle',
                    lastActivityAt: null
                };

                const isOffline = !statuses[agentName];
                const displayStatus = isOffline ? 'offline' : status.status;

                return (
                    <div
                        key={agentName}
                        className={`rounded-xl border p-4 transition-all duration-300 ${getStatusColor(displayStatus)}`}
                    >
                        <div className="flex justify-between items-start mb-3">
                            <div className="flex items-center gap-3">
                                <div className={`p-2 rounded-lg ${isOffline ? 'bg-gray-800' : 'bg-black/20'}`}>
                                    {getAgentIcon(agentName)}
                                </div>
                                <div>
                                    <h4 className="font-semibold text-sm text-gray-200">
                                        {agentName.replace('Agent', '').replace(/([A-Z])/g, ' $1').trim()}
                                    </h4>
                                    <div className="flex items-center gap-1.5 mt-1 text-xs font-mono">
                                        {getStatusIcon(displayStatus)}
                                        <span>{getStatusLabel(displayStatus)}</span>
                                    </div>
                                </div>
                            </div>

                            {!isOffline && status.status !== 'idle' && (
                                <div className="flex h-2 w-2">
                                    <span className={`animate-ping absolute inline-flex h-2 w-2 rounded-full opacity-75 ${status.status === 'error' ? 'bg-red-400' :
                                        status.status === 'waiting_approval' ? 'bg-yellow-400' :
                                            'bg-emerald-400'
                                        }`}></span>
                                    <span className={`relative inline-flex rounded-full h-2 w-2 ${status.status === 'error' ? 'bg-red-500' :
                                        status.status === 'waiting_approval' ? 'bg-yellow-500' :
                                            'bg-emerald-500'
                                        }`}></span>
                                </div>
                            )}
                        </div>

                        <div className="mt-4 pt-4 border-t border-black/10">
                            <p className="text-xs truncate opacity-80" title={status.currentTask || 'No current task'}>
                                {status.currentTask || (isOffline ? 'Connect to backend to initialize' : 'Monitoring opportunities...')}
                            </p>
                        </div>
                    </div>
                );
            })}
        </div>
    );
};
