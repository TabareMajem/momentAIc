import React, { useState, useEffect } from 'react';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Input } from '../components/ui/Input';
import { useToast } from '../components/ui/Toast';
import { Crown, Zap, RefreshCw, Copy, Download, Image as ImageIcon, Send } from 'lucide-react';
import api from '../lib/api';

// ============ TYPES ============

interface ViralAsset {
    id: string;
    campaign_topic: string;
    hook_text: string;
    image_url: string;
    status: string;
    created_at: string;
}

// ============ MAIN COMPONENT ============

export default function ViralSwarm() {
    const [topic, setTopic] = useState('');
    const [assets, setAssets] = useState<ViralAsset[]>([]);
    const [loading, setLoading] = useState(false);
    const [fetchingHistory, setFetchingHistory] = useState(true);
    const { toast } = useToast();

    useEffect(() => {
        loadHistory();
    }, []);

    const loadHistory = async () => {
        try {
            const history = await api.getViralHistory();
            setAssets(history);
        } catch (error) {
            console.error("Failed to load viral history", error);
        } finally {
            setFetchingHistory(false);
        }
    };

    const handleDeploySwarm = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!topic.trim()) return;

        setLoading(true);
        try {
            const newAssets = await api.generateViralCampaign(topic);
            setAssets(prev => [...newAssets, ...prev]);
            setTopic('');
            toast({ type: 'success', title: 'Swarm Deployed!', message: '3 new viral assets generated successfully.' });
        } catch (error: any) {
            toast({ type: 'error', title: 'Generation Failed', message: error.response?.data?.detail || 'Failed to deploy swarm.' });
        } finally {
            setLoading(false);
        }
    };

    const copyHook = (text: string) => {
        navigator.clipboard.writeText(text);
        toast({ type: 'success', title: 'Copied!', message: 'Viral hook copied to clipboard.' });
    };

    return (
        <div className="space-y-8 pb-12 max-w-6xl mx-auto">
            {/* Header */}
            <div className="border-b border-white/10 pb-6 relative overflow-hidden">
                <div className="absolute top-[-50%] right-[-10%] w-[300px] h-[300px] bg-purple-600/20 blur-[100px] rounded-full pointer-events-none" />
                <h1 className="text-3xl font-black text-white tracking-tighter flex items-center gap-3">
                    <Zap className="w-8 h-8 text-[#00f0ff]" />
                    AUTONOMOUS VIRAL SWARM
                    <Badge variant="cyber" className="text-xs">DALL-E 3 ENGINE</Badge>
                </h1>
                <p className="text-gray-500 font-mono text-sm mt-3 max-w-2xl">
                    Deploy AI agents to autonomously ideate, write, and render high-converting social media hooks and dramatic marketing imagery for your campaigns.
                </p>
            </div>

            {/* Command Input */}
            <Card className="p-8 bg-black/60 border-[#00f0ff]/20 neon-border relative overflow-hidden">

                <form onSubmit={handleDeploySwarm} className="relative z-10">
                    <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                        <Crown className="w-5 h-5 text-[#00f0ff]" />
                        Campaign Directives
                    </h2>
                    <div className="flex flex-col md:flex-row gap-4">
                        <Input
                            placeholder="e.g., The death of traditional B2B sales in 2026..."
                            value={topic}
                            onChange={(e) => setTopic(e.target.value)}
                            className="flex-1 text-lg py-6 bg-black/50 border-white/20"
                            disabled={loading}
                        />
                        <Button
                            type="submit"
                            variant="cyber"
                            className="h-auto px-8 md:w-auto w-full group relative overflow-hidden"
                            disabled={loading || !topic.trim()}
                        >
                            <span className="relative z-10 flex items-center gap-2 font-bold tracking-wider">
                                {loading ? (
                                    <><RefreshCw className="w-5 h-5 animate-spin" /> SYNTHESIZING...</>
                                ) : (
                                    <><Zap className="w-5 h-5 group-hover:scale-125 transition-transform" /> DEPLOY SWARM</>
                                )}
                            </span>
                            <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-[#00f0ff] opacity-0 group-hover:opacity-20 transition-opacity" />
                        </Button>
                    </div>
                    <p className="text-xs text-gray-400 mt-3 italic">
                        Generates 3 variant hooks with matching high-resolution 1024x1024 DALL-E images.
                    </p>
                </form>
            </Card>

            {/* Results Grid */}
            <div className="space-y-4">
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                    <ImageIcon className="w-5 h-5 text-gray-400" />
                    Asset Arsenal
                </h2>

                {fetchingHistory ? (
                    <div className="h-40 flex items-center justify-center">
                        <div className="text-[#00f0ff] font-mono animate-pulse">CONNECTING_TO_SWARM...</div>
                    </div>
                ) : assets.length === 0 ? (
                    <Card className="p-12 text-center border-dashed border-white/10 bg-white/5">
                        <div className="text-gray-500 mb-2">No viral assets generated yet.</div>
                        <div className="text-sm text-gray-600">Enter a campaign topic above to deploy the swarm.</div>
                    </Card>
                ) : (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {assets.map((asset) => (
                            <Card key={asset.id} className="overflow-hidden border-white/10 bg-black/40 flex flex-col group hover:border-[#00f0ff]/50 transition-colors">
                                {/* Image Container */}
                                <div className="h-64 relative overflow-hidden bg-gray-900 border-b border-white/10">
                                    {asset.image_url ? (
                                        <>
                                            <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent z-10" />
                                            <img
                                                src={asset.image_url}
                                                alt="Viral Asset"
                                                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
                                            />
                                        </>
                                    ) : (
                                        <div className="w-full h-full flex items-center justify-center text-gray-600">
                                            No Image
                                        </div>
                                    )}
                                    <div className="absolute top-3 left-3 z-20">
                                        <Badge variant="cyber" className="bg-black/80 backdrop-blur-md border-[#00f0ff]/30 text-[10px]">
                                            DALL-E 3
                                        </Badge>
                                    </div>
                                </div>

                                {/* Content */}
                                <div className="p-5 flex-1 flex flex-col relative z-20">
                                    <div className="text-xs text-[#00f0ff] font-mono mb-2 uppercase tracking-wider">
                                        TOPIC: {asset.campaign_topic}
                                    </div>
                                    <div className="text-sm text-white/90 mb-6 italic leading-relaxed flex-1">
                                        "{asset.hook_text}"
                                    </div>

                                    <div className="grid grid-cols-2 gap-2 mt-auto">
                                        <Button variant="outline" size="sm" onClick={() => copyHook(asset.hook_text)} className="w-full bg-white/5 hover:bg-white/10 hover:text-white border-white/10">
                                            <Copy className="w-3 h-3 mr-2" /> Hook
                                        </Button>
                                        <Button variant="outline" size="sm" onClick={() => window.open(asset.image_url, '_blank')} className="w-full bg-white/5 hover:bg-white/10 hover:text-white border-white/10">
                                            <Download className="w-3 h-3 mr-2" /> Media
                                        </Button>
                                    </div>
                                </div>
                            </Card>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
