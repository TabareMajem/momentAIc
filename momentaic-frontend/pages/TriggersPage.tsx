import React, { useState, useEffect } from 'react';

interface TriggerRule {
    id: string;
    name: string;
    description?: string;
    triggerType: 'metric' | 'time' | 'event' | 'webhook';
    condition: Record<string, any>;
    action: Record<string, any>;
    isActive: boolean;
    isPaused: boolean;
    lastTriggeredAt?: string;
    triggerCount: number;
}

const AGENT_OPTIONS = [
    { value: 'finance_cfo', label: 'Finance CFO', icon: '💰' },
    { value: 'growth_hacker', label: 'Growth Hacker', icon: '📈' },
    { value: 'customer_success', label: 'Customer Success', icon: '🎧' },
    { value: 'data_analyst', label: 'Data Analyst', icon: '📊' },
    { value: 'tech_lead', label: 'Tech Lead', icon: '⚙️' },
    { value: 'strategy', label: 'Strategy', icon: '🎯' },
];

const METRIC_OPTIONS = [
    { value: 'mrr', label: 'Monthly Recurring Revenue' },
    { value: 'arr', label: 'Annual Recurring Revenue' },
    { value: 'churn', label: 'Churn Rate' },
    { value: 'dau', label: 'Daily Active Users' },
    { value: 'commits', label: 'Commits per Week' },
    { value: 'leads', label: 'New Leads' },
];

const OPERATOR_OPTIONS = [
    { value: 'gt', label: 'Greater than' },
    { value: 'lt', label: 'Less than' },
    { value: 'increases_by', label: 'Increases by' },
    { value: 'decreases_by', label: 'Decreases by' },
];

export default function TriggersPage() {
    const [triggers, setTriggers] = useState<TriggerRule[]>([]);
    const [loading, setLoading] = useState(true);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [creating, setCreating] = useState(false);

    // Form state
    const [form, setForm] = useState({
        name: '',
        triggerType: 'metric' as const,
        metric: 'mrr',
        operator: 'decreases_by',
        value: 10,
        unit: 'percent',
        agent: 'finance_cfo',
        task: 'analyze_metric_change',
        cron: '0 9 * * 1',
    });

    useEffect(() => {
        fetchTriggers();
    }, []);

    const fetchTriggers = async () => {
        try {
            // In production: fetch from API
            // const response = await fetch('/api/v1/triggers?startup_id=...');
            setTriggers([
                {
                    id: '1',
                    name: 'MRR Drop Alert',
                    description: 'Alert when MRR drops more than 10%',
                    triggerType: 'metric',
                    condition: { metric: 'mrr', operator: 'decreases_by', value: 10, unit: 'percent' },
                    action: { agent: 'finance_cfo', task: 'analyze_metric_change' },
                    isActive: true,
                    isPaused: false,
                    lastTriggeredAt: '2024-12-15T10:30:00Z',
                    triggerCount: 3,
                },
                {
                    id: '2',
                    name: 'Weekly Growth Report',
                    description: 'Every Monday at 9 AM UTC',
                    triggerType: 'time',
                    condition: { cron: '0 9 * * 1' },
                    action: { agent: 'growth_hacker', task: 'generate_weekly_report' },
                    isActive: true,
                    isPaused: false,
                    triggerCount: 8,
                },
            ]);
        } catch (error) {
            console.error('Failed to fetch triggers:', error);
        } finally {
            setLoading(false);
        }
    };

    const createTrigger = async () => {
        setCreating(true);
        try {
            const condition = form.triggerType === 'metric'
                ? { metric: form.metric, operator: form.operator, value: form.value, unit: form.unit }
                : { cron: form.cron };

            const newTrigger: TriggerRule = {
                id: crypto.randomUUID(),
                name: form.name,
                triggerType: form.triggerType,
                condition,
                action: { agent: form.agent, task: form.task },
                isActive: true,
                isPaused: false,
                triggerCount: 0,
            };

            // In production: POST to API
            setTriggers(prev => [...prev, newTrigger]);
            setShowCreateModal(false);
            setForm({
                name: '',
                triggerType: 'metric',
                metric: 'mrr',
                operator: 'decreases_by',
                value: 10,
                unit: 'percent',
                agent: 'finance_cfo',
                task: 'analyze_metric_change',
                cron: '0 9 * * 1',
            });
        } catch (error) {
            console.error('Failed to create trigger:', error);
        } finally {
            setCreating(false);
        }
    };

    const toggleTrigger = async (id: string, active: boolean) => {
        setTriggers(prev =>
            prev.map(t => (t.id === id ? { ...t, isActive: active } : t))
        );
    };

    const deleteTrigger = async (id: string) => {
        setTriggers(prev => prev.filter(t => t.id !== id));
    };

    const getTriggerIcon = (type: TriggerRule['triggerType']) => {
        const icons = { metric: '📊', time: '⏰', event: '⚡', webhook: '🔗' };
        return icons[type];
    };

    const getAgentInfo = (agentId: string) => {
        return AGENT_OPTIONS.find(a => a.value === agentId) || { label: agentId, icon: '🤖' };
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900/20 to-gray-900 p-6">
            <div className="max-w-6xl mx-auto">
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <h1 className="text-3xl font-bold text-white">Proactive Triggers</h1>
                        <p className="text-gray-400">Automate agent actions based on metrics and schedules</p>
                    </div>
                    <button
                        onClick={() => setShowCreateModal(true)}
                        className="px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg font-medium hover:opacity-90 transition"
                    >
                        + Create Trigger
                    </button>
                </div>

                {/* Triggers List */}
                {loading ? (
                    <div className="text-gray-400 text-center py-12">Loading triggers...</div>
                ) : triggers.length === 0 ? (
                    <div className="text-center py-12 bg-gray-800/30 rounded-xl border border-gray-700/50">
                        <p className="text-gray-400 mb-4">No triggers configured yet</p>
                        <button
                            onClick={() => setShowCreateModal(true)}
                            className="px-4 py-2 bg-purple-600 text-white rounded-lg"
                        >
                            Create Your First Trigger
                        </button>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {triggers.map(trigger => (
                            <div
                                key={trigger.id}
                                className={`bg-gray-800/50 border rounded-xl p-5 ${trigger.isActive ? 'border-gray-700' : 'border-gray-700/50 opacity-60'
                                    }`}
                            >
                                <div className="flex items-start justify-between">
                                    <div className="flex items-start gap-4">
                                        <div className="text-3xl">{getTriggerIcon(trigger.triggerType)}</div>
                                        <div>
                                            <h3 className="text-lg font-semibold text-white">{trigger.name}</h3>
                                            {trigger.description && (
                                                <p className="text-sm text-gray-400">{trigger.description}</p>
                                            )}

                                            {/* Condition */}
                                            <div className="mt-2 flex gap-2 flex-wrap">
                                                <span className="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded">
                                                    {trigger.triggerType === 'metric'
                                                        ? `${trigger.condition.metric} ${trigger.condition.operator} ${trigger.condition.value}${trigger.condition.unit === 'percent' ? '%' : ''}`
                                                        : `Cron: ${trigger.condition.cron}`}
                                                </span>
                                                <span className="px-2 py-1 bg-purple-500/20 text-purple-400 text-xs rounded flex items-center gap-1">
                                                    {getAgentInfo(trigger.action.agent).icon} {getAgentInfo(trigger.action.agent).label}
                                                </span>
                                            </div>

                                            {/* Stats */}
                                            <div className="mt-2 text-xs text-gray-500">
                                                Triggered {trigger.triggerCount} times
                                                {trigger.lastTriggeredAt && (
                                                    <> • Last: {new Date(trigger.lastTriggeredAt).toLocaleDateString()}</>
                                                )}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Actions */}
                                    <div className="flex items-center gap-3">
                                        <label className="flex items-center cursor-pointer">
                                            <div className="relative">
                                                <input
                                                    type="checkbox"
                                                    checked={trigger.isActive}
                                                    onChange={e => toggleTrigger(trigger.id, e.target.checked)}
                                                    className="sr-only"
                                                />
                                                <div className={`w-10 h-6 rounded-full transition ${trigger.isActive ? 'bg-green-600' : 'bg-gray-600'}`}></div>
                                                <div className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition ${trigger.isActive ? 'translate-x-4' : ''}`}></div>
                                            </div>
                                        </label>
                                        <button
                                            onClick={() => deleteTrigger(trigger.id)}
                                            className="p-2 text-red-400 hover:bg-red-600/20 rounded-lg transition"
                                        >
                                            🗑️
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Create Modal */}
                {showCreateModal && (
                    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
                        <div className="bg-gray-800 rounded-xl p-6 w-full max-w-lg border border-gray-700">
                            <h2 className="text-xl font-bold text-white mb-4">Create Trigger</h2>

                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm text-gray-400 mb-1">Trigger Name</label>
                                    <input
                                        type="text"
                                        value={form.name}
                                        onChange={e => setForm({ ...form, name: e.target.value })}
                                        placeholder="e.g., MRR Drop Alert"
                                        className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm text-gray-400 mb-1">Trigger Type</label>
                                    <select
                                        value={form.triggerType}
                                        onChange={e => setForm({ ...form, triggerType: e.target.value as 'metric' | 'time' })}
                                        className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                                    >
                                        <option value="metric">📊 Metric Change</option>
                                        <option value="time">⏰ Scheduled (Cron)</option>
                                    </select>
                                </div>

                                {form.triggerType === 'metric' ? (
                                    <>
                                        <div className="grid grid-cols-2 gap-3">
                                            <div>
                                                <label className="block text-sm text-gray-400 mb-1">Metric</label>
                                                <select
                                                    value={form.metric}
                                                    onChange={e => setForm({ ...form, metric: e.target.value })}
                                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                                                >
                                                    {METRIC_OPTIONS.map(m => (
                                                        <option key={m.value} value={m.value}>{m.label}</option>
                                                    ))}
                                                </select>
                                            </div>
                                            <div>
                                                <label className="block text-sm text-gray-400 mb-1">Condition</label>
                                                <select
                                                    value={form.operator}
                                                    onChange={e => setForm({ ...form, operator: e.target.value })}
                                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                                                >
                                                    {OPERATOR_OPTIONS.map(o => (
                                                        <option key={o.value} value={o.value}>{o.label}</option>
                                                    ))}
                                                </select>
                                            </div>
                                        </div>
                                        <div className="grid grid-cols-2 gap-3">
                                            <div>
                                                <label className="block text-sm text-gray-400 mb-1">Value</label>
                                                <input
                                                    type="number"
                                                    value={form.value}
                                                    onChange={e => setForm({ ...form, value: parseInt(e.target.value) })}
                                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm text-gray-400 mb-1">Unit</label>
                                                <select
                                                    value={form.unit}
                                                    onChange={e => setForm({ ...form, unit: e.target.value })}
                                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                                                >
                                                    <option value="percent">Percent (%)</option>
                                                    <option value="absolute">Absolute</option>
                                                </select>
                                            </div>
                                        </div>
                                    </>
                                ) : (
                                    <div>
                                        <label className="block text-sm text-gray-400 mb-1">Cron Expression</label>
                                        <input
                                            type="text"
                                            value={form.cron}
                                            onChange={e => setForm({ ...form, cron: e.target.value })}
                                            placeholder="0 9 * * 1 (Every Monday at 9 AM)"
                                            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white font-mono"
                                        />
                                        <p className="text-xs text-gray-500 mt-1">Format: minute hour day month weekday</p>
                                    </div>
                                )}

                                <div>
                                    <label className="block text-sm text-gray-400 mb-1">Agent to Activate</label>
                                    <select
                                        value={form.agent}
                                        onChange={e => setForm({ ...form, agent: e.target.value })}
                                        className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                                    >
                                        {AGENT_OPTIONS.map(a => (
                                            <option key={a.value} value={a.value}>{a.icon} {a.label}</option>
                                        ))}
                                    </select>
                                </div>
                            </div>

                            <div className="flex gap-3 mt-6">
                                <button
                                    onClick={() => setShowCreateModal(false)}
                                    className="flex-1 px-4 py-2 bg-gray-700 text-white rounded-lg"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={createTrigger}
                                    disabled={!form.name || creating}
                                    className="flex-1 px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg disabled:opacity-50"
                                >
                                    {creating ? 'Creating...' : 'Create Trigger'}
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Info Box */}
                <div className="mt-10 p-6 bg-gradient-to-r from-blue-900/30 to-purple-900/30 border border-blue-500/30 rounded-xl">
                    <h3 className="text-lg font-semibold text-white mb-3">⚡ Trigger Examples</h3>
                    <div className="grid md:grid-cols-2 gap-4 text-sm text-gray-300">
                        <div className="p-3 bg-gray-800/50 rounded-lg">
                            <strong className="text-blue-400">MRR Drop Alert</strong>
                            <p>When MRR drops by 10% → Finance CFO analyzes and alerts you</p>
                        </div>
                        <div className="p-3 bg-gray-800/50 rounded-lg">
                            <strong className="text-purple-400">Weekly Growth Report</strong>
                            <p>Every Monday → Growth Hacker generates a performance summary</p>
                        </div>
                        <div className="p-3 bg-gray-800/50 rounded-lg">
                            <strong className="text-green-400">Churn Risk Alert</strong>
                            <p>When churn exceeds 5% → Customer Success suggests interventions</p>
                        </div>
                        <div className="p-3 bg-gray-800/50 rounded-lg">
                            <strong className="text-orange-400">New Lead Processing</strong>
                            <p>When lead score {'>'} 80 → Sales Hunter starts outreach sequence</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
