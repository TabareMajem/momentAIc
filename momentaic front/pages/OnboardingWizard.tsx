import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../lib/api';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Zap, ArrowRight, Save, Wand2, CheckCircle, Loader } from 'lucide-react';

export default function OnboardingWizard() {
    const navigate = useNavigate();
    const [step, setStep] = useState<'input' | 'analyzing' | 'review'>('input');
    const [url, setUrl] = useState('');
    const [description, setDescription] = useState('');
    const [strategy, setStrategy] = useState<any>(null);
    const [loading, setLoading] = useState(false);

    const handleAnalyze = async () => {
        setLoading(true);
        setStep('analyzing');
        try {
            const result = await api.runOnboardingWizard(url, description);
            setStrategy(result);
            setStep('review');
        } catch (error) {
            console.error("Wizard failed", error);
            // Fallback for demo if API fails (so UI doesn't break)
            setStep('input');
            alert("Analysis failed. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    const handleLaunch = () => {
        // In a real app, this would save the strategy to DB
        navigate('/dashboard');
    };

    return (
        <div className="min-h-screen bg-[#050505] text-white flex flex-col items-center justify-center p-6 relative overflow-hidden">
            {/* Background Effects */}
            <div className="absolute top-0 left-0 w-full h-full bg-cyber-grid opacity-10 pointer-events-none"></div>
            <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-[#00f0ff] opacity-10 blur-[150px] rounded-full pointer-events-none"></div>

            <div className="max-w-2xl w-full relative z-10">
                <div className="text-center mb-12">
                    <h1 className="text-4xl md:text-5xl font-black font-mono tracking-tighter mb-4 text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-500 uppercase">
                        60-Second Setup
                    </h1>
                    <p className="text-gray-400 font-mono text-sm max-w-md mx-auto">
                        Paste your URL. Agent Swarm will analyze your product, identify your ideal customer, and draft your first viral campaign.
                    </p>
                </div>

                <Card className="p-8 bg-black/40 border border-white/10 backdrop-blur-md shadow-2xl relative">
                    {/* Step Indicators */}
                    <div className="absolute top-0 left-0 w-full h-1 bg-white/5">
                        <div
                            className="h-full bg-[#00f0ff] transition-all duration-700 ease-in-out"
                            style={{ width: step === 'input' ? '33%' : step === 'analyzing' ? '66%' : '100%' }}
                        />
                    </div>

                    {step === 'input' && (
                        <div className="space-y-6 animate-fade-in-up">
                            <div>
                                <label className="block text-xs font-mono text-[#00f0ff] uppercase tracking-widest mb-2">Target URL</label>
                                <input
                                    type="text"
                                    value={url}
                                    onChange={(e) => setUrl(e.target.value)}
                                    placeholder="https://momentaic.com"
                                    className="w-full bg-[#111] border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-600 focus:outline-none focus:border-[#00f0ff] transition-colors font-mono"
                                />
                            </div>
                            <div>
                                <label className="block text-xs font-mono text-gray-500 uppercase tracking-widest mb-2">Description (Optional)</label>
                                <textarea
                                    value={description}
                                    onChange={(e) => setDescription(e.target.value)}
                                    placeholder="An AI platform for solopreneurs..."
                                    className="w-full bg-[#111] border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-600 focus:outline-none focus:border-[#00f0ff] transition-colors font-mono h-24 resize-none"
                                />
                            </div>
                            <Button
                                onClick={handleAnalyze}
                                disabled={!url}
                                className="w-full bg-[#00f0ff] text-black hover:bg-white font-bold h-12 rounded-lg uppercase tracking-widest shadow-[0_0_20px_rgba(0,240,255,0.3)] hover:shadow-[0_0_30px_rgba(0,240,255,0.5)] transition-all"
                            >
                                <Wand2 className="w-4 h-4 mr-2" />
                                Activate Agent Swarm
                            </Button>
                        </div>
                    )}

                    {step === 'analyzing' && (
                        <div className="py-12 flex flex-col items-center justify-center text-center animate-fade-in">
                            <div className="relative mb-8">
                                <div className="w-24 h-24 border-t-2 border-b-2 border-[#00f0ff] rounded-full animate-spin"></div>
                                <div className="absolute inset-0 flex items-center justify-center">
                                    <Zap className="w-8 h-8 text-[#00f0ff] animate-pulse" />
                                </div>
                            </div>
                            <h3 className="text-xl font-bold text-white mb-2">Analyzing Growth Channels</h3>
                            <p className="text-gray-500 font-mono text-xs animate-pulse">Running competitive audit...</p>
                        </div>
                    )}

                    {step === 'review' && strategy && (
                        <div className="space-y-6 animate-fade-in-up">
                            <div className="flex items-center gap-2 mb-4">
                                <CheckCircle className="w-5 h-5 text-green-500" />
                                <span className="text-sm font-mono text-green-500 uppercase tracking-widest">Analysis Complete</span>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <StrategyCard label="Ideal Customer" value={strategy.strategy.target_audience} />
                                <StrategyCard label="Pain Point" value={strategy.strategy.pain_point} />
                                <StrategyCard label="Value Prop" value={strategy.strategy.value_prop} />
                                <StrategyCard label="Weekly Goal" value={strategy.strategy.weekly_goal} />
                            </div>

                            <div className="bg-[#111] border border-white/10 rounded-lg p-4 relative group">
                                <div className="absolute -top-2 left-4 bg-[#050505] px-2 text-[10px] text-[#00f0ff] font-mono uppercase tracking-widest border border-[#00f0ff]/20 rounded">
                                    Proposed Viral Post
                                </div>
                                <p className="text-sm text-gray-300 italic leading-relaxed whitespace-pre-wrap">
                                    {strategy.generated_post}
                                </p>
                            </div>

                            <Button
                                onClick={handleLaunch}
                                className="w-full bg-green-500 text-black hover:bg-white font-bold h-12 rounded-lg uppercase tracking-widest shadow-[0_0_20px_rgba(34,197,94,0.3)] hover:shadow-[0_0_30px_rgba(34,197,94,0.5)] transition-all"
                            >
                                <Save className="w-4 h-4 mr-2" />
                                Save & Launch Campaign
                            </Button>
                        </div>
                    )}
                </Card>
            </div>
        </div>
    );
}

const StrategyCard = ({ label, value }: { label: string, value: string }) => (
    <div className="bg-[#111]/50 border border-white/5 p-3 rounded hover:border-white/20 transition-colors">
        <div className="text-[10px] text-gray-500 font-mono uppercase tracking-widest mb-1">{label}</div>
        <div className="text-sm font-bold text-white">{value}</div>
    </div>
);
