import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../stores/auth-store';
import { api } from '../lib/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../components/ui/Tabs';
import { useToast } from '../components/ui/Toast';
import {
    Zap, Shield, Bot, TrendingUp, DollarSign, Users, Eye,
    Play, Pause, Settings, AlertTriangle, CheckCircle, Clock,
    BarChart3, MessageSquare, Target, Megaphone, Brain
} from 'lucide-react';

interface AutonomySettings {
    id: string;
    startup_id: string;
    global_level: number;
    marketing_level: number | null;
    sales_level: number | null;
    finance_level: number | null;
    content_level: number | null;
    competitive_level: number | null;
    daily_action_limit: number;
    daily_spend_limit_usd: number;
    is_paused: boolean;
    paused_at: string | null;
    paused_reason: string | null;
    notify_on_action: boolean;
    notify_channel: string;
}

interface ProactiveAction {
    id: string;
    agent_type: string;
    action_type: string;
    category: string;
    title: string;
    status: string;
    created_at: string;
}

const AUTONOMY_LEVELS = [
    { level: 0, name: 'Observer', icon: Eye, color: 'gray', description: 'Information only. No actions taken.' },
    { level: 1, name: 'Advisor', icon: MessageSquare, color: 'blue', description: 'Drafts content for your approval.' },
    { level: 2, name: 'Co-Pilot', icon: Bot, color: 'purple', description: 'Acts with quick confirmation.' },
    { level: 3, name: 'Autopilot', icon: Zap, color: 'cyan', description: 'Full autonomy within guardrails.' },
];

const CATEGORIES = [
    { key: 'marketing_level', name: 'Marketing', icon: Megaphone, description: 'Social posts, ads, campaigns' },
    { key: 'sales_level', name: 'Sales', icon: Target, description: 'Outreach, lead scoring, proposals' },
    { key: 'finance_level', name: 'Finance', icon: DollarSign, description: 'KPI reports, burn rate alerts' },
    { key: 'content_level', name: 'Content', icon: Brain, description: 'Blog posts, newsletters, ideas' },
    { key: 'competitive_level', name: 'Competitive', icon: BarChart3, description: 'Competitor monitoring, SWOT' },
];

export default function AutonomySettingsPage() {
    const { user } = useAuthStore();
    const { toast } = useToast();
    const [settings, setSettings] = useState<AutonomySettings | null>(null);
    const [actions, setActions] = useState<ProactiveAction[]>([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [startupId, setStartupId] = useState<string | null>(null);
    const [activeTab, setActiveTab] = useState('levels');

    // Get first startup (in production, this would be selectable)
    useEffect(() => {
        const fetchData = async () => {
            try {
                const startups = await api.getStartups();
                if (startups.length > 0) {
                    setStartupId(startups[0].id);
                }
            } catch (err) {
                console.error(err);
            }
        };
        fetchData();
    }, []);

    // Fetch settings when startup changes
    useEffect(() => {
        if (!startupId) return;

        const fetchSettings = async () => {
            setLoading(true);
            try {
                const response = await api.client.get(`/api/v1/startups/${startupId}/autonomy`);
                setSettings(response.data);

                const actionsResponse = await api.client.get(`/api/v1/startups/${startupId}/autonomy/actions?limit=20`);
                setActions(actionsResponse.data);
            } catch (err) {
                console.error(err);
                toast({ type: 'error', title: 'Error', message: 'Failed to load autonomy settings' });
            } finally {
                setLoading(false);
            }
        };
        fetchSettings();
    }, [startupId]);

    const updateSettings = async (updates: Partial<AutonomySettings>) => {
        if (!startupId) return;
        setSaving(true);
        try {
            const response = await api.client.put(`/api/v1/startups/${startupId}/autonomy`, updates);
            setSettings(response.data);
            toast({ type: 'success', title: 'Settings Saved', message: 'Your autonomy preferences have been updated.' });
        } catch (err) {
            console.error(err);
            toast({ type: 'error', title: 'Error', message: 'Failed to save settings' });
        } finally {
            setSaving(false);
        }
    };

    const togglePause = async () => {
        if (!startupId || !settings) return;
        try {
            if (settings.is_paused) {
                await api.client.post(`/api/v1/startups/${startupId}/autonomy/resume`);
                toast({ type: 'success', title: 'Agents Resumed', message: 'Proactive agents are now active.' });
            } else {
                await api.client.post(`/api/v1/startups/${startupId}/autonomy/pause`);
                toast({ type: 'warning', title: 'Agents Paused', message: 'All proactive agents have been stopped.' });
            }
            // Refresh settings
            const response = await api.client.get(`/api/v1/startups/${startupId}/autonomy`);
            setSettings(response.data);
        } catch (err) {
            console.error(err);
            toast({ type: 'error', title: 'Error', message: 'Failed to toggle pause state' });
        }
    };

    if (!user || loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-purple"></div>
            </div>
        );
    }

    if (!settings) {
        return (
            <div className="text-center py-12">
                <p className="text-gray-500">No startup found. Create a startup first.</p>
            </div>
        );
    }

    const currentLevel = AUTONOMY_LEVELS[settings.global_level];

    return (
        <div className="max-w-5xl mx-auto space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                        <Bot className="w-7 h-7 text-brand-purple" />
                        Proactive Agent Control
                    </h1>
                    <p className="text-gray-500 mt-1">Configure how your AI workforce operates</p>
                </div>

                {/* Emergency Pause Button */}
                <Button
                    variant={settings.is_paused ? 'cyber' : 'destructive'}
                    onClick={togglePause}
                    className="flex items-center gap-2"
                >
                    {settings.is_paused ? (
                        <>
                            <Play className="w-4 h-4" />
                            Resume All Agents
                        </>
                    ) : (
                        <>
                            <Pause className="w-4 h-4" />
                            Emergency Pause
                        </>
                    )}
                </Button>
            </div>

            {/* Paused Warning */}
            {settings.is_paused && (
                <Card className="border-yellow-500/50 bg-yellow-500/10">
                    <CardContent className="py-4 flex items-center gap-3">
                        <AlertTriangle className="w-5 h-5 text-yellow-500" />
                        <span className="text-yellow-700 font-medium">
                            All proactive agents are currently paused
                            {settings.paused_reason && `: ${settings.paused_reason}`}
                        </span>
                    </CardContent>
                </Card>
            )}

            {/* Global Level Card */}
            <Card className="border-brand-purple/30 bg-gradient-to-br from-brand-purple/5 to-transparent">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Zap className="w-5 h-5 text-brand-purple" />
                        Global Autonomy Level
                    </CardTitle>
                    <CardDescription>
                        Set the default autonomy level for all agent categories
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-4 gap-4">
                        {AUTONOMY_LEVELS.map((level) => {
                            const Icon = level.icon;
                            const isSelected = settings.global_level === level.level;
                            return (
                                <button
                                    key={level.level}
                                    onClick={() => updateSettings({ global_level: level.level })}
                                    className={`
                                        p-4 rounded-xl border-2 transition-all text-left
                                        ${isSelected
                                            ? `border-brand-${level.color} bg-brand-${level.color}/10 ring-2 ring-brand-${level.color}/30`
                                            : 'border-gray-200 hover:border-gray-300 bg-white'
                                        }
                                    `}
                                    disabled={saving}
                                >
                                    <div className="flex items-center gap-2 mb-2">
                                        <Icon className={`w-5 h-5 ${isSelected ? `text-brand-${level.color}` : 'text-gray-400'}`} />
                                        <span className={`font-semibold ${isSelected ? `text-brand-${level.color}` : 'text-gray-700'}`}>
                                            {level.name}
                                        </span>
                                    </div>
                                    <p className="text-xs text-gray-500">{level.description}</p>
                                    {isSelected && (
                                        <Badge className="mt-2 bg-brand-purple text-white">Active</Badge>
                                    )}
                                </button>
                            );
                        })}
                    </div>
                </CardContent>
            </Card>

            {/* Tabs for Categories and Safety */}
            <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList className="grid grid-cols-3 w-full max-w-md">
                    <TabsTrigger value="levels">Category Levels</TabsTrigger>
                    <TabsTrigger value="safety">Safety Rails</TabsTrigger>
                    <TabsTrigger value="history">Action History</TabsTrigger>
                </TabsList>

                {/* Category Overrides */}
                <TabsContent value="levels" className="mt-4">
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-lg">Category-Specific Overrides</CardTitle>
                            <CardDescription>
                                Set different autonomy levels for specific agent categories. Leave blank to use global level.
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {CATEGORIES.map((category) => {
                                const Icon = category.icon;
                                const currentValue = settings[category.key as keyof AutonomySettings] as number | null;
                                return (
                                    <div key={category.key} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                                        <div className="flex items-center gap-3">
                                            <div className="p-2 bg-white rounded-lg shadow-sm">
                                                <Icon className="w-5 h-5 text-brand-purple" />
                                            </div>
                                            <div>
                                                <h4 className="font-medium text-gray-900">{category.name}</h4>
                                                <p className="text-xs text-gray-500">{category.description}</p>
                                            </div>
                                        </div>
                                        <select
                                            value={currentValue ?? ''}
                                            onChange={(e) => {
                                                const val = e.target.value === '' ? null : parseInt(e.target.value);
                                                updateSettings({ [category.key]: val } as any);
                                            }}
                                            className="px-3 py-2 rounded-lg border border-gray-200 bg-white text-sm focus:ring-2 focus:ring-brand-purple focus:border-transparent"
                                        >
                                            <option value="">Use Global ({AUTONOMY_LEVELS[settings.global_level].name})</option>
                                            {AUTONOMY_LEVELS.map((level) => (
                                                <option key={level.level} value={level.level}>{level.name}</option>
                                            ))}
                                        </select>
                                    </div>
                                );
                            })}
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Safety Rails */}
                <TabsContent value="safety" className="mt-4">
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-lg flex items-center gap-2">
                                <Shield className="w-5 h-5 text-green-500" />
                                Safety Guardrails
                            </CardTitle>
                            <CardDescription>
                                Set limits to protect your startup from unexpected agent behavior
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            <div className="grid grid-cols-2 gap-6">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Daily Action Limit
                                    </label>
                                    <Input
                                        type="number"
                                        value={settings.daily_action_limit}
                                        onChange={(e) => updateSettings({ daily_action_limit: parseInt(e.target.value) || 50 })}
                                        min={1}
                                        max={500}
                                    />
                                    <p className="text-xs text-gray-500 mt-1">Max actions agents can take per day</p>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Daily Spend Limit (USD)
                                    </label>
                                    <Input
                                        type="number"
                                        value={settings.daily_spend_limit_usd}
                                        onChange={(e) => updateSettings({ daily_spend_limit_usd: parseFloat(e.target.value) || 100 })}
                                        min={0}
                                        max={10000}
                                    />
                                    <p className="text-xs text-gray-500 mt-1">Max ad spend agents can authorize</p>
                                </div>
                            </div>

                            <div className="border-t pt-4">
                                <h4 className="font-medium text-gray-900 mb-3">Notification Preferences</h4>
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="font-medium text-gray-700">Notify on agent actions</p>
                                        <p className="text-xs text-gray-500">Get notified when agents take actions</p>
                                    </div>
                                    <label className="relative inline-flex items-center cursor-pointer">
                                        <input
                                            type="checkbox"
                                            className="sr-only peer"
                                            checked={settings.notify_on_action}
                                            onChange={(e) => updateSettings({ notify_on_action: e.target.checked })}
                                        />
                                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-brand-purple"></div>
                                    </label>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Action History */}
                <TabsContent value="history" className="mt-4">
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-lg flex items-center gap-2">
                                <Clock className="w-5 h-5 text-blue-500" />
                                Recent Agent Actions
                            </CardTitle>
                            <CardDescription>
                                Review what your AI workforce has been doing
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            {actions.length === 0 ? (
                                <div className="text-center py-8 text-gray-500">
                                    <Bot className="w-12 h-12 mx-auto mb-3 opacity-30" />
                                    <p>No actions yet. Your agents will start working soon!</p>
                                </div>
                            ) : (
                                <div className="space-y-3">
                                    {actions.map((action) => (
                                        <div key={action.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                            <div className="flex items-center gap-3">
                                                <div className={`w-2 h-2 rounded-full ${action.status === 'executed' ? 'bg-green-500' :
                                                        action.status === 'pending_approval' ? 'bg-yellow-500' :
                                                            action.status === 'failed' ? 'bg-red-500' : 'bg-gray-400'
                                                    }`} />
                                                <div>
                                                    <p className="font-medium text-gray-900 text-sm">{action.title}</p>
                                                    <p className="text-xs text-gray-500">{action.agent_type} • {action.category}</p>
                                                </div>
                                            </div>
                                            <div className="flex items-center gap-2">
                                                <Badge variant={action.status === 'executed' ? 'success' : 'default'}>
                                                    {action.status}
                                                </Badge>
                                                <span className="text-xs text-gray-400">
                                                    {new Date(action.created_at).toLocaleDateString()}
                                                </span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    );
}
