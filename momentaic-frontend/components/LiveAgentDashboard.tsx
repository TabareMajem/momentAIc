import React, { useEffect, useState, useRef } from 'react';
import { Activity, Terminal, Radio } from 'lucide-react';
import { useChatStore } from '../stores/chat-store';
import { api } from '../lib/api';

interface AgentEvent {
    id: string;
    type: string;
    agent: string;
    action: string;
    timestamp: string;
}

export function LiveAgentDashboard() {
    const { currentStartupId } = useChatStore();
    const [events, setEvents] = useState<AgentEvent[]>([]);
    const [isConnected, setIsConnected] = useState(false);
    const wsRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        if (!currentStartupId) return;

        const token = api.getToken();
        const wsUrl = import.meta.env.VITE_WS_URL || (window.location.protocol === 'https:' ? 'wss:' : 'ws:') + '//' + window.location.host;
        // We just need the websocket domain, assuming API URL aligns with host. If Vite uses proxy, we hit the proxy.
        const url = `${wsUrl}/api/v1/ws/agents/${currentStartupId}`;

        // Close existing connection if startup ID changes
        if (wsRef.current) {
            wsRef.current.close();
        }

        try {
            const ws = new WebSocket(url);

            ws.onopen = () => {
                setIsConnected(true);
                // Start connection
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    setEvents(prev => {
                        const newEvents = [
                            { id: Math.random().toString(36).substring(7), ...data },
                            ...prev
                        ].slice(0, 50); // Keep last 50 events
                        return newEvents;
                    });
                } catch (e) {
                    console.error("Invalid WS message", e);
                }
            };

            ws.onclose = () => {
                setIsConnected(false);
            };

            wsRef.current = ws;
        } catch (e) {
            console.error("WebSocket connection failed", e);
        }

        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, [currentStartupId]);

    if (!currentStartupId) return null;

    return (
        <div className="bg-[#050505] border border-white/10 rounded-xl flex flex-col overflow-hidden h-full max-h-[400px]">
            <div className="flex justify-between items-center p-3 border-b border-white/5 bg-black/40">
                <div className="flex items-center gap-2">
                    <Terminal className="w-4 h-4 text-[#00f0ff]" />
                    <span className="text-xs font-mono uppercase tracking-widest text-[#00f0ff]">Swarm Activity</span>
                </div>
                <div className="flex items-center gap-2">
                    {isConnected ? (
                        <span className="flex items-center gap-1 text-[10px] text-green-400 font-mono">
                            <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
                            LIVE
                        </span>
                    ) : (
                        <span className="flex items-center gap-1 text-[10px] text-gray-500 font-mono">
                            <span className="w-1.5 h-1.5 rounded-full bg-gray-600" />
                            OFFLINE
                        </span>
                    )}
                </div>
            </div>

            <div className="flex-1 overflow-y-auto p-3 space-y-2 font-mono text-[10px] sm:text-xs">
                {events.length === 0 && (
                    <div className="text-gray-600 flex flex-col items-center justify-center h-full gap-2">
                        <Radio className="w-6 h-6 animate-pulse opacity-50" />
                        <span>Awaiting telemetry...</span>
                    </div>
                )}

                {events.map((ev, i) => (
                    <div key={ev.id} className="flex items-start gap-2 animate-fade-in text-gray-400 group hover:bg-white/5 p-1 -mx-1 rounded">
                        <span className="text-[#00f0ff]/50 whitespace-nowrap pt-0.5">[{new Date(ev.timestamp).toLocaleTimeString()}]</span>
                        <span className="text-white font-bold whitespace-nowrap uppercase tracking-wider">{ev.agent}:</span>
                        <span className="text-gray-300 group-hover:text-white transition-colors">{ev.action}</span>
                    </div>
                ))}
            </div>
        </div>
    );
}
