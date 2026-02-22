import React, { useState, useEffect } from 'react';
import {
    Target, FileText, TrendingUp, Eye, Shield, Terminal,
    Zap, Globe, Cpu, Server, Lock, Activity,
    MessageSquare, Users, Briefcase, DollarSign
} from 'lucide-react';
import { cn } from '../../lib/utils';

// Full Roster of 16 Agents
const AGENT_ROSTER = [
    { id: 'REV-01', name: 'Sales Hunter', role: 'REVENUE', icon: Target, status: 'HUNTING' },
    { id: 'MKT-01', name: 'Content Engine', role: 'MARKETING', icon: FileText, status: 'VIRAL' },
    { id: 'GRO-01', name: 'Growth Hacker', role: 'SCALE', icon: TrendingUp, status: 'OPTIMIZING' },
    { id: 'INT-01', name: 'Competitor Intel', role: 'RECON', icon: Eye, status: 'WATCHING' },
    { id: 'LEG-01', name: 'Legal Sentinel', role: 'COMPLIANCE', icon: Shield, status: 'AUDITING' },
    { id: 'DEV-01', name: 'DevOps Guard', role: 'INFRA', icon: Terminal, status: 'PATCHING' },
    { id: 'ENG-01', name: 'Code Architect', role: 'PRODUCT', icon: Cpu, status: 'BUILDING' },
    { id: 'SUP-01', name: 'Support Swarm', role: 'CX', icon: MessageSquare, status: 'ANSWERING' },
    { id: 'DAT-01', name: 'Data Analyst', role: 'INSIGHT', icon: Activity, status: 'CRUNCHING' },
    { id: 'FIN-01', name: 'CFO Auto-Pilot', role: 'FINANCE', icon: DollarSign, status: 'BALANCING' },
    { id: 'HR-01', name: 'Recruiter Bot', role: 'TALENT', icon: Users, status: 'SOURCING' },
    { id: 'STR-01', name: 'Strategy Core', role: 'EXEC', icon: Briefcase, status: 'PLANNING' },
    { id: 'SEC-01', name: 'Security Grid', role: 'SEC_OPS', icon: Lock, status: 'SCANNING' },
    { id: 'NET-01', name: 'Network Mesh', role: 'CONN', icon: Globe, status: 'PINGING' },
    { id: 'SER-01', name: 'Server Admin', role: 'SYSADMIN', icon: Server, status: 'SCALING' },
    { id: 'PWR-01', name: 'Energy Optimizer', role: 'SUSTAIN', icon: Zap, status: 'SAVING' },
];

export function AgentHive() {
    const [activeAgent, setActiveAgent] = useState<string | null>(null);
    const [pulseAgent, setPulseAgent] = useState<string | null>(null);

    // Randomly pulse an agent to simulate activity
    useEffect(() => {
        const interval = setInterval(() => {
            const randomAgent = AGENT_ROSTER[Math.floor(Math.random() * AGENT_ROSTER.length)];
            setPulseAgent(randomAgent.id);
            setTimeout(() => setPulseAgent(null), 2000);
        }, 1500);
        return () => clearInterval(interval);
    }, []);

    return (
        <section className="py-24 bg-[#030014] relative overflow-hidden">
            <div className="absolute inset-0 bg-tech-grid opacity-10" />

            <div className="max-w-7xl mx-auto px-6 relative z-10">
                <div className="text-center mb-16">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-purple-500/30 bg-purple-500/10 text-purple-400 font-mono text-xs mb-6">
                        <Users className="w-3 h-3" />
                        ACTIVE_ROSTER // FULL_DEPLOYMENT
                    </div>
                    <h2 className="text-4xl md:text-6xl font-black text-white tracking-tighter mb-4">
                        The Hive Mind
                    </h2>
                    <p className="text-gray-400 font-mono text-sm">
                        16 Specialized Units working in perfect synchronization.
                    </p>
                </div>

                {/* THE HIVE GRID */}
                <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-8 gap-2">
                    {AGENT_ROSTER.map((agent) => (
                        <div
                            key={agent.id}
                            onMouseEnter={() => setActiveAgent(agent.id)}
                            onMouseLeave={() => setActiveAgent(null)}
                            className={cn(
                                "aspect-square relative group cursor-pointer transition-all duration-300",
                                pulseAgent === agent.id ? "z-20 scale-110" : "z-10 hover:scale-110 hover:z-30"
                            )}
                        >
                            {/* Card Body */}
                            <div className={cn(
                                "w-full h-full border bg-[#0a0a0f] flex flex-col items-center justify-center p-2 relative overflow-hidden clip-corner-1 transition-colors",
                                activeAgent === agent.id || pulseAgent === agent.id
                                    ? "border-purple-500 bg-purple-900/10"
                                    : "border-white/10 hover:border-white/30"
                            )}>
                                <div className="absolute inset-0 bg-tech-grid opacity-20" />

                                {(() => {
                                    const Icon = agent.icon;
                                    return (
                                        <Icon className={cn(
                                            "w-6 h-6 mb-2 transition-colors",
                                            activeAgent === agent.id || pulseAgent === agent.id ? "text-purple-400" : "text-gray-600"
                                        )} />
                                    );
                                })()}

                                <div className="text-[10px] font-mono font-bold text-center leading-tight text-gray-400">
                                    {agent.name.split(' ')[0]}
                                </div>
                                <div className="text-[8px] font-mono text-gray-600 mt-1">
                                    {agent.role}
                                </div>

                                {/* Status Indicator */}
                                {(activeAgent === agent.id || pulseAgent === agent.id) && (
                                    <div className="absolute bottom-1 right-1 flex gap-0.5">
                                        <div className="w-1 h-1 bg-green-500 rounded-full animate-ping" />
                                        <div className="w-1 h-1 bg-green-500 rounded-full" />
                                    </div>
                                )}
                            </div>

                            {/* HOVER DETAILS (Tooltip) - Commented out for debugging
                            {activeAgent === agent.id && (
                                <div className="absolute -top-24 left-1/2 -translate-x-1/2 w-48 bg-black/90 backdrop-blur-xl border border-purple-500 p-3 rounded clip-corner-4 pointer-events-none z-50 animate-fade-in-up">
                                    <div className="flex justify-between items-start mb-2 border-b border-white/10 pb-2">
                                        <span className="text-xs font-bold text-white">{agent.name}</span>
                                        <span className="text-[10px] font-mono text-purple-400">{agent.id}</span>
                                    </div>
                                    <div className="font-mono text-[10px] text-green-400 mb-1">
                                        > STATUS: {agent.status}
                                    </div>
                                    <div className="font-mono text-[10px] text-gray-500">
                                        CPU_USAGE: {Math.floor(Math.random() * 40 + 20)}%
                                    </div>
                                </div>
                            )}
                            */}
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
