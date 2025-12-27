import React, { useState, useEffect } from 'react';

interface Integration {
    id: string;
    provider: string;
    name: string;
    status: 'active' | 'pending' | 'error' | 'disconnected';
    lastSyncAt?: string;
}

const INTEGRATION_CATEGORIES = [
    {
        name: 'Revenue & Payments',
        icon: '💰',
        integrations: [
            { provider: 'stripe', name: 'Stripe', description: 'Subscriptions & MRR', icon: '💳' },
            { provider: 'paypal', name: 'PayPal', description: 'Global payments', icon: '🅿️' },
            { provider: 'gumroad', name: 'Gumroad', description: 'Digital products', icon: '🎁' },
            { provider: 'lemonsqueezy', name: 'Lemon Squeezy', description: 'SaaS & tax handling', icon: '🍋' },
            { provider: 'paddle', name: 'Paddle', description: 'All-in-one payments', icon: '🏓' },
        ]
    },
    {
        name: 'Analytics & Data',
        icon: '📊',
        integrations: [
            { provider: 'google_analytics', name: 'Google Analytics', description: 'Website traffic', icon: '📈' },
            { provider: 'mixpanel', name: 'Mixpanel', description: 'Product analytics', icon: '🔬' },
            { provider: 'amplitude', name: 'Amplitude', description: 'User behavior', icon: '📉' },
            { provider: 'posthog', name: 'PostHog', description: 'Open source analytics', icon: '🦔' },
            { provider: 'plausible', name: 'Plausible', description: 'Privacy-friendly', icon: '🌿' },
        ]
    },
    {
        name: 'Development & Code',
        icon: '⚙️',
        integrations: [
            { provider: 'github', name: 'GitHub', description: 'Code & PRs', icon: '🐙' },
            { provider: 'gitlab', name: 'GitLab', description: 'DevOps platform', icon: '🦊' },
            { provider: 'linear', name: 'Linear', description: 'Issue tracking', icon: '🔵' },
            { provider: 'jira', name: 'Jira', description: 'Project management', icon: '🔷' },
            { provider: 'vercel', name: 'Vercel', description: 'Deployments', icon: '▲' },
        ]
    },
    {
        name: 'Team Communication',
        icon: '💬',
        integrations: [
            { provider: 'slack', name: 'Slack', description: 'Team messaging', icon: '💬' },
            { provider: 'discord', name: 'Discord', description: 'Community chat', icon: '🎮' },
            { provider: 'telegram', name: 'Telegram', description: 'Global messaging', icon: '✈️' },
            { provider: 'microsoft_teams', name: 'MS Teams', description: 'Enterprise comms', icon: '🟦' },
        ]
    },
    {
        name: 'CRM & Sales',
        icon: '🧲',
        integrations: [
            { provider: 'hubspot', name: 'HubSpot', description: 'All-in-one CRM', icon: '🧲' },
            { provider: 'pipedrive', name: 'Pipedrive', description: 'Sales CRM', icon: '📊' },
            { provider: 'salesforce', name: 'Salesforce', description: 'Enterprise CRM', icon: '☁️' },
            { provider: 'close', name: 'Close', description: 'Inside sales', icon: '📞' },
        ]
    },
    {
        name: 'Marketing & Social',
        icon: '📢',
        integrations: [
            { provider: 'linkedin', name: 'LinkedIn', description: 'Professional network', icon: '💼' },
            { provider: 'twitter', name: 'Twitter / X', description: 'Social presence', icon: '𝕏' },
            { provider: 'instagram', name: 'Instagram', description: 'Visual marketing', icon: '📸' },
            { provider: 'tiktok', name: 'TikTok', description: 'Viral growth', icon: '🎵' },
            { provider: 'mailchimp', name: 'Mailchimp', description: 'Email marketing', icon: '🐵' },
            { provider: 'convertkit', name: 'ConvertKit', description: 'Creator email', icon: '✉️' },
            { provider: 'beehiiv', name: 'Beehiiv', description: 'Newsletter growth', icon: '🐝' },
        ]
    },
    {
        name: 'E-commerce',
        icon: '🛒',
        integrations: [
            { provider: 'shopify', name: 'Shopify', description: 'Online store', icon: '🛍️' },
            { provider: 'woocommerce', name: 'WooCommerce', description: 'WordPress commerce', icon: '🔌' },
        ]
    },
    {
        name: 'Scheduling',
        icon: '📅',
        integrations: [
            { provider: 'calendly', name: 'Calendly', description: 'Appointment booking', icon: '📅' },
            { provider: 'calcom', name: 'Cal.com', description: 'Open source scheduling', icon: '🗓️' },
            { provider: 'google_calendar', name: 'Google Calendar', description: 'Calendar sync', icon: '📆' },
        ]
    },
    {
        name: 'Customer Support',
        icon: '🎧',
        integrations: [
            { provider: 'intercom', name: 'Intercom', description: 'Customer messaging', icon: '💬' },
            { provider: 'zendesk', name: 'Zendesk', description: 'Support ticketing', icon: '🎫' },
            { provider: 'crisp', name: 'Crisp', description: 'Live chat', icon: '💭' },
        ]
    },
    {
        name: 'Productivity & Docs',
        icon: '📝',
        integrations: [
            { provider: 'notion', name: 'Notion', description: 'Workspace docs', icon: '📝' },
            { provider: 'airtable', name: 'Airtable', description: 'Spreadsheet-database', icon: '📋' },
            { provider: 'google_drive', name: 'Google Drive', description: 'File storage', icon: '📁' },
            { provider: 'coda', name: 'Coda', description: 'Doc-apps', icon: '📄' },
        ]
    },
    {
        name: 'Video & Meetings',
        icon: '🎥',
        integrations: [
            { provider: 'zoom', name: 'Zoom', description: 'Video meetings', icon: '📹' },
            { provider: 'loom', name: 'Loom', description: 'Async video', icon: '🎬' },
        ]
    },
    {
        name: 'Design',
        icon: '🎨',
        integrations: [
            { provider: 'figma', name: 'Figma', description: 'UI/UX design', icon: '🎨' },
            { provider: 'canva', name: 'Canva', description: 'Graphic design', icon: '🖼️' },
        ]
    },
    {
        name: 'Accounting',
        icon: '🧮',
        integrations: [
            { provider: 'quickbooks', name: 'QuickBooks', description: 'Small business accounting', icon: '💵' },
            { provider: 'xero', name: 'Xero', description: 'Cloud accounting', icon: '📒' },
        ]
    },
];

export default function IntegrationsPage() {
    const [integrations, setIntegrations] = useState<Integration[]>([]);
    const [loading, setLoading] = useState(true);
    const [connecting, setConnecting] = useState<string | null>(null);
    const [syncing, setSyncing] = useState<string | null>(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

    useEffect(() => {
        fetchIntegrations();
    }, []);

    const fetchIntegrations = async () => {
        try {
            setIntegrations([]);
        } catch (error) {
            console.error('Failed to fetch integrations:', error);
        } finally {
            setLoading(false);
        }
    };

    const connectIntegration = async (provider: string) => {
        setConnecting(provider);
        try {
            setTimeout(() => {
                const info = INTEGRATION_CATEGORIES.flatMap(c => c.integrations).find(i => i.provider === provider);
                const newIntegration: Integration = {
                    id: crypto.randomUUID(),
                    provider,
                    name: info?.name || provider,
                    status: 'active',
                    lastSyncAt: new Date().toISOString(),
                };
                setIntegrations(prev => [...prev, newIntegration]);
                setConnecting(null);
            }, 1500);
        } catch (error) {
            console.error('Failed to connect:', error);
            setConnecting(null);
        }
    };

    const disconnectIntegration = async (id: string) => {
        setIntegrations(prev => prev.filter(i => i.id !== id));
    };

    const syncIntegration = async (id: string) => {
        setSyncing(id);
        setTimeout(() => {
            setIntegrations(prev => prev.map(i =>
                i.id === id ? { ...i, lastSyncAt: new Date().toISOString() } : i
            ));
            setSyncing(null);
        }, 2000);
    };

    const getStatusBadge = (status: Integration['status']) => {
        const styles: Record<string, string> = {
            active: 'bg-green-500/20 text-green-400 border-green-500/30',
            pending: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
            error: 'bg-red-500/20 text-red-400 border-red-500/30',
            disconnected: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
        };
        return (
            <span className={`px-2 py-1 rounded-full text-xs border ${styles[status]}`}>
                {status}
            </span>
        );
    };

    const connectedProviders = new Set(integrations.map(i => i.provider));

    const filteredCategories = INTEGRATION_CATEGORIES
        .filter(cat => !selectedCategory || cat.name === selectedCategory)
        .map(cat => ({
            ...cat,
            integrations: cat.integrations.filter(i =>
                i.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                i.description.toLowerCase().includes(searchQuery.toLowerCase())
            )
        }))
        .filter(cat => cat.integrations.length > 0);

    const totalIntegrations = INTEGRATION_CATEGORIES.reduce((sum, cat) => sum + cat.integrations.length, 0);

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900/20 to-gray-900 p-6">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-white mb-2">Integration Hub</h1>
                    <p className="text-gray-400">
                        Connect <span className="text-purple-400 font-semibold">{totalIntegrations}+</span> tools to build your empire from anywhere 🌍
                    </p>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                    <div className="bg-gradient-to-br from-green-900/30 to-green-900/10 border border-green-500/30 rounded-xl p-4">
                        <div className="text-3xl font-bold text-green-400">{integrations.length}</div>
                        <div className="text-sm text-green-300/70">Connected</div>
                    </div>
                    <div className="bg-gradient-to-br from-purple-900/30 to-purple-900/10 border border-purple-500/30 rounded-xl p-4">
                        <div className="text-3xl font-bold text-purple-400">{totalIntegrations}</div>
                        <div className="text-sm text-purple-300/70">Available</div>
                    </div>
                    <div className="bg-gradient-to-br from-blue-900/30 to-blue-900/10 border border-blue-500/30 rounded-xl p-4">
                        <div className="text-3xl font-bold text-blue-400">{INTEGRATION_CATEGORIES.length}</div>
                        <div className="text-sm text-blue-300/70">Categories</div>
                    </div>
                    <div className="bg-gradient-to-br from-orange-900/30 to-orange-900/10 border border-orange-500/30 rounded-xl p-4">
                        <div className="text-3xl font-bold text-orange-400">∞</div>
                        <div className="text-sm text-orange-300/70">Possibilities</div>
                    </div>
                </div>

                {/* Search & Filter */}
                <div className="flex flex-col md:flex-row gap-4 mb-8">
                    <input
                        type="text"
                        placeholder="Search integrations..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="flex-1 px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:border-purple-500 focus:outline-none"
                    />
                    <select
                        value={selectedCategory || ''}
                        onChange={(e) => setSelectedCategory(e.target.value || null)}
                        className="px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-xl text-white focus:border-purple-500 focus:outline-none"
                    >
                        <option value="">All Categories</option>
                        {INTEGRATION_CATEGORIES.map(cat => (
                            <option key={cat.name} value={cat.name}>{cat.icon} {cat.name}</option>
                        ))}
                    </select>
                </div>

                {/* Connected Integrations */}
                {integrations.length > 0 && (
                    <div className="mb-10">
                        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                            <span className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></span>
                            Connected ({integrations.length})
                        </h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {integrations.map(integration => (
                                <div key={integration.id} className="bg-gray-800/50 border border-green-500/30 rounded-xl p-4">
                                    <div className="flex items-center justify-between mb-3">
                                        <div className="flex items-center gap-3">
                                            <span className="text-2xl">
                                                {INTEGRATION_CATEGORIES.flatMap(c => c.integrations).find(i => i.provider === integration.provider)?.icon}
                                            </span>
                                            <span className="text-white font-medium">{integration.name}</span>
                                        </div>
                                        {getStatusBadge(integration.status)}
                                    </div>
                                    {integration.lastSyncAt && (
                                        <p className="text-xs text-gray-500 mb-3">
                                            Last synced: {new Date(integration.lastSyncAt).toLocaleString()}
                                        </p>
                                    )}
                                    <div className="flex gap-2">
                                        <button
                                            onClick={() => syncIntegration(integration.id)}
                                            disabled={syncing === integration.id}
                                            className="flex-1 px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm rounded-lg transition disabled:opacity-50"
                                        >
                                            {syncing === integration.id ? 'Syncing...' : 'Sync Now'}
                                        </button>
                                        <button
                                            onClick={() => disconnectIntegration(integration.id)}
                                            className="px-3 py-2 bg-red-600/20 hover:bg-red-600/30 text-red-400 text-sm rounded-lg transition"
                                        >
                                            Disconnect
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Available Integrations by Category */}
                {filteredCategories.map(category => (
                    <div key={category.name} className="mb-10">
                        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                            <span className="text-2xl">{category.icon}</span>
                            {category.name}
                            <span className="text-sm text-gray-500">({category.integrations.length})</span>
                        </h2>
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
                            {category.integrations.filter(i => !connectedProviders.has(i.provider)).map(integration => (
                                <div
                                    key={integration.provider}
                                    className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-4 hover:border-purple-500/50 hover:bg-gray-800/50 transition group"
                                >
                                    <div className="flex items-center gap-3 mb-3">
                                        <span className="text-2xl group-hover:scale-110 transition-transform">{integration.icon}</span>
                                        <div>
                                            <h3 className="text-white font-medium text-sm">{integration.name}</h3>
                                            <p className="text-xs text-gray-500">{integration.description}</p>
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => connectIntegration(integration.provider)}
                                        disabled={connecting === integration.provider}
                                        className="w-full px-3 py-2 bg-gray-700 hover:bg-purple-600 text-white text-sm rounded-lg transition disabled:opacity-50"
                                    >
                                        {connecting === integration.provider ? 'Connecting...' : 'Connect'}
                                    </button>
                                </div>
                            ))}
                            {category.integrations.filter(i => connectedProviders.has(i.provider)).map(integration => (
                                <div
                                    key={integration.provider}
                                    className="bg-green-900/20 border border-green-500/30 rounded-xl p-4"
                                >
                                    <div className="flex items-center gap-3 mb-3">
                                        <span className="text-2xl">{integration.icon}</span>
                                        <div>
                                            <h3 className="text-white font-medium text-sm">{integration.name}</h3>
                                            <p className="text-xs text-green-400">Connected ✓</p>
                                        </div>
                                    </div>
                                    <button
                                        disabled
                                        className="w-full px-3 py-2 bg-green-600/20 text-green-400 text-sm rounded-lg cursor-default"
                                    >
                                        Active
                                    </button>
                                </div>
                            ))}
                        </div>
                    </div>
                ))}

                {/* Entrepreneur CTA */}
                <div className="mt-12 p-8 bg-gradient-to-r from-purple-900/40 via-blue-900/40 to-cyan-900/40 border border-purple-500/30 rounded-2xl text-center">
                    <h3 className="text-2xl font-bold text-white mb-3">🚀 From Your Sofa to Fortune 500</h3>
                    <p className="text-gray-300 mb-6 max-w-2xl mx-auto">
                        Whether you're in Manila, Lima, Lagos, or anywhere in the world — these integrations give you the same
                        superpowers as billion-dollar companies. Connect, automate, and scale.
                    </p>
                    <div className="flex flex-wrap justify-center gap-3 text-sm">
                        <span className="px-4 py-2 bg-green-500/20 text-green-400 rounded-full">💰 Revenue Tracking</span>
                        <span className="px-4 py-2 bg-blue-500/20 text-blue-400 rounded-full">📊 Real-Time Analytics</span>
                        <span className="px-4 py-2 bg-purple-500/20 text-purple-400 rounded-full">🤖 AI-Powered Insights</span>
                        <span className="px-4 py-2 bg-orange-500/20 text-orange-400 rounded-full">⚡ Automated Triggers</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
