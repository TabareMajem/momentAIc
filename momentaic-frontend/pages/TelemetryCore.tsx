import React, { useState } from 'react';
import { PageMeta } from '../components/ui/PageMeta';
import { Activity, Users, ShieldAlert, Bot, TrendingUp, TrendingDown, ArrowRight, Zap, RefreshCw } from 'lucide-react';
import { useToast } from '../components/ui/Toast';

export default function TelemetryCore() {
    const { toast } = useToast();
    const [deploying, setDeploying] = useState<string | null>(null);

    const handleDeploy = (agentName: string) => {
        setDeploying(agentName);
        toast({ type: 'info', title: `DEPLOYING ${agentName.toUpperCase()}`, message: 'Swarm initializing...' });

        setTimeout(() => {
            toast({ type: 'success', title: 'SWARM ACTIVE', message: `${agentName} is now infiltrating target cohort.` });
            setDeploying(null);
        }, 3000);
    };

    return (
        <div className="max-w-7xl mx-auto pb-20 mt-8 min-h-screen">
            <PageMeta title="Telemetry Core | MomentAIc" description="Review real-time cohort analytics and dispatch agent interventions." />

            {/* Header */}
            <div className="mb-12 border-b border-[#00f0ff]/20 pb-8">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-[#00f0ff]/30 bg-[#00f0ff]/10 text-[#00f0ff] font-mono text-xs mb-4">
                    <Activity className="w-3 h-3 animate-pulse" /> TELEMETRY_MATRIX_ONLINE
                </div>
                <h1 className="text-4xl md:text-5xl font-black text-white mb-4 tracking-tighter uppercase relative group">
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#00f0ff] to-purple-500 drop-shadow-[0_0_15px_rgba(0,240,255,0.8)]">
                        Cohort Intelligence
                    </span>
                </h1>
                <p className="text-gray-400 font-mono text-sm max-w-2xl border-l-2 border-[#00f0ff] pl-4">
                    Monitor real-time user retention and identify funnel leakages. When a cohort drops off, immediately dispatch an AI Swarm to extract feedback or re-engage the target.
                </p>
            </div>

            {/* Top Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                <div className="bg-[#0a0a0f] border border-white/10 p-6 rounded-xl relative overflow-hidden group hover:border-[#00f0ff]/50 transition-colors">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-[#00f0ff]/5 rounded-bl-[100px] -z-10 group-hover:bg-[#00f0ff]/10 transition-colors" />
                    <div className="text-gray-500 font-mono text-xs uppercase mb-2 flex flex-col gap-1">
                        Active Cohort Size <span className="text-emerald-500 flex items-center gap-1"><TrendingUp className="w-3 h-3" /> +14% (W/W)</span>
                    </div>
                    <div className="text-4xl font-black text-white">2,841</div>
                </div>

                <div className="bg-[#0a0a0f] border border-white/10 p-6 rounded-xl relative overflow-hidden group hover:border-purple-500/50 transition-colors">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/5 rounded-bl-[100px] -z-10 group-hover:bg-purple-500/10 transition-colors" />
                    <div className="text-gray-500 font-mono text-xs uppercase mb-2 flex flex-col gap-1">
                        Day 7 Retention <span className="text-red-500 flex items-center gap-1"><TrendingDown className="w-3 h-3" /> -2.4% (W/W)</span>
                    </div>
                    <div className="text-4xl font-black text-white">41.2%</div>
                </div>

                <div className="bg-[#0a0a0f] border border-red-500/30 p-6 rounded-xl relative overflow-hidden group shadow-[inset_0_0_20px_rgba(239,68,68,0.05)]">
                    <div className="absolute top-0 right-0 p-4 opacity-50">
                        <ShieldAlert className="w-16 h-16 text-red-500/10" />
                    </div>
                    <div className="text-red-400 font-mono text-xs uppercase mb-2 flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                        CRITICAL_LEAK_DETECTED
                    </div>
                    <div className="text-xl font-medium text-white mb-1">Onboarding Drop-off</div>
                    <div className="text-sm font-mono text-gray-400">Step 3 (Payment) losing 68% volume.</div>

                    <button
                        onClick={() => handleDeploy('Onboarding Coach')}
                        disabled={deploying === 'Onboarding Coach'}
                        className="mt-4 w-full py-2 bg-red-900/40 hover:bg-red-900/80 border border-red-500/50 text-red-300 font-mono text-xs rounded transition-colors flex justify-center items-center gap-2"
                    >
                        {deploying === 'Onboarding Coach' ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Bot className="w-4 h-4" />}
                        {deploying === 'Onboarding Coach' ? 'DEPLOYING...' : 'DEPLOY RECOVERY SWARM'}
                    </button>
                </div>
            </div>

            {/* Cohort Matrix */}
            <div className="bg-[#0a0a0f] border border-white/10 rounded-xl overflow-hidden mb-8">
                <div className="px-6 py-4 border-b border-white/10 flex items-center justify-between">
                    <h3 className="font-mono text-sm uppercase text-gray-400 font-bold flex items-center gap-2">
                        <Users className="w-4 h-4 text-[#00f0ff]" />
                        Retention Matrix // LAST 4 WEEKS
                    </h3>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-left font-mono text-sm">
                        <thead className="bg-black/50 text-gray-500 text-xs uppercase bg-white/5 border-b border-white/5">
                            <tr>
                                <th className="px-6 py-4 font-normal">Cohort Setup</th>
                                <th className="px-6 py-4 font-normal">Size</th>
                                <th className="px-6 py-4 font-normal text-center">Day 1</th>
                                <th className="px-6 py-4 font-normal text-center">Day 3</th>
                                <th className="px-6 py-4 font-normal text-center">Day 7</th>
                                <th className="px-6 py-4 font-normal text-center">Day 14</th>
                                <th className="px-6 py-4 font-normal text-center">Intervention</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5 text-gray-300">
                            <tr className="hover:bg-white/5 transition-colors">
                                <td className="px-6 py-4 font-bold text-white">Feb 12 - Feb 18</td>
                                <td className="px-6 py-4 text-gray-500">842</td>
                                <td className="px-6 py-4 text-center bg-[#00f0ff]/30 text-[#00f0ff] font-bold border-l border-black">100%</td>
                                <td className="px-6 py-4 text-center bg-[#00f0ff]/20 text-white border-l border-black">78%</td>
                                <td className="px-6 py-4 text-center bg-[#00f0ff]/10 text-gray-400 border-l border-black">--</td>
                                <td className="px-6 py-4 text-center bg-transparent border-l border-black">--</td>
                                <td className="px-6 py-4 text-center border-l border-black">
                                    <span className="text-gray-600 text-xs">Monitoring...</span>
                                </td>
                            </tr>
                            <tr className="hover:bg-white/5 transition-colors">
                                <td className="px-6 py-4 font-bold text-white">Feb 05 - Feb 11</td>
                                <td className="px-6 py-4 text-gray-500">719</td>
                                <td className="px-6 py-4 text-center bg-purple-500/30 text-purple-300 font-bold border-l border-black">100%</td>
                                <td className="px-6 py-4 text-center bg-purple-500/20 text-white border-l border-black">62%</td>
                                <td className="px-6 py-4 text-center bg-red-500/30 text-red-300 font-bold border-l border-black">28%</td>
                                <td className="px-6 py-4 text-center bg-transparent border-l border-black">--</td>
                                <td className="px-6 py-4 text-center border-l border-black">
                                    <button
                                        onClick={() => handleDeploy('Churn Analyst')}
                                        disabled={deploying === 'Churn Analyst'}
                                        className="inline-flex items-center gap-2 px-3 py-1 bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 text-red-400 rounded transition-colors uppercase text-[10px] font-bold"
                                    >
                                        <Zap className="w-3 h-3" />
                                        {deploying === 'Churn Analyst' ? 'DEPLOYING' : 'INVESTIGATE D7'}
                                    </button>
                                </td>
                            </tr>
                            <tr className="hover:bg-white/5 transition-colors">
                                <td className="px-6 py-4 font-bold text-white">Jan 29 - Feb 04</td>
                                <td className="px-6 py-4 text-gray-500">902</td>
                                <td className="px-6 py-4 text-center bg-purple-500/30 text-purple-300 font-bold border-l border-black">100%</td>
                                <td className="px-6 py-4 text-center bg-purple-500/20 text-white border-l border-black">71%</td>
                                <td className="px-6 py-4 text-center bg-purple-500/10 text-gray-300 border-l border-black">45%</td>
                                <td className="px-6 py-4 text-center bg-purple-500/5 text-gray-400 border-l border-black">32%</td>
                                <td className="px-6 py-4 text-center text-emerald-500 text-xs border-l border-black">
                                    <span className="flex items-center justify-center gap-1">✓ Stable</span>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

        </div>
    );
}
