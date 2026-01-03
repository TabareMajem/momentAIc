
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bot, Zap, Globe, Rocket, Terminal, X, CheckCircle } from 'lucide-react';
import { Button } from './ui/Button';

export const OnboardingTour = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [step, setStep] = useState(0);

    useEffect(() => {
        const hasSeenTour = localStorage.getItem('has_seen_onboarding_tour_v1');
        if (!hasSeenTour) {
            // Small delay to let the dashboard load first
            setTimeout(() => setIsOpen(true), 1000);
        }
    }, []);

    const handleComplete = () => {
        localStorage.setItem('has_seen_onboarding_tour_v1', 'true');
        setIsOpen(false);
    };

    if (!isOpen) return null;

    const steps = [
        {
            title: "WELCOME TO MISSION CONTROL",
            icon: <Terminal className="w-12 h-12 text-[#00f0ff]" />,
            desc: "You have just activated MomentAIc, the world's first AI Operating System for Entrepreneurs.",
            highlight: "This is not a chat bot. It is a workforce.",
            image: "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=2070&auto=format&fit=crop"
        },
        {
            title: "16+ SPECIALIZED AGENTS",
            icon: <Bot className="w-12 h-12 text-[#a855f7]" />,
            desc: "From Legal Counsel to Growth Hackers. Your new co-founders are standing by 24/7.",
            highlight: "No more solo founding. You have a team now.",
            image: "https://images.unsplash.com/photo-1531746790731-6c087fecd65a?q=80&w=2006&auto=format&fit=crop"
        },
        {
            title: "NEURAL SIGNAL ENGINE",
            icon: <Globe className="w-12 h-12 text-[#3b82f6]" />,
            desc: "We scan millions of data points across Reddit, X, and LinkedIn to find trends before they happen.",
            highlight: "Validate your ideas with real market data.",
            image: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop"
        },
        {
            title: "LIVE EXECUTION",
            icon: <Zap className="w-12 h-12 text-[#00f0ff]" />,
            desc: "Your agents don't just talk. They act. Watch them browse the web, fill forms, and execute tasks live.",
            highlight: "Autonomous. Real-time. Powerful.",
            image: "https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?q=80&w=2070&auto=format&fit=crop"
        }
    ];

    const currentStep = steps[step];

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
            >
                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 pointer-events-none"></div>

                <motion.div
                    initial={{ scale: 0.9, opacity: 0, y: 20 }}
                    animate={{ scale: 1, opacity: 1, y: 0 }}
                    className="relative w-full max-w-4xl bg-[#050505] border border-white/10 rounded-2xl shadow-2xl overflow-hidden flex flex-col md:flex-row h-[600px]"
                >
                    {/* Left: Image/Visual */}
                    <div className="w-full md:w-1/2 relative overflow-hidden group">
                        <div className="absolute inset-0 bg-brand-gradient opacity-20 mix-blend-overlay"></div>
                        <img
                            src={currentStep.image}
                            alt={currentStep.title}
                            className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-[#050505] via-transparent to-transparent"></div>

                        <div className="absolute bottom-8 left-8 right-8">
                            <div className="w-12 h-1 bg-[#00f0ff] mb-4"></div>
                            <h4 className="text-[#00f0ff] font-mono tracking-widest text-sm mb-2">SYSTEM_OVERVIEW // 0{step + 1}</h4>
                        </div>
                    </div>

                    {/* Right: Content */}
                    <div className="w-full md:w-1/2 p-8 md:p-12 flex flex-col justify-between relative bg-[#0a0a0a]">
                        <div className="absolute top-0 right-0 p-4">
                            <button onClick={handleComplete} className="text-gray-500 hover:text-white transition-colors">
                                <X className="w-6 h-6" />
                            </button>
                        </div>

                        <div className="space-y-6 mt-8">
                            <motion.div
                                key={step} // Animate on step change
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ duration: 0.3 }}
                            >
                                <div className="mb-6 p-4 bg-white/5 rounded-2xl w-fit border border-white/10">
                                    {currentStep.icon}
                                </div>
                                <h2 className="text-3xl md:text-4xl font-bold font-sans text-white mb-4 tracking-tight leading-tight">
                                    {currentStep.title}
                                </h2>
                                <p className="text-gray-400 text-lg leading-relaxed">
                                    {currentStep.desc}
                                </p>
                                <div className="mt-6 pl-4 border-l-2 border-[#00f0ff]">
                                    <p className="text-[#00f0ff] font-mono text-sm uppercase tracking-wider">
                                        {currentStep.highlight}
                                    </p>
                                </div>
                            </motion.div>
                        </div>

                        {/* Footer Controls */}
                        <div className="flex items-center justify-between mt-8 pt-8 border-t border-white/5">
                            <div className="flex gap-2">
                                {steps.map((_, i) => (
                                    <div
                                        key={i}
                                        className={`h-1.5 rounded-full transition-all duration-300 ${i === step ? 'w-8 bg-[#00f0ff]' : 'w-2 bg-white/20'}`}
                                    />
                                ))}
                            </div>

                            <div className="flex gap-4">
                                {step < steps.length - 1 ? (
                                    <Button
                                        variant="cyber"
                                        onClick={() => setStep(step + 1)}
                                        className="group"
                                    >
                                        NEXT SEQUENCE <Rocket className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                                    </Button>
                                ) : (
                                    <Button
                                        variant="brand"
                                        onClick={handleComplete}
                                        className="shadow-[0_0_30px_rgba(168,85,247,0.5)] hover:shadow-[0_0_50px_rgba(168,85,247,0.7)]"
                                    >
                                        ENTER MISSION CONTROL <CheckCircle className="w-4 h-4 ml-2" />
                                    </Button>
                                )}
                            </div>
                        </div>
                    </div>
                </motion.div>
            </motion.div>
        </AnimatePresence>
    );
};
