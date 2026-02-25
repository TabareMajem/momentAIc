import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { cn } from '../lib/utils';
import {
    Activity, ArrowRight, BookOpen, Brain, ChevronRight, Code2,
    Cpu, DollarSign, Globe, Layers, Lock, Send, Shield, Sparkles,
    Target, Terminal, TrendingUp, Users, Zap, AlertTriangle,
    BarChart2, GitBranch, Rocket, Eye
} from 'lucide-react';

// ─── DATA ────────────────────────────────────────────
const MARKET_STATS = [
    { value: "$780B", label: "Global SaaS Market (2025)" },
    { value: "11,000+", label: "SaaS Tools Per Enterprise" },
    { value: "68%", label: "Founders Overwhelmed by Ops" },
    { value: "$4.2T", label: "Lost Productivity Annually" },
];

const AGENT_ROSTER = [
    { name: "CFO Agent", role: "Financial Modeling & Burn Analysis", active: true },
    { name: "SDR Hunter", role: "Autonomous Lead Acquisition 24/7", active: true },
    { name: "Legal Counsel", role: "Contract Review & Compliance", active: true },
    { name: "Growth Hacker", role: "Viral Campaign Engineering", active: true },
    { name: "Reddit Sniper", role: "Community Sentiment & Infiltration", active: true },
    { name: "Character Factory", role: "AI Persona & Influencer Deployment", active: true },
    { name: "Data Analyst", role: "Signal Scoring & PMF Detection", active: true },
    { name: "Community Agent", role: "Audience Building & Retention", active: true },
    { name: "Competitor Intel", role: "Rival Monitoring & Counterplay", active: false },
    { name: "PR Architect", role: "Story Engineering & Press Coverage", active: false },
    { name: "HR Recruiter", role: "Talent Scoring & Pipeline", active: false },
    { name: "Fundraising Coach", role: "Investor Narrative Construction", active: false },
];

const THESIS_PILLARS = [
    {
        icon: Eye,
        title: "Proprietary Signal Intelligence",
        body: "Every action on MomentAIc generates real-time behavioral data — commit frequency, campaign conversion rates, agent utilization depth. We own the most granular founder execution dataset on Earth.",
        metric: "100ms", metricLabel: "Signal Refresh Rate"
    },
    {
        icon: Brain,
        title: "The Autonomous Business OS",
        body: "50+ specialized AI agents that don't just advise — they execute. Your SDR fires outbound email sequences at 3am. Your CFO models next quarter's burn while you sleep. Your PR Agent pitches journalists autonomously.",
        metric: "50+", metricLabel: "Specialized Neural Agents"
    },
    {
        icon: TrendingUp,
        title: "Convert Users → Portfolio Companies",
        body: "The kill move: we identify the top 1% of builders by Signal Score and deploy non-predatory capital in exchange for inception-stage equity. We become a co-founder BEFORE traditional VCs see the pitch deck.",
        metric: "51%", metricLabel: "Target Equity Threshold"
    },
    {
        icon: Layers,
        title: "Infinite Flywheel Economics",
        body: "More users = richer Signal Engine = better alpha = stronger portfolio = more press = more users. The system compounds on itself. Every new founder is both a customer AND a potential portfolio asset.",
        metric: "K>1", metricLabel: "Target Viral Coefficient"
    }
];

const ALLOCATION = [
    { pct: 60, usd: "$180,000", label: "Algorithmic Reinvestment", color: "from-purple-600 to-pink-600", desc: "Direct capital deployment into top-1% founders via Signal Score. We co-invest before Series A framing exists." },
    { pct: 30, usd: "$90,000", label: "Swarm Acquisition Engine", color: "from-blue-600 to-cyan-500", desc: "Fueling the Hourly Hunters, Character Factory offensive, and Ambassador network to flood the top of funnel." },
    { pct: 10, usd: "$30,000", label: "Infrastructure Supremacy", color: "from-green-600 to-emerald-400", desc: "LLM API overhead, VPS hardening, database scaling, and agent orchestration layer to run 24/7 zero-downtime." },
];

const COMPETITIVE_MOAT = [
    { label: "Notion", category: "Docs", has: false },
    { label: "HubSpot", category: "CRM", has: false },
    { label: "Linear", category: "Projects", has: false },
    { label: "Zapier", category: "Automation", has: false },
    { label: "Clay", category: "Enrichment", has: false },
    { label: "MomentAIc", category: "Autonomous OS", has: true },
];

const MILESTONES = [
    { q: "Q1 2025", title: "Core OS Built", done: true, desc: "50+ agents deployed. War Room live. Scheduler active." },
    { q: "Q2 2025", title: "Genesis Launch", done: true, desc: "Public launch. Ambassador program. First revenue." },
    { q: "Q3 2025", title: "Signal Engine v2", done: false, desc: "PMF scoring, Signal Score leaderboard, co-invest protocol live." },
    { q: "Q4 2025", title: "Fund I Close", done: false, desc: "$300K deployed. First portfolio companies identified. Series A scouting." },
    { q: "Q1 2026", title: "Agency OS Pivot", done: false, desc: "White-label product for agencies managing 100+ brands via Matrix Control." },
    { q: "Q3 2026", title: "Series A / Fund II", done: false, desc: "Raise $3M Fund II. Portfolio IRR data visible. LP syndicate expanded." },
];

// ─── ANIMATED COUNTER ────────────────────────────────
function AnimatedNumber({ value, suffix = "" }: { value: number; suffix?: string }) {
    const [display, setDisplay] = useState(0);
    const ref = useRef<HTMLSpanElement>(null);
    useEffect(() => {
        const observer = new IntersectionObserver(([entry]) => {
            if (entry.isIntersecting) {
                let start = 0;
                const step = value / 60;
                const timer = setInterval(() => {
                    start += step;
                    if (start >= value) { setDisplay(value); clearInterval(timer); }
                    else setDisplay(Math.floor(start));
                }, 16);
                observer.disconnect();
            }
        }, { threshold: 0.5 });
        if (ref.current) observer.observe(ref.current);
        return () => observer.disconnect();
    }, [value]);
    return <span ref={ref}>{display.toLocaleString()}{suffix}</span>;
}

// ─── MAIN COMPONENT ──────────────────────────────────
export default function InvestorDeck() {
    const [terminalOutput, setTerminalOutput] = useState<string[]>([
        "> GENESIS_FUND_I :: SECURE_CHANNEL_ESTABLISHED",
        "> LOADING_SIGNAL_ENGINE_v2.4...",
        "> VERIFYING_LP_CLEARANCE...",
        "> STATUS: OPEN_FOR_COMMITMENTS"
    ]);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [submitted, setSubmitted] = useState(false);
    const [formData, setFormData] = useState({ name: '', entity: '', email: '', amount: '' });
    const [activeAgent, setActiveAgent] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => setActiveAgent(a => (a + 1) % AGENT_ROSTER.length), 1800);
        return () => clearInterval(interval);
    }, []);

    const handleCommit = (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);
        const sequence = [
            `> PROCESSING: ${formData.name} @ ${formData.entity}`,
            `> COMMITMENT_VALUE: $${Number(formData.amount).toLocaleString()} USD`,
            `> ENCRYPTING_PAYLOAD... [AES-256]`,
            `> ROUTING: tabaremajem@gmail.com`,
            `> GENERATING_TERM_SHEET_DRAFT...`,
            `> SUCCESS: COMMITMENT_LOGGED. COUNTERSIGNATURE_PENDING.`
        ];
        let i = 0;
        const iv = setInterval(() => {
            if (i < sequence.length) { setTerminalOutput(prev => [...prev, sequence[i]]); i++; }
            else {
                clearInterval(iv);
                setIsSubmitting(false);
                setSubmitted(true);
                window.location.href = `mailto:tabaremajem@gmail.com?subject=Genesis Fund I — Commitment: ${formData.entity}&body=Name: ${formData.name}%0AEntity: ${formData.entity}%0AEmail: ${formData.email}%0ACommitment: $${formData.amount}%0A%0AReady to proceed with the investment protocol.`;
            }
        }, 700);
    };

    return (
        <div className="min-h-screen bg-[#020202] text-white overflow-x-hidden selection:bg-red-500/40">

            {/* ── FIXED GRID OVERLAY ── */}
            <div className="fixed inset-0 pointer-events-none z-0"
                style={{ backgroundImage: 'linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)', backgroundSize: '60px 60px' }} />

            {/* ── NAV ── */}
            <nav className="fixed top-0 left-0 right-0 z-50 bg-black/80 backdrop-blur-xl border-b border-white/5">
                <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-4">
                    <div className="flex items-center gap-3">
                        <div className="w-6 h-6 bg-gradient-to-br from-red-500 to-purple-600 rounded-sm" />
                        <span className="font-mono text-xs tracking-[0.2em] text-gray-400 uppercase">MomentAIc / Genesis Fund I</span>
                    </div>
                    <div className="flex items-center gap-4">
                        <span className="hidden sm:flex items-center gap-2 text-[10px] font-mono text-green-400 tracking-widest">
                            <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" /> LIVE
                        </span>
                        <button
                            onClick={() => document.getElementById('commit-terminal')?.scrollIntoView({ behavior: 'smooth' })}
                            className="text-[10px] font-mono font-bold tracking-[0.2em] text-black bg-white hover:bg-red-500 hover:text-white transition-colors px-4 py-2 uppercase"
                        >
                            Commit Capital
                        </button>
                    </div>
                </div>
            </nav>

            {/* ══════════════════════════════════ */}
            {/* ── 1. HERO ──────────────────────── */}
            {/* ══════════════════════════════════ */}
            <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-24">
                {/* Massive Cyberpunk Glows */}
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1200px] h-[800px] bg-red-900/10 blur-[200px] rounded-full pointer-events-none mix-blend-screen" />
                <div className="absolute top-1/3 right-1/4 w-[600px] h-[600px] bg-purple-900/15 blur-[150px] rounded-full pointer-events-none mix-blend-screen" />
                <div className="absolute bottom-0 left-1/4 w-[800px] h-[400px] bg-pink-900/10 blur-[150px] rounded-full pointer-events-none mix-blend-screen" />

                <div className="relative z-10 text-center px-6 max-w-6xl mx-auto">
                    <div className="inline-flex items-center gap-2 px-5 py-2.5 bg-red-500/10 border border-red-500/50 text-red-400 font-mono text-[10px] sm:text-xs mb-10 tracking-[0.4em] uppercase backdrop-blur-md shadow-[0_0_30px_rgba(220,38,38,0.2)]">
                        <Terminal className="w-3 h-3.5 text-red-400 animate-pulse" />
                        System Status: Inevitable · Genesis Fund I · $300,000 USD
                    </div>

                    <h1 className="text-6xl sm:text-8xl md:text-[110px] font-black text-white tracking-[-0.05em] mb-6 leading-[0.85] uppercase drop-shadow-2xl">
                        Vibe Coding the<br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-500 via-pink-400 to-purple-500 animate-pulse">
                            Inevitability.
                        </span>
                    </h1>

                    <p className="text-xl md:text-3xl text-gray-300 max-w-4xl mx-auto mb-6 font-mono leading-relaxed font-semibold">
                        We didn't just build an <strong className="text-white drop-shadow-[0_0_10px_rgba(255,255,255,0.5)]">Autonomous Business OS</strong>.<br />
                        We built the <strong className="text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-yellow-400">Signal Engine</strong> that detects the top 1% of founders before anyone else.
                    </p>
                    <p className="text-sm md:text-base text-gray-500 font-mono mb-14 max-w-2xl mx-auto">
                        Pedigree is dead. Execution is the only metric that matters. Watch it happen in real-time, co-invest at inception. This is the <span className="text-white font-bold underline decoration-red-500/50 underline-offset-4">Algorithm of Alpha.</span>
                    </p>

                    <div className="flex flex-col sm:flex-row items-center justify-center gap-6">
                        <button
                            onClick={() => document.getElementById('thesis')?.scrollIntoView({ behavior: 'smooth' })}
                            className="h-16 px-12 text-sm font-black font-mono bg-white text-black hover:bg-black hover:text-white border-2 border-transparent hover:border-white transition-all flex items-center justify-center gap-3 uppercase tracking-widest shadow-[0_0_80px_rgba(255,255,255,0.2)] hover:shadow-[0_0_100px_rgba(255,255,255,0.4)] relative group overflow-hidden"
                        >
                            <span className="relative z-10 flex items-center gap-2">Read the Thesis <ArrowRight className="w-4 h-4 group-hover:translate-x-2 transition-transform" /></span>
                            <div className="absolute inset-0 bg-red-600 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out" />
                        </button>
                        <button
                            onClick={() => document.getElementById('commit-terminal')?.scrollIntoView({ behavior: 'smooth' })}
                            className="h-16 px-12 text-sm font-mono text-gray-300 border-2 border-red-500/30 hover:border-red-500 hover:bg-red-500/10 hover:text-white transition-all flex items-center justify-center gap-3 uppercase tracking-widest shadow-[inset_0_0_20px_rgba(220,38,38,0)] hover:shadow-[inset_0_0_40px_rgba(220,38,38,0.2)]"
                        >
                            <Zap className="w-5 h-5 text-red-500 animate-pulse" /> Commit Capital
                        </button>
                    </div>

                    {/* Market Stats Row */}
                    <div className="mt-28 grid grid-cols-2 md:grid-cols-4 gap-px bg-white/5 border border-white/10 backdrop-blur-xl shadow-2xl relative">
                        <div className="absolute -inset-0.5 bg-gradient-to-r from-red-500 to-purple-500 opacity-20 blur-xl z-[-1]" />
                        {MARKET_STATS.map((s, i) => (
                            <div key={i} className="bg-black/80 p-8 text-center hover:bg-red-950/20 transition-colors duration-500 group">
                                <div className="text-3xl md:text-5xl font-black text-white mb-2 group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-b group-hover:from-white group-hover:to-red-400 transition-all">{s.value}</div>
                                <div className="text-[10px] md:text-xs font-mono text-gray-500 uppercase tracking-[0.2em] group-hover:text-red-300 transition-colors">{s.label}</div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Bottom ticker */}
                <div className="absolute bottom-0 left-0 right-0 h-10 bg-red-950/30 border-t border-red-900/20 flex items-center overflow-hidden">
                    <div className="flex animate-marquee whitespace-nowrap gap-16 text-[10px] font-mono tracking-[0.25em] text-red-400/60">
                        {Array(10).fill("PEDIGREE_IS_DEAD // EXECUTION_DEMANDS_EQUITY // ALGORITHM_OF_ALPHA_ONLINE // SIGNAL_ENGINE_V2_ACTIVE // GENESIS_FUND_I_OPEN //").map((t, i) => <span key={i}>{t}</span>)}
                    </div>
                </div>
            </section>

            {/* ══════════════════════════════════ */}
            {/* ── 2. THE INEVITABLE COLLAPSE ───── */}
            {/* ══════════════════════════════════ */}
            <section className="py-32 px-6 bg-[#040407] border-t border-white/5 relative overflow-hidden">
                <div className="absolute right-0 top-0 w-1/2 h-full opacity-10 pointer-events-none mix-blend-screen"
                    style={{ background: 'radial-gradient(circle at 80% 50%, #ff0000 0%, transparent 60%)' }} />
                <div className="absolute left-0 bottom-0 w-1/3 h-1/2 opacity-5 pointer-events-none mix-blend-screen"
                    style={{ background: 'radial-gradient(circle at 20% 80%, #a855f7 0%, transparent 70%)' }} />
                <div className="max-w-5xl mx-auto relative z-10">
                    <div className="inline-block border border-red-500/30 bg-red-500/10 text-red-400 px-3 py-1 font-mono text-[10px] tracking-[0.4em] mb-6 uppercase">Phase 1: The Collapse</div>
                    <h2 className="text-5xl md:text-7xl font-black text-white uppercase tracking-tighter mb-12 leading-[0.85]">
                        SaaS is <span className="text-red-600 line-through decoration-white/50">Obsolete.</span><br />
                        <span className="text-gray-500 text-3xl md:text-5xl">Drowning in tools is a choice.</span>
                    </h2>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-px bg-white/5">
                        {[
                            {
                                icon: AlertTriangle, color: "text-red-400",
                                title: "Tool Sprawl",
                                body: "The average funded startup runs 11+ SaaS tools: CRM, ATS, Marketing Automation, Analytics, PM — all requiring constant human babysitting.",
                                stat: "11,000+", statLabel: "SaaS tools per enterprise"
                            },
                            {
                                icon: DollarSign, color: "text-yellow-400",
                                title: "Capital Misallocation",
                                body: "Traditional VC bets on Ivy League credentials and warm intros. Returns suffer. The best builders — scrappy, global, relentless — are invisible to Sand Hill Road.",
                                stat: "85%", statLabel: "VC-backed startups fail"
                            },
                            {
                                icon: Users, color: "text-purple-400",
                                title: "Execution Bandwidth",
                                body: "A solo founder needs a CFO, SDR, lawyer, marketer, and data scientist on day one. They can't afford them. They burn out and die before product-market fit.",
                                stat: "68%", statLabel: "founders overwhelmed by ops"
                            }
                        ].map((item, i) => (
                            <div key={i} className="bg-[#020202] p-8 border border-white/5 hover:border-red-500/30 transition-colors group relative overflow-hidden">
                                <div className="absolute inset-0 bg-gradient-to-br from-red-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                                <item.icon className={cn("w-8 h-8 mb-4 relative z-10", item.color)} />
                                <h3 className="text-xl font-black text-white uppercase mb-3 relative z-10">{item.title}</h3>
                                <p className="text-sm text-gray-400 font-mono leading-relaxed mb-6 relative z-10">{item.body}</p>
                                <div className="border-t border-white/10 pt-4 relative z-10">
                                    <div className="text-4xl font-black text-white drop-shadow-md">{item.stat}</div>
                                    <div className="text-[10px] font-mono text-red-400/80 mt-1 uppercase tracking-[0.2em]">{item.statLabel}</div>
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="mt-12 p-8 border border-red-900/30 bg-red-950/10 relative">
                        <div className="absolute top-0 left-0 w-px h-full bg-red-500" />
                        <p className="text-xl md:text-2xl font-bold text-white leading-relaxed">
                            "The market is overpricing pedigree and <span className="text-red-400">catastrophically underpricing execution.</span> The founder with a Harvard MBA and a McKinsey pedigree is losing to the solo dev in Lagos who ships every day."
                        </p>
                        <div className="mt-4 text-xs font-mono text-gray-500">— MomentAIc Thesis Document, 2025</div>
                    </div>
                </div>
            </section>

            {/* ══════════════════════════════════ */}
            {/* ── 3. THE INEVITABLE ASCENDANCE ─── */}
            {/* ══════════════════════════════════ */}
            <section className="py-32 px-6 bg-[#000] border-t border-red-900/30 relative">
                <div className="max-w-7xl mx-auto relative z-10">
                    <div className="text-center mb-24">
                        <div className="inline-block border border-purple-500/30 bg-purple-500/10 text-purple-400 px-3 py-1 font-mono text-[10px] tracking-[0.4em] mb-6 uppercase">Phase 2: The Inevitability</div>
                        <h2 className="text-5xl md:text-7xl font-black text-white uppercase tracking-tighter leading-[0.85] drop-shadow-2xl">
                            Not Software.<br />
                            <span className="text-transparent bg-clip-text bg-gradient-to-br from-purple-400 via-pink-500 to-red-500">
                                A Synthetic Workforce.
                            </span>
                        </h2>
                        <p className="mt-8 text-gray-300 font-mono max-w-3xl mx-auto text-base leading-relaxed border-l-2 border-purple-500 pl-6 text-left">
                            The transition is mathematical. Software requires humans to operate it. MomentAIc deploys 50+ specialized neural agents that form a <strong className="text-white">living, breathing C-suite</strong>. They debate strategy, acquire users, and execute 24/7.
                        </p>
                    </div>

                    {/* Agent Roster Grid */}
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-px bg-white/5 border border-white/5 mb-16">
                        {AGENT_ROSTER.map((agent, i) => (
                            <div key={i}
                                className={cn(
                                    "bg-[#020202] p-5 transition-all duration-500",
                                    activeAgent === i ? "bg-purple-950/40 border-l-2 border-purple-500" : ""
                                )}
                            >
                                <div className="flex items-start justify-between mb-2">
                                    <div className={cn("w-2 h-2 rounded-full mt-1 transition-all",
                                        activeAgent === i ? "bg-purple-400 animate-pulse" : agent.active ? "bg-green-500" : "bg-gray-700"
                                    )} />
                                    <span className="text-[9px] font-mono text-gray-600">{agent.active ? "ONLINE" : "STAGING"}</span>
                                </div>
                                <div className="text-sm font-bold text-white mb-1">{agent.name}</div>
                                <div className="text-[10px] font-mono text-gray-500">{agent.role}</div>
                            </div>
                        ))}
                    </div>

                    {/* War Room Description */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                        <div>
                            <h3 className="text-3xl font-black text-white uppercase mb-6">The War Room</h3>
                            <div className="space-y-4 text-sm text-gray-400 font-mono leading-relaxed">
                                <p>Every startup gets a <strong className="text-white">private War Room</strong> — a unified command center where all agents converge. Signals flow in. Decisions are made. Actions execute. The founder observes or overrides at any level.</p>
                                <p>This isn't a dashboard. It's a <strong className="text-white">living organization</strong> — an AI-native company structure that replaces the entire SaaS stack with a single operating mind.</p>
                                <p className="border-l-2 border-purple-500 pl-4 text-white font-bold">
                                    The critical insight: every agent action generates proprietary behavioral data. We own the most granular founder execution dataset ever assembled.
                                </p>
                            </div>
                        </div>
                        <div className="bg-black border border-white/10 font-mono text-xs overflow-hidden">
                            <div className="bg-[#0a0a0a] border-b border-white/10 px-4 py-3 flex items-center gap-3">
                                <div className="flex gap-1.5">
                                    <div className="w-2.5 h-2.5 rounded-full bg-red-500" />
                                    <div className="w-2.5 h-2.5 rounded-full bg-yellow-500" />
                                    <div className="w-2.5 h-2.5 rounded-full bg-green-500" />
                                </div>
                                <span className="text-gray-600 text-[10px] tracking-widest">WAR_ROOM_LIVE_FEED</span>
                            </div>
                            <div className="p-6 space-y-3 text-[11px]">
                                {[
                                    { time: "03:14:22", agent: "SDR_HUNTER", color: "text-green-400", msg: "Lead acquired: @startup_founder via Reddit r/SaaS. Intent score: 94/100" },
                                    { time: "03:14:45", agent: "REDDIT_SNIPER", color: "text-blue-400", msg: "Signal detected: 'looking for CRM alternative' • r/entrepreneur • 247 upvotes" },
                                    { time: "03:15:01", agent: "GROWTH_HACKER", color: "text-purple-400", msg: "Campaign A/B test resolved. Variant B +34% CTR. Deploying at scale." },
                                    { time: "03:15:18", agent: "CFO_AGENT", color: "text-yellow-400", msg: "Burn rate alert: $12,400/mo. Runway: 8.2 months. Recommend Series A prep Q3." },
                                    { time: "03:15:33", agent: "INTEL_AGENT", color: "text-red-400", msg: "Competitor pricing change detected: Notion +$8/seat. Opportunity window: 72h." },
                                    { time: "03:15:44", agent: "SUPERVISOR", color: "text-white", msg: "All systems nominal. Signal Engine processing 847 active startups. Alpha mode: ON." },
                                ].map((line, i) => (
                                    <div key={i} className="flex gap-4">
                                        <span className="text-gray-700 flex-shrink-0">{line.time}</span>
                                        <span className={cn("flex-shrink-0 w-32", line.color)}>[{line.agent}]</span>
                                        <span className="text-gray-400">{line.msg}</span>
                                    </div>
                                ))}
                                <div className="text-purple-400 animate-pulse">_</div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* ─── THESIS PILLARS ─── */}
            <section id="thesis" className="py-32 px-6 bg-[#040407] border-t border-white/10 relative overflow-hidden">
                <div className="absolute left-1/2 top-0 w-3/4 h-3/4 -translate-x-1/2 opacity-10 pointer-events-none mix-blend-screen"
                    style={{ background: 'radial-gradient(ellipse at 50% 0%, #ff0055 0%, transparent 70%)' }} />

                <div className="max-w-7xl mx-auto relative z-10">
                    <div className="text-center mb-24">
                        <div className="inline-block border border-pink-500/30 bg-pink-500/10 text-pink-400 px-3 py-1 font-mono text-[10px] tracking-[0.4em] mb-6 uppercase">Phase 3: The Algorithm of Alpha</div>
                        <h2 className="text-5xl md:text-7xl font-black text-white uppercase tracking-tighter leading-[0.85] drop-shadow-2xl">
                            The Cap Table is<br />
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-500 to-pink-500">
                                Pre-computed.
                            </span>
                        </h2>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-px bg-white/10 border border-white/10">
                        {THESIS_PILLARS.map((pillar, i) => (
                            <div key={i} className="bg-[#020202] p-10 group hover:bg-[#080810] transition-colors">
                                <pillar.icon className="w-8 h-8 text-purple-400 mb-6" />
                                <h3 className="text-xl font-black text-white uppercase tracking-tighter mb-4">{pillar.title}</h3>
                                <p className="text-sm text-gray-400 font-mono leading-relaxed mb-8">{pillar.body}</p>
                                <div className="border-t border-white/5 pt-6 flex items-baseline gap-2">
                                    <span className="text-4xl font-black text-white">{pillar.metric}</span>
                                    <span className="text-[10px] font-mono text-gray-600 uppercase tracking-widest">{pillar.metricLabel}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                    <div className="mt-16 grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                        <div>
                            <h3 className="text-2xl font-black text-white uppercase mb-4">Information Asymmetry Edge</h3>
                            <p className="text-sm text-gray-400 font-mono leading-relaxed mb-6">Legacy VCs rely on lagging indicators — pitch decks, press mentions, AngelList profiles. Public signals with zero edge.</p>
                            <p className="text-sm text-gray-400 font-mono leading-relaxed mb-6">MomentAIc has <span className="text-white font-bold">100ms-refresh proprietary execution data</span>: commit velocity, campaign CTR, agent utilization, burn rate — all live across the entire user base.</p>
                            <p className="border-l-2 border-red-500 pl-4 text-sm text-white font-mono font-bold">By the time a founder walks into a VC firm, we already co-invested. We are the cap table.</p>
                        </div>
                        <div className="space-y-4">
                            {[
                                { label: "Pitch Decks (Public)", pct: 20, color: "bg-red-500/40", tag: "Lagging — 6-12 Month Lag" },
                                { label: "LinkedIn / AngelList", pct: 30, color: "bg-orange-500/40", tag: "Lagging — 3-6 Month Lag" },
                                { label: "Revenue Reports", pct: 45, color: "bg-yellow-500/40", tag: "Lagging — 1-3 Month Lag" },
                                { label: "MomentAIc Signal Score™", pct: 97, color: "bg-gradient-to-r from-purple-600 to-pink-500", tag: "Real-Time · Proprietary" },
                            ].map((item, i) => (
                                <div key={i}>
                                    <div className="flex justify-between text-[10px] font-mono mb-2">
                                        <span className={i === 3 ? "text-white font-bold" : "text-gray-500"}>{item.label}</span>
                                        <span className={i === 3 ? "text-purple-400" : "text-gray-600"}>{item.tag}</span>
                                    </div>
                                    <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden">
                                        <div className={`h-full ${item.color} rounded-full`} style={{ width: `${item.pct}%` }} />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </section>

            {/* ─── COMPETITIVE MOAT ─── */}
            <section className="py-32 px-6 bg-[#000] border-t border-red-900/30 relative">
                <div className="max-w-5xl mx-auto relative z-10">
                    <div className="inline-block border border-red-600/30 bg-red-600/10 text-red-500 px-3 py-1 font-mono text-[10px] tracking-[0.4em] mb-6 uppercase">Phase 4: Absolute Monopoly</div>
                    <h2 className="text-5xl md:text-7xl font-black text-white uppercase tracking-tighter mb-6 leading-[0.85]">
                        Every tool plays defense.<br />
                        <span className="text-red-500 drop-shadow-[0_0_20px_rgba(220,38,38,0.5)]">We play offense.</span>
                    </h2>
                    <p className="text-base text-gray-300 font-mono mb-16 max-w-3xl leading-relaxed border-l-2 border-red-500 pl-6">
                        The SaaS industry assumes humans operate software. We assumed they shouldn't have to. We are not competing in their category; we are obsoleting it.
                    </p>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm font-mono border-collapse">
                            <thead>
                                <tr className="border-b border-white/10">
                                    <th className="text-left p-4 text-gray-500 text-[10px] tracking-widest uppercase font-normal">Platform</th>
                                    {["Autonomous Exec", "Signal Intelligence", "Capital Deploy", "Replaces SaaS Stack"].map(h => (
                                        <th key={h} className="text-center p-4 text-gray-500 text-[10px] tracking-widest uppercase font-normal">{h}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {[
                                    { name: "Notion", cat: "Docs/Wiki", vals: [false, false, false, false] },
                                    { name: "HubSpot", cat: "CRM", vals: [false, false, false, false] },
                                    { name: "Clay", cat: "Data Enrichment", vals: [false, false, false, false] },
                                    { name: "Zapier", cat: "Automation", vals: [false, false, false, false] },
                                    { name: "MomentAIc", cat: "Autonomous OS", vals: [true, true, true, true], highlight: true },
                                ].map((row, i) => (
                                    <tr key={i} className={`border-b border-white/5 ${row.highlight ? "bg-purple-950/20" : ""}`}>
                                        <td className="p-4">
                                            <div className={row.highlight ? "font-bold text-white" : "text-gray-400"}>{row.name}</div>
                                            <div className="text-[10px] text-gray-600">{row.cat}</div>
                                        </td>
                                        {row.vals.map((v, j) => (
                                            <td key={j} className="p-4 text-center">
                                                {v ? <span className="text-green-400 font-bold">✓</span> : <span className="text-gray-700">✕</span>}
                                            </td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                    <div className="mt-8 p-6 bg-purple-950/10 border border-purple-500/20 text-sm font-mono text-gray-400">
                        <span className="text-purple-400 font-bold">Key Moat: </span>No competitor can replicate our Signal Engine dataset built from 847+ active founders. This data moat compounds exponentially with every new user.
                    </div>
                </div>
            </section>

            {/* ─── ALLOCATION ─── */}
            <section id="allocation" className="py-32 px-6 bg-[#040407] border-t border-red-900/10 relative overflow-hidden">
                <div className="absolute right-0 bottom-0 w-2/3 h-2/3 bg-red-900/5 blur-[120px] rounded-full pointer-events-none mix-blend-screen" />
                <div className="max-w-7xl mx-auto relative z-10">
                    <div className="text-center mb-20">
                        <div className="inline-block border border-yellow-500/30 bg-yellow-500/10 text-yellow-500 px-3 py-1 font-mono text-[10px] tracking-[0.4em] mb-6 uppercase">Phase 5: The War Chest</div>
                        <h2 className="text-5xl md:text-7xl font-black text-white uppercase tracking-tighter leading-[0.85] drop-shadow-xl">
                            Deploying<br />
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-amber-600">
                                Asymmetric Capital.
                            </span>
                        </h2>
                    </div>
                    <div className="grid grid-cols-1 gap-px bg-white/5 border border-white/5 mb-12">
                        {ALLOCATION.map((a, i) => (
                            <div key={i} className="bg-[#020202] p-10 hover:bg-[#080810] transition-colors">
                                <div className="flex flex-col lg:flex-row lg:items-center gap-8">
                                    <div className="flex-shrink-0">
                                        <div className="text-7xl font-black text-white leading-none">{a.pct}%</div>
                                        <div className="text-lg font-mono text-gray-500 mt-1">{a.usd}</div>
                                    </div>
                                    <div className="flex-1">
                                        <h3 className="text-2xl font-black text-white uppercase mb-3">{a.label}</h3>
                                        <p className="text-sm text-gray-400 font-mono leading-relaxed">{a.desc}</p>
                                    </div>
                                    <div className="flex-shrink-0 w-full lg:w-48">
                                        <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden">
                                            <div className={`h-full bg-gradient-to-r ${a.color}`} style={{ width: `${a.pct}%` }} />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-px bg-white/5 border border-white/5">
                        {[{ label: "Target IRR", value: "40-60%", sub: "Blended exits" }, { label: "Target Equity", value: "15-51%", sub: "Inception-stage" }, { label: "Portfolio Size", value: "5-10", sub: "Fund I companies" }].map((s, i) => (
                            <div key={i} className="bg-[#020202] p-8 text-center">
                                <div className="text-[10px] font-mono text-gray-600 uppercase tracking-widest mb-3">{s.label}</div>
                                <div className="text-4xl font-black text-white mb-2">{s.value}</div>
                                <div className="text-xs font-mono text-gray-500">{s.sub}</div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ─── ROADMAP ─── */}
            <section className="py-32 px-6 bg-[#000] border-t border-white/5">
                <div className="max-w-4xl mx-auto">
                    <div className="inline-block border border-blue-500/30 bg-blue-500/10 text-blue-400 px-3 py-1 font-mono text-[10px] tracking-[0.4em] mb-6 uppercase">Phase 6: Timeline</div>
                    <h2 className="text-5xl md:text-6xl font-black text-white uppercase tracking-tighter mb-16 leading-[0.85] drop-shadow-lg">
                        Inevitable<br />
                        <span className="text-blue-500">Execution.</span>
                    </h2>
                    <div className="relative">
                        <div className="absolute left-[19px] top-0 bottom-0 w-px bg-white/10" />
                        <div className="space-y-0">
                            {MILESTONES.map((m, i) => (
                                <div key={i} className="flex gap-8 pb-12 group">
                                    <div className={`flex-shrink-0 w-10 h-10 rounded-full border-2 flex items-center justify-center z-10 mt-1 transition-all ${m.done ? "bg-green-500/20 border-green-500" : "bg-[#020202] border-white/20 group-hover:border-blue-400"}`}>
                                        {m.done ? <span className="text-green-400 text-sm">✓</span> : <span className="text-gray-600 text-xs font-mono">{i + 1}</span>}
                                    </div>
                                    <div className="flex-1 pt-1">
                                        <div className="text-[10px] font-mono text-gray-600 mb-1 tracking-widest">{m.q}</div>
                                        <div className="flex items-center gap-3 mb-2">
                                            <h3 className="text-lg font-black text-white uppercase tracking-tight">{m.title}</h3>
                                            {m.done && <span className="text-[9px] font-mono bg-green-500/10 text-green-400 border border-green-500/20 px-2 py-0.5 uppercase tracking-widest">Complete</span>}
                                        </div>
                                        <p className="text-sm font-mono text-gray-400">{m.desc}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </section>

            {/* ─── ARCHITECT ─── */}
            <section className="py-32 px-6 bg-[#040407] border-t border-white/5 relative overflow-hidden">
                <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0IiBoZWlnaHQ9IjQiPgo8cmVjdCB3aWR0aD0iNCIgaGVpZ2h0PSI0IiBmaWxsPSIjZmZmIiBmaWxsLW9wYWNpdHk9IjAuMDIiLz4KPC9zdmc+')] opacity-20 pointer-events-none mix-blend-overlay" />
                <div className="max-w-5xl mx-auto relative z-10">
                    <div className="text-[10px] font-mono text-red-500 tracking-[0.4em] mb-16 uppercase text-center font-bold">The Maker of Inevitability</div>
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
                        <div className="relative">
                            <div className="absolute inset-0 bg-gradient-to-tr from-red-900/20 to-purple-900/20 blur-3xl rounded-full" />
                            <div className="relative border border-white/10 overflow-hidden aspect-square group">
                                <div className="absolute inset-0 bg-red-500/10 mix-blend-overlay group-hover:opacity-0 transition-opacity z-10" />
                                <img src="https://media.licdn.com/dms/image/v2/D4D03AQGLd1zL1T7z5w/profile-displayphoto-shrink_800_800/profile-displayphoto-shrink_800_800/0/1714574921966" alt="Tabare Majem" className="w-full h-full object-cover grayscale group-hover:grayscale-0 transition-all duration-700" onError={e => { (e.target as HTMLImageElement).src = "https://ui-avatars.com/api/?name=Tabare+Majem&background=2d0036&color=ffffff&size=800"; }} />
                                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black via-black/70 to-transparent p-6 z-20">
                                    <div className="text-[10px] font-mono text-red-400 mb-1 tracking-widest uppercase">The Architect</div>
                                    <div className="text-2xl font-black text-white uppercase tracking-wider">Tabaré Majem</div>
                                    <div className="text-xs font-mono text-gray-400 mt-1">Founder & CEO · MomentAIc</div>
                                </div>
                            </div>
                        </div>
                        <div>
                            <h2 className="text-3xl lg:text-4xl font-black text-white uppercase tracking-tighter mb-8 leading-[0.9]">Invest in the<br /><span className="text-red-400">Technology</span> and the <span className="text-purple-400">Maker.</span></h2>
                            <div className="space-y-4 text-sm text-gray-400 font-mono leading-relaxed mb-8">
                                <p>A <strong className="text-white">full-stack AI systems architect</strong> who built the swarm orchestration layer, scheduling infrastructure, War Room UI, and Signal Engine algorithms from scratch — 18 months of relentless execution.</p>
                                <p className="border-l-2 border-red-500 pl-4 text-white font-bold">Not seeking passive capital. Opening allocation for co-conspirators who understand the future of VC is quantitative, not credentialist.</p>
                            </div>
                            <div className="grid grid-cols-2 gap-4 mb-8">
                                {[{ val: "50+", label: "AI Agents Deployed" }, { val: "18mo", label: "In Development" }, { val: "847+", label: "Startups in System" }, { val: "24/7", label: "Autonomous Ops" }].map((s, i) => (
                                    <div key={i} className="border border-white/10 p-4 bg-black/40">
                                        <div className="text-2xl font-black text-white">{s.val}</div>
                                        <div className="text-[10px] font-mono text-gray-600 uppercase tracking-widest mt-1">{s.label}</div>
                                    </div>
                                ))}
                            </div>
                            <div className="flex flex-wrap gap-3">
                                <a href="https://www.linkedin.com/in/tabaremajem/" target="_blank" rel="noopener noreferrer" className="h-10 px-5 border border-white/10 hover:border-white/30 text-gray-300 hover:text-white font-mono text-xs uppercase tracking-widest flex items-center gap-2 transition-all">
                                    <Globe className="w-3.5 h-3.5" /> Verify Founder Intel
                                </a>
                                <Link to="/research" className="h-10 px-5 border border-purple-500/30 hover:border-purple-500 text-purple-400 hover:text-white font-mono text-xs uppercase tracking-widest flex items-center gap-2 transition-all">
                                    <BookOpen className="w-3.5 h-3.5" /> Algorithm of Alpha
                                </Link>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* ─── COMMIT TERMINAL ─── */}
            <section id="commit-terminal" className="py-32 px-6 bg-[#000] border-t border-red-900/20 relative">
                <div className="absolute inset-0 pointer-events-none" style={{ background: "radial-gradient(ellipse at 50% 0%, rgba(220,38,38,0.05) 0%, transparent 60%)" }} />
                <div className="max-w-5xl mx-auto relative z-10">
                    <div className="text-center mb-16">
                        <div className="text-[10px] font-mono text-red-400 tracking-[0.3em] mb-4 uppercase">Initiate Capital Protocol</div>
                        <h2 className="text-4xl md:text-6xl font-black text-white uppercase tracking-tighter leading-[0.9]">Commit to<br /><span className="text-red-500">Genesis Fund I</span></h2>
                        <p className="mt-4 text-gray-500 font-mono text-sm max-w-lg mx-auto">Minimum: $10,000 USD · Accredited investors only · Non-binding intent initiates term sheet generation</p>
                    </div>
                    <div className="bg-[#050508] border border-red-500/20 shadow-[0_0_100px_rgba(220,38,38,0.05)] overflow-hidden">
                        <div className="bg-[#0a0a0a] border-b border-white/10 px-5 py-3 flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="flex gap-1.5"><div className="w-3 h-3 rounded-full bg-red-500" /><div className="w-3 h-3 rounded-full bg-yellow-500" /><div className="w-3 h-3 rounded-full bg-green-500" /></div>
                                <span className="text-[10px] font-mono text-gray-600 tracking-widest">SECURE_COMMIT_PROTOCOL_v2.0 · AES-256 · TLS 1.3</span>
                            </div>
                            <span className="text-[10px] font-mono text-green-400 flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" /> OPEN</span>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2">
                            <div className="p-6 border-b md:border-b-0 md:border-r border-white/5 bg-black font-mono text-[11px]">
                                <div className="text-red-400 text-[10px] tracking-widest mb-4 uppercase">System Log</div>
                                <div className="space-y-2 text-gray-400 h-72 overflow-y-auto pr-2">
                                    {terminalOutput.map((log, i) => (
                                        <div key={i} className={cn("animate-fade-in", log.includes("SUCCESS") ? "text-green-400" : "")}>{log}</div>
                                    ))}
                                    {isSubmitting && <div className="animate-pulse text-purple-400">&gt; _</div>}
                                    {submitted && <div className="mt-4 p-3 bg-green-500/10 border border-green-500/20 text-green-400">✓ COMMITMENT RECEIVED — CHECK EMAIL</div>}
                                </div>
                            </div>
                            <div className="p-8 bg-[#050508]">
                                {submitted ? (
                                    <div className="h-full flex flex-col items-center justify-center text-center py-12">
                                        <div className="text-5xl mb-4">✓</div>
                                        <h3 className="text-xl font-black text-green-400 uppercase mb-2">Commitment Received</h3>
                                        <p className="text-sm font-mono text-gray-400">Check your email. Term sheet generation initiated.</p>
                                    </div>
                                ) : (
                                    <>
                                        <h3 className="text-lg font-black text-white uppercase mb-6">Initiate Wire Protocol</h3>
                                        <form onSubmit={handleCommit} className="space-y-4">
                                            {[
                                                { key: "name", label: "Lead Investor / Partner Name", placeholder: "John Doe", type: "text" },
                                                { key: "entity", label: "Entity / Fund Name", placeholder: "Alpha Ventures LP", type: "text" },
                                                { key: "email", label: "Contact Email", placeholder: "you@fund.com", type: "email" },
                                                { key: "amount", label: "Target Commitment (USD)", placeholder: "e.g. 50000", type: "number" },
                                            ].map(field => (
                                                <div key={field.key}>
                                                    <label className="text-[10px] font-mono text-gray-600 uppercase tracking-widest block mb-1">{field.label}</label>
                                                    <input
                                                        type={field.type} required disabled={isSubmitting}
                                                        value={formData[field.key as keyof typeof formData]}
                                                        onChange={e => setFormData({ ...formData, [field.key]: e.target.value })}
                                                        className="w-full bg-black border border-white/10 px-4 py-3 text-sm text-white font-mono focus:border-red-500 outline-none transition-colors placeholder:text-gray-700"
                                                        placeholder={field.placeholder}
                                                        min={field.key === "amount" ? "10000" : undefined}
                                                    />
                                                </div>
                                            ))}
                                            <button type="submit" disabled={isSubmitting} className="w-full h-12 mt-2 bg-red-600 hover:bg-red-500 text-white font-black font-mono text-xs uppercase tracking-[0.2em] transition-all flex items-center justify-center gap-2 disabled:opacity-50">
                                                {isSubmitting ? "ENCRYPTING..." : <><span>CONFIRM COMMITMENT</span><Send className="w-3.5 h-3.5" /></>}
                                            </button>
                                            <p className="text-[9px] font-mono text-gray-700 text-center">Non-binding intent · Routes to tabaremajem@gmail.com</p>
                                        </form>
                                    </>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* ─── FOOTER ─── */}
            <footer className="border-t border-white/5 py-12 px-6 bg-black">
                <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
                    <div className="text-[10px] font-mono text-gray-700 uppercase tracking-widest">© 2025 MomentAIc · Genesis Fund I · Confidential</div>
                    <div className="flex items-center gap-6 text-[10px] font-mono text-gray-700">
                        <Link to="/" className="hover:text-gray-400 transition-colors uppercase tracking-widest">Home</Link>
                        <Link to="/research" className="hover:text-gray-400 transition-colors uppercase tracking-widest">Research</Link>
                        <a href="mailto:tabaremajem@gmail.com" className="hover:text-gray-400 transition-colors uppercase tracking-widest">Contact</a>
                    </div>
                </div>
            </footer>
        </div>
    );
}
