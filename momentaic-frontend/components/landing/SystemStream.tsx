import React, { useState, useEffect } from 'react';
import { cn } from '../../lib/utils';
import { Terminal, Shield, Zap, CheckCircle2 } from 'lucide-react';

const EVENTS = [
    { type: 'info', msg: 'Sales Hunter Agent: Identified 50 new leads in Fintech.' },
    { type: 'success', msg: 'Core System: Daily backup completed successfully.' },
    { type: 'warning', msg: 'Security Grid: Blocked 3 unauthorized access attempts.' },
    { type: 'info', msg: 'Content Engine: Viral thread drafted for approval.' },
    { type: 'success', msg: 'DevOps Guard: Deployed patch v2.4.1 to production.' },
];

export function SystemStream() {
    const [events, setEvents] = useState<any[]>([]);

    useEffect(() => {
        const interval = setInterval(() => {
            const newEvent = EVENTS[Math.floor(Math.random() * EVENTS.length)];
            const timestamp = new Date().toLocaleTimeString();
            setEvents(prev => [{ ...newEvent, timestamp, id: Math.random() }, ...prev].slice(0, 3));
        }, 4000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="fixed bottom-8 right-8 z-[100] w-80 pointer-events-none flex flex-col-reverse gap-2">
            {events.map((event) => (
                <div
                    key={event.id}
                    className="bg-black/90 backdrop-blur-md border border-white/20 p-3 rounded clip-corner-4 animate-slide-up shadow-xl"
                >
                    <div className="flex justify-between items-start mb-1">
                        <div className="flex items-center gap-2">
                            {event.type === 'info' && <Terminal className="w-3 h-3 text-blue-400" />}
                            {event.type === 'success' && <CheckCircle2 className="w-3 h-3 text-green-400" />}
                            {event.type === 'warning' && <Shield className="w-3 h-3 text-yellow-400" />}
                            <span className="text-[10px] font-mono font-bold text-gray-300">SYSTEM_EVENT</span>
                        </div>
                        <span className="text-[9px] font-mono text-gray-600">{event.timestamp}</span>
                    </div>
                    <p className="text-xs font-mono text-gray-400 leading-tight">
                        {event.msg}
                    </p>
                </div>
            ))}
        </div>
    );
}
