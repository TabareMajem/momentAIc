import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, Zap, Target, Eye, PenTool, Users, Video, Palette, Code, DollarSign, Activity, Lock, AlertTriangle, Flame, CircleDashed, Check } from 'lucide-react';
import { Button } from '../../components/ui/Button';

// ============ ICONS MAPPING ============
const AGENT_ICONS: any = {
    general: Shield,
    sniper: Target,
    banshee: Zap,
    spy: Eye,
    architect: PenTool,
    riot: Users,
    director: Video,
    artist: Palette,
    hacker: Code,
    closer: DollarSign
};

export function WarRoomWidget({ product, onClose }: { product: any, onClose: () => void }) {
    const [status, setStatus] = useState<any>({}); // { [agentKey]: { status: 'idle' | 'running' | 'complete' | 'error', output: ... } }
    const [running, setRunning] = useState(false);
    const [missionComplete, setMissionComplete] = useState(false);
    const [dryRun, setDryRun] = useState(true); // SAFETY: Default to dry run

    const swarmAgents = [
        { key: "general", name: "The General", role: "Strategy" },
        { key: "sniper", name: "The Sniper", role: "Outbound Targets" },
        { key: "banshee", name: "The Banshee", role: "Viral Social" },
        { key: "spy", name: "The Spy", role: "Intel" },
        { key: "architect", name: "The Architect", role: "SEO Skyscraper" },
        { key: "riot", name: "The Riot", role: "Community Revolution" },
        { key: "director", name: "The Director", role: "Video Scripts" },
        { key: "artist", name: "The Artist", role: "Visual Identity" },
        { key: "hacker", name: "The Hacker", role: "Growth Hacks" },
        { key: "closer", name: "The Closer", role: "Closing Copies" },
    ];

    const handleDeploySwarm = async () => {
        setRunning(true);
        setMissionComplete(false);

        // Init status
        const initialCloud: any = {};
        swarmAgents.forEach(a => initialCloud[a.key] = { status: 'running' });
        setStatus(initialCloud);

        try {
            const productKey = getProductKey(product.name);

            const token = localStorage.getItem('token');
            const res = await fetch(`/api/v1/admin/swarm/deploy/${productKey}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({ dry_run: dryRun })
            });

            const data = await res.json();

            if (data.artifacts) {
                setMissionComplete(true);
                const finalStatus: any = {};
                Object.entries(data.artifacts).forEach(([key, val]: [string, any]) => {
                    finalStatus[key] = {
                        status: val.error ? 'error' : 'complete',
                        output: val.output || val.error,
                        bridge: val.bridge
                    };
                });
                setStatus(finalStatus);
            }

        } catch (e) {
            alert("Swarm deployment failed.");
            setRunning(false);
        } finally {
            setRunning(false);
        }
    };

    const getProductKey = (name: string) => {
        if (name.includes("Bond")) return "bondquests";
        if (name.includes("Otaku")) return "otaku";
        if (name.includes("Campus")) return "campus";
        if (name.includes("Kids")) return "kids";
        if (name.includes("Forge")) return "agentforge";
        if (name.includes("Moment")) return "momentaic";
        return "yokaizen";
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
            <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="bg-[#050510] border border-red-500/30 rounded-2xl w-full max-w-6xl h-[90vh] overflow-hidden flex flex-col shadow-[0_0_50px_rgba(220,38,38,0.2)]"
            >
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-red-900/30 bg-red-950/10">
                    <div className="flex items-center gap-4">
                        <Activity className="w-8 h-8 text-red-500 animate-pulse" />
                        <div>
                            <h2 className="text-2xl font-black text-white tracking-tighter uppercase">WAR ROOM: {product.name}</h2>
                            <p className="text-red-400 font-mono text-xs tracking-widest">
                                MODE: {dryRun ? 'DRY RUN (SIMULATION)' : '🔥 LIVE FIRE'}
                            </p>
                        </div>
                    </div>
                    <div className="flex gap-2 items-center">
                        {/* MODE TOGGLE */}
                        <button
                            onClick={() => setDryRun(!dryRun)}
                            className={`px-4 py-2 rounded-lg font-mono text-xs flex items-center gap-2 transition-all ${dryRun
                                ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                                : 'bg-red-600 text-white border border-red-500 shadow-[0_0_20px_rgba(239,68,68,0.5)]'
                                }`}
                        >
                            {dryRun ? <CircleDashed className="w-4 h-4" /> : <Flame className="w-4 h-4" />}
                            {dryRun ? 'DRY RUN' : 'LIVE FIRE'}
                        </button>

                        {!missionComplete && !running && (
                            <Button variant="destructive" size="lg" onClick={handleDeploySwarm} className="animate-pulse shadow-[0_0_20px_rgba(239,68,68,0.5)]">
                                <Zap className="w-5 h-5 mr-2" />
                                DEPLOY 10 AGENTS
                            </Button>
                        )}
                        <Button variant="ghost" onClick={onClose}>Close</Button>
                    </div>
                </div>

                {/* Tactical Map */}
                <div className="flex-1 p-6 overflow-y-auto relative">
                    {/* Central Hub */}
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 border border-red-500/10 rounded-full animate-ping pointer-events-none" />

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
                        {swarmAgents.map((agent) => {
                            const s = status[agent.key] || { status: 'idle' };
                            const Icon = AGENT_ICONS[agent.key] || Shield;

                            return (
                                <div key={agent.key} className={`
                          relative p-4 rounded-xl border transition-all duration-500
                          ${s.status === 'running' ? 'bg-red-500/10 border-red-500 animate-pulse' :
                                        s.status === 'complete' ? 'bg-emerald-500/5 border-emerald-500/50' :
                                            'bg-slate-900/50 border-slate-800 opacity-50'}
                      `}>
                                    <div className="flex items-center gap-3 mb-3">
                                        <div className={`p-2 rounded-lg ${s.status === 'complete' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
                                            <Icon className="w-5 h-5" />
                                        </div>
                                        <div>
                                            <div className="font-bold text-sm text-white">{agent.name}</div>
                                            <div className="text-[10px] text-slate-400 uppercase tracking-wider">{agent.role}</div>
                                        </div>
                                    </div>

                                    {/* Output Terminal */}
                                    <div className="h-48 bg-black rounded border border-white/5 p-3 overflow-y-auto font-mono text-[10px] text-green-400">
                                        {s.status === 'idle' && <span className="text-slate-600">Waiting for deployment...</span>}
                                        {isRunning && (
                                            <div className={dryRun ? "text-cyan-500/80" : "text-red-500/80"}>
                                                <div className="mb-2 opacity-50">
                                                    <span>&gt; INITIALIZING HANDSHAKE... OK</span><br />
                                                    <span>&gt; LOADING NEURAL MODEL: GEMINI-2.0... OK</span><br />
                                                    <span>&gt; CONNECTING TO {dryRun ? 'SIMULATION' : 'REALITY'} BRIDGE... OK</span>
                                                </div>
                                                <div className="animate-pulse">&gt; EXECUTING MISSION PARAMETERS...</div>
                                                <div className="mt-4 flex gap-1">
                                                    <span className="w-2 h-4 bg-current animate-[pulse_0.5s_infinite]" />
                                                </div>
                                            </div>
                                        )}
                                        {s.status === 'complete' && (
                                            <pre className="whitespace-pre-wrap">{JSON.stringify(s.output, null, 2)}</pre>
                                        )}
                                    </div>

                                    {s.status === 'running' && (
                                        <div className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full animate-ping" />
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </div>

            </motion.div>
        </div>
    );
}
