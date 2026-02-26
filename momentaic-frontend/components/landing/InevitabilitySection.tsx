import React, { useState, useEffect } from 'react';
import { cn } from '../../lib/utils';
import { Activity, Target, Zap, ShieldAlert, Cpu } from 'lucide-react';

export function InevitabilitySection() {
    const [scrolled, setScrolled] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            const element = document.getElementById('inevitability-section');
            if (element) {
                const rect = element.getBoundingClientRect();
                if (rect.top < window.innerHeight * 0.75) {
                    setScrolled(true);
                }
            }
        };
        window.addEventListener('scroll', handleScroll);
        // check initially
        handleScroll();
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    return (
        <section id="inevitability-section" className="relative py-32 px-6 overflow-hidden bg-[#020202] border-y border-white/5">
            {/* Background elements */}
            <div className="absolute inset-0 bg-tech-grid opacity-10 pointer-events-none" />
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] bg-red-900/5 blur-[120px] rounded-full mix-blend-screen pointer-events-none" />

            <div className="max-w-7xl mx-auto relative z-10">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">

                    {/* Left Narrative */}
                    <div className={cn(
                        "transition-all duration-1000 transform",
                        scrolled ? "opacity-100 translate-x-0" : "opacity-0 -translate-x-12"
                    )}>
                        <div className="flex items-center gap-2 mb-6">
                            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                            <span className="text-xs font-mono text-red-500 tracking-widest uppercase">The Efficiency Crisis</span>
                        </div>

                        <h2 className="text-4xl md:text-5xl lg:text-6xl font-black text-white leading-tight tracking-tighter mb-6">
                            The Pedigree Paradox is <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-500 to-purple-500">Over.</span>
                        </h2>

                        <p className="text-lg text-gray-400 font-mono leading-relaxed mb-8 border-l-2 border-red-500/30 pl-4">
                            The market overprices brand and underprices raw execution.
                            <br /><br />
                            Capital chases FAANG logos. We chase output.
                        </p>

                        <div className="bg-[#0a0a0f] border border-white/10 p-6 clip-corner-2 relative overflow-hidden group hover:border-purple-500/30 transition-colors">
                            <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/10 blur-2xl transform translate-x-16 -translate-y-16 group-hover:bg-purple-500/20 transition-colors" />
                            <h3 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
                                <Zap className="w-5 h-5 text-purple-400" />
                                The Inevitable Shift
                            </h3>
                            <p className="text-sm text-gray-400 font-mono">
                                Objective execution is the only signal. Scale output 100x, regardless of your resume.
                                <strong className="text-white block mt-2">Where AI Builds, Investigates, and Scales.</strong>
                            </p>
                        </div>
                    </div>

                    {/* Right Visual Data */}
                    <div className={cn(
                        "transition-all duration-1000 delay-300 transform",
                        scrolled ? "opacity-100 translate-y-0" : "opacity-0 translate-y-12"
                    )}>
                        <div className="relative bg-[#050508]/80 backdrop-blur-xl border border-white/10 p-8 rounded-2xl shadow-[0_0_50px_rgba(255,0,0,0.05)]">
                            <div className="absolute -top-3 -right-3 text-red-500/20"><ShieldAlert className="w-24 h-24" /></div>

                            <div className="flex justify-between items-end border-b border-white/10 pb-4 mb-6">
                                <div>
                                    <h4 className="text-white font-bold font-mono">Execution vs Pedigree</h4>
                                    <div className="text-[10px] text-gray-500 font-mono">LIVE_MARKET_ANALYSIS</div>
                                </div>
                                <div className="text-right">
                                    <div className="text-sm font-bold text-red-400">-35% Alpha</div>
                                    <div className="text-[10px] text-gray-500 font-mono">Inefficiency Gap</div>
                                </div>
                            </div>

                            {/* Chart Bar 1: Pedigree */}
                            <div className="mb-6">
                                <div className="flex justify-between text-xs font-mono mb-2">
                                    <span className="text-gray-400">Capital Allocated (Traditional)</span>
                                    <span className="text-red-400">80%</span>
                                </div>
                                <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden">
                                    <div className="h-full bg-red-500/50 w-[80%] relative">
                                        <div className="absolute inset-0 bg-[linear-gradient(45deg,transparent_25%,rgba(255,255,255,0.2)_50%,transparent_75%,transparent_100%)] bg-[length:20px_20px] animate-stripes" />
                                    </div>
                                </div>
                                <div className="flex justify-between text-xs font-mono mt-1">
                                    <span className="text-gray-500">Actual Output (Unicorns)</span>
                                    <span className="text-gray-400">50%</span>
                                </div>
                                <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden mt-1">
                                    <div className="h-full bg-gray-500 w-[50%]" />
                                </div>
                            </div>

                            {/* Chart Bar 2: Execution */}
                            <div className="mb-8">
                                <div className="flex justify-between text-xs font-mono mb-2">
                                    <span className="text-purple-400 flex items-center gap-1"><Target className="w-3 h-3" /> Velocity/Execution (The Signal)</span>
                                    <span className="text-green-400">+1.50x ROP</span>
                                </div>
                                <div className="h-3 w-full bg-white/5 rounded-full overflow-hidden shadow-[0_0_15px_rgba(168,85,247,0.3)]">
                                    <div className="h-full bg-gradient-to-r from-purple-600 to-pink-500 w-[95%] relative">
                                        <div className="absolute top-0 right-0 h-full w-20 bg-gradient-to-r from-transparent to-white/50 animate-glowX" />
                                    </div>
                                </div>
                            </div>

                            <div className="bg-black/50 border border-purple-500/20 p-4 rounded-lg flex items-start gap-3">
                                <Cpu className="w-5 h-5 text-purple-400 mt-0.5" />
                                <div>
                                    <div className="text-sm font-bold text-white">The Signal Engine</div>
                                    <div className="text-xs text-gray-400 font-mono mt-1">
                                        Ship code. Acquire users. Let metrics dictate valuation.
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                </div>
            </div>
        </section>
    );
}
