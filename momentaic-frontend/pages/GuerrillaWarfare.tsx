import React, { useState, useEffect } from 'react';
import { PageMeta } from '../components/ui/PageMeta';
import { Crosshair, Search, Zap, Activity, AlertTriangle, ShieldAlert, Cpu } from 'lucide-react';
import { Button } from '../components/ui/Button';

export default function GuerrillaWarfare() {
    const [scanActive, setScanActive] = useState(false);
    const [competitorUrl, setCompetitorUrl] = useState('');
    const [intelItems, setIntelItems] = useState<any[]>([]);

    const initiateScan = () => {
        if (!competitorUrl) return;
        setScanActive(true);
        setIntelItems([]);

        // Simulate a cyber-scan finding vulnerabilities
        setTimeout(() => {
            setIntelItems(prev => [...prev, {
                type: 'PRICING_CHANGE',
                message: 'Pricing update detected: Competitor increased enterprise tier by 15%.',
                severity: 'high',
                time: new Date().toLocaleTimeString()
            }]);
        }, 3000);

        setTimeout(() => {
            setIntelItems(prev => [...prev, {
                type: 'NEGATIVE_REVIEWS',
                message: 'Sentiment shift: 43 angry Reddit posts concerning recent feature removal.',
                severity: 'critical',
                time: new Date().toLocaleTimeString()
            }]);
        }, 6000);

        setTimeout(() => {
            setIntelItems(prev => [...prev, {
                type: 'SERVER_OUTAGE',
                message: 'Uptime Protocol: Competitor API latency spiked 400% over the last hour.',
                severity: 'medium',
                time: new Date().toLocaleTimeString()
            }]);
            setScanActive(false);
        }, 9000);
    };

    return (
        <div className="max-w-6xl mx-auto pb-20 mt-8 min-h-screen">
            <PageMeta title="Guerrilla Mode | MomentAIc" description="Execute asymmetric attacks and extract competitor intelligence." />

            {/* Header */}
            <div className="mb-12 border-b border-red-500/20 pb-8">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-red-500/30 bg-red-500/10 text-red-400 font-mono text-xs mb-4">
                    <Crosshair className="w-3 h-3 animate-pulse" /> GUERRILLA_WARFARE_MODE_ACTIVE
                </div>
                <h1 className="text-4xl md:text-5xl font-black text-white mb-4 tracking-tighter uppercase relative group">
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-600 to-orange-500 drop-shadow-[0_0_15px_rgba(220,38,38,0.8)]">
                        Asymmetric Warfare
                    </span>
                </h1>
                <p className="text-gray-400 font-mono text-sm max-w-2xl border-l-2 border-red-500 pl-4">
                    Intercept competitor telemetry, monitor their frustrated user-base, and auto-deploy Sales Agents to extract their customers.
                </p>
            </div>

            {/* Target Acquisition */}
            <div className="bg-[#0a0a0f] border border-red-500/30 p-8 rounded-xl relative overflow-hidden mb-8 shadow-[0_0_30px_rgba(220,38,38,0.05)]">
                {/* Background Sonar Effect */}
                {scanActive && (
                    <div className="absolute inset-0 z-0 flex items-center justify-center opacity-20 pointer-events-none">
                        <div className="w-[800px] h-[800px] rounded-full border border-red-500/50 absolute animate-[ping_4s_cubic-bezier(0,0,0.2,1)_infinite]" />
                        <div className="w-[600px] h-[600px] rounded-full border border-red-500/40 absolute animate-[ping_4s_cubic-bezier(0,0,0.2,1)_infinite_1s]" />
                        <div className="w-[400px] h-[400px] rounded-full border border-red-500/30 absolute animate-[ping_4s_cubic-bezier(0,0,0.2,1)_infinite_2s]" />
                        <div className="w-1 h-full bg-red-500/30 absolute animate-[spin_4s_linear_infinite]" />
                    </div>
                )}

                <div className="relative z-10 max-w-2xl">
                    <h3 className="text-xl font-bold font-mono text-white mb-4 flex items-center gap-3">
                        <Search className="text-red-500" />
                        Target Acquisition Protocol
                    </h3>
                    <div className="flex gap-4">
                        <input
                            type="text"
                            placeholder="Enter Competitor Domain (e.g. competitor.com)"
                            className="flex-1 bg-black/50 border border-red-500/50 rounded-lg px-4 py-3 text-white font-mono focus:outline-none focus:border-red-400 focus:ring-1 focus:ring-red-400 placeholder:text-red-900/50"
                            value={competitorUrl}
                            onChange={(e) => setCompetitorUrl(e.target.value)}
                            disabled={scanActive}
                        />
                        <button
                            onClick={initiateScan}
                            disabled={scanActive || !competitorUrl}
                            className="px-8 py-3 bg-red-600 hover:bg-red-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold font-mono text-sm rounded shadow-[0_0_15px_rgba(220,38,38,0.5)] transition-all flex items-center gap-2"
                        >
                            {scanActive ? <Cpu className="w-4 h-4 animate-spin" /> : <Crosshair className="w-4 h-4" />}
                            {scanActive ? 'SCANNING...' : 'INITIATE SWEEP'}
                        </button>
                    </div>
                </div>
            </div>

            {/* Intelligence Feed */}
            <div className="space-y-4">
                <h3 className="text-lg font-bold font-mono text-gray-400 mb-6 flex items-center gap-2">
                    <Activity className="w-5 h-5 text-gray-500" />
                    Live Interception Feed
                </h3>

                {intelItems.length === 0 && !scanActive ? (
                    <div className="p-8 border border-white/5 border-dashed rounded-lg bg-white/[0.02] text-center">
                        <p className="font-mono text-gray-600 text-sm">Awaiting target designation.</p>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {intelItems.map((item, idx) => (
                            <div key={idx} className="bg-black border border-red-500/20 rounded-lg p-5 flex items-start gap-4 animate-in fade-in slide-in-from-bottom-4">
                                <div className={`p-3 rounded-lg ${item.severity === 'critical' ? 'bg-red-500/20 text-red-500' :
                                        item.severity === 'high' ? 'bg-orange-500/20 text-orange-500' :
                                            'bg-yellow-500/20 text-yellow-500'
                                    }`}>
                                    {item.severity === 'critical' ? <ShieldAlert className="w-6 h-6" /> : <AlertTriangle className="w-6 h-6" />}
                                </div>
                                <div className="flex-1">
                                    <div className="flex items-center justify-between mb-1">
                                        <span className={`font-mono text-xs font-bold leading-none ${item.severity === 'critical' ? 'text-red-400' :
                                                item.severity === 'high' ? 'text-orange-400' :
                                                    'text-yellow-400'
                                            }`}>
                                            [{item.type}]
                                        </span>
                                        <span className="text-gray-600 font-mono text-xs">{item.time}</span>
                                    </div>
                                    <p className="text-gray-300 font-mono text-sm">{item.message}</p>

                                    <div className="mt-4 flex gap-3">
                                        <button className="px-4 py-1.5 bg-red-900/40 hover:bg-red-900/60 border border-red-500/50 text-red-300 font-mono text-xs rounded transition-colors flex items-center gap-2">
                                            <Zap className="w-3 h-3" /> DEPLOY EXTRACTOR AGENT
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                        {scanActive && (
                            <div className="p-8 border border-red-500/20 border-dashed rounded-lg bg-red-900/5 text-center">
                                <div className="flex items-center justify-center gap-3">
                                    <div className="w-2 h-2 bg-red-500 rounded-full animate-ping" />
                                    <span className="font-mono text-red-500 text-sm">DECRYPTING TELEMETRY STREAMS...</span>
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
