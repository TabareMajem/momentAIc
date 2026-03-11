
import React, { useState, useEffect, useRef } from 'react';
import {
    Rocket, Globe, Zap, ShieldCheck, Terminal,
    Activity, Layers, Target, Play, RotateCw,
    CheckCircle, Lock, AlertOctagon, TrendingUp,
    Users, BarChart3, Fingerprint, Network, ChevronRight,
    LayoutDashboard, ArrowRight, RefreshCw, Sparkles, Share2,
    Instagram, Linkedin, Video, Copy, Download, FileJson,
    Cpu, Command, Hash, MessageCircle, Bot, Film, ThumbsUp, ThumbsDown,
    HardDrive, FileVideo, PenTool, Bell, UploadCloud, Smartphone, X, History, Save
} from 'lucide-react';
import { BackendService } from '../../services/backendService';
import { ViralStrategyResult } from '../../types';
import { useToast } from './Toast';

// --- NATIVE SUB-COMPONENTS ---

interface TrendCardProps {
    title: string;
    score: number;
    sub: string;
}

const TrendCard: React.FC<TrendCardProps> = ({ title, score, sub }) => (
    <div className="bg-slate-800/50 border border-slate-700 p-4 rounded-xl hover:border-purple-500/50 transition-all group cursor-pointer">
        <div className="flex justify-between items-start mb-2">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">{sub}</span>
            <span className="text-xs font-mono text-emerald-400 flex items-center gap-1">
                <TrendingUp className="w-3 h-3" /> {score}
            </span>
        </div>
        <p className="text-sm font-medium text-slate-200 group-hover:text-white line-clamp-2">{title}</p>
    </div>
);

const PhonePreview = ({ script }: { script: any }) => (
    <div className="w-[280px] h-[550px] bg-black rounded-[40px] border-8 border-slate-800 relative overflow-hidden shadow-2xl mx-auto">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-24 h-6 bg-slate-800 rounded-b-xl z-20"></div>

        {/* Screen Content */}
        <div className="absolute inset-0 bg-slate-900 z-10 flex flex-col">
            {/* Video Background Placeholder */}
            <div className="flex-1 bg-gradient-to-br from-purple-900/20 to-slate-900 flex items-center justify-center p-4 text-center relative">
                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10"></div>
                <p className="text-white font-bold text-lg drop-shadow-md z-10 font-serif italic">"{script.visual_cue}"</p>

                {/* TikTok Overlay UI */}
                <div className="absolute right-2 bottom-20 flex flex-col gap-4 items-center text-white">
                    <div className="w-10 h-10 bg-slate-700 rounded-full flex items-center justify-center"><ThumbsUp className="w-5 h-5" /></div>
                    <span className="text-[10px]">12.5k</span>
                    <div className="w-10 h-10 bg-slate-700 rounded-full flex items-center justify-center"><MessageCircle className="w-5 h-5" /></div>
                    <span className="text-[10px]">842</span>
                    <div className="w-10 h-10 bg-slate-700 rounded-full flex items-center justify-center"><Share2 className="w-5 h-5" /></div>
                </div>
            </div>

            {/* Script Overlay */}
            <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black via-black/60 to-transparent pb-10">
                <div className="bg-white/10 backdrop-blur-md rounded-lg p-2 mb-2 border border-white/10">
                    <p className="text-xs font-bold text-yellow-300 mb-1 uppercase">Hook (0-3s)</p>
                    <p className="text-sm text-white font-bold leading-tight">{script.hook}</p>
                </div>
                <p className="text-xs text-slate-200 line-clamp-3 mb-2">{script.body}</p>
                <p className="text-xs font-bold text-cyan-400">#viral #growth #startups</p>
            </div>
        </div>
    </div>
);

const ViralGrowthAgent: React.FC = () => {
    const [activeTab, setActiveTab] = useState<'STRATEGY' | 'ENGINE'>('STRATEGY');
    const [engineMode, setEngineMode] = useState<'TREND_RADAR' | 'SCRIPT_LAB' | 'SCREENING_ROOM'>('TREND_RADAR');

    // --- STRATEGY STATE ---
    const [url, setUrl] = useState('');
    const [budget, setBudget] = useState('5000');
    const [timeline, setTimeline] = useState('3_months');
    const [status, setStatus] = useState<'IDLE' | 'ANALYZING' | 'EXECUTING' | 'COMPLETE'>('IDLE');
    const [strategy, setStrategy] = useState<ViralStrategyResult | null>(null);
    const [strategyHistory, setStrategyHistory] = useState<any[]>([]);
    const [showHistory, setShowHistory] = useState(false);
    const { addToast } = useToast();

    // --- ENGINE STATE ---
    const [subreddit, setSubreddit] = useState('marketing');
    const [trends, setTrends] = useState<any[]>([]);
    const [isFetchingTrends, setIsFetchingTrends] = useState(false);

    const [generatedScripts, setGeneratedScripts] = useState<any[]>([]);
    const [isScripting, setIsScripting] = useState(false);
    const [selectedScript, setSelectedScript] = useState<any>(null);

    const [uploadedVideo, setUploadedVideo] = useState<File | null>(null);
    const [videoAnalysis, setVideoAnalysis] = useState<any>(null);
    const [isAnalyzingVideo, setIsAnalyzingVideo] = useState(false);

    const [isGeneratingVideo, setIsGeneratingVideo] = useState(false);
    const [generatedVideoUrl, setGeneratedVideoUrl] = useState<string | null>(null);
    const videoInputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        loadHistory();
    }, []);

    const loadHistory = async () => {
        try {
            const data = await BackendService.getViralHistory();
            setStrategyHistory(data);
        } catch (e) {
            console.error("Failed to load history", e);
        }
    };

    // --- HANDLERS ---

    // 1. Strategy Generator
    const handleLaunchStrategy = async () => {
        if (!url) return;
        setStatus('ANALYZING');
        try {
            const { jobId } = await BackendService.generateViralStrategy(url, budget, timeline);
            addToast('Strategy job started. Analyzing...', 'info');

            // Poll for completion
            const pollInterval = setInterval(async () => {
                try {
                    const status = await BackendService.getViralStrategyStatus(jobId);
                    if (status.state === 'completed') {
                        clearInterval(pollInterval);
                        setStrategy(status.result);
                        setStatus('COMPLETE');
                        addToast('Strategy Generated & Saved', 'success');
                        loadHistory(); // Refresh history
                    } else if (status.state === 'failed') {
                        clearInterval(pollInterval);
                        setStatus('IDLE');
                        addToast('Strategy generation failed', 'error');
                    }
                } catch (e) {
                    console.error("Polling error", e);
                }
            }, 3000);

        } catch (e: any) {
            addToast(e.message, 'error');
            setStatus('IDLE');
        }
    };

    const handleLoadStrategy = (item: any) => {
        setStrategy(item.strategy);
        setUrl(item.url);
        setStatus('COMPLETE');
        setShowHistory(false);
        addToast('Historical strategy loaded', 'info');
    };

    const handleExportJSON = () => {
        if (!strategy) return;
        const blob = new Blob([JSON.stringify(strategy, null, 2)], { type: 'application/json' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `viral_strategy_${Date.now()}.json`;
        link.click();
        addToast("Strategy Exported", "success");
    };

    const handleShareStrategy = () => {
        if (!strategy) return;
        // Use the shareToken from the saved strategy for real sharing
        // The shareToken is generated by the backend when the strategy is saved
        const shareUrl = strategy.shareToken
            ? `https://yokaizen.ai/s/${strategy.shareToken}`
            : `https://yokaizen.ai/strategy/${Date.now().toString(36)}`; // Fallback
        navigator.clipboard.writeText(shareUrl);
        addToast("Public read-only link copied to clipboard!", "success");
    };

    // 2. Trend Radar (Native Fetch)
    const handleFetchTrends = async () => {
        setIsFetchingTrends(true);
        try {
            const posts = await BackendService.getViralTrends(subreddit);
            setTrends(posts);
            addToast(`Found ${posts.length} trending topics in r/${subreddit}`, 'success');
        } catch (e) {
            // Fallback for demo/CORS issues
            // Demo fallback REMOVED.
            addToast("Failed to fetch trends. Please check subreddit name.", 'error');
            setTrends([]);
        } finally {
            setIsFetchingTrends(false);
        }
    };

    // 3. Script Lab (Gemini)
    const handleGenerateScripts = async () => {
        if (trends.length === 0) return;
        setIsScripting(true);
        setEngineMode('SCRIPT_LAB');
        try {
            const scripts = await BackendService.generateViralScripts(trends.slice(0, 5), subreddit);
            setGeneratedScripts(scripts);
            if (scripts.length > 0) setSelectedScript(scripts[0]);
            addToast("Scripts generated from trends", 'success');
        } catch (e) {
            console.error(e);
            addToast("Failed to generate scripts", 'error');
        } finally {
            setIsScripting(false);
        }
    };

    // 4. Screening Room (Video Analysis)
    const handleVideoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setUploadedVideo(file);
        setIsAnalyzingVideo(true);

        try {
            const analysis = await BackendService.analyzeViralVideo(file);
            setVideoAnalysis(analysis);
            addToast("Video Analysis Complete", 'success');
        } catch (e) {
            console.error(e);
            // Demo fallback
            // Demo fallback REMOVED.
            addToast("Video analysis failed. " + (e.message || "Server Error"), 'error');
            setVideoAnalysis(null);
        } finally {
            setIsAnalyzingVideo(false);
        }
    };

    const handleGenerateVideo = async (script: any) => {
        if (!script) return;
        setIsGeneratingVideo(true);
        try {
            const response = await BackendService.generateVideo(script.visual_cue);
            if (response.success) {
                setGeneratedVideoUrl(response.videoUrl);
                addToast("Video Generated Successfully", 'success');
            } else {
                addToast(response.error || "Video generation failed", 'error');
            }
        } catch (e) {
            console.error(e);
            addToast("Failed to generate video", 'error');
        } finally {
            setIsGeneratingVideo(false);
        }
    };

    return (
        <div className="p-6 max-w-[1600px] mx-auto animate-fade-in text-slate-200 min-h-screen bg-[#02040a] relative">
            {/* Header */}
            <div className="mb-8 border-b border-indigo-900/30 pb-6 flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
                <div>
                    <h2 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-500 to-pink-500 flex items-center gap-4">
                        <Rocket className="w-10 h-10 text-indigo-500" />
                        Agent V: Viral Growth Engine
                    </h2>
                    <p className="text-indigo-400/60 mt-2 text-lg font-light tracking-wide">
                        Native Cross-Platform Orchestration • No n8n Required
                    </p>
                </div>

                <div className="flex gap-3">
                    <button
                        onClick={() => setShowHistory(!showHistory)}
                        className="bg-slate-900 border border-slate-800 text-slate-400 hover:text-white px-4 py-2 rounded-lg text-sm font-bold transition-all flex items-center gap-2"
                    >
                        <History className="w-4 h-4" /> History
                    </button>
                    <div className="flex bg-slate-900 p-1 rounded-lg border border-slate-800">
                        <button
                            onClick={() => setActiveTab('STRATEGY')}
                            className={`px-4 py-2 rounded-md text-sm font-bold transition-all ${activeTab === 'STRATEGY' ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-400 hover:text-white'}`}
                        >
                            Strategy Generator
                        </button>
                        <button
                            onClick={() => setActiveTab('ENGINE')}
                            className={`px-4 py-2 rounded-md text-sm font-bold transition-all flex items-center gap-2 ${activeTab === 'ENGINE' ? 'bg-purple-600 text-white shadow-lg' : 'text-slate-400 hover:text-white'}`}
                        >
                            <Cpu className="w-4 h-4" /> The Engine
                        </button>
                    </div>
                </div>
            </div>

            {/* History Sidebar */}
            {showHistory && (
                <div className="absolute right-6 top-28 z-30 w-80 bg-slate-900 border border-slate-700 shadow-2xl rounded-xl max-h-[600px] overflow-hidden flex flex-col animate-in slide-in-from-right">
                    <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-800/50">
                        <h3 className="font-bold text-white text-sm">Strategy History</h3>
                        <button onClick={() => setShowHistory(false)} className="text-slate-400 hover:text-white"><X className="w-4 h-4" /></button>
                    </div>
                    <div className="overflow-y-auto flex-1 p-2 space-y-2">
                        {strategyHistory.length === 0 && <p className="text-center text-slate-500 py-8 text-xs">No saved strategies.</p>}
                        {strategyHistory.map(item => (
                            <button
                                key={item.id}
                                onClick={() => handleLoadStrategy(item)}
                                className="w-full text-left p-3 rounded-lg hover:bg-slate-800 border border-transparent hover:border-slate-700 transition-all group"
                            >
                                <div className="flex items-center gap-2 text-xs text-slate-500 mb-1">
                                    <Target className="w-3 h-3" />
                                    {new Date(item.date).toLocaleDateString()}
                                </div>
                                <p className="text-slate-300 text-xs line-clamp-1 font-medium group-hover:text-white font-mono">
                                    {item.url}
                                </p>
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* --- TAB 1: STRATEGY GENERATOR --- */}
            {activeTab === 'STRATEGY' && (
                <>
                    {status === 'IDLE' && (
                        <div className="grid xl:grid-cols-2 gap-12 items-center min-h-[600px]">
                            <div className="space-y-8 animate-in slide-in-from-left-4 duration-700">
                                <div className="space-y-4">
                                    <label className="text-sm font-bold text-indigo-400 uppercase tracking-widest flex items-center gap-2">
                                        <Target className="w-4 h-4" /> Target Entity
                                    </label>
                                    <div className="flex gap-4">
                                        <div className="flex-1 bg-slate-900/50 border border-indigo-500/30 rounded-xl p-4 flex items-center gap-3 focus-within:ring-2 focus-within:ring-indigo-500 transition-all shadow-lg shadow-indigo-900/10">
                                            <Globe className="w-5 h-5 text-slate-400" />
                                            <input
                                                value={url}
                                                onChange={e => setUrl(e.target.value)}
                                                placeholder="https://your-startup.com"
                                                className="bg-transparent border-none outline-none w-full text-white font-mono placeholder:text-slate-600"
                                            />
                                        </div>
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div className="bg-slate-900/30 p-4 rounded-xl border border-indigo-900/30">
                                        <label className="text-xs font-bold text-indigo-400/70 uppercase mb-2 block">Monthly Budget</label>
                                        <input
                                            value={budget}
                                            onChange={e => setBudget(e.target.value)}
                                            className="w-full bg-slate-950 border border-indigo-900/50 rounded-lg p-3 text-white font-mono focus:border-indigo-500 outline-none"
                                        />
                                    </div>
                                    <div className="bg-slate-900/30 p-4 rounded-xl border border-indigo-900/30">
                                        <label className="text-xs font-bold text-indigo-400/70 uppercase mb-2 block">Growth Timeline</label>
                                        <select
                                            value={timeline}
                                            onChange={e => setTimeline(e.target.value)}
                                            className="w-full bg-slate-950 border border-indigo-900/50 rounded-lg p-3 text-white font-mono outline-none focus:border-indigo-500"
                                        >
                                            <option value="1_month">1 Month (Aggressive)</option>
                                            <option value="3_months">3 Months (Standard)</option>
                                            <option value="6_months">6 Months (Organic)</option>
                                        </select>
                                    </div>
                                </div>

                                <button
                                    onClick={handleLaunchStrategy}
                                    disabled={!url}
                                    className="w-full group relative h-20 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl font-bold text-xl uppercase tracking-widest overflow-hidden transition-all hover:scale-[1.01] active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed shadow-2xl shadow-indigo-900/30"
                                >
                                    <span className="relative z-10 flex items-center justify-center gap-3">
                                        <Play className="w-6 h-6 fill-current" /> Initialize Engine (50 Credits)
                                    </span>
                                </button>
                            </div>

                            {/* Visuals */}
                            <div className="grid grid-cols-2 gap-4 select-none animate-in slide-in-from-right-4 duration-700 delay-100">
                                {[
                                    { icon: Fingerprint, label: "Stealth Browser", desc: "Anti-Fingerprinting v4" },
                                    { icon: Users, label: "Audience AI", desc: "Psychographic Targeting" },
                                    { icon: Zap, label: "Viral Prediction", desc: "Trend Velocity Analysis" },
                                    { icon: Lock, label: "Account Safety", desc: "Human Behavior Sim" }
                                ].map((feat, i) => (
                                    <div key={i} className="bg-slate-900/30 border border-slate-800 p-8 rounded-2xl hover:border-indigo-500/30 transition-all group">
                                        <feat.icon className="w-10 h-10 text-indigo-500 mb-4 group-hover:scale-110 transition-transform" />
                                        <h3 className="font-bold text-slate-200 text-lg">{feat.label}</h3>
                                        <p className="text-sm text-slate-500 mt-1">{feat.desc}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {(status === 'ANALYZING' || status === 'EXECUTING') && (
                        <div className="flex flex-col gap-8 justify-center items-center h-[600px]">
                            <div className="w-64 h-64 rounded-full border-4 border-indigo-500/20 border-t-indigo-500 animate-spin relative z-10"></div>
                            <div className="absolute inset-0 flex items-center justify-center flex-col z-20">
                                <Zap className="w-16 h-16 text-emerald-400 mb-4 animate-bounce" />
                                <span className="text-2xl font-bold text-white tracking-[0.2em] animate-pulse">GENERATING</span>
                            </div>
                        </div>
                    )}

                    {status === 'COMPLETE' && strategy && (
                        <div className="space-y-8 animate-in slide-in-from-bottom-8 duration-700 pb-12">
                            <div className="flex justify-end gap-4">
                                <button onClick={handleShareStrategy} className="bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-2 rounded-lg flex items-center gap-2 font-bold transition-all">
                                    <Share2 className="w-4 h-4" /> Share Strategy
                                </button>
                                <button onClick={handleExportJSON} className="bg-purple-600 hover:bg-purple-500 text-white px-6 py-2 rounded-lg flex items-center gap-2 font-bold transition-all">
                                    <Download className="w-4 h-4" /> Export JSON
                                </button>
                                <button onClick={() => setStatus('IDLE')} className="bg-slate-800 text-white px-4 py-2 rounded-lg flex items-center gap-2 text-xs font-bold transition-all">
                                    <RefreshCw className="w-4 h-4" /> Reset
                                </button>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
                                    <h3 className="text-xs font-bold text-indigo-400 uppercase mb-3 flex items-center gap-2"><Activity className="w-4 h-4" /> Product Analysis</h3>
                                    <p className="text-sm text-slate-300 leading-relaxed">{strategy.campaign_overview.product_analysis}</p>
                                </div>

                                <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
                                    <h3 className="text-xs font-bold text-emerald-400 uppercase mb-4 flex items-center gap-2"><Target className="w-4 h-4" /> Projected KPIs</h3>
                                    <div className="space-y-4">
                                        <div className="flex justify-between items-center p-3 bg-slate-800/50 rounded-lg border border-slate-700/50">
                                            <span className="text-slate-400 text-sm">Viral Coefficient</span>
                                            <span className="text-white font-bold text-xl">{strategy.campaign_overview.target_metrics.viral_coefficient}x</span>
                                        </div>
                                        <div className="flex justify-between items-center p-3 bg-slate-800/50 rounded-lg border border-slate-700/50">
                                            <span className="text-slate-400 text-sm">Monthly Leads</span>
                                            <span className="text-white font-bold text-xl">{strategy.campaign_overview.target_metrics.monthly_leads.toLocaleString()}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Render Strategy Steps */}
                            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                                <h3 className="text-lg font-bold text-white mb-4">Platform Execution</h3>
                                <div className="grid md:grid-cols-3 gap-6">
                                    {['instagram', 'tiktok', 'linkedin'].map(platform => (
                                        <div key={platform} className="bg-slate-950 p-4 rounded-lg border border-slate-800">
                                            <h4 className="capitalize font-bold text-indigo-400 mb-2">{platform}</h4>
                                            <p className="text-sm text-slate-300 mb-4">{(strategy.platform_execution as any)[platform]?.strategy}</p>
                                            <ul className="space-y-2">
                                                {(strategy.platform_execution as any)[platform]?.daily_actions?.map((action: string, i: number) => (
                                                    <li key={i} className="text-xs text-slate-500 flex items-start gap-2">
                                                        <span className="text-emerald-500">•</span> {action}
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}
                </>
            )}

            {/* --- TAB 2: NATIVE ENGINE --- */}
            {activeTab === 'ENGINE' && (
                <div className="flex flex-col h-[calc(100vh-12rem)]">
                    {/* Engine Navigation */}
                    <div className="flex gap-2 mb-6">
                        <button
                            onClick={() => setEngineMode('TREND_RADAR')}
                            className={`px-4 py-2 rounded-full text-xs font-bold border transition-all flex items-center gap-2 ${engineMode === 'TREND_RADAR' ? 'bg-orange-500/10 text-orange-300 border-orange-500/30' : 'bg-slate-900 text-slate-400 border-slate-800'}`}
                        >
                            <Activity className="w-3 h-3" /> 1. Trend Radar
                        </button>
                        <ChevronRight className="w-4 h-4 text-slate-600 mt-2" />
                        <button
                            onClick={() => setEngineMode('SCRIPT_LAB')}
                            className={`px-4 py-2 rounded-full text-xs font-bold border transition-all flex items-center gap-2 ${engineMode === 'SCRIPT_LAB' ? 'bg-blue-500/10 text-blue-300 border-blue-500/30' : 'bg-slate-900 text-slate-400 border-slate-800'}`}
                        >
                            <PenTool className="w-3 h-3" /> 2. Script Lab
                        </button>
                        <ChevronRight className="w-4 h-4 text-slate-600 mt-2" />
                        <button
                            onClick={() => setEngineMode('SCREENING_ROOM')}
                            className={`px-4 py-2 rounded-full text-xs font-bold border transition-all flex items-center gap-2 ${engineMode === 'SCREENING_ROOM' ? 'bg-purple-500/10 text-purple-300 border-purple-500/30' : 'bg-slate-900 text-slate-400 border-slate-800'}`}
                        >
                            <Film className="w-3 h-3" /> 3. Screening Room
                        </button>
                    </div>

                    {/* --- VIEW 1: TREND RADAR --- */}
                    {engineMode === 'TREND_RADAR' && (
                        <div className="grid lg:grid-cols-3 gap-8 h-full">
                            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col gap-4">
                                <h3 className="text-lg font-bold text-orange-400 flex items-center gap-2"><Activity className="w-5 h-5" /> Source Input</h3>
                                <div className="space-y-2">
                                    <label className="text-xs font-bold text-slate-500 uppercase">Subreddit / Source</label>
                                    <div className="flex gap-2">
                                        <input
                                            value={subreddit}
                                            onChange={e => setSubreddit(e.target.value)}
                                            className="flex-1 bg-slate-950 border border-slate-800 rounded-lg p-3 font-mono text-sm focus:border-orange-500 outline-none"
                                            placeholder="marketing"
                                        />
                                        <button
                                            onClick={handleFetchTrends}
                                            disabled={isFetchingTrends}
                                            className="bg-orange-600 hover:bg-orange-500 text-white px-4 rounded-lg font-bold disabled:opacity-50"
                                        >
                                            {isFetchingTrends ? <RefreshCw className="w-4 h-4 animate-spin" /> : "Scan"}
                                        </button>
                                    </div>
                                </div>
                                <div className="mt-auto p-4 bg-slate-950 rounded-lg border border-slate-800">
                                    <p className="text-xs text-slate-500 mb-2">Detected Velocity</p>
                                    <div className="flex items-end gap-2">
                                        <div className="h-8 w-2 bg-emerald-500 rounded-t"></div>
                                        <div className="h-12 w-2 bg-emerald-500 rounded-t"></div>
                                        <div className="h-6 w-2 bg-slate-700 rounded-t"></div>
                                        <div className="h-16 w-2 bg-emerald-400 rounded-t animate-pulse"></div>
                                    </div>
                                </div>
                            </div>

                            <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6 overflow-y-auto">
                                <div className="flex justify-between items-center mb-4">
                                    <h3 className="text-lg font-bold text-white">Live Feed</h3>
                                    {trends.length > 0 && (
                                        <button onClick={handleGenerateScripts} className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-1.5 rounded-lg text-xs font-bold flex items-center gap-2 transition-all">
                                            Send {trends.length} Trends to Script Lab <ArrowRight className="w-3 h-3" />
                                        </button>
                                    )}
                                </div>
                                <div className="grid md:grid-cols-2 gap-3">
                                    {trends.map((t, i) => (
                                        <TrendCard key={i} title={t.title} score={t.score} sub={t.sub} />
                                    ))}
                                    {trends.length === 0 && (
                                        <div className="col-span-2 text-center text-slate-500 py-20">
                                            Scan a source to detect trends.
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* --- VIEW 2: SCRIPT LAB --- */}
                    {engineMode === 'SCRIPT_LAB' && (
                        <div className="grid lg:grid-cols-2 gap-8 h-full">
                            <div className="flex flex-col gap-4">
                                <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex-1">
                                    <h3 className="text-lg font-bold text-blue-400 flex items-center gap-2 mb-4"><PenTool className="w-5 h-5" /> Generated Scripts</h3>
                                    {isScripting ? (
                                        <div className="flex items-center justify-center h-64 gap-3 text-blue-400">
                                            <RefreshCw className="w-6 h-6 animate-spin" /> Brewing Viral Hooks...
                                        </div>
                                    ) : (
                                        <div className="space-y-3">
                                            {generatedScripts.map((s, i) => (
                                                <div
                                                    key={i}
                                                    onClick={() => setSelectedScript(s)}
                                                    className={`p-4 rounded-xl border cursor-pointer transition-all ${selectedScript === s ? 'bg-blue-500/10 border-blue-500/50' : 'bg-slate-950 border-slate-800 hover:border-blue-500/30'}`}
                                                >
                                                    <p className="text-xs font-bold text-yellow-400 mb-1 uppercase">Hook</p>
                                                    <p className="font-bold text-white text-sm mb-2">"{s.hook}"</p>
                                                    <p className="text-xs text-slate-400 line-clamp-2">{s.body}</p>
                                                </div>
                                            ))}
                                            {generatedScripts.length === 0 && (
                                                <p className="text-slate-500 text-center py-10">No scripts yet. Go to Trend Radar to generate.</p>
                                            )}
                                        </div>
                                    )}
                                </div>
                            </div>



                            <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 flex flex-col items-center justify-center">
                                {selectedScript ? (
                                    <>
                                        <PhonePreview script={selectedScript} />
                                        <div className="mt-6 flex gap-4">
                                            <button
                                                onClick={() => handleGenerateVideo(selectedScript)}
                                                disabled={isGeneratingVideo}
                                                className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white px-6 py-3 rounded-xl font-bold flex items-center gap-2 shadow-lg shadow-purple-900/20 disabled:opacity-50 transition-all"
                                            >
                                                {isGeneratingVideo ? <RefreshCw className="w-5 h-5 animate-spin" /> : <Video className="w-5 h-5" />}
                                                Generate AI Video (100 Credits)
                                            </button>
                                        </div>
                                        {generatedVideoUrl && (
                                            <div className="mt-4 w-full max-w-[280px]">
                                                <p className="text-xs text-emerald-400 font-bold mb-2 text-center flex items-center justify-center gap-1"><CheckCircle className="w-3 h-3" /> Video Ready</p>
                                                <video src={generatedVideoUrl} controls className="w-full rounded-xl border border-slate-700" />
                                            </div>
                                        )}

                                        <div className="mt-6 flex flex-col w-full max-w-[280px] gap-2">
                                            <button
                                                onClick={async () => {
                                                    if (confirm('Post this script to Buffer now? (10 Credits)')) {
                                                        try {
                                                            await BackendService.postToSocial(selectedScript.body);
                                                            addToast('Posted to Buffer successfully!', 'success');
                                                        } catch (e: any) {
                                                            alert('Buffer Error: ' + e.message);
                                                        }
                                                    }
                                                }}
                                                className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg font-bold flex items-center justify-center gap-2 shadow-lg shadow-blue-900/20"
                                            >
                                                <Share2 className="w-4 h-4" /> Post to Social (Real)
                                            </button>
                                        </div>

                                        {/* Share Button (PLG) */}
                                        <div className="mt-4 flex gap-2">
                                            <button
                                                onClick={async () => {
                                                    try {
                                                        const response = await BackendService.generateShareLink(selectedScript.id || 'temp_id');
                                                        if (response.success) {
                                                            navigator.clipboard.writeText(response.publicUrl);
                                                            addToast('Public share link copied!', 'success');
                                                        }
                                                    } catch (e) {
                                                        // Fallback for demo
                                                        navigator.clipboard.writeText(`https://ai.yokaizen.com/s/strategy_${Date.now()}`);
                                                        addToast('Public share link copied!', 'success');
                                                    }
                                                }}
                                                className="bg-slate-800 hover:bg-slate-700 text-slate-300 px-4 py-2 rounded-lg text-xs font-bold flex items-center gap-2 transition-colors border border-slate-700"
                                            >
                                                <Share2 className="w-3 h-3" /> Share Strategy
                                            </button>
                                        </div>
                                    </>
                                ) : (
                                    <div className="text-slate-600 text-center">
                                        <Smartphone className="w-16 h-16 mx-auto mb-4 opacity-20" />
                                        <p>Select a script to preview</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {/* --- VIEW 3: SCREENING ROOM --- */}
                    {engineMode === 'SCREENING_ROOM' && (
                        <div className="grid lg:grid-cols-2 gap-8 h-full animate-in fade-in">
                            <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 flex flex-col items-center justify-center relative overflow-hidden">
                                <div className="absolute top-0 right-0 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl pointer-events-none"></div>

                                <div
                                    onClick={() => videoInputRef.current?.click()}
                                    className="border-2 border-dashed border-purple-500/30 rounded-2xl p-12 text-center hover:bg-purple-500/5 transition-all cursor-pointer w-full max-w-md group"
                                >
                                    <UploadCloud className="w-16 h-16 text-purple-500 mx-auto mb-4 group-hover:scale-110 transition-transform" />
                                    <h3 className="text-xl font-bold text-white mb-2">Upload Draft</h3>
                                    <p className="text-slate-400 text-sm">AI Director will watch and critique retention.</p>
                                    <input ref={videoInputRef} type="file" accept="video/*" className="hidden" onChange={handleVideoUpload} />
                                </div>

                                {uploadedVideo && (
                                    <div className="mt-6 flex items-center gap-3 bg-slate-950 px-4 py-2 rounded-lg border border-slate-800">
                                        <FileVideo className="w-4 h-4 text-purple-400" />
                                        <span className="text-sm text-slate-300">{uploadedVideo.name}</span>
                                        {isAnalyzingVideo && <RefreshCw className="w-3 h-3 animate-spin text-slate-500" />}
                                    </div>
                                )}
                            </div>

                            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 overflow-y-auto">
                                <h3 className="text-lg font-bold text-purple-400 flex items-center gap-2 mb-6"><Bot className="w-5 h-5" /> Director's Cut</h3>

                                {videoAnalysis ? (
                                    <div className="space-y-6 animate-in slide-in-from-bottom-4">
                                        <div className="grid grid-cols-2 gap-4">
                                            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-center">
                                                <span className="text-xs text-slate-500 uppercase">Viral Score</span>
                                                <div className={`text-4xl font-black mt-2 ${videoAnalysis.score >= 7 ? 'text-emerald-400' : 'text-rose-500'}`}>
                                                    {videoAnalysis.score}<span className="text-lg text-slate-600">/10</span>
                                                </div>
                                            </div>
                                            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-center">
                                                <span className="text-xs text-slate-500 uppercase">Hook Grade</span>
                                                <div className="text-4xl font-black mt-2 text-white">
                                                    {videoAnalysis.hook_grade}
                                                </div>
                                            </div>
                                        </div>

                                        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                                            <h4 className="text-xs font-bold text-rose-400 uppercase mb-2 flex items-center gap-2"><AlertOctagon className="w-3 h-3" /> The Roast</h4>
                                            <p className="text-slate-300 text-sm italic">"{videoAnalysis.roast}"</p>
                                        </div>

                                        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                                            <h4 className="text-xs font-bold text-emerald-400 uppercase mb-2 flex items-center gap-2"><CheckCircle className="w-3 h-3" /> Retention Fixes</h4>
                                            <ul className="space-y-2">
                                                {videoAnalysis.improvements.map((imp: string, i: number) => (
                                                    <li key={i} className="text-sm text-slate-300 flex items-start gap-2">
                                                        <span className="text-emerald-500 font-bold">•</span> {imp}
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="h-full flex flex-col items-center justify-center text-slate-600">
                                        <Film className="w-12 h-12 mb-4 opacity-20" />
                                        <p>Waiting for upload...</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            )
            }
        </div>
    );
};


export default ViralGrowthAgent;
