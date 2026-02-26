import React, { useState, useEffect } from 'react';
import { useStartupStore } from '../stores/startup-store';
import {
    CheckCircle, XCircle, Zap, RefreshCw, Send, Twitter, ShieldAlert,
    Filter, Inbox, CheckCheck, Ban, Clock, ChevronRight, Bell, Mail, MessageSquare,
    Smartphone, X
} from 'lucide-react';
import { api } from '../lib/api';

// ============ TYPES ============

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

type TabFilter = 'pending' | 'approved' | 'rejected' | 'all';

// ============ MAIN PAGE ============

export default function HitLDashboard() {
    const { currentStartup } = useStartupStore();
    const [actions, setActions] = useState<ActionItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<TabFilter>('pending');
    const [agentFilter, setAgentFilter] = useState<string>('all');
    const [selectedAction, setSelectedAction] = useState<ActionItem | null>(null);
    const [showNotifPrefs, setShowNotifPrefs] = useState(false);
    const [notifPrefs, setNotifPrefs] = useState({ email: true, push: true, whatsapp: false });

    const fetchActions = async () => {
        if (!currentStartup) return;
        setLoading(true);
        try {
            const statusParam = activeTab === 'all' ? '' : `?status_filter=${activeTab}`;
            const res = await api.get(`/hitl/startups/${currentStartup.id}/actions${statusParam}`);
            setActions(res.data);
        } catch (err) {
            console.error("Failed to fetch actions", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchActions();
    }, [currentStartup, activeTab]);

    const handleReview = async (ids: string[], approve: boolean) => {
        if (!currentStartup) return;
        try {
            await api.post(`/hitl/startups/${currentStartup.id}/actions/review`, {
                action_ids: ids,
                approve: approve
            });
            setSelectedAction(null);
            fetchActions();
        } catch (err) {
            console.error("Failed to review actions", err);
        }
    };

    const filteredActions = agentFilter === 'all'
        ? actions
        : actions.filter(a => a.source_agent === agentFilter);

    const uniqueAgents = [...new Set(actions.map(a => a.source_agent))];
    const pendingCount = actions.filter(a => a.status === 'pending').length;

    const tabs: { key: TabFilter; label: string; icon: React.ReactNode }[] = [
        { key: 'pending', label: 'Pending', icon: <Clock className="w-4 h-4" /> },
        { key: 'approved', label: 'Approved', icon: <CheckCheck className="w-4 h-4" /> },
        { key: 'rejected', label: 'Rejected', icon: <Ban className="w-4 h-4" /> },
        { key: 'all', label: 'All', icon: <Inbox className="w-4 h-4" /> },
    ];

    const getIcon = (text: string) => {
        const lower = text.toLowerCase();
        if (lower.includes('tweet') || lower.includes('content')) return <Twitter className="w-4 h-4 text-blue-400" />;
        if (lower.includes('email') || lower.includes('support')) return <Send className="w-4 h-4 text-emerald-400" />;
        if (lower.includes('bug') || lower.includes('qa')) return <ShieldAlert className="w-4 h-4 text-amber-400" />;
        if (lower.includes('mrr') || lower.includes('burn') || lower.includes('churn')) return <Zap className="w-4 h-4 text-rose-400" />;
        return <ShieldAlert className="w-4 h-4 text-slate-400" />;
    };

    const getPriorityBadge = (priority: string) => {
        const colors: Record<string, string> = {
            urgent: 'bg-red-500/20 text-red-300 border-red-500/30',
            high: 'bg-orange-500/20 text-orange-300 border-orange-500/30',
            medium: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
            low: 'bg-slate-500/20 text-slate-300 border-slate-500/30',
        };
        return (
            <span className={`text-[10px] font-mono uppercase px-1.5 py-0.5 rounded border ${colors[priority] || colors.medium}`}>
                {priority}
            </span>
        );
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white flex items-center gap-3">
                        <div className="p-2 bg-gradient-to-br from-rose-500 to-orange-500 rounded-xl">
                            <Zap className="w-6 h-6 text-white" />
                        </div>
                        Action Command Center
                    </h1>
                    <p className="text-slate-400 mt-1">Review and approve autonomous agent proposals</p>
                </div>
                <div className="flex items-center gap-3">
                    <button
                        onClick={() => setShowNotifPrefs(!showNotifPrefs)}
                        className="p-2.5 text-slate-400 hover:text-white bg-slate-800/50 hover:bg-slate-800 rounded-xl border border-white/5 transition-all"
                        title="Notification Preferences"
                    >
                        <Bell className="w-5 h-5" />
                    </button>
                    {activeTab === 'pending' && filteredActions.length > 0 && (
                        <button
                            onClick={() => handleReview(filteredActions.map(a => a.id), true)}
                            className="px-4 py-2.5 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-400 hover:to-emerald-500 text-white rounded-xl font-medium text-sm flex items-center gap-2 shadow-lg shadow-emerald-500/20 transition-all"
                        >
                            <CheckCheck className="w-4 h-4" />
                            Approve All ({filteredActions.length})
                        </button>
                    )}
                </div>
            </div>

            {/* Notification Preferences Panel */}
            {showNotifPrefs && (
                <div className="bg-slate-900/80 border border-white/10 rounded-xl p-5 animate-fade-in">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-white font-semibold flex items-center gap-2">
                            <Bell className="w-4 h-4 text-blue-400" /> Notification Preferences
                        </h3>
                        <button onClick={() => setShowNotifPrefs(false)} className="text-slate-400 hover:text-white">
                            <X className="w-4 h-4" />
                        </button>
                    </div>
                    <div className="grid grid-cols-3 gap-4">
                        {[
                            { key: 'email', label: 'Email', icon: <Mail className="w-5 h-5" />, desc: 'Get notified via email' },
                            { key: 'push', label: 'Push', icon: <Smartphone className="w-5 h-5" />, desc: 'Browser push notifications' },
                            { key: 'whatsapp', label: 'WhatsApp', icon: <MessageSquare className="w-5 h-5" />, desc: 'Via Twilio WhatsApp' },
                        ].map(ch => (
                            <label
                                key={ch.key}
                                className={`flex items-center gap-3 p-4 rounded-xl border cursor-pointer transition-all ${notifPrefs[ch.key as keyof typeof notifPrefs]
                                        ? 'bg-blue-500/10 border-blue-500/30'
                                        : 'bg-slate-800/50 border-white/5 hover:border-white/10'
                                    }`}
                            >
                                <input
                                    type="checkbox"
                                    checked={notifPrefs[ch.key as keyof typeof notifPrefs]}
                                    onChange={() => setNotifPrefs(prev => ({ ...prev, [ch.key]: !prev[ch.key as keyof typeof prev] }))}
                                    className="hidden"
                                />
                                <div className={notifPrefs[ch.key as keyof typeof notifPrefs] ? 'text-blue-400' : 'text-slate-500'}>
                                    {ch.icon}
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-white">{ch.label}</p>
                                    <p className="text-xs text-slate-400">{ch.desc}</p>
                                </div>
                            </label>
                        ))}
                    </div>
                </div>
            )}

            {/* Tabs + Agent Filter */}
            <div className="flex items-center justify-between border-b border-white/5 pb-3">
                <div className="flex gap-1">
                    {tabs.map(tab => (
                        <button
                            key={tab.key}
                            onClick={() => setActiveTab(tab.key)}
                            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === tab.key
                                    ? 'bg-white/10 text-white'
                                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                                }`}
                        >
                            {tab.icon}
                            {tab.label}
                            {tab.key === 'pending' && pendingCount > 0 && (
                                <span className="bg-rose-500 text-white text-[10px] px-1.5 py-0.5 rounded-full font-mono">
                                    {pendingCount}
                                </span>
                            )}
                        </button>
                    ))}
                </div>
                <div className="flex items-center gap-2">
                    <Filter className="w-4 h-4 text-slate-500" />
                    <select
                        value={agentFilter}
                        onChange={(e) => setAgentFilter(e.target.value)}
                        className="bg-slate-800/80 text-slate-300 text-sm rounded-lg px-3 py-1.5 border border-white/5 focus:outline-none focus:border-blue-500/50"
                    >
                        <option value="all">All Agents</option>
                        {uniqueAgents.map(agent => (
                            <option key={agent} value={agent}>{agent}</option>
                        ))}
                    </select>
                </div>
            </div>

            {/* Actions List */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left: Action List */}
                <div className="lg:col-span-2 space-y-2">
                    {loading && filteredActions.length === 0 ? (
                        <div className="flex items-center justify-center h-64">
                            <RefreshCw className="w-6 h-6 text-slate-500 animate-spin" />
                        </div>
                    ) : filteredActions.length === 0 ? (
                        <div className="flex flex-col items-center justify-center h-64 text-center">
                            <div className="w-16 h-16 bg-slate-800/50 rounded-full flex items-center justify-center mb-4 border border-white/5">
                                <CheckCircle className="w-8 h-8 text-emerald-500" />
                            </div>
                            <h3 className="text-lg font-semibold text-white mb-1">Queue Clear</h3>
                            <p className="text-sm text-slate-400">No {activeTab !== 'all' ? activeTab : ''} actions to display.</p>
                        </div>
                    ) : (
                        filteredActions.map((action) => (
                            <div
                                key={action.id}
                                onClick={() => setSelectedAction(action)}
                                className={`p-4 rounded-xl border cursor-pointer transition-all group ${selectedAction?.id === action.id
                                        ? 'bg-slate-800/80 border-blue-500/30'
                                        : 'bg-slate-900/50 border-white/5 hover:border-white/10 hover:bg-slate-800/30'
                                    }`}
                            >
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-3 flex-1 min-w-0">
                                        <div className="p-2 bg-slate-800 rounded-lg border border-white/5">
                                            {getIcon(action.title + action.description)}
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center gap-2 mb-1">
                                                <span className="text-[10px] font-mono text-rose-400 bg-rose-500/10 px-1.5 py-0.5 rounded">
                                                    {action.source_agent}
                                                </span>
                                                {getPriorityBadge(action.priority)}
                                                <span className="text-[10px] text-slate-500">
                                                    {new Date(action.created_at).toLocaleString()}
                                                </span>
                                            </div>
                                            <h3 className="text-sm font-medium text-white truncate">{action.title}</h3>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        {action.status === 'pending' && (
                                            <>
                                                <button
                                                    onClick={(e) => { e.stopPropagation(); handleReview([action.id], false); }}
                                                    className="p-1.5 text-slate-500 hover:text-red-400 hover:bg-slate-800 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
                                                    title="Reject"
                                                >
                                                    <XCircle className="w-5 h-5" />
                                                </button>
                                                <button
                                                    onClick={(e) => { e.stopPropagation(); handleReview([action.id], true); }}
                                                    className="p-1.5 text-slate-500 hover:text-emerald-400 hover:bg-slate-800 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
                                                    title="Approve"
                                                >
                                                    <CheckCircle className="w-5 h-5" />
                                                </button>
                                            </>
                                        )}
                                        <ChevronRight className="w-4 h-4 text-slate-600" />
                                    </div>
                                </div>
                            </div>
                        ))
                    )}
                </div>

                {/* Right: Detail Drawer */}
                <div className="lg:col-span-1">
                    {selectedAction ? (
                        <div className="bg-slate-900/80 rounded-xl border border-white/10 p-5 sticky top-6 space-y-4">
                            <div className="flex items-center justify-between">
                                <h3 className="text-white font-semibold">Action Detail</h3>
                                <button onClick={() => setSelectedAction(null)} className="text-slate-400 hover:text-white">
                                    <X className="w-4 h-4" />
                                </button>
                            </div>

                            <div>
                                <p className="text-xs text-slate-500 mb-1">Title</p>
                                <p className="text-sm text-white">{selectedAction.title}</p>
                            </div>

                            <div>
                                <p className="text-xs text-slate-500 mb-1">Agent</p>
                                <p className="text-sm text-rose-400 font-mono">{selectedAction.source_agent}</p>
                            </div>

                            <div>
                                <p className="text-xs text-slate-500 mb-1">Description</p>
                                <p className="text-sm text-slate-300">{selectedAction.description}</p>
                            </div>

                            <div>
                                <p className="text-xs text-slate-500 mb-1">Priority</p>
                                {getPriorityBadge(selectedAction.priority)}
                            </div>

                            <div>
                                <p className="text-xs text-slate-500 mb-1">Payload Preview</p>
                                <pre className="text-xs text-slate-400 bg-slate-800/80 p-3 rounded-lg overflow-auto max-h-48 font-mono border border-white/5">
                                    {JSON.stringify(selectedAction.payload, null, 2)}
                                </pre>
                            </div>

                            {selectedAction.status === 'pending' && (
                                <div className="flex gap-2 pt-2">
                                    <button
                                        onClick={() => handleReview([selectedAction.id], false)}
                                        className="flex-1 px-4 py-2.5 bg-slate-800 hover:bg-red-500/20 text-slate-300 hover:text-red-300 rounded-xl text-sm font-medium border border-white/5 hover:border-red-500/30 transition-all flex items-center justify-center gap-2"
                                    >
                                        <XCircle className="w-4 h-4" /> Reject
                                    </button>
                                    <button
                                        onClick={() => handleReview([selectedAction.id], true)}
                                        className="flex-1 px-4 py-2.5 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 rounded-xl text-sm font-medium border border-emerald-500/30 transition-all flex items-center justify-center gap-2"
                                    >
                                        <CheckCircle className="w-4 h-4" /> Approve
                                    </button>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="bg-slate-900/50 rounded-xl border border-white/5 p-8 flex flex-col items-center justify-center text-center h-64">
                            <Inbox className="w-8 h-8 text-slate-600 mb-3" />
                            <p className="text-sm text-slate-400">Select an action to preview its details</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
