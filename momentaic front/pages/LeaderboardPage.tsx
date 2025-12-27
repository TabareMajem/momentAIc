import React, { useState, useEffect } from 'react';
import { TrendingUp, Trophy, Star, Zap, Globe, Users, BarChart3, Award, ArrowUp, Filter } from 'lucide-react';
import { api } from '../lib/api';

interface LeaderboardEntry {
    rank: number;
    startup_id: string;
    name: string;
    tagline: string;
    traction_score: number;
    tier: string;
    verified: boolean;
    category: string;
    public_metrics: {
        mrr?: number;
        users?: number;
        growth?: number;
    };
    integrations_connected: number;
}

const TIERS = {
    rocket: { color: 'from-purple-500 to-pink-500', icon: '🚀', label: 'Rocket' },
    scaling: { color: 'from-blue-500 to-cyan-500', icon: '📈', label: 'Scaling' },
    rising: { color: 'from-green-500 to-emerald-500', icon: '🌱', label: 'Rising' },
    building: { color: 'from-yellow-500 to-orange-500', icon: '🔨', label: 'Building' },
    ideation: { color: 'from-gray-500 to-gray-600', icon: '💡', label: 'Ideation' },
};

const CATEGORIES = ['all', 'saas', 'fintech', 'health', 'ai', 'ecommerce', 'marketplace'];

export default function LeaderboardPage() {
    const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
    const [loading, setLoading] = useState(true);
    const [category, setCategory] = useState('all');
    const [timePeriod, setTimePeriod] = useState<'week' | 'month' | 'all'>('all');

    useEffect(() => {
        fetchLeaderboard();
    }, [category, timePeriod]);



    const fetchLeaderboard = async () => {
        setLoading(true);
        try {
            const response = await api.getLeaderboard({
                category: category !== 'all' ? category : undefined,
                time_period: timePeriod
            });
            setLeaderboard(response.leaderboard || []);
        } catch (error) {
            console.error("Failed to fetch leaderboard", error);
        } finally {
            setLoading(false);
        }
    };

    const getTierInfo = (tier: string) => TIERS[tier as keyof typeof TIERS] || TIERS.ideation;

    const formatMetric = (value: number | undefined, prefix = '') => {
        if (!value) return '-';
        if (value >= 1000000) return `${prefix}${(value / 1000000).toFixed(1)}M`;
        if (value >= 1000) return `${prefix}${(value / 1000).toFixed(1)}K`;
        return `${prefix}${value}`;
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900/20 to-gray-900 p-6">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <div className="flex items-center gap-3 mb-2">
                        <Trophy className="w-8 h-8 text-yellow-500" />
                        <h1 className="text-3xl font-bold text-white">Founder Leaderboard</h1>
                    </div>
                    <p className="text-gray-400">
                        <span className="text-purple-400 font-semibold">No pedigree. No BS.</span> Pure performance ranking based on real traction metrics.
                    </p>
                </div>

                {/* Anti-YC Banner */}
                <div className="mb-8 p-6 bg-gradient-to-r from-purple-900/40 via-blue-900/40 to-cyan-900/40 border border-purple-500/30 rounded-2xl">
                    <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                        <div>
                            <h3 className="text-xl font-bold text-white mb-1">🏆 The Anti-YC Leaderboard</h3>
                            <p className="text-gray-300 text-sm">Ranked by metrics, not by where you went to school. Show, don't tell.</p>
                        </div>
                        <div className="flex gap-3">
                            <div className="px-4 py-2 bg-green-500/20 rounded-full text-green-400 text-sm font-medium">
                                ✓ Verified Metrics
                            </div>
                            <div className="px-4 py-2 bg-blue-500/20 rounded-full text-blue-400 text-sm font-medium">
                                ✓ Public Rankings
                            </div>
                        </div>
                    </div>
                </div>

                {/* Filters */}
                <div className="flex flex-wrap gap-4 mb-8">
                    <div className="flex items-center gap-2 bg-gray-800/50 rounded-xl p-1">
                        {['week', 'month', 'all'].map((period) => (
                            <button
                                key={period}
                                onClick={() => setTimePeriod(period as 'week' | 'month' | 'all')}
                                className={`px-4 py-2 rounded-lg text-sm font-medium transition ${timePeriod === period
                                    ? 'bg-purple-600 text-white'
                                    : 'text-gray-400 hover:text-white'
                                    }`}
                            >
                                {period === 'all' ? 'All Time' : period.charAt(0).toUpperCase() + period.slice(1)}
                            </button>
                        ))}
                    </div>
                    <select
                        value={category}
                        onChange={(e) => setCategory(e.target.value)}
                        className="px-4 py-2 bg-gray-800/50 border border-gray-700 rounded-xl text-white text-sm"
                    >
                        {CATEGORIES.map((cat) => (
                            <option key={cat} value={cat}>
                                {cat === 'all' ? 'All Categories' : cat.charAt(0).toUpperCase() + cat.slice(1)}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Leaderboard Table */}
                <div className="bg-gray-800/30 rounded-2xl border border-gray-700/50 overflow-hidden">
                    {/* Header */}
                    <div className="grid grid-cols-12 gap-4 p-4 bg-gray-800/50 text-xs font-mono text-gray-500 uppercase tracking-wider">
                        <div className="col-span-1">Rank</div>
                        <div className="col-span-4">Startup</div>
                        <div className="col-span-2 text-center">Score</div>
                        <div className="col-span-2 text-center">MRR</div>
                        <div className="col-span-1 text-center">Growth</div>
                        <div className="col-span-2 text-center">Status</div>
                    </div>

                    {/* Rows */}
                    {loading ? (
                        <div className="p-12 text-center text-gray-500">Loading rankings...</div>
                    ) : (
                        leaderboard.map((entry) => {
                            const tierInfo = getTierInfo(entry.tier);
                            return (
                                <div
                                    key={entry.startup_id}
                                    className="grid grid-cols-12 gap-4 p-4 border-t border-gray-700/30 hover:bg-gray-800/30 transition cursor-pointer"
                                >
                                    {/* Rank */}
                                    <div className="col-span-1 flex items-center">
                                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${entry.rank === 1 ? 'bg-yellow-500 text-black' :
                                            entry.rank === 2 ? 'bg-gray-400 text-black' :
                                                entry.rank === 3 ? 'bg-orange-500 text-black' :
                                                    'bg-gray-700 text-gray-300'
                                            }`}>
                                            {entry.rank}
                                        </div>
                                    </div>

                                    {/* Startup Info */}
                                    <div className="col-span-4">
                                        <div className="flex items-center gap-2">
                                            <span className="text-white font-semibold">{entry.name}</span>
                                            {entry.verified && (
                                                <span className="text-green-400 text-xs">✓</span>
                                            )}
                                            <span className="text-lg">{tierInfo.icon}</span>
                                        </div>
                                        <p className="text-gray-500 text-sm truncate">{entry.tagline}</p>
                                    </div>

                                    {/* Score */}
                                    <div className="col-span-2 flex items-center justify-center">
                                        <div className={`px-3 py-1 rounded-full bg-gradient-to-r ${tierInfo.color} text-white font-bold text-sm`}>
                                            {entry.traction_score}
                                        </div>
                                    </div>

                                    {/* MRR */}
                                    <div className="col-span-2 flex items-center justify-center">
                                        <span className="text-white font-medium">
                                            {formatMetric(entry.public_metrics.mrr, '$')}
                                        </span>
                                    </div>

                                    {/* Growth */}
                                    <div className="col-span-1 flex items-center justify-center">
                                        <span className="text-green-400 flex items-center gap-1">
                                            <ArrowUp className="w-3 h-3" />
                                            {entry.public_metrics.growth}%
                                        </span>
                                    </div>

                                    {/* Status */}
                                    <div className="col-span-2 flex items-center justify-center gap-2">
                                        <span className={`px-2 py-1 rounded text-xs ${tierInfo.color} bg-gradient-to-r text-white`}>
                                            {tierInfo.label}
                                        </span>
                                        <span className="text-gray-500 text-xs">
                                            {entry.integrations_connected} 🔌
                                        </span>
                                    </div>
                                </div>
                            );
                        })
                    )}
                </div>

                {/* CTA */}
                <div className="mt-12 p-8 bg-gradient-to-r from-green-900/30 to-emerald-900/30 border border-green-500/30 rounded-2xl text-center">
                    <h3 className="text-2xl font-bold text-white mb-3">Ready to Rank? 🚀</h3>
                    <p className="text-gray-300 mb-6 max-w-xl mx-auto">
                        Connect your integrations, build in public, and let your metrics speak for themselves.
                        No application process. No gatekeeping.
                    </p>
                    <div className="flex flex-wrap justify-center gap-4">
                        <button className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-bold rounded-xl transition">
                            Join the Leaderboard
                        </button>
                        <button className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white font-medium rounded-xl transition">
                            How Scoring Works
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
