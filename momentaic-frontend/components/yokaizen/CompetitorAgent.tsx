import React, { useState, useEffect } from 'react';
import { Radar, Plus, RefreshCw, FileText, Trash2, AlertTriangle, Shield, Target, Zap } from 'lucide-react';
import api from '../../services/api';
import { useToast } from './Toast';

interface Competitor {
    id: string;
    name: string;
    url: string;
    latestAnalysis: any;
    analysisCount: number;
    createdAt: string;
}

const CompetitorAgent: React.FC = () => {
    const [competitors, setCompetitors] = useState<Competitor[]>([]);
    const [loading, setLoading] = useState(true);
    const [newUrl, setNewUrl] = useState('');
    const [newName, setNewName] = useState('');
    const [analyzing, setAnalyzing] = useState<string | null>(null);
    const [report, setReport] = useState<string | null>(null);
    const [showReport, setShowReport] = useState(false);
    const { addToast } = useToast();

    useEffect(() => { loadCompetitors(); }, []);

    const loadCompetitors = async () => {
        try {
            const res = await api.get('/competitor');
            setCompetitors(res.data);
        } catch (e) {
            console.error('Failed to load competitors', e);
        } finally {
            setLoading(false);
        }
    };

    const handleAdd = async () => {
        if (!newUrl) return;
        try {
            await api.post('/competitor', { url: newUrl, name: newName || undefined });
            addToast('Competitor added', 'success');
            setNewUrl('');
            setNewName('');
            loadCompetitors();
        } catch (e: any) {
            addToast(e.response?.data?.error || 'Failed to add', 'error');
        }
    };

    const handleAnalyze = async (id: string) => {
        setAnalyzing(id);
        try {
            await api.post(`/competitor/${id}/analyze`);
            addToast('Analysis complete!', 'success');
            loadCompetitors();
        } catch (e: any) {
            addToast('Analysis failed', 'error');
        } finally {
            setAnalyzing(null);
        }
    };

    const handleReport = async () => {
        try {
            const res = await api.get('/competitor/report');
            setReport(res.data.report);
            setShowReport(true);
        } catch (e) {
            addToast('Report generation failed', 'error');
        }
    };

    const getThreatColor = (level: string) => {
        if (level === 'HIGH') return 'text-red-400 bg-red-500/20';
        if (level === 'MEDIUM') return 'text-yellow-400 bg-yellow-500/20';
        return 'text-green-400 bg-green-500/20';
    };

    if (loading) return <div className="p-8 text-white">Loading intelligence data...</div>;

    return (
        <div className="p-6 max-w-7xl mx-auto animate-fade-in">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h2 className="text-3xl font-bold text-white flex items-center gap-3">
                        <Radar className="w-8 h-8 text-red-500" />
                        Competitor Intelligence
                    </h2>
                    <p className="text-slate-400 mt-1">AI-powered competitive analysis & counter-strategy</p>
                </div>
                <button onClick={handleReport} className="flex items-center gap-2 bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-500 hover:to-orange-500 text-white px-5 py-2.5 rounded-xl font-medium transition-all shadow-lg">
                    <FileText className="w-4 h-4" /> Weekly Brief
                </button>
            </div>

            {/* Add Competitor */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-5 mb-6 backdrop-blur-sm">
                <h3 className="text-sm font-bold text-slate-400 uppercase mb-3">Track New Competitor</h3>
                <div className="flex gap-3">
                    <input value={newName} onChange={e => setNewName(e.target.value)} placeholder="Company Name" className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:ring-2 focus:ring-red-500 outline-none" />
                    <input value={newUrl} onChange={e => setNewUrl(e.target.value)} placeholder="https://competitor.com" className="flex-[2] bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:ring-2 focus:ring-red-500 outline-none" />
                    <button onClick={handleAdd} className="flex items-center gap-2 bg-red-600 hover:bg-red-500 text-white px-5 py-2.5 rounded-lg font-medium transition-colors">
                        <Plus className="w-4 h-4" /> Track
                    </button>
                </div>
            </div>

            {/* Competitor Cards */}
            {competitors.length === 0 ? (
                <div className="text-center py-16 text-slate-500">
                    <Radar className="w-16 h-16 mx-auto mb-4 opacity-30" />
                    <p className="text-lg">No competitors tracked yet</p>
                    <p className="text-sm mt-1">Add a competitor URL above to start intelligence gathering</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    {competitors.map(comp => (
                        <div key={comp.id} className="bg-slate-800/60 border border-slate-700 rounded-xl p-5 hover:border-red-500/50 transition-all group">
                            <div className="flex items-start justify-between mb-4">
                                <div>
                                    <h3 className="text-lg font-bold text-white">{comp.name}</h3>
                                    <p className="text-sm text-slate-500 mt-0.5">{comp.url}</p>
                                </div>
                                {comp.latestAnalysis?.threatLevel && (
                                    <span className={`text-xs font-bold px-3 py-1 rounded-full ${getThreatColor(comp.latestAnalysis.threatLevel)}`}>
                                        {comp.latestAnalysis.threatLevel} THREAT
                                    </span>
                                )}
                            </div>

                            {comp.latestAnalysis ? (
                                <div className="space-y-3">
                                    <p className="text-sm text-slate-300">{comp.latestAnalysis.companyOverview}</p>

                                    {comp.latestAnalysis.strengths && (
                                        <div>
                                            <span className="text-xs font-bold text-emerald-400 uppercase">Strengths</span>
                                            <ul className="mt-1 space-y-1">
                                                {comp.latestAnalysis.strengths.slice(0, 3).map((s: string, i: number) => (
                                                    <li key={i} className="text-xs text-slate-400 flex items-center gap-1.5">
                                                        <Shield className="w-3 h-3 text-emerald-500" /> {s}
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}

                                    {comp.latestAnalysis.weaknesses && (
                                        <div>
                                            <span className="text-xs font-bold text-red-400 uppercase">Weaknesses</span>
                                            <ul className="mt-1 space-y-1">
                                                {comp.latestAnalysis.weaknesses.slice(0, 3).map((w: string, i: number) => (
                                                    <li key={i} className="text-xs text-slate-400 flex items-center gap-1.5">
                                                        <AlertTriangle className="w-3 h-3 text-red-500" /> {w}
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}

                                    {comp.latestAnalysis.counterStrategy && (
                                        <div className="mt-3 pt-3 border-t border-slate-700">
                                            <span className="text-xs font-bold text-violet-400 uppercase">Counter Moves</span>
                                            <ul className="mt-1 space-y-1">
                                                {comp.latestAnalysis.counterStrategy.slice(0, 3).map((c: string, i: number) => (
                                                    <li key={i} className="text-xs text-slate-300 flex items-center gap-1.5">
                                                        <Zap className="w-3 h-3 text-violet-500" /> {c}
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <p className="text-sm text-slate-500 italic">No analysis yet — click Analyze to generate intelligence</p>
                            )}

                            <div className="flex items-center justify-between mt-4 pt-3 border-t border-slate-700">
                                <span className="text-xs text-slate-500">{comp.analysisCount} analyses</span>
                                <button
                                    onClick={() => handleAnalyze(comp.id)}
                                    disabled={analyzing === comp.id}
                                    className="flex items-center gap-1.5 bg-red-600/20 hover:bg-red-600 text-red-400 hover:text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-all disabled:opacity-50"
                                >
                                    <RefreshCw className={`w-3 h-3 ${analyzing === comp.id ? 'animate-spin' : ''}`} />
                                    {analyzing === comp.id ? 'Analyzing...' : 'Analyze'}
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Weekly Report Modal */}
            {showReport && (
                <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 backdrop-blur-sm" onClick={() => setShowReport(false)}>
                    <div className="bg-slate-800 border border-slate-700 rounded-2xl p-8 max-w-3xl w-full max-h-[80vh] overflow-y-auto shadow-2xl" onClick={e => e.stopPropagation()}>
                        <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                            <FileText className="w-5 h-5 text-red-500" /> Weekly Competitive Brief
                        </h3>
                        <div className="prose prose-invert prose-sm max-w-none whitespace-pre-wrap text-slate-300">
                            {report || 'Generating report...'}
                        </div>
                        <button onClick={() => setShowReport(false)} className="mt-6 bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-lg text-sm">
                            Close
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default CompetitorAgent;
