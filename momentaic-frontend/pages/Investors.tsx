import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Network, Activity, Cpu, Percent, ChevronRight, Zap, Target, TrendingUp, Users } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';

const mockSignalData = [
    { name: 'Q1', pedigreeIndex: 1.2, executionAlpha: 1.5, pmf: 60 },
    { name: 'Q2', pedigreeIndex: 1.1, executionAlpha: 1.8, pmf: 68 },
    { name: 'Q3', pedigreeIndex: 0.9, executionAlpha: 2.4, pmf: 75 },
    { name: 'Q4', pedigreeIndex: 0.85, executionAlpha: 3.1, pmf: 86 },
    { name: 'Q1(New)', pedigreeIndex: 0.65, executionAlpha: 4.2, pmf: 94 },
];

export default function InvestorsPage() {
    return (
        <div className="space-y-8 animate-fade-in pb-20">

            {/* Header Section */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                        The Algorithm of Alpha
                    </h1>
                    <p className="text-gray-400 mt-1 max-w-2xl">
                        Genesis Fund I: Deconstructing the "Pedigree Paradox" with real-time quantitative execution tracking.
                        Where AI builds, AI invests.
                    </p>
                </div>
                <div className="flex items-center gap-3 bg-black/40 border border-green-500/20 px-4 py-2 rounded-lg">
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                    <span className="text-green-500 font-mono text-sm">Signal Engine: ACTIVE</span>
                </div>
            </div>

            {/* Hero Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card className="bg-[#0a0a0f] border-purple-500/20 shadow-[0_0_15px_rgba(168,85,247,0.1)] relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-1 h-full bg-purple-500" />
                    <CardContent className="p-6">
                        <div className="flex justify-between items-start">
                            <div>
                                <p className="text-sm font-medium text-purple-400">Fund IRR</p>
                                <h3 className="text-3xl font-bold text-white mt-1">28.4%</h3>
                            </div>
                            <div className="p-2 bg-purple-500/10 rounded-lg">
                                <TrendingUp className="w-5 h-5 text-purple-400" />
                            </div>
                        </div>
                        <p className="text-xs text-gray-500 mt-2">+12.1% Alpha vs Top Quartile VC</p>
                    </CardContent>
                </Card>

                <Card className="bg-[#0a0a0f] border-blue-500/20 shadow-[0_0_15px_rgba(59,130,246,0.1)] relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-1 h-full bg-blue-500" />
                    <CardContent className="p-6">
                        <div className="flex justify-between items-start">
                            <div>
                                <p className="text-sm font-medium text-blue-400">TVPI Multiple</p>
                                <h3 className="text-3xl font-bold text-white mt-1">2.1x</h3>
                            </div>
                            <div className="p-2 bg-blue-500/10 rounded-lg">
                                <Activity className="w-5 h-5 text-blue-400" />
                            </div>
                        </div>
                        <p className="text-xs text-gray-500 mt-2">$47.2M Target Value on $32.8M</p>
                    </CardContent>
                </Card>

                <Card className="bg-[#0a0a0f] border-red-500/20 shadow-[0_0_15px_rgba(239,68,68,0.1)] relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-1 h-full bg-red-500" />
                    <CardContent className="p-6">
                        <div className="flex justify-between items-start">
                            <div>
                                <p className="text-sm font-medium text-red-400">US Pedigree (ROP)</p>
                                <h3 className="text-3xl font-bold text-white mt-1">0.65</h3>
                            </div>
                            <div className="p-2 bg-red-500/10 rounded-lg">
                                <Percent className="w-5 h-5 text-red-500" />
                            </div>
                        </div>
                        <p className="text-xs text-red-500 mt-2">DANGER: Systematic Overpricing</p>
                    </CardContent>
                </Card>

                <Card className="bg-[#0a0a0f] border-green-500/20 shadow-[0_0_15px_rgba(34,197,94,0.1)] relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-1 h-full bg-green-500" />
                    <CardContent className="p-6">
                        <div className="flex justify-between items-start">
                            <div>
                                <p className="text-sm font-medium text-green-400">Immigrant ROP</p>
                                <h3 className="text-3xl font-bold text-white mt-1">1.85</h3>
                            </div>
                            <div className="p-2 bg-green-500/10 rounded-lg">
                                <Network className="w-5 h-5 text-green-400" />
                            </div>
                        </div>
                        <p className="text-xs text-green-500 mt-2">ALPHA: Homophily Arbitrage detected</p>
                    </CardContent>
                </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                {/* Main Chart */}
                <Card className="lg:col-span-2 bg-[#0a0a0f] border-white/5">
                    <CardHeader>
                        <CardTitle className="text-lg flex items-center gap-2">
                            <Activity className="w-5 h-5 text-blue-400" />
                            Execution vs. Pedigree Signal Over Time
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="h-[300px] w-full mt-4">
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={mockSignalData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                                    <defs>
                                        <linearGradient id="colorExecution" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                        </linearGradient>
                                        <linearGradient id="colorPedigree" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#222" vertical={false} />
                                    <XAxis dataKey="name" stroke="#666" tickLine={false} axisLine={false} />
                                    <YAxis stroke="#666" tickLine={false} axisLine={false} />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#111', border: '1px solid #333', borderRadius: '8px' }}
                                        itemStyle={{ color: '#fff' }}
                                    />
                                    <Area type="monotone" dataKey="executionAlpha" stroke="#3b82f6" fillOpacity={1} fill="url(#colorExecution)" name="Execution Alpha" strokeWidth={2} />
                                    <Area type="monotone" dataKey="pedigreeIndex" stroke="#ef4444" fillOpacity={1} fill="url(#colorPedigree)" name="Pedigree Premium" strokeWidth={2} />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </CardContent>
                </Card>

                {/* The 4 Signal Scores */}
                <Card className="bg-[#0a0a0f] border-white/5">
                    <CardHeader>
                        <CardTitle className="text-lg flex items-center gap-2">
                            <Cpu className="w-5 h-5 text-purple-400" />
                            Core Signal Scores
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-6">

                        <div>
                            <div className="flex justify-between items-center mb-2">
                                <span className="text-sm font-medium text-gray-300">Product-Market Fit</span>
                                <span className="text-sm font-bold text-white">35% Weight</span>
                            </div>
                            <div className="h-2 w-full bg-gray-800 rounded-full overflow-hidden">
                                <div className="h-full bg-blue-500 w-[85%]" />
                            </div>
                            <p className="text-xs text-gray-500 mt-1">Retention tracking via TelemetryCore.</p>
                        </div>

                        <div>
                            <div className="flex justify-between items-center mb-2">
                                <span className="text-sm font-medium text-gray-300">Technical Velocity</span>
                                <span className="text-sm font-bold text-white">25% Weight</span>
                            </div>
                            <div className="h-2 w-full bg-gray-800 rounded-full overflow-hidden">
                                <div className="h-full bg-purple-500 w-[92%]" />
                            </div>
                            <p className="text-xs text-gray-500 mt-1">Code commits & Agent deployment speed.</p>
                        </div>

                        <div>
                            <div className="flex justify-between items-center mb-2">
                                <span className="text-sm font-medium text-gray-300">Founder Performance</span>
                                <span className="text-sm font-bold text-white">20% Weight</span>
                            </div>
                            <div className="h-2 w-full bg-gray-800 rounded-full overflow-hidden">
                                <div className="h-full bg-indigo-500 w-[78%]" />
                            </div>
                            <p className="text-xs text-gray-500 mt-1">Strategic agility and AI Copilot interaction.</p>
                        </div>

                        <div>
                            <div className="flex justify-between items-center mb-2">
                                <span className="text-sm font-medium text-gray-300">Capital Efficiency</span>
                                <span className="text-sm font-bold text-white">20% Weight</span>
                            </div>
                            <div className="h-2 w-full bg-gray-800 rounded-full overflow-hidden">
                                <div className="h-full bg-green-500 w-[88%]" />
                            </div>
                            <p className="text-xs text-gray-500 mt-1">Projected LTV/CAC ratio & runway optimization.</p>
                        </div>

                    </CardContent>
                </Card>

            </div>

            {/* The Thesis Panel */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card className="bg-[#050508] border-white/5 overflow-hidden group">
                    <div className="p-8">
                        <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center mb-6 border border-blue-500/20 group-hover:bg-blue-500/20 transition-colors">
                            <Target className="w-6 h-6 text-blue-400" />
                        </div>
                        <h3 className="text-xl font-bold text-white mb-3">The "Safe Bet" Fallacy</h3>
                        <p className="text-gray-400 text-sm leading-relaxed">
                            Traditional VC optimizes for "hard-to-fake" pedigree signals (Stanford, ex-Google) to de-risk investments. Our data proves these assets are globally overpriced (US ROP = 0.65). Momentaic bypasses narrative bias by analyzing raw execution velocity directly via Mission Control.
                        </p>
                        <button className="mt-6 flex items-center gap-2 text-sm text-blue-400 font-medium hover:text-blue-300">
                            Read NBER Execution Report <ChevronRight className="w-4 h-4" />
                        </button>
                    </div>
                </Card>

                <Card className="bg-[#050508] border-white/5 overflow-hidden group">
                    <div className="p-8">
                        <div className="w-12 h-12 rounded-xl bg-green-500/10 flex items-center justify-center mb-6 border border-green-500/20 group-hover:bg-green-500/20 transition-colors">
                            <Users className="w-6 h-6 text-green-400" />
                        </div>
                        <h3 className="text-xl font-bold text-white mb-3">The Immigrant Arbitrage</h3>
                        <p className="text-gray-400 text-sm leading-relaxed">
                            60% of top US AI companies feature immigrant founders. Visa restrictions and a lack of elite alumni networks cause systematic underfunding by traditional VCs. The Momentaic Signal Engine is perfectly positioned to capitalize on this homophily blind-spot.
                        </p>
                        <button className="mt-6 flex items-center gap-2 text-sm text-green-400 font-medium hover:text-green-300">
                            View Geographic Disparity Model <ChevronRight className="w-4 h-4" />
                        </button>
                    </div>
                </Card>
            </div>

        </div>
    );
}
