import React, { useState, useEffect } from 'react';
import { api } from '../lib/api';
import {
    Zap, Plug, ExternalLink, RefreshCw, Trash2,
    Search, Plus, ShieldCheck, Download, Globe,
    ArrowRight, MessageSquare, Briefcase, Code, Terminal,
    Star, Info, Sparkles, LayoutGrid, CheckCircle2,
    Database, Activity, Lock, Layers, Rocket
} from 'lucide-react';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../components/ui/Tabs';
import { Dialog } from '../components/ui/Dialog';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/Card';

interface Integration {
    id: string;
    provider: string;
    name: string;
    status: 'active' | 'pending' | 'error' | 'disconnected';
    lastSyncAt?: string;
    config?: any;
}

interface MarketplaceTool {
    id: string;
    name: string;
    description: string;
    mcp_url: string;
    category: string;
    icon: string;
    total_installs: number;
    version: string;
    author?: string;
}

const INTEGRATION_CATEGORIES = [
    { name: 'Revenue', icon: <Database className="w-4 h-4" />, providers: ['stripe', 'paypal', 'gumroad', 'lemonsqueezy'] },
    { name: 'Analytics', icon: <Activity className="w-4 h-4" />, providers: ['google_analytics', 'mixpanel', 'amplitude', 'posthog'] },
    { name: 'DevOps', icon: <Terminal className="w-4 h-4" />, providers: ['github', 'gitlab', 'vercel', 'linear'] },
    { name: 'Comms', icon: <MessageSquare className="w-4 h-4" />, providers: ['slack', 'discord', 'telegram'] },
];

export default function IntegrationsPage() {
    const [integrations, setIntegrations] = useState<Integration[]>([]);
    const [marketplaceTools, setMarketplaceTools] = useState<MarketplaceTool[]>([]);
    const [loading, setLoading] = useState(true);
    const [connecting, setConnecting] = useState<string | null>(null);
    const [syncing, setSyncing] = useState<string | null>(null);
    const [searchQuery, setSearchQuery] = useState('');

    const [startups, setStartups] = useState<any[]>([]);
    const [selectedStartupId, setSelectedStartupId] = useState<string | null>(null);

    // Developer Beta Modal State
    const [isSubmitModalOpen, setIsSubmitModalOpen] = useState(false);
    const [submitForm, setSubmitForm] = useState({ name: '', description: '', mcp_url: '', category: 'productivity' });

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        setLoading(true);
        try {
            const [startupList, tools] = await Promise.all([
                api.getStartups(),
                api.getMarketplaceTools()
            ]);

            setStartups(startupList);
            setMarketplaceTools(tools);

            if (startupList.length > 0) {
                const sid = startupList[0].id;
                setSelectedStartupId(sid);
                const results = await api.getIntegrations(sid);
                setIntegrations(results);
            }
        } catch (error) {
            console.error('Failed to load data:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchIntegrations = async () => {
        if (!selectedStartupId) return;
        try {
            const results = await api.getIntegrations(selectedStartupId);
            setIntegrations(results);
        } catch (error) {
            console.error('Failed to fetch integrations:', error);
        }
    };

    const connectIntegration = async (provider: string, configParams: any = {}) => {
        if (!selectedStartupId) {
            alert("Please select or create a startup first.");
            return;
        }

        let config = { ...configParams };
        if (provider === 'mcp' && !config.server_url) {
            const url = window.prompt("Enter MCP Server URL (e.g. http://localhost:3001/mcp):");
            if (!url) return;
            config = { server_url: url };
        }

        setConnecting(provider);
        try {
            await api.connectIntegration(selectedStartupId, {
                provider,
                name: config.name || provider,
                config
            });
            await fetchIntegrations();
        } catch (error) {
            console.error('Failed to connect:', error);
        } finally {
            setConnecting(null);
        }
    };

    const installMarketplaceTool = async (tool: MarketplaceTool) => {
        if (!selectedStartupId) return;
        setConnecting(tool.id);
        try {
            await api.installMarketplaceTool(selectedStartupId, tool.id);
            await fetchIntegrations();
        } catch (error) {
            console.error('Install failed:', error);
        } finally {
            setConnecting(null);
        }
    };

    const connectSocialOAuth = async (platform: 'twitter' | 'linkedin') => {
        if (!selectedStartupId) {
            alert("Please select a startup first.");
            return;
        }
        try {
            const response = await api.connectSocial(platform, selectedStartupId);
            if (response.auth_url) {
                window.location.href = response.auth_url;
            }
        } catch (error) {
            console.error('OAuth Init Failed:', error);
        }
    };

    const submitTool = async () => {
        if (!submitForm.name || !submitForm.mcp_url) return;
        try {
            await api.submitMarketplaceTool(submitForm);
            alert("Tool submitted for vetting! It will appear in the marketplace once approved.");
            setIsSubmitModalOpen(false);
            setSubmitForm({ name: '', description: '', mcp_url: '', category: 'productivity' });
        } catch (error) {
            console.error('Submission failed:', error);
        }
    };

    const disconnectIntegration = async (id: string) => {
        if (!selectedStartupId || !window.confirm("Disconnect this tool?")) return;
        try {
            await api.disconnectIntegration(selectedStartupId, id);
            setIntegrations(prev => prev.filter(i => i.id !== id));
        } catch (error) {
            console.error('Disconnect failed:', error);
        }
    };

    if (loading) return <div className="p-8 text-center font-mono animate-pulse">BOOTING INTEGRATION HUB...</div>;

    return (
        <div className="space-y-8 animate-fade-in pb-20">
            {/* Header with Startup Selector */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 bg-[#0a0a0a] border border-white/10 p-8 rounded-2xl relative overflow-hidden">
                <div className="absolute inset-0 bg-cyber-grid opacity-10 pointer-events-none"></div>

                <div className="relative z-10">
                    <h1 className="text-4xl font-black text-white uppercase tracking-tighter mb-2 italic">Hub // Integrations</h1>
                    <p className="text-gray-400 font-mono text-xs uppercase tracking-widest">Connect your startup to the global infrastructure.</p>
                </div>

                <div className="relative z-10 w-full md:w-64 space-y-2">
                    <label className="text-[10px] text-gray-500 font-mono uppercase font-bold tracking-[0.2em] flex items-center gap-2">
                        <Terminal className="w-3 h-3" /> Target Entity
                    </label>
                    <div className="relative group">
                        <div className="absolute -inset-0.5 bg-gradient-to-r from-[#00f0ff] to-[#a855f7] rounded-lg opacity-20 filter blur group-hover:opacity-40 transition border border-white/10"></div>
                        <select
                            value={selectedStartupId || ''}
                            onChange={(e) => setSelectedStartupId(e.target.value)}
                            className="relative w-full bg-black border border-white/10 rounded-lg px-4 py-2 text-white font-mono text-sm appearance-none cursor-pointer focus:outline-none focus:ring-1 focus:ring-[#00f0ff]"
                        >
                            {startups.map(s => <option key={s.id} value={s.id}>{s.name.toUpperCase()}</option>)}
                        </select>
                    </div>
                </div>
            </div>

            <Tabs defaultValue="installed" className="w-full">
                <div className="flex justify-between items-center mb-6">
                    <TabsList>
                        <TabsTrigger value="installed">Active Tools</TabsTrigger>
                        <TabsTrigger value="marketplace">Marketplace</TabsTrigger>
                        <TabsTrigger value="developer">Developer Beta</TabsTrigger>
                    </TabsList>

                    <div className="hidden md:flex items-center gap-4">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                            <Input
                                placeholder="SEARCH PROTOCOLS..."
                                className="pl-10 w-64 bg-black border-white/10 text-xs font-mono"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                            />
                        </div>
                    </div>
                </div>

                {/* TAB: ACTIVE TOOLS */}
                <TabsContent value="installed">
                    {integrations.length === 0 ? (
                        <div className="text-center py-20 border border-dashed border-white/10 rounded-2xl bg-white/5">
                            <Plug className="w-12 h-12 text-gray-700 mx-auto mb-4 opacity-20" />
                            <p className="font-mono text-xs text-gray-500 uppercase tracking-widest">No active integrations found for this entity.</p>
                            <Button variant="outline" className="mt-4 border-white/10 text-white" onClick={() => (document.querySelector('[value="marketplace"]') as HTMLButtonElement)?.click()}>
                                BROWSE MARKETPLACE
                            </Button>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {integrations.map(integration => (
                                <Card key={integration.id} className="bg-black border-white/10 hover:border-[#00f0ff]/30 transition group overflow-hidden">
                                    <div className="absolute top-0 right-0 p-4 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <Badge className="bg-green-500/20 text-green-400 border-green-500/30 text-[10px]">ACTIVE</Badge>
                                    </div>
                                    <CardHeader>
                                        <div className="flex items-center gap-4">
                                            <div className="p-3 bg-white/5 rounded-xl border border-white/10 group-hover:bg-[#00f0ff]/10 group-hover:border-[#00f0ff]/20 transition">
                                                <Zap className="w-5 h-5 text-[#00f0ff]" />
                                            </div>
                                            <div>
                                                <CardTitle className="text-sm font-bold uppercase tracking-tight">{integration.name}</CardTitle>
                                                <CardDescription className="text-[10px] font-mono text-gray-500 uppercase">{integration.provider.replace('_', ' ')}</CardDescription>
                                            </div>
                                        </div>
                                    </CardHeader>
                                    <div className="px-6 py-4 flex gap-2 border-t border-white/5 bg-white/[0.02]">
                                        <Button variant="outline" size="sm" className="flex-1 text-[10px] border-white/10 hover:bg-white/5" onClick={() => disconnectIntegration(integration.id)}>
                                            <Trash2 className="w-3 h-3 mr-2" /> DISCONNECT
                                        </Button>
                                        <Button variant="cyber" size="sm" className="flex-1 h-8 text-[10px]">
                                            CONFIGURE <ArrowRight className="w-3 h-3 ml-2" />
                                        </Button>
                                    </div>
                                </Card>
                            ))}
                        </div>
                    )}
                </TabsContent>

                {/* TAB: MARKETPLACE */}
                <TabsContent value="marketplace">
                    {/* SOCIAL CHANNELS (Phase 7 Update) */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                        <Card className="bg-black border border-white/10 hover:border-[#1DA1F2]/50 transition group overflow-hidden relative">
                            <div className="absolute inset-0 bg-[#1DA1F2]/5 opacity-0 group-hover:opacity-100 transition duration-500"></div>
                            <CardHeader className="relative z-10 flex flex-row items-center justify-between pb-2">
                                <div className="space-y-1">
                                    <div className="flex items-center gap-2">
                                        <div className="p-2 bg-[#1DA1F2]/20 rounded-lg">
                                            <svg className="w-5 h-5 text-[#1DA1F2]" fill="currentColor" viewBox="0 0 24 24"><path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.84 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z" /></svg>
                                        </div>
                                        <CardTitle className="text-lg font-black italic uppercase">Twitter X</CardTitle>
                                    </div>
                                    <CardDescription className="text-xs font-mono">Auto-post & Engagement</CardDescription>
                                </div>
                                {integrations.find(i => i.provider === 'twitter') ? (
                                    <Badge className="bg-green-500/20 text-green-400 border-green-500/30">CONNECTED</Badge>
                                ) : (
                                    <Button
                                        size="sm"
                                        variant="outline"
                                        className="border-[#1DA1F2]/30 text-[#1DA1F2] hover:bg-[#1DA1F2]/10"
                                        onClick={() => connectSocialOAuth('twitter')}
                                    >
                                        CONNECT
                                    </Button>
                                )}
                            </CardHeader>
                        </Card>

                        <Card className="bg-black border border-white/10 hover:border-[#0077b5]/50 transition group overflow-hidden relative">
                            <div className="absolute inset-0 bg-[#0077b5]/5 opacity-0 group-hover:opacity-100 transition duration-500"></div>
                            <CardHeader className="relative z-10 flex flex-row items-center justify-between pb-2">
                                <div className="space-y-1">
                                    <div className="flex items-center gap-2">
                                        <div className="p-2 bg-[#0077b5]/20 rounded-lg">
                                            <Briefcase className="w-5 h-5 text-[#0077b5]" />
                                        </div>
                                        <CardTitle className="text-lg font-black italic uppercase">LinkedIn</CardTitle>
                                    </div>
                                    <CardDescription className="text-xs font-mono">Professional Network Growth</CardDescription>
                                </div>
                                {integrations.find(i => i.provider === 'linkedin') ? (
                                    <Badge className="bg-green-500/20 text-green-400 border-green-500/30">CONNECTED</Badge>
                                ) : (
                                    <Button
                                        size="sm"
                                        variant="outline"
                                        className="border-[#0077b5]/30 text-[#0077b5] hover:bg-[#0077b5]/10"
                                        onClick={() => connectSocialOAuth('linkedin')}
                                    >
                                        CONNECT
                                    </Button>
                                )}
                            </CardHeader>
                        </Card>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                        {/* Categories Sidebar */}
                        <div className="md:col-span-1 space-y-2">
                            <h3 className="text-[10px] font-bold text-gray-500 font-mono tracking-widest mb-4 uppercase flex items-center gap-2">
                                <LayoutGrid className="w-3 h-3" /> Core Categories
                            </h3>
                            {INTEGRATION_CATEGORIES.map(cat => (
                                <button key={cat.name} className="w-full flex items-center justify-between px-4 py-3 rounded-lg bg-white/5 border border-white/5 hover:border-[#00f0ff]/20 hover:bg-white/10 transition text-left group">
                                    <span className="flex items-center gap-3 text-xs font-mono uppercase tracking-wide text-gray-400 group-hover:text-white">
                                        {cat.icon} {cat.name}
                                    </span>
                                    <ArrowRight className="w-3 h-3 text-gray-700 opacity-0 group-hover:opacity-100 transition" />
                                </button>
                            ))}

                            <div className="pt-8 space-y-4">
                                <div className="p-4 rounded-xl bg-gradient-to-br from-[#a855f7]/20 to-[#3b82f6]/20 border border-white/10">
                                    <div className="flex items-center gap-2 text-[#00f0ff] mb-2 font-black italic uppercase text-xs">
                                        <Sparkles className="w-4 h-4" /> Global Beta
                                    </div>
                                    <p className="text-[10px] text-gray-400 font-mono leading-relaxed">Join the first 100 creators building the future of autonomous startup tools.</p>
                                    <Button variant="ghost" className="w-full mt-3 text-[10px] text-[#00f0ff] hover:bg-[#00f0ff]/10 h-8" onClick={() => (document.querySelector('[value="developer"]') as HTMLButtonElement)?.click()}>
                                        LEARN MORE
                                    </Button>
                                </div>
                            </div>
                        </div>

                        {/* Marketplace Grid */}
                        <div className="md:col-span-3 space-y-8">
                            {/* Featured Banner */}
                            <div className="relative h-48 rounded-2xl bg-gradient-to-r from-[#00f0ff]/10 via-[#a855f7]/10 to-transparent border border-white/10 overflow-hidden group p-8 flex items-center">
                                <div className="absolute inset-0 bg-cyber-grid opacity-10 pointer-events-none"></div>
                                <div className="absolute -right-20 -bottom-20 w-64 h-64 bg-[#00f0ff]/10 blur-[100px] rounded-full group-hover:bg-[#a855f7]/10 transition-colors duration-1000"></div>

                                <div className="relative z-10 space-y-4">
                                    <Badge className="bg-[#00f0ff] text-black font-bold text-[10px] tracking-widest px-3">FEATURED PROTOCOL</Badge>
                                    <h2 className="text-3xl font-black text-white italic tracking-tighter uppercase leading-none">Custom MCP // Connector</h2>
                                    <p className="text-xs text-gray-400 max-w-md font-mono">Connect any community-built Model Context Protocol server instantly. No code required.</p>
                                    <Button variant="cyber" size="sm" onClick={() => connectIntegration('mcp')}>
                                        LINK SERVER NOW <ArrowRight className="w-4 h-4 ml-2" />
                                    </Button>
                                </div>
                            </div>

                            {/* Tool Grid */}
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                {marketplaceTools.map(tool => (
                                    <Card key={tool.id} className="bg-black border-white/10 hover:border-purple-500/30 transition group relative overflow-hidden">
                                        <CardHeader className="pb-2">
                                            <div className="flex justify-between items-start mb-4">
                                                <div className="p-3 bg-white/5 rounded-xl border border-white/10 group-hover:border-purple-500/20 group-hover:bg-purple-500/10 transition text-2xl">
                                                    {tool.icon}
                                                </div>
                                                <Badge variant="secondary" className="bg-black border-white/5 text-[9px] font-mono">{tool.version}</Badge>
                                            </div>
                                            <CardTitle className="text-sm font-bold uppercase tracking-tight">{tool.name}</CardTitle>
                                            <CardDescription className="text-[10px] font-mono text-gray-500 h-10 overflow-hidden line-clamp-2">{tool.description}</CardDescription>
                                        </CardHeader>
                                        <CardContent className="pt-0">
                                            <div className="flex items-center gap-2 mb-4">
                                                <Download className="w-3 h-3 text-gray-600" />
                                                <span className="text-[10px] font-mono text-gray-600 uppercase tracking-widest">{tool.total_installs} Activations</span>
                                            </div>
                                            <Button
                                                className="w-full h-8 text-[10px] font-mono bg-white/5 hover:bg-white/10 border-white/10 text-white"
                                                variant="outline"
                                                disabled={connecting === tool.id}
                                                onClick={() => installMarketplaceTool(tool)}
                                            >
                                                {connecting === tool.id ? 'INSTALLING...' : '1-CLICK INSTALL'}
                                            </Button>
                                        </CardContent>
                                    </Card>
                                ))}
                            </div>
                        </div>
                    </div>
                </TabsContent>

                {/* TAB: DEVELOPER BETA */}
                <TabsContent value="developer">
                    <div className="max-w-3xl mx-auto space-y-12 py-10">
                        <section className="text-center space-y-6">
                            <h2 className="text-5xl font-black text-white italic tracking-tighter uppercase leading-none">The Future is // Extensible</h2>
                            <p className="text-lg text-gray-400 font-mono italic max-w-xl mx-auto">Build tools that empower 1,000+ startups globally using the Model Context Protocol (MCP).</p>
                        </section>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                            <div className="p-8 rounded-2xl bg-white/5 border border-white/10 space-y-4">
                                <div className="p-3 bg-[#00f0ff]/10 border border-[#00f0ff]/20 rounded-xl w-fit">
                                    <Globe className="w-6 h-6 text-[#00f0ff]" />
                                </div>
                                <h3 className="text-xl font-bold text-white uppercase tracking-tight">Global Reach</h3>
                                <p className="text-xs text-gray-500 font-mono leading-relaxed italic">Your tools available to startups from Lima to Tokyo with one click. No complex OAuth setups for every user.</p>
                            </div>

                            <div className="p-8 rounded-2xl bg-white/5 border border-white/10 space-y-4">
                                <div className="p-3 bg-[#a855f7]/10 border border-[#a855f7]/20 rounded-xl w-fit">
                                    <Code className="w-6 h-6 text-[#a855f7]" />
                                </div>
                                <h3 className="text-xl font-bold text-white uppercase tracking-tight">Open Protocol</h3>
                                <p className="text-xs text-gray-500 font-mono leading-relaxed italic">Standardized communication via MCP means your tool works instantly with MomentAIc Agents.</p>
                            </div>
                        </div>

                        <div className="bg-gradient-to-br from-[#00f0ff]/10 via-[#a855f7]/10 to-[#0a0a0a] border border-white/10 p-12 rounded-3xl text-center space-y-8 relative overflow-hidden">
                            <div className="absolute inset-0 bg-cyber-grid opacity-10 pointer-events-none"></div>

                            <div className="relative z-10">
                                <h2 className="text-3xl font-black text-white italic tracking-tighter uppercase mb-4">Launch Your Protocol</h2>
                                <p className="text-sm text-gray-400 font-mono mb-8 max-w-md mx-auto italic">Submit your MCP server and join the first wave of authorized marketplace developers.</p>
                                <Button className="px-8 py-6 h-auto text-sm font-black italic bg-gradient-to-r from-[#00f0ff] to-[#a855f7] text-white hover:scale-105 transition-all shadow-[0_0_30px_rgba(0,240,255,0.3)]" onClick={() => setIsSubmitModalOpen(true)}>
                                    SUBMIT TO MARKETPLACE <Plus className="w-5 h-5 ml-2" />
                                </Button>
                            </div>
                        </div>
                    </div>
                </TabsContent>
            </Tabs>

            {/* Submission Modal */}
            <Dialog
                isOpen={isSubmitModalOpen}
                onClose={() => setIsSubmitModalOpen(false)}
                title="Protocol // Submission"
                description="Provide details for your MCP server. High-quality tools get featured in the marketplace."
                footer={
                    <>
                        <Button variant="ghost" onClick={() => setIsSubmitModalOpen(false)} className="text-gray-500 hover:text-white font-mono text-xs">CANCEL</Button>
                        <Button variant="cyber" className="h-10 text-xs px-6" onClick={submitTool}>
                            LAUNCH PROTOCOL <ArrowRight className="w-3 h-3 ml-2" />
                        </Button>
                    </>
                }
            >
                <div className="space-y-6 font-mono">
                    <div className="space-y-2">
                        <label className="text-[10px] font-bold text-gray-500 tracking-widest uppercase">Tool Name</label>
                        <Input
                            placeholder="e.g. SLACK_BRIDGE_X"
                            className="bg-black border-white/10 text-xs"
                            value={submitForm.name}
                            onChange={e => setSubmitForm({ ...submitForm, name: e.target.value })}
                        />
                    </div>
                    <div className="space-y-2">
                        <label className="text-[10px] font-bold text-gray-500 tracking-widest uppercase">MCP Server URL</label>
                        <Input
                            placeholder="https://your-mcp-server.com/mcp"
                            className="bg-black border-white/10 text-xs text-[#00f0ff]"
                            value={submitForm.mcp_url}
                            onChange={e => setSubmitForm({ ...submitForm, mcp_url: e.target.value })}
                        />
                    </div>
                    <div className="space-y-2">
                        <label className="text-[10px] font-bold text-gray-500 tracking-widest uppercase">Description</label>
                        <Input
                            placeholder="Briefly explain what this does..."
                            className="bg-black border-white/10 text-xs h-20"
                            value={submitForm.description}
                            onChange={e => setSubmitForm({ ...submitForm, description: e.target.value })}
                        />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <label className="text-[10px] font-bold text-gray-500 tracking-widest uppercase">Category</label>
                            <select
                                className="w-full bg-black border border-white/10 rounded-lg px-3 py-2 text-xs text-white"
                                value={submitForm.category}
                                onChange={e => setSubmitForm({ ...submitForm, category: e.target.value })}
                            >
                                <option value="productivity">PRODUCTIVITY</option>
                                <option value="marketing">MARKETING</option>
                                <option value="devops">DEVOPS</option>
                                <option value="comms">COMMS</option>
                            </select>
                        </div>
                        <div className="space-y-2 text-center border border-white/5 bg-white/5 rounded-lg flex flex-col justify-center">
                            <label className="text-[10px] font-bold text-gray-400 font-mono tracking-widest uppercase">Requirements</label>
                            <div className="flex items-center justify-center gap-2 text-[10px] font-mono text-green-400 uppercase">
                                <CheckCircle2 className="w-3 h-3" /> MCP SPEC V1
                            </div>
                        </div>
                    </div>
                </div>
            </Dialog>

            {/* Entrepreneur CTA */}
            <div className="mt-12 p-8 bg-gradient-to-r from-purple-900/40 via-blue-900/40 to-cyan-900/40 border border-purple-500/30 rounded-2xl text-center relative overflow-hidden">
                <div className="absolute inset-0 bg-cyber-grid opacity-10 pointer-events-none"></div>
                <h3 className="text-2xl font-bold text-white mb-3 tracking-tighter uppercase italic">From Your Sofa to Fortune 500</h3>
                <p className="text-gray-300 mb-6 max-w-2xl mx-auto font-mono text-xs italic tracking-wide">
                    Whether you're in Manila, Lima, Lagos, or anywhere in the world — these protocols give you the same
                    superpowers as billion-dollar companies. Connect, automate, and scale.
                </p>
                <div className="flex flex-wrap justify-center gap-3 text-[10px] font-mono uppercase tracking-widest">
                    <span className="px-4 py-2 bg-green-500/10 text-green-400 border border-green-500/20 rounded-full">💰 Revenue Tracking</span>
                    <span className="px-4 py-2 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded-full">📊 Real-Time Analytics</span>
                    <span className="px-4 py-2 bg-purple-500/10 text-purple-400 border border-purple-500/20 rounded-full">🤖 AI Insights</span>
                </div>
            </div>
        </div>
    );
}
