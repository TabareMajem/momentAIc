import React, { useState, useEffect } from 'react';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Input } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';
import { cn } from '../lib/utils';
import { Activity, ArrowRight, BookOpen, ChevronRight, Cpu, Globe, Send, Shield, Sparkles, Target, Terminal, TrendingUp, Zap } from 'lucide-react';

export default function InvestorDeck() {
    const [scrolled, setScrolled] = useState(false);

    // Terminal Form State
    const [terminalOutput, setTerminalOutput] = useState<string[]>([
        "> SECURE_CONNECTION_ESTABLISHED",
        "> INITIALIZING_QUANTITATIVE_PROPOSAL_V1.4",
        "> AWAITING_LP_INPUT..."
    ]);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [formData, setFormData] = useState({ name: '', entity: '', amount: '' });

    useEffect(() => {
        const handleScroll = () => setScrolled(window.scrollY > 50);
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const handleCommit = (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);

        const sequence = [
            `> PROCESSING_CAPITAL_COMMITMENT: $${formData.amount}`,
            `> VERIFYING_ENTITY: ${formData.entity}`,
            `> GENERATING_SECURE_CONTRACT...`,
            `> DISPATCHING_TO_ARCHITECT (tabaremajem@gmail.com)`,
            `> SUCCESS: AWAITING_COUNTERSIGNATURE.`
        ];

        let i = 0;
        const interval = setInterval(() => {
            if (i < sequence.length) {
                setTerminalOutput(prev => [...prev, sequence[i]]);
                i++;
            } else {
                clearInterval(interval);
                // Trigger actual mailto after animation
                window.location.href = `mailto:tabaremajem@gmail.com?subject=Genesis Fund I Commitment: ${formData.entity}&body=Name: ${formData.name}%0AEntity: ${formData.entity}%0ACommitted Amount: $${formData.amount}%0A%0AWe are ready to initiate the investment protocol.`;
                setIsSubmitting(false);
            }
        }, 800);
    };

    return (
        <div className="min-h-screen bg-[#020202] text-white font-sans selection:bg-red-500 text-selection-white overflow-x-hidden">
            {/* ─── GLOBAL OVERLAYS ─── */}
            <div className="fixed inset-0 pointer-events-none z-50 bg-transparent opacity-[0.03] mix-blend-overlay" />
            <div className="fixed inset-0 bg-tech-grid opacity-20 pointer-events-none z-0" />

            {/* ─── HERO SECION (The Genesis Fund I) ─── */}
            <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-20 border-b border-white/5">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-4xl h-[500px] bg-red-900/10 blur-[150px] rounded-full mix-blend-screen pointer-events-none z-0" />

                <div className="relative z-10 text-center px-6 max-w-5xl mx-auto flex flex-col items-center">
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-red-500/40 bg-red-500/10 text-red-200 font-mono text-xs mb-8 animate-fade-in-up backdrop-blur-md">
                        <Terminal className="w-3.5 h-3.5 text-red-400" />
                        <span>QUANTITATIVE VENTURE CAPITAL • FUND I</span>
                    </div>

                    <h1 className="text-5xl sm:text-7xl md:text-8xl font-black text-white tracking-tighter mb-6 leading-tight animate-fade-in-up delay-[100ms] uppercase">
                        The Genesis <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-500 via-pink-500 to-purple-500">Fund</span>
                    </h1>

                    <p className="text-xl md:text-3xl text-gray-400 max-w-3xl mx-auto mb-12 font-mono leading-relaxed animate-fade-in-up delay-[200ms]">
                        Target Raise: <strong className="text-white">$300,000 USD</strong>
                        <br />
                        <span className="text-sm mt-4 block text-gray-500">The first AI-native index fund securing deep equity in the top 1% of global builders.</span>
                    </p>

                    <div className="flex flex-col sm:flex-row items-center justify-center gap-6 animate-fade-in-up delay-[400ms]">
                        <button onClick={() => document.getElementById('allocation')?.scrollIntoView({ behavior: 'smooth' })} className="h-14 px-8 text-sm font-bold font-mono bg-white text-black hover:bg-red-600 hover:text-white transition-all clip-corner-4 shadow-[0_0_40px_rgba(255,0,0,0.15)] flex items-center gap-2">
                            VIEW PROPOSAL <ArrowRight className="w-4 h-4" />
                        </button>
                        <button onClick={() => document.getElementById('commit-terminal')?.scrollIntoView({ behavior: 'smooth' })} className="h-14 px-8 text-sm font-mono text-gray-300 border border-white/10 hover:border-red-500/50 hover:text-red-400 bg-black/50 transition-all clip-corner-4 flex items-center gap-2">
                            <Zap className="w-4 h-4" /> COMMIT CAPITAL
                        </button>
                    </div>
                </div>

                {/* Data Scroll */}
                <div className="absolute bottom-0 left-0 w-full h-12 bg-black/80 border-t border-red-900/30 flex items-center overflow-hidden z-20">
                    <div className="flex animate-marquee whitespace-nowrap gap-12 text-[10px] font-mono tracking-widest text-red-400/80">
                        {Array(8).fill("SYSTEM_THESIS: PEDIGREE IS DEAD. EXECUTION DEMANDS EQUITY. // ALGORITHM OF ALPHA ONLINE.").map((t, i) => <span key={i}>{t}</span>)}
                    </div>
                </div>
            </section>

            {/* ─── THE ALPHA THESIS ─── */}
            <section className="py-32 px-6 relative bg-[#050508] border-b border-white/5">
                <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
                    <div>
                        <h2 className="text-4xl md:text-5xl font-black text-white mb-6 tracking-tighter uppercase">Information Asymmetry</h2>
                        <div className="text-lg text-gray-400 font-mono leading-relaxed space-y-6">
                            <p>
                                Traditional Venture Capital is suffering an efficiency crisis. It relies on <strong>subjective heuristic signals</strong> (like Ivy League pedigree or warm introductions) to allocate capital.
                            </p>
                            <p className="border-l-2 border-purple-500 pl-4 text-white font-bold">
                                The result is a negative Return on Pedigree (ROP). The market overprices the brand and underprices raw execution.
                            </p>
                            <p>
                                MomentAIc is not just a software company; it is the <strong>Signal Engine</strong>. By providing founders with an Autonomous Business OS to build their companies, we gain proprietary, real-time observability into their execution velocity, capital efficiency, and product-market fit.
                            </p>
                        </div>
                    </div>

                    <div className="relative">
                        <div className="absolute inset-0 bg-gradient-to-tr from-purple-900/20 to-red-900/20 blur-3xl rounded-full" />
                        <Card className="relative p-8 bg-black/60 border-white/10 backdrop-blur-md overflow-hidden">
                            <div className="flex justify-between items-center mb-8 border-b border-white/10 pb-4">
                                <span className="font-mono text-xs text-gray-500 uppercase">Legacy VC vs Signal Engine</span>
                                <Badge variant="cyber" className="bg-red-500/10 text-red-400 border-red-500/30">ALPHA DETECTED</Badge>
                            </div>

                            <div className="space-y-6">
                                <div>
                                    <div className="flex justify-between text-xs font-mono mb-2">
                                        <span className="text-gray-500">Public Market Signals (Pitch Decks, LinkedIn)</span>
                                        <span className="text-red-400">Lagging Indicator</span>
                                    </div>
                                    <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden"><div className="h-full bg-red-500/40 w-[30%]" /></div>
                                </div>
                                <div>
                                    <div className="flex justify-between text-xs font-mono mb-2">
                                        <span className="text-white flex items-center gap-1"><Activity className="w-3 h-3 text-purple-400" /> Code Velocity & Agent Usage</span>
                                        <span className="text-purple-400">Proprietary Leading Indicator</span>
                                    </div>
                                    <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden shadow-[0_0_15px_rgba(168,85,247,0.2)]"><div className="h-full bg-gradient-to-r from-purple-600 to-pink-500 w-[95%]" /></div>
                                </div>
                            </div>
                        </Card>
                    </div>
                </div>
            </section>

            {/* ─── CAPITAL ALLOCATION (TRANCHE 1) ─── */}
            <section id="allocation" className="py-32 px-6 relative bg-[#020202]">
                <div className="max-w-7xl mx-auto text-center mb-20">
                    <div className="text-[10px] font-mono text-purple-400 tracking-[0.3em] mb-3">FINANCIAL_ARCHITECTURE</div>
                    <h2 className="text-4xl md:text-5xl font-black text-white uppercase tracking-tighter">The $300k Allocation Model</h2>
                    <p className="mt-4 text-gray-400 font-mono text-sm max-w-2xl mx-auto">
                        We are raising $300,000 USD to ignite the flywheel. This capital is deployed systematically to capture the most undervalued asset in the market: top-decile global builders.
                    </p>
                </div>

                <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6">
                    {/* 60% Reinvestment */}
                    <Card className="col-span-1 md:col-span-3 lg:col-span-2 p-8 bg-[#0a0a0f]/60 backdrop-blur-xl border-purple-500/30 clip-corner-4 relative group overflow-hidden hover:border-purple-500 transition-colors">
                        <div className="absolute top-0 right-0 w-64 h-64 bg-purple-500/5 rounded-full blur-3xl group-hover:bg-purple-500/10 transition-colors" />
                        <div className="flex justify-between items-start mb-6 align-top">
                            <div>
                                <div className="text-4xl font-black text-white mb-1">60%</div>
                                <div className="text-xs font-mono text-purple-400">$180,000 USD</div>
                            </div>
                            <div className="p-3 bg-purple-500/10 rounded-lg border border-purple-500/20 text-purple-400">
                                <TrendingUp className="w-6 h-6" />
                            </div>
                        </div>
                        <h3 className="text-2xl font-bold text-white mb-4 uppercase">Algorithmic Reinvestment</h3>
                        <p className="text-sm text-gray-400 font-mono leading-relaxed mb-6">
                            The core thesis. 60% of raised capital is injected directly back into the top 1% of founders actively building on MomentAIc. We identify them via their "Signal Score" (live execution metrics) and deploy non-predatory capital in exchange for aggressive, inception-stage equity (targeting 51%).
                        </p>
                        <div className="bg-black/50 border border-white/5 p-4 rounded text-xs font-mono text-gray-300">
                            <strong>Mechanism:</strong> Convert software users into portfolio companies before traditional VCs even know they exist. We become the co-founder and the capital allocator simultaneously.
                        </div>
                    </Card>

                    <div className="flex flex-col gap-6">
                        {/* 30% Marketing */}
                        <Card className="p-8 bg-black/40 border-white/10 clip-corner-2 hover:border-pink-500/30 transition-colors">
                            <div className="flex justify-between items-start mb-4">
                                <div>
                                    <div className="text-3xl font-black text-white mb-1">30%</div>
                                    <div className="text-[10px] font-mono text-gray-500">$90,000 USD</div>
                                </div>
                                <Target className="w-5 h-5 text-gray-500" />
                            </div>
                            <h3 className="text-lg font-bold text-white mb-2 uppercase">Network Expansion</h3>
                            <p className="text-xs text-gray-400 font-mono leading-relaxed">
                                Feeding the top of the funnel. Aggressive marketing and ambassador programs to acquire thousands of founders onto the OS, enriching the dataset for the Signal Engine.
                            </p>
                        </Card>

                        {/* 10% Operations */}
                        <Card className="p-8 bg-black/40 border-white/10 clip-corner-2 hover:border-green-500/30 transition-colors">
                            <div className="flex justify-between items-start mb-4">
                                <div>
                                    <div className="text-3xl font-black text-white mb-1">10%</div>
                                    <div className="text-[10px] font-mono text-gray-500">$30,000 USD</div>
                                </div>
                                <Cpu className="w-5 h-5 text-gray-500" />
                            </div>
                            <h3 className="text-lg font-bold text-white mb-2 uppercase">Infrastructure Ops</h3>
                            <p className="text-xs text-gray-400 font-mono leading-relaxed">
                                Maintenance of the core Autonomous OS, LLM API overhead, and database scaling to support the swarm of agents operating 24/7.
                            </p>
                        </Card>
                    </div>
                </div>
            </section>

            {/* ─── THE ARCHITECT & THE ASSET ─── */}
            <section className="py-32 px-6 bg-gradient-to-b from-[#020202] to-[#05000a] border-t border-white/5">
                <div className="max-w-5xl mx-auto flex flex-col md:flex-row gap-12 items-center bg-[#0a0a0f]/80 backdrop-blur-xl border border-white/10 p-8 lg:p-12 clip-corner-4 relative">
                    <div className="absolute -top-4 -left-4 w-12 h-12 border-t-2 border-l-2 border-red-500/50" />
                    <div className="absolute -bottom-4 -right-4 w-12 h-12 border-b-2 border-r-2 border-red-500/50" />

                    <div className="w-full md:w-1/3">
                        <div className="aspect-square bg-black border border-white/10 p-2 overflow-hidden relative group cursor-pointer">
                            <div className="absolute inset-0 bg-red-500/10 mix-blend-overlay group-hover:bg-transparent transition-colors z-10 pointer-events-none" />
                            {/* Visual representation of Founder or Tech */}
                            <img
                                src="https://media.licdn.com/dms/image/v2/D4D03AQGLd1zL1T7z5w/profile-displayphoto-shrink_800_800/profile-displayphoto-shrink_800_800/0/1714574921966?e=1745452800&v=beta&t=Zk4aZ6S8M5x-W1I_r"
                                alt="Tabaré Majem"
                                className="w-full h-full object-cover grayscale group-hover:grayscale-0 transition-all duration-500"
                                onError={(e) => {
                                    // Fallback if linkedin blocks hotlinking
                                    (e.target as HTMLImageElement).src = 'https://ui-avatars.com/api/?name=Tabare+Majem&background=random&size=800';
                                }}
                            />
                            <div className="absolute bottom-4 left-4 right-4 bg-black/90 backdrop-blur border border-white/10 p-3 z-20">
                                <div className="text-xs font-mono text-red-400 mb-1">THE ARCHITECT</div>
                                <div className="text-lg font-bold text-white uppercase tracking-wider">Tabaré Majem</div>
                            </div>
                        </div>
                    </div>

                    <div className="w-full md:w-2/3 space-y-6">
                        <h2 className="text-3xl lg:text-4xl font-black text-white uppercase tracking-tighter">Invest in the Tech. <br />Invest in the Maker.</h2>
                        <p className="text-gray-400 font-mono text-sm leading-relaxed">
                            MomentAIc is built to be the central nervous system for the next generation of digital enterprise.
                            The technology—a swarm of 50+ autonomous agents orchestrated via a unified OS—is the ultimate moat.
                            <br /><br />
                            We are not seeking passive capital. We are opening an allocation for visionaries who understand that the future of venture capital relies on quantitative execution, not country_club pedigree.
                        </p>

                        <div className="pt-4 flex items-center gap-4">
                            <a href="https://www.linkedin.com/in/tabaremajem/" target="_blank" rel="noopener noreferrer">
                                <Button variant="outline" className="text-xs font-mono">
                                    <Globe className="w-4 h-4 mr-2" /> VERIFY FOUNDER INTEL
                                </Button>
                            </a>
                            <Link to="/research">
                                <Button variant="ghost" className="text-xs font-mono text-gray-500 hover:text-white">
                                    <BookOpen className="w-4 h-4 mr-2" /> READ THE ALGORITHM OF ALPHA
                                </Button>
                            </Link>
                        </div>
                    </div>
                </div>
            </section>

            {/* ─── COMMITMENT TERMINAL ─── */}
            <section id="commit-terminal" className="py-32 px-6 bg-[#000] relative border-t border-purple-900/30">
                <div className="max-w-4xl mx-auto">
                    <div className="bg-[#050508] border border-red-500/30 rounded-lg overflow-hidden shadow-[0_0_80px_rgba(255,0,0,0.1)]">
                        {/* Terminal Header */}
                        <div className="bg-[#0a0a0a] border-b border-white/10 px-4 py-3 flex items-center gap-4">
                            <div className="flex gap-2">
                                <div className="w-3 h-3 rounded-full bg-red-500" />
                                <div className="w-3 h-3 rounded-full bg-yellow-500" />
                                <div className="w-3 h-3 rounded-full bg-green-500" />
                            </div>
                            <div className="text-[10px] font-mono text-gray-500 tracking-widest">SECURE_COMMIT_PROTOCOL_v1.0</div>
                        </div>

                        <div className="flex flex-col md:flex-row">
                            {/* Left: Logs */}
                            <div className="w-full md:w-1/2 p-6 border-r border-white/5 bg-black font-mono text-[10px] sm:text-xs">
                                <div className="text-red-400 mb-4 tracking-wider">SYSTEM LOGS</div>
                                <div className="space-y-2 text-gray-400 h-64 overflow-y-auto">
                                    {terminalOutput.map((log, i) => (
                                        <div key={i} className={cn("animate-fade-in", log.includes('SUCCESS') ? "text-green-400" : "")}>
                                            {log}
                                        </div>
                                    ))}
                                    {isSubmitting && <div className="animate-pulse text-purple-400">&gt; _</div>}
                                </div>
                            </div>

                            {/* Right: Input Form */}
                            <div className="w-full md:w-1/2 p-6 bg-[#050508]">
                                <h3 className="text-xl font-bold text-white mb-6 uppercase">Initiate Wire Protocol</h3>
                                <form onSubmit={handleCommit} className="space-y-4">
                                    <div>
                                        <label className="text-[10px] font-mono text-gray-500 uppercase tracking-widest block mb-2">Lead Investor / Partner Name</label>
                                        <input
                                            type="text"
                                            required
                                            disabled={isSubmitting}
                                            value={formData.name}
                                            onChange={e => setFormData({ ...formData, name: e.target.value })}
                                            className="w-full bg-black border border-white/10 rounded px-4 py-3 text-sm text-white font-mono focus:border-red-500 outline-none transition-colors"
                                            placeholder="John Doe"
                                        />
                                    </div>
                                    <div>
                                        <label className="text-[10px] font-mono text-gray-500 uppercase tracking-widest block mb-2">Entity / Fund Name</label>
                                        <input
                                            type="text"
                                            required
                                            disabled={isSubmitting}
                                            value={formData.entity}
                                            onChange={e => setFormData({ ...formData, entity: e.target.value })}
                                            className="w-full bg-black border border-white/10 rounded px-4 py-3 text-sm text-white font-mono focus:border-red-500 outline-none transition-colors"
                                            placeholder="Alpha Ventures LP"
                                        />
                                    </div>
                                    <div>
                                        <label className="text-[10px] font-mono text-gray-500 uppercase tracking-widest block mb-2">Target Commitment (USD)</label>
                                        <input
                                            type="number"
                                            required
                                            disabled={isSubmitting}
                                            value={formData.amount}
                                            onChange={e => setFormData({ ...formData, amount: e.target.value })}
                                            className="w-full bg-black border border-white/10 rounded px-4 py-3 text-sm text-white font-mono focus:border-red-500 outline-none transition-colors"
                                            placeholder="e.g. 50000"
                                            min="10000"
                                            step="5000"
                                        />
                                    </div>

                                    <Button
                                        type="submit"
                                        disabled={isSubmitting}
                                        className="w-full h-12 mt-4 bg-red-600 hover:bg-red-500 text-white font-bold font-mono text-xs uppercase tracking-widest shadow-[0_0_20px_rgba(220,38,38,0.3)] transition-all"
                                    >
                                        {isSubmitting ? 'ENCRYPTING... ' : 'CONFIRM COMMITMENT'}
                                        {!isSubmitting && <Send className="w-4 h-4 ml-2" />}
                                    </Button>
                                    <p className="text-[9px] font-mono text-gray-500 text-center mt-4">
                                        By committing, you authorize secure transmittal of intent directly to tabaremajem@gmail.com.
                                    </p>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
}
