import React, { useState, useEffect, useRef } from 'react';
import { cn } from '../../lib/utils';
import { Terminal, Cpu, Shield, Globe, Zap, Activity } from 'lucide-react';

interface Log {
    id: string;
    agent: string;
    action: string;
    status: 'success' | 'processing' | 'warning';
    timestamp: string;
}

const AGENTS = [
    { name: 'Sales Hunter', status: 'active', color: 'text-blue-400' },
    { name: 'Growth Hacker', status: 'active', color: 'text-emerald-400' },
    { name: 'Legal Sentinel', status: 'processing', color: 'text-red-400' },
    { name: 'Content Creator', status: 'active', color: 'text-pink-400' },
    { name: 'Competitor Intel', status: 'idle', color: 'text-amber-400' },
];

const MOCK_LOGS = [
    { agent: 'Sales Hunter', action: 'Identified 3 high-value leads in Fintech sector', status: 'success' },
    { agent: 'Growth Hacker', action: 'Optimizing landing page A/B test (Variant B)', status: 'processing' },
    { agent: 'Competitor Intel', action: 'Detected pricing change: Competitor X (-15%)', status: 'warning' },
    { agent: 'Content Creator', action: 'Generated viral thread: "AI Scaling Secrets"', status: 'success' },
    { agent: 'Legal Sentinel', action: 'Scanning contract for compliance risks...', status: 'processing' },
    { agent: 'Sales Hunter', action: 'Drafting personalized outreach for CEO @ TechCorp', status: 'processing' },
    { agent: 'Growth Hacker', action: ' SEO Score updated: 92/100 (+4%)', status: 'success' },
    { agent: 'System', action: 'Auto-scaling infrastructure to handle load spike', status: 'warning' },
];

export const AgentCommandCenter = () => {
    const [logs, setLogs] = useState<Log[]>([]);
    const scrollRef = useRef<HTMLDivElement>(null);

    // Simulate live logs
    useEffect(() => {
        let interval: NodeJS.Timeout;
        const addLog = () => {
            const randomLog = MOCK_LOGS[Math.floor(Math.random() * MOCK_LOGS.length)];
            const newLog: Log = {
                id: Math.random().toString(36).substr(2, 9),
                agent: randomLog.agent,
                action: randomLog.action,
                status: randomLog.status as any,
                timestamp: new Date().toLocaleTimeString('en-US', { hour12: false })
            };

            setLogs(prev => [...prev.slice(-15), newLog]); // Keep last 15 logs
        };

        // Initial burst
        for (let i = 0; i < 5; i++) setTimeout(addLog, i * 200);

        // Ongoing stream
        interval = setInterval(() => {
            if (Math.random() > 0.3) addLog();
        }, 1500);

        return () => clearInterval(interval);
    }, []);

    // Auto-scroll
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [logs]);

    return (
        <div className="w-full max-w-5xl mx-auto p-4">
            <div className="relative rounded-xl overflow-hidden bg-[#0a0a0f] border border-white/10 shadow-2xl shadow-purple-500/10">
                {/* Header Bar */}
                <div className="bg-[#12121a] border-b border-white/5 p-3 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <div className="flex gap-1.5">
                            <div className="w-3 h-3 rounded-full bg-red-500/80" />
                            <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                            <div className="w-3 h-3 rounded-full bg-green-500/80" />
                        </div>
                        <span className="ml-4 text-xs font-mono text-gray-500">momentaic-core // live-ops</span>
                    </div>
                    <div className="flex items-center gap-4 text-xs font-mono text-gray-500">
                        <span className="flex items-center gap-1.5">
                            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                            Connected
                        </span>
                        <span>v2.4.0-stable</span>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 h-[400px]">
                    {/* Sidebar: Active Agents */}
                    <div className="hidden md:block col-span-1 bg-[#0f0f15] border-r border-white/5 p-4 overflow-y-auto">
                        <h3 className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                            <Cpu className="w-3 h-3" /> Active Agents
                        </h3>
                        <div className="space-y-3">
                            {AGENTS.map((agent) => (
                                <div key={agent.name} className="flex items-center justify-between group cursor-default">
                                    <div className="flex items-center gap-2">
                                        <div className={cn("w-1.5 h-1.5 rounded-full", agent.status === 'active' ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]' : 'bg-yellow-500')} />
                                        <span className={cn("text-xs font-mono group-hover:text-white transition-colors", agent.color)}>{agent.name}</span>
                                    </div>
                                    <Activity className="w-3 h-3 text-white/10 group-hover:text-white/30" />
                                </div>
                            ))}
                        </div>

                        <div className="mt-8 pt-4 border-t border-white/5">
                            <div className="bg-white/5 rounded-lg p-3">
                                <span className="text-[10px] text-gray-400 block mb-1">System Load</span>
                                <div className="w-full h-1 bg-white/10 rounded-full overflow-hidden">
                                    <div className="h-full bg-purple-500 w-[42%] animate-pulse" />
                                </div>
                                <div className="flex justify-between mt-1 text-[10px] font-mono text-gray-500">
                                    <span>CPU: 42%</span>
                                    <span>MEM: 1.2GB</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Main Terminal Window */}
                    <div className="col-span-3 bg-[#050508] relative font-mono text-xs md:text-sm p-4 overflow-hidden group">
                        {/* CRT Scanline Overlay */}
                        <div className="absolute inset-0 scanlines opacity-50 pointer-events-none z-10" />

                        {/* Logs */}
                        <div ref={scrollRef} className="h-full overflow-y-auto space-y-2 pr-2 pb-8 scroll-smooth hide-scrollbar relative z-0">
                            {logs.map((log) => (
                                <div key={log.id} className="flex gap-3 animate-slide-up hover:bg-white/5 p-1 rounded transition-colors">
                                    <span className="text-gray-600 shrink-0">[{log.timestamp}]</span>
                                    <span className={cn("font-bold shrink-0 w-32",
                                        log.agent === 'Sales Hunter' ? 'text-blue-400' :
                                            log.agent === 'Growth Hacker' ? 'text-emerald-400' :
                                                log.agent === 'Legal Sentinel' ? 'text-red-400' :
                                                    log.agent === 'Competitor Intel' ? 'text-amber-400' :
                                                        log.agent === 'Content Creator' ? 'text-pink-400' : 'text-gray-400'
                                    )}>
                                        {log.agent}
                                    </span>
                                    <span className={cn("truncate",
                                        log.status === 'success' ? 'text-gray-300' :
                                            log.status === 'warning' ? 'text-yellow-200' : 'text-gray-500'
                                    )}>{log.action}</span>
                                    {log.status === 'success' && <span className="text-green-500 ml-auto opacity-0 group-hover:opacity-100 transition-opacity">✓</span>}
                                </div>
                            ))}
                            {/* Blinking Cursor */}
                            <div className="flex items-center gap-2 text-purple-500/50 mt-4">
                                <span>_ root@momentaic-core:</span>
                                <span className="w-2 h-4 bg-purple-500 animate-pulse" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
