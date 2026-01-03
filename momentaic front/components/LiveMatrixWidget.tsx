import React, { useEffect, useState, useRef } from 'react';
import { Activity, Zap, Search, MessageSquare, Terminal, UserPlus, DollarSign } from 'lucide-react';
import { cn } from '../../lib/utils';
import { api } from '../../lib/api';

type EventType = 'agent_activity' | 'new_lead' | 'email_sent' | 'user_signed_up' | 'payment_received';

interface ActivityEvent {
    id: string;
    type: EventType;
    data: any;
    timestamp: string;
}

const EVENT_ICONS: Record<EventType, any> = {
    'agent_activity': Terminal,
    'new_lead': Search,
    'email_sent': MessageSquare,
    'user_signed_up': UserPlus,
    'payment_received': DollarSign
};

export const LiveMatrixWidget = () => {
    const [events, setEvents] = useState<ActivityEvent[]>([]);
    const [isConnected, setIsConnected] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        // SSE Connection
        const token = api.getToken();
        const url = `${import.meta.env.VITE_API_URL || ''}/api/v1/events/stream`;

        // Native EventSource doesn't support headers easily, using fetch approach similar to streaming chat
        // OR using a polyfill. For simplicity, we'll try standard EventSource first (if authentication is cookie based or query param)
        // Since we use Bearer token, we need a workaround or query param. 
        // Let's assume we pass token in query param for SSE temporarily if possible, OR mostly likely use fetch loop in useEffect.

        // Using the Polyfill approach or just fetch loop for robust header support
        // Actually, let's use the fetch reader approach we mastered for chat

        const controller = new AbortController();

        const connectStream = async () => {
            try {
                const response = await fetch(url, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    },
                    signal: controller.signal
                });

                if (response.ok && response.body) {
                    setIsConnected(true);
                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();

                    while (true) {
                        const { value, done } = await reader.read();
                        if (done) break;

                        const chunk = decoder.decode(value, { stream: true });
                        const lines = chunk.split('\n\n');

                        for (const line of lines) {
                            if (line.startsWith('data: ')) {
                                try {
                                    const eventData = JSON.parse(line.slice(6));
                                    const newEvent: ActivityEvent = {
                                        id: Date.now().toString() + Math.random(),
                                        type: eventData.type || 'agent_activity', // fallback
                                        data: eventData,
                                        timestamp: new Date().toISOString()
                                    };

                                    setEvents(prev => [newEvent, ...prev].slice(0, 50)); // Keep last 50
                                } catch (e) {
                                    console.warn("Parse error", e);
                                }
                            }
                        }
                    }
                }
            } catch (err: any) {
                if (err.name !== 'AbortError') {
                    console.error("LiveMatrix connection failed", err);
                    setIsConnected(false);
                    // Retry logic could go here
                }
            }
        };

        connectStream();

        return () => {
            controller.abort();
            setIsConnected(false);
        };
    }, []);

    // Auto-scroll logic could be added here, currently sticking to top (newest first)

    return (
        <div className="bg-[#050505] border border-white/10 rounded-xl overflow-hidden flex flex-col h-[300px]">
            <div className="p-3 bg-black/50 border-b border-white/5 flex justify-between items-center">
                <div className="flex items-center gap-2">
                    <Activity className={cn("w-4 h-4", isConnected ? "text-green-500" : "text-gray-500")} />
                    <span className="text-xs font-mono uppercase tracking-widest text-gray-400">Live Matrix</span>
                </div>
                {isConnected && <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />}
            </div>

            <div className="flex-1 overflow-y-auto p-2 space-y-2 font-mono text-xs" ref={scrollRef}>
                {events.length === 0 && (
                    <div className="text-center text-gray-600 py-8">
                        Waiting for signals...
                    </div>
                )}

                {events.map((event) => {
                    const Icon = EVENT_ICONS[event.type] || Zap;
                    return (
                        <div key={event.id} className="flex gap-3 p-2 rounded bg-white/5 border border-white/5 items-start animate-fade-in group hover:bg-white/10 transition-colors">
                            <div className="mt-0.5 text-gray-400 group-hover:text-[#00f0ff] transition-colors">
                                <Icon className="w-3 h-3" />
                            </div>
                            <div className="flex-1 overflow-hidden">
                                <div className="flex justify-between items-baseline mb-1">
                                    <span className="text-[#00f0ff] font-bold uppercase text-[10px] tracking-wider">
                                        {event.data.agent || event.type}
                                    </span>
                                    <span className="text-gray-600 text-[9px]">
                                        {new Date(event.timestamp).toLocaleTimeString()}
                                    </span>
                                </div>
                                <p className="text-gray-300 truncate font-light">
                                    {event.data.action || JSON.stringify(event.data)}
                                    {event.data.status && <span className="text-gray-500 ml-1">[{event.data.status}]</span>}
                                </p>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};
