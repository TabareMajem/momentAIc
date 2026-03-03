import React, { useState, useEffect } from 'react';
import { api } from '../lib/api';
import { Button } from '../components/ui/Button';
import { Sparkles, CheckCircle2, AlertTriangle, ArrowRight, Loader2, Zap, Rocket, Terminal, PlayCircle } from 'lucide-react';
import { useAuthStore } from '../stores/auth-store';
import { GeneratedImage } from '../components/ui/GeneratedImage';
import { SymbioTaskVideoModal } from '../components/ui/SymbioTaskVideoModal';

interface Move {
    id: string;
    title: string;
    agent_type: string;
    payload: any;
}

interface MorningBrief {
    overnight_updates: { icon: string; text: string }[];
    today_moves: Move[];
    mentor_note: string;
    mentor_persona: string;
}

export default function GhostBoard() {
    const { user } = useAuthStore();
    const [brief, setBrief] = useState<MorningBrief | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [executingMoves, setExecutingMoves] = useState<Record<string, 'pending' | 'running' | 'done' | 'error'>>({});
    const [generatedAssets, setGeneratedAssets] = useState<Record<string, { uri: string; prompt: string }>>({});
    const [videoModal, setVideoModal] = useState<{ open: boolean; imageUri?: string; prompt?: string }>({ open: false });

    useEffect(() => {
        loadBrief();
    }, []);

    const loadBrief = async () => {
        try {
            // Using the actual backend API request
            const data = await api.getMorningBrief();
            setBrief(data);

            // Initialize execution state
            const initialExecState: Record<string, 'pending'> = {};
            data.today_moves.forEach((m: Move) => {
                initialExecState[m.id] = 'pending';
            });
            setExecutingMoves(initialExecState);
        } catch (error) {
            console.error('Failed to load morning brief:', error);
            // Fallback for visual testing if disconnected
            setBrief({
                overnight_updates: [
                    { icon: '⚠️', text: 'Error connecting to Ghost Board matrix.' }
                ],
                today_moves: [],
                mentor_note: 'Fix your server configuration immediately.',
                mentor_persona: 'pg'
            });
        } finally {
            setIsLoading(false);
        }
    };

    const handleAuthorize = async (move: Move) => {
        if (executingMoves[move.id] === 'running' || executingMoves[move.id] === 'done') return;

        setExecutingMoves(prev => ({ ...prev, [move.id]: 'running' }));

        try {
            const resp = await api.client.post('/proactive/execute-action', {
                action_id: move.id,
                agent_type: move.agent_type,
                payload: move.payload
            });

            setExecutingMoves(prev => ({ ...prev, [move.id]: 'done' }));

            if (resp.data?.generated_asset) {
                setGeneratedAssets(prev => ({
                    ...prev,
                    [move.id]: {
                        uri: resp.data.generated_asset,
                        prompt: resp.data.asset_prompt || "AI Generated Asset"
                    }
                }));
            }
        } catch (error) {
            console.error('Failed to execute move:', error);
            setExecutingMoves(prev => ({ ...prev, [move.id]: 'error' }));
        }
    };

    if (isLoading) {
        return (
            <div className="min-h-[80vh] flex flex-col items-center justify-center gap-4 text-gray-500 font-mono">
                <Loader2 className="w-8 h-8 animate-spin text-purple-500" />
                <p className="animate-pulse tracking-widest text-xs">SYNTHESIZING MORNING BRIEF...</p>
            </div>
        );
    }

    if (!brief) return null;

    return (
        <div className="max-w-4xl mx-auto py-8">
            <div className="flex items-center gap-3 mb-8">
                <Terminal className="w-6 h-6 text-purple-400" />
                <h1 className="text-3xl font-black tracking-tighter uppercase text-white">Ghost Board</h1>
            </div>

            {/* ASCII Style Terminal Container */}
            <div className="bg-[#050505] border border-gray-800 rounded-xl overflow-hidden font-mono text-sm shadow-2xl">

                {/* Header Tape */}
                <div className="bg-gray-900 border-b border-gray-800 px-6 py-3 flex justify-between items-center text-xs text-gray-400">
                    <div className="flex items-center gap-2">
                        <Sparkles className="w-3.5 h-3.5 text-yellow-500" />
                        <span>SYNTHETIC CO-FOUNDER BRIEF</span>
                    </div>
                    <div>{new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}</div>
                </div>

                <div className="p-8 space-y-10">

                    {/* 1. Overnight */}
                    <section>
                        <h2 className="text-gray-500 mb-4 flex items-center gap-2 text-xs font-bold tracking-widest">
                            <span className="w-2 h-2 bg-purple-500 rounded-full animate-pulse"></span>
                            OVERNIGHT TELEMETRY
                        </h2>
                        <ul className="space-y-3">
                            {brief.overnight_updates.map((update, idx) => (
                                <li key={idx} className="flex gap-3 text-gray-300">
                                    <span className="flex-shrink-0 w-6 text-center">{update.icon}</span>
                                    <span>{update.text}</span>
                                </li>
                            ))}
                        </ul>
                    </section>

                    {/* 2. Today's Moves (Actionable) */}
                    <section>
                        <h2 className="text-gray-500 mb-4 flex items-center gap-2 text-xs font-bold tracking-widest">
                            <Zap className="w-4 h-4 text-purple-500" />
                            YOUR 3 MOVES TODAY
                        </h2>

                        <div className="space-y-4">
                            {brief.today_moves.map((move, idx) => {
                                const state = executingMoves[move.id] || 'pending';

                                return (
                                    <div key={idx} className="flex flex-col border border-gray-800 rounded-lg overflow-hidden bg-gray-900/50 hover:border-purple-500/30 transition-colors mb-4">
                                        <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center p-4">
                                            <div>
                                                <div className="flex items-center gap-2 mb-1">
                                                    <span className="px-2 py-0.5 rounded text-[10px] bg-purple-500/10 text-purple-400 font-bold tracking-wider">
                                                        {move.agent_type}
                                                    </span>
                                                </div>
                                                <div className="text-gray-200">{move.title}</div>
                                            </div>

                                            <div className="w-full sm:w-auto flex-shrink-0 shrink-0">
                                                {state === 'done' ? (
                                                    <div className="flex items-center gap-2 px-4 py-2 w-full sm:w-[140px] justify-center bg-green-500/10 text-green-400 border border-green-500/20 rounded-md text-xs font-bold font-mono">
                                                        <CheckCircle2 className="w-4 h-4" /> EXECUTED
                                                    </div>
                                                ) : state === 'running' ? (
                                                    <div className="flex items-center gap-2 px-4 py-2 w-full sm:w-[140px] justify-center bg-purple-500/20 text-purple-300 border border-purple-500/40 rounded-md text-xs font-bold font-mono animate-pulse">
                                                        <Loader2 className="w-4 h-4 animate-spin" /> DEPLOYING
                                                    </div>
                                                ) : state === 'error' ? (
                                                    <Button
                                                        onClick={() => handleAuthorize(move)}
                                                        className="w-full sm:w-[140px] bg-red-500/20 hover:bg-red-500/30 text-red-500 border border-red-500/50 font-mono text-xs h-9 uppercase"
                                                    >
                                                        <AlertTriangle className="w-4 h-4 mr-2" /> RETRY
                                                    </Button>
                                                ) : (
                                                    <Button
                                                        onClick={() => handleAuthorize(move)}
                                                        className="w-full sm:w-[140px] bg-purple-600 hover:bg-purple-500 text-white font-mono text-xs scale-100 active:scale-95 transition-all shadow-[0_0_15px_rgba(168,85,247,0.4)] h-9 uppercase group"
                                                    >
                                                        <Rocket className="w-3.5 h-3.5 mr-2 group-hover:-translate-y-0.5 group-hover:translate-x-0.5 transition-transform" />
                                                        AUTHORIZE
                                                    </Button>
                                                )}
                                            </div>
                                        </div>

                                        {/* Render Generated Asset If Available */}
                                        {generatedAssets[move.id] && (
                                            <div className="p-4 border-t border-gray-800 bg-black/20 space-y-3">
                                                <GeneratedImage
                                                    dataUri={generatedAssets[move.id].uri}
                                                    prompt={generatedAssets[move.id].prompt}
                                                />
                                                <Button
                                                    onClick={() => setVideoModal({ open: true, imageUri: generatedAssets[move.id].uri, prompt: generatedAssets[move.id].prompt })}
                                                    className="w-full sm:w-auto h-10 px-6 bg-gradient-to-r from-pink-600 to-purple-600 hover:from-pink-500 hover:to-purple-500 text-white text-xs font-bold font-mono rounded-lg shadow-[0_0_15px_rgba(236,72,153,0.3)] transition-all flex items-center gap-2 uppercase tracking-wider"
                                                >
                                                    <PlayCircle className="w-4 h-4" /> Generate Video Ad · 10% OFF
                                                </Button>
                                            </div>
                                        )}
                                    </div>
                                );
                            })}

                            {brief.today_moves.length === 0 && (
                                <div className="p-4 text-gray-500 italic">No recommended moves for today. Keep building.</div>
                            )}
                        </div>
                    </section>

                    <hr className="border-gray-800" />

                    {/* 3. Ghost Mentor Note */}
                    <section className="bg-[#0a0a0a] border-l-2 border-red-500 p-5 rounded-r-lg">
                        <h2 className="text-red-500 mb-2 flex items-center gap-2 text-xs font-bold tracking-widest uppercase">
                            <AlertTriangle className="w-4 h-4" />
                            MENTOR NOTE ({brief.mentor_persona.toUpperCase()} MODE)
                        </h2>
                        <p className="text-gray-300 italic leading-relaxed text-sm">
                            "{brief.mentor_note}"
                        </p>
                    </section>

                </div>
            </div >
            <div className="mt-8 text-center text-gray-600 text-[10px] font-mono tracking-widest">
                END OF COMMUNICATION. CLOSING CHANNEL.
            </div>

            {/* Symbiotask Video Generation Modal */}
            <SymbioTaskVideoModal
                isOpen={videoModal.open}
                onClose={() => setVideoModal({ open: false })}
                imageUri={videoModal.imageUri}
                prompt={videoModal.prompt}
            />
        </div>
    );
}
