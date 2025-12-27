
import React, { useState, useEffect } from 'react';
import { api } from '../lib/api';
import { Lead, LeadStatus, Startup } from '../types';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Dialog } from '../components/ui/Dialog';
import { useAuthStore } from '../stores/auth-store';
import { useToast } from '../components/ui/Toast';
import {
    BarChart2, Users, Mail, ArrowRight, Sparkles, Send,
    Copy, RefreshCw, PenTool, Share2, DollarSign, Calendar,
    Zap, Power, Activity
} from 'lucide-react';
import { cn, formatCurrency } from '../lib/utils';
import { Textarea } from '../components/ui/Textarea';

const AI_COST = 5;

// === CRM KANBAN COMPONENT ===

const STATUS_COLS: { id: LeadStatus; label: string; color: string }[] = [
    { id: 'new', label: 'Cold Leads', color: 'border-blue-500/50' },
    { id: 'outreach', label: 'Contacted', color: 'border-yellow-500/50' },
    { id: 'negotiation', label: 'Negotiation', color: 'border-purple-500/50' },
    { id: 'closed_won', label: 'Closed Won', color: 'border-green-500/50' },
];

function CRMBoard({ startupId, autopilot }: { startupId: string, autopilot: boolean }) {
    const [leads, setLeads] = useState<Lead[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
    const [aiAnalysis, setAiAnalysis] = useState('');
    const [generating, setGenerating] = useState(false);
    const { deductCredits } = useAuthStore();
    const { toast } = useToast();

    const loadLeads = async () => {
        try {
            const data = await api.getLeads(startupId);
            setLeads(data);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { loadLeads(); }, [startupId]);

    // Autopilot Simulation Effect
    useEffect(() => {
        if (!autopilot) return;

        const interval = setInterval(() => {
            // Randomly simulate an agent working on a lead
            if (leads.length > 0 && Math.random() > 0.7) {
                const randomLead = leads[Math.floor(Math.random() * leads.length)];
                toast({
                    type: 'info',
                    title: 'Sales Agent Active',
                    message: `Analyzing buying signals for ${randomLead.company_name}...`
                });
            }
        }, 8000);
        return () => clearInterval(interval);
    }, [autopilot, leads]);

    const moveLead = async (id: string, newStatus: LeadStatus) => {
        // Optimistic update
        setLeads(prev => prev.map(l => l.id === id ? { ...l, status: newStatus } : l));
        await api.updateLead(id, { status: newStatus });
    };

    const generateOutreach = async () => {
        if (!selectedLead) return;
        if (!deductCredits(AI_COST)) {
            toast({ type: 'error', title: 'Insufficient Credits', message: 'Recharge credits to use AI Outreach.' });
            return;
        }

        setGenerating(true);
        try {
            // SECURITY: AI generation handled by backend API
            // Frontend uses demo response for UI demonstration
            await new Promise(r => setTimeout(r, 2000));
            setAiAnalysis(`Subject: Scaling ${selectedLead.company_name} with AI\n\nHi ${selectedLead.contact_person},\n\nI noticed ${selectedLead.company_name} is expanding rapidly. Our AI OS can automate your entire backend workflow, saving 40+ hours/week.\n\nOpen to a 10-min demo?\n\nBest,\nFounder`);
        } catch (e) {
            setAiAnalysis("Error generating outreach. Please try again.");
        } finally {
            setGenerating(false);
        }
    };

    if (loading) return <div className="text-center p-10 text-[#00f0ff] font-mono">LOADING_PIPELINE_DATA...</div>;

    return (
        <div className="h-full overflow-x-auto pb-4">
            <div className="flex gap-4 min-w-[1000px]">
                {STATUS_COLS.map(col => (
                    <div key={col.id} className="flex-1 min-w-[240px]">
                        <div className={`flex justify-between items-center mb-3 pb-2 border-b-2 ${col.color}`}>
                            <h3 className="font-mono font-bold text-xs uppercase text-gray-400 tracking-widest">{col.label}</h3>
                            <span className="text-xs font-mono text-gray-600">{leads.filter(l => l.status === col.id).length}</span>
                        </div>

                        <div className="space-y-3">
                            {leads.filter(l => l.status === col.id).map(lead => (
                                <div
                                    key={lead.id}
                                    onClick={() => setSelectedLead(lead)}
                                    className="bg-[#0a0a0a] border border-white/10 p-4 rounded-lg hover:border-white/30 cursor-pointer group transition-all relative overflow-hidden"
                                >
                                    {autopilot && Math.random() > 0.8 && (
                                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-[#00f0ff]/5 to-transparent animate-shimmer pointer-events-none"></div>
                                    )}

                                    <div className="flex justify-between items-start mb-2 relative z-10">
                                        <div className="font-bold text-white text-sm">{lead.company_name}</div>
                                        <div className="text-[10px] font-mono text-green-500">{formatCurrency(lead.value)}</div>
                                    </div>
                                    <div className="text-xs text-gray-500 mb-3 relative z-10">{lead.contact_person}</div>

                                    <div className="flex justify-between items-center opacity-0 group-hover:opacity-100 transition-opacity relative z-10">
                                        <Button size="sm" variant="ghost" className="h-6 text-[10px] px-2 text-[#00f0ff]" onClick={(e) => { e.stopPropagation(); setSelectedLead(lead); }}>
                                            <Sparkles className="w-3 h-3 mr-1" /> AI INTEL
                                        </Button>
                                        {lead.status !== 'closed_won' && (
                                            <Button size="sm" variant="outline" className="h-6 text-[10px] px-2" onClick={(e) => {
                                                e.stopPropagation();
                                                const nextIdx = STATUS_COLS.findIndex(c => c.id === lead.status) + 1;
                                                if (nextIdx < STATUS_COLS.length) moveLead(lead.id, STATUS_COLS[nextIdx].id);
                                            }}>
                                                <ArrowRight className="w-3 h-3" />
                                            </Button>
                                        )}
                                    </div>
                                </div>
                            ))}
                            <Button variant="outline" className="w-full border-dashed border-white/10 text-gray-600 hover:border-white/20 hover:text-white">
                                + Add Lead
                            </Button>
                        </div>
                    </div>
                ))}
            </div>

            {/* Lead Detail Dialog */}
            <Dialog isOpen={!!selectedLead} onClose={() => { setSelectedLead(null); setAiAnalysis(''); }} title="Lead Command">
                {selectedLead && (
                    <div className="space-y-6">
                        <div className="flex justify-between items-start bg-black p-4 rounded-lg border border-white/10">
                            <div>
                                <div className="text-2xl font-bold text-white">{selectedLead.company_name}</div>
                                <div className="text-sm text-gray-400">{selectedLead.contact_person} &lt;{selectedLead.email}&gt;</div>
                            </div>
                            <div className="text-right">
                                <div className="text-xl font-mono text-green-500">{formatCurrency(selectedLead.value)}</div>
                                <div className="text-xs text-gray-500 uppercase tracking-widest">{selectedLead.status.replace('_', ' ')}</div>
                            </div>
                        </div>

                        {/* AI Action Area */}
                        <div className="bg-[#0a0a0a] border border-white/10 rounded-lg p-4">
                            <div className="flex items-center gap-2 mb-3 text-[#00f0ff] font-bold text-xs uppercase tracking-widest">
                                <Sparkles className="w-4 h-4" /> Neural Agent Outreach
                            </div>

                            {!aiAnalysis ? (
                                <div className="text-center py-6">
                                    <p className="text-gray-500 text-xs mb-4">Generate hyper-personalized outreach emails using signal data.</p>
                                    <Button variant="cyber" onClick={generateOutreach} isLoading={generating}>
                                        GENERATE DRAFT ({AI_COST} CREDITS)
                                    </Button>
                                </div>
                            ) : (
                                <div className="space-y-3">
                                    <div className="bg-[#111] p-4 rounded border border-white/5 text-gray-300 text-sm whitespace-pre-wrap font-mono">
                                        {aiAnalysis}
                                    </div>
                                    <div className="flex justify-end gap-2">
                                        <Button variant="outline" size="sm" onClick={() => navigator.clipboard.writeText(aiAnalysis)}>
                                            <Copy className="w-3 h-3 mr-2" /> Copy
                                        </Button>
                                        <Button variant="secondary" size="sm" onClick={generateOutreach}>
                                            <RefreshCw className="w-3 h-3 mr-2" /> Regenerate
                                        </Button>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </Dialog>
        </div>
    );
}

// === CONTENT MATRIX COMPONENT ===

function ContentMatrix({ startup, autopilot }: { startup: Startup, autopilot: boolean }) {
    const [topic, setTopic] = useState('');
    const [platform, setPlatform] = useState('LinkedIn');
    const [content, setContent] = useState('');
    const [generating, setGenerating] = useState(false);
    const { deductCredits } = useAuthStore();
    const { toast } = useToast();

    // Autopilot Content Simulation
    useEffect(() => {
        if (!autopilot) return;
        const interval = setInterval(() => {
            if (Math.random() > 0.8) {
                toast({
                    type: 'info',
                    title: 'Content Agent',
                    message: `Drafted viral thread for ${startup.industry} trends.`
                });
            }
        }, 12000);
        return () => clearInterval(interval);
    }, [autopilot, startup]);

    const handleGenerate = async () => {
        if (!topic) return;
        if (!deductCredits(AI_COST)) {
            toast({ type: 'error', title: 'Insufficient Credits', message: 'Recharge needed.' });
            return;
        }

        setGenerating(true);
        try {
            // SECURITY: AI generation handled by backend API
            // Frontend uses demo response for UI demonstration
            await new Promise(r => setTimeout(r, 2000));
            setContent(`🚀 The Future of ${startup.industry} is Here\n\nEveryone is talking about efficiency, but few are solving the root cause.\n\nAt ${startup.name}, we're taking a different approach.\n\n#${startup.industry.replace(' ', '')} #Innovation #Tech`);
        } catch (e) {
            setContent("Failed to connect to Neural Engine.");
        } finally {
            setGenerating(false);
        }
    };

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 h-full">
            <div className="space-y-6">
                <div className="bg-[#0a0a0a] border border-white/10 p-6 rounded-xl">
                    <h3 className="text-white font-bold mb-4 flex items-center gap-2">
                        <PenTool className="w-4 h-4 text-purple-500" /> Content Parameters
                    </h3>
                    <div className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-xs text-gray-500 font-bold uppercase">Platform</label>
                            <div className="flex gap-2">
                                {['LinkedIn', 'Twitter/X', 'Blog', 'Email'].map(p => (
                                    <button
                                        key={p}
                                        onClick={() => setPlatform(p)}
                                        className={cn(
                                            "px-3 py-1.5 rounded text-xs border transition-colors",
                                            platform === p ? "bg-white text-black border-white" : "bg-black text-gray-400 border-white/20 hover:border-white/50"
                                        )}
                                    >
                                        {p}
                                    </button>
                                ))}
                            </div>
                        </div>
                        <div className="space-y-2">
                            <label className="text-xs text-gray-500 font-bold uppercase">Topic / Angle</label>
                            <Textarea
                                placeholder="e.g. How AI is changing logistics..."
                                value={topic}
                                onChange={e => setTopic(e.target.value)}
                                className="h-32 bg-black border-white/20"
                            />
                        </div>
                        <Button className="w-full" variant="cyber" onClick={handleGenerate} isLoading={generating} disabled={!topic}>
                            NEURAL GENERATE ({AI_COST} CREDITS)
                        </Button>
                    </div>
                </div>
            </div>

            <div className="bg-[#0a0a0a] border border-white/10 p-6 rounded-xl flex flex-col h-full relative overflow-hidden">
                {autopilot && <div className="absolute inset-0 bg-cyber-grid opacity-10 pointer-events-none animate-grid-flow"></div>}

                <h3 className="text-white font-bold mb-4 flex items-center gap-2 justify-between relative z-10">
                    <span className="flex items-center gap-2"><Sparkles className="w-4 h-4 text-[#00f0ff]" /> Output</span>
                    {content && (
                        <Button size="sm" variant="ghost" className="h-6 px-2 text-gray-400 hover:text-white" onClick={() => navigator.clipboard.writeText(content)}>
                            <Copy className="w-3 h-3" />
                        </Button>
                    )}
                </h3>
                <div className="flex-1 bg-[#111] rounded border border-white/5 p-4 text-gray-300 font-mono text-sm whitespace-pre-wrap overflow-y-auto relative z-10">
                    {content ? content : <span className="text-gray-600 italic">Waiting for input parameters...</span>}
                </div>
            </div>
        </div>
    );
}

// === MAIN PAGE ===

export default function GrowthEngine() {
    const [startups, setStartups] = useState<Startup[]>([]);
    const [selectedStartupId, setSelectedStartupId] = useState<string>('');
    const [activeTab, setActiveTab] = useState<'crm' | 'content'>('crm');
    const [autopilot, setAutopilot] = useState(false);

    useEffect(() => {
        api.getStartups().then(data => {
            setStartups(data);
            if (data.length > 0) setSelectedStartupId(data[0].id);
        });
    }, []);

    const selectedStartup = startups.find(s => s.id === selectedStartupId);

    return (
        <div className="h-[calc(100vh-6rem)] flex flex-col">
            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between items-end mb-6 border-b border-white/10 pb-6 gap-4">
                <div>
                    <h1 className="text-3xl font-black text-white tracking-tighter mb-2 flex items-center gap-3">
                        GROWTH_ENGINE <span className="px-2 py-0.5 rounded text-[10px] bg-[#00f0ff]/10 text-[#00f0ff] border border-[#00f0ff]/20">BETA</span>
                    </h1>
                    <p className="text-gray-500 font-mono text-xs">AUTOMATED REVENUE PROTOCOL</p>
                </div>

                <div className="flex flex-wrap items-center gap-4">
                    {/* Autopilot Toggle */}
                    <Button
                        onClick={() => setAutopilot(!autopilot)}
                        className={cn(
                            "h-9 px-4 text-xs font-mono font-bold tracking-wider transition-all duration-500",
                            autopilot
                                ? "bg-[#00f0ff]/10 text-[#00f0ff] border border-[#00f0ff] shadow-[0_0_20px_rgba(0,240,255,0.4)]"
                                : "bg-black text-gray-500 border border-white/10 hover:border-white/30"
                        )}
                    >
                        <Zap className={cn("w-3 h-3 mr-2", autopilot ? "fill-current" : "")} />
                        AUTOPILOT: {autopilot ? 'ON' : 'OFF'}
                    </Button>

                    <div className="w-px h-8 bg-white/10 mx-2 hidden md:block"></div>

                    <select
                        className="bg-black border border-white/20 text-white text-sm rounded px-3 py-2 focus:border-[#00f0ff] focus:outline-none"
                        value={selectedStartupId}
                        onChange={e => setSelectedStartupId(e.target.value)}
                    >
                        {startups.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                    </select>

                    <div className="flex bg-[#111] p-1 rounded-lg border border-white/10">
                        <button
                            onClick={() => setActiveTab('crm')}
                            className={cn("px-4 py-1.5 rounded text-xs font-bold uppercase transition-all", activeTab === 'crm' ? "bg-white text-black shadow-lg" : "text-gray-500 hover:text-white")}
                        >
                            Pipeline
                        </button>
                        <button
                            onClick={() => setActiveTab('content')}
                            className={cn("px-4 py-1.5 rounded text-xs font-bold uppercase transition-all", activeTab === 'content' ? "bg-white text-black shadow-lg" : "text-gray-500 hover:text-white")}
                        >
                            Content Studio
                        </button>
                    </div>
                </div>
            </div>

            {/* Main Content Area */}
            <div className="flex-1 overflow-hidden relative">
                {autopilot && (
                    <div className="absolute top-0 right-0 p-4 z-50">
                        <div className="flex items-center gap-2 px-3 py-1 bg-[#00f0ff]/10 border border-[#00f0ff]/30 rounded-full">
                            <Activity className="w-3 h-3 text-[#00f0ff] animate-pulse" />
                            <span className="text-[10px] text-[#00f0ff] font-mono font-bold">AGENTS ACTIVE</span>
                        </div>
                    </div>
                )}

                {selectedStartup ? (
                    activeTab === 'crm' ? (
                        <CRMBoard startupId={selectedStartup.id} autopilot={autopilot} />
                    ) : (
                        <ContentMatrix startup={selectedStartup} autopilot={autopilot} />
                    )
                ) : (
                    <div className="text-center p-20 text-gray-500">Initialize a startup to access Growth Engine.</div>
                )}
            </div>
        </div>
    );
}
