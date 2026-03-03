import React from 'react';
import { AgentActivity } from '../../hooks/useAgentStream';
import {
    CheckCircle,
    Activity,
    Clock,
    AlertTriangle,
    XCircle,
    Brain,
    MessageSquare,
    TrendingUp,
    DollarSign,
    Briefcase
} from 'lucide-react';

interface AgentActivityFeedProps {
    activities: AgentActivity[];
    limit?: number;
}

const getAgentIcon = (agentName: string) => {
    const name = agentName.toLowerCase();
    if (name.includes('sdr') || name.includes('sales')) return <MessageSquare size={16} />;
    if (name.includes('growth') || name.includes('content')) return <TrendingUp size={16} />;
    if (name.includes('finance') || name.includes('cfo')) return <DollarSign size={16} />;
    if (name.includes('success') || name.includes('support')) return <CheckCircle size={16} />;
    if (name.includes('strategy') || name.includes('deal')) return <Briefcase size={16} />;
    return <Brain size={16} />;
};

const getStatusIcon = (status: string) => {
    switch (status) {
        case 'started':
        case 'running':
            return <Activity size={14} className="text-blue-500 animate-pulse" />;
        case 'completed':
            return <CheckCircle size={14} className="text-green-500" />;
        case 'waiting_approval':
            return <Clock size={14} className="text-yellow-500" />;
        case 'failed':
            return <XCircle size={14} className="text-red-500" />;
        default:
            return <AlertTriangle size={14} className="text-gray-500" />;
    }
};

const formatTime = (isoString: string) => {
    try {
        const date = new Date(isoString);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch (e) {
        return isoString;
    }
};

export const AgentActivityFeed: React.FC<AgentActivityFeedProps> = ({
    activities,
    limit = 20
}) => {
    const displayActivities = activities.slice(0, limit);

    return (
        <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden flex flex-col h-full">
            <div className="px-5 py-4 border-b border-gray-800 flex justify-between items-center bg-gray-900/50">
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                    <Activity className="text-blue-500" size={20} />
                    Live Agent Activity
                </h3>
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                    <span className="text-xs text-gray-400 font-mono">STREAM ACTIVE</span>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto p-2 space-y-1">
                {displayActivities.length === 0 ? (
                    <div className="h-40 flex items-center justify-center text-gray-500 text-sm">
                        Waiting for agent activity...
                    </div>
                ) : (
                    displayActivities.map((activity, idx) => (
                        <div
                            key={`${activity.id}-${idx}`}
                            className="group p-3 hover:bg-gray-800/50 rounded-lg transition-colors border border-transparent hover:border-gray-700/50 flex gap-4"
                        >
                            <div className="flex flex-col items-center pt-1 relative">
                                <div className={`p-1.5 rounded-full bg-gray-800 border ${activity.status === 'failed' ? 'border-red-500/30 text-red-400' :
                                        activity.status === 'waiting_approval' ? 'border-yellow-500/30 text-yellow-400' :
                                            activity.status === 'completed' ? 'border-green-500/30 text-green-400' :
                                                'border-blue-500/30 text-blue-400'
                                    }`}>
                                    {getAgentIcon(activity.agent)}
                                </div>
                                {idx !== displayActivities.length - 1 && (
                                    <div className="absolute top-9 bottom-0 w-px bg-gray-800 -mb-2 group-hover:bg-gray-700"></div>
                                )}
                            </div>

                            <div className="flex-1 min-w-0">
                                <div className="flex justify-between items-start mb-1">
                                    <div className="flex items-center gap-2">
                                        <span className="font-medium text-sm text-gray-200">
                                            {activity.agent.replace(/([A-Z])/g, ' $1').trim()}
                                        </span>
                                        <span className="text-xs text-gray-500">•</span>
                                        <span className="text-xs font-mono text-gray-400">
                                            {activity.action}
                                        </span>
                                    </div>
                                    <div className="flex items-center gap-2 text-xs text-gray-500 font-mono">
                                        {getStatusIcon(activity.status)}
                                        {formatTime(activity.timestamp)}
                                    </div>
                                </div>

                                {activity.details && (
                                    <p className="text-sm text-gray-400 truncate pr-4">
                                        {activity.details}
                                    </p>
                                )}
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};
