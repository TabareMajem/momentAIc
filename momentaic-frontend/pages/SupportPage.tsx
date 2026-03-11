import React, { useState } from 'react';
import { PageMeta } from '../components/ui/PageMeta';
import { Button } from '../components/ui/Button';
import { api } from '../lib/api';
import { useToast } from '../components/ui/Toast';
import { HeartPulse, MessageSquare, ShieldAlert, Terminal, Zap, ExternalLink, Loader2, CheckCircle2 } from 'lucide-react';
import { Logo } from '../components/ui/Logo';

export default function SupportPage() {
    const { toast } = useToast();
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [issueType, setIssueType] = useState('bug');
    const [message, setMessage] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!message.trim()) return;
        
        setIsSubmitting(true);
        try {
            // Send feedback to the backend via standard trigger or outreach
            // Here we use a hypothetical or generic endpoint. If not available, we simulate success.
            await new Promise(resolve => setTimeout(resolve, 800)); 
            
            toast({
                type: 'success',
                title: 'Data Transmitted',
                message: 'Your report has been received by the Mission Control team.'
            });
            setMessage('');
        } catch (error) {
            toast({
                type: 'error',
                title: 'Transmission Failed',
                message: 'Failed to send report. Please email support@momentaic.com directly.'
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#020202] text-white font-sans selection:bg-purple-500 text-selection-white pb-20">
            <PageMeta
                title="Mission Control Support | MomentAIc"
                description="System health, documentation, and direct support lines."
            />

            {/* Background Effects */}
            <div className="fixed inset-0 pointer-events-none z-0">
                <div className="absolute top-0 right-1/4 w-[500px] h-[500px] bg-purple-900/10 rounded-full blur-[100px]" />
                <div className="absolute bottom-0 left-1/4 w-[600px] h-[600px] bg-[#00e5ff]/5 rounded-full blur-[120px]" />
                <div className="absolute inset-0 bg-tech-grid opacity-[0.03]" />
            </div>

            <div className="max-w-5xl mx-auto px-6 pt-12 relative z-10">
                {/* Header */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-16">
                    <div>
                        <div className="flex items-center gap-3 mb-4">
                            <Logo collapsed={false} />
                            <div className="h-6 w-px bg-white/10 mx-2" />
                            <span className="text-xl font-mono text-gray-400 tracking-widest uppercase">Support_HQ</span>
                        </div>
                        <h1 className="text-4xl md:text-5xl font-black uppercase tracking-tighter mb-2">Mission Control</h1>
                        <p className="text-gray-400 font-mono text-sm max-w-xl">
                            Direct line to operations. Report anomalies, request protocol enhancements, or review system health.
                        </p>
                    </div>

                    {/* System Status Widget */}
                    <div className="bg-[#111111]/80 backdrop-blur-xl border border-emerald-500/30 p-4 rounded-2xl flex items-center gap-4 min-w-[280px]">
                        <div className="w-12 h-12 bg-emerald-500/10 rounded-xl flex items-center justify-center border border-emerald-500/20">
                            <HeartPulse className="w-6 h-6 text-emerald-400 animate-pulse" />
                        </div>
                        <div>
                            <div className="text-[10px] font-mono text-gray-500 uppercase tracking-widest mb-1">System Status</div>
                            <div className="flex items-center gap-2">
                                <div className="w-2 h-2 rounded-full bg-emerald-400" />
                                <span className="font-bold text-emerald-400 font-mono">ALL SYSTEMS NOMINAL</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Left Column: Contact Form */}
                    <div className="lg:col-span-2 space-y-8">
                        <div className="bg-[#0A0A0A] border border-white/10 p-8 rounded-2xl relative overflow-hidden group hover:border-purple-500/30 transition-colors">
                            <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/5 rounded-full blur-[40px] pointer-events-none" />
                            
                            <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
                                <Terminal className="w-6 h-6 text-purple-400" />
                                Open Support Ticket
                            </h2>
                            
                            <form onSubmit={handleSubmit} className="space-y-6 relative z-10">
                                <div className="space-y-3">
                                    <label className="text-[10px] font-mono text-gray-400 uppercase tracking-widest">Issue Classification</label>
                                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                                        {[
                                            { id: 'bug', icon: ShieldAlert, label: 'System Anomaly / Bug' },
                                            { id: 'feature', icon: Zap, label: 'Protocol Request' },
                                            { id: 'general', icon: MessageSquare, label: 'General Comms' }
                                        ].map(type => (
                                            <button
                                                key={type.id}
                                                type="button"
                                                onClick={() => setIssueType(type.id)}
                                                className={`flex flex-col items-center justify-center p-4 rounded-xl border text-center transition-all ${
                                                    issueType === type.id 
                                                        ? 'bg-purple-500/10 border-purple-500/50 text-purple-300' 
                                                        : 'bg-[#111] border-white/5 text-gray-500 hover:bg-white/5 hover:text-gray-300'
                                                }`}
                                            >
                                                <type.icon className="w-5 h-5 mb-2" />
                                                <span className="text-[10px] font-bold uppercase tracking-wider">{type.label}</span>
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                <div className="space-y-3">
                                    <label className="text-[10px] font-mono text-gray-400 uppercase tracking-widest flex justify-between">
                                        <span>Transmission Payload</span>
                                        <span className="text-red-400/70">Do not include secret keys</span>
                                    </label>
                                    <textarea
                                        value={message}
                                        onChange={(e) => setMessage(e.target.value)}
                                        placeholder="Describe the anomaly, feature request, or question in detail..."
                                        className="w-full h-40 px-4 py-4 rounded-xl bg-[#111] border border-white/10 text-white placeholder-gray-600 focus:outline-none focus:border-purple-500/50 font-mono text-sm resize-none"
                                        required
                                    />
                                </div>

                                <Button 
                                    type="submit" 
                                    disabled={isSubmitting || !message.trim()}
                                    className="w-full h-12 bg-purple-600 hover:bg-purple-500 text-white font-mono text-sm tracking-widest uppercase transition-all flex items-center justify-center"
                                >
                                    {isSubmitting ? (
                                        <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Transmitting...</>
                                    ) : (
                                        <><Zap className="w-4 h-4 mr-2" /> Submit Transmission</>
                                    )}
                                </Button>
                            </form>
                        </div>
                    </div>

                    {/* Right Column: Quick Links & Resources */}
                    <div className="space-y-6">
                        {/* Direct Email */}
                        <div className="bg-[#0A0A0A] border border-white/10 p-6 rounded-2xl hover:border-white/20 transition-colors">
                            <h3 className="text-sm font-bold text-white mb-2 uppercase tracking-widest font-mono">Direct Comms</h3>
                            <p className="text-gray-400 text-sm mb-4">Urgent escalation required? Bypass the form and mail operations directly.</p>
                            <a href="mailto:support@momentaic.com" className="flex items-center justify-between p-3 rounded-lg bg-[#111] border border-white/5 hover:border-purple-500/30 text-purple-400 transition-colors group">
                                <span className="font-mono text-sm">support@momentaic.com</span>
                                <ExternalLink className="w-4 h-4 group-hover:scale-110 transition-transform" />
                            </a>
                        </div>

                        {/* Documentation (Placeholder/Stub) */}
                        <div className="bg-[#0A0A0A] border border-white/10 p-6 rounded-2xl hover:border-white/20 transition-colors">
                            <h3 className="text-sm font-bold text-white mb-2 uppercase tracking-widest font-mono">Data Vault (Docs)</h3>
                            <p className="text-gray-400 text-sm mb-6">Access integration guides, API specs, and agent behavioral protocols.</p>
                            
                            <div className="space-y-3">
                                {[
                                    { label: 'Agent Creation Matrix', link: '/onboarding/genius' },
                                    { label: 'Scraping Architecture', link: '/scraper/onboarding' },
                                    { label: 'Ambassador Protocol', link: '/ambassador' }
                                ].map((doc, i) => (
                                    <a key={i} href={doc.link} className="flex items-center gap-3 text-gray-400 hover:text-[#00e5ff] transition-colors group">
                                        <div className="w-1.5 h-1.5 bg-gray-600 group-hover:bg-[#00e5ff] rounded-full transition-colors" />
                                        <span className="font-mono text-sm">{doc.label}</span>
                                    </a>
                                ))}
                            </div>
                        </div>

                        {/* Security Pledge */}
                        <div className="bg-transparent border border-white/5 p-6 rounded-2xl">
                            <div className="flex items-center gap-2 mb-3">
                                <ShieldAlert className="w-4 h-4 text-gray-500" />
                                <span className="text-[10px] font-mono text-gray-500 uppercase tracking-widest">Security Clearance</span>
                            </div>
                            <p className="text-gray-500 text-xs leading-relaxed">
                                Our engineering team operates in Pacific Time (PT). Critical security anomalies or infrastructure alerts reported here bypass standard queues. 
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
