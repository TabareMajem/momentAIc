import React, { useState, useEffect } from 'react';
import { Target, MessageSquare, Zap, Database, Search, FileText, CheckCircle2, ArrowRight } from 'lucide-react';
import { cn } from '../../lib/utils';

// Types for our simulation steps
type ProtocolStep = {
    id: string;
    label: string;
    icon: any;
    status: 'pending' | 'active' | 'complete';
    log: string;
};

const PROTOCOLS = {
    'REVENUE_HUNT': {
        name: 'REVENUE_HUNT_v9',
        desc: 'Autonomous Outbound Sales Campaign',
        steps: [
            { id: '1', label: 'TARGET_IDENTIFICATION', icon: Search, log: 'Scanning LinkedIn for CEOs in Fintech...' },
            { id: '2', label: 'DATA_ENRICHMENT', icon: Database, log: 'Enriching profiles with Clay/Apollo data...' },
            { id: '3', label: 'STRATEGY_GENERATION', icon: Zap, log: 'Generating personalized hooks using GPT-4o...' },
            { id: '4', label: 'EXECUTION', icon: MessageSquare, log: 'Dispatching emails. A/B tests active.' },
        ]
    },
    'VIRAL_DOMINATION': {
        name: 'VIRAL_DOMINATION_v4',
        desc: 'Trend-Hijacking Content Engine',
        steps: [
            { id: '1', label: 'TREND_ANALYSIS', icon: Search, log: 'Detecting rising topics on X/Reddit...' },
            { id: '2', label: 'NARRATIVE_CRAFT', icon: FileText, log: 'Drafting thread: "AI in 2026"...' },
            { id: '3', label: 'ASSET_GENERATION', icon: Target, log: 'Creating Midjourney thumbnails...' },
            { id: '4', label: 'DISTRIBUTION', icon: Zap, log: 'Posted to X, LinkedIn, Medium.' },
        ]
    }
};

export function ProtocolShowcase() {
    const [activeProtocol, setActiveProtocol] = useState<keyof typeof PROTOCOLS>('REVENUE_HUNT');
    const [progress, setProgress] = useState(0);
    const [logs, setLogs] = useState<string[]>([]);

    // Simulation Loop
    useEffect(() => {
        setProgress(0);
        setLogs([]);
        let stepIndex = 0;

        const interval = setInterval(() => {
            if (stepIndex <= 3) {
                const currentProtocol = PROTOCOLS[activeProtocol];
                const step = currentProtocol.steps[stepIndex];

                // Update Progress
                setProgress(stepIndex + 1);

                // Add Log
                setLogs(prev => [`[${new Date().toLocaleTimeString()}] ${step.label}: ${step.log}`, ...prev].slice(0, 5));

                stepIndex++;
            } else {
                // Reset simulation after a pause
                setTimeout(() => {
                    stepIndex = 0;
                    setProgress(0);
                    setLogs([]);
                }, 2000);
            }
        }, 1500);

        return () => clearInterval(interval);
    }, [activeProtocol]);

    return (
        <section className="py-24 px-6 bg-[#020202] relative overflow-hidden">
            {/* Background Decorations */}
            <div className="absolute top-0 right-0 w-1/2 h-full bg-purple-900/5 clip-corner-1" />
            <div className="absolute bottom-0 left-0 w-64 h-64 bg-blue-900/10 rounded-full blur-[100px]" />

            <div className="max-w-7xl mx-auto relative z-10">
                <div className="flex flex-col lg:flex-row gap-12">

                    {/* LEFT: Controls */}
                    <div className="lg:w-1/3 space-y-8">
                        <div>
                            <div className="flex items-center gap-2 mb-2">
                                <div className="w-2 h-2 bg-purple-500 animate-pulse" />
                                <span className="text-xs font-mono text-purple-500 tracking-widest">MISSION CONTROL</span>
                            </div>
                            <h2 className="text-4xl font-black text-white mb-4">Execute Protocol</h2>
                            <p className="text-gray-400 font-mono text-sm leading-relaxed">
                                Select a mission objective. Watch the Agent Swarm execute the workflow in real-time.
                            </p>
                        </div>

                        <div className="space-y-4">
                            {(Object.keys(PROTOCOLS) as Array<keyof typeof PROTOCOLS>).map((key) => (
                                <button
                                    key={key}
                                    onClick={() => setActiveProtocol(key)}
                                    className={cn(
                                        "w-full text-left p-6 border transition-all duration-300 group relative overflow-hidden clip-corner-4",
                                        activeProtocol === key
                                            ? "bg-purple-900/20 border-purple-500/50"
                                            : "bg-[#0a0a0f] border-white/10 hover:border-white/20"
                                    )}
                                >
                                    <div className="relative z-10">
                                        <div className="text-xs font-mono text-gray-500 mb-1">{key}</div>
                                        <div className={cn(
                                            "font-bold text-lg",
                                            activeProtocol === key ? "text-white" : "text-gray-400 group-hover:text-white"
                                        )}>
                                            {PROTOCOLS[key].desc}
                                        </div>
                                    </div>

                                    {/* Active Indicator */}
                                    {activeProtocol === key && (
                                        <div className="absolute right-4 top-1/2 -translate-y-1/2 text-purple-500">
                                            <div className="flex gap-1">
                                                <div className="w-1 h-1 bg-purple-500 rounded-full animate-ping" />
                                                <div className="w-1 h-1 bg-purple-500 rounded-full" />
                                            </div>
                                        </div>
                                    )}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* RIGHT: Visualization */}
                    <div className="lg:w-2/3">
                        <div className="h-full bg-[#050508] border border-white/10 rounded-xl relative overflow-hidden p-8 flex flex-col">
                            {/* Header */}
                            <div className="flex justify-between items-center mb-12 border-b border-white/5 pb-4">
                                <div className="font-mono text-sm text-gray-400">
                                    PROTOCOL: <span className="text-purple-400">{PROTOCOLS[activeProtocol].name}</span>
                                </div>
                                <div className="flex gap-2">
                                    <div className="w-3 h-3 rounded-full bg-red-500/20 border border-red-500/50" />
                                    <div className="w-3 h-3 rounded-full bg-yellow-500/20 border border-yellow-500/50" />
                                    <div className="w-3 h-3 rounded-full bg-green-500/20 border border-green-500/50" />
                                </div>
                            </div>

                            {/* Flowchart */}
                            <div className="flex-1 relative">
                                {/* Connecting Line */}
                                <div className="absolute top-8 left-8 right-8 h-1 bg-white/5 z-0">
                                    <div
                                        className="h-full bg-purple-500 transition-all duration-500 ease-linear"
                                        style={{ width: `${(Math.max(0, progress - 1) / 3) * 100}%` }}
                                    />
                                </div>

                                <div className="relative z-10 grid grid-cols-4 gap-4">
                                    {PROTOCOLS[activeProtocol].steps.map((step, index) => {
                                        const isActive = index < progress;
                                        const isCurrent = index === progress - 1;

                                        return (
                                            <div key={step.id} className="flex flex-col items-center text-center">
                                                <div className={cn(
                                                    "w-16 h-16 rounded-xl flex items-center justify-center border-2 transition-all duration-500 mb-4 bg-[#0a0a0f]",
                                                    isActive
                                                        ? "border-purple-500 text-purple-400 shadow-[0_0_20px_rgba(168,85,247,0.3)]"
                                                        : "border-white/10 text-gray-600"
                                                )}>
                                                    <step.icon className={cn("w-6 h-6", isCurrent && "animate-pulse")} />
                                                </div>
                                                <div className={cn(
                                                    "text-[10px] font-mono tracking-widest transition-colors duration-300",
                                                    isActive ? "text-purple-400" : "text-gray-600"
                                                )}>
                                                    {step.label}
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>

                            {/* Live Logs */}
                            <div className="mt-12 bg-black/50 border border-white/10 rounded-lg p-4 font-mono text-xs h-32 overflow-hidden relative">
                                <div className="absolute top-2 right-4 text-gray-600 text-[10px]">LIVE_LOGS_TERM_01</div>
                                <div className="space-y-2 mt-4">
                                    {logs.map((log, i) => (
                                        <div key={i} className="text-green-400/80 animate-slide-up">
                                            <span className="text-gray-600 mr-2">{'>'}</span>
                                            {log}
                                        </div>
                                    ))}
                                    {logs.length === 0 && (
                                        <div className="text-gray-700 italic">Waiting for execution command...</div>
                                    )}
                                </div>
                            </div>

                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
