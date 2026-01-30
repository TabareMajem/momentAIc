import React, { useState, useEffect, useRef } from 'react';
import { api } from '../lib/api';
import { useAuthStore } from '../stores/auth-store';
import { useNavigate } from 'react-router-dom';
import {
    Send, Sparkles, Zap, Bot, ArrowRight, CheckCircle2,
    AlertCircle, Terminal, Cpu, Loader2, Play, Lock, Rocket, Target, TrendingUp
} from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Dialog } from '../components/ui/Dialog';
import { Card } from '../components/ui/Card';
import { TypingText, ConfettiBurst } from '../components/ui/AnimatedEffects';

interface Message {
    role: 'user' | 'assistant';
    content: string;
    isTyping?: boolean;
}

interface ExecutionPlan {
    summary: string;
    social_posts: Array<{ platform: string; content: string }>;
    leads_icp: string;
    experiment: { name: string; hypothesis: string };
}

export default function GeniusOnboarding() {
    const { user } = useAuthStore();
    const navigate = useNavigate();
    const [messages, setMessages] = useState<Message[]>([
        {
            role: 'assistant',
            content: "I am your AI Co-Founder. Drop your product URL, and I'll build your Day-1 Growth Strategy."
        }
    ]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [plan, setPlan] = useState<ExecutionPlan | null>(null);
    const [isExecuting, setIsExecuting] = useState(false);
    const [startupId, setStartupId] = useState<string | null>(null);
    const [showPaywall, setShowPaywall] = useState(false);
    const [showConfetti, setShowConfetti] = useState(false);
    const [currentStep, setCurrentStep] = useState(1); // 1: URL, 2: Analysis, 3: Strategy

    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    // Load user's first startup ID to attach context
    useEffect(() => {
        const loadStartup = async () => {
            const startups = await api.getStartups();
            if (startups.length > 0) setStartupId(startups[0].id);
        };
        loadStartup();
    }, []);

    const handleSend = async () => {
        if (!inputValue.trim()) return;

        const userMsg = inputValue;
        setInputValue('');
        setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
        setIsLoading(true);

        try {
            // First message? Start session.
            if (messages.length === 1) {
                setCurrentStep(2); // Move to Analysis step
                const response = await api.startGeniusSession(userMsg, startupId || undefined);
                setMessages(prev => [...prev, { role: 'assistant', content: response.message }]);
            } else {
                // Continue chat
                const response = await api.continueGeniusChat(userMsg);
                setMessages(prev => [...prev, { role: 'assistant', content: response.message }]);

                // If plan returned, parse and show it
                if (response.is_plan) {
                    try {
                        const jsonMatch = response.message.match(/\{[\s\S]*\}/);
                        if (jsonMatch) {
                            const parsedPlan = JSON.parse(jsonMatch[0]);
                            if (parsedPlan.social_posts) {
                                setPlan(parsedPlan);
                                setShowConfetti(true);
                                setCurrentStep(3);
                                setTimeout(() => setShowConfetti(false), 3000);
                            }
                        }
                    } catch (e) {
                        console.error("Failed to parse plan JSON", e);
                    }
                }
            }
        } catch (error) {
            console.error(error);
            setMessages(prev => [...prev, { role: 'assistant', content: "I encountered a glitch in the matrix. Please try again." }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleExecute = async () => {
        if (!plan || !startupId) {
            if (!startupId) alert("No startup found. Please create one in the dashboard first.");
            return;
        }

        // PAYWALL CHECK
        // If user is not "pro" or "growth", show paywall
        const tier = user?.subscription_tier || 'starter';
        if (tier === 'starter') {
            setShowPaywall(true);
            return;
        }

        setIsExecuting(true);
        try {
            await api.executeGeniusPlan(startupId, plan);

            setMessages(prev => [...prev, {
                role: 'assistant',
                content: "🚀 Plan Executed! I've scheduled your posts and queued the lead generation task. Check your Dashboard."
            }]);

            setTimeout(() => navigate('/dashboard'), 3000);
        } catch (error) {
            console.error(error);
            alert("Execution failed. Check console.");
        } finally {
            setIsExecuting(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#050505] text-white flex flex-col font-sans selection:bg-[#00f0ff] selection:text-black">
            {/* Confetti Burst */}
            <ConfettiBurst trigger={showConfetti} />

            {/* Progress Stepper */}
            <div className="fixed top-20 left-1/2 -translate-x-1/2 z-30 hidden md:flex items-center gap-4 bg-black/80 backdrop-blur-md border border-white/10 rounded-full px-6 py-3">
                {[
                    { step: 1, label: "Drop URL", icon: <Target className="w-4 h-4" /> },
                    { step: 2, label: "AI Analysis", icon: <Cpu className="w-4 h-4" /> },
                    { step: 3, label: "Get Strategy", icon: <Rocket className="w-4 h-4" /> },
                ].map((item, idx) => (
                    <React.Fragment key={item.step}>
                        <div className={`flex items-center gap-2 transition-all duration-300 ${currentStep >= item.step ? 'text-[#00f0ff]' : 'text-gray-600'
                            }`}>
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 transition-all duration-300 ${currentStep > item.step
                                ? 'bg-[#00f0ff] border-[#00f0ff] text-black'
                                : currentStep === item.step
                                    ? 'border-[#00f0ff] text-[#00f0ff]'
                                    : 'border-gray-600'
                                }`}>
                                {currentStep > item.step ? <CheckCircle2 className="w-4 h-4" /> : item.icon}
                            </div>
                            <span className="text-xs font-mono uppercase tracking-wider">{item.label}</span>
                        </div>
                        {idx < 2 && <div className={`w-12 h-0.5 transition-all duration-300 ${currentStep > item.step ? 'bg-[#00f0ff]' : 'bg-gray-700'
                            }`} />}
                    </React.Fragment>
                ))}
            </div>

            {/* Header */}
            <header className="p-6 border-b border-white/10 bg-black/50 backdrop-blur-md sticky top-0 z-20">
                <div className="max-w-4xl mx-auto flex justify-between items-center">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-[#00f0ff] to-[#a855f7] flex items-center justify-center shadow-[0_0_20px_rgba(168,85,247,0.4)]">
                            <Bot className="w-6 h-6 text-black" />
                        </div>
                        <div>
                            <h1 className="text-xl font-black italic tracking-tighter uppercase">Genius Mode</h1>
                            <div className="flex items-center gap-2 text-[10px] text-gray-400 font-mono">
                                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                                LIVE // STRATEGY IN 60 SECONDS
                            </div>
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        {(!user?.subscription_tier || user?.subscription_tier === 'starter') && (
                            <Button variant="outline" size="sm" className="hidden md:flex text-[10px] h-8 border-purple-500/50 text-purple-400" onClick={() => setShowPaywall(true)}>
                                UPGRADE TO LAUNCH
                            </Button>
                        )}
                        <Button variant="ghost" className="text-xs font-mono text-gray-500 hover:text-white" onClick={() => navigate('/dashboard')}>
                            EXIT SESSION
                        </Button>
                    </div>
                </div>
            </header>

            {/* Chat Area */}
            <main className="flex-1 overflow-y-auto p-4 md:p-8 relative">
                <div className="absolute inset-0 bg-cyber-grid opacity-[0.03] pointer-events-none"></div>

                <div className="max-w-3xl mx-auto space-y-6 pb-32">
                    {messages.map((msg, idx) => (
                        <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in-up`}>
                            {msg.role === 'assistant' && (
                                <div className="w-8 h-8 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center shrink-0 mt-1">
                                    <Sparkles className="w-4 h-4 text-[#00f0ff]" />
                                </div>
                            )}

                            <div className={`
                                max-w-[80%] rounded-2xl p-4 md:p-6 text-sm md:text-base leading-relaxed whitespace-pre-wrap
                                ${msg.role === 'user'
                                    ? 'bg-[#00f0ff] text-black font-medium rounded-tr-none'
                                    : 'bg-[#111] border border-white/10 text-gray-200 rounded-tl-none font-mono'}
                            `}>
                                {msg.content}
                            </div>
                        </div>
                    ))}

                    {isLoading && (
                        <div className="flex gap-4 animate-fade-in">
                            <div className="w-8 h-8 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center">
                                <Loader2 className="w-4 h-4 text-[#00f0ff] animate-spin" />
                            </div>
                            <div className="bg-[#111] border border-white/10 rounded-2xl rounded-tl-none p-4 flex items-center gap-1">
                                <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></span>
                                <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce [animation-delay:0.2s]"></span>
                                <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce [animation-delay:0.4s]"></span>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>
            </main>

            {/* Plan Approval Modal (Inline) */}
            {plan && !isExecuting && (
                <div className="fixed inset-x-0 bottom-24 z-30 px-4 animate-in slide-in-from-bottom-10 fade-in duration-500">
                    <div className="max-w-3xl mx-auto bg-[#0a0a0a] border border-[#00f0ff]/30 rounded-2xl shadow-[0_0_50px_rgba(0,240,255,0.1)] overflow-hidden">
                        <div className="bg-gradient-to-r from-[#00f0ff]/10 to-[#a855f7]/10 p-4 border-b border-white/10 flex justify-between items-center">
                            <div className="flex items-center gap-2 text-[#00f0ff] font-bold uppercase tracking-wider text-sm">
                                <Zap className="w-4 h-4" /> Strategic Plan Ready
                            </div>
                        </div>
                        <div className="p-6 grid gap-6 md:grid-cols-2">
                            <div className="space-y-4">
                                <h3 className="text-xs font-mono text-gray-500 uppercase tracking-widest">Planned Posts</h3>
                                {plan.social_posts.map((post, i) => (
                                    <div key={i} className="p-3 bg-white/5 rounded-lg border border-white/10 text-xs text-gray-300 font-mono">
                                        <span className="text-[#1DA1F2] font-bold mr-2">[{post.platform.toUpperCase()}]</span>
                                        {post.content.slice(0, 80)}...
                                    </div>
                                ))}
                            </div>
                            <div className="space-y-4">
                                <h3 className="text-xs font-mono text-gray-500 uppercase tracking-widest">Growth Experiment</h3>
                                <div className="p-3 bg-purple-500/10 rounded-lg border border-purple-500/20 text-xs text-gray-300">
                                    <strong className="text-purple-400 block mb-1">{plan.experiment.name}</strong>
                                    {plan.experiment.hypothesis}
                                </div>
                                <Button onClick={handleExecute} className="w-full bg-[#00f0ff] hover:bg-[#00d0df] text-black font-black italic uppercase tracking-wider h-12 shadow-[0_0_20px_rgba(0,240,255,0.4)] hover:shadow-[0_0_30px_rgba(0,240,255,0.6)] transition-all relative group overflow-hidden">
                                    <span className="relative z-10 flex items-center justify-center gap-2">
                                        EXECUTE PLAN <Play className="w-4 h-4 fill-current" />
                                    </span>
                                    {(user?.subscription_tier === 'starter' || !user?.subscription_tier) && (
                                        <span className="absolute right-0 top-0 bg-black text-white text-[9px] px-2 py-1 font-mono uppercase">Includes Lock</span>
                                    )}
                                </Button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Input Area */}
            <div className="p-4 md:p-6 bg-black border-t border-white/10 sticky bottom-0 z-20">
                <div className="max-w-3xl mx-auto relative">
                    <input
                        type="text"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                        placeholder={messages.length === 1 ? "Paste your landing page URL..." : "Reply to your AI strategist..."}
                        className="w-full bg-[#111] border border-white/20 rounded-xl px-6 py-4 pr-16 text-white placeholder-gray-600 focus:outline-none focus:border-[#00f0ff] focus:ring-1 focus:ring-[#00f0ff] transition-all font-mono"
                        autoFocus
                    />
                    <button
                        onClick={handleSend}
                        disabled={!inputValue.trim() || isLoading}
                        className="absolute right-2 top-2 p-2 bg-gradient-to-tr from-[#00f0ff] to-[#a855f7] rounded-lg text-black hover:opacity-90 disabled:opacity-50 transition-all"
                    >
                        <ArrowRight className="w-5 h-5" />
                    </button>
                </div>
                <div className="max-w-3xl mx-auto mt-2 text-center">
                    <p className="text-[10px] text-gray-600 font-mono uppercase tracking-widest">
                        Powered by Gemini 1.5 Pro • 1M Context Window
                    </p>
                </div>
            </div>

            {/* PAYWALL MODAL */}
            <Dialog
                isOpen={showPaywall}
                onClose={() => setShowPaywall(false)}
                title="Unlock Autonomous Execution"
                description="Your AI strategy is ready. Upgrade to Pro to let the agents execute it for you instantly."
                footer={
                    <>
                        <Button variant="ghost" onClick={() => setShowPaywall(false)}>CANCEL</Button>
                        <Button variant="cyber" onClick={() => navigate('/investment')}>
                            UPGRADE NOW <Zap className="w-4 h-4 ml-2" />
                        </Button>
                    </>
                }
            >
                <div className="space-y-6">
                    <div className="flex justify-center py-6">
                        <div className="w-20 h-20 rounded-full bg-purple-500/10 flex items-center justify-center border border-purple-500/30 animate-pulse">
                            <Lock className="w-10 h-10 text-purple-400" />
                        </div>
                    </div>
                    <div className="space-y-4">
                        <div className="flex items-center gap-3 p-3 bg-white/5 rounded-lg border border-white/5">
                            <CheckCircle2 className="w-5 h-5 text-green-400" />
                            <div>
                                <h4 className="font-bold text-sm">One-Click Execution</h4>
                                <p className="text-xs text-gray-400">Post to Twitter & LinkedIn instantly</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-3 p-3 bg-white/5 rounded-lg border border-white/5">
                            <CheckCircle2 className="w-5 h-5 text-green-400" />
                            <div>
                                <h4 className="font-bold text-sm">Unlimited Strategies</h4>
                                <p className="text-xs text-gray-400">Generate fresh plans daily</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-3 p-3 bg-white/5 rounded-lg border border-white/5">
                            <CheckCircle2 className="w-5 h-5 text-green-400" />
                            <div>
                                <h4 className="font-bold text-sm">Full Growth Suite</h4>
                                <p className="text-xs text-gray-400">Access Experiment Lab & Lead Engine</p>
                            </div>
                        </div>
                    </div>
                </div>
            </Dialog>
        </div>
    );
}
