
import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/auth-store';
import { api } from '../lib/api';
import { Button } from '../components/ui/Button';
import { Logo } from '../components/ui/Logo';
import {
    ArrowRight, Bot, Target, Activity, Zap, CheckCircle,
    Terminal, Shield, Code2, Cpu, Globe, Network,
    ChevronRight, Play, Wifi, Battery
} from 'lucide-react';
import { cn } from '../lib/utils';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card';
import { useToast } from '../components/ui/Toast';

// --- VISUAL FX COMPONENTS ---

// 1. Text Scramble Effect (For technical/terminal text)
const DecodeText = ({ text, className, delay = 0 }: { text: string, className?: string, delay?: number }) => {
    const [displayText, setDisplayText] = useState('');
    const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()";

    useEffect(() => {
        let iteration = 0;
        let interval: any = null;

        const start = setTimeout(() => {
            interval = setInterval(() => {
                setDisplayText(prev =>
                    text.split("").map((letter, index) => {
                        if (index < iteration) return text[index];
                        return chars[Math.floor(Math.random() * chars.length)];
                    }).join("")
                );
                if (iteration >= text.length) clearInterval(interval);
                iteration += 1 / 3;
            }, 30);
        }, delay);

        return () => { clearInterval(interval); clearTimeout(start); };
    }, [text, delay]);

    return <span className={className}>{displayText}</span>;
};

// 2. Elegant Word Reveal (Refined for maximum smoothness)
const ElegantText = ({ text, className, delay = 0 }: { text: string, className?: string, delay?: number }) => {
    const [start, setStart] = useState(false);

    useEffect(() => {
        const timer = setTimeout(() => setStart(true), delay);
        return () => clearTimeout(timer);
    }, [delay]);

    return (
        <span className={cn("inline-block leading-relaxed", className)}>
            {text.split(" ").map((word, i) => (
                <span
                    key={i}
                    className={cn(
                        "inline-block transition-all duration-1000 ease-[cubic-bezier(0.25,0.46,0.45,0.94)] will-change-[opacity,transform]",
                        start ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"
                    )}
                    style={{ transitionDelay: `${i * 50}ms` }}
                >
                    {word}&nbsp;
                </span>
            ))}
        </span>
    );
};

// 3. Interactive 3D Card
const TiltCard = ({ children, className }: { children?: React.ReactNode, className?: string }) => {
    const ref = useRef<HTMLDivElement>(null);

    const handleMouseMove = (e: React.MouseEvent) => {
        if (!ref.current) return;
        const rect = ref.current.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        const rotateX = ((y - centerY) / centerY) * -5; // Max 5deg tilt
        const rotateY = ((x - centerX) / centerX) * 5;

        ref.current.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.02)`;
    };

    const handleMouseLeave = () => {
        if (!ref.current) return;
        ref.current.style.transform = `perspective(1000px) rotateX(0deg) rotateY(0deg) scale(1)`;
    };

    return (
        <div
            ref={ref}
            className={cn("transition-transform duration-100 ease-out preserve-3d will-change-transform", className)}
            onMouseMove={handleMouseMove}
            onMouseLeave={handleMouseLeave}
        >
            {children}
        </div>
    );
};

export default function LandingPage() {
    const { isAuthenticated, upgradeTier } = useAuthStore();
    const [scrolled, setScrolled] = useState(false);
    const [activeFeature, setActiveFeature] = useState(0);
    const [loadingCheckout, setLoadingCheckout] = useState<string | null>(null);
    const navigate = useNavigate();
    const { toast } = useToast();

    useEffect(() => {
        const handleScroll = () => setScrolled(window.scrollY > 20);
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const scrollToSection = (id: string) => {
        const element = document.getElementById(id);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth' });
        }
    };

    const handleCheckout = async (tier: 'starter' | 'growth' | 'god_mode') => {
        if (!isAuthenticated) {
            navigate('/signup');
            return;
        }

        setLoadingCheckout(tier);
        try {
            toast({ type: 'info', title: 'Connecting', message: 'Initializing Stripe Secure Session...' });
            await api.createCheckoutSession(tier);
            // Simulating successful return for demo:
            upgradeTier(tier);
            toast({ type: 'success', title: 'Access Granted', message: `Welcome to ${tier.toUpperCase()} protocol.` });
            navigate('/dashboard');
        } catch (e) {
            toast({ type: 'error', title: 'Error', message: 'Payment gateway unavailable.' });
        } finally {
            setLoadingCheckout(null);
        }
    };

    const handleFooterLink = (e: React.MouseEvent) => {
        e.preventDefault();
        toast({ type: 'info', title: 'Restricted Access', message: 'Public clearance level insufficient for internal docs.' });
    };

    const features = [
        {
            id: 'swarm',
            title: 'NEURAL SWARM',
            icon: <Network className="w-5 h-5 text-[#00f0ff]" />,
            desc: 'Autonomous Agent Deployment',
            code: `> INIT_SWARM_PROTOCOL
> DEPLOYING: SALES_BOT_V4 [ACTIVE]
> DEPLOYING: DEV_OPS_CORE [ACTIVE]
> DEPLOYING: LEGAL_SENTINEL [ACTIVE]
> STATUS: 24/7 AUTONOMY ESTABLISHED
> REVENUE_IMPACT: +400%
`
        },
        {
            id: 'radar',
            title: 'SIGNAL RADAR',
            icon: <Activity className="w-5 h-5 text-[#a855f7]" />,
            desc: 'Predictive Velocity Analytics',
            code: `> SCANNING_MARKET_VECTORS...
> ANALYZING: PMF_SCORE [94.2/100]
> DETECTED: VIRAL_COEFFICIENT_SPIKE
> RECOMMENDATION: DOUBLE_DOWN_AD_SPEND
> COMPETITOR_ANALYSIS: [WEAK]
> OPPORTUNITY: HIGH`
        },
        {
            id: 'forge',
            title: 'VISION FORGE',
            icon: <Cpu className="w-5 h-5 text-[#3b82f6]" />,
            desc: 'Text-to-Software Compiler',
            code: `> INPUT: "Build a CRM for dentists"
> ARCHITECTING_DB_SCHEMA... [DONE]
> GENERATING_REACT_COMPONENTS... [DONE]
> CONFIGURING_API_ROUTES... [DONE]
> DEPLOYING_TO_EDGE... [SUCCESS]
> URL: DENTIST-OS.MOMENT.AI
`
        }
    ];

    return (
        <div className="min-h-screen bg-[#020202] text-white font-sans selection:bg-[#00f0ff] selection:text-black overflow-x-hidden">

            {/* --- AMBIENT LAYER --- */}
            <div className="fixed inset-0 z-0 pointer-events-none">
                {/* CRT Scanline Overlay */}
                <div className="crt-overlay opacity-20"></div>
                {/* Deep Space Grid with Motion */}
                <div className="absolute inset-0 bg-[linear-gradient(to_right,#111_1px,transparent_1px),linear-gradient(to_bottom,#111_1px,transparent_1px)] bg-[size:50px_50px] opacity-[0.25] [transform:perspective(1000px)_rotateX(60deg)] origin-top animate-grid-flow"></div>
                {/* Spotlights */}
                <div className="absolute top-[-30%] left-[20%] w-[600px] h-[600px] bg-brand-purple/20 blur-[120px] rounded-full mix-blend-screen animate-pulse-fast"></div>
                <div className="absolute top-[20%] right-[-10%] w-[800px] h-[800px] bg-brand-blue/10 blur-[150px] rounded-full mix-blend-screen"></div>
            </div>

            {/* --- HUD NAVBAR --- */}
            <nav className={cn(
                "fixed top-0 w-full z-50 transition-all duration-300 border-b",
                scrolled ? "bg-[#020202]/90 border-white/10 backdrop-blur-xl py-3" : "bg-transparent border-transparent py-6"
            )}>
                <div className="max-w-7xl mx-auto px-6 flex items-center justify-between">
                    <Logo collapsed={false} />

                    <div className="flex items-center gap-8">
                        <div className="hidden md:flex items-center gap-1 font-mono text-[10px] text-gray-500 tracking-widest">
                            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                            SYSTEM_ONLINE
                        </div>

                        <div className="flex items-center gap-6">
                            <button onClick={() => scrollToSection('terminal')} className="hidden md:block text-xs font-bold font-mono text-gray-400 hover:text-[#00f0ff] transition-colors tracking-widest uppercase bg-transparent border-none">
                                [TERMINAL]
                            </button>
                            <button onClick={() => scrollToSection('pricing')} className="hidden md:block text-xs font-bold font-mono text-gray-400 hover:text-[#00f0ff] transition-colors tracking-widest uppercase bg-transparent border-none">
                                [ACCESS]
                            </button>

                            {isAuthenticated ? (
                                <Link to="/dashboard">
                                    <Button variant="cyber" className="h-9 px-6 text-xs shadow-[0_0_20px_rgba(0,240,255,0.3)]">
                                        ENTER_CONSOLE
                                    </Button>
                                </Link>
                            ) : (
                                <div className="flex gap-4">
                                    <Link to="/login" className="hidden sm:block text-xs font-bold font-mono text-white hover:text-[#00f0ff] tracking-widest transition-colors py-2">
                            // LOGIN
                                    </Link>
                                    <Link to="/signup">
                                        <Button variant="outline" className="text-xs h-9 px-6 font-mono tracking-widest border-[#00f0ff]/50 text-[#00f0ff] hover:bg-[#00f0ff] hover:text-black">
                                            INITIALIZE_
                                        </Button>
                                    </Link>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </nav>

            {/* --- HERO SECTION --- */}
            <section className="relative pt-32 pb-20 px-6 z-10 max-w-7xl mx-auto min-h-[90vh] flex flex-col justify-center">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-24 items-center">

                    {/* Left: Typography (Staggered Entrance) */}
                    <div className="space-y-8 order-2 lg:order-1 text-center lg:text-left">
                        <div className="inline-flex items-center gap-2 border border-[#a855f7]/30 bg-[#a855f7]/5 px-3 py-1 rounded font-mono text-[#a855f7] text-[10px] tracking-[0.2em] uppercase backdrop-blur-md animate-fade-in-up" style={{ animationDelay: '0ms' }}>
                            <Terminal className="w-3 h-3" />
                            <DecodeText text="OPEN SOURCE // THE ANTI-YC" />
                        </div>

                        <h1 className="text-5xl sm:text-7xl lg:text-9xl font-black leading-[0.9] tracking-tighter uppercase relative animate-fade-in-up" style={{ animationDelay: '200ms' }}>
                            <span className="block text-white relative z-10">BUILD YOUR</span>
                            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-[#a855f7] via-[#e11d48] to-[#00f0ff] relative z-10 py-2">
                                EMPIRE
                            </span>
                        </h1>

                        <p className="text-lg text-gray-400 font-mono max-w-xl leading-relaxed mx-auto lg:mx-0 tracking-tight border-l-2 border-purple-500/30 pl-4 animate-fade-in-up" style={{ animationDelay: '400ms' }}>
                            <ElegantText text="16 AI Co-Founders. One Operating System. Infinite Potential. The platform for the next generation of entrepreneurs." delay={800} />
                        </p>

                        <div className="flex flex-col sm:flex-row gap-4 pt-4 justify-center lg:justify-start animate-fade-in-up" style={{ animationDelay: '600ms' }}>
                            <Link to="/signup" className="w-full sm:w-auto">
                                <Button size="lg" variant="cyber" className="w-full sm:w-auto h-14 text-sm px-10 shadow-[0_0_40px_rgba(168,85,247,0.4)] border-[#a855f7]/50">
                                    🚀 START BUILDING <ArrowRight className="ml-2 w-4 h-4" />
                                </Button>
                            </Link>
                            <Link to="/mission" className="w-full sm:w-auto">
                                <Button size="lg" variant="outline" className="w-full sm:w-auto h-14 text-sm px-8 border-green-500/30 hover:bg-green-500/10 text-green-400 font-mono tracking-widest">
                                    💻 JOIN THE MISSION
                                </Button>
                            </Link>
                        </div>
                        <div className="flex flex-wrap gap-3 pt-4 justify-center lg:justify-start animate-fade-in-up" style={{ animationDelay: '700ms' }}>
                            <Link to="/leaderboard" className="text-xs font-mono text-gray-500 hover:text-purple-400 transition">🏆 LEADERBOARD</Link>
                            <span className="text-gray-700">•</span>
                            <a href="https://github.com/momentaic/momentaic" className="text-xs font-mono text-gray-500 hover:text-green-400 transition">⭐ GITHUB</a>
                            <span className="text-gray-700">•</span>
                            <span className="text-xs font-mono text-gray-600">$9/mo</span>
                        </div>
                    </div>

                    {/* Right: 3D Interface (Staggered Entrance) */}
                    <div className="relative h-[600px] w-full flex items-center justify-center order-1 lg:order-2 animate-fade-in-up px-4" style={{ animationDelay: '800ms' }}>
                        <TiltCard className="relative w-full max-w-[360px] h-[700px] bg-[#050505] border border-white/10 rounded-[3rem] shadow-2xl z-10">
                            {/* Screen Content */}
                            <div className="absolute inset-[4px] bg-[#000] rounded-[2.8rem] overflow-hidden flex flex-col z-20 border border-white/5">

                                {/* Dynamic Grid Background */}
                                <div className="absolute inset-0 bg-cyber-grid bg-[length:30px_30px] opacity-20 pointer-events-none"></div>

                                {/* Top Bar */}
                                <div className="h-14 flex justify-between items-center px-6 pt-4 border-b border-white/5 bg-black/50 backdrop-blur-sm relative z-30">
                                    <div className="text-[10px] font-mono text-[#00f0ff] tracking-widest animate-pulse">LIVE_FEED</div>
                                    <div className="flex gap-2">
                                        <Wifi className="w-4 h-4 text-gray-400" />
                                        <Battery className="w-4 h-4 text-gray-400" />
                                    </div>
                                </div>

                                {/* App UI */}
                                <div className="p-6 space-y-8 flex-1 relative z-20">
                                    {/* Revenue Block */}
                                    <div className="relative">
                                        <div className="text-[10px] text-gray-500 font-mono mb-1 tracking-widest uppercase">Total Valuation</div>
                                        <div className="text-4xl font-black font-mono text-white tracking-tighter flex items-center gap-2">
                                            $2.4M <span className="text-xs bg-green-500/20 text-green-500 px-2 py-0.5 rounded font-bold">+12%</span>
                                        </div>
                                        <div className="h-32 mt-4 flex items-end justify-between gap-1">
                                            {[20, 45, 30, 60, 55, 80, 70, 90, 85, 100].map((h, i) => (
                                                <div key={i} className="flex-1 bg-gradient-to-t from-[#3b82f6] to-[#00f0ff] rounded-t-sm opacity-80" style={{ height: `${h}%` }}></div>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Agent Feed */}
                                    <div className="space-y-3">
                                        <div className="text-[10px] text-gray-500 font-mono uppercase tracking-widest border-b border-white/5 pb-2 flex justify-between">
                                            <span>Active Protocols</span>
                                            <span className="text-white">3/3</span>
                                        </div>
                                        {[
                                            { name: 'SALES_BOT', task: 'Closing Lead #492', time: '2s ago', color: 'text-[#00f0ff]' },
                                            { name: 'DEV_CORE', task: 'Deploying Hotfix', time: '12s ago', color: 'text-[#a855f7]' },
                                            { name: 'LEGAL_AI', task: 'Reviewing NDA', time: '45s ago', color: 'text-[#3b82f6]' },
                                        ].map((agent, i) => (
                                            <div key={i} className="flex items-center gap-3 bg-white/5 p-3 rounded-xl border border-white/5 backdrop-blur-md">
                                                <div className="w-8 h-8 rounded-lg bg-black flex items-center justify-center border border-white/10">
                                                    <Bot className={`w-4 h-4 ${agent.color}`} />
                                                </div>
                                                <div className="flex-1">
                                                    <div className="text-[10px] font-bold text-white uppercase tracking-wide flex justify-between">
                                                        {agent.name} <span className="text-gray-600 font-mono">{agent.time}</span>
                                                    </div>
                                                    <div className="text-[10px] text-gray-400 font-mono truncate">{agent.task}</div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Bottom Actions */}
                                <div className="h-20 bg-black/80 backdrop-blur-xl border-t border-white/10 flex items-center justify-around px-6 relative z-30">
                                    <div className="w-12 h-12 rounded-full bg-[#00f0ff]/10 flex items-center justify-center border border-[#00f0ff]/50 shadow-[0_0_15px_rgba(0,240,255,0.3)]">
                                        <Zap className="w-5 h-5 text-[#00f0ff]" />
                                    </div>
                                    <div className="w-32 h-1 bg-white/20 rounded-full"></div>
                                    <div className="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center">
                                        <Activity className="w-5 h-5 text-gray-400" />
                                    </div>
                                </div>
                            </div>
                        </TiltCard>

                        {/* Decorative Elements behind phone */}
                        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] border border-white/5 rounded-full animate-[spin_20s_linear_infinite] z-0"></div>
                        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] border border-white/5 rounded-full animate-[spin_30s_linear_infinite_reverse] z-0"></div>
                    </div>
                </div>
            </section>

            {/* --- MARQUEE --- */}
            <div className="w-full bg-[#0a0a0a] py-3 border-y border-white/5 relative z-20 overflow-hidden">
                <div className="whitespace-nowrap animate-[scanline_30s_linear_infinite] font-mono text-xs text-gray-600 tracking-[0.3em] flex gap-24 select-none uppercase items-center">
                    {[1, 2, 3, 4].map(i => (
                        <React.Fragment key={i}>
                            <span className="flex items-center gap-4"><Globe className="w-4 h-4" /> Global Neural Network</span>
                            <span className="flex items-center gap-4"><Cpu className="w-4 h-4" /> 99.9% Uptime</span>
                            <span className="flex items-center gap-4"><Shield className="w-4 h-4" /> Military Grade Encryption</span>
                        </React.Fragment>
                    ))}
                </div>
            </div>

            {/* --- TERMINAL (FORMERLY TOTAL COMMAND) --- */}
            <section id="terminal" className="py-32 px-6 relative bg-[#020202] scroll-mt-24">
                <div className="max-w-7xl mx-auto">
                    <div className="mb-16 md:flex justify-between items-end">
                        <div>
                            <h2 className="text-4xl md:text-6xl font-black uppercase mb-4 tracking-tighter text-white">
                                System <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#00f0ff] to-white">Capabilities</span>
                            </h2>
                            <p className="text-gray-400 max-w-xl text-sm font-mono border-l border-[#00f0ff] pl-4">
                                Direct neural interface to your business operations. <br />
                                Select a module to initialize protocol.
                            </p>
                        </div>
                        <div className="hidden md:block font-mono text-[10px] text-gray-600 text-right">
                            <div className="mb-1">CPU_LOAD: 12%</div>
                            <div>MEM_USAGE: 4.2GB</div>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 border border-white/10 rounded-2xl bg-[#050505] overflow-hidden shadow-2xl">

                        {/* Left: Feature List */}
                        <div className="lg:col-span-4 border-r border-white/10 bg-[#0a0a0a]">
                            <div className="p-4 border-b border-white/10 font-mono text-[10px] text-gray-500 uppercase tracking-widest bg-[#020202]">
                                Available Modules
                            </div>
                            {features.map((feature, idx) => (
                                <button
                                    key={feature.id}
                                    onClick={() => setActiveFeature(idx)}
                                    className={cn(
                                        "w-full text-left p-6 border-b border-white/5 transition-all duration-300 group relative overflow-hidden",
                                        activeFeature === idx ? "bg-[#00f0ff]/5" : "hover:bg-white/5"
                                    )}
                                >
                                    {activeFeature === idx && <div className="absolute left-0 top-0 bottom-0 w-1 bg-[#00f0ff]"></div>}
                                    <div className="flex justify-between items-center mb-2">
                                        <div className="p-2 bg-black rounded-lg border border-white/10 group-hover:border-[#00f0ff]/50 transition-colors">
                                            {feature.icon}
                                        </div>
                                        <span className="font-mono text-[9px] text-gray-600 group-hover:text-[#00f0ff]">{`0${idx + 1}`}</span>
                                    </div>
                                    <h3 className={cn("font-bold font-mono text-sm uppercase tracking-wide transition-colors", activeFeature === idx ? "text-white" : "text-gray-400 group-hover:text-white")}>
                                        {feature.title}
                                    </h3>
                                    <p className="text-xs text-gray-600 mt-1">{feature.desc}</p>
                                </button>
                            ))}
                        </div>

                        {/* Right: Terminal Visualizer */}
                        <div className="lg:col-span-8 bg-black relative min-h-[400px] flex flex-col font-mono text-sm">
                            {/* Window Controls */}
                            <div className="h-10 border-b border-white/10 flex items-center px-4 gap-2 bg-[#0a0a0a]">
                                <div className="w-3 h-3 rounded-full bg-red-500/20 border border-red-500/50"></div>
                                <div className="w-3 h-3 rounded-full bg-yellow-500/20 border border-yellow-500/50"></div>
                                <div className="w-3 h-3 rounded-full bg-green-500/20 border border-green-500/50"></div>
                                <div className="ml-auto text-xs text-gray-600">bash --login</div>
                            </div>

                            {/* Code Output */}
                            <div className="p-8 text-gray-300 relative z-10">
                                <div className="absolute top-4 right-4 text-[10px] text-[#00f0ff] animate-pulse">LIVE EXECUTION</div>
                                <div className="space-y-1">
                                    <div className="text-gray-500 mb-4"># Initializing module: {features[activeFeature].title}</div>
                                    <pre className="whitespace-pre-wrap font-mono text-[#00f0ff] text-xs md:text-sm leading-relaxed">
                                        <DecodeText text={features[activeFeature].code} delay={0} className="block" />
                                    </pre>
                                    <div className="animate-pulse mt-2">_</div>
                                </div>
                            </div>

                            {/* Background Grid inside terminal */}
                            <div className="absolute inset-0 bg-cyber-grid bg-[length:20px_20px] opacity-10 pointer-events-none"></div>
                        </div>
                    </div>
                </div>
            </section>

            {/* --- PRICING (CLEARANCE LEVELS) --- */}
            <section id="pricing" className="py-32 px-6 bg-[#050505] border-t border-white/5 relative scroll-mt-24">
                <div className="absolute inset-0 bg-cyber-grid bg-[length:40px_40px] opacity-[0.03] pointer-events-none"></div>
                <div className="max-w-7xl mx-auto">
                    <div className="text-center mb-20">
                        <h2 className="text-3xl md:text-5xl font-black uppercase mb-6 tracking-tighter text-white">
                            Choose Your <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-purple to-brand-blue">Protocol</span>
                        </h2>
                        <p className="text-gray-400 font-mono text-xs uppercase tracking-widest">All plans include cross-platform access with AgentForge</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        {/* Starter - $9 */}
                        <div className="group relative">
                            <div className="absolute inset-0 bg-gradient-to-b from-cyan-500/10 to-transparent rounded-2xl transform transition-transform group-hover:scale-[1.02] duration-300"></div>
                            <Card className="border-cyan-500/20 bg-[#0a0a0a] relative h-full">
                                <CardHeader className="border-b border-white/5 pb-6">
                                    <div className="font-mono text-[10px] text-cyan-400 uppercase tracking-widest mb-2">Level 1</div>
                                    <CardTitle className="text-3xl font-black text-white">STARTER</CardTitle>
                                    <CardDescription className="text-gray-500 text-sm mt-2">For indie hackers testing the waters</CardDescription>
                                </CardHeader>
                                <CardContent className="space-y-6 pt-8">
                                    <div className="text-5xl font-black text-white font-sans">$9<span className="text-sm text-gray-500 font-normal">/mo</span></div>
                                    <ul className="space-y-3 text-xs font-mono text-gray-400 uppercase tracking-wide">
                                        <li className="flex items-center gap-3"><div className="w-1.5 h-1.5 bg-cyan-400 rounded-full"></div> 100 AI Credits/month</li>
                                        <li className="flex items-center gap-3"><div className="w-1.5 h-1.5 bg-cyan-400 rounded-full"></div> 1 Startup Project</li>
                                        <li className="flex items-center gap-3"><div className="w-1.5 h-1.5 bg-cyan-400 rounded-full"></div> Basic Signal Radar</li>
                                        <li className="flex items-center gap-3"><div className="w-1.5 h-1.5 bg-cyan-400 rounded-full"></div> Community Access</li>
                                        <li className="flex items-center gap-3"><div className="w-1.5 h-1.5 bg-cyan-400 rounded-full"></div> Email Support</li>
                                    </ul>
                                    <Button
                                        className="w-full h-12 border-cyan-500/30 text-cyan-400 hover:bg-cyan-500 hover:text-black"
                                        variant="outline"
                                        onClick={() => handleCheckout('starter')}
                                        isLoading={loadingCheckout === 'starter'}
                                        disabled={!!loadingCheckout}
                                    >
                                        START FREE TRIAL
                                    </Button>
                                </CardContent>
                            </Card>
                        </div>

                        {/* Builder - $19 */}
                        <div className="group relative -mt-4 mb-4 md:mt-0 md:mb-0">
                            <div className="absolute inset-0 bg-gradient-to-b from-[#a855f7]/20 to-transparent rounded-2xl transform transition-transform group-hover:scale-[1.02] duration-300 blur-sm"></div>
                            <Card className="border-[#a855f7]/50 bg-[#0c0c0c] relative h-full shadow-[0_0_50px_rgba(168,85,247,0.1)]">
                                <div className="absolute top-0 w-full h-1 bg-gradient-to-r from-transparent via-[#a855f7] to-transparent"></div>
                                <CardHeader className="border-b border-white/5 pb-6">
                                    <div className="font-mono text-[10px] text-[#a855f7] uppercase tracking-widest mb-2 flex justify-between">
                                        Level 2 <span className="bg-[#a855f7]/20 px-2 py-0.5 rounded">⭐ POPULAR</span>
                                    </div>
                                    <CardTitle className="text-3xl font-black text-white">BUILDER</CardTitle>
                                    <CardDescription className="text-gray-400 text-sm mt-2">For serious founders building in public</CardDescription>
                                </CardHeader>
                                <CardContent className="space-y-6 pt-8">
                                    <div className="text-5xl font-black text-white font-sans">$19<span className="text-sm text-gray-500 font-normal">/mo</span></div>
                                    <ul className="space-y-3 text-xs font-mono text-gray-300 uppercase tracking-wide">
                                        <li className="flex items-center gap-3"><div className="w-1.5 h-1.5 bg-[#a855f7] rounded-full"></div> 500 AI Credits/month</li>
                                        <li className="flex items-center gap-3"><div className="w-1.5 h-1.5 bg-[#a855f7] rounded-full"></div> 3 Startup Projects</li>
                                        <li className="flex items-center gap-3"><div className="w-1.5 h-1.5 bg-[#a855f7] rounded-full"></div> Full Signal Radar + Traction</li>
                                        <li className="flex items-center gap-3"><div className="w-1.5 h-1.5 bg-[#a855f7] rounded-full"></div> All 6 AI Agents</li>
                                        <li className="flex items-center gap-3"><div className="w-1.5 h-1.5 bg-[#a855f7] rounded-full"></div> Priority Support</li>
                                        <li className="flex items-center gap-3"><div className="w-1.5 h-1.5 bg-[#a855f7] rounded-full"></div> AgentForge Access</li>
                                    </ul>
                                    <Button
                                        className="w-full h-12 shadow-[0_0_20px_rgba(168,85,247,0.3)] bg-[#a855f7] hover:bg-[#9333ea] border-none text-white"
                                        variant="default"
                                        onClick={() => handleCheckout('growth')}
                                        isLoading={loadingCheckout === 'growth'}
                                        disabled={!!loadingCheckout}
                                    >
                                        UPGRADE TO BUILDER
                                    </Button>
                                </CardContent>
                            </Card>
                        </div>

                        {/* Founder / God Mode - $39 */}
                        <div className="group relative">
                            <div className="absolute inset-0 bg-gradient-to-b from-amber-500/10 to-transparent rounded-2xl transform transition-transform group-hover:scale-[1.02] duration-300"></div>
                            <Card className="border-amber-500/30 bg-[#0a0a0a] relative h-full">
                                <div className="absolute top-0 w-full h-0.5 bg-gradient-to-r from-transparent via-amber-500 to-transparent"></div>
                                <CardHeader className="border-b border-white/5 pb-6">
                                    <div className="font-mono text-[10px] text-amber-400 uppercase tracking-widest mb-2 flex items-center gap-2">
                                        Level 3 <span className="text-lg">👑</span>
                                    </div>
                                    <CardTitle className="text-3xl font-black text-amber-400">FOUNDER</CardTitle>
                                    <CardDescription className="text-gray-400 text-sm mt-2">God Mode for founders ready to scale</CardDescription>
                                </CardHeader>
                                <CardContent className="space-y-6 pt-8">
                                    <div className="text-5xl font-black text-white font-sans">$39<span className="text-sm text-gray-500 font-normal">/mo</span></div>
                                    <ul className="space-y-3 text-xs font-mono text-gray-400 uppercase tracking-wide">
                                        <li className="flex items-center gap-3"><div className="w-1.5 h-1.5 bg-amber-400 rounded-full"></div> 2000 AI Credits/month</li>
                                        <li className="flex items-center gap-3"><div className="w-1.5 h-1.5 bg-amber-400 rounded-full"></div> Unlimited Projects</li>
                                        <li className="flex items-center gap-3"><div className="w-1.5 h-1.5 bg-amber-400 rounded-full"></div> Vision Portal (Claude)</li>
                                        <li className="flex items-center gap-3"><div className="w-1.5 h-1.5 bg-amber-400 rounded-full"></div> Custom Workflows (Forge)</li>
                                        <li className="flex items-center gap-3"><div className="w-1.5 h-1.5 bg-amber-400 rounded-full"></div> Deep Research (Gemini 2.0)</li>
                                        <li className="flex items-center gap-3"><div className="w-1.5 h-1.5 bg-amber-400 rounded-full"></div> White-label Options</li>
                                        <li className="flex items-center gap-3"><div className="w-1.5 h-1.5 bg-amber-400 rounded-full"></div> AgentForge Pro Access</li>
                                    </ul>
                                    <Button
                                        className="w-full h-12 border-amber-500/50 text-amber-400 hover:bg-amber-500 hover:text-black shadow-[0_0_20px_rgba(245,158,11,0.2)]"
                                        variant="outline"
                                        onClick={() => handleCheckout('god_mode')}
                                        isLoading={loadingCheckout === 'god_mode'}
                                        disabled={!!loadingCheckout}
                                    >
                                        ACTIVATE GOD MODE
                                    </Button>
                                </CardContent>
                            </Card>
                        </div>
                    </div>
                </div>
            </section>

            {/* --- MANIFESTO (RAW TEXT) --- */}
            <section className="py-20 px-6 bg-black border-t border-purple-500/20 font-mono text-xs text-gray-500">
                <div className="max-w-2xl mx-auto space-y-4">
                    <div className="text-[#a855f7] mb-4">root@momentaic:~/manifesto.txt</div>
                    <p>{">> THE PEDIGREE ERA IS OVER."}</p>
                    <p>{">> YOUR SCHOOL DOESN'T MATTER. YOUR NETWORK DOESN'T MATTER. YOUR METRICS DO."}</p>
                    <p>{">> WE BUILT MOMENTAIC FOR THE HUSTLE FROM THE FAVELA, THE FLAT IN MANILA, THE CAFE IN LAGOS."}</p>
                    <p>{">> 16 AI CO-FOUNDERS. 42 INTEGRATIONS. INFINITE POSSIBILITIES."}</p>
                    <p>{">> THIS IS NOT A TOOL. THIS IS YOUR EQUALIZER."}</p>
                    <div className="animate-pulse text-[#a855f7]">_</div>
                </div>
            </section>

            {/* --- CTA SECTION --- */}
            <section className="py-40 px-6 bg-[#050505] relative overflow-hidden border-t border-purple-500/10">
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-[#a855f7] opacity-[0.05] blur-[150px] rounded-full pointer-events-none"></div>

                <div className="relative z-10 max-w-4xl mx-auto text-center space-y-10">
                    <div className="flex justify-center gap-2 text-3xl mb-4">
                        <span>🇵🇭</span><span>🇵🇪</span><span>🇳🇬</span><span>🇮🇳</span><span>🇧🇷</span><span>🇮🇩</span><span>🌍</span>
                    </div>
                    <h2 className="text-5xl md:text-8xl font-black text-white tracking-tighter leading-[0.85]">
                        BUILD FROM<br /><span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-500">ANYWHERE.</span>
                    </h2>
                    <p className="text-gray-400 max-w-xl mx-auto">$9/mo for the same AI power that $500K YC companies use.</p>
                    <div className="flex flex-col sm:flex-row justify-center gap-6 pt-8">
                        <Link to="/signup" className="w-full sm:w-auto">
                            <Button variant="cyber" size="lg" className="w-full sm:w-auto h-16 px-12 text-lg shadow-[0_0_50px_rgba(168,85,247,0.4)]">
                                🚀 START BUILDING
                            </Button>
                        </Link>
                    </div>
                </div>
            </section>

            {/* --- FOOTER --- */}
            <footer className="border-t border-white/5 bg-[#020202] py-12 px-6 font-mono text-xs text-gray-700">
                <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-8 text-center md:text-left">
                    <div className="flex items-center gap-3 opacity-50 hover:opacity-100 transition-opacity">
                        <Logo collapsed={true} className="opacity-50" />
                        <span className="text-gray-500 font-bold text-sm tracking-tight">MOMENT.AI.C // OS</span>
                    </div>
                    <div className="tracking-widest uppercase">© 2024 MOMENTUM SYSTEMS</div>
                    <div className="flex gap-8">
                        <a href="#" onClick={handleFooterLink} className="hover:text-white transition-colors">STATUS</a>
                        <a href="#" onClick={handleFooterLink} className="hover:text-white transition-colors">LEGAL</a>
                        <a href="#" onClick={handleFooterLink} className="hover:text-white transition-colors">DOCS</a>
                    </div>
                </div>
            </footer>
        </div>
    );
}
