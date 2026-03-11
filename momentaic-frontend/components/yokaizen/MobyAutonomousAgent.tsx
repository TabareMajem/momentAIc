
import React, { useState } from 'react';
import { BrainCircuit, Share2, Activity, Zap, Layers, Network, ShieldCheck, ChevronRight, RefreshCw, Globe, Lock } from 'lucide-react';
import { BackendService } from '../../services/backendService';
import { useToast } from './Toast';

export interface QuantumState {
    dimension: string;
    status: 'COHERENT' | 'ENTANGLED' | 'SUPERPOSITION';
    probability: number;
    insight: string;
}

export interface IntegrationDiscovery {
    id: string;
    platform: string;
    type: 'API' | 'WEBHOOK' | 'OAUTH';
    potentialImpact: string;
    status: 'DISCOVERED' | 'MAPPED' | 'INTEGRATED';
}

const MobyAutonomousAgent: React.FC = () => {
    const [targetDomain, setTargetDomain] = useState('');
    const [quantumContext, setQuantumContext] = useState('SaaS Enterprise Buyer, hesitant about pricing, exploring AI competitors.');

    const [quantumStates, setQuantumStates] = useState<QuantumState[]>([]);
    const [integrations, setIntegrations] = useState<IntegrationDiscovery[]>([]);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [isScanning, setIsScanning] = useState(false);
    const { addToast } = useToast();

    const handleQuantumAnalysis = async () => {
        setIsAnalyzing(true);
        try {
            const response = await BackendService.analyzeQuantumState(quantumContext);
            if (response.success) {
                setQuantumStates(response.states);
                addToast("Quantum state analyzed", 'success');
            } else {
                addToast(response.error || "Analysis failed", 'error');
            }
        } catch (e) {
            console.error(e);
            addToast("Analysis failed", 'error');
        } finally {
            setIsAnalyzing(false);
        }
    };

    const handleScan = async () => {
        setIsScanning(true);
        try {
            const response = await BackendService.runIntegrationSpider(targetDomain);
            if (response.success) {
                setIntegrations(response.integrations);
                addToast("Integration scan complete", 'success');
            } else {
                addToast(response.error || "Scan failed", 'error');
            }
        } catch (e) {
            console.error(e);
            addToast("Scan failed", 'error');
        } finally {
            setIsScanning(false);
        }
    };

    return (
        <div className="p-6 max-w-[1600px] mx-auto animate-fade-in text-slate-200 min-h-screen bg-[#050b14]">
            <div className="mb-8 border-b border-cyan-900/30 pb-6 text-center md:text-left">
                <h2 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500 flex flex-col sm:flex-row items-center justify-center md:justify-start gap-4">
                    <BrainCircuit className="w-10 h-10 text-cyan-400 shrink-0" />
                    Moby v4: Autonomous Organism
                </h2>
                <p className="text-cyan-400/60 mt-2 text-lg font-light tracking-wide">Self-Evolving Business Infrastructure • Quantum State Analysis • Auto-Integration</p>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">

                {/* --- LEFT: QUANTUM CUSTOMER STATE --- */}
                <div className="bg-slate-900/50 border border-cyan-500/20 rounded-2xl p-8 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/5 rounded-full blur-[100px] pointer-events-none"></div>

                    <div className="flex items-center justify-between mb-6">
                        <h3 className="text-xl font-bold text-cyan-100 flex items-center gap-2">
                            <Activity className="w-5 h-5 text-cyan-400" /> Quantum Customer Consciousness
                        </h3>
                        <div className="px-3 py-1 rounded-full bg-cyan-950/50 border border-cyan-500/30 text-xs text-cyan-400 font-mono">
                            STATUS: OBSERVING
                        </div>
                    </div>

                    <div className="mb-6">
                        <label className="text-xs font-bold text-cyan-500/70 uppercase mb-2 block">Context Input Stream</label>
                        <div className="flex flex-col sm:flex-row gap-2">
                            <input
                                value={quantumContext}
                                onChange={e => setQuantumContext(e.target.value)}
                                className="flex-1 bg-slate-950 border border-cyan-900/50 rounded-lg p-3 text-cyan-100 focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 outline-none transition-all font-mono text-sm"
                            />
                            <button
                                onClick={handleQuantumAnalysis}
                                disabled={isAnalyzing}
                                className="w-full sm:w-auto bg-cyan-600/20 hover:bg-cyan-600/40 text-cyan-300 border border-cyan-500/50 px-6 py-3 sm:py-0 rounded-lg font-bold transition-all disabled:opacity-50 flex items-center justify-center"
                            >
                                {isAnalyzing ? <RefreshCw className="w-5 h-5 animate-spin" /> : <Zap className="w-5 h-5" />}
                            </button>
                        </div>
                    </div>

                    <div className="grid gap-4">
                        {quantumStates.length === 0 && !isAnalyzing && (
                            <div className="text-center py-12 text-cyan-500/30 border-2 border-dashed border-cyan-900/30 rounded-xl">
                                <Layers className="w-12 h-12 mx-auto mb-2 opacity-50" />
                                <p>Waiting for waveform collapse...</p>
                            </div>
                        )}
                        {quantumStates.map((state, i) => (
                            <div key={i} className="bg-slate-950/80 border border-cyan-500/20 p-4 rounded-xl hover:border-cyan-500/40 transition-all group/card relative overflow-hidden">
                                <div className={`absolute left-0 top-0 bottom-0 w-1 ${state.status === 'COHERENT' ? 'bg-emerald-500' :
                                        state.status === 'ENTANGLED' ? 'bg-purple-500' : 'bg-amber-500'
                                    }`}></div>
                                <div className="flex justify-between items-start mb-2 pl-3">
                                    <h4 className="font-bold text-cyan-100">{state.dimension}</h4>
                                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${state.status === 'COHERENT' ? 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10' :
                                            state.status === 'ENTANGLED' ? 'text-purple-400 border-purple-500/30 bg-purple-500/10' : 'text-amber-400 border-amber-500/30 bg-amber-500/10'
                                        }`}>{state.status}</span>
                                </div>
                                <div className="pl-3">
                                    <div className="flex items-center gap-2 text-xs text-cyan-500/60 mb-2 font-mono">
                                        Probability: {(state.probability * 100).toFixed(1)}%
                                        <div className="flex-1 h-1 bg-cyan-900/30 rounded-full overflow-hidden">
                                            <div className="h-full bg-cyan-500/50" style={{ width: `${state.probability * 100}%` }}></div>
                                        </div>
                                    </div>
                                    <p className="text-sm text-cyan-200/80 leading-relaxed">{state.insight}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* --- RIGHT: INTEGRATION SPIDER --- */}
                <div className="bg-slate-900/50 border border-indigo-500/20 rounded-2xl p-8 relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-96 h-96 bg-indigo-500/5 rounded-full blur-[100px] pointer-events-none"></div>

                    <div className="flex items-center justify-between mb-6">
                        <h3 className="text-xl font-bold text-indigo-100 flex items-center gap-2">
                            <Network className="w-5 h-5 text-indigo-400" /> Autonomous Integration Spider
                        </h3>
                        <div className="px-3 py-1 rounded-full bg-indigo-950/50 border border-indigo-500/30 text-xs text-indigo-400 font-mono">
                            MODE: HUNTER
                        </div>
                    </div>

                    <div className="mb-6">
                        <label className="text-xs font-bold text-indigo-500/70 uppercase mb-2 block">Target Ecosystem / Domain</label>
                        <div className="flex flex-col sm:flex-row gap-2">
                            <input
                                value={targetDomain}
                                onChange={e => setTargetDomain(e.target.value)}
                                placeholder="e.g. company.com"
                                className="flex-1 bg-slate-950 border border-indigo-900/50 rounded-lg p-3 text-indigo-100 focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50 outline-none transition-all font-mono text-sm"
                            />
                            <button
                                onClick={handleScan}
                                disabled={isScanning || !targetDomain}
                                className="w-full sm:w-auto bg-indigo-600/20 hover:bg-indigo-600/40 text-indigo-300 border border-indigo-500/50 px-6 py-3 sm:py-0 rounded-lg font-bold transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                            >
                                {isScanning ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Share2 className="w-4 h-4" />}
                                Scan
                            </button>
                        </div>
                    </div>

                    <div className="space-y-3">
                        {integrations.length === 0 && !isScanning && (
                            <div className="text-center py-12 text-indigo-500/30 border-2 border-dashed border-indigo-900/30 rounded-xl">
                                <Globe className="w-12 h-12 mx-auto mb-2 opacity-50" />
                                <p>Target a domain to map endpoints.</p>
                            </div>
                        )}
                        {integrations.map((int, i) => (
                            <div key={int.id} className="bg-slate-950 border border-indigo-500/10 p-4 rounded-xl flex items-center justify-between group hover:border-indigo-500/40 transition-all">
                                <div className="flex items-center gap-4">
                                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center border ${int.type === 'API' ? 'bg-blue-500/10 border-blue-500/20 text-blue-400' :
                                            int.type === 'WEBHOOK' ? 'bg-pink-500/10 border-pink-500/20 text-pink-400' : 'bg-amber-500/10 border-amber-500/20 text-amber-400'
                                        }`}>
                                        {int.type === 'API' ? <Zap className="w-5 h-5" /> : int.type === 'WEBHOOK' ? <Share2 className="w-5 h-5" /> : <Lock className="w-5 h-5" />}
                                    </div>
                                    <div>
                                        <h4 className="font-bold text-indigo-100">{int.platform}</h4>
                                        <p className="text-xs text-indigo-400/60">{int.potentialImpact}</p>
                                    </div>
                                </div>
                                <div className="flex items-center gap-3">
                                    <span className="text-[10px] font-mono text-indigo-500 uppercase tracking-wider">{int.type}</span>
                                    <button className="w-8 h-8 rounded-full bg-indigo-500/10 flex items-center justify-center text-indigo-400 hover:bg-indigo-500 hover:text-white transition-colors">
                                        <ChevronRight className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

            </div>
        </div>
    );
};

export default MobyAutonomousAgent;
