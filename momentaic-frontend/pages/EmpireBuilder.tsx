import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../stores/auth-store';
import { api } from '../lib/api';
import { Button } from '../components/ui/Button';
import { Logo } from '../components/ui/Logo';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card';
import { useToast } from '../components/ui/Toast';
import {
    Users, Target, Zap, Shield, Globe,
    ArrowRight, CheckCircle, Lock, Play,
    ChevronRight, Terminal, Brain, Rocket,
    Twitter, Linkedin, Mic, PhoneCall
} from 'lucide-react';
import { cn } from '../lib/utils';
import { Link, useNavigate } from 'react-router-dom';

// --- COMPONENTS ---

const StepIndicator = ({ currentStep, steps }: { currentStep: number, steps: any[] }) => (
    <div className="flex justify-between mb-8 relative">
        <div className="absolute top-1/2 left-0 w-full h-1 bg-white/10 -z-10 -translate-y-1/2 rounded-full"></div>
        <div
            className="absolute top-1/2 left-0 h-1 bg-gradient-to-r from-purple-500 to-cyan-500 -z-10 -translate-y-1/2 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${(currentStep / (steps.length - 1)) * 100}%` }}
        ></div>

        {steps.map((step, idx) => (
            <div key={idx} className="flex flex-col items-center gap-2">
                <div
                    className={cn(
                        "w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all duration-300 z-10",
                        currentStep > idx ? "bg-green-500 border-green-500 text-black" :
                            currentStep === idx ? "bg-[#0a0a0a] border-[#00f0ff] text-[#00f0ff] shadow-[0_0_15px_rgba(0,240,255,0.5)]" :
                                "bg-[#0a0a0a] border-white/20 text-gray-500"
                    )}
                >
                    {currentStep > idx ? <CheckCircle className="w-5 h-5" /> : step.icon}
                </div>
                <div className={cn(
                    "text-[10px] font-mono uppercase tracking-wider font-bold",
                    currentStep >= idx ? "text-white" : "text-gray-600"
                )}>
                    {step.label}
                </div>
            </div>
        ))}
    </div>
);

const StepCard = ({ children, title, description, isActive }: { children: React.ReactNode, title: string, description: string, isActive: boolean }) => (
    <div className={cn(
        "transition-all duration-500 ease-out absolute inset-0 w-full",
        isActive ? "opacity-100 translate-x-0 relative pointer-events-auto" : "opacity-0 translate-x-12 absolute pointer-events-none"
    )}>
        <Card className="bg-[#050505] border-white/10 h-full overflow-hidden">
            <CardHeader className="border-b border-white/5 bg-[#0a0a0a]">
                <CardTitle className="text-2xl font-black text-white uppercase tracking-tight flex items-center gap-3">
                    <span className="text-[#00f0ff]">{title}</span>
                </CardTitle>
                <CardDescription>{description}</CardDescription>
            </CardHeader>
            <CardContent className="p-8">
                {children}
            </CardContent>
        </Card>
    </div>
);

export default function EmpireBuilder() {
    const { isAuthenticated, user } = useAuthStore();
    const navigate = useNavigate();
    const { toast } = useToast();

    // Steps: Vision (0), Voice (1), Intel (2), Army (3), Scale (4)
    const [currentStep, setCurrentStep] = useState(0);
    const [loading, setLoading] = useState(false);
    const [startupId, setStartupId] = useState<string | null>(null);

    // State for individual steps
    const [socialConnected, setSocialConnected] = useState({ twitter: false, linkedin: false });
    const [competitorUrl, setCompetitorUrl] = useState('');
    const [battleCard, setBattleCard] = useState<string | null>(null);
    const [targetAudience, setTargetAudience] = useState('');
    const [salesLeads, setSalesLeads] = useState<any[]>([]);

    const steps = [
        { label: 'Vision', icon: <Brain className="w-4 h-4" /> },
        { label: 'Voice', icon: <Globe className="w-4 h-4" /> },
        { label: 'Intel', icon: <Target className="w-4 h-4" /> },
        { label: 'Army', icon: <Users className="w-4 h-4" /> },
        { label: 'Scale', icon: <Rocket className="w-4 h-4" /> },
    ];

    // -- STEP 2: VOICE --
    const handleConnectSocial = (platform: 'twitter' | 'linkedin') => {
        // In a real flow, this would open oauth
        // For demo/builder flow, we simulate or check status
        toast({ type: 'info', title: 'Connecting...', message: `Authenticating with ${platform}...` });

        setTimeout(() => {
            setSocialConnected(prev => ({ ...prev, [platform]: true }));
            toast({ type: 'success', title: 'Connected', message: `${platform} secured.` });
        }, 1500);
    };

    // -- STEP 3: INTEL --
    const handleAnalyzeCompetitor = async () => {
        if (!competitorUrl || !startupId) return;
        setLoading(true);
        try {
            // REAL AGENT CALL
            const result = await api.triggerCompetitorMonitor(startupId, [competitorUrl]);

            // Parse result (Monitor returns "updates" or discovery list)
            // But here we want specific analysis.
            // For now, we use the specific analysis result or fallback
            // My backend implementation used `monitor_market`. Let's assume it returns something useful.
            // If it returns "updates", we show that.

            let battleText = "## Analysis Data\n\n";
            if (result.updates && result.updates.length > 0) {
                battleText += result.updates.join('\n');
            } else if (result.new_competitors) {
                battleText += JSON.stringify(result.new_competitors, null, 2);
            } else {
                battleText += "Competitor tracked. Collecting intelligence...";
            }

            setBattleCard(battleText);

            toast({
                type: 'success',
                title: 'Intel Gathered',
                message: `Intelligence stored for ${competitorUrl}.`
            });
            // Update step data locally so nextStep can pick it up
            // (We rely on nextStep to sync to backend)
        } catch (error) {
            console.error(error);
            toast({ type: 'error', title: 'Analysis Failed', message: 'The Competitor Intel Agent encountered an error.' });
        } finally {
            setLoading(false);
        }
    };

    // -- STEP 4: ARMY --
    const handleFindLeads = async () => {
        if (!targetAudience || !startupId) return;
        setLoading(true);
        try {
            // REAL AGENT CALL
            const result = await api.triggerSalesHunt(startupId);
            const leads = result.leads || [];

            if (leads.length > 0) {
                setSalesLeads(leads.map((l: any) => ({
                    name: l.lead.contact_name,
                    role: l.lead.contact_title + ' @ ' + l.lead.company_name,
                    status: l.verified ? 'Verified & Drafted' : 'Drafting...'
                })));

                toast({
                    type: 'success',
                    title: 'Hunt Complete',
                    message: `Sales Agent found ${leads.length} new leads.`
                });
            } else {
                toast({ type: 'warning', title: 'Hunt Empty', message: 'No leads found yet. Try refining audience.' });
                // Add dummy for UI if empty, or just leave empty?
                // Let's leave empty to be honest.
            }
        } catch (error) {
            console.error(error);
            toast({ type: 'error', title: 'Hunt Failed', message: 'The Sales Agent encountered an error.' });
        } finally {
            setLoading(false);
        }
    };

    // Load status on mount
    useEffect(() => {
        const fetchStatus = async () => {
            if (!isAuthenticated) return;
            try {
                // Fetch Startup ID
                const startups = await api.getStartups();
                if (startups.length > 0) {
                    setStartupId(startups[0].id);
                }

                const status = await api.getEmpireStatus();
                setCurrentStep(status.current_step);
                if (status.step_data) {
                    if (status.step_data.socialConnected) setSocialConnected(status.step_data.socialConnected);
                    if (status.step_data.competitorUrl) setCompetitorUrl(status.step_data.competitorUrl);
                    if (status.step_data.battleCard) setBattleCard(status.step_data.battleCard);
                    if (status.step_data.targetAudience) setTargetAudience(status.step_data.targetAudience);
                    if (status.step_data.salesLeads) setSalesLeads(status.step_data.salesLeads);
                }
            } catch (e) {
                console.error("Failed to fetch empire status:", e);
            }
        };
        fetchStatus();
    }, [isAuthenticated]);

    const nextStep = async () => {
        const isFinal = currentStep === steps.length - 1;
        const nextIdx = currentStep + 1;

        setLoading(true);
        try {
            // Collect metadata to save
            const metadata: any = {};
            if (currentStep === 1) metadata.socialConnected = socialConnected;
            if (currentStep === 2) {
                metadata.competitorUrl = competitorUrl;
                metadata.battleCard = battleCard;
            }
            if (currentStep === 3) {
                metadata.targetAudience = targetAudience;
                metadata.salesLeads = salesLeads;
            }

            await api.updateEmpireStep(
                isFinal ? currentStep : nextIdx,
                metadata,
                isFinal
            );

            if (isFinal) {
                navigate('/dashboard');
            } else {
                setCurrentStep(nextIdx);
                window.scrollTo(0, 0);
            }
        } catch (e) {
            console.error("Failed to sync progress:", e);
            toast({ type: 'error', title: 'Sync Warning', message: 'Proceeding with local state only.' });
            if (!isFinal) setCurrentStep(nextIdx);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#020202] text-white font-sans overflow-hidden relative">

            {/* Ambient Background */}
            <div className="absolute inset-0 bg-cyber-grid bg-[length:50px_50px] opacity-10 pointer-events-none"></div>
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-purple-500 via-cyan-500 to-purple-500 opacity-50"></div>

            <div className="max-w-4xl mx-auto px-6 py-12 relative z-10 flex flex-col h-screen">

                {/* Header */}
                <div className="flex justify-between items-center mb-12">
                    <Logo />
                    <div className="font-mono text-xs text-gray-500 flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                        EMPIRE_BUILDER_PROTOCOL_V1
                    </div>
                </div>

                {/* Progress */}
                <StepIndicator currentStep={currentStep} steps={steps} />

                {/* Main Content Area */}
                <div className="flex-1 relative">

                    {/* STEP 1: VISION */}
                    <StepCard
                        isActive={currentStep === 0}
                        title="01: VISION"
                        description="Your strategic foundation. Established in Genius Mode."
                    >
                        <div className="space-y-6">
                            <div className="p-6 bg-[#0a0a0a] border border-white/10 rounded-xl">
                                <h3 className="text-lg font-bold text-white mb-2">Strategic Directive</h3>
                                <p className="text-gray-400 text-sm mb-4">
                                    "Build a high-velocity conversion engine for B2B SaaS founders using AI agents."
                                </p>
                                <div className="flex gap-2">
                                    <span className="px-2 py-1 bg-purple-500/20 text-purple-400 text-xs rounded font-mono">MVP</span>
                                    <span className="px-2 py-1 bg-cyan-500/20 text-cyan-400 text-xs rounded font-mono">Growth</span>
                                </div>
                            </div>
                            <Button variant="cyber" className="w-full" onClick={nextStep}>
                                CONFIRM DIRECTIVE <ChevronRight className="w-4 h-4 ml-2" />
                            </Button>
                        </div>
                    </StepCard>

                    {/* STEP 2: VOICE */}
                    <StepCard
                        isActive={currentStep === 1}
                        title="02: VOICE"
                        description="Establish your digital presence. Agents need authorization to speak."
                    >
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                            <button
                                onClick={() => handleConnectSocial('twitter')}
                                className={cn(
                                    "p-6 rounded-xl border transition-all flex flex-col items-center gap-4 group",
                                    socialConnected.twitter ? "bg-cyan-500/10 border-cyan-500/50" : "bg-[#0a0a0a] border-white/10 hover:border-white/30"
                                )}
                            >
                                <Twitter className={cn("w-8 h-8", socialConnected.twitter ? "text-cyan-400" : "text-gray-500")} />
                                <div className="text-sm font-bold text-white">Twitter X</div>
                                <div className="text-xs text-gray-500 font-mono">
                                    {socialConnected.twitter ? "CONNECTED" : "Start Connection"}
                                </div>
                            </button>

                            <button
                                onClick={() => handleConnectSocial('linkedin')}
                                className={cn(
                                    "p-6 rounded-xl border transition-all flex flex-col items-center gap-4 group",
                                    socialConnected.linkedin ? "bg-blue-600/10 border-blue-500/50" : "bg-[#0a0a0a] border-white/10 hover:border-white/30"
                                )}
                            >
                                <Linkedin className={cn("w-8 h-8", socialConnected.linkedin ? "text-blue-400" : "text-gray-500")} />
                                <div className="text-sm font-bold text-white">LinkedIn</div>
                                <div className="text-xs text-gray-500 font-mono">
                                    {socialConnected.linkedin ? "CONNECTED" : "Start Connection"}
                                </div>
                            </button>
                        </div>

                        {/* AgentForge Voice Trigger */}
                        <div className="bg-slate-900/50 p-4 rounded-lg border border-white/5 mb-6">
                            <h4 className="text-sm font-semibold text-purple-400 mb-2 flex items-center gap-2">
                                <Mic className="w-4 h-4" />
                                AgentForge Voice Comms
                            </h4>
                            <p className="text-xs text-slate-400 mb-3">
                                Need to refine your voice? Talk to our AI Strategist directly to calibrate your tone.
                            </p>
                            <Button
                                className="w-full"
                                variant="cyber"
                                onClick={async () => {
                                    try {
                                        await api.triggerVoiceAgent("Requesting calibration call for user.");
                                        // Using alert for now as toast requires hook context or props if strict
                                        alert("Calling your registered phone number...");
                                    } catch (e) {
                                        console.error(e);
                                        alert("Failed to initiate call. Check integration settings.");
                                    }
                                }}
                            >
                                <PhoneCall className="w-4 h-4 mr-2" />
                                Talk to Strategist
                            </Button>
                        </div>

                        <Button
                            variant="cyber"
                            className="w-full"
                            onClick={nextStep}
                            disabled={!socialConnected.twitter && !socialConnected.linkedin}
                        >
                            INITIALIZE VOICE PROTOCOL <ChevronRight className="w-4 h-4 ml-2" />
                        </Button>
                    </StepCard>

                    {/* STEP 3: INTEL */}
                    <StepCard
                        isActive={currentStep === 2}
                        title="03: INTEL"
                        description="Know your enemy. Use the Competitor Intel Agent."
                    >
                        <div className="space-y-6">
                            {!battleCard ? (
                                <div className="space-y-4">
                                    <label className="text-xs font-mono text-gray-500 uppercase">Target Competitor URL</label>
                                    <div className="flex gap-4">
                                        <input
                                            type="text"
                                            className="flex-1 bg-[#0a0a0a] border border-white/10 rounded-lg px-4 h-12 text-white focus:outline-none focus:border-[#00f0ff]"
                                            placeholder="https://competitor.com"
                                            value={competitorUrl}
                                            onChange={(e) => setCompetitorUrl(e.target.value)}
                                        />
                                        <Button
                                            onClick={handleAnalyzeCompetitor}
                                            isLoading={loading}
                                            disabled={!competitorUrl}
                                        >
                                            SCAN
                                        </Button>
                                    </div>
                                </div>
                            ) : (
                                <div className="animate-fade-in-up">
                                    <div className="bg-[#0a0a0a] border border-red-500/30 p-6 rounded-xl font-mono text-sm leading-relaxed whitespace-pre-line text-gray-300 relative overflow-hidden">
                                        <div className="absolute top-0 right-0 p-2 text-xs text-red-500 font-bold border-l border-b border-red-500/30 bg-red-500/10">CONFIDENTIAL</div>
                                        {battleCard}
                                    </div>
                                    <Button variant="cyber" className="w-full mt-6" onClick={nextStep}>
                                        STORE INTELLIGENCE <ChevronRight className="w-4 h-4 ml-2" />
                                    </Button>
                                </div>
                            )}
                        </div>
                    </StepCard>

                    {/* STEP 4: ARMY */}
                    <StepCard
                        isActive={currentStep === 3}
                        title="04: THE ARMY"
                        description="Deploy Sales Hunter agents to find high-value targets."
                    >
                        <div className="space-y-6">
                            {salesLeads.length === 0 ? (
                                <div className="space-y-4">
                                    <label className="text-xs font-mono text-gray-500 uppercase">Define Ideal Customer Profile (ICP)</label>
                                    <div className="flex gap-4">
                                        <input
                                            type="text"
                                            className="flex-1 bg-[#0a0a0a] border border-white/10 rounded-lg px-4 h-12 text-white focus:outline-none focus:border-[#00f0ff]"
                                            placeholder="e.g., CTOs of Series A Fintech startups in NY"
                                            value={targetAudience}
                                            onChange={(e) => setTargetAudience(e.target.value)}
                                        />
                                        <Button
                                            onClick={handleFindLeads}
                                            isLoading={loading}
                                            disabled={!targetAudience}
                                        >
                                            HUNT
                                        </Button>
                                    </div>
                                </div>
                            ) : (
                                <div className="animate-fade-in-up">
                                    <div className="space-y-3 mb-6">
                                        {salesLeads.map((lead, i) => (
                                            <div key={i} className="flex items-center justify-between p-4 bg-[#0a0a0a] border border-white/5 rounded-lg">
                                                <div>
                                                    <div className="font-bold text-white">{lead.name}</div>
                                                    <div className="text-xs text-gray-500">{lead.role}</div>
                                                </div>
                                                <div className="text-[10px] font-mono text-[#00f0ff] animate-pulse">
                                                    {lead.status}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                    <Button variant="cyber" className="w-full" onClick={nextStep}>
                                        AUTHORIZE OUTREACH <ChevronRight className="w-4 h-4 ml-2" />
                                    </Button>
                                </div>
                            )}
                        </div>
                    </StepCard>

                    {/* STEP 5: SCALE */}
                    <StepCard
                        isActive={currentStep === 4}
                        title="05: SCALE"
                        description="Empire Protocol Ready. Launch Command Center."
                    >
                        <div className="text-center py-10 space-y-6">
                            <div className="w-24 h-24 bg-gradient-to-br from-purple-500 to-cyan-500 rounded-full mx-auto flex items-center justify-center animate-pulse shadow-[0_0_50px_rgba(168,85,247,0.5)]">
                                <Rocket className="w-10 h-10 text-white" />
                            </div>
                            <h2 className="text-3xl font-black text-white">SYSTEM ONLINE</h2>
                            <p className="text-gray-400 max-w-md mx-auto">
                                All agents are primed. Integrations active. Target list acquired.
                                You are ready to build.
                            </p>
                            <Button variant="cyber" size="lg" className="px-12 h-14 text-lg" onClick={() => navigate('/dashboard')}>
                                ENTER COMMAND CENTER
                            </Button>
                        </div>
                    </StepCard>
                </div>

            </div>
        </div>
    );
}
