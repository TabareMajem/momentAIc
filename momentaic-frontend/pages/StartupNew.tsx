import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../lib/api';
import { Button } from '../components/ui/Button';
import { StartupCreate } from '../types';
import { ArrowLeft, Send, Bot, Target, Lightbulb, ShieldAlert, Rocket, Check, Loader2, ExternalLink } from 'lucide-react';
import { useToast } from '../components/ui/Toast';
import { Card } from '../components/ui/Card';

interface Competitor {
    name: string;
    url: string;
    description: string;
}

interface AnalysisReport {
    industry: string | null;
    stage: string | null;
    summary: string | null;
    insight: string | null;
    competitors: Competitor[];
    follow_up_question: string | null;
}

type AnalysisPhase = 'input' | 'analyzing' | 'complete' | 'assembly';

export default function StartupNew() {
    const navigate = useNavigate();
    const { toast } = useToast();

    // States
    const [phase, setPhase] = useState<AnalysisPhase>('input');
    const [description, setDescription] = useState('');
    const [name, setName] = useState('');
    const [progress, setProgress] = useState(0);
    const [progressMessage, setProgressMessage] = useState('');
    const [competitors, setCompetitors] = useState<Competitor[]>([]);
    const [report, setReport] = useState<AnalysisReport | null>(null);
    const [isCreating, setIsCreating] = useState(false);
    const [importMode, setImportMode] = useState(false);
    const [repoUrl, setRepoUrl] = useState('');

    const handleImport = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!repoUrl.trim()) return;

        setPhase('analyzing');
        setProgress(10);
        setProgressMessage('🚀 Analyzing source availability...');
        setCompetitors([]);
        setReport(null);

        try {
            // Auto-detect source type
            const isGithub = repoUrl.includes('github.com');
            const sourceType = isGithub ? 'github' : 'web';

            setProgressMessage(isGithub ? '📦 Fetching repository context...' : '🌍 Scraping website content...');

            // Simulated progress while waiting
            const interval = setInterval(() => {
                setProgress(prev => Math.min(prev + 5, 90));
            }, 800);

            const data = await api.importFromSource(repoUrl, sourceType);
            clearInterval(interval);

            // Map Response to Report
            const strategy = data.strategy;
            setReport({
                industry: "Auto-Detected Strategy",
                stage: "Execution Ready",
                summary: `${strategy.value_prop}\n\nProblem: ${strategy.pain_point}`,
                insight: strategy.viral_post_hook,
                competitors: [],
                follow_up_question: `Proposed Weekly Goal: ${strategy.weekly_goal}`,
            });

            setProgress(100);
            setPhase('complete');

        } catch (error: any) {
            console.error(error);
            toast({ type: 'error', title: 'Import Failed', message: error.response?.data?.detail || 'Could not analyze source.' });
            setPhase('input');
        }
    };

    const handleAnalyze = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!description.trim()) return;

        setPhase('analyzing');
        setProgress(5);
        setProgressMessage('🚀 Initializing AI analysis...');
        setCompetitors([]);
        setReport(null);

        await api.streamInstantAnalysis(description, {
            onProgress: (data) => {
                setProgress(data.percent);
                setProgressMessage(data.message);
            },
            onCompetitor: (data) => {
                setCompetitors(prev => [...prev, data]);
            },
            onInsight: (data) => {
                setReport(prev => ({
                    ...(prev || { competitors: [], industry: null, stage: null, summary: null, insight: null, follow_up_question: null }),
                    industry: data.industry,
                    stage: data.stage,
                    summary: data.summary,
                    insight: data.insight,
                    follow_up_question: data.follow_up_question,
                }));
            },
            onComplete: (finalReport) => {
                setReport({
                    ...finalReport,
                    competitors: competitors.length > 0 ? competitors : finalReport.competitors || [],
                });
                setProgress(100);
                setPhase('complete');
            },
            onError: (error) => {
                toast({ type: 'error', title: 'Analysis Failed', message: error });
                setPhase('input');
            }
        });
    };

    // ... (keep imports)

    // New State for Team Assembly
    const [assemblyStep, setAssemblyStep] = useState(0);
    const [recruitedAgents, setRecruitedAgents] = useState<string[]>([]);

    // ... (keep existing handleImport and handleAnalyze)

    const handleCreate = async () => {
        if (!report) return;

        setIsCreating(true);
        try {
            const payload: StartupCreate = {
                name: name || 'Untitled Startup',
                description: description,
                industry: report.industry || 'Technology',
                stage: (report.stage as any) || 'idea',
                website: '',
                github_url: '',
            };

            const newStartup = await api.createStartup(payload);

            // START CINEMATIC SEQUENCE INSTEAD OF DIRECT REDIRECT
            setPhase('assembly');
            runAssemblySequence(newStartup.id);

        } catch (error: any) {
            toast({ type: 'error', title: 'Creation Failed', message: error.message });
            setIsCreating(false);
        }
    };

    const runAssemblySequence = (startupId: string) => {
        const sequence = [
            { agent: 'Orchestrator', role: 'Chief Executive AI', color: 'text-purple-400' },
            { agent: 'Tech Lead', role: 'CTO / Architect', color: 'text-cyan-400' },
            { agent: 'Growth Hacker', role: 'Head of Growth', color: 'text-green-400' },
            { agent: 'Legal Eagle', role: 'General Counsel', color: 'text-slate-400' },
        ];

        let delay = 0;
        sequence.forEach((item, index) => {
            delay += 1200; // 1.2s per agent
            setTimeout(() => {
                setRecruitedAgents(prev => [...prev, item.agent]);
                setAssemblyStep(index + 1);
            }, delay);
        });

        // Final Redirect
        setTimeout(() => {
            navigate(`/startups/${startupId}`);
        }, delay + 2000);
    };

    return (
        <div className="max-w-3xl mx-auto py-8 px-4">
            <Button variant="ghost" onClick={() => navigate(-1)} className="mb-6 pl-0 text-gray-500 hover:text-white" disabled={phase === 'assembly'}>
                <ArrowLeft className="w-4 h-4 mr-2" /> Back
            </Button>

            
                {/* ... (keep input and analyzing phases) ... */}

                {/* PHASE 1: INPUT */}
                {phase === 'input' && (
                    <div
                        key="input"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                    >
                        <Card className="p-8 bg-[#0a0a0a] border-white/10">
                            <div className="flex items-center gap-3 mb-6">
                                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#00f0ff] to-[#0066ff] flex items-center justify-center">
                                    <Rocket className="w-5 h-5 text-white" />
                                </div>
                                <div className="flex-1">
                                    <h1 className="text-2xl font-bold text-white">Launch Your Startup</h1>
                                    <p className="text-gray-400 text-sm">Get instant AI-powered insights in 60 seconds</p>
                                </div>
                                {/* Import Toggle */}
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => setImportMode(!importMode)}
                                    className="border-white/10 text-gray-400 hover:text-white"
                                >
                                    {importMode ? (
                                        <>
                                            <Lightbulb className="w-4 h-4 mr-2" />
                                            Describe Idea
                                        </>
                                    ) : (
                                        <>
                                            <ExternalLink className="w-4 h-4 mr-2" />
                                            Import from GitHub
                                        </>
                                    )}
                                </Button>
                            </div>

                            <form onSubmit={importMode ? handleImport : handleAnalyze} className="space-y-6">
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        Startup Name (optional)
                                    </label>
                                    <input
                                        type="text"
                                        value={name}
                                        onChange={(e) => setName(e.target.value)}
                                        placeholder="e.g., MomentAIc"
                                        className="w-full bg-black border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-600 focus:border-[#00f0ff] focus:ring-1 focus:ring-[#00f0ff] transition-colors"
                                    />
                                </div>

                                {importMode ? (
                                    <div className="bg-[#00f0ff]/5 border border-[#00f0ff]/20 rounded-lg p-4">
                                        <label className="block text-sm font-medium text-[#00f0ff] mb-2 flex items-center">
                                            <ExternalLink className="w-4 h-4 mr-2" />
                                            GitHub Repository URL
                                        </label>
                                        <input
                                            type="url"
                                            value={repoUrl}
                                            onChange={(e) => setRepoUrl(e.target.value)}
                                            placeholder="https://github.com/username/project"
                                            className="w-full bg-black border border-[#00f0ff]/30 rounded-lg px-4 py-3 text-white placeholder-gray-600 focus:border-[#00f0ff] focus:ring-1 focus:ring-[#00f0ff] transition-colors"
                                            required
                                        />
                                        <p className="text-xs text-[#00f0ff]/70 mt-2">
                                            We'll analyze your README to generate a Go-to-Market strategy.
                                        </p>
                                    </div>
                                ) : (
                                    <div>
                                        <label className="block text-sm font-medium text-gray-300 mb-2">
                                            Describe your startup idea <span className="text-[#00f0ff] font-bold">OR</span> paste your Website URL
                                        </label>
                                        <textarea
                                            value={description}
                                            onChange={(e) => setDescription(e.target.value)}
                                            placeholder="Paste your URL (e.g. https://www.bondquests.com) or describe your idea..."
                                            rows={4}
                                            className="w-full bg-black border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-600 focus:border-[#00f0ff] focus:ring-1 focus:ring-[#00f0ff] transition-colors resize-none"
                                            required
                                        />
                                    </div>
                                )}

                                <Button type="submit" variant="cyber" className="w-full py-4 text-lg font-semibold">
                                    <Bot className="w-5 h-5 mr-2" />
                                    {importMode ? 'Analyze Repository' : 'Analyze My Startup'}
                                </Button>
                            </form>
                        </Card>
                    </div>
                )}

                {/* PHASE 2: ANALYZING (Live Progress) */}
                {phase === 'analyzing' && (
                    <div
                        key="analyzing"
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                    >
                        <Card className="p-8 bg-[#0a0a0a] border-white/10">
                            <div className="text-center mb-8">
                                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-[#00f0ff]/20 to-[#0066ff]/20 flex items-center justify-center mx-auto mb-4 animate-pulse">
                                    <Loader2 className="w-8 h-8 text-[#00f0ff] animate-spin" />
                                </div>
                                <h2 className="text-xl font-bold text-white mb-2">Analyzing Your Startup...</h2>
                                <p className="text-gray-400">{progressMessage}</p>
                            </div>

                            {/* Progress Bar */}
                            <div className="relative h-3 bg-white/10 rounded-full overflow-hidden mb-8">
                                <div
                                    className="absolute inset-y-0 left-0 bg-gradient-to-r from-[#00f0ff] to-[#0066ff] rounded-full"
                                    initial={{ width: '0%' }}
                                    animate={{ width: `${progress}%` }}
                                    transition={{ duration: 0.3 }}
                                />
                            </div>

                            {/* Live Competitor Feed */}
                            {competitors.length > 0 && (
                                <div className="space-y-3">
                                    <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider">Competitors Found</h3>
                                    <div className="space-y-2">
                                        {competitors.map((comp, i) => (
                                            <div
                                                key={i}
                                                initial={{ opacity: 0, x: -20 }}
                                                animate={{ opacity: 1, x: 0 }}
                                                className="flex items-center gap-3 p-3 bg-white/5 rounded-lg border border-white/10"
                                            >
                                                <Check className="w-4 h-4 text-green-500 shrink-0" />
                                                <div className="flex-1 min-w-0">
                                                    <div className="font-medium text-white truncate">{comp.name}</div>
                                                    <div className="text-xs text-gray-500 truncate">{comp.description}</div>
                                                </div>
                                                {comp.url && (
                                                    <a href={comp.url} target="_blank" rel="noopener noreferrer" className="text-[#00f0ff] hover:text-white">
                                                        <ExternalLink className="w-4 h-4" />
                                                    </a>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </Card>
                    </div>
                )}


                {/* PHASE 3: COMPLETE (AI CEO Report) */}
                {phase === 'complete' && report && (
                    <div
                        key="complete"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                    >
                        <Card className="p-8 bg-[#0a0a0a] border-white/10">
                            {/* Header */}
                            <div className="flex items-start justify-between mb-6">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#00f0ff] to-[#0066ff] flex items-center justify-center">
                                        <Target className="w-5 h-5 text-white" />
                                    </div>
                                    <div>
                                        <div className="text-xs font-mono text-[#00f0ff] uppercase tracking-widest">AI CEO Report</div>
                                        <h2 className="text-xl font-bold text-white">{name || 'Your Startup'}</h2>
                                    </div>
                                </div>
                                <div className="flex gap-2">
                                    <span className="bg-[#00f0ff]/10 border border-[#00f0ff]/30 px-3 py-1 rounded text-xs text-[#00f0ff] font-mono uppercase">
                                        {report.industry}
                                    </span>
                                    <span className="bg-white/10 border border-white/20 px-3 py-1 rounded text-xs text-gray-300 font-mono uppercase">
                                        {report.stage}
                                    </span>
                                </div>
                            </div>

                            {/* Summary */}
                            {report.summary && (
                                <div className="bg-white/5 rounded-lg p-4 mb-4 border border-white/10">
                                    <p className="text-gray-300">{report.summary}</p>
                                </div>
                            )}

                            {/* Insight */}
                            {report.insight && (
                                <div className="bg-[#0a0a0a] rounded-lg p-4 border border-yellow-500/30 mb-4 relative overflow-hidden">
                                    <div className="absolute top-0 left-0 w-1 h-full bg-yellow-500"></div>
                                    <div className="flex items-start gap-3 pl-2">
                                        <Lightbulb className="w-5 h-5 text-yellow-500 shrink-0 mt-0.5" />
                                        <div>
                                            <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">Strategic Insight</div>
                                            <p className="text-sm text-gray-300 italic">"{report.insight}"</p>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Competitors */}
                            {competitors.length > 0 && (
                                <div className="bg-[#0a0a0a] rounded-lg p-4 border border-red-500/30 mb-4 relative overflow-hidden">
                                    <div className="absolute top-0 left-0 w-1 h-full bg-red-500"></div>
                                    <div className="flex items-start gap-3 pl-2">
                                        <ShieldAlert className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
                                        <div className="flex-1">
                                            <div className="text-xs text-gray-500 uppercase tracking-wider mb-2">Competitors</div>
                                            <div className="flex flex-wrap gap-2">
                                                {competitors.map((comp, i) => (
                                                    <a
                                                        key={i}
                                                        href={comp.url}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="bg-white/5 px-3 py-1 rounded text-sm text-gray-300 border border-white/10 hover:border-[#00f0ff]/50 hover:text-[#00f0ff] transition-colors"
                                                    >
                                                        {comp.name}
                                                    </a>
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Follow-up Question */}
                            {report.follow_up_question && (
                                <div className="border-t border-white/10 pt-4 mt-4">
                                    <p className="text-sm text-gray-400 font-mono">
                                        <span className="text-[#00f0ff]">{'>'}</span> {report.follow_up_question}
                                    </p>
                                </div>
                            )}

                            {/* Action Buttons */}
                            <div className="flex gap-4 mt-8">
                                <Button
                                    variant="ghost"
                                    onClick={() => setPhase('input')}
                                    className="flex-1"
                                >
                                    Start Over
                                </Button>
                                <Button
                                    variant="cyber"
                                    onClick={handleCreate}
                                    disabled={isCreating}
                                    className="flex-1"
                                >
                                    {isCreating ? (
                                        <>
                                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                            Initializing...
                                        </>
                                    ) : (
                                        <>
                                            <Rocket className="w-4 h-4 mr-2" />
                                            Assemble Team & Launch
                                        </>
                                    )}
                                </Button>
                            </div>
                        </Card>
                    </div>
                )}

                {/* PHASE 4: TEAM ASSEMBLY (CINEMATIC) */}
                {phase === 'assembly' && (
                    <div
                        key="assembly"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="fixed inset-0 bg-[#020202] z-50 flex flex-col items-center justify-center p-4"
                    >
                        {/* Matrix Background */}
                        <div className="absolute inset-0 bg-cyber-grid opacity-20 bg-[length:30px_30px] animate-[pulse_4s_infinite]"></div>

                        <div className="relative z-10 w-full max-w-2xl text-center space-y-12">

                            <div
                                initial={{ y: 20, opacity: 0 }}
                                animate={{ y: 0, opacity: 1 }}
                                className="space-y-4"
                            >
                                <h2 className="text-4xl font-black text-white tracking-tighter uppercase glitch-text">
                                    Recruiting Your AI Executive Team
                                </h2>
                                <p className="text-[#00f0ff] font-mono animate-pulse">
                                    &gt; SCANNING GLOBAL TALENT POOL...
                                </p>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {recruitedAgents.map((agent, i) => (
                                    <div
                                        key={agent}
                                        initial={{ scale: 0.8, opacity: 0 }}
                                        animate={{ scale: 1, opacity: 1 }}
                                        className="bg-[#0a0a0a] border border-white/20 p-4 rounded-xl flex items-center gap-4 relative overflow-hidden"
                                    >
                                        <div className="absolute inset-0 bg-white/5 animate-[ping_1s_ease-out_once]"></div>
                                        <div className="p-3 bg-white/10 rounded-lg">
                                            <Bot className="w-6 h-6 text-white" />
                                        </div>
                                        <div className="text-left">
                                            <div className="font-bold text-white text-lg">{agent}</div>
                                            <div className="text-xs text-green-400 font-mono flex items-center gap-1">
                                                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                                                ONLINE
                                            </div>
                                        </div>
                                        <Check className="ml-auto text-green-500 w-6 h-6" />
                                    </div>
                                ))}
                            </div>

                            <div
                                animate={{ opacity: [0.5, 1, 0.5] }}
                                transition={{ repeat: Infinity, duration: 2 }}
                                className="text-gray-500 font-mono text-sm mt-8"
                            >
                                Initializing Neural Links... {Math.min(recruitedAgents.length * 25, 100)}%
                            </div>

                        </div>
                    </div>
                )}

            
        </div>
    );
}
