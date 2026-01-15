import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Brain, Search, Users, ShieldAlert, Rocket, Newspaper, AlertTriangle, CheckCircle, Zap } from 'lucide-react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import toast from 'react-hot-toast';

// Helper for mocked API calls during development if backend isn't reachable yet
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const InnovatorLab: React.FC = () => {
    const [activeTab, setActiveTab] = useState<'research' | 'growth' | 'wargame'>('research');

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-8 pb-20">
            {/* Header */}
            <div className="space-y-2">
                <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent flex items-center gap-2">
                    <Rocket className="w-8 h-8 text-purple-400" />
                    Innovator Lab
                </h1>
                <p className="text-gray-400">Experimental autonomous agents for aggressive growth and strategy.</p>
            </div>

            {/* Navigation */}
            <div className="flex gap-4 border-b border-white/10 pb-1 overflow-x-auto">
                <TabButton
                    active={activeTab === 'research'}
                    onClick={() => setActiveTab('research')}
                    icon={<Brain className="w-4 h-4" />}
                    label="Deep Research"
                />
                <TabButton
                    active={activeTab === 'growth'}
                    onClick={() => setActiveTab('growth')}
                    icon={<Users className="w-4 h-4" />}
                    label="Growth Monitor"
                />
                <TabButton
                    active={activeTab === 'wargame'}
                    onClick={() => setActiveTab('wargame')}
                    icon={<ShieldAlert className="w-4 h-4" />}
                    label="War Gaming"
                />
            </div>

            {/* Content Area */}
            <div className="min-h-[600px]">
                {activeTab === 'research' && <DeepResearchWidget />}
                {activeTab === 'growth' && <GrowthMonitorWidget />}
                {activeTab === 'wargame' && <WarGamingWidget />}
            </div>
        </div>
    );
};

// --- Sub-Components ---

const DeepResearchWidget = () => {
    const [topic, setTopic] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [report, setReport] = useState<string | null>(null);

    const handleResearch = async () => {
        if (!topic) return;
        setIsLoading(true);
        setReport(null);
        try {
            const res = await axios.post(`${API_URL}/innovator/deep-research`, { topic, depth: 3 });
            setReport(res.data.report);
            toast.success("Research complete!");
        } catch (error) {
            console.error(error);
            toast.error("Research failed. See console.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            <div className="bg-white/5 border border-white/10 rounded-xl p-6 space-y-4">
                <h2 className="text-xl font-semibold flex items-center gap-2">
                    <Search className="w-5 h-5 text-blue-400" />
                    Deep Research Agent
                </h2>
                <p className="text-sm text-gray-400">
                    Generates a comprehensive "State of the Union" report by reading multiple live sources (PDFs, Whitepapers).
                </p>
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={topic}
                        onChange={(e) => setTopic(e.target.value)}
                        placeholder="e.g., Agentic AI Trends 2025"
                        className="flex-1 bg-black/50 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500 transition-colors"
                        onKeyDown={(e) => e.key === 'Enter' && handleResearch()}
                    />
                    <button
                        onClick={handleResearch}
                        disabled={isLoading || !topic}
                        className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed px-6 py-2 rounded-lg font-medium transition-colors flex items-center gap-2"
                    >
                        {isLoading ? <span className="animate-spin">⏳</span> : <Zap className="w-4 h-4" />}
                        {isLoading ? "Reading Sources..." : "Start Research"}
                    </button>
                </div>
            </div>

            {report && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-white/5 border border-white/10 rounded-xl p-8 prose prose-invert max-w-none"
                >
                    <ReactMarkdown>{report}</ReactMarkdown>
                </motion.div>
            )}
        </div>
    );
};

const GrowthMonitorWidget = () => {
    const [keywords, setKeywords] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [opportunities, setOpportunities] = useState<any[]>([]);

    const handleScan = async () => {
        if (!keywords) return;
        setIsLoading(true);
        try {
            const keywordList = keywords.split(',').map(k => k.trim());
            const res = await axios.post(`${API_URL}/innovator/growth-monitor`, { keywords: keywordList });
            setOpportunities(res.data.opportunities || []);
            if (res.data.opportunities?.length === 0) {
                toast("No discussions found. Try broader keywords.", { icon: "ℹ️" });
            } else {
                toast.success(`Found ${res.data.opportunities.length} leads!`);
            }
        } catch (error) {
            console.error(error);
            toast.error("Scan failed.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            <div className="bg-white/5 border border-white/10 rounded-xl p-6 space-y-4">
                <h2 className="text-xl font-semibold flex items-center gap-2">
                    <Users className="w-5 h-5 text-green-400" />
                    Growth Social Monitor
                </h2>
                <p className="text-sm text-gray-400">
                    Scans Reddit for discussions related to your keywords and drafts helpful, non-spammy replies.
                </p>
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={keywords}
                        onChange={(e) => setKeywords(e.target.value)}
                        placeholder="e.g., SaaS marketing, startup growth (comma separated)"
                        className="flex-1 bg-black/50 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-green-500 transition-colors"
                    />
                    <button
                        onClick={handleScan}
                        disabled={isLoading || !keywords}
                        className="bg-green-600 hover:bg-green-500 disabled:opacity-50 px-6 py-2 rounded-lg font-medium transition-colors flex items-center gap-2"
                    >
                        {isLoading ? <span className="animate-spin">⏳</span> : <Search className="w-4 h-4" />}
                        Scan Reddit
                    </button>
                </div>
            </div>

            <div className="grid gap-4">
                {opportunities.map((opp, idx) => (
                    <div key={idx} className="bg-white/5 border border-white/10 rounded-xl p-6 space-y-3">
                        <div className="flex justify-between items-start">
                            <h3 className="font-semibold text-lg text-blue-300 truncate w-3/4">
                                <a href={opp.url} target="_blank" rel="noreferrer" className="hover:underline">
                                    {opp.summary ? opp.summary.slice(0, 80) + "..." : opp.url}
                                </a>
                            </h3>
                            <span className="text-xs bg-green-500/20 text-green-300 px-2 py-1 rounded">Reddit</span>
                        </div>
                        <div className="bg-black/30 p-4 rounded-lg text-sm text-gray-300 whitespace-pre-wrap font-mono">
                            {opp.draft_reply}
                        </div>
                        <div className="flex justify-end gap-2">
                            <button
                                onClick={() => { navigator.clipboard.writeText(opp.draft_reply); toast.success("Copied!"); }}
                                className="text-sm text-gray-400 hover:text-white px-3 py-1 rounded border border-white/10 hover:bg-white/10"
                            >
                                Copy Draft
                            </button>
                            <a
                                href={opp.url}
                                target="_blank"
                                rel="noreferrer"
                                className="text-sm bg-blue-600/20 text-blue-300 hover:bg-blue-600/30 px-3 py-1 rounded border border-blue-500/30"
                            >
                                Open Thread
                            </a>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

const WarGamingWidget = () => {
    const [isLoading, setIsLoading] = useState(false);
    const [result, setResult] = useState<any>(null);

    // Default context for demo (in production, fetch from selected startup)
    const [context, setContext] = useState({
        name: "MomentAIc",
        description: "AI Operating System for Startups. Replaces employees with agents.",
        industry: "SaaS",
        pain_point: "Founders are overwhelmed.",
        value_prop: "Full AI Team for $50/mo.",
        price_point: "$49/mo"
    });

    const handleSimulate = async () => {
        setIsLoading(true);
        setResult(null);
        try {
            const res = await axios.post(`${API_URL}/innovator/war-game`, context);
            setResult(res.data);
            toast.success("Simulation complete!", { icon: "🔥" });
        } catch (error) {
            console.error(error);
            toast.error("Simulation failed.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            <div className="bg-white/5 border border-white/10 rounded-xl p-6 space-y-6">
                <div className="flex justify-between items-center">
                    <div>
                        <h2 className="text-xl font-semibold flex items-center gap-2 text-red-400">
                            <ShieldAlert className="w-6 h-6" />
                            Launch Simulator (War Games)
                        </h2>
                        <p className="text-sm text-gray-400 mt-1">
                            Simulate 4 user personas (Skeptic, VC, Enterprise, User) brutally critiquing your pitch.
                        </p>
                    </div>
                    <button
                        onClick={handleSimulate}
                        disabled={isLoading}
                        className="bg-red-600 hover:bg-red-500 disabled:opacity-50 px-6 py-3 rounded-lg font-bold transition-transform active:scale-95 flex items-center gap-2 shadow-lg shadow-red-900/20"
                    >
                        {isLoading ? <span className="animate-spin">⚔️</span> : <Zap className="w-5 h-5 fill-current" />}
                        {isLoading ? "Simulating Audit..." : "RUN WAR GAMES"}
                    </button>
                </div>

                {/* Context Editor (Collapsible or visible) */}
                <div className="grid grid-cols-2 gap-4 text-sm bg-black/20 p-4 rounded-lg border border-white/5">
                    <div>
                        <label className="block text-gray-500 mb-1">Product Name</label>
                        <input value={context.name} onChange={e => setContext({ ...context, name: e.target.value })} className="w-full bg-transparent border-b border-white/10 focus:border-red-500 outline-none" />
                    </div>
                    <div>
                        <label className="block text-gray-500 mb-1">One-Liner</label>
                        <input value={context.description} onChange={e => setContext({ ...context, description: e.target.value })} className="w-full bg-transparent border-b border-white/10 focus:border-red-500 outline-none" />
                    </div>
                </div>
            </div>

            {result && (
                <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    {/* Survival Score */}
                    {/* We need to extract the score from the text if it's there, or just show the report */}
                    <div className="bg-gradient-to-br from-red-900/40 to-black border border-red-500/30 rounded-xl p-8 text-center relative overflow-hidden">
                        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20"></div>
                        <h3 className="text-gray-400 uppercase tracking-widest text-sm mb-2 font-bold">Launch Survival Score</h3>
                        <div className="text-6xl font-black text-white" style={{ textShadow: "0 0 20px rgba(220, 38, 38, 0.5)" }}>
                            {/* Naive extraction of score if present */}
                            {result.report.match(/Survival Score: (\d+)/)?.[1] || "??"}/100
                        </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-6">
                        {/* The Critiques */}
                        <div className="bg-white/5 border border-white/10 rounded-xl p-6 h-96 overflow-y-auto custom-scrollbar">
                            <h3 className="font-semibold text-gray-300 mb-4 flex items-center gap-2">
                                <AlertTriangle className="w-4 h-4 text-yellow-500" />
                                Raw Critiques
                            </h3>
                            <div className="space-y-4 text-sm text-gray-400">
                                {result.raw_critiques.map((c: string, i: number) => (
                                    <div key={i} className="p-3 bg-black/30 rounded border border-white/5">
                                        <ReactMarkdown>{c}</ReactMarkdown>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* The Final Report */}
                        <div className="bg-white/5 border border-white/10 rounded-xl p-6 h-96 overflow-y-auto custom-scrollbar prose prose-sm prose-invert">
                            <h3 className="font-semibold text-gray-300 mb-4 flex items-center gap-2">
                                <CheckCircle className="w-4 h-4 text-green-500" />
                                War Room Strategy
                            </h3>
                            <ReactMarkdown>{result.report}</ReactMarkdown>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

const TabButton = ({ active, onClick, icon, label }: any) => (
    <button
        onClick={onClick}
        className={`
            flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors border-b-2 whitespace-nowrap
            ${active
                ? 'border-purple-500 text-white'
                : 'border-transparent text-gray-400 hover:text-gray-200 hover:border-gray-700'}
        `}
    >
        {icon}
        {label}
    </button>
);

export default InnovatorLab;
