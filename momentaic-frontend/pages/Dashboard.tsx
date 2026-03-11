import { useState, useEffect } from 'react';
import {
    FileText, Users, TrendingUp, Send, Bot, Eye, Rocket, ArrowRight,
    BarChart2, Shield, ChevronDown, ChevronUp, Film, Image as ImageIcon, PlayCircle,
    Zap, Loader, CheckCircle, Clock, Pause, Play, Sparkles, Database, Crosshair, Terminal
} from 'lucide-react';
import { api } from '../lib/api';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import ActivityFeed from '../components/ActivityFeed';
import { AdminEcosystemWidget } from '../components/dashboard/AdminEcosystemWidget';
import { AstroTurfWidget } from '../components/ui/AstroTurfWidget';
import { LiveAgentDashboard } from '../components/LiveAgentDashboard';
import { BenchmarkWidget } from '../components/dashboard/BenchmarkWidget';
import { ActionQueueWidget } from '../components/dashboard/ActionQueueWidget';
import { useAuthStore } from '../stores/auth-store';
import { useStartupStore } from '../stores/startup-store';
import { useWowTour } from '../components/tour/WowTourProvider';
import { Card, CardContent } from '../components/ui/Card';
import { Skeleton } from '../components/ui/Skeleton';

import { AgentActivity, AgentCard } from '../components/dashboard/AgentCard';
import { AdminAgentWidget } from '../components/dashboard/AdminAgentWidget';
import { EmpireProgressWidget } from '../components/dashboard/EmpireProgressWidget';
import { ZeroStateWidget } from '../components/dashboard/ZeroStateWidget';
import { FounderFeedbackWidget } from '../components/dashboard/FounderFeedbackWidget';
import { AgentStatusGrid } from '@/src/components/agents/AgentStatusGrid';
import { AgentActivityFeed } from '@/src/components/agents/AgentActivityFeed';
import { useAgentStream } from '@/src/hooks/useAgentStream';

export default function Dashboard() {
    const user = useAuthStore((state) => state.user);
    const navigate = useNavigate();
    const { startups, activeStartupId, fetchStartups } = useStartupStore();
    const [activities, setActivities] = useState<AgentActivity[]>([]);
    const [loading, setLoading] = useState(true);
    const [pendingStrategy, setPendingStrategy] = useState<any>(null);

    // Initialize Real-Time Agent Stream
    const { activities: liveActivities, agentStatuses, isConnected } = useAgentStream(activeStartupId || undefined);

    const hasStartups = startups.length > 0;

    // Hydrate startup store if needed
    useEffect(() => {
        if (user && startups.length === 0) {
            fetchStartups();
        }
    }, [user]);

    // Load dashboard data whenever the active startup changes
    useEffect(() => {
        if (!user || !activeStartupId) {
            setLoading(false);
            return;
        }

        const loadRealData = async () => {
            setLoading(true);
            try {
                // Check for pending strategies from onboarding
                const pendingStrategyData = localStorage.getItem('pendingStrategy');
                const pendingGeniusPlan = localStorage.getItem('pendingGeniusPlan');
                if (pendingStrategyData) {
                    setPendingStrategy(JSON.parse(pendingStrategyData));
                } else if (pendingGeniusPlan) {
                    setPendingStrategy(JSON.parse(pendingGeniusPlan));
                }

                // Get Dashboard Data scoped to active startup
                const dashboard = await api.getDashboard(activeStartupId);

                // Map to Frontend Model
                const realActivities: AgentActivity[] = dashboard.recent_activity.map((a: any, idx: number) => ({
                    id: `act-${idx}`,
                    agent: a.agent || 'System',
                    task: a.type === 'content_drafted' ? 'Drafting Content' :
                        a.type === 'lead_acquired' ? 'Hunting Leads' :
                            a.message.split(':')[0] || 'Processing',
                    status: 'complete',
                    progress: 100,
                    message: a.message,
                    started_at: a.timestamp
                }));

                setActivities(realActivities);
            } catch (e) {
                console.error("Failed to load dashboard:", e);
            } finally {
                setLoading(false);
            }
        };

        loadRealData();
    }, [user, activeStartupId]);

    const activeCount = activities.filter(a => a.status === 'running').length;
    const pendingCount = activities.filter(a => a.status === 'pending').length;
    const completedTodayCount = activities.filter(a => a.status === 'complete').length;

    return (
        <div className="min-h-screen bg-[#020202] text-white">
            {/* Header */}
            <div className="mb-8">
                <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-[#111111] from-purple-500/20 ">
                            <Zap className="w-6 h-6 text-purple-400" />
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold">Command Center</h1>
                            <p className="text-sm text-slate-400">Your AI team working in real-time</p>
                        </div>
                    </div>

                    {/* Admin Badge */}
                    {user?.is_superuser && (
                        <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/20 rounded-full">
                            <Shield className="w-4 h-4 text-emerald-400" />
                            <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">
                                System Verified v2.0
                            </span>
                        </div>
                    )}
                </div>

                {/* Stats Bar */}
                <div className="flex flex-col sm:flex-row gap-4 sm:gap-6 mt-6">
                    <div className="flex items-center gap-2">
                        <Loader className="w-4 h-4 text-blue-400 animate-spin" />
                        <span className="text-sm text-slate-300">{activeCount} Active</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4 text-slate-400" />
                        <span className="text-sm text-slate-300">{pendingCount} Pending</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-emerald-400" />
                        <span className="text-sm text-slate-300">{completedTodayCount} Completed Today</span>
                    </div>
                </div>
            </div>

            {/* PMF Pulse Widget */}
            <FounderFeedbackWidget />

            {/* Morning Briefing Hero */}
            {hasStartups && (
                <Card variant="neon" className="mb-8 p-6 from-[#0a0a1a]/90 to-[#0f0520]/90">
                    <div className="absolute top-0 right-0 w-48 h-48 bg-purple-500/10 rounded-full blur-[80px] -translate-y-1/2 translate-x-1/2 group-hover:bg-purple-500/15 transition-colors" />
                    <div className="absolute bottom-0 left-0 w-32 h-32 bg-blue-500/10 rounded-full blur-[60px] translate-y-1/2 -translate-x-1/2" />

                    <div className="relative z-10">
                        <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-xl bg-[#111111] from-purple-500 flex items-center justify-center shadow-lg ">
                                    <Zap className="w-5 h-5 text-white" />
                                </div>
                                <div>
                                    <h2 className="text-lg font-bold text-white">Mission Control</h2>
                                    <p className="text-xs text-gray-400 mt-0.5">
                                        Live visibility into your autonomous team
                                    </p>
                                </div>
                            </div>
                            <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/20 rounded-full">
                                <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                                <span className="text-xs font-medium text-emerald-400">Stream Connected</span>
                            </div>
                        </div>

                        {/* REAL-TIME AGENT STATUS GRID */}
                        <div className="mb-4">
                            <AgentStatusGrid statuses={agentStatuses} />
                        </div>

                        <div className="text-sm text-gray-400 leading-relaxed mt-4">
                            Your autonomous team is monitoring competitors, scanning for leads, and executing growth strategies in real-time based on live data triggers.
                        </div>
                    </div>
                </Card>
            )}

            {/* Show Zero State if no startups */}
            {hasStartups === false ? (
                <ZeroStateWidget
                    pendingStrategy={pendingStrategy}
                    onCreateStartup={() => navigate('/onboarding/genius')}
                />
            ) : (
                <>
                    {/* Admin Specialized Agents */}
                    {user?.is_superuser && (
                        <div className="space-y-8">
                            <AdminEcosystemWidget />
                            <AdminAgentWidget />
                        </div>
                    )}

                    {/* Empire Progress Widget */}
                    <EmpireProgressWidget />

                    {/* CORE APP QUICK ACTIONS - INFLUENCER SCRAPER HIGHLIGHT */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                        {/* Stealth Scraper Banner Card */}
                        <div className="group relative bg-[#111111] border border-[#00e5ff]/30 rounded-2xl p-6 overflow-hidden flex flex-col justify-between hover:border-[#00e5ff] transition-all duration-300">
                            <div className="absolute inset-0 bg-gradient-to-br from-[#00e5ff]/5 to-transparent pointer-events-none" />
                            <div className="absolute top-0 right-0 w-32 h-32 bg-[#00e5ff]/10 rounded-full blur-[50px] pointer-events-none" />
                            
                            <div className="relative z-10">
                                <div className="flex justify-between items-start mb-4">
                                    <div className="p-3 bg-[#020202] rounded-xl border border-white/10 group-hover:border-[#00e5ff]/50 transition-colors">
                                        <Crosshair className="w-6 h-6 text-[#00e5ff]" />
                                    </div>
                                    <span className="px-3 py-1 bg-[#00e5ff]/10 text-[#00e5ff] text-[10px] font-bold font-mono tracking-widest rounded-full uppercase border border-[#00e5ff]/20">
                                        New Core Matrix
                                    </span>
                                </div>
                                <h3 className="text-xl font-bold text-white mb-2 tracking-tight">Influecer Scraper & Data Pool</h3>
                                <p className="text-sm text-gray-400 mb-6 font-mono leading-relaxed">
                                    Deploy our anti-detect DeerFlow engine to scrape up to 10k highly targeted profiles from Instagram, X, and TikTok with zero API costs.
                                </p>
                            </div>
                            
                            <Button 
                                onClick={() => navigate('/scraper/onboarding')}
                                className="relative z-10 w-full bg-[#111111] border border-[#00e5ff]/50 text-[#00e5ff] hover:bg-[#00e5ff] hover:text-black font-bold font-mono tracking-widest uppercase transition-all shadow-[0_0_15px_rgba(0,229,255,0.15)] group-hover:shadow-[0_0_25px_rgba(0,229,255,0.4)]"
                            >
                                <Database className="w-4 h-4 mr-2" /> Launch Extractor
                            </Button>
                        </div>
                        
                        {/* Ghost Board Shortcut Card */}
                        <div className="group relative bg-[#111111] border border-purple-500/30 rounded-2xl p-6 overflow-hidden flex flex-col justify-between hover:border-purple-500 transition-all duration-300">
                            <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-transparent pointer-events-none" />
                            <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/10 rounded-full blur-[50px] pointer-events-none" />
                            
                            <div className="relative z-10">
                                <div className="flex justify-between items-start mb-4">
                                    <div className="p-3 bg-[#020202] rounded-xl border border-white/10 group-hover:border-purple-500/50 transition-colors">
                                        <Terminal className="w-6 h-6 text-purple-400" />
                                    </div>
                                    <span className="flex items-center gap-2 px-3 py-1 bg-purple-500/10 text-purple-400 text-[10px] font-bold font-mono tracking-widest rounded-full uppercase border border-purple-500/20">
                                        <span className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-pulse" /> Daily Brief
                                    </span>
                                </div>
                                <h3 className="text-xl font-bold text-white mb-2 tracking-tight">Ghost Board HQ</h3>
                                <p className="text-sm text-gray-400 mb-6 font-mono leading-relaxed">
                                    Review your daily synthetic co-founder updates, telemetry overnight, and approve your 3 core autonomous AI moves for today.
                                </p>
                            </div>
                            
                            <Button 
                                onClick={() => navigate('/ghost-board')}
                                className="relative z-10 w-full bg-purple-600/20 border border-purple-500/50 text-purple-400 hover:bg-purple-600 hover:text-white font-bold font-mono tracking-widest uppercase transition-all"
                            >
                                <Zap className="w-4 h-4 mr-2" /> Enter Ghost Board
                            </Button>
                        </div>
                    </div>

                    {/* AstroTurf Row (Hidden by default, shown if actively campaigning) */}
                    <div className="mb-6">
                        <details className="group [&_summary::-webkit-details-marker]:hidden">
                            <summary className="flex cursor-pointer items-center justify-between bg-[#111111]/50 p-4 rounded-xl border border-white/5 hover:border-white/10 transition-colors">
                                <span className="font-semibold text-sm flex items-center gap-2">
                                    <Sparkles className="w-4 h-4 text-purple-400" />
                                    Advanced Telemetry & Growth Campaigns
                                </span>
                                <span className="text-slate-500 group-open:rotate-180 transition-transform duration-300">
                                    <ChevronDown className="w-4 h-4" />
                                </span>
                            </summary>
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-4 opacity-0 group-open:opacity-100 transition-opacity duration-300">
                                <BenchmarkWidget />
                                <AstroTurfWidget />
                            </div>
                        </details>
                    </div>

                    {/* Main Grid */}
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {/* Active Agents */}
                        <div className="lg:col-span-2 space-y-4">
                            <div className="flex items-center justify-between">
                                <h2 className="text-lg font-semibold flex items-center gap-2">
                                    <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
                                    Active Agents
                                </h2>
                                <Button size="sm" variant="outline">
                                    <Pause className="w-3 h-3 mr-1" />
                                    Pause All
                                </Button>
                            </div>

                            {loading ? (
                                <div className="space-y-4 pt-2">
                                    <Skeleton className="h-24 w-full rounded-xl" />
                                    <Skeleton className="h-24 w-full rounded-xl" />
                                    <Skeleton className="h-24 w-full rounded-xl opacity-50" />
                                </div>
                            ) : (
                                <div className="space-y-3">
                                    {activities
                                        .filter(a => a.status === 'running')
                                        .map(activity => (
                                            <AgentCard key={activity.id} activity={activity} />
                                        ))}
                                </div>
                            )}

                            {/* Pending Operations */}
                            <div className="mt-8">
                                <details className="group [&_summary::-webkit-details-marker]:hidden">
                                    <summary className="flex cursor-pointer items-center justify-between">
                                        <h2 className="text-lg font-semibold flex items-center gap-2">
                                            <Clock className="w-4 h-4 text-slate-400" />
                                            Pending Queue ({activities.filter(a => a.status === 'pending').length})
                                        </h2>
                                        <span className="text-slate-500 group-open:rotate-180 transition-transform">
                                            <ChevronDown className="w-4 h-4" />
                                        </span>
                                    </summary>
                                    <div className="space-y-3 mt-4">
                                        {activities
                                            .filter(a => a.status === 'pending')
                                            .map(activity => (
                                                <AgentCard key={activity.id} activity={activity} />
                                            ))}
                                    </div>
                                </details>
                            </div>

                            {/* Completed Operations */}
                            <div className="mt-8">
                                <details className="group [&_summary::-webkit-details-marker]:hidden">
                                    <summary className="flex cursor-pointer items-center justify-between">
                                        <h2 className="text-lg font-semibold flex items-center gap-2">
                                            <CheckCircle className="w-4 h-4 text-emerald-400" />
                                            Completed Today ({activities.filter(a => a.status === 'complete').length})
                                        </h2>
                                        <span className="text-slate-500 group-open:rotate-180 transition-transform">
                                            <ChevronDown className="w-4 h-4" />
                                        </span>
                                    </summary>
                                    <div className="space-y-3 mt-4">
                                        {activities
                                            .filter(a => a.status === 'complete')
                                            .map(activity => (
                                                <AgentCard key={activity.id} activity={activity} />
                                            ))}
                                    </div>
                                </details>
                            </div>
                        </div>

                        {/* Sidebar: Live Ops & Swarm Feed */}
                        <div className="space-y-6">
                            {/* Quick Focus */}
                            <Card variant="glass">
                                <CardContent className="p-4">
                                    <h3 className="font-medium mb-3 flex items-center gap-2">
                                        <Zap className="w-4 h-4 text-purple-400" /> Quick Override
                                    </h3>
                                    <input
                                        type="text"
                                        placeholder="Intercept AI focus..."
                                        className="w-full px-4 py-3 rounded-lg bg-[#1A1A1A]/50 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-purple-500/50 text-sm"
                                    />
                                    <Button className="w-full mt-3 h-10 text-xs font-bold font-mono tracking-widest" variant="cyber">
                                        <Play className="w-3 h-3 mr-2" />
                                        DISPATCH
                                    </Button>
                                </CardContent>
                            </Card>

                            {/* Live WebSocket Swarm Feed */}
                            <div className="h-[400px]">
                                <AgentActivityFeed activities={liveActivities} limit={50} />
                            </div>

                            {/* Historical Activity Logs */}
                            <details className="group [&_summary::-webkit-details-marker]:hidden">
                                <summary className="flex cursor-pointer items-center justify-between bg-[#111111]/50 p-3 rounded-lg border border-white/5 text-xs font-mono text-slate-400 hover:text-white transition-colors">
                                    <span>View Historical Logs</span>
                                    <ChevronDown className="w-4 h-4 group-open:rotate-180 transition-transform" />
                                </summary>
                                <div className="mt-4">
                                    <ActivityFeed />
                                </div>
                            </details>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}