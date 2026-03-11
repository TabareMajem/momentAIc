
import React, { useState } from 'react';
import { Crosshair, MessageSquare, Radio, Users, TrendingUp, AlertTriangle, Globe, Zap, Play } from 'lucide-react';
import { BackendService } from '../../services/backendService';
import { MarketNarrative } from '../../types';
import { useToast } from './Toast';

const LemlistDominationAgent: React.FC = () => {
    const [competitor, setCompetitor] = useState('Outreach.io');
    const [goal, setGoal] = useState('Position them as legacy/bloated, frame us as the agile future.');
    const [narratives, setNarratives] = useState<MarketNarrative[]>([]);
    const [isGenerating, setIsGenerating] = useState(false);
    const { addToast } = useToast();

    const handleGenerate = async () => {
        setIsGenerating(true);
        try {
            const response = await BackendService.generateMarketNarrative(competitor, goal);
            if (response.success) {
                setNarratives(response.narratives);
                addToast("Narrative generated successfully", 'success');
            } else {
                addToast(response.error || "Generation failed", 'error');
            }
        } catch (e) {
            console.error(e);
            addToast("Failed to generate narrative", 'error');
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <div className="p-6 max-w-[1600px] mx-auto animate-fade-in text-slate-200 min-h-screen bg-[#0f0518]">
            <div className="mb-8 border-b border-rose-900/30 pb-6 text-center sm:text-left">
                <h2 className="text-3xl sm:text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-rose-500 via-orange-500 to-amber-500 flex flex-col sm:flex-row items-center gap-4 justify-center sm:justify-start">
                    <Crosshair className="w-10 h-10 text-rose-500 shrink-0" />
                    Lemlist v4: Domination Organism
                </h2>
                <p className="text-rose-400/60 mt-2 text-base sm:text-lg font-light tracking-wide">Market Reality Manipulation • Ecosystem Colonization • Competitive Annihilation</p>
            </div>

            <div className="grid xl:grid-cols-12 gap-8">

                {/* --- LEFT: NARRATIVE ENGINEER --- */}
                <div className="xl:col-span-7 bg-slate-900/50 border border-rose-500/20 rounded-2xl p-8 relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-rose-500 via-orange-500 to-transparent opacity-50"></div>

                    <div className="flex items-center justify-between mb-8">
                        <h3 className="text-xl font-bold text-rose-100 flex items-center gap-2">
                            <MessageSquare className="w-5 h-5 text-rose-500" /> Market Reality Manipulator
                        </h3>
                    </div>

                    <div className="grid md:grid-cols-2 gap-6 mb-8">
                        <div>
                            <label className="text-xs font-bold text-rose-500/70 uppercase mb-2 block">Target Entity / Competitor</label>
                            <input
                                value={competitor}
                                onChange={e => setCompetitor(e.target.value)}
                                className="w-full bg-slate-950 border border-rose-900/50 rounded-lg p-3 text-rose-100 focus:border-rose-500/50 outline-none transition-all font-mono text-sm"
                            />
                        </div>
                        <div>
                            <label className="text-xs font-bold text-rose-500/70 uppercase mb-2 block">Distortion Goal</label>
                            <input
                                value={goal}
                                onChange={e => setGoal(e.target.value)}
                                className="w-full bg-slate-950 border border-rose-900/50 rounded-lg p-3 text-rose-100 focus:border-rose-500/50 outline-none transition-all font-mono text-sm"
                            />
                        </div>
                    </div>

                    <button
                        onClick={handleGenerate}
                        disabled={isGenerating}
                        className="w-full bg-rose-600/20 hover:bg-rose-600/40 text-rose-300 border border-rose-500/50 py-4 rounded-xl font-bold uppercase tracking-widest transition-all disabled:opacity-50 mb-8 flex items-center justify-center gap-2"
                    >
                        {isGenerating ? <Zap className="w-5 h-5 animate-pulse" /> : <Radio className="w-5 h-5" />}
                        Initialize Narrative Injection
                    </button>

                    <div className="space-y-6">
                        {narratives.map((n, i) => (
                            <div key={i} className="bg-slate-950 border border-rose-500/20 rounded-xl p-6 hover:border-rose-500/50 transition-all">
                                <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-3 mb-4">
                                    <h4 className="text-lg font-bold text-white">{n.topic}</h4>
                                    <div className="flex flex-wrap items-center gap-2">
                                        <span className="text-[10px] font-mono bg-rose-950 text-rose-400 border border-rose-900 px-2 py-1 rounded">
                                            CURRENT: {n.currentSentiment}
                                        </span>
                                        <ArrowRightIcon className="w-4 h-4 text-rose-500/50 hidden sm:block" />
                                        <span className="text-[10px] font-mono bg-emerald-950 text-emerald-400 border border-emerald-900 px-2 py-1 rounded">
                                            TARGET: {n.targetSentiment}
                                        </span>
                                    </div>
                                </div>
                                <p className="text-sm text-rose-200/80 italic mb-4 border-l-2 border-rose-500 pl-4">
                                    "{n.strategy}"
                                </p>
                                <div className="grid gap-2">
                                    {n.tactics.map((t, idx) => (
                                        <div key={idx} className="flex items-center gap-3 text-xs text-slate-400 bg-slate-900/50 p-2 rounded">
                                            <Zap className="w-3 h-3 text-amber-500" />
                                            {t}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* --- RIGHT: ECOSYSTEM COLONIZER --- */}
                <div className="xl:col-span-5 flex flex-col gap-6">
                    <div className="bg-slate-900/50 border border-orange-500/20 rounded-2xl p-6 flex-1">
                        <div className="flex items-center justify-between mb-6">
                            <h3 className="text-lg font-bold text-orange-100 flex items-center gap-2">
                                <Globe className="w-5 h-5 text-orange-500" /> Ecosystem Colonization
                            </h3>
                        </div>

                        <div className="space-y-4">
                            {[
                                { platform: "LinkedIn", status: "COLONIZED", score: 92, trend: "up" },
                                { platform: "YouTube", status: "INFILTRATING", score: 64, trend: "up" },
                                { platform: "Reddit (r/sales)", status: "TARGETED", score: 15, trend: "flat" },
                                { platform: "Twitter/X", status: "COLONIZED", score: 88, trend: "down" }
                            ].map((p, i) => (
                                <div key={i} className="flex items-center justify-between bg-slate-950 p-4 rounded-xl border border-slate-800">
                                    <div className="flex items-center gap-3">
                                        <div className={`w-2 h-2 rounded-full ${p.status === 'COLONIZED' ? 'bg-emerald-500 animate-pulse' :
                                            p.status === 'INFILTRATING' ? 'bg-orange-500' : 'bg-rose-500'
                                            }`}></div>
                                        <span className="font-bold text-slate-200">{p.platform}</span>
                                    </div>
                                    <div className="flex items-center gap-4">
                                        <div className="text-right">
                                            <div className="text-xs text-slate-500 font-mono">INFLUENCE</div>
                                            <div className="text-lg font-bold text-white leading-none">{p.score}%</div>
                                        </div>
                                        <TrendingUp className={`w-4 h-4 ${p.trend === 'up' ? 'text-emerald-500' : p.trend === 'down' ? 'text-rose-500' : 'text-slate-500'}`} />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="bg-slate-900/50 border border-rose-500/20 rounded-2xl p-6">
                        <h3 className="text-lg font-bold text-rose-100 flex items-center gap-2 mb-4">
                            <AlertTriangle className="w-5 h-5 text-rose-500" /> Competitive Annihilation
                        </h3>
                        <div className="bg-slate-950 rounded-xl p-4 border border-rose-900/30">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-xs text-rose-400 font-bold uppercase">Target Vulnerability</span>
                                <span className="text-xs text-rose-500 font-mono">DETECTED</span>
                            </div>
                            <p className="text-sm text-slate-300 mb-3">
                                Competitor pricing update caused 15% negative sentiment spike on G2/Capterra.
                            </p>
                            <button className="w-full py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-bold uppercase tracking-wide flex items-center justify-center gap-2 transition-colors">
                                <Play className="w-3 h-3" /> Deploy Counter-Campaign
                            </button>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
};

const ArrowRightIcon = ({ className }: { className?: string }) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <line x1="5" y1="12" x2="19" y2="12"></line>
        <polyline points="12 5 19 12 12 19"></polyline>
    </svg>
);

export default LemlistDominationAgent;
