import React, { useState } from 'react';
import { api } from '../lib/api';
import { Button } from '../components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card';
import { useToast } from '../components/ui/Toast';
import {
    Zap, Github, Twitter, TrendingUp, Search,
    MessageSquare, Copy, ExternalLink, RefreshCw, XCircle
} from 'lucide-react';
import { cn } from '../lib/utils';
import { Badge } from '../components/ui/Badge';

// --- TYPES ---
type Opportunity = {
    platform: 'reddit' | 'twitter' | 'linkedin';
    type: 'comment' | 'reply' | 'trend_jack' | 'other';
    title?: string;
    url?: string;
    topic?: string;
    insight: string;
    draft: string;
    timestamp: string;
};

// --- COMPONENTS ---
const OppCard = ({ item }: { item: Opportunity }) => {
    const { toast } = useToast();

    const handleCopy = () => {
        navigator.clipboard.writeText(item.draft);
        toast({ type: 'success', title: 'Copied', message: 'Draft copied to clipboard.' });
    };

    return (
        <Card className="bg-[#0a0a0a] border border-white/10 hover:border-purple-500/30 transition-all group">
            <CardHeader className="pb-2">
                <div className="flex justify-between items-start">
                    <div className="flex items-center gap-2">
                        {item.platform === 'reddit' ? <span className="p-1 px-2 rounded bg-orange-500/10 text-orange-500 font-bold text-xs">REDDIT</span> :
                            item.platform === 'twitter' ? <Twitter className="w-4 h-4 text-cyan-400" /> :
                                <TrendingUp className="w-4 h-4 text-green-400" />}
                        <span className="text-xs text-gray-500 font-mono">{new Date(item.timestamp).toLocaleTimeString()}</span>
                    </div>
                    {item.url && (
                        <a href={item.url} target="_blank" rel="noopener noreferrer" className="text-gray-500 hover:text-white transition-colors">
                            <ExternalLink className="w-4 h-4" />
                        </a>
                    )}
                </div>
                {item.title && <CardTitle className="text-sm font-bold text-white line-clamp-1">{item.title}</CardTitle>}
                {item.topic && <CardTitle className="text-sm font-bold text-white uppercase tracking-wide">TREND: {item.topic}</CardTitle>}
                <CardDescription className="text-xs text-gray-400 font-mono border-l-2 border-white/20 pl-2">
                    {item.insight}
                </CardDescription>
            </CardHeader>
            <CardContent>
                <div className="bg-[#050505] p-3 rounded-lg border border-white/5 font-mono text-xs text-gray-300 relative group-hover:border-purple-500/20 transition-colors">
                    <p>{item.draft}</p>
                    <button
                        onClick={handleCopy}
                        className="absolute bottom-2 right-2 p-1.5 bg-black border border-white/20 rounded hover:text-[#00f0ff] hover:border-[#00f0ff] transition-colors"
                    >
                        <Copy className="w-3 h-3" />
                    </button>
                </div>
                <div className="mt-3 flex justify-end">
                    <Button
                        size="sm"
                        variant="outline"
                        className="h-7 text-xs border-purple-500/30 text-purple-400 hover:bg-purple-500 hover:text-white"
                        onClick={() => item.url ? window.open(item.url, '_blank') : null}
                        disabled={!item.url}
                    >
                        {item.url ? 'ENGAGE' : 'NO LINK'} <ExternalLink className="w-3 h-3 ml-2" />
                    </Button>
                </div>
            </CardContent>
        </Card>
    );
};

export default function WarRoomDashboard() {
    const [activeTab, setActiveTab] = useState<'reddit' | 'twitter' | 'trends'>('reddit');
    const [loading, setLoading] = useState(false);
    const [opportunities, setOpportunities] = useState<Opportunity[]>([]);

    const [redditKeywords, setRedditKeywords] = useState('');
    const [twitterCompetitors, setTwitterCompetitors] = useState('');

    const runScan = async () => {
        setLoading(true);
        setOpportunities([]); // Clear previous

        try {
            // [REALITY UPGRADE] Call real backend agent scan
            // POST /api/v1/guerrilla/scan { platform: 'reddit', keywords: '...' }
            const platform = activeTab === 'trends' ? 'general' : activeTab;
            const keywords = activeTab === 'reddit' ? (redditKeywords || 'SaaS, AI, Startup') :
                activeTab === 'twitter' ? (twitterCompetitors || 'Competitor') :
                    'Technology Trends';

            const data = await api.scanOpportunities(platform, keywords);
            setOpportunities(data);

        } catch (e) {
            console.error("Scan failed", e);
            toast({ type: 'error', title: 'Scan Failed', message: 'Could not deploy agents. Check backend.' });

            // Fallback for visual continuity if API fails (optional, good for demo resilience)
            // But for this task, we want to rely on the real thing primarily.
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-end border-b border-white/10 pb-6">
                <div>
                    <div className="flex items-center gap-2 mb-2">
                        <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                        <span className="font-mono text-xs text-red-500 tracking-widest uppercase">Live Operation</span>
                    </div>
                    <h1 className="text-3xl font-black text-white uppercase tracking-tight">Guerrilla War Room</h1>
                    <p className="text-gray-400 text-sm mt-1">Deploy automated agents to intercept high-intent traffic.</p>
                </div>
                <div className="flex gap-2">
                    <Button
                        variant={activeTab === 'reddit' ? 'cyber' : 'outline'}
                        onClick={() => setActiveTab('reddit')}
                        className="h-9 text-xs"
                    >
                        REDDIT SLEEPER
                    </Button>
                    <Button
                        variant={activeTab === 'twitter' ? 'cyber' : 'outline'}
                        onClick={() => setActiveTab('twitter')}
                        className="h-9 text-xs"
                    >
                        TWITTER SHARK
                    </Button>
                    <Button
                        variant={activeTab === 'trends' ? 'cyber' : 'outline'}
                        onClick={() => setActiveTab('trends')}
                        className="h-9 text-xs"
                    >
                        TREND SURFER
                    </Button>
                </div>
            </div>

            {/* Controls */}
            <Card className="bg-[#050505] border-white/10">
                <CardContent className="p-6 flex gap-4 items-end">
                    <div className="flex-1 space-y-2">
                        <label className="text-xs font-mono text-gray-500 uppercase">
                            {activeTab === 'reddit' ? 'Target Keywords (comma sep)' :
                                activeTab === 'twitter' ? 'Competitor Handles (comma sep)' :
                                    'Trend Vertical'}
                        </label>
                        <input
                            type="text"
                            className="w-full bg-[#0a0a0a] border border-white/10 rounded-lg h-10 px-4 text-white text-sm focus:outline-none focus:border-[#00f0ff]"
                            placeholder={
                                activeTab === 'reddit' ? 'e.g. "salesforce alternative", "cold email tool"' :
                                    activeTab === 'twitter' ? 'e.g. @salesforce, @hubspot' :
                                        'Technology, AI, SaaS'
                            }
                            value={activeTab === 'reddit' ? redditKeywords : activeTab === 'twitter' ? twitterCompetitors : 'Technology'}
                            onChange={(e) => activeTab === 'reddit' ? setRedditKeywords(e.target.value) : setTwitterCompetitors(e.target.value)}
                        />
                    </div>
                    <Button onClick={runScan} isLoading={loading} className="h-10 px-8" variant="cyber">
                        <Zap className="w-4 h-4 mr-2" /> DEPLOY AGENTS
                    </Button>
                </CardContent>
            </Card>

            {/* Results Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {opportunities.map((opp, i) => (
                    <OppCard key={i} item={opp} />
                ))}
            </div>

            {opportunities.length === 0 && !loading && (
                <div className="text-center py-20 border border-dashed border-white/10 rounded-xl">
                    <div className="w-16 h-16 bg-white/5 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Search className="w-6 h-6 text-gray-600" />
                    </div>
                    <p className="text-gray-500 font-mono text-sm">Waiting for target coordinates...</p>
                </div>
            )}
        </div>
    );
}
