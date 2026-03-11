import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bot, Shield, Globe, ArrowRight, CheckCircle2, Server } from 'lucide-react';
import { cn } from '../lib/utils';

export default function ScraperOnboarding() {
    const navigate = useNavigate();
    const [step, setStep] = useState(1);

    const nextStep = () => {
        if (step === 3) {
            navigate('/scraper');
        } else {
            setStep(prev => prev + 1);
        }
    };

    return (
        <div className="min-h-screen bg-[#020202] text-white flex items-center justify-center relative overflow-hidden px-4">
            
            
            <div className="max-w-3xl w-full z-10">
                {/* Progress Grid */}
                <div className="grid grid-cols-3 gap-2 mb-12 opacity-50">
                    <div className={cn("h-1 rounded-full", step >= 1 ? "bg-brand-purple" : "bg-white/10")} />
                    <div className={cn("h-1 rounded-full", step >= 2 ? "bg-[#00f0ff]" : "bg-white/10")} />
                    <div className={cn("h-1 rounded-full", step >= 3 ? "bg-emerald-500" : "bg-white/10")} />
                </div>

                <div className="bg-[#111]/80 backdrop-blur-xl border border-white/10 rounded-3xl p-8 lg:p-12 shadow-2xl relative overflow-hidden">
                    {/* Decorative element */}
                    <div className="absolute top-0 right-0 w-64 h-64 bg-brand-purple/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
                    
                    {step === 1 && (
                        <div className="animate-in fade-in slide-in-from-right-8 duration-500">
                            <div className="w-16 h-16 bg-brand-purple/10 rounded-2xl flex items-center justify-center border border-brand-purple/20 mb-8">
                                <Bot className="w-8 h-8 text-brand-purple" />
                            </div>
                            <h1 className="text-4xl font-mono font-bold tracking-tight mb-4">
                                The Output Engine.
                            </h1>
                            <p className="text-xl text-gray-400 font-light mb-8 max-w-2xl leading-relaxed">
                                You are about to deploy the <span className="text-white font-mono tracking-widest text-sm">DEERFLOW_SCRAPER</span>. 
                                This tool is designed to traverse platforms, aggregate target profiles, and secure contact vectors entirely autonomously.
                            </p>
                            <div className="space-y-4 mb-10">
                                <div className="flex items-center text-sm font-mono text-gray-300">
                                    <CheckCircle2 className="w-5 h-5 text-brand-purple mr-3" /> Mass scale execution (Instagram, Twitter, TikTok)
                                </div>
                                <div className="flex items-center text-sm font-mono text-gray-300">
                                    <CheckCircle2 className="w-5 h-5 text-brand-purple mr-3" /> Automatic extraction of email vectors + engagement data
                                </div>
                            </div>
                        </div>
                    )}

                    {step === 2 && (
                        <div className="animate-in fade-in slide-in-from-right-8 duration-500">
                            <div className="w-16 h-16 bg-[#00f0ff]/10 rounded-2xl flex items-center justify-center border border-[#00f0ff]/20 mb-8">
                                <Shield className="w-8 h-8 text-[#00f0ff]" />
                            </div>
                            <h1 className="text-4xl font-mono font-bold tracking-tight mb-4">
                                Ghost Mode Enabled.
                            </h1>
                            <p className="text-xl text-gray-400 font-light mb-8 max-w-2xl leading-relaxed">
                                Behind the scenes, the system connects to the <span className="text-[#00f0ff]">Camoufox</span> Anti-Detect network. 
                                We simulate human pacing across proxy clusters to ensure 100% stealth.
                            </p>
                            <div className="bg-black/50 border border-white/5 rounded-xl p-6 font-mono text-sm space-y-3 mb-10 text-gray-400 relative overflow-hidden">
                                <div className="absolute top-0 right-0 p-4 opacity-10">
                                    <Server className="w-24 h-24" />
                                </div>
                                <p><span className="text-[#00f0ff]">&gt;</span> Bootstrapping 90 isolated browser instances...</p>
                                <p><span className="text-[#00f0ff]">&gt;</span> Injecting artificial WebGL fingerprints...</p>
                                <p><span className="text-[#00f0ff]">&gt;</span> Rotational sticky-proxies engaged.</p>
                                <p><span className="text-[#00f0ff]">&gt;</span> Evasion heuristics rated: AAA+++</p>
                            </div>
                        </div>
                    )}

                    {step === 3 && (
                        <div className="animate-in fade-in slide-in-from-right-8 duration-500">
                            <div className="w-16 h-16 bg-emerald-500/10 rounded-2xl flex items-center justify-center border border-emerald-500/20 mb-8">
                                <Globe className="w-8 h-8 text-emerald-500" />
                            </div>
                            <h1 className="text-4xl font-mono font-bold tracking-tight mb-4">
                                The Pact.
                            </h1>
                            <p className="text-xl text-gray-400 font-light mb-8 max-w-2xl leading-relaxed">
                                Scraping is hard, resource intensive, and requires constant warfare against platform defenses. 
                                By sharing your extracted targets with the <span className="text-emerald-400 font-bold">Global Pool</span>, you gain access to the collective database curated by all Momentaic operators.
                            </p>
                            <div className="p-6 bg-gradient-to-r from-emerald-500/10 to-transparent border border-emerald-500/20 rounded-xl mb-10">
                                <p className="text-emerald-400 font-mono text-sm leading-relaxed">
                                    "Provide 1 target, access 100,000."
                                    <br/><br/>
                                    You control exactly what you upload. Look for the 'SHARE TO GLOBAL COMMUNITY DB' switch before launching a job.
                                </p>
                            </div>
                        </div>
                    )}

                    <div className="flex justify-between items-center mt-4">
                        <button 
                            onClick={() => setStep(prev => Math.max(1, prev - 1))}
                            className={cn(
                                "text-gray-500 font-mono text-sm uppercase tracking-widest hover:text-white transition-colors",
                                step === 1 && "opacity-0 pointer-events-none"
                            )}
                        >
                            Back
                        </button>
                        
                        <button 
                            onClick={nextStep}
                            className="px-8 py-4 bg-white text-black font-mono font-bold text-sm tracking-widest uppercase hover:bg-gray-200 transition-colors rounded-xl flex items-center gap-2 group"
                        >
                            {step === 3 ? 'ENTER COMMAND CENTER' : 'PROCEED'}
                            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
