import React, { useState, useEffect, useRef } from 'react';
import { 
    Bot, ArrowRight, Activity, Terminal, CheckCircle2,
    Shield, Globe, Database, Download, Users, Plus, Upload, Play,
    Loader2, Search, Target, Key, Trash2, Cookie, AlertTriangle
} from 'lucide-react';
import { cn } from '../lib/utils';
import { useAuthStore } from '../stores/auth-store';
import { api } from '../lib/api';

type TabType = 'upload' | 'active' | 'community' | 'accounts';

interface JobStatus {
    job_id: string;
    status: string;
    total_targets: number;
    processed: number;
    errors: number;
    progress_pct: number;
    elapsed_seconds: number;
    rate_per_second: number;
}

interface SavedAccount {
    id: string;
    platform: string;
    username: string;
    status: string;
    has_password: boolean;
    has_cookies: boolean;
    proxy_url: string | null;
    last_error: string | null;
    created_at: string | null;
}

interface AccountStats {
    accounts: SavedAccount[];
    total: number;
    by_platform: { instagram: number; twitter: number; tiktok: number };
}

export default function ScraperDashboard() {
    const { user } = useAuthStore();
    const [activeTab, setActiveTab] = useState<TabType>('upload');
    const [file, setFile] = useState<File | null>(null);
    const [isShared, setIsShared] = useState(false);
    
    // Job State
    const [currentJobId, setCurrentJobId] = useState<string | null>(null);
    const [logs, setLogs] = useState<string[]>([]);
    const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
    const [isLaunching, setIsLaunching] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    // Community Date State
    const [communityData, setCommunityData] = useState<any[]>([]);
    const [communityLoading, setCommunityLoading] = useState(false);

    // Account Management State
    const [savedAccounts, setSavedAccounts] = useState<AccountStats | null>(null);
    const [accountsLoading, setAccountsLoading] = useState(false);
    const [showAddForm, setShowAddForm] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [newAccount, setNewAccount] = useState({
        platform: 'instagram',
        username: '',
        password: '',
        cookie_string: '',
        proxy_url: '',
    });
    const [authMode, setAuthMode] = useState<'cookie' | 'password'>('cookie');

    // Scroll logs to bottom
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [logs]);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            setFile(e.target.files[0]);
        }
    };

    const fetchCommunityData = async () => {
        setCommunityLoading(true);
        try {
            const res = await api.get('/scraper/community');
            setCommunityData(res.items || []);
        } catch (err) {
            console.error("Failed to load community DB", err);
        } finally {
            setCommunityLoading(false);
        }
    };

    const fetchAccounts = async () => {
        setAccountsLoading(true);
        try {
            const res = await api.get('/scraper/accounts/mine');
            setSavedAccounts(res as unknown as AccountStats);
        } catch (err) {
            console.error('Failed to load accounts', err);
        } finally {
            setAccountsLoading(false);
        }
    };

    const saveAccount = async () => {
        setIsSaving(true);
        try {
            await api.post('/scraper/accounts/save', {
                platform: newAccount.platform,
                username: newAccount.username,
                password: authMode === 'password' ? newAccount.password : undefined,
                cookie_string: authMode === 'cookie' ? newAccount.cookie_string : undefined,
                proxy_url: newAccount.proxy_url || undefined,
            });
            setNewAccount({ platform: 'instagram', username: '', password: '', cookie_string: '', proxy_url: '' });
            setShowAddForm(false);
            fetchAccounts();
        } catch (err: any) {
            console.error('Failed to save account', err);
        } finally {
            setIsSaving(false);
        }
    };

    const deleteAccount = async (id: string) => {
        try {
            await api.delete(`/scraper/accounts/${id}`);
            fetchAccounts();
        } catch (err) {
            console.error('Failed to delete account', err);
        }
    };

    useEffect(() => {
        if (activeTab === 'community') {
            fetchCommunityData();
        }
        if (activeTab === 'accounts') {
            fetchAccounts();
        }
    }, [activeTab]);

    const launchScraper = async () => {
        if (!file) return;
        setIsLaunching(true);
        setLogs(prev => [...prev, '> Initializing DeerFlow Master Agent...']);
        setLogs(prev => [...prev, '> Establishing Camoufox Anti-Detect Bridge...']);
        
        const formData = new FormData();
        formData.append('file', file);
        // Note: For a complete implementation, the backend needs to parse these fields from Form(...)
        // We'll append them for when it's ready.
        formData.append('is_shared', isShared ? 'true' : 'false');
        
        try {
            const res = await api.post('/scraper/launch', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            
            setLogs(prev => [...prev, `> Job Created: ${res.job_id} | Targets: ${res.total_targets}`]);
            setCurrentJobId(res.job_id);
            setActiveTab('active');
            startSseStream(res.job_id);
        } catch (err) {
            setLogs(prev => [...prev, `> [ERROR] Failed to launch job. ${err}`]);
        } finally {
            setIsLaunching(false);
        }
    };

    const startSseStream = (jobId: string) => {
        setLogs(prev => [...prev, `> Conecting to EventStream /status/${jobId}...`]);
        
        // Use native EventSource or a fetch wrapper for SSE. This is a simplified fetch approach
        // since we use auth headers.
        const source = new EventSource(`${api.defaults.baseURL}/scraper/status/${jobId}?token=${user?.token}`);
        
        source.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                
                if (data.event === 'stream_end') {
                    setLogs(prev => [...prev, `> [SYSTEM] Transmission End.`]);
                    source.close();
                    return;
                }
                
                if (data.event === 'job_completed') {
                    setLogs(prev => [...prev, `> [SUCCESS] Job completed! Saved to DB: ${data.saved_to_db || 0}`]);
                    source.close();
                }

                // Update metrics if available
                if (data.progress_pct !== undefined) {
                    setJobStatus(data as JobStatus);
                }
                
                // Format log message
                const logMsg = `> [${new Date().toISOString().split('T')[1].slice(0, 8)}] [${data.event?.toUpperCase() || 'INFO'}] ${JSON.stringify(data)}`;
                setLogs(prev => [...prev, logMsg]);
                
            } catch (e) {
                setLogs(prev => [...prev, '> [RAW] ' + event.data]);
            }
        };

        source.onerror = (err) => {
            setLogs(prev => [...prev, `> [SYSTEM ERROR] Connection lost.`]);
            source.close();
        };
    };

    const downloadResults = async () => {
        if (!currentJobId) return;
        try {
            const res = await api.get(`/scraper/results/${currentJobId}?format=csv`, { responseType: 'blob' });
            const url = window.URL.createObjectURL(new Blob([res]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `influencers_${currentJobId}.csv`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (error) {
            console.error(error);
        }
    };

    return (
        <div className="min-h-screen pt-20 pb-12 px-4 sm:px-6 lg:px-8 bg-[#020202]">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-4">
                    <div>
                        <div className="flex items-center gap-3 mb-2">
                            <Bot className="w-8 h-8 text-[#00f0ff]" />
                            <h1 className="text-3xl font-bold font-mono text-white tracking-widest uppercase">
                                INFLUENCER<span className="text-brand-purple">_SCRAPER</span>
                            </h1>
                        </div>
                        <p className="text-sm font-mono text-gray-400">
                            Distributed Stealth Extraction Engine via DeerFlow // OpenClaw Gateway
                        </p>
                    </div>
                </div>

                {/* Main Content Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                    {/* Left Sidebar - Navigation */}
                    <div className="lg:col-span-1 space-y-2">
                         <button
                            onClick={() => setActiveTab('upload')}
                            className={cn(
                                "w-full flex items-center p-4 rounded-xl font-mono text-sm tracking-widest transition-all",
                                activeTab === 'upload' 
                                    ? "bg-brand-purple border border-brand-purple text-white shadow-[0_0_15px_rgba(168,85,247,0.3)]" 
                                    : "bg-[#111] border border-white/10 text-gray-400 hover:text-white hover:bg-white/5"
                            )}
                        >
                            <Upload className="w-4 h-4 mr-3" />
                            TARGET DEPLOY
                        </button>
                        <button
                            onClick={() => setActiveTab('active')}
                            className={cn(
                                "w-full flex items-center p-4 rounded-xl font-mono text-sm tracking-widest transition-all",
                                activeTab === 'active' 
                                    ? "bg-[#00f0ff]/10 border border-[#00f0ff] text-[#00f0ff] shadow-[0_0_15px_rgba(0,240,255,0.2)]" 
                                    : "bg-[#111] border border-white/10 text-gray-400 hover:text-white hover:bg-white/5"
                            )}
                        >
                            <Activity className="w-4 h-4 mr-3" />
                            ACTIVE JOBS
                        </button>
                        <button
                            onClick={() => setActiveTab('community')}
                            className={cn(
                                "w-full flex items-center p-4 rounded-xl font-mono text-sm tracking-widest transition-all",
                                activeTab === 'community' 
                                    ? "bg-emerald-500/10 border border-emerald-500 text-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.2)]" 
                                    : "bg-[#111] border border-white/10 text-gray-400 hover:text-white hover:bg-white/5"
                            )}
                        >
                            <Globe className="w-4 h-4 mr-3" />
                            COMMUNITY DB
                        </button>
                        <button
                            onClick={() => setActiveTab('accounts')}
                            className={cn(
                                "w-full flex items-center p-4 rounded-xl font-mono text-sm tracking-widest transition-all",
                                activeTab === 'accounts' 
                                    ? "bg-amber-500/10 border border-amber-500 text-amber-400 shadow-[0_0_15px_rgba(245,158,11,0.2)]" 
                                    : "bg-[#111] border border-white/10 text-gray-400 hover:text-white hover:bg-white/5"
                            )}
                        >
                            <Key className="w-4 h-4 mr-3" />
                            ACCOUNTS
                            {savedAccounts && (
                                <span className="ml-auto text-xs bg-white/10 px-2 py-0.5 rounded-full">
                                    {savedAccounts.total}
                                </span>
                            )}
                        </button>
                    </div>

                    {/* Right Content Area */}
                    <div className="lg:col-span-3">
                        
                        {/* TAB: UPLOAD */}
                        {activeTab === 'upload' && (
                            <div className="bg-[#111] border border-white/10 rounded-2xl p-6 lg:p-8">
                                <h2 className="text-xl font-mono font-bold text-white mb-6 uppercase tracking-widest border-b border-white/10 pb-4 flex items-center gap-2">
                                    <Target className="w-5 h-5 text-brand-purple" />
                                    Launch Extraction Swarm
                                </h2>
                                
                                <div className="space-y-6">
                                    {/* File Dropzone */}
                                    <div className="border-2 border-dashed border-white/20 rounded-xl p-10 text-center hover:border-brand-purple/50 hover:bg-brand-purple/5 transition-all cursor-pointer relative">
                                        <input 
                                            type="file" 
                                            accept=".csv" 
                                            onChange={handleFileChange}
                                            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                        />
                                        <Database className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                                        <p className="text-white font-mono font-bold text-lg mb-2">
                                            {file ? file.name : 'DROP TARGET.CSV HERE'}
                                        </p>
                                        <p className="text-gray-500 text-sm font-mono">
                                            Format: column1(handle), column2(platform)
                                        </p>
                                    </div>

                                    {/* Options */}
                                    <div className="bg-[#0A0A0A] border border-white/5 rounded-xl p-5">
                                        <div className="flex items-start gap-4">
                                            <div className="mt-1">
                                                <input 
                                                    type="checkbox" 
                                                    id="share-db" 
                                                    checked={isShared}
                                                    onChange={(e) => setIsShared(e.target.checked)}
                                                    className="w-5 h-5 rounded border-white/20 bg-black text-[#00f0ff] focus:ring-[#00f0ff]/50 focus:ring-offset-0"
                                                />
                                            </div>
                                            <div>
                                                <label htmlFor="share-db" className="text-white font-bold font-mono block mb-1">
                                                    SHARE TO GLOBAL COMMUNITY DB
                                                </label>
                                                <p className="text-gray-400 text-sm font-mono max-w-xl">
                                                    Opting in allows your extracted targets to enter the Global Pool. 
                                                    As a reward, you gain access to the data extracted by the rest of the Momentaic collective. 
                                                    (Give 1, Get 1000).
                                                </p>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Action */}
                                    <button
                                        onClick={launchScraper}
                                        disabled={!file || isLaunching}
                                        className="w-full py-4 bg-gradient-to-r from-brand-purple to-brand-cyan hover:opacity-90 disabled:opacity-50 text-white font-mono font-bold tracking-[0.2em] rounded-xl flex items-center justify-center transition-all"
                                    >
                                        {isLaunching ? (
                                            <><Loader2 className="w-5 h-5 mr-3 animate-spin" /> INITIATING...</>
                                        ) : (
                                            <><Play className="w-5 h-5 mr-3" /> LAUNCH SWARM</>
                                        )}
                                    </button>
                                </div>
                            </div>
                        )}

                        {/* TAB: ACTIVE JOBS (TERMINAL VIEW) */}
                        {activeTab === 'active' && (
                            <div className="bg-[#111] border border-white/10 rounded-2xl flex flex-col overflow-hidden" style={{ height: '600px' }}>
                                {/* HUD Stats */}
                                <div className="p-4 border-b border-white/10 bg-[#0A0A0A] grid grid-cols-2 md:grid-cols-4 gap-4">
                                    <div className="bg-black/50 border border-[#00f0ff]/20 p-3 rounded-lg">
                                        <div className="text-[10px] text-gray-500 font-mono tracking-widest mb-1">STATUS</div>
                                        <div className="text-white font-bold font-mono uppercase text-sm flex items-center gap-2">
                                            {jobStatus?.status === 'running' ? (
                                                <><span className="w-2 h-2 rounded-full bg-[#00f0ff] animate-pulse"></span> RUNNING</>
                                            ) : jobStatus?.status || 'IDLE'}
                                        </div>
                                    </div>
                                    <div className="bg-black/50 border border-white/10 p-3 rounded-lg">
                                        <div className="text-[10px] text-gray-500 font-mono tracking-widest mb-1">PROCESSED</div>
                                        <div className="text-[#00f0ff] font-bold font-mono text-lg">
                                            {jobStatus ? `${jobStatus.processed} / ${jobStatus.total_targets}` : '0 / 0'}
                                        </div>
                                    </div>
                                    <div className="bg-black/50 border border-white/10 p-3 rounded-lg">
                                        <div className="text-[10px] text-gray-500 font-mono tracking-widest mb-1">ACCURACY</div>
                                        <div className={cn("font-bold font-mono text-lg", (jobStatus?.errors || 0) > 0 ? "text-yellow-500" : "text-emerald-500")}>
                                            {jobStatus ? `${(100 - (jobStatus.errors / jobStatus.processed * 100) || 100).toFixed(1)}%` : '100%'}
                                        </div>
                                    </div>
                                    <div className="bg-black/50 border border-white/10 p-3 rounded-lg">
                                        <div className="text-[10px] text-gray-500 font-mono tracking-widest mb-1">RATE LIMITS</div>
                                        <div className="text-emerald-500 font-bold font-mono text-lg">0</div>
                                    </div>
                                </div>

                                {/* Terminal Console */}
                                <div 
                                    ref={scrollRef}
                                    className="flex-1 bg-black p-4 overflow-y-auto font-mono text-sm"
                                >
                                    {logs.length === 0 ? (
                                        <div className="text-gray-600 italic">No active session...</div>
                                    ) : (
                                        logs.map((log, i) => (
                                            <div key={i} className="mb-1">
                                                <span className="text-[#00f0ff] mr-2">root@deerflow:~#</span>
                                                <span className={
                                                    log.includes('[ERROR]') ? 'text-red-500' :
                                                    log.includes('[SUCCESS]') ? 'text-emerald-500' :
                                                    log.includes('[RUNNING]') ? 'text-yellow-500' :
                                                    'text-gray-300'
                                                }>{log}</span>
                                            </div>
                                        ))
                                    )}
                                </div>

                                {/* Bottom Action */}
                                <div className="p-4 border-t border-white/10 bg-[#0A0A0A] flex justify-between items-center">
                                    <div className="text-gray-500 font-mono text-xs hidden md:block">
                                        <Shield className="w-3 h-3 inline mr-1 text-emerald-500" /> Camoufox Proxy Routing Active
                                    </div>
                                    <button 
                                        onClick={downloadResults}
                                        disabled={!currentJobId || jobStatus?.status === 'running'}
                                        className="px-6 py-2 bg-white/5 border border-white/10 hover:bg-white/10 disabled:opacity-50 rounded-lg text-white font-mono font-bold tracking-widest text-xs flex items-center transition-all uppercase"
                                    >
                                        <Download className="w-4 h-4 mr-2" />
                                        EXPORT CSV
                                    </button>
                                </div>
                            </div>
                        )}

                        {/* TAB: COMMUNITY DB */}
                        {activeTab === 'community' && (
                           <div className="bg-[#111] border border-white/10 rounded-2xl p-6 lg:p-8 min-h-[600px] flex flex-col">
                               <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 border-b border-white/10 pb-6">
                                   <h2 className="text-xl font-mono font-bold text-emerald-400 uppercase tracking-widest flex items-center gap-2">
                                       <Globe className="w-5 h-5" />
                                       Global Target Pool
                                   </h2>
                                   
                                   <div className="flex items-center gap-3">
                                       <div className="relative">
                                           <Search className="w-4 h-4 text-gray-500 absolute left-3 top-1/2 -translate-y-1/2" />
                                           <input 
                                                type="text" 
                                                placeholder="Search keywords..." 
                                                className="w-64 pl-9 pr-4 py-2 bg-black border border-white/10 rounded-lg text-sm text-white font-mono focus:outline-none focus:border-brand-purple"
                                            />
                                       </div>
                                       <button className="px-4 py-2 bg-white/5 border border-white/10 text-white font-mono text-xs rounded-lg hover:bg-white/10">
                                           FILTER
                                       </button>
                                   </div>
                               </div>

                               {communityLoading ? (
                                   <div className="flex-1 flex flex-col items-center justify-center text-gray-500 font-mono">
                                       <Loader2 className="w-8 h-8 animate-spin mb-4 text-brand-purple" />
                                       SYNCHRONIZING WITH GLOBAL GRID...
                                   </div>
                               ) : communityData.length === 0 ? (
                                    <div className="flex-1 flex flex-col items-center justify-center text-gray-500 font-mono">
                                        <Database className="w-12 h-12 mb-4 opacity-50" />
                                        NO TARGETS FOUND IN POOL.
                                    </div>
                               ) : (
                                   <div className="flex-1 overflow-x-auto">
                                       <table className="w-full text-left font-mono text-sm border-separate border-spacing-y-2">
                                           <thead>
                                               <tr className="text-gray-500 text-xs tracking-widest">
                                                   <th className="pb-2 font-normal">PLATFORM</th>
                                                   <th className="pb-2 font-normal">HANDLE</th>
                                                   <th className="pb-2 font-normal text-right">FOLLOWERS</th>
                                                   <th className="pb-2 font-normal">ENGAGEMENT</th>
                                                   <th className="pb-2 font-normal">KEYWORDS</th>
                                               </tr>
                                           </thead>
                                           <tbody>
                                               {communityData.map((row, i) => (
                                                   <tr key={i} className="bg-black/50 hover:bg-white/5 transition-colors group">
                                                       <td className="p-3 border-y border-l border-white/5 rounded-l-lg capitalize text-gray-400">
                                                           {row.platform}
                                                       </td>
                                                       <td className="p-3 border-y border-white/5 text-[#00f0ff] font-bold">
                                                           <a href={row.url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                                                               {row.handle}
                                                           </a>
                                                       </td>
                                                       <td className="p-3 border-y border-white/5 text-right text-white">
                                                           {(row.follower_count / 1000).toFixed(1)}K
                                                       </td>
                                                       <td className="p-3 border-y border-white/5 text-gray-400 text-xs">
                                                           {row.engagement_rate || 'N/A'}
                                                       </td>
                                                       <td className="p-3 border-y border-r border-white/5 rounded-r-lg text-xs text-gray-500">
                                                           {row.keywords?.join(', ') || '-'}
                                                       </td>
                                                   </tr>
                                               ))}
                                           </tbody>
                                       </table>
                                   </div>
                               )}
                           </div>
                        )}

                        {/* TAB: ACCOUNT MANAGEMENT */}
                        {activeTab === 'accounts' && (
                            <div className="bg-[#111] border border-white/10 rounded-2xl p-6 lg:p-8 min-h-[600px]">
                                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 border-b border-white/10 pb-6">
                                    <div>
                                        <h2 className="text-xl font-mono font-bold text-amber-400 uppercase tracking-widest flex items-center gap-2">
                                            <Key className="w-5 h-5" />
                                            Account Vault
                                        </h2>
                                        <p className="text-gray-500 text-xs font-mono mt-1">Encrypted at rest • Auto-rotation on job launch</p>
                                    </div>
                                    <button
                                        onClick={() => setShowAddForm(!showAddForm)}
                                        className="px-5 py-2.5 bg-gradient-to-r from-amber-500 to-orange-500 hover:opacity-90 text-black font-mono font-bold tracking-widest text-xs rounded-xl flex items-center gap-2 transition-all"
                                    >
                                        <Plus className="w-4 h-4" />
                                        ADD ACCOUNT
                                    </button>
                                </div>

                                {/* Platform Summary Cards */}
                                {savedAccounts && (
                                    <div className="grid grid-cols-3 gap-3 mb-6">
                                        {(['instagram', 'twitter', 'tiktok'] as const).map((p) => {
                                            const count = savedAccounts.by_platform[p] || 0;
                                            const colors = {
                                                instagram: { bg: 'bg-pink-500/10', border: 'border-pink-500/30', text: 'text-pink-400' },
                                                twitter: { bg: 'bg-sky-500/10', border: 'border-sky-500/30', text: 'text-sky-400' },
                                                tiktok: { bg: 'bg-rose-500/10', border: 'border-rose-500/30', text: 'text-rose-400' },
                                            };
                                            const c = colors[p];
                                            return (
                                                <div key={p} className={cn("p-4 rounded-xl border", c.bg, c.border)}>
                                                    <div className="text-[10px] text-gray-500 font-mono tracking-widest uppercase">{p}</div>
                                                    <div className={cn("text-2xl font-bold font-mono mt-1", c.text)}>{count}</div>
                                                    <div className="text-gray-500 font-mono text-xs">accounts</div>
                                                </div>
                                            );
                                        })}
                                    </div>
                                )}

                                {/* Add Account Form */}
                                {showAddForm && (
                                    <div className="bg-[#0A0A0A] border border-amber-500/30 rounded-xl p-6 mb-6 animate-in slide-in-from-top-2">
                                        <h3 className="text-white font-mono font-bold text-sm tracking-widest mb-4 flex items-center gap-2"><Plus className="w-4 h-4 text-amber-400" /> NEW ACCOUNT</h3>
                                        
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                                            <div>
                                                <label className="block text-gray-500 font-mono text-xs tracking-widest mb-2">PLATFORM</label>
                                                <select 
                                                    value={newAccount.platform} 
                                                    onChange={(e) => setNewAccount(prev => ({...prev, platform: e.target.value}))}
                                                    className="w-full bg-black border border-white/10 rounded-lg px-4 py-3 text-white font-mono text-sm focus:outline-none focus:border-amber-500"
                                                >
                                                    <option value="instagram">Instagram</option>
                                                    <option value="twitter">X (Twitter)</option>
                                                    <option value="tiktok">TikTok</option>
                                                </select>
                                            </div>
                                            <div>
                                                <label className="block text-gray-500 font-mono text-xs tracking-widest mb-2">USERNAME</label>
                                                <input 
                                                    type="text" 
                                                    placeholder="@username" 
                                                    value={newAccount.username}
                                                    onChange={(e) => setNewAccount(prev => ({...prev, username: e.target.value}))}
                                                    className="w-full bg-black border border-white/10 rounded-lg px-4 py-3 text-white font-mono text-sm focus:outline-none focus:border-amber-500"
                                                />
                                            </div>
                                        </div>

                                        {/* Auth Mode Toggle */}
                                        <div className="flex gap-2 mb-4">
                                            <button 
                                                onClick={() => setAuthMode('cookie')}
                                                className={cn(
                                                    "flex-1 py-2.5 rounded-lg font-mono text-xs tracking-widest flex items-center justify-center gap-2 transition-all",
                                                    authMode === 'cookie' 
                                                        ? "bg-emerald-500/10 border border-emerald-500 text-emerald-400" 
                                                        : "bg-black border border-white/10 text-gray-500 hover:text-white"
                                                )}
                                            >
                                                <Cookie className="w-3.5 h-3.5" />
                                                COOKIE AUTH (RECOMMENDED)
                                            </button>
                                            <button 
                                                onClick={() => setAuthMode('password')}
                                                className={cn(
                                                    "flex-1 py-2.5 rounded-lg font-mono text-xs tracking-widest flex items-center justify-center gap-2 transition-all",
                                                    authMode === 'password' 
                                                        ? "bg-amber-500/10 border border-amber-500 text-amber-400" 
                                                        : "bg-black border border-white/10 text-gray-500 hover:text-white"
                                                )}
                                            >
                                                <Key className="w-3.5 h-3.5" />
                                                PASSWORD
                                            </button>
                                        </div>

                                        {authMode === 'cookie' ? (
                                            <div className="mb-4">
                                                <label className="block text-gray-500 font-mono text-xs tracking-widest mb-2">COOKIE STRING</label>
                                                <textarea 
                                                    placeholder="Paste cookie header from your browser (safer, bypasses 2FA)..." 
                                                    value={newAccount.cookie_string}
                                                    onChange={(e) => setNewAccount(prev => ({...prev, cookie_string: e.target.value}))}
                                                    rows={3}
                                                    className="w-full bg-black border border-white/10 rounded-lg px-4 py-3 text-white font-mono text-sm focus:outline-none focus:border-amber-500 resize-none"
                                                />
                                                <p className="text-emerald-500/70 text-xs font-mono mt-2 flex items-center gap-1">
                                                    <Shield className="w-3 h-3" /> Recommended: No password stored. Bypasses 2FA automatically.
                                                </p>
                                            </div>
                                        ) : (
                                            <div className="mb-4">
                                                <label className="block text-gray-500 font-mono text-xs tracking-widest mb-2">PASSWORD</label>
                                                <input 
                                                    type="password" 
                                                    placeholder="Account password (Fernet encrypted at rest)" 
                                                    value={newAccount.password}
                                                    onChange={(e) => setNewAccount(prev => ({...prev, password: e.target.value}))}
                                                    className="w-full bg-black border border-white/10 rounded-lg px-4 py-3 text-white font-mono text-sm focus:outline-none focus:border-amber-500"
                                                />
                                                <p className="text-amber-500/70 text-xs font-mono mt-2 flex items-center gap-1">
                                                    <AlertTriangle className="w-3 h-3" /> Password is AES-256 encrypted at rest. Cookie auth is preferred.
                                                </p>
                                            </div>
                                        )}

                                        <div className="mb-4">
                                            <label className="block text-gray-500 font-mono text-xs tracking-widest mb-2">DEDICATED PROXY (OPTIONAL)</label>
                                            <input 
                                                type="text" 
                                                placeholder="socks5://user:pass@host:port" 
                                                value={newAccount.proxy_url}
                                                onChange={(e) => setNewAccount(prev => ({...prev, proxy_url: e.target.value}))}
                                                className="w-full bg-black border border-white/10 rounded-lg px-4 py-3 text-white font-mono text-sm focus:outline-none focus:border-amber-500"
                                            />
                                        </div>

                                        <div className="flex gap-3">
                                            <button 
                                                onClick={saveAccount}
                                                disabled={isSaving || !newAccount.username || (authMode === 'cookie' ? !newAccount.cookie_string : !newAccount.password)}
                                                className="flex-1 py-3 bg-gradient-to-r from-amber-500 to-orange-500 hover:opacity-90 disabled:opacity-50 text-black font-mono font-bold tracking-widest text-xs rounded-xl flex items-center justify-center gap-2 transition-all"
                                            >
                                                {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
                                                {isSaving ? 'ENCRYPTING...' : 'SAVE TO VAULT'}
                                            </button>
                                            <button 
                                                onClick={() => setShowAddForm(false)}
                                                className="px-6 py-3 bg-white/5 border border-white/10 hover:bg-white/10 text-gray-400 font-mono text-xs rounded-xl tracking-widest transition-all"
                                            >
                                                CANCEL
                                            </button>
                                        </div>
                                    </div>
                                )}

                                {/* Account List */}
                                {accountsLoading ? (
                                    <div className="flex flex-col items-center justify-center py-16 text-gray-500 font-mono">
                                        <Loader2 className="w-8 h-8 animate-spin mb-4 text-amber-400" />
                                        DECRYPTING VAULT...
                                    </div>
                                ) : !savedAccounts || savedAccounts.accounts.length === 0 ? (
                                    <div className="flex flex-col items-center justify-center py-16 text-gray-500 font-mono">
                                        <Key className="w-12 h-12 mb-4 opacity-30" />
                                        <p className="text-white font-bold mb-2">NO ACCOUNTS LOADED</p>
                                        <p className="text-xs text-gray-600 max-w-sm text-center">
                                            Add your social media alt accounts to power the scraping engine. 
                                            The system handles rotation, cooldown, and ban detection automatically.
                                        </p>
                                    </div>
                                ) : (
                                    <div className="space-y-3">
                                        {savedAccounts.accounts.map((acct) => {
                                            const statusColors: Record<string, string> = {
                                                active: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
                                                cooldown: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
                                                banned: 'text-red-400 bg-red-500/10 border-red-500/30',
                                            };
                                            const platformIcons: Record<string, string> = {
                                                instagram: '📸',
                                                twitter: '𝕏',
                                                tiktok: '🎵',
                                            };
                                            return (
                                                <div key={acct.id} className="flex items-center gap-4 bg-[#0A0A0A] border border-white/5 rounded-xl p-4 hover:border-white/10 transition-all group">
                                                    <div className="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center text-lg">
                                                        {platformIcons[acct.platform] || '?'}
                                                    </div>
                                                    <div className="flex-1 min-w-0">
                                                        <div className="flex items-center gap-2">
                                                            <span className="text-white font-mono font-bold text-sm">@{acct.username}</span>
                                                            <span className={cn("text-[10px] font-mono px-2 py-0.5 rounded-full border uppercase tracking-widest", statusColors[acct.status] || 'text-gray-400')}>
                                                                {acct.status}
                                                            </span>
                                                        </div>
                                                        <div className="flex items-center gap-3 text-xs text-gray-500 font-mono mt-1">
                                                            <span className="capitalize">{acct.platform}</span>
                                                            <span>•</span>
                                                            <span>{acct.has_cookies ? '🍪 Cookie' : acct.has_password ? '🔑 Password' : '—'}</span>
                                                            {acct.proxy_url && <><span>•</span><span>🛡 Proxy</span></>}
                                                        </div>
                                                        {acct.last_error && (
                                                            <p className="text-red-500/70 text-xs font-mono mt-1 truncate">{acct.last_error}</p>
                                                        )}
                                                    </div>
                                                    <button 
                                                        onClick={() => deleteAccount(acct.id)}
                                                        className="opacity-0 group-hover:opacity-100 p-2 hover:bg-red-500/10 rounded-lg text-gray-500 hover:text-red-400 transition-all"
                                                        title="Remove account"
                                                    >
                                                        <Trash2 className="w-4 h-4" />
                                                    </button>
                                                </div>
                                            );
                                        })}
                                    </div>
                                )}
                            </div>
                        )}

                    </div>
                </div>
            </div>
        </div>
    );
}
