import React, { useState, useEffect, useRef } from 'react';
import { PageMeta } from '../components/ui/PageMeta';
import { Globe, Terminal, Play, Square, Loader2, MousePointer2, Type, RefreshCw, Zap, ShieldAlert, CheckCircle2, ChevronRight } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { useToast } from '../components/ui/Toast';
import { cn } from '../lib/utils';
import { Badge } from '../components/ui/Badge';

interface BrowserLog {
    id: string;
    timestamp: string;
    action: 'NAVIGATE' | 'CLICK' | 'TYPE' | 'EXTRACT' | 'SYSTEM' | 'ERROR';
    details: string;
}

export default function OpenClawProxy() {
    const { toast } = useToast();
    const scrollRef = useRef<HTMLDivElement>(null);
    const wsRef = useRef<WebSocket | null>(null);

    const [directive, setDirective] = useState('');
    const [status, setStatus] = useState<'IDLE' | 'INITIALIZING' | 'EXECUTING' | 'COMPLETED' | 'FAILED'>('IDLE');
    const [activeUrl, setActiveUrl] = useState('about:blank');
    const [cursorPos, setCursorPos] = useState({ x: 50, y: 50 });
    const [logs, setLogs] = useState<BrowserLog[]>([]);

    const addLog = (action: BrowserLog['action'], details: string) => {
        setLogs(prev => [...prev, {
            id: Math.random().toString(36).substr(2, 9),
            timestamp: new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }),
            action,
            details
        }]);
    };

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [logs]);

    const handleExecute = () => {
        if (!directive.trim()) return;

        setStatus('INITIALIZING');
        setLogs([]);

        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const wsUrl = apiUrl.replace('http', 'ws') + '/api/v1/openclaw/stream';

        try {
            const ws = new WebSocket(wsUrl);
            wsRef.current = ws;

            ws.onopen = () => {
                setStatus('EXECUTING');
                ws.send(directive);
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.type === 'log') {
                        addLog(data.action, data.details);
                        if (data.details.includes('Routing to')) {
                            const urlMatch = data.details.split('Routing to ')[1];
                            if (urlMatch) setActiveUrl(urlMatch.replace('...', ''));
                        }
                        if (data.details.includes('Container shutting down')) {
                            setStatus('COMPLETED');
                            toast({ type: 'success', title: 'EXECUTION COMPLETE', message: 'OpenClaw successfully handled the browser simulation.' });
                        }
                        if (data.action === 'ERROR') {
                            setStatus('FAILED');
                        }
                    } else if (data.type === 'cursor') {
                        setCursorPos({ x: data.x, y: data.y });
                    }
                } catch (e) {
                    console.error("Failed to parse WS message", e);
                }
            };

            ws.onerror = (err) => {
                console.error('WebSocket Error:', err);
                setStatus('FAILED');
                addLog('ERROR', 'WebSocket connection failed.');
            };

            ws.onclose = () => {
                if (status === 'EXECUTING') {
                    setStatus('COMPLETED');
                }
            };
        } catch (error) {
            setStatus('FAILED');
            addLog('ERROR', 'Failed to establish WebSocket connection.');
        }
    };

    const handleAbort = () => {
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }
        setStatus('FAILED');
        addLog('ERROR', 'USER ABORT INITIATED. Killing browser container.');
    };

    return (
        <div className="max-w-6xl mx-auto pb-20 mt-8 min-h-screen flex flex-col">
            <PageMeta title="OpenClaw Proxy | MomentAIc" description="Watch your agents execute tasks on the actual internet." />

            {/* Header */}
            <div className="mb-8">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-[#00f0ff]/30 bg-[#00f0ff]/10 text-[#00f0ff] font-mono text-xs mb-4">
                    <Globe className="w-3 h-3 animate-pulse" /> OPEN_CLAW_PROXY_ONLINE
                </div>
                <h1 className="text-4xl md:text-5xl font-black text-white mb-4 tracking-tighter uppercase relative group">
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#00f0ff] to-blue-500 drop-shadow-[0_0_15px_rgba(0,240,255,0.8)]">
                        Internet Execution
                    </span>
                </h1>
                <p className="text-gray-400 font-mono text-sm max-w-2xl border-l-2 border-[#00f0ff] pl-4">
                    When an API doesn't exist, we send in the Claws. Give the Swarm a natural language directive, and watch it spin up a headless browser to execute actions natively on the internet.
                </p>
            </div>

            {/* Main Interactive Area */}
            <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-6">

                {/* Left Column: Command & Logs */}
                <div className="lg:col-span-1 flex flex-col gap-6">
                    {/* Command Input */}
                    <div className="bg-[#0a0a0f] border border-white/10 p-5 rounded-xl shadow-lg relative overflow-hidden group hover:border-[#00f0ff]/50 transition-colors">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-[#00f0ff]/5 rounded-bl-[100px] -z-10 group-hover:bg-[#00f0ff]/10 transition-colors" />

                        <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest font-mono mb-4 flex items-center gap-2">
                            <Terminal className="w-4 h-4 text-[#00f0ff]" /> Directive Input
                        </h3>

                        <textarea
                            value={directive}
                            onChange={(e) => setDirective(e.target.value)}
                            disabled={status === 'INITIALIZING' || status === 'EXECUTING'}
                            placeholder="e.g. Go to LinkedIn, search 'VP Engineering Series A', and send contextual connection requests to the first 10 profiles."
                            className="w-full bg-black/50 border border-white/10 rounded-lg p-3 text-sm text-white font-mono placeholder-gray-600 focus:outline-none focus:border-[#00f0ff] focus:ring-1 focus:ring-[#00f0ff] resize-none h-32 mb-4"
                        />

                        <div className="flex gap-2">
                            {status === 'IDLE' || status === 'COMPLETED' || status === 'FAILED' ? (
                                <Button
                                    onClick={handleExecute}
                                    disabled={!directive.trim()}
                                    className="w-full bg-[#00f0ff]/20 hover:bg-[#00f0ff]/30 text-[#00f0ff] border border-[#00f0ff]/50 font-mono text-xs uppercase"
                                >
                                    <Play className="w-4 h-4 mr-2" /> Dispatch OpenClaw
                                </Button>
                            ) : (
                                <Button
                                    onClick={handleAbort}
                                    className="w-full bg-red-900/40 hover:bg-red-900/60 text-red-400 border border-red-500/50 font-mono text-xs uppercase"
                                >
                                    <Square className="w-4 h-4 mr-2" /> Kill Container
                                </Button>
                            )}
                        </div>
                    </div>

                    {/* Execution Logs */}
                    <div className="flex-1 min-h-[300px] bg-[#020202] border border-white/10 rounded-xl p-4 flex flex-col relative overflow-hidden">
                        <div className="absolute inset-0 bg-cyber-grid bg-[length:20px_20px] opacity-10 pointer-events-none" />

                        <h3 className="text-xs font-bold text-gray-500 uppercase tracking-widest font-mono mb-4 flex items-center gap-2 border-b border-white/5 pb-2 relative z-10">
                            <Zap className="w-4 h-4" /> Live Execution Stream
                        </h3>

                        <div className="flex-1 overflow-y-auto space-y-2 font-mono text-[10px] md:text-xs relative z-10" ref={scrollRef}>
                            {logs.map((log) => (
                                <div key={log.id} className="flex items-start gap-2 animate-fade-in-up">
                                    <span className="text-gray-600 shrink-0">[{log.timestamp}]</span>
                                    <span className={cn(
                                        "shrink-0 w-16 uppercase font-bold text-[9px]",
                                        log.action === 'ERROR' ? 'text-red-500' :
                                            log.action === 'SYSTEM' ? 'text-purple-500' :
                                                log.action === 'NAVIGATE' ? 'text-blue-500' :
                                                    log.action === 'EXTRACT' ? 'text-yellow-500' :
                                                        'text-emerald-500'
                                    )}>{log.action}</span>
                                    <span className={cn(
                                        "break-words",
                                        log.action === 'ERROR' ? 'text-red-400' : 'text-gray-300'
                                    )}>{log.details}</span>
                                </div>
                            ))}
                            {status === 'EXECUTING' && (
                                <div className="flex items-center gap-2 text-[#00f0ff] animate-pulse py-2">
                                    <Loader2 className="w-3 h-3 animate-spin" />
                                    <span>Executing next sequence...</span>
                                </div>
                            )}
                            {logs.length === 0 && status === 'IDLE' && (
                                <div className="text-gray-600 italic h-full flex items-center justify-center">Awaiting directive...</div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Right Column: Virtual Browser */}
                <div className="lg:col-span-2 bg-[#020202] border border-white/10 rounded-xl overflow-hidden flex flex-col shadow-2xl relative">

                    {/* Browser Chrome */}
                    <div className="h-12 bg-[#0a0a0f] border-b border-white/10 flex items-center px-4 gap-4 relative z-20">
                        <div className="flex gap-1.5 opacity-50">
                            <div className="w-3 h-3 rounded-full bg-red-500" />
                            <div className="w-3 h-3 rounded-full bg-yellow-500" />
                            <div className="w-3 h-3 rounded-full bg-green-500" />
                        </div>
                        <div className="flex-1 max-w-xl mx-auto bg-black/50 border border-white/5 rounded px-3 py-1.5 flex items-center gap-2">
                            <Globe className="w-3 h-3 text-gray-500" />
                            <span className="text-gray-400 font-mono text-xs truncate">{activeUrl}</span>
                        </div>
                        {status === 'EXECUTING' && (
                            <Badge variant="outline" className="border-red-500 text-red-500 text-[9px] animate-pulse">LIVE VIEW</Badge>
                        )}
                    </div>

                    {/* Viewport */}
                    <div className="flex-1 relative bg-[#0a0a0f] overflow-hidden">
                        {status === 'IDLE' || status === 'INITIALIZING' ? (
                            <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-6">
                                <div className={cn(
                                    "w-20 h-20 mb-6 rounded-full flex items-center justify-center border-2 border-dashed",
                                    status === 'INITIALIZING' ? 'border-[#00f0ff] animate-[spin_3s_linear_infinite]' : 'border-gray-800'
                                )}>
                                    <Globe className={cn("w-8 h-8", status === 'INITIALIZING' ? 'text-[#00f0ff] animate-pulse' : 'text-gray-700')} />
                                </div>
                                <h2 className="text-xl font-mono font-bold text-gray-400 uppercase tracking-widest mb-2">
                                    {status === 'INITIALIZING' ? 'Waking Container...' : 'Container Offline'}
                                </h2>
                                <p className="text-xs text-gray-600 font-mono max-w-sm">
                                    The virtual browser viewport will activate once a directive is dispatched.
                                </p>
                            </div>
                        ) : (
                            // Simulated Content Area
                            <div className="absolute inset-0 bg-white text-black p-8 shadow-[inset_0_0_50px_rgba(0,0,0,0.5)]">
                                {/* Fake LinkedIn Header */}
                                <div className="h-12 border-b border-gray-200 flex items-center px-4 mb-6">
                                    <div className="text-blue-700 font-black text-xl mr-8">in</div>
                                    <div className="bg-gray-100 rounded px-3 py-1 flex-1 text-sm text-gray-500">VP Engineering...</div>
                                </div>

                                {/* Fake Search Results */}
                                <div className="flex gap-6">
                                    <div className="w-64 hidden md:block space-y-4">
                                        <div className="h-4 bg-gray-200 rounded w-1/2" />
                                        <div className="h-4 bg-gray-200 rounded w-full" />
                                        <div className="h-4 bg-gray-200 rounded w-3/4" />
                                    </div>
                                    <div className="flex-1 space-y-6">
                                        <div className="h-6 bg-gray-200 rounded w-1/3 mb-6" />

                                        {[1, 2, 3].map(i => (
                                            <div key={i} className="flex gap-4 p-4 border border-gray-200 rounded-lg">
                                                <div className="w-16 h-16 rounded-full bg-gray-200" />
                                                <div className="flex-1">
                                                    <div className="h-5 bg-blue-100 rounded w-1/4 mb-2" />
                                                    <div className="h-4 bg-gray-100 rounded w-1/2 mb-4" />
                                                    <div className="flex gap-2">
                                                        <div className="h-8 bg-blue-600 rounded-full w-24" />
                                                        <div className="h-8 bg-white border border-gray-300 rounded-full w-24" />
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Virtual Mouse Cursor Overlay */}
                                <div
                                    className="absolute w-5 h-5 z-50 transition-all duration-1000 ease-in-out drop-shadow-lg"
                                    style={{
                                        left: `${cursorPos.x}%`,
                                        top: `${cursorPos.y}%`,
                                        transform: 'translate(-50%, -50%)'
                                    }}
                                >
                                    <MousePointer2 className="text-black fill-white w-6 h-6" />
                                    <div className="absolute top-6 left-6 bg-black/80 text-white text-[8px] font-mono px-1.5 py-0.5 rounded whitespace-nowrap">
                                        Agent_{status === 'EXECUTING' ? 'Active' : 'Halted'}
                                    </div>
                                </div>

                                {/* CRT Scanline Overlay */}
                                <div className="absolute inset-0 bg-transparent opacity-10 pointer-events-none mix-blend-overlay z-40" />
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
