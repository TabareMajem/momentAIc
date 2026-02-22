
import React, { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { AgentInfo } from '../types';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Input } from '../components/ui/Input';
import { Skeleton } from '../components/ui/Skeleton';
import { Bot, Lock, ArrowRight, Search, Sparkles, Zap, TrendingUp, Shield } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuthStore } from '../stores/auth-store';
import { InteractiveAgentShowcase } from '../components/marketing/InteractiveAgentShowcase';

export default function AgentsMarket() {
    const [agents, setAgents] = useState<{ available: AgentInfo[], locked: AgentInfo[] }>({ available: [], locked: [] });
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [intent, setIntent] = useState<string | null>(null);
    const { user } = useAuthStore();

    useEffect(() => {
        let mounted = true;
        api.getAvailableAgents()
            .then((data) => {
                if (!mounted) return;
                setAgents({
                    available: Array.isArray(data?.available) ? data.available : [],
                    locked: Array.isArray(data?.locked) ? data.locked : []
                });
            })
            .catch(console.error)
            .finally(() => {
                if (mounted) setLoading(false);
            });
        return () => { mounted = false; };
    }, []);

    // Simple Intent Mapping (Simulating NLP)
    useEffect(() => {
        const q = searchQuery.toLowerCase();
        if (q.includes('user') || q.includes('growth') || q.includes('market')) setIntent('growth');
        else if (q.includes('code') || q.includes('bug') || q.includes('tech')) setIntent('tech');
        else if (q.includes('fund') || q.includes('money') || q.includes('vc')) setIntent('finance');
        else if (q.includes('legal') || q.includes('contract')) setIntent('legal');
        else setIntent(null);
    }, [searchQuery]);

    const allAgents = [...(agents.available || []), ...(agents.locked || [])];

    const filteredAgents = allAgents.filter(agent => {
        if (!searchQuery) return true;
        const matchesText = agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
            agent.description.toLowerCase().includes(searchQuery.toLowerCase());

        // Intent matching
        if (intent === 'growth' && (agent.id.includes('sales') || agent.id.includes('business'))) return true;
        if (intent === 'tech' && agent.id.includes('technical')) return true;
        if (intent === 'finance' && agent.id.includes('fundraising')) return true;
        if (intent === 'legal' && agent.id.includes('legal')) return true;

        return matchesText;
    });

    const AgentCard: React.FC<{ agent: AgentInfo }> = ({ agent }) => {
        const isLocked = (user?.subscription_tier === 'starter' && agent.tier !== 'starter') ||
            (user?.subscription_tier === 'growth' && agent.tier === 'god_mode');

        return (
            <Card className={`h-full flex flex-col group relative overflow-hidden ${isLocked ? 'opacity-75 bg-gray-50/5' : 'hover:shadow-[0_0_30px_rgba(59,130,246,0.15)] border-white/10'}`}>
                {/* Hover Glow */}
                {!isLocked && <div className="absolute inset-0 bg-gradient-to-br from-[#00f0ff]/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div>}

                <CardHeader>
                    <div className="flex justify-between items-start">
                        <div className={`p-3 rounded-xl border ${isLocked ? 'bg-gray-900 border-white/5' : 'bg-[#00f0ff]/10 border-[#00f0ff]/20'}`}>
                            {isLocked ? <Lock className="w-6 h-6 text-gray-500" /> : <Bot className="w-6 h-6 text-[#00f0ff]" />}
                        </div>
                        <Badge variant={agent.tier === 'god_mode' ? 'warning' : 'secondary'} className="bg-black border border-white/10">
                            {agent.tier.replace('_', ' ')}
                        </Badge>
                    </div>
                    <CardTitle className="mt-4 font-mono uppercase tracking-tight">{agent.name}</CardTitle>
                    <CardDescription className="min-h-[40px] font-mono text-xs">{agent.description}</CardDescription>
                </CardHeader>
                <CardFooter className="mt-auto pt-4 border-t border-white/5">
                    {isLocked ? (
                        <Link to="/settings" className="w-full">
                            <Button variant="outline" className="w-full border-white/10 hover:bg-white/5 text-gray-400" title={`Requires ${agent.tier} tier`}>
                                <Lock className="w-3 h-3 mr-2" /> UNLOCK
                            </Button>
                        </Link>
                    ) : (
                        <Link to={`/agents/chat?agent=${agent.id}`} className="w-full">
                            <Button variant="cyber" className="w-full h-10 text-xs">
                                DEPLOY AGENT <ArrowRight className="w-3 h-3 ml-2" />
                            </Button>
                        </Link>
                    )}
                </CardFooter>
            </Card>
        );
    };

    if (loading) return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map(i => <Skeleton key={i} className="h-[280px] bg-white/5" />)}
        </div>
    );

    return (
        <div className="space-y-8 min-h-[80vh]">
            {/* Intelligent Search Header */}
            <div className="relative overflow-hidden rounded-2xl bg-[#0a0a0a] border border-white/10 p-8 md:p-12 text-center">
                <div className="absolute inset-0 bg-cyber-grid opacity-10 pointer-events-none"></div>
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-[#00f0ff]/10 blur-[100px] rounded-full pointer-events-none"></div>

                <h1 className="relative z-10 text-3xl md:text-4xl font-black text-white mb-2 uppercase tracking-tighter">
                    Agent Command Center
                </h1>
                <p className="relative z-10 text-gray-400 mb-8 max-w-lg mx-auto font-mono text-sm">
                    Don't browse. Command. Describe your problem, and we'll assemble the team.
                </p>

                <div className="relative z-10 max-w-2xl mx-auto">
                    <div className="relative group">
                        <div className="absolute -inset-0.5 bg-gradient-to-r from-[#00f0ff] to-[#a855f7] rounded-xl opacity-30 group-hover:opacity-70 blur transition duration-500"></div>
                        <div className="relative flex items-center bg-black rounded-xl p-1">
                            <Search className="ml-4 w-5 h-5 text-gray-400" />
                            <input
                                type="text"
                                placeholder='Try "I need to raise capital" or "Fix my code quality"...'
                                className="w-full bg-transparent border-none focus:ring-0 text-white p-4 font-mono text-sm placeholder:text-gray-600"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                            />
                            {intent && (
                                <div className="hidden md:flex items-center gap-2 pr-4 animate-fade-in">
                                    <span className="text-[10px] uppercase text-[#00f0ff] font-bold bg-[#00f0ff]/10 px-2 py-1 rounded border border-[#00f0ff]/20">
                                        DETECTED: {intent}
                                    </span>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Quick Prompts */}
                <div className="relative z-10 flex flex-wrap justify-center gap-3 mt-6">
                    {[
                        { label: "Need more users", intent: "growth", icon: <TrendingUp className="w-3 h-3" /> },
                        { label: "Code audit", intent: "tech", icon: <Zap className="w-3 h-3" /> },
                        { label: "Draft contracts", intent: "legal", icon: <Shield className="w-3 h-3" /> },
                    ].map((btn, i) => (
                        <button
                            key={i}
                            onClick={() => setSearchQuery(btn.label)}
                            className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-[10px] text-gray-400 hover:text-white transition-colors font-mono uppercase tracking-wide"
                        >
                            {btn.icon} {btn.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Interactive Swarm Demonstration Feature */}
            <div className="py-8">
                <InteractiveAgentShowcase />
            </div>

            {/* Recommendations Section */}
            {searchQuery && filteredAgents.length > 0 && (
                <div className="space-y-4 animate-fade-in-up">
                    <div className="flex items-center gap-2 text-[#00f0ff]">
                        <Sparkles className="w-4 h-4" />
                        <span className="font-mono text-xs uppercase font-bold tracking-widest">AI Recommendation</span>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {filteredAgents.slice(0, 3).map(agent => (
                            <AgentCard key={agent.id} agent={agent} />
                        ))}
                    </div>
                    <div className="border-t border-white/5 my-8"></div>
                </div>
            )}

            {/* All Agents Grid */}
            <section className="space-y-4">
                <div className="flex justify-between items-end">
                    <h2 className="font-mono text-sm font-bold text-gray-500 uppercase tracking-widest">
                        Full Roster ({filteredAgents.length})
                    </h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {filteredAgents.length > 0 ? filteredAgents.map(agent => (
                        <AgentCard key={agent.id} agent={agent} />
                    )) : (
                        <div className="col-span-full py-12 text-center text-gray-500 font-mono">
                            No agents match your query. Try "Orchestrator".
                        </div>
                    )}
                </div>
            </section>
        </div>
    );
}
