
import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../ui/Button';
import { ArrowRight, Zap, Play, Terminal, Target, Bot, CheckCircle2, ChevronRight, Sparkles, TrendingUp, Shield } from 'lucide-react';
import { cn } from '../../lib/utils';
import { useTranslation } from 'react-i18next';

// --- Animated Typing Text Component ---
const RotatingKeywords = () => {
    const words = ["SALES", "MARKETING", "OPERATIONS", "GROWTH", "EVERYTHING"];
    const [index, setIndex] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => {
            setIndex((prev) => (prev + 1) % words.length);
        }, 2500);
        return () => clearInterval(interval);
    }, []);

    return (
        <span className="inline-block min-w-[280px] text-left">
            {words.map((word, i) => (
                <span
                    key={word}
                    className={cn(
                        "absolute transition-all duration-700 ease-in-out font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-500 to-purple-400 bg-300% animate-gradient",
                        i === index ? "opacity-100 transform-none" : "opacity-0 -translate-y-8 pointer-events-none"
                    )}
                >
                    {word}
                </span>
            ))}
            {/* Hack to keep layout height stable */}
            <span className="opacity-0 pointer-events-none block">{words[0]}</span>
        </span>
    );
};

// --- Floating Showcase Component ---
const FloatingCard = ({ delay, posObj, children, className }: any) => (
    <div
        className={cn(
            "absolute hidden lg:flex flex-col bg-[#0a0a0f]/80 backdrop-blur-xl border border-white/10 p-4 clip-corner-2 shadow-[0_0_30px_rgba(168,85,247,0.15)] animate-float transition-transform duration-300",
            className
        )}
        style={{
            animationDelay: `${delay}s`,
            transform: `translate(${posObj.x * 20}px, ${posObj.y * 20}px)`
        }}
    >
        {children}
    </div>
);

export function SentientHero() {
    const { t } = useTranslation();
    const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
    const [logs, setLogs] = useState<string[]>([]);

    // MCP Boot Sequence
    useEffect(() => {
        const sequence = [
            "> INITIALIZING_AUTONOMY_ENGINE...",
            "> LOADING_LLM_MODELS: [GPT-4o, CLAUDE-3.5] [OK]",
            "> CONNECTING_TO_STRIPE_API [OK]",
            "> STARTING_WORKER_SWARM...",
            "> AGENTS_ONLINE: 16",
            "> WAITING_FOR_COMMAND."
        ];
        let i = 0;
        const interval = setInterval(() => {
            if (i < sequence.length) {
                setLogs(prev => [...prev, sequence[i]]);
                i++;
            } else {
                clearInterval(interval);
            }
        }, 800);
        return () => clearInterval(interval);
    }, []);

    // Track mouse for parallax effect
    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            const x = (e.clientX / window.innerWidth - 0.5);
            const y = (e.clientY / window.innerHeight - 0.5);
            setMousePos({ x, y });
        };
        window.addEventListener('mousemove', handleMouseMove);
        return () => window.removeEventListener('mousemove', handleMouseMove);
    }, []);

    return (
        <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-[#020202] pt-20">
            {/* ─── SCENE BACKGROUND ─── */}
            <div className="absolute inset-0 bg-tech-grid opacity-20 pointer-events-none z-0" />
            <div className="absolute inset-0 z-0">
                <img
                    src="/root/.gemini/antigravity/brain/eaaa4a7a-8d33-4a12-b01d-322663287d37/momentai_business_os_1771770121942.png"
                    alt="Autonomous Business OS"
                    className="w-full h-full object-cover opacity-20 mix-blend-screen"
                />
            </div>
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-5xl h-[500px] bg-purple-600/20 blur-[150px] rounded-full mix-blend-screen pointer-events-none z-1" />
            <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#020202]/80 to-[#020202] z-1 pointer-events-none" />
            <div className="absolute top-0 w-full h-px bg-gradient-to-r from-transparent via-purple-500/80 to-transparent z-10" />

            {/* ─── TERMINAL OVERLAY ─── */}
            <div className="absolute top-28 left-6 hidden xl:block opacity-60">
                <div className="font-mono text-[11px] text-purple-400 space-y-1">
                    {logs.map((log, i) => (
                        <div key={i} className="animate-fade-in">{log}</div>
                    ))}
                    <div className="w-2 h-4 bg-purple-500 animate-blink inline-block" />
                </div>
            </div>

            {/* ─── FLOATING UI SHOWCASES (PARALLAX) ─── */}
            <FloatingCard delay={0} posObj={mousePos} className="top-[20%] left-[2%] xl:left-[8%] w-[260px] opacity-80 hover:opacity-100 z-10">
                <div className="flex items-center justify-between mb-3 border-b border-white/5 pb-2">
                    <span className="text-[10px] font-mono text-gray-500 flex items-center gap-1"><Terminal className="w-3 h-3" /> SALES_NODE</span>
                    <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                </div>
                <div className="flex items-start gap-3">
                    <div className="p-2 bg-green-500/10 rounded border border-green-500/30 text-green-400">
                        <Target className="w-5 h-5" />
                    </div>
                    <div>
                        <div className="text-sm font-bold text-white mb-1">Lead Scored: 98/100</div>
                        <div className="text-[10px] text-gray-400 font-mono">Found CTO at Series B startup. Drafted hyper-personalized email.</div>
                    </div>
                </div>
            </FloatingCard>

            <FloatingCard delay={1.5} posObj={{ x: -mousePos.x, y: -mousePos.y }} className="bottom-[20%] left-[2%] xl:left-[8%] w-[280px] opacity-80 hover:opacity-100 z-10">
                <div className="flex items-center justify-between mb-3 border-b border-white/5 pb-2">
                    <span className="text-[10px] font-mono text-gray-500 flex items-center gap-1"><Bot className="w-3 h-3" /> SUPPORT_SWARM</span>
                    <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                </div>
                <div className="space-y-2">
                    <div className="flex items-center justify-between text-xs">
                        <span className="text-gray-400">Tickets Resolved</span>
                        <span className="font-mono text-white">1,402</span>
                    </div>
                    <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                        <div className="bg-blue-500 h-full w-[85%]" />
                    </div>
                    <div className="flex items-center justify-between text-xs mt-1">
                        <span className="text-gray-400">Avg Resolution Time</span>
                        <span className="font-mono text-green-400">0m 45s</span>
                    </div>
                </div>
            </FloatingCard>

            {/* ─── UI CONTENT ─── */}
            <div className="relative z-20 text-center px-6 max-w-6xl mx-auto flex flex-col items-center">

                {/* Status Pill */}
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-purple-500/40 bg-purple-500/10 text-purple-200 font-mono text-xs mb-10 animate-fade-in-up backdrop-blur-md shadow-[0_0_20px_rgba(168,85,247,0.2)]">
                    <Sparkles className="w-3.5 h-3.5 text-purple-400" />
                    <span>MOMENTAIC V5.0 LIVE — LEVEL 4 AUTONOMY</span>
                </div>

                {/* Main Headline */}
                <h1 className="text-5xl sm:text-7xl md:text-8xl font-black text-white tracking-tighter mb-6 leading-tight animate-fade-in-up delay-[100ms]">
                    {t('hero.title_prefix')}<br />
                    <span>{t('hero.title_highlight')} </span>
                    <RotatingKeywords />
                </h1>

                {/* Subheadline */}
                <p className="text-lg md:text-2xl text-gray-400 max-w-3xl mx-auto mb-12 font-mono leading-relaxed animate-fade-in-up delay-[200ms]">
                    {t('hero.subtitle')}
                </p>

                {/* Use Case Tags */}
                <div className="flex flex-wrap items-center justify-center gap-3 mb-12 animate-fade-in-up delay-[300ms]">
                    <span className="text-xs font-mono text-gray-500 mr-2">USE_CASES:</span>
                    {["B2B Outbound", "Content Operations", "Customer Support", "Data Analysis", "DevOps Monitoring"].map((useCase) => (
                        <div key={useCase} className="flex items-center gap-1.5 px-3 py-1.5 rounded border border-white/10 bg-white/5 text-gray-300 text-xs font-mono">
                            <CheckCircle2 className="w-3 h-3 text-purple-500" /> {useCase}
                        </div>
                    ))}
                </div>

                {/* CTA Buttons */}
                <div className="flex flex-col sm:flex-row items-center justify-center gap-6 animate-fade-in-up delay-[400ms] w-full sm:w-auto">
                    <Link to="/signup" className="w-full sm:w-auto group">
                        <Button className="w-full sm:w-auto h-16 px-10 text-base font-bold font-mono bg-white text-black hover:bg-purple-500 hover:text-white transition-all clip-corner-4 shadow-[0_0_40px_rgba(255,255,255,0.15)] group-hover:shadow-[0_0_60px_rgba(168,85,247,0.4)]">
                            {t('hero.cta_primary')} <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
                        </Button>
                    </Link>

                    <Link to="/leaderboard" className="w-full sm:w-auto group">
                        <button className="w-full sm:w-auto h-16 px-8 text-sm font-mono text-gray-300 border border-white/10 hover:border-purple-500/50 hover:text-purple-400 hover:bg-purple-500/5 transition-all clip-corner-4 flex items-center justify-center gap-2">
                            <Zap className="w-4 h-4 text-gray-500 group-hover:text-purple-400 transition-colors" />
                            VIEW CASE STUDIES
                        </button>
                    </Link>
                </div>

                <div className="mt-8 flex items-center gap-4 text-xs font-mono text-gray-500 animate-fade-in-up delay-[500ms]">
                    <div className="flex -space-x-2">
                        {[1, 2, 3, 4].map((i) => (
                            <div key={i} className="w-8 h-8 rounded-full bg-gray-800 border-2 border-black flex items-center justify-center text-[10px] text-gray-400 overflow-hidden">
                                {String.fromCharCode(64 + i)}
                            </div>
                        ))}
                    </div>
                    <span>Trusted by 500+ YC & VC-backed founders</span>
                </div>
            </div>

            {/* ─── DECORATIVE DATA STREAM ─── */}
            <div className="absolute bottom-0 left-0 w-full h-12 bg-black/80 backdrop-blur-sm border-t border-purple-900/30 flex items-center overflow-hidden z-30">
                <div className="flex animate-marquee whitespace-nowrap gap-12 text-[11px] font-mono tracking-widest">
                    {Array(10).fill(0).map((_, i) => (
                        <div key={i} className="flex gap-8 items-center">
                            <span className="text-green-400 flex items-center gap-2"><div className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse" /> $$$ NEW_DEAL_CLOSED: $1,200</span>
                            <span className="text-purple-400 flex items-center gap-2"><TrendingUp className="w-3 h-3" /> ARR_GROWTH: +12%</span>
                            <span className="text-gray-400">USER_ACQUIRED: @founders_club</span>
                            <span className="text-blue-400 flex items-center gap-2"><Shield className="w-3 h-3" /> INFRA_HEALTH: 100%</span>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
