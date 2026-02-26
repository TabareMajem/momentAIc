import React, { useState, useEffect } from 'react';
import { useStartupStore } from '../../stores/startup-store';
import { CheckCircle, XCircle, Zap, RefreshCw, Send, Twitter, ShieldAlert } from 'lucide-react';
import { Button } from '../Button';
import { api } from '../../../lib/api';

interface ActionItem {
    id: string;
    source_agent: string;
    title: string;
    description: string;
    priority: string;
    payload: any;
    status: string;
    created_at: string;
}

export function ActionQueueWidget() {
    const { currentStartup } = useStartupStore();
    const [actions, setActions] = useState<ActionItem[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchActions = async () => {
        if (!currentStartup) return;
        setLoading(true);
        try {
            const res = await api.get(`/hitl/startups/${currentStartup.id}/actions?status_filter=pending`);
            setActions(res.data);
        } catch (err) {
            console.error("Failed to fetch HitL actions", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchActions();
        const interval = setInterval(fetchActions, 15000); // Poll every 15s
        return () => clearInterval(interval);
    }, [currentStartup]);

    const handleReview = async (ids: string[], approve: boolean) => {
        if (!currentStartup) return;
        try {
            await api.post(`/hitl/startups/${currentStartup.id}/actions/review`, {
                action_ids: ids,
                approve: approve
            });
            fetchActions();
        } catch (err) {
            console.error("Failed to review actions", err);
        }
    };

    const getIcon = (type: string) => {
        if (type.includes('tweet') || type.includes('content')) return <Twitter className="w-4 h-4 text-blue-400" />;
        if (type.includes('email') || type.includes('reply')) return <Send className="w-4 h-4 text-emerald-400" />;
        return <ShieldAlert className="w-4 h-4 text-amber-400" />;
    };

    if (loading && actions.length === 0) {
        return (
            <div className="bg-slate-900/50 rounded-xl border border-white/5 p-6 flex justify-center items-center h-48">
                <RefreshCw className="w-6 h-6 text-slate-500 animate-spin" />
            </div>
        );
    }

    if (actions.length === 0) {
        return (
            <div className="bg-slate-900/50 rounded-xl border border-white/5 p-6 flex flex-col items-center justify-center h-48 text-center">
                <div className="w-12 h-12 bg-slate-800/50 rounded-full flex items-center justify-center mb-3 border border-white/5">
                    <CheckCircle className="w-6 h-6 text-emerald-500" />
                </div>
                <h3 className="font-semibold text-white mb-1">Inbox Zero</h3>
                <p className="text-sm text-slate-400">All autonomous agent actions have been reviewed.</p>
            </div>
        );
    }

    return (
        <div className="bg-slate-900/50 rounded-xl border border-rose-500/20 overflow-hidden relative shadow-[0_0_15px_rgba(244,63,94,0.1)]">
            {/* Background glow for urgent feel */}
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-rose-500 to-orange-500"></div>

            <div className="p-4 border-b border-white/5 flex items-center justify-between bg-slate-800/20">
                <div className="flex items-center gap-2">
                    <Zap className="w-5 h-5 text-rose-500" />
                    <h2 className="font-semibold text-white">Action Approval Queue</h2>
                    <span className="bg-rose-500/20 text-rose-300 text-xs px-2 py-0.5 rounded-full font-medium">
                        {actions.length} Pending
                    </span>
                </div>
                <Button
                    variant="cyber"
                    size="sm"
                    onClick={() => handleReview(actions.map(a => a.id), true)}
                >
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Approve All
                </Button>
            </div>

            <div className="divide-y divide-white/5 max-h-[400px] overflow-y-auto">
                {actions.map((action) => (
                    <div key={action.id} className="p-4 hover:bg-slate-800/30 transition-colors group">
                        <div className="flex items-start justify-between gap-4">
                            <div className="flex items-start gap-3 flex-1 min-w-0">
                                <div className="mt-1 p-2 bg-slate-800 rounded-lg border border-white/5">
                                    {getIcon(action.title.toLowerCase() + action.description.toLowerCase())}
                                </div>
                                <div>
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className="text-xs font-mono text-rose-400 bg-rose-500/10 px-1.5 py-0.5 rounded">
                                            {action.source_agent}
                                        </span>
                                        <span className="text-xs text-slate-500">
                                            {new Date(action.created_at).toLocaleTimeString()}
                                        </span>
                                    </div>
                                    <h3 className="text-sm font-medium text-white mb-1 truncate">{action.title}</h3>
                                    <p className="text-sm text-slate-400 line-clamp-2">{action.description}</p>
                                </div>
                            </div>

                            {/* Individual Actions */}
                            <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                <button
                                    onClick={() => handleReview([action.id], false)}
                                    className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded-lg transition-colors"
                                    title="Reject"
                                >
                                    <XCircle className="w-5 h-5" />
                                </button>
                                <button
                                    onClick={() => handleReview([action.id], true)}
                                    className="p-1.5 text-slate-400 hover:text-emerald-400 hover:bg-slate-800 rounded-lg transition-colors"
                                    title="Approve"
                                >
                                    <CheckCircle className="w-5 h-5" />
                                </button>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
