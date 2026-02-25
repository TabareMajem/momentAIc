import React, { useEffect, useState } from 'react';
import { Target, TrendingUp, Sparkles, AlertCircle } from 'lucide-react';
import { api } from '../../lib/api';
import { useChatStore } from '../../stores/chat-store';

export function BenchmarkWidget() {
    const { currentStartupId } = useChatStore();
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!currentStartupId) return;

        async function loadBenchmarks() {
            try {
                setLoading(true);
                const res = await api.getBenchmarks(currentStartupId!);
                setData(res);
            } catch (e) {
                console.error("Failed to load benchmarks", e);
            } finally {
                setLoading(false);
            }
        }
        loadBenchmarks();
    }, [currentStartupId]);

    if (!currentStartupId || loading) {
        return (
            <div className="bg-[#050505] border border-white/5 rounded-xl p-4 h-48 animate-pulse flex flex-col justify-center items-center">
                <Target className="w-8 h-8 text-gray-700 mb-2" />
                <span className="text-xs text-gray-600 font-mono">Calibrating against Moat Matrix...</span>
            </div>
        );
    }

    if (!data?.benchmarks || Object.keys(data.benchmarks).length === 0) {
        return (
            <div className="bg-[#050505] border border-white/5 rounded-xl p-4 h-48 flex flex-col justify-center items-center text-center">
                <AlertCircle className="w-6 h-6 text-yellow-500 mb-2" />
                <h3 className="text-sm font-bold text-white">Insufficient Data</h3>
                <p className="text-xs text-gray-500 max-w-[200px] mt-1">Need more {data?.industry || 'industry'} peers to calculate percentiles.</p>
            </div>
        );
    }

    const { industry, benchmarks, current_metrics, peer_count } = data;

    const getMetricLabel = (key: string) => {
        const labels: Record<string, string> = {
            mrr: "Monthly Recurring Rev",
            cac: "Customer Acq Cost",
            ltv: "Lifetime Value",
            retention_rate: "Retention %",
            dau: "Daily Active Users"
        };
        return labels[key] || key.toUpperCase();
    };

    const getBarColor = (current: number, median: number, top10: number, key: string) => {
        // For CAC lower is better, for others higher is better
        const lowerIsBetter = key === 'cac';
        if (lowerIsBetter) {
            if (current <= top10) return "bg-[#00f0ff]"; // Top 10%
            if (current <= median) return "bg-emerald-500"; // Top 50%
            return "bg-amber-500"; // Bottom 50%
        } else {
            if (current >= top10) return "bg-[#00f0ff]"; // Top 10%
            if (current >= median) return "bg-emerald-500"; // Top 50%
            return "bg-amber-500"; // Bottom 50%
        }
    };

    const getPercentage = (current: number, top10: number, key: string) => {
        // Normalize to a 0-100 scale for the bar chart
        const lowerIsBetter = key === 'cac';
        if (lowerIsBetter) {
            // If top10 is 45, and current is 90 (worse), we want bar to be shorter
            // Max bound let's say is top10 * 4
            const worst = top10 * 4;
            const pct = Math.max(0, Math.min(100, 100 - ((current / worst) * 100)));
            return pct + "%";
        } else {
            // Normal: higher is better
            const pct = Math.min(100, (current / top10) * 100);
            return pct + "%";
        }
    };

    return (
        <div className="bg-[#050505] border border-white/10 rounded-xl p-5 shadow-lg group hover:border-[#bf25eb]/30 transition-colors">
            <div className="flex justify-between items-start mb-6">
                <div>
                    <h3 className="text-sm font-bold text-white flex items-center gap-2">
                        <Target className="w-4 h-4 text-[#bf25eb]" />
                        COMPETITIVE BENCHMARKS
                    </h3>
                    <p className="text-[10px] text-gray-500 font-mono mt-1 uppercase">Vs. {peer_count} {industry} Startups</p>
                </div>
                <div className="p-1.5 bg-[#bf25eb]/10 rounded-lg">
                    <TrendingUp className="w-4 h-4 text-[#bf25eb]" />
                </div>
            </div>

            <div className="space-y-4">
                {Object.entries(benchmarks).slice(0, 3).map(([key, bench]: [string, any]) => {
                    const current = current_metrics[key] || 0;
                    const barColor = getBarColor(current, bench.median, bench.top_10, key);
                    const width = getPercentage(current, bench.top_10, key);

                    return (
                        <div key={key}>
                            <div className="flex justify-between text-xs mb-1">
                                <span className="text-gray-300 font-medium">{getMetricLabel(key)}</span>
                                <span className="text-white font-mono flex items-center gap-2">
                                    {current > 0 ? (
                                        key === 'mrr' || key === 'cac' || key === 'ltv' ? `$${current}` : current
                                    ) : '---'}
                                    {current >= bench.top_10 && key !== 'cac' && <Sparkles className="w-3 h-3 text-[#00f0ff]" />}
                                    {current <= bench.top_10 && key === 'cac' && <Sparkles className="w-3 h-3 text-[#00f0ff]" />}
                                </span>
                            </div>

                            <div className="relative h-2 bg-black/50 rounded-full overflow-hidden border border-white/5">
                                <div
                                    className={`absolute top-0 left-0 h-full ${barColor} rounded-full`}
                                    style={{ width }}
                                />
                                {/* Median Marker */}
                                <div
                                    className="absolute top-0 bottom-0 w-px bg-white/50 z-10 hover:bg-white hover:w-0.5 transition-all"
                                    style={{ left: getPercentage(bench.median, bench.top_10, key) }}
                                    title={`Median: ${bench.median}`}
                                />
                                {/* Top 10 Marker */}
                                <div
                                    className="absolute top-0 bottom-0 w-px bg-[#00f0ff]/50 z-10 hover:bg-[#00f0ff] hover:w-0.5 transition-all shadow-[0_0_5px_rgba(0,240,255,0.5)]"
                                    style={{ left: getPercentage(bench.top_10, bench.top_10, key) }}
                                    title={`Top 10%: ${bench.top_10}`}
                                />
                            </div>
                            <div className="flex justify-between text-[8px] text-gray-600 font-mono mt-1 uppercase">
                                <span>You</span>
                                <span>Top 10%</span>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
