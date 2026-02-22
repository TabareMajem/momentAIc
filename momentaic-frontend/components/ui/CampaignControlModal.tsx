import React, { useState } from 'react';
import { Button } from './Button';
import { Card } from './Card';
import { Badge } from './Badge';
import { Input } from './Input';
import { Textarea } from './Textarea';
import { useToast } from './Toast';
import { cn } from '../../lib/utils';
import {
    Activity, Crosshair, Globe, Instagram, Play, RefreshCw, Send,
    Settings, Shield, Sparkles, Terminal, Twitter, Video, X
} from 'lucide-react';
import { api } from '../../lib/api';

interface CampaignControlModalProps {
    isOpen: boolean;
    onClose: () => void;
}

const DOMAINS = [
    'symbiotask.com',
    'ai.yokaizencampus.com',
    'yokaizencampus.com',
    'agentforgeai.com',
    'bondquests.com',
    'momentaic.com',
    'yokaizen.com',
    'otaku.yokaizen.com'
];

export function CampaignControlModal({ isOpen, onClose }: CampaignControlModalProps) {
    const [activeTab, setActiveTab] = useState<'overview' | 'accounts' | 'content' | 'actions'>('overview');
    const [selectedDomain, setSelectedDomain] = useState<string>(DOMAINS[0]);
    const [isGenerating, setIsGenerating] = useState(false);
    const { toast } = useToast();

    if (!isOpen) return null;

    const handleGenerateContent = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsGenerating(true);
        // Simulate generation delay
        await new Promise(r => setTimeout(r, 2000));
        toast({ type: 'success', title: 'Content Generated', message: 'Viral content matrix compiled successfully.' });
        setIsGenerating(false);
    };

    const handleTriggerAction = async (action: string) => {
        toast({ type: 'success', title: 'Action Triggered', message: `Dispatched [${action}] to ai.yokaizen.com matrix.` });
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
            <div className="absolute inset-0 z-0 pointer-events-none">
                <img
                    src="/momentai_campaign_matrix.png"
                    alt="Campaign Matrix Background"
                    className="w-full h-full object-cover opacity-10 mix-blend-screen"
                />
            </div>
            <div className="absolute inset-0 bg-tech-grid opacity-10 pointer-events-none z-0" />

            <div className="relative z-10 w-full max-w-6xl max-h-[90vh] bg-[#050508]/90 backdrop-blur-md border border-purple-500/30 rounded-xl shadow-[0_0_50px_rgba(168,85,247,0.15)] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-300">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-white/5 bg-[#0a0a0f]">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-purple-500/10 rounded-lg flex items-center justify-center border border-purple-500/20">
                            <Shield className="w-6 h-6 text-purple-400" />
                        </div>
                        <div>
                            <div className="flex items-center gap-2">
                                <h2 className="text-2xl font-black text-white tracking-tight">Campaign Matrix</h2>
                                <Badge variant="cyber" className="text-[10px] animate-pulse">GOD_MODE</Badge>
                            </div>
                            <p className="text-xs font-mono text-gray-500 mt-1">Super Admin Control Panel • Master Access Granted</p>
                        </div>
                    </div>
                    <button onClick={onClose} className="p-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                {/* Main Content Area */}
                <div className="flex flex-1 overflow-hidden">
                    {/* Sidebar Navigation */}
                    <div className="w-64 border-r border-white/5 bg-[#08080c] p-4 flex flex-col gap-2">
                        <div className="px-3 mb-2 text-xs font-mono text-gray-500 uppercase tracking-widest">Modules</div>
                        {[
                            { id: 'overview', label: 'Command Center', icon: Activity },
                            { id: 'accounts', label: 'Social Nodes', icon: Globe },
                            { id: 'content', label: 'Content Forge', icon: Sparkles },
                            { id: 'actions', label: 'Triggers & Webhooks', icon: Terminal },
                        ].map(tab => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id as any)}
                                className={cn(
                                    "flex items-center gap-3 px-3 py-3 rounded-lg text-sm font-mono transition-all duration-200",
                                    activeTab === tab.id
                                        ? "bg-purple-500/10 text-purple-400 border border-purple-500/20 glow glow-purple"
                                        : "text-gray-400 hover:text-white hover:bg-white/5 border border-transparent"
                                )}
                            >
                                <tab.icon className="w-4 h-4" />
                                {tab.label}
                            </button>
                        ))}

                        <div className="mt-auto pt-4 border-t border-white/5">
                            <label className="block px-3 mb-2 text-xs font-mono text-gray-500 uppercase tracking-widest">Active Target</label>
                            <select
                                value={selectedDomain}
                                onChange={(e) => setSelectedDomain(e.target.value)}
                                className="w-full bg-black border border-white/10 rounded text-sm text-purple-400 p-2 outline-none focus:border-purple-500/50"
                            >
                                {DOMAINS.map(d => <option key={d} value={d}>{d}</option>)}
                            </select>
                        </div>
                    </div>

                    {/* Tab Content */}
                    <div className="flex-1 overflow-y-auto p-6 bg-[#050508] relative">
                        {/* Domain Watermark */}
                        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-[120px] font-black text-white/[0.02] pointer-events-none whitespace-nowrap rotate-[-15deg]">
                            {selectedDomain}
                        </div>

                        {activeTab === 'overview' && (
                            <div className="space-y-6 relative z-10">
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    <div className="p-4 bg-black/40 border border-white/10 rounded-xl">
                                        <div className="text-xs text-gray-500 font-mono mb-1">Active Campaigns</div>
                                        <div className="text-3xl font-black text-white">24</div>
                                        <div className="text-xs text-green-500 mt-2">+12% vs last week</div>
                                    </div>
                                    <div className="p-4 bg-black/40 border border-white/10 rounded-xl">
                                        <div className="text-xs text-gray-500 font-mono mb-1">Total Reach</div>
                                        <div className="text-3xl font-black text-white">1.2M</div>
                                        <div className="text-xs text-green-500 mt-2">+45% vs last week</div>
                                    </div>
                                    <div className="p-4 bg-black/40 border border-purple-500/30 rounded-xl shadow-[0_0_20px_rgba(168,85,247,0.1)] relative overflow-hidden">
                                        <div className="absolute top-0 right-0 w-16 h-16 bg-gradient-to-br from-purple-500/20 to-transparent blur-xl" />
                                        <div className="text-xs text-purple-400 font-mono mb-1">Agents Deployed</div>
                                        <div className="text-3xl font-black text-white">142</div>
                                        <div className="text-xs text-[#00f0ff] mt-2 flex items-center gap-1"><Activity className="w-3 h-3" /> Swarm operational</div>
                                    </div>
                                </div>

                                <Card className="p-6 bg-black/40 border-white/10">
                                    <h3 className="text-lg font-bold text-white mb-4">Live Activity Stream</h3>
                                    <div className="space-y-3">
                                        {[
                                            "[TikTok] Viral clip #4 posted for symbiotask.com. Views: 12k",
                                            "[Twitter] Engagement agent replied to 45 relevant threads.",
                                            "[SEO] Article generated for bondquests.com deployed.",
                                        ].map((log, i) => (
                                            <div key={i} className="flex gap-3 text-sm font-mono border-l-2 border-purple-500/50 pl-3">
                                                <span className="text-gray-500">2 mins ago</span>
                                                <span className="text-gray-300">{log}</span>
                                            </div>
                                        ))}
                                    </div>
                                </Card>
                            </div>
                        )}

                        {activeTab === 'accounts' && (
                            <div className="space-y-6 relative z-10">
                                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                                    <Globe className="w-5 h-5 text-blue-400" /> Platform Connections
                                </h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <Card className="p-6 bg-black/40 border-white/10 hover:border-pink-500/30 transition-colors">
                                        <div className="flex justify-between items-start mb-4">
                                            <div className="flex gap-3 items-center">
                                                <div className="p-2 bg-pink-500/10 rounded-lg"><Instagram className="w-6 h-6 text-pink-500" /></div>
                                                <div>
                                                    <div className="font-bold text-white">Instagram Matrix</div>
                                                    <div className="text-xs text-gray-500 font-mono">12 Accounts Connected</div>
                                                </div>
                                            </div>
                                            <Badge variant="success">Active</Badge>
                                        </div>
                                        <Button variant="outline" className="w-full text-xs" onClick={() => toast({ type: 'info', title: 'Redirecting', message: 'Opening OAuth flow...' })}>Sync New Account</Button>
                                    </Card>

                                    <Card className="p-6 bg-black/40 border-white/10 hover:border-gray-300/30 transition-colors">
                                        <div className="flex justify-between items-start mb-4">
                                            <div className="flex gap-3 items-center">
                                                <div className="p-2 bg-gray-800 rounded-lg"><Video className="w-6 h-6 text-white" /></div>
                                                <div>
                                                    <div className="font-bold text-white">TikTok Farm</div>
                                                    <div className="text-xs text-gray-500 font-mono">8 Accounts Connected</div>
                                                </div>
                                            </div>
                                            <Badge variant="success">Active</Badge>
                                        </div>
                                        <Button variant="outline" className="w-full text-xs" onClick={() => toast({ type: 'info', title: 'Redirecting', message: 'Opening OAuth flow...' })}>Sync New Account</Button>
                                    </Card>

                                    <Card className="p-6 bg-black/40 border-white/10 hover:border-blue-400/30 transition-colors">
                                        <div className="flex justify-between items-start mb-4">
                                            <div className="flex gap-3 items-center">
                                                <div className="p-2 bg-blue-400/10 rounded-lg"><Twitter className="w-6 h-6 text-blue-400" /></div>
                                                <div>
                                                    <div className="font-bold text-white">Twitter Swarm</div>
                                                    <div className="text-xs text-gray-500 font-mono">25 Accounts Connected</div>
                                                </div>
                                            </div>
                                            <Badge variant="success">Active</Badge>
                                        </div>
                                        <Button variant="outline" className="w-full text-xs" onClick={() => toast({ type: 'info', title: 'Redirecting', message: 'Opening OAuth flow...' })}>Sync New Account</Button>
                                    </Card>
                                </div>
                            </div>
                        )}

                        {activeTab === 'content' && (
                            <div className="space-y-6 relative z-10">
                                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                                    <Sparkles className="w-5 h-5 text-yellow-400" /> Infinite Content Generator
                                </h3>
                                <form onSubmit={handleGenerateContent} className="space-y-4">
                                    <div className="grid grid-cols-2 gap-4">
                                        <Input label="Campaign Topic / Keyword" placeholder="e.g. AI Agents, Automation" required />
                                        <div className="space-y-1.5">
                                            <label className="text-xs font-bold uppercase tracking-widest text-gray-500 ml-1">Content Type</label>
                                            <select className="flex h-12 w-full rounded-lg border border-white/10 bg-[#0a0a0a] px-4 py-2 text-sm text-white font-mono">
                                                <option>Short-form Video Scripts (TikTok/Reels)</option>
                                                <option>Viral Twitter Threads</option>
                                                <option>SEO Blog Posts</option>
                                                <option>Automated Image Carousels</option>
                                            </select>
                                        </div>
                                    </div>
                                    <Textarea label="Brand Tone & Instructions" placeholder="Use aggressive hook, emphasize saving time, target agency owners..." className="h-32" />
                                    <div className="flex justify-between items-center bg-purple-500/5 p-4 rounded-lg border border-purple-500/20">
                                        <div className="text-sm font-mono text-purple-300">Target Project: <span className="font-bold text-white">{selectedDomain}</span></div>
                                        <Button type="submit" variant="cyber" isLoading={isGenerating}>Build Assets</Button>
                                    </div>
                                </form>
                            </div>
                        )}

                        {activeTab === 'actions' && (
                            <div className="space-y-6 relative z-10">
                                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                                    <Terminal className="w-5 h-5 text-green-400" /> Action Triggers
                                </h3>
                                <p className="text-gray-400 text-sm mb-6">Dispatch commands directly to interconnected AI systems.</p>

                                <div className="space-y-3">
                                    {[
                                        { label: "Trigger ai.yokaizen.com Aggregator", cmd: "SYNC_YOKAIZEN_NETWORK", color: "blue" },
                                        { label: "Deploy Comment Sentinels", cmd: "EXECUTE_SENTINEL_SWARM", color: "purple" },
                                        { label: "Force Sync Cross-Platform Profiles", cmd: "RECALIBRATE_IDENTITIES", color: "orange" },
                                        { label: "Launch Blast Email Campaign", cmd: "INIT_ASTROTURF_MAILING", color: "red" },
                                    ].map((action, i) => (
                                        <div key={i} className="flex items-center justify-between p-4 bg-black/40 border border-white/5 rounded-lg hover:bg-white/[0.02] transition-colors">
                                            <div>
                                                <div className="text-white font-bold">{action.label}</div>
                                                <div className={`text-xs font-mono text-${action.color}-400 mt-1`}>&gt; {action.cmd}</div>
                                            </div>
                                            <Button variant="outline" size="sm" onClick={() => handleTriggerAction(action.cmd)}>
                                                <Play className="w-4 h-4 mr-2" /> Execute
                                            </Button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
