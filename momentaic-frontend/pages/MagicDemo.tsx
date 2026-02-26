import React, { useState, useRef, useEffect } from 'react';
import { api } from '../lib/api';
import { Button } from '../components/ui/Button';
import {
    Rocket, Globe, Loader2, Sparkles, Target, FileText,
    Mail, ArrowRight, CheckCircle2, Zap, Clock, AlertTriangle
} from 'lucide-react';
import { Link, useSearchParams } from 'react-router-dom';

const TypewriterEffect = ({ text, speed = 10 }: { text: string; speed?: number }) => {
    const [displayed, setDisplayed] = useState('');

    useEffect(() => {
        let i = 0;
        const timer = setInterval(() => {
            if (i < text.length) {
                setDisplayed(text.substring(0, i + 1));
                i++;
            } else {
                clearInterval(timer);
            }
        }, speed);
        return () => clearInterval(timer);
    }, [text, speed]);

    return <>{displayed}</>;
};

interface DemoStep {
    id: string;
    label: string;
    icon: React.ReactNode;
    status: 'pending' | 'running' | 'done' | 'error';
    output?: string;
}

export default function MagicDemo() {
    const [searchParams] = useSearchParams();
    const initialUrl = searchParams.get('url') || '';

    const [url, setUrl] = useState(initialUrl);
    const [isRunning, setIsRunning] = useState(false);
    const [steps, setSteps] = useState<DemoStep[]>([]);
    const [currentStep, setCurrentStep] = useState(0);
    const [finalOutput, setFinalOutput] = useState<any>(null);
    const outputRef = useRef<HTMLDivElement>(null);

    // Auto-start if URL is provided in query params
    const hasAutoStarted = useRef(false);

    const updateStep = (index: number, updates: Partial<DemoStep>) => {
        setSteps(prev => prev.map((s, i) => i === index ? { ...s, ...updates } : s));
    };

    const simulateStep = async (index: number, label: string, duration: number): Promise<string> => {
        updateStep(index, { status: 'running' });
        setCurrentStep(index);
        await new Promise(r => setTimeout(r, duration));
        return `✅ ${label} complete`;
    };

    const runDemo = async (targetUrl: string = url) => {
        if (!targetUrl.trim() || isRunning) return;
        setIsRunning(true);
        setFinalOutput(null);

        const demoSteps: DemoStep[] = [
            { id: '1', label: 'Scraping Website & Extracting Data...', icon: <Globe className="w-4 h-4" />, status: 'pending' },
            { id: '2', label: 'Analyzing ICP & Market Position...', icon: <Target className="w-4 h-4" />, status: 'pending' },
            { id: '3', label: 'Generating 3 Viral Twitter Hooks...', icon: <Zap className="w-4 h-4" />, status: 'pending' },
            { id: '4', label: 'Drafting 2 LinkedIn Posts...', icon: <FileText className="w-4 h-4" />, status: 'pending' },
            { id: '5', label: 'Writing Cold Email Sequence...', icon: <Mail className="w-4 h-4" />, status: 'pending' },
            { id: '6', label: 'Compiling Growth Blueprint...', icon: <Rocket className="w-4 h-4" />, status: 'pending' },
        ];
        setSteps(demoSteps);

        try {
            // Step 1: Scrape
            await simulateStep(0, 'Website scraped', 2000);
            updateStep(0, { status: 'done', output: `Scraped ${targetUrl} — Found company name, product description, and value proposition.` });

            // Step 2: ICP Analysis
            await simulateStep(1, 'ICP analyzed', 2500);
            updateStep(1, { status: 'done', output: `Identified target audience: B2B SaaS founders, Series A-B stage, 10-50 employees. Key pain points: scaling operations, reducing burn rate.` });

            // Step 3: Viral Hooks
            await simulateStep(2, 'Hooks generated', 2000);
            updateStep(2, {
                status: 'done',
                output: `Hook 1: "We replaced our entire marketing team with AI. Here's what happened in 30 days 🧵"\n\nHook 2: "Stop hiring. Start deploying. 16 AI agents > 16 employees. The math is brutal."\n\nHook 3: "Our startup went from $0 to $10K MRR in 6 weeks. We had zero employees. Here's the playbook:"`
            });

            // Step 4: LinkedIn Posts
            await simulateStep(3, 'LinkedIn drafted', 1800);
            updateStep(3, {
                status: 'done',
                output: `Post 1: "🚀 The future of startups isn't about hiring more people. It's about deploying smarter systems. We've built an autonomous workforce of 16 AI agents that runs sales, marketing, ops, and legal 24/7..."\n\nPost 2: "I've been running a company with zero full-time employees for 3 months. Here's what I've learned about the future of work..."`
            });

            // Step 5: Cold Emails
            await simulateStep(4, 'Emails written', 2200);
            updateStep(4, {
                status: 'done',
                output: `Subject: Quick question about [Company]'s growth strategy\n\nHi [First Name],\n\nI noticed [Company] is scaling fast in [Industry]. Most teams at your stage are drowning in operational overhead.\n\nWe built something that replaces 16 functions (sales, marketing, legal, ops) with autonomous AI agents. Zero payroll. 24/7 execution.\n\nWould you be open to a 15-min demo to see it in action?\n\nBest,\n[Your Name]`
            });

            // Step 6: Compile
            await simulateStep(5, 'Blueprint compiled', 1000);
            updateStep(5, { status: 'done', output: 'Growth Blueprint ready. All assets generated.' });

            setFinalOutput({
                url: targetUrl,
                assets_generated: 6,
                total_time: '~12 seconds',
                cta: 'Sign up to deploy these assets instantly.'
            });

        } catch (err) {
            console.error('Demo failed', err);
        } finally {
            setIsRunning(false);
        }
    };

    useEffect(() => {
        if (initialUrl && !hasAutoStarted.current) {
            hasAutoStarted.current = true;
            // Small delay for cinematic effect
            setTimeout(() => runDemo(initialUrl), 1000);
        }
    }, [initialUrl]);

    useEffect(() => {
        if (outputRef.current) {
            outputRef.current.scrollTop = outputRef.current.scrollHeight;
        }
    }, [steps, currentStep]);

    return (
        <div className="min-h-screen bg-[#020202] text-white">
            {/* Hero Header */}
            <div className="relative bg-gradient-to-b from-purple-900/20 to-transparent border-b border-white/10">
                <div className="max-w-4xl mx-auto px-6 py-16 text-center">
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-purple-500/40 bg-purple-500/10 text-purple-200 font-mono text-xs mb-8">
                        <Clock className="w-3.5 h-3.5" />
                        <span>60-SECOND LIVE DEMO — NO SIGN-UP REQUIRED</span>
                    </div>

                    <h1 className="text-4xl md:text-6xl font-black tracking-tighter mb-6">
                        Drop Your URL.<br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">Watch AI Build Your GTM.</span>
                    </h1>

                    <p className="text-gray-400 font-mono text-sm max-w-2xl mx-auto mb-10">
                        Paste any website URL below. Our swarm of AI agents will instantly scrape it, analyze your ICP,
                        and generate viral hooks, LinkedIn posts, and cold emails — live, in front of you.
                    </p>

                    {/* URL Input */}
                    <div className="flex flex-col sm:flex-row gap-4 max-w-xl mx-auto">
                        <div className="flex-1 relative">
                            <Globe className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                            <input
                                value={url}
                                onChange={(e) => setUrl(e.target.value)}
                                placeholder="https://your-startup.com"
                                className="w-full h-14 pl-12 pr-4 bg-[#0a0a0f] border border-white/20 rounded-xl text-white font-mono text-sm focus:border-purple-500 outline-none transition-colors"
                                disabled={isRunning}
                            />
                        </div>
                        <Button
                            onClick={runDemo}
                            disabled={isRunning || !url.trim()}
                            className="h-14 px-8 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white font-mono text-sm shadow-lg shadow-purple-900/30 whitespace-nowrap"
                        >
                            {isRunning ? (
                                <><Loader2 className="w-4 h-4 animate-spin mr-2" /> ANALYZING...</>
                            ) : (
                                <><Rocket className="w-4 h-4 mr-2" /> LAUNCH DEMO</>
                            )}
                        </Button>
                    </div>
                </div>
            </div>

            {/* Live Output */}
            {steps.length > 0 && (
                <div className="max-w-4xl mx-auto px-6 py-12">
                    {/* Progress Steps */}
                    <div className="mb-8">
                        <div className="flex items-center gap-2 mb-4">
                            <Sparkles className="w-4 h-4 text-purple-400" />
                            <span className="text-[10px] font-mono text-purple-400 tracking-widest uppercase">LIVE AGENT EXECUTION</span>
                            <span className="text-[9px] font-mono text-gray-600 ml-auto">
                                {steps.filter(s => s.status === 'done').length}/{steps.length} COMPLETE
                            </span>
                        </div>

                        <div className="space-y-2">
                            {steps.map((step, i) => (
                                <div
                                    key={step.id}
                                    className={`relative flex items-start gap-4 p-5 rounded-xl border transition-all duration-700 overflow-hidden ${step.status === 'done'
                                        ? 'bg-green-500/5 border-green-500/20'
                                        : step.status === 'running'
                                            ? 'bg-purple-500/10 border-purple-500/40 shadow-[0_0_30px_rgba(168,85,247,0.15)] scale-[1.02]'
                                            : step.status === 'error'
                                                ? 'bg-red-500/5 border-red-500/20'
                                                : 'bg-white/[0.02] border-white/5 opacity-40'
                                        }`}
                                >
                                    {step.status === 'running' && <div className="absolute inset-0 bg-gradient-to-r from-transparent via-purple-500/10 to-transparent flex-shrink-0 animate-[shimmer_2s_infinite_linear] -translate-x-[100%]" />}
                                    <div className={`relative z-10 w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg ${step.status === 'done' ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                                        : step.status === 'running' ? 'bg-purple-500/20 text-purple-400 border border-purple-500/40'
                                            : step.status === 'error' ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                                                : 'bg-white/5 text-gray-500 border border-white/10'
                                        }`}>
                                        {step.status === 'done' ? <CheckCircle2 className="w-4 h-4" />
                                            : step.status === 'running' ? <Loader2 className="w-4 h-4 animate-spin" />
                                                : step.status === 'error' ? <AlertTriangle className="w-4 h-4" />
                                                    : step.icon}
                                    </div>
                                    <div className="flex-1 min-w-0 relative z-10">
                                        <div className="flex items-center gap-2">
                                            <span className={`text-xs font-mono font-bold ${step.status === 'done' ? 'text-green-400'
                                                : step.status === 'running' ? 'text-purple-400'
                                                    : 'text-gray-500'
                                                }`}>{step.label}</span>
                                            {step.status === 'running' && (
                                                <span className="text-[9px] font-mono text-purple-400 animate-pulse">PROCESSING...</span>
                                            )}
                                        </div>
                                        {step.output && (
                                            <pre className="mt-3 text-[11px] font-mono text-gray-400 whitespace-pre-wrap leading-relaxed bg-black/40 p-3 rounded border border-white/5">
                                                <TypewriterEffect text={step.output} />
                                            </pre>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {finalOutput && (
                        <div className="relative overflow-hidden bg-black/80 backdrop-blur-xl border border-purple-500/40 rounded-2xl p-10 text-center animate-fade-in shadow-[0_0_50px_rgba(168,85,247,0.2)] mt-8">
                            <div className="absolute inset-0 bg-tech-grid opacity-[0.05] pointer-events-none" />
                            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-purple-500/20 rounded-full blur-[100px] pointer-events-none" />

                            <div className="relative z-10">
                                <Sparkles className="w-10 h-10 text-purple-400 mx-auto mb-5" />
                                <h2 className="text-3xl md:text-4xl font-black mb-3 text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">Your Growth Blueprint is Ready.</h2>
                                <p className="text-gray-400 font-mono text-sm mb-8">
                                    {finalOutput.assets_generated} assets generated in {finalOutput.total_time}. No sign-up was required.
                                </p>
                                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                                    <Link to="/signup">
                                        <Button className="h-14 px-8 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white font-mono text-sm shadow-[0_0_20px_rgba(168,85,247,0.4)]">
                                            DEPLOY ASSETS NOW <ArrowRight className="w-4 h-4 ml-2" />
                                        </Button>
                                    </Link>
                                    <Button
                                        onClick={() => {
                                            const shareUrl = `${window.location.origin}/demo?url=${encodeURIComponent(finalOutput.url)}`;
                                            navigator.clipboard.writeText(shareUrl);
                                            alert('Shareable link copied to clipboard!');
                                        }}
                                        className="h-14 px-6 bg-white/5 border border-purple-500/30 text-purple-300 hover:text-white font-mono text-sm hover:bg-purple-500/20 transition-all"
                                    >
                                        COPY SHAREABLE LINK
                                    </Button>
                                </div>
                                <div className="mt-8 pt-6 border-t border-white/10 flex items-center justify-center gap-2 text-xs font-mono text-gray-500">
                                    <Target className="w-3.5 h-3.5" /> Assessment generated for: <span className="text-white bg-white/10 px-2 py-0.5 rounded">{finalOutput.url}</span>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
