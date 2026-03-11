import React, { useState } from 'react';
import { Scale, Upload, FileText, AlertTriangle, CheckCircle, XCircle, Loader, ArrowRight } from 'lucide-react';
import { BackendService } from '../../services/backendService';
import { useToast } from './Toast';

interface AuditResult {
    riskScore: number;
    summary: string;
    flaggedClauses: { clause: string; issue: string; severity: 'HIGH' | 'MEDIUM' | 'LOW' }[];
    missingClauses: string[];
    recommendation: 'Sign' | 'Negotiate' | 'Reject';
}

const LegalAgent: React.FC = () => {
    const [contractText, setContractText] = useState('');
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [result, setResult] = useState<AuditResult | null>(null);
    const { addToast } = useToast();

    const handleAnalyze = async () => {
        if (!contractText.trim()) return;

        setIsAnalyzing(true);
        setResult(null);

        try {
            const response = await BackendService.reviewContract(contractText);
            if (response.success) {
                setResult(response.analysis);
                addToast("Contract analysis complete", 'success');
            } else {
                addToast(response.error || "Analysis failed", 'error');
            }
        } catch (error) {
            console.error(error);
            addToast("Failed to analyze contract", 'error');
        } finally {
            setIsAnalyzing(false);
        }
    };

    const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            // In a real app, we'd use PDF.js or similar to extract text
            // For now, we'll just simulate text extraction for text files
            const reader = new FileReader();
            reader.onload = (e) => {
                const text = e.target?.result as string;
                setContractText(text);
            };
            reader.readAsText(file);
        }
    };

    return (
        <div className="p-6 max-w-6xl mx-auto animate-fade-in">
            <div className="mb-8 text-center sm:text-left">
                <h2 className="text-3xl font-bold text-white flex flex-col sm:flex-row items-center gap-3 justify-center sm:justify-start">
                    <Scale className="w-8 h-8 text-indigo-500 shrink-0" />
                    Legal Eagle
                </h2>
                <p className="text-slate-400 mt-2">AI-powered contract review and risk analysis.</p>
            </div>

            <div className="grid lg:grid-cols-2 gap-8">
                {/* Input Section */}
                <div className="space-y-6">
                    <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="text-lg font-semibold text-white">Contract Input</h3>
                            <div className="relative">
                                <input
                                    type="file"
                                    id="contract-upload"
                                    className="hidden"
                                    accept=".txt,.md"
                                    onChange={handleFileUpload}
                                />
                                <label
                                    htmlFor="contract-upload"
                                    className="flex items-center gap-2 px-3 py-1.5 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm text-white cursor-pointer transition-colors"
                                >
                                    <Upload className="w-4 h-4" /> Upload Text
                                </label>
                            </div>
                        </div>

                        <textarea
                            value={contractText}
                            onChange={(e) => setContractText(e.target.value)}
                            placeholder="Paste contract text here or upload a file..."
                            className="w-full h-96 bg-slate-900 border border-slate-700 rounded-lg p-4 text-slate-300 focus:ring-2 focus:ring-indigo-500 outline-none resize-none font-mono text-sm"
                        />

                        <div className="mt-4 flex justify-end">
                            <button
                                onClick={handleAnalyze}
                                disabled={isAnalyzing || !contractText}
                                className={`
                  flex items-center gap-2 px-6 py-3 rounded-xl font-bold text-white transition-all
                  ${isAnalyzing || !contractText
                                        ? 'bg-slate-700 cursor-not-allowed text-slate-500'
                                        : 'bg-indigo-600 hover:bg-indigo-700 hover:shadow-lg hover:shadow-indigo-500/20'}
                `}
                            >
                                {isAnalyzing ? (
                                    <>
                                        <Loader className="w-5 h-5 animate-spin" /> Analyzing...
                                    </>
                                ) : (
                                    <>
                                        <Scale className="w-5 h-5" /> Review Contract
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </div>

                {/* Results Section */}
                <div className="space-y-6">
                    {result ? (
                        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 animate-in slide-in-from-right-4">
                            <div className="flex items-center justify-between mb-6">
                                <h3 className="text-lg font-semibold text-white">Analysis Report</h3>
                                <div className={`px-4 py-2 rounded-lg font-bold flex items-center gap-2 text-sm sm:text-base whitespace-nowrap ${result.recommendation === 'Sign' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                                        result.recommendation === 'Reject' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' :
                                            'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                                    }`}>
                                    {result.recommendation === 'Sign' && <CheckCircle className="w-5 h-5 shrink-0" />}
                                    {result.recommendation === 'Reject' && <XCircle className="w-5 h-5 shrink-0" />}
                                    {result.recommendation === 'Negotiate' && <AlertTriangle className="w-5 h-5 shrink-0" />}
                                    {result.recommendation}
                                </div>
                            </div>

                            <div className="mb-6">
                                <div className="flex items-center justify-between text-sm text-slate-400 mb-2">
                                    <span>Risk Score</span>
                                    <span>{result.riskScore}/100</span>
                                </div>
                                <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                                    <div
                                        className={`h-full transition-all duration-1000 ${result.riskScore < 30 ? 'bg-emerald-500' :
                                                result.riskScore < 70 ? 'bg-amber-500' : 'bg-rose-500'
                                            }`}
                                        style={{ width: `${result.riskScore}%` }}
                                    />
                                </div>
                            </div>

                            <div className="space-y-6">
                                <div>
                                    <h4 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-2">Summary</h4>
                                    <p className="text-slate-400 text-sm leading-relaxed">{result.summary}</p>
                                </div>

                                {result.flaggedClauses.length > 0 && (
                                    <div>
                                        <h4 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-3">Flagged Clauses</h4>
                                        <div className="space-y-3">
                                            {result.flaggedClauses.map((item, i) => (
                                                <div key={i} className="bg-slate-900/50 p-4 rounded-lg border border-slate-700/50">
                                                    <div className="flex items-start gap-3">
                                                        <AlertTriangle className={`w-4 h-4 mt-0.5 shrink-0 ${item.severity === 'HIGH' ? 'text-rose-400' :
                                                                item.severity === 'MEDIUM' ? 'text-amber-400' : 'text-blue-400'
                                                            }`} />
                                                        <div>
                            <p className="text-slate-300 text-sm italic mb-2">"{item.clause}"</p>
                            <p className="text-slate-400 text-xs">{item.issue}</p>
                                                        </div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {result.missingClauses.length > 0 && (
                                    <div>
                                        <h4 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-2">Missing Clauses</h4>
                                        <ul className="space-y-1">
                                            {result.missingClauses.map((clause, i) => (
                                                <li key={i} className="text-sm text-slate-400 flex items-center gap-2">
                                                    <div className="w-1.5 h-1.5 rounded-full bg-slate-600" />
                                                    {clause}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </div>
                        </div>
                    ) : (
                        <div className="h-full flex flex-col items-center justify-center text-slate-500 border-2 border-dashed border-slate-700 rounded-xl p-12">
                            <FileText className="w-16 h-16 mb-4 opacity-20" />
                            <p>Upload or paste a contract to begin analysis</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default LegalAgent;
