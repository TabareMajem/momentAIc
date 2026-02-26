import React, { useState, useEffect, useRef } from 'react';
import {
    Bot, Sparkles, Zap, Send, Users, TrendingUp, FileText,
    Activity, Radio, Loader2, CheckCircle, ArrowRight
} from 'lucide-react';
import { Button } from '../components/ui/Button';

interface AgentEvent {
    id: string;
    agent: string;
    action: string;
    status: 'working' | 'complete' | 'waiting';
    timestamp: Date;
    details?: string;
}

const AGENT_CONFIG = {
    'Siren': { icon: Sparkles, color: 'from-pink-500 to-purple-500', desc: 'Content & Growth' },
    'Hunter': { icon: Users, color: 'from-blue-500 to-cyan-500', desc: 'Sales & Leads' },
    'Builder': { icon: Zap, color: 'from-yellow-500 to-orange-500', desc: 'Dev & Ops' },
    'Strategist': { icon: TrendingUp, color: 'from-green-500 to-emerald-500', desc: 'Analysis' },
};

export default function LiveAgentView() {
    const [events, setEvents] = useState<AgentEvent[]>([]);
    const [connected, setConnected] = useState(false);
    const [activeAgents, setActiveAgents] = useState<string[]>([]);
    const eventEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        // Connect to WebSocket for real-time agent updates
        const token = localStorage.getItem('access_token');
        const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/agents?token=${token}`;

        let ws: WebSocket | null = null;

        try {
            ws = new WebSocket(wsUrl);

            ws.onopen = () => {
                setConnected(true);
                console.log('Agent WebSocket connected');
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);

                if (data.type === 'agent_event') {
                    const newEvent: AgentEvent = {
                        id: `${Date.now()}-${Math.random()}`,
                        agent: data.agent,
                        action: data.action,
                        status: data.status,
                        timestamp: new Date(),
                        details: data.details
                    };

                    setEvents(prev => [...prev.slice(-50), newEvent]); // Keep last 50 events

                    if (data.status === 'working' && !activeAgents.includes(data.agent)) {
                        setActiveAgents(prev => [...prev, data.agent]);
                    } else if (data.status === 'complete') {
                        setActiveAgents(prev => prev.filter(a => a !== data.agent));
                    }
                }
            };

            ws.onclose = () => {
                setConnected(false);
                console.log('Agent WebSocket disconnected');
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
        } catch (e) {
            console.error('Failed to connect WebSocket:', e);
        }

        // Simulate some events for demo
        // REMOVED: Previously injected hardcoded demo events.
        // The WebSocket connection above handles real agent events.

        return () => {
            if (ws) ws.close();
        };
    }, []);

    useEffect(() => {
        eventEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [events]);

    return (
        <div className="min-h-screen bg-[#020202] text-white">
            {/* Header */}
            <div className="border-b border-white/10 bg-black/50 backdrop-blur-xl sticky top-0 z-20 p-6">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <div className="relative">
                            <div className="p-3 rounded-xl bg-gradient-to-br from-purple-500/20 to-cyan-500/20 border border-white/10">
                                <Activity className="w-6 h-6 text-purple-400" />
                            </div>
                            <div className={`absolute -top-1 -right-1 w-3 h-3 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'} animate-pulse`} />
                        </div>
                        <div>
                            <h1 className="text-2xl font-black tracking-tight">LIVE AI TEAM</h1>
                            <p className="text-sm text-gray-500 font-mono">Watch your agents work in real-time</p>
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <div className={`flex items-center gap-2 px-4 py-2 rounded-full ${connected ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'} text-sm font-mono`}>
                            <Radio className="w-4 h-4" />
                            {connected ? 'CONNECTED' : 'CONNECTING...'}
                        </div>
                        <div className="text-sm text-gray-500">
                            {activeAgents.length} agents active
                        </div>
                    </div>
                </div>
            </div>

            <div className="p-6 grid grid-cols-1 lg:grid-cols-4 gap-6">
                {/* Agent Status Cards */}
                <div className="lg:col-span-1 space-y-4">
                    <h2 className="text-xs font-mono text-gray-500 uppercase tracking-widest mb-4">AGENT SWARM STATUS</h2>

                    {Object.entries(AGENT_CONFIG).map(([name, config]) => {
                        const Icon = config.icon;
                        const isActive = activeAgents.includes(name);

                        return (
                            <div
                                key={name}
                                className={`p-4 rounded-xl border transition-all ${isActive
                                    ? 'bg-white/5 border-white/20'
                                    : 'bg-black/30 border-white/5'
                                    }`}
                                animate={{
                                    boxShadow: isActive ? '0 0 30px rgba(168,85,247,0.2)' : 'none'
                                }}
                            >
                                <div className="flex items-center gap-3">
                                    <div className={`p-2 rounded-lg bg-gradient-to-br ${config.color}`}>
                                        <Icon className="w-5 h-5 text-white" />
                                    </div>
                                    <div className="flex-1">
                                        <div className="font-bold text-white">{name}</div>
                                        <div className="text-xs text-gray-500">{config.desc}</div>
                                    </div>
                                    {isActive ? (
                                        <Loader2 className="w-4 h-4 text-purple-400 animate-spin" />
                                    ) : (
                                        <div className="w-2 h-2 rounded-full bg-gray-600" />
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>

                {/* Live Event Stream */}
                <div className="lg:col-span-3">
                    <h2 className="text-xs font-mono text-gray-500 uppercase tracking-widest mb-4">LIVE ACTIVITY STREAM</h2>

                    <div className="bg-black/30 rounded-xl border border-white/10 p-4 h-[600px] overflow-y-auto">

                        {events.map((event) => {
                            const agentConfig = AGENT_CONFIG[event.agent as keyof typeof AGENT_CONFIG] || AGENT_CONFIG['Strategist'];
                            const Icon = agentConfig.icon;

                            return (
                                <div
                                    key={event.id}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: 20 }}
                                    className="flex items-start gap-4 p-4 border-b border-white/5 last:border-0"
                                >
                                    <div className={`p-2 rounded-lg bg-gradient-to-br ${agentConfig.color} shrink-0`}>
                                        <Icon className="w-4 h-4 text-white" />
                                    </div>

                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-2 mb-1">
                                            <span className="font-bold text-white">{event.agent}</span>
                                            {event.status === 'working' && (
                                                <span className="flex items-center gap-1 text-xs text-purple-400 font-mono">
                                                    <Loader2 className="w-3 h-3 animate-spin" />
                                                    WORKING
                                                </span>
                                            )}
                                            {event.status === 'complete' && (
                                                <span className="flex items-center gap-1 text-xs text-green-400 font-mono">
                                                    <CheckCircle className="w-3 h-3" />
                                                    DONE
                                                </span>
                                            )}
                                        </div>
                                        <p className="text-sm text-gray-300">{event.action}</p>
                                        {event.details && (
                                            <p className="text-xs text-gray-500 mt-1 font-mono">{event.details}</p>
                                        )}
                                    </div>

                                    <div className="text-xs text-gray-600 font-mono shrink-0">
                                        {event.timestamp.toLocaleTimeString()}
                                    </div>
                                </div>
                            );
                        })}

                        <div ref={eventEndRef} />
                    </div>
                </div>
            </div>
        </div>
    );
}
