import React, { useState, useEffect } from 'react';
import { UserPlus, Upload, FileText, CheckCircle, XCircle, Loader, Search, Briefcase } from 'lucide-react';
import { BackendService } from '../../services/backendService';
import { useToast } from './Toast';

interface Candidate {
    id: string;
    name: string;
    fitScore: number;
    status: string;
    analysis: {
        summary: string;
        strengths: string[];
        weaknesses: string[];
        questions: string[];
    };
}

const RecruitingAgent: React.FC = () => {
    const [activeTab, setActiveTab] = useState<'ANALYZE' | 'CANDIDATES'>('ANALYZE');
    const [resumeText, setResumeText] = useState('');
    const [jobDescription, setJobDescription] = useState('');
    const [candidateName, setCandidateName] = useState('');
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [candidates, setCandidates] = useState<Candidate[]>([]);
    const [result, setResult] = useState<Candidate | null>(null);
    const { addToast } = useToast();

    useEffect(() => {
        if (activeTab === 'CANDIDATES') {
            loadCandidates();
        }
    }, [activeTab]);

    const loadCandidates = async () => {
        try {
            const data = await BackendService.getCandidates();
            setCandidates(data);
        } catch (e) {
            console.error(e);
            addToast("Failed to load candidates", 'error');
        }
    };

    const handleAnalyze = async () => {
        if (!resumeText.trim()) return;

        setIsAnalyzing(true);
        setResult(null);

        try {
            const response = await BackendService.analyzeCandidate(candidateName, resumeText, jobDescription);
            if (response.success) {
                setResult(response.candidate);
                addToast("Candidate analyzed", 'success');
            } else {
                addToast(response.error || "Analysis failed", 'error');
            }
        } catch (error) {
            console.error(error);
            addToast("Failed to analyze candidate", 'error');
        } finally {
            setIsAnalyzing(false);
        }
    };

    const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const text = e.target?.result as string;
                setResumeText(text);
                if (!candidateName) {
                    setCandidateName(file.name.replace(/\.[^/.]+$/, ""));
                }
            };
            reader.readAsText(file);
        }
    };

    return (
        <div className="p-6 max-w-6xl mx-auto animate-fade-in">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8">
                <div>
                    <h2 className="text-3xl font-bold text-white flex items-center gap-3">
                        <UserPlus className="w-8 h-8 text-indigo-500 shrink-0" />
                        HR Scout
                    </h2>
                    <p className="text-slate-400 mt-2">AI-powered resume screening and candidate analysis.</p>
                </div>
                <div className="flex bg-slate-800 p-1 rounded-lg border border-slate-700 mx-auto md:mx-0">
                    <button onClick={() => setActiveTab('ANALYZE')} className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${activeTab === 'ANALYZE' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'}`}>Analyze</button>
                    <button onClick={() => setActiveTab('CANDIDATES')} className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${activeTab === 'CANDIDATES' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'}`}>Candidates</button>
                </div>
            </div>

            {activeTab === 'ANALYZE' && (
                <div className="grid lg:grid-cols-2 gap-8">
                    <div className="space-y-6">
                        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-slate-400 mb-1">Candidate Name</label>
                                <input
                                    type="text"
                                    value={candidateName}
                                    onChange={(e) => setCandidateName(e.target.value)}
                                    className="w-full bg-slate-900 border border-slate-600 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-indigo-500 outline-none"
                                    placeholder="John Doe"
                                />
                            </div>

                            <div>
                                <div className="flex justify-between items-center mb-1">
                                    <label className="block text-sm font-medium text-slate-400">Resume Content</label>
                                    <div className="relative">
                                        <input type="file" id="resume-upload" className="hidden" accept=".txt,.md" onChange={handleFileUpload} />
                                        <label htmlFor="resume-upload" className="text-xs text-indigo-400 hover:text-indigo-300 cursor-pointer flex items-center gap-1">
                                            <Upload className="w-3 h-3" /> Upload Text
                                        </label>
                                    </div>
                                </div>
                                <textarea
                                    value={resumeText}
                                    onChange={(e) => setResumeText(e.target.value)}
                                    className="w-full h-48 bg-slate-900 border border-slate-600 rounded-lg p-3 text-sm text-slate-300 focus:ring-2 focus:ring-indigo-500 outline-none resize-none"
                                    placeholder="Paste resume text here..."
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-slate-400 mb-1">Job Description (Optional)</label>
                                <textarea
                                    value={jobDescription}
                                    onChange={(e) => setJobDescription(e.target.value)}
                                    className="w-full h-32 bg-slate-900 border border-slate-600 rounded-lg p-3 text-sm text-slate-300 focus:ring-2 focus:ring-indigo-500 outline-none resize-none"
                                    placeholder="Paste job description here for better matching..."
                                />
                            </div>

                            <button
                                onClick={handleAnalyze}
                                disabled={isAnalyzing || !resumeText}
                                className={`w-full py-3 rounded-lg font-bold text-white transition-all flex items-center justify-center gap-2 ${isAnalyzing || !resumeText ? 'bg-slate-700 cursor-not-allowed text-slate-500' : 'bg-indigo-600 hover:bg-indigo-700'
                                    }`}
                            >
                                {isAnalyzing ? <Loader className="w-5 h-5 animate-spin" /> : <UserPlus className="w-5 h-5" />}
                                {isAnalyzing ? 'Analyzing...' : 'Analyze Candidate'}
                            </button>
                        </div>
                    </div>

                    <div className="space-y-6">
                        {result ? (
                            <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 animate-in slide-in-from-right-4">
                                <div className="flex items-center justify-between mb-6">
                                    <div>
                                        <h3 className="text-xl font-bold text-white">{result.name}</h3>
                                        <p className="text-sm text-slate-400">Analysis Result</p>
                                    </div>
                                    <div className={`px-4 py-2 rounded-lg font-bold text-lg ${result.fitScore >= 80 ? 'bg-emerald-500/10 text-emerald-400' :
                                            result.fitScore >= 50 ? 'bg-amber-500/10 text-amber-400' : 'bg-rose-500/10 text-rose-400'
                                        }`}>
                                        {result.fitScore}% Match
                                    </div>
                                </div>

                                <div className="space-y-6">
                                    <div>
                                        <h4 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-2">Summary</h4>
                                        <p className="text-slate-400 text-sm leading-relaxed">{result.analysis.summary}</p>
                                    </div>

                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <h4 className="text-sm font-bold text-emerald-400 uppercase tracking-wider mb-2 flex items-center gap-2"><CheckCircle className="w-4 h-4" /> Strengths</h4>
                                            <ul className="space-y-1">
                                                {result.analysis.strengths.map((s, i) => (
                                                    <li key={i} className="text-xs text-slate-300">• {s}</li>
                                                ))}
                                            </ul>
                                        </div>
                                        <div>
                                            <h4 className="text-sm font-bold text-rose-400 uppercase tracking-wider mb-2 flex items-center gap-2"><XCircle className="w-4 h-4" /> Weaknesses</h4>
                                            <ul className="space-y-1">
                                                {result.analysis.weaknesses.map((w, i) => (
                                                    <li key={i} className="text-xs text-slate-300">• {w}</li>
                                                ))}
                                            </ul>
                                        </div>
                                    </div>

                                    <div>
                                        <h4 className="text-sm font-bold text-indigo-400 uppercase tracking-wider mb-2">Suggested Interview Questions</h4>
                                        <ul className="space-y-2">
                                            {result.analysis.questions.map((q, i) => (
                                                <li key={i} className="text-sm text-slate-300 bg-slate-900/50 p-3 rounded border border-slate-700/50">
                                                    "{q}"
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="h-full flex flex-col items-center justify-center text-slate-500 border-2 border-dashed border-slate-700 rounded-xl p-12">
                                <Briefcase className="w-16 h-16 mb-4 opacity-20" />
                                <p>Upload a resume to see AI analysis</p>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {activeTab === 'CANDIDATES' && (
                <div className="grid gap-4 animate-in fade-in">
                    {candidates.length === 0 ? (
                        <div className="text-center py-12 text-slate-500">No candidates found.</div>
                    ) : (
                        candidates.map(c => (
                            <div key={c.id} className="bg-slate-800 p-4 rounded-xl border border-slate-700 flex justify-between items-center hover:border-slate-600 transition-colors">
                                <div className="flex items-center gap-4">
                                    <div className="w-10 h-10 rounded-full bg-indigo-500/20 flex items-center justify-center text-indigo-400 font-bold">
                                        {c.name.charAt(0)}
                                    </div>
                                    <div>
                                        <h4 className="font-bold text-white">{c.name}</h4>
                                        <p className="text-xs text-slate-400 line-clamp-1">{c.analysis.summary}</p>
                                    </div>
                                </div>
                                <div className={`px-3 py-1 rounded font-bold text-sm shrink-0 ${c.fitScore >= 80 ? 'bg-emerald-500/10 text-emerald-400' :
                                        c.fitScore >= 50 ? 'bg-amber-500/10 text-amber-400' : 'bg-rose-500/10 text-rose-400'
                                    }`}>
                                    {c.fitScore}%
                                </div>
                            </div>
                        ))
                    )}
                </div>
            )}
        </div>
    );
};

export default RecruitingAgent;
