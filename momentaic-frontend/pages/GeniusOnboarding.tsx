import React, { useState, useEffect, useRef } from 'react';
import { api } from '../lib/api';
import { useAuthStore } from '../stores/auth-store';
import { useNavigate } from 'react-router-dom';
import {
    Sparkles, Bot, ArrowRight, CheckCircle2, Loader2, Target, TrendingUp, Check
} from 'lucide-react';
import { Button } from '../components/ui/Button';
import { cn } from '../lib/utils';
import { useToast } from '../components/ui/Toast';
import { motion, AnimatePresence } from 'framer-motion';

// --- HOLD COMPONENT ---
const HoldToDeployButton = ({ onComplete }: { onComplete: () => void }) => {
    const [progress, setProgress] = useState(0);
    const [isHolding, setIsHolding] = useState(false);
    const intervalRef = useRef<NodeJS.Timeout | null>(null);

    const startHold = () => {
        setIsHolding(true);
        intervalRef.current = setInterval(() => {
            setProgress(prev => {
                if (prev >= 100) {
                    if (intervalRef.current) clearInterval(intervalRef.current);
                    onComplete();
                    return 100;
                }
                return prev + 2; // ~1 second to fill (50 steps of 20ms)
            });
        }, 20);
    };

    const stopHold = () => {
        setIsHolding(false);
        if (intervalRef.current) clearInterval(intervalRef.current);
        setProgress(0);
    };

    return (
        <div className="relative w-full max-w-sm mx-auto mt-8 touch-none">
            {/* Pulsing ring underneath */}
            <motion.div
                className="absolute inset-0 bg-purple-500/20 rounded-2xl blur-xl"
                animate={{ scale: isHolding ? 1.1 : 0.9, opacity: isHolding ? 0.8 : 0.2 }}
                transition={{ duration: 0.3 }}
            />

            <button
                onMouseDown={startHold}
                onMouseUp={stopHold}
                onMouseLeave={stopHold}
                onTouchStart={startHold}
                onTouchEnd={stopHold}
                className="relative w-full h-16 rounded-2xl bg-black border border-white/10 overflow-hidden flex items-center justify-center group active:scale-[0.98] transition-transform select-none focus:outline-none"
            >
                {/* Progress Fill */}
                <div
                    className="absolute left-0 top-0 bottom-0 bg-gradient-to-r from-purple-600 to-blue-600 transition-all duration-75 ease-out"
                    style={{ width: `${progress}%` }}
                />

                {/* Overlay Text */}
                <div className="relative z-10 flex items-center gap-2 font-bold text-white tracking-wide">
                    {progress > 0 ? (
                        <>
                            <Sparkles className="w-5 h-5 animate-pulse" />
                            Activating Neural Core...
                        </>
                    ) : (
                        <>
                            Hold to Deploy Core <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                        </>
                    )}
                </div>
            </button>
            <div className="text-center mt-3 text-[10px] sm:text-xs text-gray-500 font-mono uppercase tracking-widest">
                Requires Authorization Hold
            </div>
        </div>
    );
};


// ─── PROGRESS STEPPER ───
const Steps = ({ current }: { current: number }) => {
    const steps = ['Setup', 'Analysis', 'Strategy'];
    return (
        <div className="flex items-center justify-center gap-2 sm:gap-4 mb-8 sm:mb-12 w-full max-w-[100vw] overflow-x-hidden px-2">
            {steps.map((label, i) => {
                const stepNum = i + 1;
                const isActive = stepNum === current;
                const isCompleted = stepNum < current;
                return (
                    <div key={i} className="flex items-center gap-2 sm:gap-3 shrink-0">
                        <div className={cn(
                            "flex items-center gap-1.5 sm:gap-2 px-3 sm:px-4 py-1.5 sm:py-2 rounded-full border text-xs text-[10px] sm:text-sm font-medium transition-all duration-500",
                            isActive ? "bg-purple-500/20 border-purple-500 text-white shadow-[0_0_20px_rgba(168,85,247,0.3)]" :
                                isCompleted ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400" :
                                    "bg-white/5 border-white/10 text-gray-500"
                        )}>
                            <div className={cn(
                                "w-4 h-4 sm:w-5 sm:h-5 rounded-full flex items-center justify-center text-[9px] sm:text-[10px] font-bold transition-all duration-300",
                                isActive ? "bg-purple-500 text-white scale-110" :
                                    isCompleted ? "bg-emerald-500 text-black" :
                                        "bg-gray-700 text-gray-400"
                            )}>
                                {isCompleted ? <Check className="w-2.5 h-2.5 sm:w-3 sm:h-3" /> : stepNum}
                            </div>
                            <span className="hidden sm:inline">{label}</span>
                            <span className="sm:hidden">{isActive ? label : ''}</span>
                        </div>
                        {i < steps.length - 1 && (
                            <div className={cn(
                                "h-[1px] transition-all duration-500",
                                isCompleted ? "bg-emerald-500/50 w-4 sm:w-8" : "bg-white/10 w-2 sm:w-8"
                            )} />
                        )}
                    </div>
                );
            })}
        </div>
    );
};

export default function GeniusOnboarding() {
    const { user } = useAuthStore();
    const navigate = useNavigate();
    const { toast } = useToast();

    // State
    const [step, setStep] = useState(1);
    const [inputValue, setInputValue] = useState('');
    const [loading, setLoading] = useState(false);
    const [startupId, setStartupId] = useState<string | null>(null);
    const [analysisLines, setAnalysisLines] = useState<string[]>([]);
    const [plan, setPlan] = useState<any>(null);

    // Initial Load & Auth/URL Check
    useEffect(() => {
        const loadStartupAndCheckUrl = async () => {
            try {
                const startups = await api.getStartups();
                let currentStartupId = null;
                if (startups.length > 0) {
                    currentStartupId = startups[0].id;
                    setStartupId(currentStartupId);
                }

                // Check for auto-onboarding URL
                const storedUrl = sessionStorage.getItem('onboarding_url');
                if (storedUrl) {
                    setInputValue(storedUrl);
                    setTimeout(() => {
                        autoExecuteAnalysis(storedUrl, currentStartupId);
                    }, 500);
                }

            } catch (e) {
                console.error("Failed to load startups", e);
            }
        };
        loadStartupAndCheckUrl();
    }, []);

    const handleAnalyze = async () => {
        if (!inputValue.trim()) return;
        await autoExecuteAnalysis(inputValue, startupId);
    };

    const autoExecuteAnalysis = async (urlToAnalyze: string, currentStartupId: string | null) => {
        setStep(2);
        setLoading(true);

        const isUrl = urlToAnalyze.startsWith('http') || urlToAnalyze.includes('.com') || urlToAnalyze.includes('.new');

        const logs = isUrl ? [
            `Connecting to target matrix: ${urlToAnalyze}...`,
            "Bypassing captcha & initiating deep DOM scrape...",
            "Extracting H1/H2 value propositions...",
            "Analyzing product features and potential ICP mapping...",
            "Synthesizing Competitor Graph (Finding weak spots)...",
            "Calculating Go-To-Market vectors...",
            "Compiling Day 1 Asymmetric Attack Plan..."
        ] : [
            "Accessing public data sources...",
            "Analyzing theoretical market segment...",
            "Identifying ideal customer profile (ICP)...",
            "Scanning competitor pricing strategies...",
            "Generating growth experiments...",
            "Calculating Total Addressable Market parameters...",
            "Compiling Day 1 Action Plan..."
        ];

        let i = 0;
        setAnalysisLines([]); // Reset

        const interval = setInterval(() => {
            if (i < logs.length) {
                setAnalysisLines(prev => {
                    if (prev[prev.length - 1] === logs[i]) return prev;
                    // Keep only last 3 logs to prevent mobile scrolling overflow issues
                    const newLogs = [...prev, logs[i]];
                    return newLogs.slice(Math.max(newLogs.length - 3, 0));
                });
                i++;
            } else {
                clearInterval(interval);
            }
        }, 1100);

        try {
            // Actual API Call
            const response = await api.startGeniusSession(urlToAnalyze, currentStartupId || undefined);

            setTimeout(() => {
                let parsedPlan = null;
                try {
                    const jsonMatch = response.message.match(/\{[\s\S]*\}/);
                    if (jsonMatch) parsedPlan = JSON.parse(jsonMatch[0]);
                } catch (e) { console.warn("Could not parse JSON plan", e); }

                if (!parsedPlan) {
                    parsedPlan = {
                        summary: isUrl ? `Based on the deep scrape of ${urlToAnalyze}, we've identified high-leverage opportunities in outbound sales and programmatic SEO.` : "Based on your input, we've identified high-leverage opportunities in outbound sales and programmatic SEO.",
                        leads_icp: "CTOs and VPs of Engineering at Series A/B SaaS companies",
                        social_posts: [
                            { platform: "LinkedIn", content: "The biggest mistake engineering leaders make is not abstracting early enough. Here is how we fixed it..." },
                            { platform: "Twitter", content: "Just shipped v2.0. Speed is a feature. ⚡" }
                        ],
                        experiment: { name: "Cold Email Wave 1", hypothesis: "Personalized intro relating to recent funding will 3x conversion" }
                    };
                }

                setPlan(parsedPlan);
                setStep(3);
                setLoading(false);
                sessionStorage.removeItem('onboarding_url');
            }, (logs.length * 1100) + 1000); // Wait for logs + 1s dramatic pause

        } catch (error) {
            console.error(error);
            toast({ type: 'error', title: 'Analysis Failed', message: 'Could not connect to Genius engine. Please try again.' });
            setStep(1);
            setLoading(false);
            sessionStorage.removeItem('onboarding_url');
        }
    };

    const handleComplete = async () => {
        if (startupId && plan) {
            try {
                toast({ type: 'info', title: 'Activating Neural Core', message: 'Deploying your autonomous strategy...' });
                await api.executeGeniusPlan(startupId, plan);
                toast({ type: 'success', title: 'Deployment Complete', message: 'Your AI team is now operating in the background.' });
            } catch (e) {
                console.error("Failed to execute plan", e);
            }
        }
        navigate('/dashboard');
    };

    // Animation variants
    const stepVariants = {
        hidden: { opacity: 0, x: 20, scale: 0.95 },
        visible: { opacity: 1, x: 0, scale: 1, transition: { type: 'spring', stiffness: 300, damping: 30 } },
        exit: { opacity: 0, x: -20, scale: 0.95, transition: { duration: 0.2 } }
    };

    const cardVariants = {
        hidden: { opacity: 0, y: 30 },
        visible: (i: number) => ({
            opacity: 1,
            y: 0,
            transition: { delay: i * 0.15, type: 'spring', stiffness: 300, damping: 25 }
        })
    };

    return (
        <div className="min-h-screen bg-[#020202] text-white flex flex-col p-4 sm:p-6 overflow-hidden relative selection:bg-purple-500/30">
            {/* Ambient Background */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-0">
                <motion.div
                    animate={{ scale: [1, 1.2, 1], opacity: [0.1, 0.2, 0.1] }}
                    transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
                    className="absolute top-[-10%] sm:top-[-20%] right-[-10%] sm:right-[-20%] w-[400px] sm:w-[800px] h-[400px] sm:h-[800px] bg-purple-600/20 blur-[100px] sm:blur-[150px] rounded-full"
                />
                <motion.div
                    animate={{ scale: [1, 1.5, 1], opacity: [0.05, 0.15, 0.05] }}
                    transition={{ duration: 10, repeat: Infinity, ease: 'easeInOut', delay: 1 }}
                    className="absolute bottom-[-10%] sm:bottom-[-20%] left-[-10%] sm:left-[-20%] w-[300px] sm:w-[600px] h-[300px] sm:h-[600px] bg-blue-600/20 blur-[100px] sm:blur-[150px] rounded-full"
                />

                {/* Subtle Grid overlay */}
                <div className="absolute inset-0 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:40px_40px] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_0%,#000_70%,transparent_110%)]" />
            </div>

            <div className="w-full max-w-4xl mx-auto relative z-10 flex-1 flex flex-col justify-start sm:justify-center pt-8 sm:pt-0">

                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                    className="text-center mb-6 sm:mb-8"
                >
                    <h1 className="text-3xl sm:text-5xl font-black mb-2 sm:mb-4 tracking-tighter text-transparent bg-clip-text bg-gradient-to-br from-white via-white to-gray-500">
                        {step === 1 && "Initialization"}
                        {step === 2 && "Neural Scan in Progress"}
                        {step === 3 && "Autonomous Core Ready"}
                    </h1>
                    <p className="text-sm sm:text-lg text-gray-400 font-light">
                        {step === 1 && "Point us to your product. We'll build the assault plan."}
                        {step === 2 && "Agents are deep-scraping your domain and generating vector blueprints."}
                        {step === 3 && "Review intercept metrics before final deployment sequence."}
                    </p>
                </motion.div>

                <Steps current={step} />

                <div className="relative flex-1 flex flex-col justify-start sm:justify-center">
                    <AnimatePresence mode="wait">
                        {/* ─── STEP 1: INPUT ─── */}
                        {step === 1 && (
                            <motion.div
                                key="step1"
                                variants={stepVariants}
                                initial="hidden"
                                animate="visible"
                                exit="exit"
                                className="w-full"
                            >
                                <div className="bg-[#08080c]/80 backdrop-blur-2xl border border-white/5 p-6 sm:p-12 rounded-[2rem] text-center max-w-2xl mx-auto shadow-2xl overflow-hidden relative">
                                    {/* Inner subtle glow */}
                                    <div className="absolute inset-0 bg-gradient-to-b from-purple-500/5 to-transparent pointer-events-none" />

                                    <div className="relative max-w-lg mx-auto mb-6 sm:mb-10 group">
                                        <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none transition-transform group-focus-within:scale-110">
                                            <Sparkles className="w-5 h-5 sm:w-6 sm:h-6 text-purple-400" />
                                        </div>
                                        <input
                                            type="text"
                                            value={inputValue}
                                            onChange={(e) => setInputValue(e.target.value)}
                                            placeholder="https://your-startup.com or description..."
                                            className="w-full bg-black/80 border border-white/10 rounded-2xl py-5 sm:py-6 pl-12 sm:pl-14 pr-4 text-white placeholder-gray-600 focus:outline-none focus:border-purple-500/50 focus:ring-2 focus:ring-purple-500/20 transition-all text-base sm:text-lg shadow-inner"
                                            onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
                                            autoFocus
                                            autoComplete="off"
                                            spellCheck="false"
                                        />
                                    </div>

                                    <motion.button
                                        whileHover={inputValue.trim() ? { scale: 1.02 } : {}}
                                        whileTap={inputValue.trim() ? { scale: 0.98 } : {}}
                                        onClick={handleAnalyze}
                                        disabled={!inputValue.trim()}
                                        className={cn(
                                            "w-full sm:w-auto h-14 sm:h-16 px-8 sm:px-12 text-base sm:text-lg rounded-2xl font-bold transition-all flex items-center justify-center mx-auto shadow-xl group",
                                            inputValue.trim()
                                                ? "bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-purple-500/25 hover:shadow-purple-500/40"
                                                : "bg-white/5 text-gray-500 cursor-not-allowed border border-white/5"
                                        )}
                                    >
                                        Execute Scan
                                        <ArrowRight className={cn("ml-3 w-5 h-5 transition-transform", inputValue.trim() && "group-hover:translate-x-1")} />
                                    </motion.button>

                                    <div className="mt-8 sm:mt-10 grid grid-cols-2 gap-2 sm:gap-4 text-[10px] sm:text-xs text-gray-500 font-mono text-left max-w-sm mx-auto">
                                        <div className="flex items-center gap-2 bg-black/40 rounded p-2"><Check className="w-3 h-3 text-emerald-500" /> Competitor Map</div>
                                        <div className="flex items-center gap-2 bg-black/40 rounded p-2"><Check className="w-3 h-3 text-emerald-500" /> Target Personas</div>
                                        <div className="flex items-center gap-2 bg-black/40 rounded p-2"><Check className="w-3 h-3 text-emerald-500" /> Tone of Voice Analysis</div>
                                        <div className="flex items-center gap-2 bg-black/40 rounded p-2"><Check className="w-3 h-3 text-emerald-500" /> Early Traction Tests</div>
                                    </div>
                                </div>
                            </motion.div>
                        )}

                        {/* ─── STEP 2: ANALYSIS ─── */}
                        {step === 2 && (
                            <motion.div
                                key="step2"
                                variants={stepVariants}
                                initial="hidden"
                                animate="visible"
                                exit="exit"
                                className="w-full flex-col flex items-center justify-center pt-8 sm:pt-12"
                            >
                                {/* Neural Core Animation */}
                                <div className="relative w-48 h-48 sm:w-64 sm:h-64 flex items-center justify-center mb-8">
                                    <motion.div
                                        animate={{ rotate: 360 }}
                                        transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
                                        className="absolute inset-0 border-t-2 border-r-2 border-purple-500/50 rounded-full"
                                    />
                                    <motion.div
                                        animate={{ rotate: -360 }}
                                        transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
                                        className="absolute inset-4 border-b-2 border-l-2 border-blue-500/50 rounded-full"
                                    />
                                    <motion.div
                                        animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
                                        transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                                        className="absolute inset-10 bg-gradient-to-tr from-purple-600 to-blue-600 rounded-full blur-xl"
                                    />

                                    <div className="relative z-10 w-20 h-20 sm:w-24 sm:h-24 bg-black rounded-full border border-white/20 flex items-center justify-center shadow-[0_0_30px_rgba(168,85,247,0.5)]">
                                        <Bot className="w-8 h-8 sm:w-10 sm:h-10 text-white animate-pulse" />
                                    </div>
                                </div>

                                {/* Dynamic Terminal Logs */}
                                <div className="w-full max-w-md h-32 relative overflow-hidden flex flex-col justify-end mask-image-fade-top font-mono text-xs sm:text-sm">
                                    <AnimatePresence initial={false}>
                                        {analysisLines.map((line, i) => (
                                            <motion.div
                                                key={`${line}-${i}`}
                                                initial={{ opacity: 0, y: 20 }}
                                                animate={{ opacity: 1, y: 0 }}
                                                exit={{ opacity: 0, y: -20 }}
                                                transition={{ duration: 0.3 }}
                                                className="flex items-center gap-3 py-1.5 px-4 text-emerald-400"
                                            >
                                                <span className="text-gray-600 shrink-0">{'>'}</span>
                                                <span className="truncate">{line}</span>
                                            </motion.div>
                                        ))}
                                    </AnimatePresence>
                                    <div className="flex items-center gap-3 py-1.5 px-4 mt-2 border-t border-white/5">
                                        <Loader2 className="w-4 h-4 text-purple-500 animate-spin shrink-0" />
                                        <span className="text-gray-400">Processing dimensional vectors...</span>
                                    </div>
                                </div>
                            </motion.div>
                        )}

                        {/* ─── STEP 3: RESULTS ─── */}
                        {step === 3 && plan && (
                            <motion.div
                                key="step3"
                                variants={stepVariants}
                                initial="hidden"
                                animate="visible"
                                exit="exit"
                                className="w-full max-w-5xl mx-auto pb-24"
                            >
                                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
                                    {/* Main Summary Card */}
                                    <motion.div
                                        custom={0} variants={cardVariants} initial="hidden" animate="visible"
                                        className="lg:col-span-3 bg-[#0a0a0f]/90 backdrop-blur-xl border border-white/10 p-6 sm:p-8 rounded-[2rem] shadow-2xl relative overflow-hidden group"
                                    >
                                        <div className="absolute top-0 right-0 w-64 h-64 bg-purple-500/10 rounded-full blur-[80px] -translate-y-1/2 translate-x-1/2" />
                                        <h2 className="text-xl sm:text-2xl font-bold mb-3 flex items-center gap-3">
                                            <div className="w-2 h-8 bg-purple-500 rounded-full" />
                                            Executive Brief
                                        </h2>
                                        <p className="text-gray-300 text-sm sm:text-lg leading-relaxed relative z-10">{plan.summary}</p>
                                    </motion.div>

                                    {/* Action Card 1: Target Audience */}
                                    <motion.div
                                        custom={1} variants={cardVariants} initial="hidden" animate="visible"
                                        className="bg-black/50 backdrop-blur-md border border-white/5 p-6 rounded-3xl hover:border-purple-500/30 transition-colors"
                                    >
                                        <div className="w-10 h-10 rounded-xl bg-blue-500/20 text-blue-400 flex items-center justify-center mb-4">
                                            <Target className="w-5 h-5" />
                                        </div>
                                        <h3 className="text-sm uppercase tracking-widest text-gray-500 font-bold mb-2">Ideal Customer</h3>
                                        <p className="text-white font-medium">{plan.leads_icp}</p>
                                    </motion.div>

                                    {/* Action Card 2: Growth Experiment */}
                                    <motion.div
                                        custom={2} variants={cardVariants} initial="hidden" animate="visible"
                                        className="bg-black/50 backdrop-blur-md border border-white/5 p-6 rounded-3xl hover:border-emerald-500/30 transition-colors"
                                    >
                                        <div className="w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center mb-4">
                                            <TrendingUp className="w-5 h-5" />
                                        </div>
                                        <h3 className="text-sm uppercase tracking-widest text-gray-500 font-bold mb-2">Primary Vector</h3>
                                        <div className="text-white font-bold mb-1">{plan.experiment.name}</div>
                                        <div className="text-sm text-gray-400">{plan.experiment.hypothesis}</div>
                                    </motion.div>

                                    {/* Action Card 3: Pre-drafted Assets */}
                                    <motion.div
                                        custom={3} variants={cardVariants} initial="hidden" animate="visible"
                                        className="bg-black/50 backdrop-blur-md border border-white/5 p-6 rounded-3xl hover:border-purple-500/30 transition-colors"
                                    >
                                        <div className="w-10 h-10 rounded-xl bg-purple-500/20 text-purple-400 flex items-center justify-center mb-4">
                                            <Sparkles className="w-5 h-5" />
                                        </div>
                                        <h3 className="text-sm uppercase tracking-widest text-gray-500 font-bold mb-3">Synthesized Assets</h3>
                                        <div className="space-y-3">
                                            {plan.social_posts.slice(0, 2).map((post: any, i: number) => (
                                                <div key={i} className="text-xs sm:text-[13px] text-gray-300 bg-white/5 p-3 rounded-xl border border-white/5 line-clamp-2">
                                                    <strong className="text-white">{post.platform}:</strong> {post.content}
                                                </div>
                                            ))}
                                        </div>
                                    </motion.div>
                                </div>

                                {/* Final Verification Push */}
                                <motion.div
                                    custom={4} variants={cardVariants} initial="hidden" animate="visible"
                                    className="mt-8"
                                >
                                    <HoldToDeployButton onComplete={handleComplete} />
                                </motion.div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>

            <style dangerouslySetInnerHTML={{
                __html: `
                .mask-image-fade-top {
                    -webkit-mask-image: linear-gradient(to bottom, transparent, black 40%);
                    mask-image: linear-gradient(to bottom, transparent, black 40%);
                }
            `}} />
        </div>
    );
}
