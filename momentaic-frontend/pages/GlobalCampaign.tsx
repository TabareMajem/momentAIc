import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Globe, Users, Languages, Zap, Loader2, Sparkles, Target, Copy, CheckCircle2, Crosshair } from 'lucide-react';
import { api } from '../lib/api';
import { CampaignWarMap } from '../components/campaign/CampaignWarMap';

const AVAILABLE_PERSONAS = [
    { id: 'Publishers', label: 'Publishers & Media' },
    { id: 'Advertisers', label: 'Advertisers & Brands' },
    { id: 'Agencies', label: 'Marketing Agencies' },
    { id: 'SMB Producers', label: 'SMB Producers' }
];

const AVAILABLE_LANGUAGES = [
    { id: 'EN', label: 'English (Global)' },
    { id: 'ES', label: 'Spanish (LatAm/ES)' },
    { id: 'JP', label: 'Japanese (Keigo)' }
];

interface CampaignAsset {
    persona: string;
    language: string;
    cold_email_subject: string;
    cold_email_body: string;
    linkedin_dm: string;
    landing_page_hook: string;
}

export function GlobalCampaign() {
    const [domain, setDomain] = useState('Symbiotask.com');
    const [additionalContext, setAdditionalContext] = useState('');
    const [selectedPersonas, setSelectedPersonas] = useState<string[]>(['Publishers', 'Advertisers', 'Agencies', 'SMB Producers']);
    const [selectedLanguages, setSelectedLanguages] = useState<string[]>(['EN', 'ES', 'JP']);

    const [isDeploying, setIsDeploying] = useState(false);
    const [assets, setAssets] = useState<CampaignAsset[]>([]);
    const [copiedField, setCopiedField] = useState<string | null>(null);
    const [telemetryLogs, setTelemetryLogs] = useState<string[]>([]);

    const togglePersona = (id: string) => {
        setSelectedPersonas(prev =>
            prev.includes(id) ? prev.filter(p => p !== id) : [...prev, id]
        );
    };

    const toggleLanguage = (id: string) => {
        setSelectedLanguages(prev =>
            prev.includes(id) ? prev.filter(l => l !== id) : [...prev, id]
        );
    };

    const handleDeploy = async () => {
        if (!domain || selectedPersonas.length === 0 || selectedLanguages.length === 0) return;

        setIsDeploying(true);
        setAssets([]); // clear previous
        setTelemetryLogs([]);

        const logsSequence = [
            `> TARGET_LOCK: ${domain}`,
            `> CALIBRATING_VECTORS: [${selectedPersonas.join(', ')}]`,
            `> INITIALIZING_UPLINK: [${selectedLanguages.join(', ')}]`,
            `> DEPLOYING_AUTONOMOUS_WORKERS...`,
            `> COMPILING_CULTURAL_MATRICES...`,
            `> BYPASSING_SPAM_FILTERS...`
        ];

        let i = 0;
        const logInterval = setInterval(() => {
            if (i < logsSequence.length) {
                setTelemetryLogs(prev => [...prev, logsSequence[i]]);
                i++;
            }
        }, 1200);

        try {
            const response = await api.deployGlobalCampaign({
                domain,
                personas: selectedPersonas,
                languages: selectedLanguages,
                additional_context: additionalContext
            });
            clearInterval(logInterval);
            setTelemetryLogs(prev => [...prev, '> PAYLOADS_GENERATED [OK]. TRANSMITTING TO TERMINAL...']);

            setTimeout(() => {
                setAssets(response.assets || []);
                setIsDeploying(false);
            }, 1000);
        } catch (error) {
            clearInterval(logInterval);
            console.error("Failed to deploy global campaign:", error);
            alert("Generative error occurred. Check container logs.");
            setIsDeploying(false);
        }
    };

    const copyToClipboard = (text: string, fieldId: string) => {
        navigator.clipboard.writeText(text);
        setCopiedField(fieldId);
        setTimeout(() => setCopiedField(null), 2000);
    };

    return (
        <div className="p-8 max-w-7xl mx-auto space-y-8 font-mono pb-24">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold flex items-center gap-3 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400">
                        <Globe className="w-8 h-8 text-blue-400" />
                        WORLD DOMINATION ENGINE
                    </h1>
                    <p className="text-gray-400 mt-2 tracking-widest text-sm uppercase">Multilingual Outbound Matrix Generator</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

                {/* Radar Configuration Column */}
                <div className="space-y-6">
                    <div className="bg-[#111] border border-white/10 rounded-2xl p-6 relative overflow-hidden group">
                        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-emerald-500/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>

                        <h2 className="text-white font-bold tracking-widest mb-6 flex items-center gap-2 text-sm uppercase">
                            <Target className="w-4 h-4 text-emerald-400" /> Mission Parameters
                        </h2>

                        <div className="space-y-4">
                            <div>
                                <label className="text-[10px] text-gray-500 tracking-widest uppercase mb-1 block">Target Domain / Product</label>
                                <input
                                    type="text"
                                    value={domain}
                                    onChange={(e) => setDomain(e.target.value)}
                                    className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-3 text-white focus:border-emerald-500 transition-colors"
                                    placeholder="e.g. Symbiotask.com"
                                />
                            </div>

                            <div>
                                <label className="text-[10px] text-gray-500 tracking-widest uppercase mb-1 block">Strategic Context (Optional)</label>
                                <textarea
                                    value={additionalContext}
                                    onChange={(e) => setAdditionalContext(e.target.value)}
                                    className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-3 text-white focus:border-emerald-500 transition-colors h-24 resize-none"
                                    placeholder="Explain the core value prop..."
                                />
                            </div>
                        </div>
                    </div>

                    {/* Targeting */}
                    <div className="bg-[#111] border border-white/10 rounded-2xl p-6">
                        <h2 className="text-white font-bold tracking-widest mb-4 flex items-center gap-2 text-sm uppercase">
                            <Users className="w-4 h-4 text-blue-400" /> Target Vectors
                        </h2>
                        <div className="grid grid-cols-2 gap-2">
                            {AVAILABLE_PERSONAS.map(p => (
                                <button
                                    key={p.id}
                                    onClick={() => togglePersona(p.id)}
                                    className={`text-left p-3 rounded-lg border text-xs transition-all ${selectedPersonas.includes(p.id)
                                        ? 'bg-blue-500/20 border-blue-500/50 text-blue-400'
                                        : 'bg-black/50 border-white/10 text-gray-500 hover:border-white/20'
                                        }`}
                                >
                                    {p.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Languages */}
                    <div className="bg-[#111] border border-white/10 rounded-2xl p-6">
                        <h2 className="text-white font-bold tracking-widest mb-4 flex items-center gap-2 text-sm uppercase">
                            <Languages className="w-4 h-4 text-purple-400" /> Localization Protocols
                        </h2>
                        <div className="flex flex-col gap-2">
                            {AVAILABLE_LANGUAGES.map(l => (
                                <button
                                    key={l.id}
                                    onClick={() => toggleLanguage(l.id)}
                                    className={`flex justify-between items-center p-3 rounded-lg border text-xs transition-all ${selectedLanguages.includes(l.id)
                                        ? 'bg-purple-500/20 border-purple-500/50 text-purple-400'
                                        : 'bg-black/50 border-white/10 text-gray-500 hover:border-white/20'
                                        }`}
                                >
                                    <span className="font-bold">{l.id}</span>
                                    <span>{l.label}</span>
                                </button>
                            ))}
                        </div>
                    </div>

                    <button
                        onClick={handleDeploy}
                        disabled={isDeploying || !domain || selectedPersonas.length === 0 || selectedLanguages.length === 0}
                        className={`w-full py-4 rounded-xl font-bold tracking-widest uppercase flex items-center justify-center gap-2 transition-all ${isDeploying
                            ? 'bg-gray-800 text-gray-500 cursor-not-allowed'
                            : 'bg-gradient-to-r from-emerald-500 to-blue-500 hover:from-emerald-400 hover:to-blue-400 text-white shadow-[0_0_30px_rgba(16,185,129,0.3)]'
                            }`}
                    >
                        {isDeploying ? (
                            <><Loader2 className="w-5 h-5 animate-spin" /> GENERATING MATRIX...</>
                        ) : (
                            <><Zap className="w-5 h-5" /> DEPLOY GLOBAL SWARM</>
                        )}
                    </button>
                </div>

                {/* Output Matrix Grid */}
                <div className="lg:col-span-2 space-y-6">
                    <div className="bg-[#111] border border-white/10 rounded-2xl p-6 min-h-[600px]">
                        <h2 className="text-white font-bold tracking-widest mb-6 flex items-center justify-between text-sm uppercase border-b border-white/10 pb-4">
                            <span className="flex items-center gap-2"><Sparkles className="w-4 h-4 text-yellow-500" /> OUTBOUND MATRIX PAYLOADS</span>
                            <span className="text-[10px] text-gray-500">{assets.length} ASSETS GENERATED</span>
                        </h2>

                        {isDeploying ? (
                            <div className="relative w-full h-full min-h-[600px] rounded-xl overflow-hidden bg-[#020202] border border-white/5">
                                <CampaignWarMap activeTargets={selectedLanguages} isDeploying={isDeploying} />

                                {/* Telemetry Terminal Overlay */}
                                <div className="absolute bottom-4 left-4 right-4 bg-black/80 backdrop-blur-md border border-purple-500/30 rounded-lg p-4 font-mono text-[11px] text-emerald-400 space-y-1 shadow-[0_0_20px_rgba(168,85,247,0.15)] z-20">
                                    <div className="flex items-center gap-2 mb-2 pb-2 border-b border-white/10 text-gray-500">
                                        <Crosshair className="w-3 h-3 text-purple-400" />
                                        <span>LIVE_EXECUTION_STREAM</span>
                                    </div>
                                    {telemetryLogs.map((log, i) => (
                                        <div key={i} className="animate-fade-in">{log}</div>
                                    ))}
                                    <div className="w-2 h-3 bg-emerald-500 animate-blink inline-block" />
                                </div>
                            </div>
                        ) : assets.length > 0 ? (
                            <div className="space-y-8">
                                {assets.map((asset, idx) => (
                                    <motion.div
                                        key={idx}
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ delay: idx * 0.1 }}
                                        className="bg-black/40 border border-white/10 rounded-xl overflow-hidden"
                                    >
                                        {/* Asset Header */}
                                        <div className="bg-white/5 px-4 py-2 border-b border-white/10 flex items-center justify-between text-xs">
                                            <div className="flex items-center gap-3">
                                                <span className="px-2 py-1 bg-amber-500/20 text-amber-400 rounded-md font-bold">{asset.persona}</span>
                                                <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded-md font-bold">{asset.language}</span>
                                            </div>
                                        </div>

                                        {/* Asset Content */}
                                        <div className="p-4 space-y-4 text-sm">

                                            {/* Cold Email */}
                                            <div className="space-y-2">
                                                <div className="flex items-center justify-between text-[10px] tracking-widest text-gray-500 uppercase">
                                                    <span>Cold Email Pipeline</span>
                                                    <button onClick={() => copyToClipboard(`Subject: ${asset.cold_email_subject}\n\n${asset.cold_email_body}`, `${idx}-email`)} className="hover:text-white transition-colors">
                                                        {copiedField === `${idx}-email` ? <CheckCircle2 className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                                                    </button>
                                                </div>
                                                <div className="bg-white/5 p-3 rounded-lg border border-white/5 hover:border-white/10 transition-colors">
                                                    <p className="text-white font-bold mb-2">Subj: {asset.cold_email_subject}</p>
                                                    <p className="text-gray-300 font-sans whitespace-pre-wrap">{asset.cold_email_body}</p>
                                                </div>
                                            </div>

                                            {/* LinkedIn DM & Hook */}
                                            <div className="grid grid-cols-2 gap-4">
                                                <div className="space-y-2">
                                                    <div className="flex items-center justify-between text-[10px] tracking-widest text-gray-500 uppercase">
                                                        <span>LinkedIn DM / Quick Pitch</span>
                                                        <button onClick={() => copyToClipboard(asset.linkedin_dm, `${idx}-dm`)} className="hover:text-white transition-colors">
                                                            {copiedField === `${idx}-dm` ? <CheckCircle2 className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                                                        </button>
                                                    </div>
                                                    <div className="bg-white/5 p-3 rounded-lg border border-white/5 hover:border-white/10 transition-colors h-full">
                                                        <p className="text-gray-300 font-sans">{asset.linkedin_dm}</p>
                                                    </div>
                                                </div>

                                                <div className="space-y-2">
                                                    <div className="flex items-center justify-between text-[10px] tracking-widest text-gray-500 uppercase">
                                                        <span>Landing Page Hook (H1)</span>
                                                        <button onClick={() => copyToClipboard(asset.landing_page_hook, `${idx}-hook`)} className="hover:text-white transition-colors">
                                                            {copiedField === `${idx}-hook` ? <CheckCircle2 className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                                                        </button>
                                                    </div>
                                                    <div className="bg-emerald-500/10 p-3 rounded-lg border border-emerald-500/20 hover:border-emerald-500/40 transition-colors h-full flex items-center justify-center text-center">
                                                        <p className="text-emerald-400 font-bold text-lg">{asset.landing_page_hook}</p>
                                                    </div>
                                                </div>
                                            </div>

                                        </div>
                                    </motion.div>
                                ))}
                            </div>
                        ) : (
                            <div className="h-full min-h-[400px] flex flex-col items-center justify-center text-center opacity-30">
                                <Target className="w-16 h-16 text-gray-500 mb-4" />
                                <h3 className="text-gray-400 font-bold tracking-widest uppercase mb-2">Awaiting Target Coordinates</h3>
                                <p className="text-xs text-gray-500 max-w-sm">Select your personas and languages on the left, then deploy the swarm to generate localized assets.</p>
                            </div>
                        )}
                    </div>
                </div>

            </div>
        </div>
    );
}

export default GlobalCampaign;
