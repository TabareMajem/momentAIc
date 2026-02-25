import React, { useEffect, useState } from 'react';
import { Target, FileText, Download, ThumbsUp, Sparkles, Filter, Search, Terminal } from 'lucide-react';
import { api } from '../lib/api';
import { Button } from '../components/ui/Button';
import { useNavigate } from 'react-router-dom';
import { useChatStore } from '../stores/chat-store';

interface Template {
    id: string;
    title: string;
    description: string;
    system_prompt: string;
    author_name: string;
    industry: string;
    agent_type_target: string;
    upvotes: int;
    clones: int;
}

export default function AgentMarketplace() {
    const [templates, setTemplates] = useState<Template[]>([]);
    const [loading, setLoading] = useState(true);
    const [industryFilter, setIndustryFilter] = useState('');
    const [sortBy, setSortBy] = useState<'upvotes' | 'newest'>('upvotes');
    const [upvoted, setUpvoted] = useState<Set<string>>(new Set());

    const navigate = useNavigate();

    useEffect(() => {
        loadTemplates();
    }, [industryFilter, sortBy]);

    async function loadTemplates() {
        setLoading(true);
        try {
            const data = await api.getMarketplaceTemplates(industryFilter || undefined, undefined, sortBy);
            setTemplates(data);
        } catch (e) {
            console.error("Failed to load marketplace", e);
        } finally {
            setLoading(false);
        }
    }

    const handleUpvote = async (e: React.MouseEvent, id: string) => {
        e.stopPropagation();
        if (upvoted.has(id)) return;
        try {
            await api.upvoteTemplate(id);
            setUpvoted(prev => new Set(prev).add(id));
            setTemplates(templates.map(t => t.id === id ? { ...t, upvotes: t.upvotes + 1 } : t));
        } catch (err) {
            console.error(err);
        }
    };

    const handleClone = async (id: string, agentType: string) => {
        try {
            const res = await api.cloneTemplate(id);
            if (res.system_prompt) {
                // Store it in session storage to be picked up by Agent Studio
                sessionStorage.setItem('clonedSystemPrompt', res.system_prompt);
                sessionStorage.setItem('clonedAgentType', agentType);
                navigate('/agent-studio');
            }
        } catch (err) {
            console.error("Failed to clone", err);
        }
    };

    return (
        <div className="min-h-screen bg-[#020202] text-white">
            {/* Header */}
            <div className="mb-8 p-6 bg-gradient-to-r from-purple-900/30 to-blue-900/10 border border-white/5 rounded-2xl relative overflow-hidden">
                <div className="absolute top-0 right-0 p-8 opacity-10 pointer-events-none">
                    <Terminal className="w-48 h-48 rotate-12 text-[#bf25eb]" />
                </div>

                <div className="relative z-10 flex flex-col md:flex-row md:items-end justify-between gap-6">
                    <div>
                        <h1 className="text-3xl font-bold flex items-center gap-3">
                            <Sparkles className="w-8 h-8 text-[#bf25eb]" />
                            Agent Marketplace
                        </h1>
                        <p className="text-gray-400 mt-2 max-w-xl">
                            Browse community-submitted system prompts, configurations, and autonomous strategies. Clone them directly into your workflow with one click.
                        </p>
                    </div>

                    <div className="flex items-center gap-3">
                        <Button variant="outline" size="sm" className="hidden sm:flex border-white/10 text-white">
                            <Target className="w-4 h-4 mr-2" />
                            Submit Template
                        </Button>
                    </div>
                </div>
            </div>

            {/* Filters */}
            <div className="flex flex-col sm:flex-row items-center gap-4 mb-8">
                <div className="relative flex-1 w-full max-w-md">
                    <Search className="absolute left-3 top-3 w-4 h-4 text-gray-500" />
                    <input
                        type="text"
                        placeholder="Search templates..."
                        className="w-full bg-[#0a0a0a] border border-white/10 rounded-lg pl-9 pr-4 py-2 text-sm text-white focus:outline-none focus:border-[#bf25eb]/50 transition-colors"
                    />
                </div>

                <div className="flex gap-2 w-full sm:w-auto overflow-x-auto pb-1">
                    {['', 'SaaS', 'E-commerce', 'General'].map(ind => (
                        <button
                            key={ind || 'all'}
                            onClick={() => setIndustryFilter(ind)}
                            className={`px-4 py-2 rounded-full text-xs font-mono transition-colors whitespace-nowrap ${industryFilter === ind
                                    ? 'bg-[#bf25eb] text-white font-bold'
                                    : 'bg-white/5 text-gray-400 hover:bg-white/10'
                                }`}
                        >
                            {ind || 'All Industries'}
                        </button>
                    ))}
                </div>

                <div className="flex gap-1 bg-[#0a0a0a] p-1 rounded-lg border border-white/10 ml-auto w-full sm:w-auto">
                    <button
                        onClick={() => setSortBy('upvotes')}
                        className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors flex-1 sm:flex-none text-center ${sortBy === 'upvotes' ? 'bg-white/10 text-white' : 'text-gray-500 hover:text-white'}`}
                    >
                        Top
                    </button>
                    <button
                        onClick={() => setSortBy('newest')}
                        className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors flex-1 sm:flex-none text-center ${sortBy === 'newest' ? 'bg-white/10 text-white' : 'text-gray-500 hover:text-white'}`}
                    >
                        Newest
                    </button>
                </div>
            </div>

            {/* Grid */}
            {loading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
                    {[1, 2, 3].map(i => (
                        <div key={i} className="bg-[#050505] border border-white/5 rounded-xl h-64" />
                    ))}
                </div>
            ) : templates.length === 0 ? (
                <div className="text-center py-24 text-gray-500 font-mono">
                    No templates found for this criteria.
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {templates.map(tmpl => (
                        <div key={tmpl.id} className="bg-[#0a0a0a] border border-white/10 rounded-xl p-5 hover:border-[#bf25eb]/40 transition-all flex flex-col hover:-translate-y-1 hover:shadow-2xl hover:shadow-[#bf25eb]/10 group cursor-default">
                            <div className="flex justify-between items-start mb-3">
                                <div className="flex gap-2">
                                    <span className="px-2 py-0.5 bg-white/5 border border-white/10 rounded uppercase text-[10px] font-mono text-gray-300">
                                        {tmpl.industry}
                                    </span>
                                    <span className="px-2 py-0.5 bg-[#bf25eb]/10 border border-[#bf25eb]/20 text-[#bf25eb] rounded uppercase text-[10px] font-mono">
                                        {tmpl.agent_type_target}
                                    </span>
                                </div>
                            </div>

                            <h3 className="text-lg font-bold text-white mb-2 leading-tight">{tmpl.title}</h3>
                            <p className="text-sm text-gray-400 line-clamp-2 mb-4 flex-1">
                                {tmpl.description}
                            </p>

                            {/* Interaction Row */}
                            <div className="flex items-center justify-between mt-auto pt-4 border-t border-white/5">
                                <div className="flex items-center gap-4">
                                    <button
                                        onClick={(e) => handleUpvote(e, tmpl.id)}
                                        className={`flex items-center gap-1.5 text-xs font-medium transition-colors ${upvoted.has(tmpl.id) ? 'text-[#bf25eb]' : 'text-gray-500 hover:text-gray-300'}`}
                                    >
                                        <ThumbsUp className={`w-4 h-4 ${upvoted.has(tmpl.id) ? 'fill-[#bf25eb]' : ''}`} />
                                        {tmpl.upvotes}
                                    </button>
                                    <span className="flex items-center gap-1.5 text-xs text-gray-500 font-medium">
                                        <Download className="w-4 h-4" />
                                        {tmpl.clones}
                                    </span>
                                </div>

                                <Button
                                    size="sm"
                                    variant="cyber"
                                    onClick={() => handleClone(tmpl.id, tmpl.agent_type_target)}
                                    className="opacity-0 group-hover:opacity-100 transition-opacity"
                                >
                                    Clone to Studio
                                </Button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
