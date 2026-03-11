import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, Sparkles, Target, Zap, TrendingUp, MonitorPlay, ArrowRight } from 'lucide-react';

const FEATURES = [
    {
        id: 'ghost',
        title: 'Ghost Board',
        description: 'A deeply integrated synthetic brain trust. High-context AI personas of legendary operators instantly summoned to critique your strategies.',
        icon: Shield,
        color: 'from-red-500 to-orange-500',
        bg: 'bg-red-500/10'
    },
    {
        id: 'swarm',
        title: 'Agent Swarm',
        description: 'Deploy specialized autonomous agents for parallel execution. Scraping, analyzing, and synthesizing intelligence instantly.',
        icon: Sparkles,
        color: 'from-purple-500 to-pink-500',
        bg: 'bg-purple-500/10'
    },
    {
        id: 'prospector',
        title: 'Browser Prospector',
        description: 'Unleash Browser Use agents to visually navigate platforms like LinkedIn, finding your exact Ideal Customer Profile autonomously.',
        icon: Target,
        color: 'from-blue-500 to-cyan-500',
        bg: 'bg-blue-500/10'
    },
    {
        id: 'empire',
        title: 'Empire Builder',
        description: 'Transform disparate execution tasks into a unified, asymmetric growth machine. Scale infinitely without hiring.',
        icon: TrendingUp,
        color: 'from-emerald-500 to-teal-500',
        bg: 'bg-emerald-500/10'
    },
    {
        id: 'openclaw',
        title: 'OpenClaw Framework',
        description: 'Complete autonomy. Watch agents take over raw browser sessions via Live Agent View and execute complex workflows pixel by pixel.',
        icon: MonitorPlay,
        color: 'from-violet-500 to-fuchsia-500',
        bg: 'bg-violet-500/10'
    }
];

export default function WowOnboarding() {
    const navigate = useNavigate();
    const [activeFeature, setActiveFeature] = useState(0);

    // Auto-advance features slowly
    useEffect(() => {
        const timer = setInterval(() => {
            setActiveFeature((prev) => (prev + 1) % FEATURES.length);
        }, 4500);
        return () => clearInterval(timer);
    }, []);

    return (
        <div className="min-h-[90vh] flex flex-col items-center justify-center p-4 relative overflow-hidden bg-[#0A0A0A]">
            {/* Ambient background matching active feature */}
            <AnimatePresence mode="wait">
                <motion.div
                    key={FEATURES[activeFeature].id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 0.15 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 1 }}
                    className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] sm:w-[800px] sm:h-[800px] rounded-full blur-[120px] bg-gradient-to-tr ${FEATURES[activeFeature].color} pointer-events-none`}
                />
            </AnimatePresence>

            <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:32px_32px] pointer-events-none" />

            <div className="relative z-10 w-full max-w-6xl mx-auto flex flex-col items-center pt-8 pb-16">
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                    className="text-center mb-12"
                >
                    <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-xs font-mono uppercase tracking-widest text-gray-400 mb-6">
                        <Zap className="w-3.5 h-3.5 text-yellow-500" /> System Authorization
                    </div>
                    <h1 className="text-4xl sm:text-6xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-white via-gray-200 to-gray-500 mb-4 uppercase">
                        Welcome to MomentAIc
                    </h1>
                    <p className="text-gray-400 text-base sm:text-xl font-light max-w-2xl mx-auto">
                        You are entirely augmenting your operations with an infrastructure previously reserved for hyper-growth unicorns.
                    </p>
                </motion.div>

                {/* Dynamic Showcase Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 sm:gap-6 w-full mb-16">
                    {FEATURES.map((feature, idx) => {
                        const isActive = idx === activeFeature;
                        const Icon = feature.icon;

                        return (
                            <motion.div
                                key={feature.id}
                                onMouseEnter={() => setActiveFeature(idx)}
                                className={`relative p-6 rounded-3xl border transition-all duration-500 cursor-pointer overflow-hidden ${isActive
                                        ? 'bg-[#111111]/90 border-white/30 sm:col-span-2 lg:col-span-3 lg:row-span-2 shadow-2xl scale-[1.02]'
                                        : 'bg-black/50 border-white/5 hover:border-white/20'
                                    }`}
                                layout
                            >
                                {isActive && (
                                    <motion.div
                                        layoutId="activeFeatureGlow"
                                        className={`absolute inset-0 opacity-20 bg-gradient-to-br ${feature.color}`}
                                        transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
                                    />
                                )}

                                <div className={`w-12 h-12 rounded-2xl flex items-center justify-center mb-4 relative z-10 transition-colors duration-500 ${isActive ? 'bg-black' : feature.bg}`}>
                                    <Icon className={`w-6 h-6 transition-colors duration-500 ${isActive ? 'text-white' : 'text-gray-400'}`} />
                                </div>

                                <h3 className={`font-bold mb-2 relative z-10 uppercase tracking-wide transition-all duration-500 ${isActive ? 'text-2xl sm:text-3xl text-white' : 'text-base sm:text-lg text-gray-300'}`}>
                                    {feature.title}
                                </h3>

                                <AnimatePresence>
                                    {isActive && (
                                        <motion.p
                                            initial={{ opacity: 0, height: 0 }}
                                            animate={{ opacity: 1, height: 'auto' }}
                                            exit={{ opacity: 0, height: 0 }}
                                            className="text-gray-400 text-sm sm:text-base leading-relaxed relative z-10 font-mono mt-4"
                                        >
                                            {feature.description}
                                        </motion.p>
                                    )}
                                </AnimatePresence>
                            </motion.div>
                        );
                    })}
                </div>

                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 1, duration: 0.5 }}
                >
                    <button
                        onClick={() => navigate('/onboarding/genius')}
                        className="group relative px-8 py-5 bg-gradient-to-r from-[#111111] to-purple-800 text-white rounded-2xl font-bold text-lg overflow-hidden transition-all hover:scale-105 active:scale-95 shadow-2xl flex items-center gap-4"
                    >
                        <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity" />
                        Initialize Genius Setup
                        <ArrowRight className="w-5 h-5 group-hover:translate-x-2 transition-transform" />
                    </button>
                </motion.div>
            </div>
        </div>
    );
}
