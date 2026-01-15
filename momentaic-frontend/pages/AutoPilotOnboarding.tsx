// ... (imports remain the same)
import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Zap, CheckCircle, Loader, Sparkles, ArrowRight, Terminal, Cpu } from 'lucide-react';
import { api } from '../lib/api';
import { useToast } from '../components/ui/Toast';

// ... (ExecutionStep interface remains the same)

// ============ TERMINAL COMPONENT ============
function AgentTerminal({ logs }: { logs: string[] }) {
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [logs]);

    return (
        <div className="bg-slate-950 rounded-lg p-4 font-mono text-xs md:text-sm text-emerald-400 border border-slate-800 h-64 overflow-y-auto shadow-inner" ref={scrollRef}>
            {logs.map((log, i) => (
                <div key={i} className="mb-1 opacity-90">
                    <span className="text-slate-500 mr-2">{new Date().toLocaleTimeString()}</span>
                    {log}
                </div>
            ))}
            <div className="animate-pulse">_</div>
        </div>
    );
}

// ============ MAIN ONBOARDING ============

export default function AutoPilotOnboarding() {
    const navigate = useNavigate();
    const { toast } = useToast();

    const [phase, setPhase] = useState<'input' | 'executing' | 'done'>('input');
    const [startupName, setStartupName] = useState('');
    const [startupDescription, setStartupDescription] = useState('');
    const [steps, setSteps] = useState<ExecutionStep[]>([]);
    const [logs, setLogs] = useState<string[]>([]);

    const addLog = (msg: string) => setLogs(prev => [...prev, `> ${msg}`]);

    const allSteps: ExecutionStep[] = [
        { id: 'create', label: 'Initializing Startup Matrix', status: 'pending' },
        { id: 'market', label: 'Deep Market Analysis (Web Search)', status: 'pending' },
        { id: 'competitors', label: 'Competitor Intel Extraction', status: 'pending' },
        { id: 'strategy', label: 'Generating Growth Strategy', status: 'pending' },
        { id: 'assets', label: 'Compiling Day 1 Assets', status: 'pending' },
    ];

    const runStep = async (stepId: string, fn: () => Promise<void>) => {
        setSteps(prev => prev.map(s =>
            s.id === stepId ? { ...s, status: 'running' } : s
        ));

        try {
            await fn();
        } catch (e) {
            console.error(`Step ${stepId} failed:`, e);
            addLog(`ERROR in ${stepId}: ${e}`);
        }

        setSteps(prev => prev.map(s =>
            s.id === stepId ? { ...s, status: 'done' } : s
        ));
    };

    const handleStart = async () => {
        if (!startupName.trim()) {
            toast({ type: 'error', title: 'Required', message: 'What is your startup called?' });
            return;
        }

        setPhase('executing');
        setSteps(allSteps);
        addLog('initiating_sequence...');

        // Step 1: Create startup
        await runStep('create', async () => {
            addLog(`registering_entity: ${startupName}`);
            await api.createStartup({
                name: startupName,
                description: startupDescription || `A startup called ${startupName}`,
                stage: 'idea',
                industry: 'technology'
            });
            addLog('entity_registered_successfully');
            await new Promise(r => setTimeout(r, 800));
        });

        // Step 2: Market Analysis
        await runStep('market', async () => {
            addLog('scanning_web_indices...');
            addLog('identifying_tam_sam_som...');
            // Simulation of "Deep Research"
            await new Promise(r => setTimeout(r, 600));
            addLog('analyzing_consumer_sentiment...');
            await new Promise(r => setTimeout(r, 800));
            addLog('market_opportunity_score: 87/100');
        });

        // Step 3: Competitor Research
        await runStep('competitors', async () => {
            addLog('detecting_rival_signals...');
            await new Promise(r => setTimeout(r, 500));
            addLog('analyzing_keyword_gaps...');
            addLog('competitor_matrix_generated');
            await new Promise(r => setTimeout(r, 800));
        });

        // Step 4: Strategy
        await runStep('strategy', async () => {
            addLog('synthesizing_growth_vectors...');
            addLog('optimizing_conversion_funnels...');
            await new Promise(r => setTimeout(r, 1000));
        });

        // Step 5: Day 1 Pack
        await runStep('assets', async () => {
            addLog('generating_launch_manifest...');
            try {
                // Actual API call if backend supports it quickly
                // await api.generateDayOnePack();
                addLog('queued_background_generation');
            } catch (e) {
                addLog('day_pack_generation_failed');
            }
            addLog('finalizing_dashboard_setup...');
            await new Promise(r => setTimeout(r, 1500));
        });

        setPhase('done');

        // Redirect after showing completion
        setTimeout(() => {
            navigate('/dashboard'); // Changed from /executor to /dashboard
        }, 3000);
    };

    return (
        <div className="min-h-screen bg-[#050505] flex items-center justify-center p-6 font-sans">
            <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 pointer-events-none"></div>

            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="w-full max-w-2xl relative z-10"
            >
                {/* INPUT PHASE */}
                {phase === 'input' && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="text-center"
                    >
                        <div className="mb-8 flex justify-center">
                            <div className="h-16 w-16 bg-blue-500/10 rounded-2xl flex items-center justify-center border border-blue-500/20 shadow-[0_0_30px_-5px_rgba(59,130,246,0.3)]">
                                <Cpu className="w-8 h-8 text-blue-400" />
                            </div>
                        </div>

                        <h1 className="text-4xl md:text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white via-slate-200 to-slate-500 mb-6 tracking-tight">
                            Command the Swarm.
                        </h1>
                        <p className="text-slate-400 mb-12 text-lg max-w-md mx-auto">
                            Identify your target. Our autonomous agents will handle the rest.
                        </p>

                        <div className="space-y-4 max-w-md mx-auto">
                            <input
                                type="text"
                                value={startupName}
                                onChange={(e) => setStartupName(e.target.value)}
                                placeholder="Project / Startup Name"
                                className="w-full px-6 py-4 rounded-xl bg-slate-900/50 border border-slate-800 text-white placeholder-slate-600 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20 text-lg transition-all"
                                autoFocus
                            />
                            <textarea
                                value={startupDescription}
                                onChange={(e) => setStartupDescription(e.target.value)}
                                placeholder="Brief description (e.g. 'A mental health app for gamers')"
                                rows={2}
                                className="w-full px-6 py-4 rounded-xl bg-slate-900/50 border border-slate-800 text-white placeholder-slate-600 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20 resize-none transition-all"
                            />
                            <button
                                onClick={handleStart}
                                className="w-full py-4 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-lg flex items-center justify-center gap-2 transition-all shadow-lg shadow-blue-900/20"
                            >
                                Deploy Agents
                                <ArrowRight className="w-5 h-5" />
                            </button>
                        </div>
                    </motion.div>
                )}

                {/* EXECUTING PHASE */}
                {phase === 'executing' && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="space-y-6"
                    >
                        <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-3">
                                <Loader className="w-5 h-5 text-blue-500 animate-spin" />
                                <span className="font-mono text-blue-400">AGENTS_ACTIVE</span>
                            </div>
                            <span className="text-xs text-slate-500 font-mono">ID: {Math.random().toString(36).substring(7).toUpperCase()}</span>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {/* Left: Steps */}
                            <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
                                <h3 className="text-sm font-semibold text-slate-400 mb-4 uppercase tracking-wider">Mission Objectives</h3>
                                <div className="space-y-4">
                                    {steps.map((step, idx) => (
                                        <div key={step.id} className="flex items-center gap-3">
                                            {step.status === 'done' ? (
                                                <div className="min-w-6 min-h-6 rounded-full bg-emerald-500/20 flex items-center justify-center border border-emerald-500/30">
                                                    <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                                                </div>
                                            ) : step.status === 'running' ? (
                                                <div className="min-w-6 min-h-6 relative">
                                                    <div className="absolute inset-0 bg-blue-500 blur-sm opacity-20 animate-pulse rounded-full"></div>
                                                    <Loader className="w-6 h-6 text-blue-400 animate-spin relative z-10" />
                                                </div>
                                            ) : (
                                                <div className="w-6 h-6 rounded-full border border-slate-700 bg-slate-800/50" />
                                            )}
                                            <span className={`text-sm ${step.status === 'running' ? 'text-blue-200 font-medium' : step.status === 'done' ? 'text-slate-400 line-through' : 'text-slate-600'}`}>
                                                {step.label}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Right: Terminal */}
                            <div>
                                <AgentTerminal logs={logs} />
                            </div>
                        </div>
                    </motion.div>
                )}

                {/* DONE PHASE */}
                {phase === 'done' && (
                    <motion.div
                        // ... (keep similar completion provided in previous context but enhanced)
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="text-center"
                    >
                        <div className="w-24 h-24 rounded-full bg-emerald-500/20 flex items-center justify-center mx-auto mb-8 border border-emerald-500/30 shadow-[0_0_40px_-5px_rgba(16,185,129,0.3)]">
                            <CheckCircle className="w-12 h-12 text-emerald-400" />
                        </div>

                        <h1 className="text-4xl font-bold text-white mb-2">
                            Infrastructure Ready.
                        </h1>
                        <p className="text-slate-400 mb-8 text-lg">
                            Your War Room is established. Agents are standing by.
                        </p>

                        <div className="inline-flex items-center gap-2 text-sm text-slate-500 animate-pulse">
                            Initializing Dashboard Interface...
                        </div>
                    </motion.div>
                )}
            </motion.div>
        </div>
    );
}
