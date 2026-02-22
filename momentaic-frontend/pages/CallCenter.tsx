import React, { useState, useEffect, useRef } from 'react';
import { PageMeta } from '../components/ui/PageMeta';
import { Phone, PhoneCall, PhoneIncoming, PhoneOff, Mic, Volume2, Users, Bot, Settings, Activity, Clock, Shield, Plus, Search, CheckCircle } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Input } from '../components/ui/Input';
import { useToast } from '../components/ui/Toast';
import { api } from '../lib/api';
import { useAuthStore } from '../stores/auth-store';
import { cn } from '../lib/utils';

interface ActiveCall {
    id: string;
    type: 'inbound' | 'outbound';
    agentName: string;
    customerPhone: string;
    duration: number;
    status: 'connected' | 'analyzing' | 'speaking' | 'completed';
    sentiment: 'positive' | 'neutral' | 'negative';
}

interface TranscriptLine {
    speaker: 'agent' | 'customer';
    text: string;
    time: string;
}

export default function CallCenter() {
    const { toast } = useToast();
    const [activeTab, setActiveTab] = useState<'live' | 'agents' | 'numbers'>('live');

    // Mock State for Live Demo
    const [calls, setCalls] = useState<ActiveCall[]>([
        { id: 'call-1', type: 'outbound', agentName: 'Alex (SDR)', customerPhone: '+1 (415) 555-0198', duration: 124, status: 'speaking', sentiment: 'positive' },
        { id: 'call-2', type: 'inbound', agentName: 'Sarah (Support)', customerPhone: '+44 20 7123 4567', duration: 45, status: 'analyzing', sentiment: 'neutral' }
    ]);
    const [selectedCall, setSelectedCall] = useState<string>('call-1');
    const [transcript, setTranscript] = useState<TranscriptLine[]>([
        { speaker: 'agent', text: 'Hi, this is Alex reaching out from MomentAIc. I noticed your team recently deployed a new Next.js app, and I was wondering how you are handling automated testing for those deployments?', time: '10:01 AM' },
        { speaker: 'customer', text: 'Yeah, hi. We are using Cypress but frankly it takes too long to write the tests. Why do you ask?', time: '10:01 AM' },
        { speaker: 'agent', text: 'That is exactly why I called. Our AI platform writes and maintains end-to-end tests automatically by just looking at your codebase. Would you have 5 minutes next Tuesday to see how we could cut your QA time in half?', time: '10:02 AM' }
    ]);

    const [isGeneratingCall, setIsGeneratingCall] = useState(false);
    const wsRef = useRef<WebSocket | null>(null);

    // Twilio Integration State
    const { user } = useAuthStore();
    const [provisionedNumbers, setProvisionedNumbers] = useState<any[]>([]);
    const [availableNumbers, setAvailableNumbers] = useState<any[]>([]);
    const [areaCode, setAreaCode] = useState('415');
    const [isSearching, setIsSearching] = useState(false);
    const VOICE_LANGUAGES = [
        { code: 'en-US', name: 'English (US)' },
        { code: 'es-ES', name: 'Spanish (ES)' },
        { code: 'ja-JP', name: 'Japanese (JP)' },
        { code: 'ko-KR', name: 'Korean (KR)' },
        { code: 'pt-BR', name: 'Portuguese (BR)' },
        { code: 'fr-FR', name: 'French (FR)' },
        { code: 'th-TH', name: 'Thai (TH)' },
        { code: 'id-ID', name: 'Indonesian (ID)' },
    ];
    const [selectedLang, setSelectedLang] = useState('en-US');
    const [isProvisioning, setIsProvisioning] = useState<string | null>(null);

    useEffect(() => {
        if (activeTab === 'numbers' && user?.active_startup_id) {
            loadNumbers();
        }
    }, [activeTab, user?.active_startup_id]);

    const loadNumbers = async () => {
        if (!user?.active_startup_id) return;
        try {
            const data = await api.getProvisionedNumbers(user.active_startup_id);
            setProvisionedNumbers(data);
        } catch (e) {
            console.error(e);
        }
    };

    const handleSearchNumbers = async () => {
        const sid = localStorage.getItem('twilio_sid');
        const token = localStorage.getItem('twilio_token');
        if (!sid || !token) {
            toast({ type: 'error', title: 'Missing Keys', message: 'Please add Twilio API keys in Settings.' });
            return;
        }

        setIsSearching(true);
        try {
            const data = await api.searchTelecomNumbers(sid, token, areaCode);
            setAvailableNumbers(data.numbers);
        } catch (e: any) {
            toast({ type: 'error', title: 'Search Failed', message: e.response?.data?.detail || 'Failed to search Twilio.' });
        } finally {
            setIsSearching(false);
        }
    };

    const handleProvision = async (phoneNumber: string) => {
        const sid = localStorage.getItem('twilio_sid');
        const token = localStorage.getItem('twilio_token');
        if (!sid || !token || !user?.active_startup_id) return;

        setIsProvisioning(phoneNumber);
        try {
            await api.provisionTelecomNumber(sid, token, phoneNumber, user.active_startup_id, selectedLang);
            toast({ type: 'success', title: 'Number Provisioned', message: `Successfully purchased ${phoneNumber} configured for ${selectedLang}` });
            setAvailableNumbers(prev => prev.filter(n => n.phone_number !== phoneNumber));
            loadNumbers();
        } catch (e: any) {
            toast({ type: 'error', title: 'Provisioning Failed', message: e.response?.data?.detail || 'Failed to buy number.' });
        } finally {
            setIsProvisioning(null);
        }
    };

    // Call duration timer effect
    useEffect(() => {
        const interval = setInterval(() => {
            setCalls(prev => prev.map(call =>
                call.status !== 'completed' ? { ...call, duration: call.duration + 1 } : call
            ));
        }, 1000);
        return () => clearInterval(interval);
    }, []);

    // WebSocket connection for live transcripts
    useEffect(() => {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const wsUrl = apiUrl.replace('http', 'ws') + '/api/v1/voice/webhooks/stream';

        try {
            const ws = new WebSocket(wsUrl);
            wsRef.current = ws;

            ws.onopen = () => {
                console.log('Connected to Voice Control Center');
                setInterval(() => {
                    if (ws.readyState === WebSocket.OPEN) ws.send('ping');
                }, 30000);
            };

            ws.onmessage = (event) => {
                try {
                    if (event.data === 'pong') return;
                    const data = JSON.parse(event.data);

                    if (data.type === 'transcript') {
                        setTranscript(prev => [...prev, {
                            speaker: data.role === 'bot' || data.role === 'agent' ? 'agent' : 'customer',
                            text: data.text,
                            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                        }]);
                    } else if (data.type === 'status') {
                        setCalls(prev => prev.map(c => c.id === data.call_id ? { ...c, status: data.status as any } : c));
                    }
                } catch (e) {
                    console.error("Failed to parse Voice WS message", e);
                }
            };

            return () => ws.close();
        } catch (error) {
            console.error("Failed to connect Voice WebSocket:", error);
        }
    }, []);

    const formatTime = (seconds: number) => {
        const m = Math.floor(seconds / 60);
        const s = seconds % 60;
        return `${m}:${s.toString().padStart(2, '0')}`;
    };

    const triggerMockCall = () => {
        setIsGeneratingCall(true);
        toast({ type: 'info', title: 'DISPATCHING SDR', message: 'Agent Alex is spinning up...' });

        setTimeout(() => {
            const newId = `call-${Date.now()}`;
            setCalls(prev => [...prev, {
                id: newId,
                type: 'outbound',
                agentName: 'Alex (SDR)',
                customerPhone: '+1 (650) 555-' + Math.floor(1000 + Math.random() * 9000),
                duration: 0,
                status: 'connected',
                sentiment: 'neutral'
            }]);
            setSelectedCall(newId);
            setTranscript([
                { speaker: 'agent', text: 'Ringing...', time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }
            ]);
            setIsGeneratingCall(false);
            toast({ type: 'success', title: 'CALL CONNECTED', message: 'Target answered. Agent is engaging.' });
        }, 2000);
    };

    return (
        <div className="max-w-7xl mx-auto pb-20 mt-8 min-h-screen flex flex-col">
            <PageMeta title="Synthetic Call Center | MomentAIc" description="Manage Voice/Video AI Agents and monitor live phone calls." />

            {/* Header */}
            <div className="mb-8 border-b border-white/10 pb-8">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-purple-500/30 bg-purple-500/10 text-purple-400 font-mono text-xs mb-4">
                    <Mic className="w-3 h-3 animate-pulse" /> SYNTHETIC_VOICE_ACTIVE
                </div>
                <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
                    <div>
                        <h1 className="text-4xl md:text-5xl font-black text-white mb-4 tracking-tighter uppercase">
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600 drop-shadow-[0_0_15px_rgba(168,85,247,0.5)]">
                                Call Center Protocol
                            </span>
                        </h1>
                        <p className="text-gray-400 font-mono text-sm max-w-2xl border-l-2 border-purple-500 pl-4">
                            Your agents don't just type. They speak. Provision numbers, deploy outbound sales dialers, and handle tier-1 support across 50+ languages simultaneously.
                        </p>
                    </div>
                    <div className="flex gap-2">
                        <Button
                            variant="cyber"
                            className="bg-purple-600 hover:bg-purple-500 border-none font-mono text-xs"
                            onClick={triggerMockCall}
                            disabled={isGeneratingCall}
                        >
                            <PhoneCall className="w-4 h-4 mr-2" />
                            {isGeneratingCall ? 'DIALING...' : 'INITIATE COLD CALL'}
                        </Button>
                    </div>
                </div>
            </div>

            {/* App Nav */}
            <div className="flex gap-4 mb-6 border-b border-white/10">
                {(['live', 'agents', 'numbers'] as const).map(tab => (
                    <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        className={cn(
                            "px-4 py-3 font-mono text-sm tracking-wider uppercase border-b-2 transition-colors",
                            activeTab === tab ? "border-purple-500 text-purple-400" : "border-transparent text-gray-500 hover:text-gray-300"
                        )}
                    >
                        {tab === 'live' ? 'Live Transcripts' : tab === 'agents' ? 'Voice Agents' : 'Phone Numbers'}
                    </button>
                ))}
            </div>

            {/* Main Content Area */}
            {activeTab === 'live' && (
                <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 relative">
                    {/* Background glow */}
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-purple-600/5 rounded-full blur-[120px] pointer-events-none" />

                    {/* Left Panel: Call Queue */}
                    <div className="lg:col-span-4 flex flex-col gap-4">
                        <div className="bg-[#0a0a0f] border border-white/10 rounded-xl p-4 flex flex-col gap-3">
                            <h3 className="text-xs font-bold text-gray-500 uppercase tracking-widest font-mono flex items-center gap-2">
                                <Activity className="w-4 h-4 text-purple-500" /> Active Connections ({calls.length})
                            </h3>

                            <div className="space-y-2">
                                {calls.map(call => (
                                    <div
                                        key={call.id}
                                        onClick={() => setSelectedCall(call.id)}
                                        className={cn(
                                            "p-3 rounded-lg border transition-all cursor-pointer group flex flex-col gap-2 relative overflow-hidden",
                                            selectedCall === call.id
                                                ? "border-purple-500 bg-purple-500/10 shadow-[0_0_15px_rgba(168,85,247,0.2)]"
                                                : "border-white/5 bg-white/5 hover:border-white/20"
                                        )}
                                    >
                                        {call.status === 'speaking' && (
                                            <div className="absolute top-0 right-0 w-16 h-full bg-gradient-to-l from-purple-500/10 to-transparent flex items-center justify-end pr-2 pointer-events-none">
                                                <Volume2 className="w-4 h-4 text-purple-400 animate-pulse" />
                                            </div>
                                        )}

                                        <div className="flex justify-between items-start">
                                            <div className="flex items-center gap-2">
                                                {call.type === 'inbound' ? <PhoneIncoming className="w-3 h-3 text-cyan-400" /> : <PhoneCall className="w-3 h-3 text-orange-400" />}
                                                <span className="font-mono text-sm font-bold text-white">{call.customerPhone}</span>
                                            </div>
                                            <span className="font-mono text-xs text-gray-400">{formatTime(call.duration)}</span>
                                        </div>

                                        <div className="flex justify-between items-center text-xs">
                                            <span className="text-gray-500 flex items-center gap-1">
                                                <Bot className="w-3 h-3" /> {call.agentName}
                                            </span>
                                            <Badge variant="outline" className={cn(
                                                "border-transparent font-mono text-[9px]",
                                                call.sentiment === 'positive' ? 'text-green-400 bg-green-400/10' :
                                                    call.sentiment === 'negative' ? 'text-red-400 bg-red-400/10' :
                                                        'text-gray-400 bg-gray-400/10'
                                            )}>
                                                {call.sentiment.toUpperCase()}
                                            </Badge>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Summary Stats */}
                        <div className="grid grid-cols-2 gap-4">
                            <div className="bg-[#0a0a0f] border border-white/10 p-4 rounded-xl">
                                <div className="text-gray-500 font-mono text-[10px] uppercase mb-1">Today's Cost</div>
                                <div className="text-xl font-bold text-white">$14.82</div>
                                <div className="text-emerald-500 text-[10px] font-mono">142 minutes billed</div>
                            </div>
                            <div className="bg-[#0a0a0f] border border-white/10 p-4 rounded-xl">
                                <div className="text-gray-500 font-mono text-[10px] uppercase mb-1">Conversion Rate</div>
                                <div className="text-xl font-bold text-white">12.4%</div>
                                <div className="text-emerald-500 text-[10px] font-mono">+2.1% outperforming human</div>
                            </div>
                        </div>
                    </div>

                    {/* Right Panel: Active Call Focus */}
                    <div className="lg:col-span-8 bg-[#020202] border border-white/10 rounded-xl overflow-hidden flex flex-col shadow-2xl relative">
                        {/* Audio Waveform Visualization Header */}
                        <div className="bg-[#0a0a0f] border-b border-white/10 p-6 relative overflow-hidden">
                            <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-5" />
                            <div className="relative z-10 flex justify-between items-center">
                                <div>
                                    <div className="flex items-center gap-3 mb-1">
                                        <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                                        <h2 className="text-lg font-mono font-bold text-white tracking-widest">
                                            {calls.find(c => c.id === selectedCall)?.customerPhone || 'NO CALL SELECTED'}
                                        </h2>
                                    </div>
                                    <p className="text-xs font-mono text-purple-400">
                                        Agent: {calls.find(c => c.id === selectedCall)?.agentName}
                                    </p>
                                </div>
                                <div className="flex items-center gap-6">
                                    <div className="flex flex-col items-end">
                                        <span className="text-[10px] text-gray-500 font-mono uppercase">Call Duration</span>
                                        <span className="text-xl font-mono text-white">
                                            {formatTime(calls.find(c => c.id === selectedCall)?.duration || 0)}
                                        </span>
                                    </div>
                                    <Button variant="outline" size="sm" className="border-red-500/50 text-red-500 hover:bg-red-500/10 p-2 h-auto" onClick={() => {
                                        setCalls(prev => prev.filter(c => c.id !== selectedCall));
                                        if (calls.length > 1) setSelectedCall(calls.find(c => c.id !== selectedCall)!.id);
                                    }}>
                                        <PhoneOff className="w-5 h-5" />
                                    </Button>
                                </div>
                            </div>
                        </div>

                        {/* Live Transcription */}
                        <div className="flex-1 overflow-y-auto p-6 space-y-6">
                            {transcript.map((line, i) => (
                                <div key={i} className={cn(
                                    "flex flex-col max-w-[80%]",
                                    line.speaker === 'agent' ? "mr-auto" : "ml-auto items-end"
                                )}>
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className="text-[10px] text-gray-500 font-mono">{line.time}</span>
                                        <span className={cn(
                                            "text-xs font-bold uppercase",
                                            line.speaker === 'agent' ? "text-purple-400" : "text-cyan-400"
                                        )}>
                                            {line.speaker === 'agent' ? 'AI Agent' : 'Customer'}
                                        </span>
                                    </div>
                                    <div className={cn(
                                        "p-3 rounded-xl text-sm leading-relaxed",
                                        line.speaker === 'agent'
                                            ? "bg-purple-900/20 border border-purple-500/20 text-gray-200 rounded-tl-none"
                                            : "bg-cyan-900/10 border border-cyan-500/20 text-gray-300 rounded-tr-none"
                                    )}>
                                        {line.text}
                                    </div>
                                </div>
                            ))}
                            <div className="flex items-center gap-2 text-purple-500/50 animate-pulse">
                                <Bot className="w-4 h-4" /> <span className="text-xs font-mono">Agent analyzing audio stream...</span>
                            </div>
                        </div>

                        {/* Injection Terminal */}
                        <div className="p-4 bg-black/40 border-t border-white/10 flex gap-2">
                            <Input
                                placeholder="Whisper an instruction to the AI agent mid-call (e.g. 'Offer a 20% discount')..."
                                className="bg-white/5 border-white/10 text-white font-mono text-sm placeholder:text-gray-600 focus:bg-white/10"
                            />
                            <Button variant="cyber" className="bg-purple-600 hover:bg-purple-500 border-none shrink-0">
                                INJECT DIRECTIVE
                            </Button>
                        </div>
                    </div>
                </div>
            )}

            {activeTab === 'agents' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="bg-[#0a0a0f] border border-white/10 rounded-xl p-6">
                        <div className="flex justify-between items-start mb-6">
                            <div className="flex items-center gap-3">
                                <div className="w-12 h-12 rounded-lg bg-orange-500/20 flex items-center justify-center border border-orange-500/30">
                                    <PhoneCall className="w-6 h-6 text-orange-400" />
                                </div>
                                <div>
                                    <h3 className="text-white font-bold text-lg">Alex (SDR Outbound)</h3>
                                    <p className="text-xs text-gray-400 font-mono">Voice ID: ElevenLabs "Daniel"</p>
                                </div>
                            </div>
                            <Badge className="bg-green-500/10 text-green-400 border-none">ACTIVE</Badge>
                        </div>
                        <div className="space-y-4 font-mono text-sm border-t border-white/10 pt-4">
                            <div className="flex justify-between"><span className="text-gray-500">Latency:</span><span className="text-white">650ms</span></div>
                            <div className="flex justify-between"><span className="text-gray-500">Goal:</span><span className="text-white">Book Calendar Meeting</span></div>
                            <div className="flex justify-between"><span className="text-gray-500">Language:</span><span className="text-white">English (US)</span></div>
                        </div>
                        <div className="mt-6 flex gap-2">
                            <Button variant="outline" className="flex-1"><Settings className="w-4 h-4 mr-2" /> Configure</Button>
                            <Button variant="outline" className="flex-1 text-red-400 hover:text-red-300"><PhoneOff className="w-4 h-4 mr-2" /> Stop Dialing</Button>
                        </div>
                    </div>
                </div>
            )}

            {/* PHONE NUMBERS TAB */}
            {activeTab === 'numbers' && (
                <div className="space-y-6">
                    <div className="bg-[#0a0a0f] border border-white/10 rounded-xl p-6">
                        <div className="flex items-center justify-between mb-6">
                            <div>
                                <h2 className="text-xl font-bold text-white mb-2 tracking-widest uppercase font-mono">Provisioned Telecom Lines</h2>
                                <p className="text-sm text-gray-500 font-mono">These Twilio numbers are actively routed to your AI voice agents.</p>
                            </div>
                        </div>

                        {provisionedNumbers.length === 0 ? (
                            <div className="text-center py-12 border-2 border-dashed border-white/10 rounded-xl bg-white/5">
                                <PhoneCall className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                                <h3 className="text-lg font-bold text-gray-400 mb-2 font-mono">No Active Numbers</h3>
                                <p className="text-sm text-gray-500 font-mono max-w-sm mx-auto">
                                    You have not provisioned any Twilio numbers yet. Search and buy a number below to start receiving inbound AI calls.
                                </p>
                            </div>
                        ) : (
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                {provisionedNumbers.map(num => (
                                    <div key={num.id} className="bg-[#020202] border border-purple-500/30 p-4 rounded-xl relative overflow-hidden group">
                                        <div className="absolute top-0 right-0 p-3 opacity-0 group-hover:opacity-100 transition-opacity">
                                            <Button variant="outline" size="sm" className="h-8 text-[10px] text-gray-400 border-white/10 hover:border-white/30">RELEASE</Button>
                                        </div>
                                        <div className="flex items-center gap-3 mb-4">
                                            <div className="p-2 bg-purple-500/20 rounded-lg">
                                                <Phone className="w-5 h-5 text-purple-400" />
                                            </div>
                                            <div>
                                                <div className="text-lg font-bold font-mono text-white">{num.phone_number}</div>
                                                <div className="text-[10px] text-gray-500 font-mono uppercase">Status: <span className="text-green-400">ACTIVE</span></div>
                                            </div>
                                        </div>
                                        <div className="flex items-center justify-between text-xs border-t border-white/10 pt-3 mt-2">
                                            <span className="text-gray-500 font-mono">Assigned To:</span>
                                            <Badge className="bg-white/5 text-gray-300 font-mono border-white/10 hover:bg-white/10 cursor-pointer">Unassigned (Click to Map)</Badge>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    <div className="bg-[#0a0a0f] border border-white/10 rounded-xl p-6">
                        <h2 className="text-xl font-bold text-white mb-6 tracking-widest uppercase font-mono flex items-center gap-2">
                            <Search className="w-5 h-5 text-cyan-400" /> Acquire New Numbers
                        </h2>

                        <div className="flex gap-4 mb-8 items-end">
                            <div className="flex-1 max-w-xs">
                                <label className="text-[10px] text-gray-500 font-mono uppercase mb-1 block">Target Area Code</label>
                                <Input
                                    placeholder="Area Code (e.g. 415)"
                                    value={areaCode}
                                    onChange={(e) => setAreaCode(e.target.value)}
                                    className="font-mono bg-black/40 border-white/10 text-white focus:bg-white/5"
                                />
                            </div>
                            <div className="flex-1 max-w-xs">
                                <label className="text-[10px] text-purple-400 font-mono uppercase mb-1 block flex items-center gap-1">Native Model Language</label>
                                <select
                                    className="w-full h-10 rounded-md border border-purple-500/30 bg-purple-900/10 px-3 py-2 text-sm text-purple-300 font-mono focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                                    value={selectedLang}
                                    onChange={(e) => setSelectedLang(e.target.value)}
                                >
                                    {VOICE_LANGUAGES.map(lang => (
                                        <option key={lang.code} value={lang.code} className="bg-[#0a0a0f] text-white">
                                            {lang.name} [{lang.code}]
                                        </option>
                                    ))}
                                </select>
                            </div>
                            <Button
                                onClick={handleSearchNumbers}
                                disabled={isSearching || !areaCode}
                                className="bg-cyan-600 hover:bg-cyan-500 font-mono"
                            >
                                {isSearching ? 'SEARCHING...' : 'SEARCH TWILIO inventory'}
                            </Button>
                        </div>

                        {availableNumbers.length > 0 && (
                            <div className="space-y-3">
                                <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest font-mono mb-4">Available Numbers</h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {availableNumbers.map(num => (
                                        <div key={num.phone_number} className="flex items-center justify-between p-4 bg-black/40 border border-white/10 rounded-lg hover:border-cyan-500/30 transition-colors">
                                            <div className="flex items-center gap-3">
                                                <Phone className="w-4 h-4 text-gray-500" />
                                                <span className="font-mono text-lg text-gray-200">{num.friendly_name}</span>
                                            </div>
                                            <Button
                                                disabled={isProvisioning === num.phone_number}
                                                onClick={() => handleProvision(num.phone_number)}
                                                className="bg-purple-600/20 text-purple-400 border border-purple-500/30 hover:bg-purple-600/40 text-xs font-mono"
                                            >
                                                {isProvisioning === num.phone_number ? 'PROVISIONING...' : '$1.15/mo - PROVISION'}
                                            </Button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
