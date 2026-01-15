import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Bot, CheckCircle, Clock, XCircle, Send, Edit, Sparkles,
    FileText, Mail, MessageSquare, Zap, ChevronRight, Loader
} from 'lucide-react';
import { Button } from './ui/Button';
import { useToast } from './ui/Toast';

// ============ TYPES ============

interface AgentActivity {
    id: string;
    agent: string;
    action: string;
    status: 'pending' | 'awaiting_approval' | 'completed' | 'failed';
    content?: string;
    createdAt: Date;
    output?: any;
}

// ============ ACTIVITY CARD ============

function ActivityCard({
    activity,
    onApprove,
    onReject,
    onEdit
}: {
    activity: AgentActivity;
    onApprove?: () => void;
    onReject?: () => void;
    onEdit?: () => void;
}) {
    const getStatusIcon = () => {
        switch (activity.status) {
            case 'completed': return <CheckCircle className="w-4 h-4 text-emerald-400" />;
            case 'failed': return <XCircle className="w-4 h-4 text-red-400" />;
            case 'pending': return <Loader className="w-4 h-4 text-blue-400 animate-spin" />;
            case 'awaiting_approval': return <Clock className="w-4 h-4 text-yellow-400" />;
            default: return <Sparkles className="w-4 h-4 text-purple-400" />;
        }
    };

    const getAgentColor = () => {
        const colors: Record<string, string> = {
            content: 'from-purple-500 to-pink-500',
            sdr: 'from-blue-500 to-cyan-500',
            growth_hacker: 'from-green-500 to-emerald-500',
            marketing: 'from-orange-500 to-red-500',
        };
        return colors[activity.agent] || 'from-slate-500 to-slate-600';
    };

    const formatTime = (date: Date) => {
        const now = new Date();
        const diff = now.getTime() - date.getTime();
        const mins = Math.floor(diff / 60000);
        if (mins < 1) return 'Just now';
        if (mins < 60) return `${mins}m ago`;
        const hours = Math.floor(mins / 60);
        if (hours < 24) return `${hours}h ago`;
        return `${Math.floor(hours / 24)}d ago`;
    };

    return (
        <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="relative flex gap-4 p-4 rounded-xl bg-slate-900/50 border border-white/5 hover:border-white/10 transition-colors"
        >
            {/* Agent Avatar */}
            <div className={`flex-shrink-0 w-10 h-10 rounded-lg bg-gradient-to-br ${getAgentColor()} flex items-center justify-center`}>
                <Bot className="w-5 h-5 text-white" />
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                    <span className="font-medium text-white capitalize">
                        {activity.agent.replace('_', ' ')}
                    </span>
                    {getStatusIcon()}
                    <span className="text-xs text-slate-500">{formatTime(activity.createdAt)}</span>
                </div>

                <p className="text-sm text-slate-300 mb-2">{activity.action}</p>

                {activity.content && (
                    <div className="bg-slate-800/50 rounded-lg p-3 text-sm text-slate-400 mb-3">
                        "{activity.content.slice(0, 200)}{activity.content.length > 200 ? '...' : ''}"
                    </div>
                )}

                {/* Action Buttons for Pending Approval */}
                {activity.status === 'awaiting_approval' && (
                    <div className="flex gap-2">
                        <Button size="sm" variant="cyber" onClick={onApprove}>
                            <Send className="w-3 h-3 mr-1" />
                            Approve & Post
                        </Button>
                        <Button size="sm" variant="outline" onClick={onEdit}>
                            <Edit className="w-3 h-3 mr-1" />
                            Edit
                        </Button>
                        <Button size="sm" variant="ghost" onClick={onReject}>
                            <XCircle className="w-3 h-3 mr-1" />
                            Dismiss
                        </Button>
                    </div>
                )}
            </div>
        </motion.div>
    );
}

// ============ MAIN COMPONENT ============

export default function ActivityFeed() {
    const { toast } = useToast();
    const [activities, setActivities] = useState<AgentActivity[]>([]);
    const [loading, setLoading] = useState(true);

    // Simulate fetching activities (in production, use WebSocket or polling)
    useEffect(() => {
        // Demo activities
        const demoActivities: AgentActivity[] = [
            {
                id: '1',
                agent: 'content',
                action: 'Generated 3 LinkedIn posts for this week',
                status: 'awaiting_approval',
                content: "🚀 Just launched our new AI-powered feature that helps founders automate their growth. Here's what we learned...",
                createdAt: new Date(Date.now() - 5 * 60000),
            },
            {
                id: '2',
                agent: 'sdr',
                action: 'Drafted outreach for 5 qualified leads',
                status: 'awaiting_approval',
                content: "Hi [Name], I noticed your work on [Topic]. We help companies like yours...",
                createdAt: new Date(Date.now() - 30 * 60000),
            },
            {
                id: '3',
                agent: 'growth_hacker',
                action: 'Completed weekly growth report',
                status: 'completed',
                createdAt: new Date(Date.now() - 2 * 3600000),
            },
        ];

        setTimeout(() => {
            setActivities(demoActivities);
            setLoading(false);
        }, 500);
    }, []);

    const handleApprove = async (id: string) => {
        // In production, call API to approve and execute
        setActivities(prev =>
            prev.map(a => a.id === id ? { ...a, status: 'completed' as const } : a)
        );
        toast({
            type: 'success',
            title: 'Posted!',
            message: 'Content has been published to your connected accounts.'
        });
    };

    const handleReject = (id: string) => {
        setActivities(prev => prev.filter(a => a.id !== id));
        toast({
            type: 'info',
            title: 'Dismissed',
            message: 'Activity removed from queue.'
        });
    };

    const pendingCount = activities.filter(a => a.status === 'awaiting_approval').length;

    return (
        <div className="bg-slate-950/50 rounded-2xl border border-white/10 overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-white/5">
                <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-gradient-to-br from-purple-500/20 to-cyan-500/20">
                        <Zap className="w-5 h-5 text-purple-400" />
                    </div>
                    <div>
                        <h3 className="font-semibold text-white">AI Army Activity</h3>
                        <p className="text-xs text-slate-400">Real-time agent updates</p>
                    </div>
                </div>
                {pendingCount > 0 && (
                    <span className="px-2 py-1 rounded-full bg-yellow-500/20 text-yellow-400 text-xs font-medium">
                        {pendingCount} pending
                    </span>
                )}
            </div>

            {/* Activity List */}
            <div className="p-4 space-y-3 max-h-[400px] overflow-y-auto">
                {loading ? (
                    <div className="flex items-center justify-center py-8">
                        <Loader className="w-6 h-6 text-slate-400 animate-spin" />
                    </div>
                ) : activities.length === 0 ? (
                    <div className="text-center py-8 text-slate-500">
                        <Bot className="w-8 h-8 mx-auto mb-2 opacity-50" />
                        <p>No recent activity</p>
                    </div>
                ) : (
                    <AnimatePresence>
                        {activities.map(activity => (
                            <ActivityCard
                                key={activity.id}
                                activity={activity}
                                onApprove={() => handleApprove(activity.id)}
                                onReject={() => handleReject(activity.id)}
                                onEdit={() => toast({ type: 'info', title: 'Editor', message: 'Edit modal coming soon' })}
                            />
                        ))}
                    </AnimatePresence>
                )}
            </div>

            {/* Footer */}
            <div className="p-3 border-t border-white/5 bg-slate-900/30">
                <button className="w-full flex items-center justify-center gap-2 text-sm text-slate-400 hover:text-white transition-colors">
                    View All Activity
                    <ChevronRight className="w-4 h-4" />
                </button>
            </div>
        </div>
    );
}
