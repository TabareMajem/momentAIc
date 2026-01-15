import { useState, useEffect } from 'react';
import {
    Target, Users, Mail, Globe, TrendingUp, Zap,
    Play, Loader, CheckCircle, AlertCircle, Rocket,
    Search, FileText, MessageSquare, BarChart3
} from 'lucide-react';

interface BlitzPhase {
    name: string;
    status: 'pending' | 'running' | 'complete' | 'error';
    modules?: number;
    platforms?: string[];
    communities?: number;
    tactics?: number;
    data?: any;
}

interface BlitzResult {
    started_at: string;
    completed_at?: string;
    target_users: number;
    phases: BlitzPhase[];
}

export default function WarRoomDashboard() {
    const [isExecuting, setIsExecuting] = useState(false);
    const [blitzResult, setBlitzResult] = useState<BlitzResult | null>(null);
    const [activeTab, setActiveTab] = useState<'blitz' | 'kols' | 'content' | 'communities'>('blitz');
    const [kolData, setKolData] = useState<string>('');
    const [contentIdeas, setContentIdeas] = useState<string>('');

    const executeBlitz = async () => {
        setIsExecuting(true);
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch('/api/v1/growth-hack/blitz', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ target_users: 100000 })
            });

            if (response.ok) {
                const data = await response.json();
                setBlitzResult(data);

                // Extract KOL and content data
                const researchPhase = data.phases?.find((p: BlitzPhase) => p.name === 'Google-Powered Research');
                if (researchPhase?.data?.research_modules) {
                    const kolModule = researchPhase.data.research_modules.find((m: any) => m.name === 'KOLs');
                    const contentModule = researchPhase.data.research_modules.find((m: any) => m.name === 'Content');
                    if (kolModule?.data?.kol_recommendations) setKolData(kolModule.data.kol_recommendations);
                    if (contentModule?.data?.content_ideas) setContentIdeas(contentModule.data.content_ideas);
                }
            }
        } catch (error) {
            console.error('Blitz execution failed:', error);
        } finally {
            setIsExecuting(false);
        }
    };

    const StatusIcon = ({ status }: { status: string }) => {
        switch (status) {
            case 'complete': return <CheckCircle className="w-5 h-5 text-green-400" />;
            case 'running': return <Loader className="w-5 h-5 text-blue-400 animate-spin" />;
            case 'error': return <AlertCircle className="w-5 h-5 text-red-400" />;
            default: return <div className="w-5 h-5 rounded-full border-2 border-white/20" />;
        }
    };

    return (
        <div className="min-h-screen bg-[#050505] text-white">
            {/* Header */}
            <div className="border-b border-white/10 bg-gradient-to-r from-purple-900/20 to-blue-900/20">
                <div className="max-w-7xl mx-auto px-6 py-8">
                    <div className="flex items-center gap-4">
                        <div className="p-3 rounded-xl bg-gradient-to-br from-red-500 to-orange-500">
                            <Target className="w-8 h-8" />
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold">War Room</h1>
                            <p className="text-white/60">Global Domination Command Center</p>
                        </div>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-6 py-8">
                {/* Tabs */}
                <div className="flex gap-2 mb-8">
                    {[
                        { id: 'blitz', label: 'Launch Blitz', icon: Rocket },
                        { id: 'kols', label: 'KOL Hit List', icon: Users },
                        { id: 'content', label: 'Content Ideas', icon: FileText },
                        { id: 'communities', label: 'Communities', icon: MessageSquare }
                    ].map(tab => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id as any)}
                            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${activeTab === tab.id
                                    ? 'bg-white text-black font-medium'
                                    : 'bg-white/5 text-white/60 hover:bg-white/10'
                                }`}
                        >
                            <tab.icon className="w-4 h-4" />
                            {tab.label}
                        </button>
                    ))}
                </div>

                {/* Launch Blitz Tab */}
                {activeTab === 'blitz' && (
                    <div className="space-y-8">
                        {/* Big Launch Button */}
                        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-red-600/20 to-orange-600/20 border border-red-500/30 p-8">
                            <div className="absolute inset-0 bg-[url('data:image/svg+xml,...')] opacity-5" />
                            <div className="relative z-10 text-center">
                                <h2 className="text-2xl font-bold mb-2">🎯 100,000 User Launch Blitz</h2>
                                <p className="text-white/60 mb-6 max-w-xl mx-auto">
                                    Execute full growth sequence: KOL discovery, content syndication, community mapping, reverse outreach tactics
                                </p>

                                <button
                                    onClick={executeBlitz}
                                    disabled={isExecuting}
                                    className={`px-12 py-4 rounded-xl font-bold text-lg transition-all ${isExecuting
                                            ? 'bg-white/20 cursor-not-allowed'
                                            : 'bg-gradient-to-r from-red-500 to-orange-500 hover:from-red-400 hover:to-orange-400 shadow-lg shadow-red-500/30'
                                        }`}
                                >
                                    {isExecuting ? (
                                        <span className="flex items-center gap-2">
                                            <Loader className="w-5 h-5 animate-spin" />
                                            Executing Blitz...
                                        </span>
                                    ) : (
                                        <span className="flex items-center gap-2">
                                            <Zap className="w-5 h-5" />
                                            EXECUTE LAUNCH BLITZ
                                        </span>
                                    )}
                                </button>
                            </div>
                        </div>

                        {/* Results */}
                        {blitzResult && (
                            <div className="space-y-4">
                                <h3 className="text-xl font-bold flex items-center gap-2">
                                    <CheckCircle className="w-6 h-6 text-green-400" />
                                    Blitz Complete
                                </h3>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {blitzResult.phases.map((phase, i) => (
                                        <div key={i} className="p-4 rounded-xl bg-white/5 border border-white/10">
                                            <div className="flex items-center gap-3 mb-2">
                                                <StatusIcon status={phase.status} />
                                                <span className="font-medium">{phase.name}</span>
                                            </div>
                                            <div className="text-sm text-white/60">
                                                {phase.modules && <div>• {phase.modules} research modules</div>}
                                                {phase.platforms && <div>• {phase.platforms.length} platforms ready</div>}
                                                {phase.communities && <div>• {phase.communities} communities mapped</div>}
                                                {phase.tactics && <div>• {phase.tactics} tactics available</div>}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Quick Stats */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            {[
                                { label: 'Target Users', value: '100,000', icon: Target, color: 'text-red-400' },
                                { label: 'Platforms', value: '6', icon: Globe, color: 'text-blue-400' },
                                { label: 'Communities', value: '11+', icon: Users, color: 'text-green-400' },
                                { label: 'AI Research', value: 'Gemini', icon: TrendingUp, color: 'text-purple-400' }
                            ].map((stat, i) => (
                                <div key={i} className="p-4 rounded-xl bg-white/5 border border-white/10">
                                    <stat.icon className={`w-6 h-6 ${stat.color} mb-2`} />
                                    <div className="text-2xl font-bold">{stat.value}</div>
                                    <div className="text-sm text-white/60">{stat.label}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* KOL Hit List Tab */}
                {activeTab === 'kols' && (
                    <div className="space-y-6">
                        <div className="flex items-center justify-between">
                            <h2 className="text-xl font-bold">KOL Discovery (Powered by Gemini)</h2>
                            <button
                                onClick={async () => {
                                    const token = localStorage.getItem('access_token');
                                    const res = await fetch('/api/v1/growth-hack/kol/generate-hitlist', {
                                        method: 'POST',
                                        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
                                        body: JSON.stringify({ regions: ['US', 'LatAm', 'Europe', 'Asia'] })
                                    });
                                    if (res.ok) {
                                        const data = await res.json();
                                        setKolData(JSON.stringify(data, null, 2));
                                    }
                                }}
                                className="px-4 py-2 bg-blue-500 rounded-lg hover:bg-blue-400 flex items-center gap-2"
                            >
                                <Search className="w-4 h-4" /> Discover KOLs
                            </button>
                        </div>

                        <div className="p-6 rounded-xl bg-white/5 border border-white/10">
                            <pre className="text-sm text-white/80 whitespace-pre-wrap overflow-auto max-h-[600px]">
                                {kolData || 'Click "Discover KOLs" to generate recommendations via Gemini AI'}
                            </pre>
                        </div>
                    </div>
                )}

                {/* Content Ideas Tab */}
                {activeTab === 'content' && (
                    <div className="space-y-6">
                        <div className="flex items-center justify-between">
                            <h2 className="text-xl font-bold">Viral Content Ideas</h2>
                            <button
                                onClick={async () => {
                                    const token = localStorage.getItem('access_token');
                                    const res = await fetch('/api/v1/growth-hack/syndicate', {
                                        method: 'POST',
                                        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
                                        body: JSON.stringify({
                                            title: 'AI Operating System for Founders',
                                            body: 'Full startup team powered by AI'
                                        })
                                    });
                                    if (res.ok) {
                                        const data = await res.json();
                                        setContentIdeas(JSON.stringify(data, null, 2));
                                    }
                                }}
                                className="px-4 py-2 bg-purple-500 rounded-lg hover:bg-purple-400 flex items-center gap-2"
                            >
                                <FileText className="w-4 h-4" /> Generate Content
                            </button>
                        </div>

                        <div className="p-6 rounded-xl bg-white/5 border border-white/10">
                            <pre className="text-sm text-white/80 whitespace-pre-wrap overflow-auto max-h-[600px]">
                                {contentIdeas || 'Click "Generate Content" to create platform-specific content plans'}
                            </pre>
                        </div>
                    </div>
                )}

                {/* Communities Tab */}
                {activeTab === 'communities' && (
                    <div className="space-y-6">
                        <h2 className="text-xl font-bold">Target Communities</h2>

                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {[
                                { name: 'Indie Hackers', platform: 'Discord', members: '15k', access: 'Open' },
                                { name: 'SaaS Growth', platform: 'Discord', members: '8k', access: 'Invite' },
                                { name: 'No-Code Founders', platform: 'Discord', members: '12k', access: 'Open' },
                                { name: 'Online Geniuses', platform: 'Slack', members: '35k', access: 'Paid $199' },
                                { name: 'Demand Curve', platform: 'Slack', members: '20k', access: 'Free' },
                                { name: 'Product Hunt Makers', platform: 'Slack', members: '18k', access: 'Apply' },
                                { name: 'SaaS Growth Hacks', platform: 'Facebook', members: '45k', access: 'Open' },
                                { name: 'Startup Founders Network', platform: 'Facebook', members: '120k', access: 'Open' },
                                { name: 'r/startups', platform: 'Reddit', members: '1.2M', access: 'Open' },
                                { name: 'r/SaaS', platform: 'Reddit', members: '85k', access: 'Open' },
                                { name: 'r/Entrepreneur', platform: 'Reddit', members: '2M', access: 'Open' }
                            ].map((community, i) => (
                                <div key={i} className="p-4 rounded-xl bg-white/5 border border-white/10 hover:border-white/20 transition-all">
                                    <div className="font-medium mb-1">{community.name}</div>
                                    <div className="text-sm text-white/60 flex justify-between">
                                        <span>{community.platform}</span>
                                        <span>{community.members} members</span>
                                    </div>
                                    <div className={`text-xs mt-2 px-2 py-1 rounded inline-block ${community.access === 'Open' ? 'bg-green-500/20 text-green-400' :
                                            community.access.includes('Paid') ? 'bg-red-500/20 text-red-400' :
                                                'bg-yellow-500/20 text-yellow-400'
                                        }`}>
                                        {community.access}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
