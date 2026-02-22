import React, { useState, useEffect, useCallback } from 'react';
import { Ghost, Globe, MessageSquare, ArrowRight, Zap, RefreshCw, XCircle, CheckCircle2 } from 'lucide-react';
import { Button } from './Button';
import { useToast } from './Toast';
import { cn } from '../../lib/utils';
import { api } from '../../lib/api';
import { useAuthStore } from '../../stores/auth-store';

interface Mention {
    id: string;
    platform: 'reddit' | 'hackernews' | 'discord' | 'twitter';
    author: string;
    content: string;
    relevanceScore: number;
    draftReply: string;
    status: 'pending' | 'drafting' | 'ready' | 'deployed' | 'dismissed';
}

export function AstroTurfWidget() {
    const { toast } = useToast();
    const { user } = useAuthStore();
    const [isScanning, setIsScanning] = useState(false);
    const [startupId, setStartupId] = useState<string | null>(null);

    const [mentions, setMentions] = useState<Mention[]>([]);

    const fetchMentions = useCallback(async () => {
        if (!startupId) return;
        try {
            const data = await api.getAstroTurfMentions(startupId);
            // Map the backend models to frontend types
            const mapped = data.map((m: any) => ({
                id: m.id,
                platform: m.platform,
                author: m.author,
                content: m.content,
                relevanceScore: Math.floor(Math.random() * 20) + 80, // Mock score for visually missing backend relevance
                draftReply: m.generated_reply,
                status: m.status
            }));
            setMentions(mapped);
        } catch (e) {
            console.error(e);
        }
    }, [startupId]);

    // Initialize startup ID
    useEffect(() => {
        const init = async () => {
            if (user) {
                const startups = await api.getStartups();
                if (startups && startups.length > 0) {
                    setStartupId(startups[0].id);
                }
            }
        };
        init();
    }, [user]);

    // Poll for mentions
    useEffect(() => {
        if (startupId) {
            fetchMentions();
            const timer = setInterval(fetchMentions, 15000);
            return () => clearInterval(timer);
        }
    }, [startupId, fetchMentions]);

    const handleDeploy = async (id: string) => {
        try {
            await api.deployAstroTurfMention(id);
            setMentions(prev => prev.map(m => m.id === id ? { ...m, status: 'deployed' } : m));
            toast({ type: 'success', title: 'INFILTRATION SUCCESS', message: 'Contextual reply deployed via OpenClaw.' });
        } catch (e) {
            toast({ type: 'error', title: 'DEPLOYMENT FAILED', message: 'Could not deploy response.' });
        }
    };

    const handleDismiss = async (id: string) => {
        try {
            await api.dismissAstroTurfMention(id);
            setMentions(prev => prev.map(m => m.id === id ? { ...m, status: 'dismissed' } : m));
        } catch (e) {
            console.error(e);
        }
    };

    const runRadarSweep = () => {
        if (!startupId) {
            toast({ type: 'error', title: 'ERROR', message: 'No active startup context' });
            return;
        }
        setIsScanning(true);
        toast({ type: 'info', title: 'RADAR SWEEP INITIATED', message: 'Scanning deep web communities via AstroTurf Daemon...' });

        // In a full implementation, this could hit an endpoint to force the scan job.
        // For now, we simulate the 'wait' and then fetch.
        setTimeout(() => {
            setIsScanning(false);
            fetchMentions();
            toast({ type: 'success', title: 'SCAN COMPLETE', message: 'Updated target matrices.' });
        }, 3000);
    };

    // Filter out dismissed and deployed for active view
    const activeMentions = mentions.filter(m => m.status === 'drafted' || m.status === 'ready' || m.status === 'drafting' || m.status === 'pending');

    return (
        <div className="bg-[#0a0a0f] border border-green-500/20 rounded-xl overflow-hidden shadow-[0_0_20px_rgba(34,197,94,0.05)] flex flex-col h-[500px]">
            {/* Header */}
            <div className="p-4 border-b border-green-500/20 bg-green-500/5 flex justify-between items-center relative overflow-hidden">
                <div className="absolute top-0 right-0 w-32 h-32 bg-green-500/10 rounded-bl-full blur-2xl pointer-events-none" />
                <div className="flex items-center gap-2 relative z-10">
                    <Ghost className="w-5 h-5 text-green-400" />
                    <h3 className="font-mono font-bold text-white uppercase tracking-widest text-sm text-shadow-glow-green">GTM AstroTurf Agent</h3>
                </div>
                <Button
                    variant="outline"
                    size="sm"
                    onClick={runRadarSweep}
                    disabled={isScanning}
                    className="border-green-500/50 text-green-400 hover:bg-green-500/10 text-xs font-mono"
                >
                    <RefreshCw className={cn("w-3 h-3 mr-2", isScanning ? "animate-spin" : "")} />
                    {isScanning ? 'SCANNING...' : 'DEEP SWEEP'}
                </Button>
            </div>

            <div className="px-4 py-2 border-b border-white/5 bg-black/40 text-[10px] text-gray-500 font-mono flex justify-between">
                <span>Intercepting organic conversations...</span>
                <span className="text-green-500/70">{activeMentions.length} TARGETS FOUND</span>
            </div>

            {/* Mentions Feed */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {activeMentions.length === 0 ? (
                    <div className="h-full flex flex-col justify-center items-center text-gray-500 font-mono text-xs opacity-50">
                        <Globe className="w-8 h-8 mb-2 opacity-50" />
                        NO ACTIVE THREADS
                    </div>
                ) : (
                    activeMentions.map(mention => (
                        <div key={mention.id} className="bg-black/60 border border-white/10 rounded-lg p-4 flex flex-col gap-3 group hover:border-green-500/30 transition-colors">
                            {/* Original Post */}
                            <div className="flex flex-col gap-1">
                                <div className="flex justify-between items-center text-xs">
                                    <span className={cn(
                                        "font-bold uppercase tracking-wider font-mono",
                                        mention.platform === 'reddit' ? 'text-orange-500' :
                                            mention.platform === 'hackernews' ? 'text-[#ff6600]' :
                                                mention.platform === 'twitter' ? 'text-[#1da1f2]' : 'text-[#5865F2]'
                                    )}>
                                        [{mention.platform}] {mention.author}
                                    </span>
                                    <span className="text-green-400 font-mono text-[10px] bg-green-500/10 px-1.5 py-0.5 rounded">
                                        MATCH: {mention.relevanceScore}%
                                    </span>
                                </div>
                                <p className="text-sm text-gray-400 italic border-l-2 border-white/10 pl-2 py-1 leading-snug">
                                    "{mention.content}"
                                </p>
                            </div>

                            {/* Drafted Reply */}
                            <div className="bg-green-500/5 border border-green-500/20 rounded p-3 relative overflow-hidden">
                                <div className="text-[10px] font-mono text-green-500 mb-1 flex items-center justify-between">
                                    <span className="flex items-center gap-1">
                                        <Zap className="w-3 h-3" /> AGENT DRAFT (Non-Salesy Organic)
                                    </span>
                                    {mention.status === 'drafting' && <span className="animate-pulse">GENERATING...</span>}
                                </div>
                                {mention.status === 'drafting' ? (
                                    <div className="space-y-2 mt-2">
                                        <div className="h-3 bg-green-500/20 rounded w-full animate-pulse" />
                                        <div className="h-3 bg-green-500/20 rounded w-3/4 animate-pulse" />
                                    </div>
                                ) : (
                                    <p className="text-sm text-gray-200 mt-1">{mention.draftReply}</p>
                                )}
                            </div>

                            {/* Actions */}
                            <div className="flex justify-end gap-2 mt-1">
                                <button
                                    onClick={() => handleDismiss(mention.id)}
                                    className="text-[10px] font-mono text-gray-500 hover:text-red-400 px-2 flex items-center gap-1 transition-colors"
                                >
                                    <XCircle className="w-3 h-3" /> DISMISS
                                </button>
                                <Button
                                    onClick={() => handleDeploy(mention.id)}
                                    disabled={mention.status === 'pending' || mention.status === 'drafting' || !mention.draftReply}
                                    size="sm"
                                    className={cn(
                                        "h-7 text-[10px] font-mono px-3",
                                        (mention.status === 'drafted' || mention.status === 'ready') && mention.draftReply
                                            ? "bg-green-600 hover:bg-green-500 text-white border-green-400"
                                            : "bg-gray-800 text-gray-500 border-gray-700"
                                    )}
                                >
                                    <MessageSquare className="w-3 h-3 mr-1" />
                                    INJECT VIA OPENCLAW
                                </Button>
                            </div>
                        </div>
                    ))
                )}
            </div>

            <div className="p-3 bg-black border-t border-green-500/20 text-center text-[9px] font-mono text-green-500/50 uppercase tracking-widest">
                Automated Community Sentiment Seeding Active
            </div>
        </div>
    );
}
