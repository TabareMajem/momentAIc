import React, { useState, useEffect, useCallback } from 'react';
import { Activity, Zap, AlertTriangle, Brain, CheckCircle2, Clock, RefreshCw, Eye, Scale, DollarSign, FileText } from 'lucide-react';
import { api } from '../lib/api';
import { useAuthStore } from '../stores/auth-store';

interface HeartbeatSummary {
    agent_id: string;
    total_heartbeats: number;
    ok_count: number;
    insight_count: number;
    action_count: number;
    escalation_count: number;
    last_heartbeat: string | null;
}

interface PulseOverview {
    total_heartbeats_24h: number;
    active_agents: number;
    pending_escalations: number;
    total_insights: number;
    agents: HeartbeatSummary[];
}

interface TimelineEntry {
    id: string;
    agent_id: string;
    result_type: string;
    checklist_item: string | null;
    action_taken: string | null;
    tokens_used: number;
    cost_usd: number;
    latency_ms: number;
    founder_notified: boolean;
    timestamp: string;
}

const STATUS_COLORS: Record<string, { bg: string; border: string; text: string; glow: string }> = {
    OK: { bg: 'bg-green-500/10', border: 'border-green-500/30', text: 'text-green-400', glow: 'shadow-green-500/20' },
    INSIGHT: { bg: 'bg-blue-500/10', border: 'border-blue-500/30', text: 'text-blue-400', glow: 'shadow-blue-500/20' },
    ACTION: { bg: 'bg-orange-500/10', border: 'border-orange-500/30', text: 'text-orange-400', glow: 'shadow-orange-500/20' },
    ESCALATION: { bg: 'bg-red-500/10', border: 'border-red-500/30', text: 'text-red-400', glow: 'shadow-red-500/20' },
};

const AGENT_LABELS: Record<string, string> = {
    business_copilot: 'Business CoPilot',
    technical_copilot: 'Technical CoPilot',
    fundraising_copilot: 'Fundraising CoPilot',
    sales_automation_agent: 'Sales Hunter',
    content_strategy_agent: 'Content Engine',
    data_analyst_agent: 'Data Analyst',
    churn_prediction_agent: 'Churn Guard',
    security_auditor_agent: 'Security Grid',
};

function getAgentLabel(id: string): string {
    return AGENT_LABELS[id] || id.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function getDominantStatus(agent: HeartbeatSummary): string {
    if (agent.escalation_count > 0) return 'ESCALATION';
    if (agent.action_count > 0) return 'ACTION';
    if (agent.insight_count > 0) return 'INSIGHT';
    return 'OK';
}

function timeAgo(ts: string | null): string {
    if (!ts) return 'Never';
    const diff = Date.now() - new Date(ts).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'Just now';
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    return `${Math.floor(hrs / 24)}d ago`;
}

export default function BusinessPulse() {
    const [pulse, setPulse] = useState<PulseOverview | null>(null);
    const [timeline, setTimeline] = useState<TimelineEntry[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState<string>('all');
    const [startupId, setStartupId] = useState<string>('');

    const fetchPulse = useCallback(async (sid: string) => {
        if (!sid) return;
        try {
            const [pulseRes, timelineRes] = await Promise.all([
                api.getPulse(sid),
                api.getPulseTimeline(sid, { limit: 50, ...(filter !== 'all' ? { result_type: filter } : {}) }),
            ]);
            setPulse(pulseRes);
            setTimeline(timelineRes);
        } catch (err) {
            console.error('Failed to fetch pulse data', err);
        } finally {
            setLoading(false);
        }
    }, [filter]);

    useEffect(() => {
        // Try to get startup ID from local storage or current context
        const stored = localStorage.getItem('currentStartupId');
        if (stored) {
            setStartupId(stored);
            fetchPulse(stored);
        } else {
            setLoading(false);
        }

        // Auto-refresh every 30 seconds
        const interval = setInterval(() => {
            if (startupId) fetchPulse(startupId);
        }, 30000);
        return () => clearInterval(interval);
    }, [startupId, fetchPulse]);

    const handleRunMission = async (mission: string, context: any) => {
        if (!startupId) return;
        try {
            await api.runOperationsMission(mission, context, startupId);
            fetchPulse(startupId); // Refresh to see new activity
            alert(`Mission "${mission}" started! Check timeline for results.`);
        } catch (err) {
            console.error("Mission failed", err);
            alert("Failed to start mission");
        }
    };

    return (
        <div className="min-h-screen bg-[#020202] text-white p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center border border-purple-500/30">
                        <Activity className="w-5 h-5 text-purple-400" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-black font-mono tracking-tight">BUSINESS PULSE</h1>
                        <p className="text-xs font-mono text-gray-500">OpenClaw Heartbeat Monitor // Real-time Operations</p>
                    </div>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={() => handleRunMission("financial_review", { metrics: { mrr: 1000, burn: 500 } })}
                        className="flex items-center gap-2 px-4 py-2 bg-green-500/10 border border-green-500/20 rounded font-mono text-xs text-green-400 hover:bg-green-500/20 transition-all"
                    >
                        <DollarSign className="w-3 h-3" /> AUDIT FINANCE
                    </button>
                    <button
                        onClick={() => handleRunMission("compliance_check", { type: "generic" })}
                        className="flex items-center gap-2 px-4 py-2 bg-blue-500/10 border border-blue-500/20 rounded font-mono text-xs text-blue-400 hover:bg-blue-500/20 transition-all"
                    >
                        <Scale className="w-3 h-3" /> LEGAL CHECK
                    </button>
                    <button
                        onClick={() => startupId && fetchPulse(startupId)}
                        className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded font-mono text-xs text-gray-400 hover:text-white hover:border-purple-500/50 transition-all"
                    >
                        <RefreshCw className="w-3 h-3" /> REFRESH
                    </button>
                </div>
            </div>

            {/* KPI Cards */}
            {pulse && (
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                    <div className="bg-white/5 border border-white/10 rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-2">
                            <Zap className="w-4 h-4 text-green-400" />
                            <span className="text-[10px] font-mono text-gray-500">HEARTBEATS (24H)</span>
                        </div>
                        <p className="text-3xl font-black font-mono">{pulse.total_heartbeats_24h}</p>
                    </div>
                    <div className="bg-white/5 border border-white/10 rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-2">
                            <Brain className="w-4 h-4 text-blue-400" />
                            <span className="text-[10px] font-mono text-gray-500">ACTIVE AGENTS</span>
                        </div>
                        <p className="text-3xl font-black font-mono">{pulse.active_agents}</p>
                    </div>
                    <div className="bg-white/5 border border-white/10 rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-2">
                            <Eye className="w-4 h-4 text-purple-400" />
                            <span className="text-[10px] font-mono text-gray-500">INSIGHTS</span>
                        </div>
                        <p className="text-3xl font-black font-mono">{pulse.total_insights}</p>
                    </div>
                    <div className="bg-white/5 border border-white/10 rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-2">
                            <AlertTriangle className="w-4 h-4 text-red-400" />
                            <span className="text-[10px] font-mono text-gray-500">PENDING ESCALATIONS</span>
                        </div>
                        <p className="text-3xl font-black font-mono text-red-400">{pulse.pending_escalations}</p>
                    </div>
                </div>
            )}

            {/* Agent Status Grid */}
            {pulse && pulse.agents.length > 0 && (
                <div className="mb-8">
                    <h2 className="text-sm font-mono font-bold text-gray-400 mb-4 flex items-center gap-2">
                        <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                        AGENT STATUS GRID
                    </h2>
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-3">
                        {pulse.agents.map((agent) => {
                            const status = getDominantStatus(agent);
                            const colors = STATUS_COLORS[status];
                            return (
                                <div
                                    key={agent.agent_id}
                                    className={`${colors.bg} border ${colors.border} rounded-lg p-3 shadow-lg ${colors.glow} transition-all hover:scale-105`}
                                >
                                    <div className="flex items-center justify-between mb-2">
                                        <span className={`text-[10px] font-mono font-bold ${colors.text}`}>{status}</span>
                                        <span className="text-[9px] font-mono text-gray-600">{timeAgo(agent.last_heartbeat)}</span>
                                    </div>
                                    <p className="text-xs font-bold font-mono text-white mb-1 truncate">
                                        {getAgentLabel(agent.agent_id)}
                                    </p>
                                    <div className="flex gap-2 text-[9px] font-mono text-gray-500">
                                        <span>⚡{agent.total_heartbeats}</span>
                                        <span className="text-blue-400">💡{agent.insight_count}</span>
                                        <span className="text-orange-400">⚙️{agent.action_count}</span>
                                        <span className="text-red-400">🚨{agent.escalation_count}</span>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}

            {/* Timeline Filter */}
            <div className="flex items-center gap-2 mb-4">
                <h2 className="text-sm font-mono font-bold text-gray-400 flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    HEARTBEAT TIMELINE
                </h2>
                <div className="flex gap-1 ml-auto">
                    {['all', 'OK', 'INSIGHT', 'ACTION', 'ESCALATION'].map((f) => (
                        <button
                            key={f}
                            onClick={() => setFilter(f)}
                            className={`px-3 py-1 text-[10px] font-mono rounded border transition-all ${filter === f
                                ? 'bg-purple-500/20 border-purple-500/50 text-purple-400'
                                : 'bg-white/5 border-white/10 text-gray-500 hover:text-white'
                                }`}
                        >
                            {f.toUpperCase()}
                        </button>
                    ))}
                </div>
            </div>

            {/* Timeline Entries */}
            <div className="space-y-2">
                {timeline.length === 0 && !loading && (
                    <div className="text-center py-16 text-gray-600 font-mono text-sm">
                        <Brain className="w-12 h-12 mx-auto mb-4 opacity-30" />
                        {startupId
                            ? 'No heartbeat activity yet. Agents will begin their first cycle shortly.'
                            : 'No startup selected. Visit your dashboard first to initialize.'}
                    </div>
                )}
                {timeline.map((entry) => {
                    const colors = STATUS_COLORS[entry.result_type] || STATUS_COLORS.OK;
                    return (
                        <div
                            key={entry.id}
                            className={`${colors.bg} border ${colors.border} rounded-lg p-4 flex items-start gap-4 transition-all hover:scale-[1.01]`}
                        >
                            <div className={`w-8 h-8 rounded flex items-center justify-center flex-shrink-0 ${colors.bg} border ${colors.border}`}>
                                {entry.result_type === 'OK' && <CheckCircle2 className={`w-4 h-4 ${colors.text}`} />}
                                {entry.result_type === 'INSIGHT' && <Eye className={`w-4 h-4 ${colors.text}`} />}
                                {entry.result_type === 'ACTION' && <Zap className={`w-4 h-4 ${colors.text}`} />}
                                {entry.result_type === 'ESCALATION' && <AlertTriangle className={`w-4 h-4 ${colors.text}`} />}
                            </div>
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-1">
                                    <span className="text-xs font-bold font-mono text-white">
                                        {getAgentLabel(entry.agent_id)}
                                    </span>
                                    <span className={`text-[10px] font-mono font-bold ${colors.text}`}>
                                        {entry.result_type}
                                    </span>
                                    {entry.founder_notified && (
                                        <span className="text-[9px] font-mono text-yellow-400 bg-yellow-500/10 px-1.5 py-0.5 rounded">
                                            FOUNDER_NOTIFIED
                                        </span>
                                    )}
                                </div>
                                {entry.checklist_item && (
                                    <p className="text-[11px] font-mono text-gray-400 mb-1">
                                        Check: {entry.checklist_item}
                                    </p>
                                )}
                                {entry.action_taken && (
                                    <p className="text-[11px] font-mono text-gray-300">
                                        → {entry.action_taken}
                                    </p>
                                )}
                            </div>
                            <div className="text-right flex-shrink-0">
                                <p className="text-[9px] font-mono text-gray-600">
                                    {new Date(entry.timestamp).toLocaleTimeString()}
                                </p>
                                <p className="text-[9px] font-mono text-gray-700">
                                    {entry.latency_ms}ms • ${entry.cost_usd.toFixed(4)}
                                </p>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
