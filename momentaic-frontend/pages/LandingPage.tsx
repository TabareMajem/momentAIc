import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/auth-store';
import { api } from '../lib/api';
import { Button } from '../components/ui/Button';
import { Logo } from '../components/ui/Logo';
import {
    ArrowRight, Target, FileText, Shield, CheckCircle2,
    TrendingUp, Eye, Sparkles, Rocket, MessageSquare,
    Zap, Globe, Cpu, ChevronRight, Play, Server, Activity,
    Terminal, Lock, Radio, Crosshair
} from 'lucide-react';
import { cn } from '../lib/utils';
import { useToast } from '../components/ui/Toast';

import { SentientHero } from '../components/landing/SentientHero';
import { EcosystemSection } from '../components/landing/EcosystemSection';
import { ProtocolShowcase } from '../components/landing/ProtocolShowcase';
import { AgentHive } from '../components/landing/AgentHive';
import { SystemStream } from '../components/landing/SystemStream';

// ─── UTILS ───
const TypewriterText = ({ text, delay = 0, speed = 50 }: { text: string, delay?: number, speed?: number }) => {
    const [displayed, setDisplayed] = useState('');
    const [start, setStart] = useState(false);

    useEffect(() => {
        const timeout = setTimeout(() => setStart(true), delay);
        return () => clearTimeout(timeout);
    }, [delay]);

    useEffect(() => {
        if (!start) return;
        let i = 0;
        const interval = setInterval(() => {
            if (i < text.length) {
                setDisplayed(text.substring(0, i + 1));
                i++;
            } else {
                clearInterval(interval);
            }
        }, speed);
        return () => clearInterval(interval);
    }, [text, speed, start]);

    return (
        <span className="font-mono text-purple-400">
            {displayed}
            <span className="cursor-block" />
        </span>
    );
};

// ─── COMPONENTS ───

const SectionHeader = ({ title, subtitle, id }: { title: string, subtitle: string, id: string }) => (
    <div className="relative mb-20">
        <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-purple-500/50 to-transparent" />
        <div className="flex justify-between items-center py-4 px-2 font-mono text-xs text-purple-500/70 uppercase tracking-widest">
            <span>/// SYSTEM_MODULE: {id}</span>
            <span>STATUS: ONLINE</span>
        </div>
        <div className="text-center mt-10">
            <h2 className="text-4xl md:text-5xl font-black uppercase tracking-tighter mb-4 glitch-text" data-text={title}>
                {title}
            </h2>
            <p className="text-gray-400 font-mono text-sm max-w-2xl mx-auto">
                <span className="text-purple-500 mr-2">{'>'}</span>
                {subtitle}
            </p>
        </div>
    </div>
);

const ModuleCard = ({ icon: Icon, title, desc, delay, visible = true }: { icon: any, title: string, desc: string, delay: number, visible?: boolean }) => (
    <div
        className={`group relative bg-[#0a0a0f]/60 backdrop-blur-xl border border-white/10 p-1 transition-all duration-700 hover:border-purple-500/50 clip-corner-4 transform ${visible ? 'translate-y-0 opacity-100' : 'translate-y-8 opacity-0'} hover:-translate-y-2 hover:shadow-[0_0_30px_rgba(168,85,247,0.15)]`}
        style={{ transitionDelay: `${delay}ms` }}
    >
        <div className="absolute inset-0 bg-tech-grid opacity-20" />
        <div className="relative h-full bg-[#050508] p-6 clip-corner-4 overflow-hidden">
            <div className="absolute top-0 right-0 p-2 opacity-50">
                <div className="w-16 h-16 border-t border-r border-white/10 rounded-tr-3xl" />
            </div>

            <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-purple-500/10 text-purple-400 rounded-sm border border-purple-500/20 group-hover:bg-purple-500/20 transition-colors">
                    <Icon className="w-5 h-5" />
                </div>
                <div className="font-mono text-xs text-gray-500 group-hover:text-purple-400/50 transition-colors">MOD_v2.4</div>
            </div>

            <h3 className="text-xl font-bold font-sans mb-2 group-hover:text-purple-400 transition-colors">{title}</h3>
            <p className="text-sm text-gray-400 leading-relaxed font-mono opacity-80">{desc}</p>

            <div className="mt-6 flex items-center justify-between border-t border-white/5 pt-4">
                <div className="flex items-center gap-1.5">
                    <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                    <span className="text-[10px] uppercase text-gray-500 tracking-wider">Active</span>
                </div>
                <div className="text-purple-500 opacity-0 transform translate-x-[-10px] group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-300">
                    <ArrowRight className="w-4 h-4" />
                </div>
            </div>
        </div>
    </div>
);

const AgentBadge = ({ agent, delay = 0, visible = true }: { agent: any, delay?: number, visible?: boolean }) => (
    <div
        className={`min-w-[300px] bg-[#0c0c12] border border-white/10 clip-id-card relative group hover:border-purple-500/40 transition-all duration-700 transform ${visible ? 'translate-y-0 opacity-100' : 'translate-y-12 opacity-0'}`}
        style={{ transitionDelay: `${delay}ms` }}
    >
        {/* Holographic Header */}
        <div className="h-24 bg-gradient-to-b from-purple-900/20 to-transparent p-4 flex justify-between items-start relative overflow-hidden">
            <div className="absolute inset-0 bg-tech-grid opacity-30" />
            <div className="relative z-10 w-12 h-12 bg-black border border-white/20 rounded flex items-center justify-center text-purple-400">
                {agent.icon}
            </div>
            <div className="text-right">
                <div className="text-[10px] font-mono text-purple-400">ID: {Math.random().toString(36).substr(2, 6).toUpperCase()}</div>
                <div className="text-[10px] font-mono text-gray-500">CLEARANCE: L4</div>
            </div>
        </div>

        {/* Info Body */}
        <div className="p-5 pt-2">
            <div className="mb-4">
                <h3 className="text-lg font-bold uppercase tracking-tight">{agent.name}</h3>
                <div className="inline-flex items-center gap-1 text-[10px] font-mono text-purple-400 border border-purple-500/20 px-1.5 py-0.5 mt-1 bg-purple-500/5">
                    <Activity className="w-3 h-3" /> {agent.role}
                </div>
            </div>

            <p className="text-xs text-gray-400 font-mono mb-4 border-l-2 border-white/10 pl-3 leading-relaxed">
                {agent.desc}
            </p>

            <div className="flex flex-col gap-1.5">
                {[1, 2, 3].map(i => (
                    <div key={i} className="h-1 w-full bg-white/5 overflow-hidden rounded-full">
                        <div className="h-full bg-purple-500/30 w-[60%] animate-pulse" style={{ width: `${Math.random() * 60 + 20}%` }} />
                    </div>
                ))}
            </div>
        </div>

        {/* Scanline Overlay */}
        <div className="absolute inset-0 pointer-events-none bg-[linear-gradient(rgba(18,16,16,0)50%,rgba(0,0,0,0.25)50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[length:100%_4px,3px_100%] opacity-20" />
    </div>
);

// ═══════════════════════════════════════════
// MAIN COMPONENT
// ═══════════════════════════════════════════

import { PageMeta } from '../components/ui/PageMeta';

export default function LandingPage() {
    const { isAuthenticated } = useAuthStore();
    const navigate = useNavigate();
    const { toast } = useToast();

    // ─── SCROLL HANDLER ───
    const [modulesVisible, setModulesVisible] = useState(false);
    const modulesRef = useRef<HTMLDivElement>(null);

    const [rosterVisible, setRosterVisible] = useState(false);
    const rosterRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        if (entry.target === modulesRef.current) setModulesVisible(true);
                        if (entry.target === rosterRef.current) setRosterVisible(true);
                    }
                });
            },
            { threshold: 0.1 }
        );

        if (modulesRef.current) observer.observe(modulesRef.current);
        if (rosterRef.current) observer.observe(rosterRef.current);

        return () => observer.disconnect();
    }, []);

    const handleCheckout = async (tier: string) => {
        if (!isAuthenticated) { navigate('/signup'); return; }
        try {
            await api.createCheckoutSession(tier);
        } catch (e) {
            toast({ type: 'error', title: 'Error', message: 'Initialization failed.' });
        }
    };

    return (
        <div className="min-h-screen bg-[#020202] text-white font-sans selection:bg-purple-500 text-selection-white overflow-x-hidden">
            <PageMeta
                title="MomentAIc | Autonomous Business Operating System"
                description="Hire an elite workforce of autonomous AI agents. MomentAIc replaces SaaS subscriptions with intelligent workers that scale your operations, sales, and marketing 24/7."
            />

            {/* ─── GLOBAL OVERLAYS ─── */}
            <div className="fixed inset-0 pointer-events-none z-50 bg-transparent opacity-[0.03] mix-blend-overlay" />
            <div className="fixed top-0 left-0 w-full h-1 bg-purple-600 z-50 animate-pulse-slow" />

            {/* ─── NAVBAR (System HUD) ─── */}
            <nav className="fixed top-0 w-full z-40 bg-[#020202]/80 backdrop-blur-md border-b border-white/5">
                <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <Logo collapsed={false} />
                        <div className="hidden md:flex gap-1">
                            <div className="w-1 h-1 bg-green-500 rounded-full animate-blink" />
                            <span className="text-[10px] font-mono text-green-500 tracking-widest">SYSTEM ONLINE</span>
                        </div>
                    </div>

                    <div className="flex items-center gap-6">
                        <div className="hidden md:flex gap-6 text-[11px] font-mono text-gray-500 uppercase tracking-widest">
                            <button onClick={() => document.getElementById('modules')?.scrollIntoView({ behavior: 'smooth' })} className="hover:text-purple-400 transition-colors">[ Modules ]</button>
                            <button onClick={() => document.getElementById('roster')?.scrollIntoView({ behavior: 'smooth' })} className="hover:text-purple-400 transition-colors">[ Roster ]</button>
                            <button onClick={() => document.getElementById('allocation')?.scrollIntoView({ behavior: 'smooth' })} className="hover:text-purple-400 transition-colors">[ Costs ]</button>
                        </div>

                        {isAuthenticated ? (
                            <Link to="/dashboard">
                                <Button className="h-8 px-4 text-xs font-mono bg-purple-600/20 text-purple-400 border border-purple-500/50 hover:bg-purple-600 hover:text-white clip-corner-4">
                                    ENTER_DASHBOARD
                                </Button>
                            </Link>
                        ) : (
                            <div className="flex items-center gap-4">
                                <Link to="/login" className="text-xs font-mono text-gray-400 hover:text-white">LOGIN</Link>
                                <Link to="/signup">
                                    <Button className="h-8 px-4 text-xs font-mono bg-white text-black hover:bg-purple-500 hover:text-white transition-all clip-corner-4 font-bold">
                                        INITIALIZE &gt;
                                    </Button>
                                </Link>
                            </div>
                        )}
                    </div>
                </div>
            </nav>

            {/* ─── V5 SENTIENT HERO ─── */}
            <SentientHero />

            {/* ─── SYSTEM EVENT STREAM (Proactive) ─── */}
            <SystemStream />

            {/* ─── ECOSYSTEM (The Brain) ─── */}
            <EcosystemSection />

            {/* ─── PROTOCOL SIMULATION (Show, Don't Tell) ─── */}
            <ProtocolShowcase />

            {/* ─── V5 THE HIVE (Full Roster) ─── */}
            <AgentHive />

            {/* ─── SYSTEM MODULES (Features) ─── */}
            <section id="modules" className="py-32 px-6 relative bg-[#030014]">
                <div className="absolute inset-0 bg-tech-grid opacity-10" />
                <div className="max-w-7xl mx-auto relative z-10">
                    <SectionHeader
                        id="SYS-01"
                        title="Autonomous Modules"
                        subtitle="Self-executing protocols designed for zero-touch operations."
                    />

                    <div ref={modulesRef} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        <ModuleCard
                            icon={Cpu}
                            title="The Live War Room"
                            desc="Watch specialized agents strictly debate growth strategies before you deploy them."
                            delay={0}
                            visible={modulesVisible}
                        />
                        <ModuleCard
                            icon={Globe}
                            title="Global Campaign Engine"
                            desc="Instantly synthesize localized GTM assets across 8+ dialects and regional nuances."
                            delay={100}
                            visible={modulesVisible}
                        />
                        <ModuleCard
                            icon={Activity}
                            title="Synthetic Call Center"
                            desc="Voice-native AI agents dialing real numbers to close leads and handle support 24/7."
                            delay={200}
                            visible={modulesVisible}
                        />
                        <ModuleCard
                            icon={Target}
                            title="AstroTurf Infiltration"
                            desc="Autonomous agents scanning Reddit & HackerNews to seed your product organically."
                            delay={300}
                            visible={modulesVisible}
                        />
                        <ModuleCard
                            icon={Zap}
                            title="Proactive Event Triggers"
                            desc="Hook Stripe and Slack to the Swarm. Instant reflexive execution when metrics drop."
                            delay={400}
                            visible={modulesVisible}
                        />
                        <ModuleCard
                            icon={Terminal}
                            title="OpenClaw Internet Proxy"
                            desc="Break free from APIs. Deploy headless browser agents that click, type, and navigate."
                            delay={500}
                            visible={modulesVisible}
                        />
                    </div>
                </div>
            </section>

            {/* ─── ACTIVE ROSTER (Agents) ─── */}
            <section id="roster" className="py-32 border-y border-white/5 bg-[#050508] relative overflow-hidden">
                <div className="max-w-7xl mx-auto px-6 mb-12">
                    <SectionHeader
                        id="SYS-02"
                        title="Active Personnel"
                        subtitle="16 Specialized AI Units. Verified. Operational. Ready."
                    />
                </div>

                {/* Horizontal Scroll Area */}
                <div ref={rosterRef} className="flex gap-6 overflow-x-auto pb-12 px-6 lg:px-[calc(50vw-600px)] hide-scrollbar snap-x snap-mandatory">
                    {[
                        { name: 'Sales Hunter', role: 'REVENUE_OPS', icon: <Target />, desc: 'Autonomous lead generation and qualification unit. Scrapes LinkedIn/Twitter.' },
                        { name: 'Content Engine', role: 'MARKETING_OPS', icon: <FileText />, desc: 'Generates viral tweets, blog posts, and newsletters based on trending topics.' },
                        { name: 'Growth Hacker', role: 'SCALE_OPS', icon: <TrendingUp />, desc: 'Optimizes landing page usage and SEO keywords for maximum conversion.' },
                        { name: 'Competitor Intel', role: 'RECON_OPS', icon: <Eye />, desc: 'Monitors competitor pricing and feature releases. Alerts on changes.' },
                        { name: 'Legal Sentinel', role: 'COMPLIANCE', icon: <Shield />, desc: 'Drafts contracts, NDAs, and privacy policies instantly.' },
                        { name: 'DevOps Guard', role: 'INFRASTRUCTURE', icon: <Terminal />, desc: 'Monitors uptime, deployments, and container health.' },
                    ].map((agent, i) => (
                        <div key={i} className="snap-center">
                            <AgentBadge agent={agent} delay={i * 150} visible={rosterVisible} />
                        </div>
                    ))}

                    {/* "More" Card */}
                    <div className="min-w-[300px] flex items-center justify-center border border-white/5 border-dashed rounded-xl bg-white/[0.02]">
                        <Link to="/signup" className="text-gray-500 font-mono text-sm hover:text-purple-400 flex flex-col items-center gap-2">
                            <span>[ VIEW FULL ROSTER ]</span>
                            <ArrowRight className="w-4 h-4" />
                        </Link>
                    </div>
                </div>
            </section>

            {/* ─── SOCIAL PROOF ─── */}
            <section className="py-20 px-6 border-y border-white/5 bg-[#030014] relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-r from-purple-900/5 via-transparent to-blue-900/5" />
                <div className="max-w-7xl mx-auto relative z-10">
                    <div className="text-center mb-12">
                        <div className="text-[10px] font-mono text-purple-400 tracking-[0.3em] mb-3">SYSTEM_METRICS</div>
                        <h2 className="text-2xl font-bold text-white">Trusted by Forward-Thinking Founders</h2>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
                        {[
                            { metric: '16+', label: 'AI Agents Active', icon: '🤖' },
                            { metric: '99.99%', label: 'System Uptime', icon: '⚡' },
                            { metric: '24/7', label: 'Autonomous Ops', icon: '🔄' },
                            { metric: '<120s', label: 'Deploy Time', icon: '🚀' },
                        ].map((stat, i) => (
                            <div key={i} className="text-center group">
                                <div className="text-3xl mb-2">{stat.icon}</div>
                                <div className="text-3xl md:text-4xl font-mono font-bold text-white mb-1 group-hover:text-purple-400 transition-colors">{stat.metric}</div>
                                <div className="text-[10px] font-mono text-gray-500 uppercase tracking-widest">{stat.label}</div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ─── RESOURCE ALLOCATION (Pricing) ─── */}
            <section id="allocation" className="py-32 px-6 bg-[#020202] relative">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-purple-600/5 rounded-full blur-[150px]" />
                <div className="max-w-7xl mx-auto relative z-10">
                    <SectionHeader
                        id="SYS-03"
                        title="Resource Allocation"
                        subtitle="Select compute power level."
                    />

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
                        {/* Plan 1 */}
                        <div className="border border-white/10 bg-[#0a0a0f]/60 backdrop-blur-xl p-8 clip-corner-2 hover:border-gray-400 transition-all duration-300 hover:shadow-[0_0_30px_rgba(255,255,255,0.03)] group">
                            <div className="text-xs font-mono text-gray-500 mb-2">TIER_1</div>
                            <h3 className="text-2xl font-bold text-white mb-4 group-hover:text-gray-100">Starter</h3>
                            <div className="text-4xl font-mono text-white mb-1">$9<span className="text-sm text-gray-500">/mo</span></div>
                            <div className="text-[10px] font-mono text-gray-600 mb-6">Perfect for solo founders</div>
                            <ul className="space-y-3 font-mono text-xs text-gray-400 mb-8">
                                <li className="flex gap-2 items-center"><div className="w-1.5 h-1.5 bg-gray-500 rounded-full" /> 100 Credits/mo</li>
                                <li className="flex gap-2 items-center"><div className="w-1.5 h-1.5 bg-gray-500 rounded-full" /> Basic Agent Access</li>
                                <li className="flex gap-2 items-center"><div className="w-1.5 h-1.5 bg-gray-500 rounded-full" /> 1 Startup Profile</li>
                                <li className="flex gap-2 items-center"><div className="w-1.5 h-1.5 bg-gray-500 rounded-full" /> Email Support</li>
                            </ul>
                            <Button onClick={() => handleCheckout('starter')} className="w-full h-10 bg-white/5 border border-white/20 hover:bg-white/10 font-mono text-xs uppercase tracking-widest transition-all duration-300">
                                Deploy Unit
                            </Button>
                        </div>

                        {/* Plan 2 (Highlighted) */}
                        <div className="relative border border-purple-500/50 bg-[#0f0f16] p-8 clip-corner-2 transform md:scale-105 shadow-[0_0_60px_rgba(168,85,247,0.15)] hover:shadow-[0_0_80px_rgba(168,85,247,0.25)] transition-all duration-500 group">
                            <div className="absolute -top-px -left-px -right-px h-px bg-gradient-to-r from-transparent via-purple-500 to-transparent" />
                            <div className="absolute top-0 right-0 bg-gradient-to-r from-purple-600 to-purple-500 text-white text-[10px] font-bold px-3 py-1 font-mono rounded-bl-lg">MOST POPULAR</div>
                            <div className="text-xs font-mono text-purple-400 mb-2">TIER_2</div>
                            <h3 className="text-2xl font-bold text-white mb-4">Growth</h3>
                            <div className="text-4xl font-mono text-white mb-1">$19<span className="text-sm text-gray-500">/mo</span></div>
                            <div className="text-[10px] font-mono text-purple-400/60 mb-6">Best for growing startups</div>
                            <ul className="space-y-3 font-mono text-xs text-gray-300 mb-8">
                                <li className="flex gap-2 items-center"><div className="w-1.5 h-1.5 bg-purple-500 rounded-full animate-pulse" /> 500 Credits/mo</li>
                                <li className="flex gap-2 items-center"><div className="w-1.5 h-1.5 bg-purple-500 rounded-full animate-pulse" /> Full Swarm Access</li>
                                <li className="flex gap-2 items-center"><div className="w-1.5 h-1.5 bg-purple-500 rounded-full animate-pulse" /> Sales Automation</li>
                                <li className="flex gap-2 items-center"><div className="w-1.5 h-1.5 bg-purple-500 rounded-full animate-pulse" /> 5 Startup Profiles</li>
                                <li className="flex gap-2 items-center"><div className="w-1.5 h-1.5 bg-purple-500 rounded-full animate-pulse" /> Priority Support</li>
                            </ul>
                            <Button onClick={() => handleCheckout('growth')} className="w-full h-10 bg-gradient-to-r from-purple-600 to-purple-500 hover:from-purple-500 hover:to-purple-400 text-white font-mono text-xs uppercase tracking-widest shadow-lg shadow-purple-900/50 transition-all duration-300">
                                Deploy Unit →
                            </Button>
                        </div>

                        {/* Plan 3 */}
                        <div className="border border-white/10 bg-[#0a0a0f]/60 backdrop-blur-xl p-8 clip-corner-2 hover:border-blue-500/30 transition-all duration-300 hover:shadow-[0_0_30px_rgba(59,130,246,0.05)] group">
                            <div className="text-xs font-mono text-blue-400 mb-2">TIER_3</div>
                            <h3 className="text-2xl font-bold text-white mb-4 group-hover:text-blue-100">God Mode</h3>
                            <div className="text-4xl font-mono text-white mb-1">$39<span className="text-sm text-gray-500">/mo</span></div>
                            <div className="text-[10px] font-mono text-blue-400/60 mb-6">Unlimited everything</div>
                            <ul className="space-y-3 font-mono text-xs text-gray-400 mb-8">
                                <li className="flex gap-2 items-center"><div className="w-1.5 h-1.5 bg-blue-500 rounded-full" /> 2000 Credits/mo</li>
                                <li className="flex gap-2 items-center"><div className="w-1.5 h-1.5 bg-blue-500 rounded-full" /> Unlimited Startups</li>
                                <li className="flex gap-2 items-center"><div className="w-1.5 h-1.5 bg-blue-500 rounded-full" /> Full API Access</li>
                                <li className="flex gap-2 items-center"><div className="w-1.5 h-1.5 bg-blue-500 rounded-full" /> White-glove Onboarding</li>
                                <li className="flex gap-2 items-center"><div className="w-1.5 h-1.5 bg-blue-500 rounded-full" /> Dedicated Support</li>
                            </ul>
                            <Button onClick={() => handleCheckout('god_mode')} className="w-full h-10 bg-white/5 border border-blue-500/30 hover:bg-blue-900/20 hover:border-blue-500/50 font-mono text-xs uppercase tracking-widest transition-all duration-300">
                                Deploy Unit
                            </Button>
                        </div>
                    </div>
                </div>
            </section>

            {/* ─── AMBASSADOR CTA ─── */}
            <section className="py-20 px-6 bg-gradient-to-r from-[#0a0014] via-[#050508] to-[#000a14] border-y border-white/5">
                <div className="max-w-4xl mx-auto text-center">
                    <div className="inline-flex items-center gap-2 bg-purple-500/10 border border-purple-500/20 px-4 py-1.5 rounded-full mb-6">
                        <span className="text-[10px] font-mono text-purple-400 tracking-widest">💰 EARN WITH US</span>
                    </div>
                    <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Become an Ambassador</h2>
                    <p className="text-gray-400 font-mono text-sm mb-8 max-w-2xl mx-auto">
                        Earn up to 30% recurring commissions. Share your referral link, track conversions in real-time, and get paid via Stripe Connect.
                    </p>
                    <div className="flex flex-col sm:flex-row gap-4 justify-center">
                        <Link to="/ambassador">
                            <Button className="h-12 px-8 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white font-mono text-sm uppercase tracking-widest shadow-lg shadow-purple-900/30">
                                Apply Now →
                            </Button>
                        </Link>
                        <div className="flex items-center gap-6 justify-center">
                            <div className="text-center">
                                <div className="text-lg font-bold text-white font-mono">20-30%</div>
                                <div className="text-[9px] text-gray-500 font-mono">COMMISSION</div>
                            </div>
                            <div className="w-px h-8 bg-white/10" />
                            <div className="text-center">
                                <div className="text-lg font-bold text-white font-mono">RECURRING</div>
                                <div className="text-[9px] text-gray-500 font-mono">MONTHLY</div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* ─── FOOTER (Boot Log) ─── */}
            <footer className="border-t border-white/10 bg-[#020202] py-16 px-6">
                <div className="max-w-7xl mx-auto">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
                        {/* Brand */}
                        <div className="md:col-span-2">
                            <Logo collapsed={false} />
                            <p className="mt-4 text-sm font-mono text-gray-500 max-w-md">
                                The autonomous AI operating system for startups. 16 specialized agents working 24/7 to grow your business.
                            </p>
                            <div className="flex items-center gap-2 mt-4">
                                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                                <span className="text-[10px] font-mono text-green-500 tracking-widest">ALL SYSTEMS OPERATIONAL</span>
                            </div>
                        </div>

                        {/* Product */}
                        <div>
                            <div className="text-[10px] font-mono text-gray-400 uppercase tracking-widest mb-4">PRODUCT</div>
                            <div className="space-y-3">
                                <Link to="/signup" className="block text-xs font-mono text-gray-500 hover:text-purple-400 transition-colors">Get Started</Link>
                                <Link to="/login" className="block text-xs font-mono text-gray-500 hover:text-purple-400 transition-colors">Sign In</Link>
                                <Link to="/ambassador" className="block text-xs font-mono text-gray-500 hover:text-purple-400 transition-colors">Ambassador Program</Link>
                            </div>
                        </div>

                        {/* Legal */}
                        <div>
                            <div className="text-[10px] font-mono text-gray-400 uppercase tracking-widest mb-4">LEGAL</div>
                            <div className="space-y-3">
                                <Link to="/privacy" className="block text-xs font-mono text-gray-500 hover:text-purple-400 transition-colors">Privacy Policy</Link>
                                <Link to="/terms" className="block text-xs font-mono text-gray-500 hover:text-purple-400 transition-colors">Terms of Service</Link>
                                <a href="https://twitter.com/momentaic" target="_blank" rel="noopener noreferrer" className="block text-xs font-mono text-gray-500 hover:text-purple-400 transition-colors">Twitter / X →</a>
                            </div>
                        </div>
                    </div>

                    <div className="border-t border-white/5 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
                        <div className="font-mono text-[10px] text-gray-700">
                            SYSTEM_ID: MOMENTAIC_CORE_v5.0 | LOC: SAN FRANCISCO, CA
                        </div>
                        <div className="text-[10px] text-gray-700 font-mono">
                            COPYRIGHT © 2026 MOMENTAIC INC. ALL SYSTEMS SECURED.
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    );
}
