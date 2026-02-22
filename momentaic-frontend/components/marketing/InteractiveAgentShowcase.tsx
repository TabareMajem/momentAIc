import React, { useState, useEffect } from 'react';
import { Bot, Zap, Orbit, ArrowRight, ShieldCheck, Cpu, Code2, Megaphone, Target } from 'lucide-react';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { cn } from '../../lib/utils';
import { Badge } from '../ui/Badge';

type NodeState = 'idle' | 'processing' | 'completed';

interface AgentNode {
    id: string;
    name: string;
    icon: any;
    color: string;
    state: NodeState;
    actionLog: string;
}

const ALL_AGENTS: AgentNode[] = [
    { id: 'brain', name: 'Startup Brain', icon: Cpu, color: 'text-purple-400', state: 'idle', actionLog: 'Awaiting signals...' },
    { id: 'sales', name: 'SDR Hunter', icon: Target, color: 'text-red-400', state: 'idle', actionLog: 'Standing by.' },
    { id: 'marketing', name: 'Viral Marketing', icon: Megaphone, color: 'text-green-400', state: 'idle', actionLog: 'Monitoring trends.' },
    { id: 'devops', name: 'DevOps & QA', icon: Code2, color: 'text-blue-400', state: 'idle', actionLog: 'All systems green.' },
    { id: 'legal', name: 'Legal Counsel', icon: ShieldCheck, color: 'text-yellow-400', state: 'idle', actionLog: 'Contracts synced.' },
];

export function InteractiveAgentShowcase() {
    const [agents, setAgents] = useState<AgentNode[]>(ALL_AGENTS);
    const [activeScenario, setActiveScenario] = useState<number | null>(null);
    const [logs, setLogs] = useState<string[]>(["> SWARM INITIALIZED. STATUS: DORMANT."]);

    const runSimulation = async (scenarioIndex: number) => {
        if (activeScenario !== null) return;
        setActiveScenario(scenarioIndex);
        setLogs([`> TRIGGERING EVENT SEQUENCE [${scenarioIndex}]...`]);

        // Reset state
        const resetAgents = agents.map(a => ({ ...a, state: 'idle' as NodeState, actionLog: 'Standing by.' }));
        setAgents(resetAgents);

        const seq = getSequence(scenarioIndex);

        for (let i = 0; i < seq.length; i++) {
            const step = seq[i];

            // Set processing
            setAgents(curr => curr.map(a =>
                a.id === step.agentId ? { ...a, state: 'processing', actionLog: step.action } : a
            ));
            setLogs(curr => [...curr, `[${step.agentId.toUpperCase()}] ${step.action}`]);

            await new Promise(r => setTimeout(r, 1500));

            // Set completed
            setAgents(curr => curr.map(a =>
                a.id === step.agentId ? { ...a, state: 'completed' } : a
            ));
        }

        setLogs(curr => [...curr, `> SEQUENCE COMPLETED. ALL NODES RETURN TO IDLE.`]);
        setTimeout(() => setActiveScenario(null), 2000);
    };

    const getSequence = (idx: number) => {
        if (idx === 1) {
            return [
                { agentId: 'brain', action: 'Detected competitor pricing drop.' },
                { agentId: 'marketing', action: 'Drafted counter-offer campaign.' },
                { agentId: 'sales', action: 'Emailed top 50 churn-risk accounts.' },
                { agentId: 'devops', action: 'Deployed promo banner to production.' }
            ];
        }
        return [
            { agentId: 'brain', action: 'Identified trending Reddit thread.' },
            { agentId: 'marketing', action: 'Generated viral reply + product mockup.' },
            { agentId: 'legal', action: 'Ensured compliance with promotional guidelines.' },
            { agentId: 'sales', action: 'Captured 42 new inbound leads.' }
        ];
    };

    return (
        <Card className="w-full bg-[#0a0a0a] border-purple-500/20 shadow-2xl overflow-hidden mt-8">
            <div className="p-6 border-b border-white/5 bg-gradient-to-r from-purple-900/20 to-transparent flex justify-between items-center">
                <div>
                    <h3 className="text-xl font-bold font-mono tracking-tight flex items-center gap-2">
                        <Orbit className="w-5 h-5 text-purple-400 animate-spin-slow" />
                        SWARM SIMULATOR v1.0
                    </h3>
                    <p className="text-xs text-gray-500 mt-1">Interactive demonstration of multi-agent concurrency.</p>
                </div>
                <Badge variant="cyber" className="text-[10px]">LIVE DEMO</Badge>
            </div>

            <div className="flex flex-col md:flex-row h-[500px]">
                {/* Left: Triggers & Logs */}
                <div className="w-full md:w-1/3 border-r border-white/5 bg-black/40 p-4 flex flex-col">
                    <div className="mb-6">
                        <h4 className="text-xs font-bold text-gray-400 mb-3 tracking-wider uppercase">Select Incident</h4>
                        <div className="space-y-2">
                            <Button
                                variant={activeScenario === 1 ? "cyber" : "outline"}
                                className="w-full justify-start text-xs h-10"
                                onClick={() => runSimulation(1)}
                                disabled={activeScenario !== null}
                            >
                                <Zap className="w-3 h-3 mr-2" /> Competitor Threat
                            </Button>
                            <Button
                                variant={activeScenario === 2 ? "cyber" : "outline"}
                                className="w-full justify-start text-xs h-10"
                                onClick={() => runSimulation(2)}
                                disabled={activeScenario !== null}
                            >
                                <Target className="w-3 h-3 mr-2" /> Viral Opportunity
                            </Button>
                        </div>
                    </div>

                    <div className="flex-1 bg-[#050505] rounded-md border border-white/10 p-3 font-mono text-[10px] overflow-y-auto w-full">
                        <div className="text-purple-400 mb-2">SYSTEM TERMINAL</div>
                        {logs.map((log, i) => (
                            <div key={i} className={cn(
                                "mb-1",
                                log.startsWith('>') ? "text-cyan-400" : "text-gray-300"
                            )}>
                                {log}
                            </div>
                        ))}
                    </div>
                </div>

                {/* Right: Visual Nodes */}
                <div className="flex-1 p-8 relative flex items-center justify-center bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-purple-900/10 via-[#0a0a0a] to-[#0a0a0a]">
                    <div className="relative w-full h-full max-w-md">
                        {/* Central Hub */}
                        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-16 h-16 bg-purple-500/10 border-2 border-purple-500/50 rounded-full flex items-center justify-center shadow-[0_0_30px_rgba(168,85,247,0.2)] z-10">
                            <Bot className="w-8 h-8 text-purple-400" />
                        </div>

                        {/* Orbiting Agents */}
                        {agents.map((agent, i) => {
                            const angle = (i * (360 / agents.length)) * (Math.PI / 180);
                            const radius = 140; // px
                            const x = Math.cos(angle) * radius;
                            const y = Math.sin(angle) * radius;

                            return (
                                <div
                                    key={agent.id}
                                    className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 transition-all duration-500 ease-in-out"
                                    style={{ transform: `translate(calc(-50% + ${x}px), calc(-50% + ${y}px))` }}
                                >
                                    <div className="flex flex-col items-center">
                                        <div className={cn(
                                            "w-12 h-12 rounded-full border-2 flex items-center justify-center mb-2 transition-all duration-300",
                                            agent.state === 'idle' ? "bg-black/50 border-gray-600 text-gray-500" :
                                                agent.state === 'processing' ? `bg-black border-white shadow-[0_0_15px_rgba(255,255,255,0.5)] ${agent.color} animate-pulse` :
                                                    `bg-black/80 ${agent.color} border-current shadow-[0_0_20px_currentColor]`
                                        )}>
                                            <agent.icon className="w-5 h-5" />
                                        </div>
                                        <div className="bg-black/80 border border-white/10 px-2 py-1 rounded text-[9px] font-mono whitespace-nowrap overflow-hidden text-center max-w-[120px]">
                                            <span className="font-bold text-white block mb-0.5">{agent.name}</span>
                                            <span className={cn(
                                                "truncate block transition-colors",
                                                agent.state === 'processing' ? "text-cyan-400" : "text-gray-500"
                                            )}>{agent.actionLog}</span>
                                        </div>
                                    </div>

                                    {/* Connection Line */}
                                    <svg className="absolute top-1/2 left-1/2 w-full h-full pointer-events-none -translate-x-1/2 -translate-y-1/2 opacity-30 z-[-1]" style={{ width: radius * 2, height: radius * 2, transform: `translate(-50%, -50%) rotate(${i * (360 / agents.length)}deg)` }}>
                                        <line x1="50%" y1="50%" x2="100%" y2="50%" stroke={agent.state !== 'idle' ? "currentColor" : "gray"} strokeWidth="1" className={cn(agent.state !== 'idle' ? agent.color : "", agent.state === 'processing' ? "animate-pulse" : "")} />
                                    </svg>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
        </Card>
    );
}
