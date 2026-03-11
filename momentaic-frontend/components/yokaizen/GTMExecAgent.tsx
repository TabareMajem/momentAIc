import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, Play, CheckCircle, AlertTriangle, Loader2, ArrowRight, LayoutDashboard, Calendar } from 'lucide-react';
import { BackendService } from '../../services/backendService';
import { useToast } from './Toast';

const GTMExecAgent: React.FC = () => {
    const [isUploading, setIsUploading] = useState(false);
    const [campaign, setCampaign] = useState<any>(null);
    const [strategy, setStrategy] = useState<any>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const { addToast } = useToast();

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setIsUploading(true);
        try {
            const response = await BackendService.uploadGTMDoc(file);
            setCampaign(response.campaign);
            setStrategy(response.strategy);
            addToast('GTM Strategy Extracted Successfully!', 'success');
        } catch (error: any) {
            console.error(error);
            addToast('Failed to parse strategy document', 'error');
        } finally {
            setIsUploading(false);
        }
    };

    const handleExecuteTask = async (taskId: string) => {
        if (!taskId) {
            addToast('Task ID represents a real DB task but is missing from this payload.', 'error');
            return;
        }
        try {
            const response = await BackendService.executeCampaignTask(taskId);
            if (response.action === 'redirect') {
                addToast(`Redirecting to ${response.to} for execution...`, 'info');
                // Allow toast to show briefly
                setTimeout(() => window.location.href = response.to, 1000);
            } else {
                addToast('Task started successfully', 'success');
            }
        } catch (error) {
            addToast('Failed to execute task', 'error');
        }
    };

    return (
        <div className="p-6 max-w-[1600px] mx-auto animate-fade-in text-slate-200 min-h-screen bg-[#02040a]">
            {/* Header */}
            <div className="mb-8 border-b border-indigo-900/30 pb-6">
                <h2 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-500 flex items-center gap-4">
                    <LayoutDashboard className="w-10 h-10 text-emerald-500" />
                    GTM Executive Agent
                </h2>
                <p className="text-emerald-400/60 mt-2 text-lg font-light tracking-wide">
                    Document-Driven Growth Execution • From PDF to Revenue
                </p>
            </div>

            {!strategy ? (
                <div className="min-h-[500px] flex flex-col items-center justify-center border-2 border-dashed border-emerald-500/20 rounded-3xl bg-slate-900/50 p-12">
                    <div className="w-24 h-24 bg-emerald-500/10 rounded-full flex items-center justify-center mb-6 animate-pulse">
                        <UploadCloud className="w-12 h-12 text-emerald-400" />
                    </div>
                    <h3 className="text-2xl font-bold text-white mb-3">Upload GTM Strategy</h3>
                    <p className="text-slate-400 max-w-md text-center mb-8">
                        Upload your Product GTM Plan (PDF, DOCX). The AI will extract timeline, channels, and tasks, then auto-assign them to agents.
                    </p>

                    <input
                        ref={fileInputRef}
                        type="file"
                        accept=".pdf,.docx,.txt"
                        className="hidden"
                        onChange={handleFileUpload}
                    />

                    <button
                        onClick={() => fileInputRef.current?.click()}
                        disabled={isUploading}
                        className="bg-emerald-600 hover:bg-emerald-500 text-white px-8 py-4 rounded-xl font-bold text-lg flex items-center gap-3 transition-all shadow-lg shadow-emerald-900/40"
                    >
                        {isUploading ? <Loader2 className="w-6 h-6 animate-spin" /> : <FileText className="w-6 h-6" />}
                        {isUploading ? 'Analyzing Strategy...' : 'Select Document'}
                    </button>

                    <p className="mt-4 text-xs text-slate-600 uppercase tracking-widest">Supports PDF • DOCX • TXT</p>
                </div>
            ) : (
                <div className="animate-in slide-in-from-bottom-8 duration-700">
                    {/* Strategy Overview */}
                    <div className="grid md:grid-cols-3 gap-6 mb-8">
                        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
                            <h3 className="text-sm font-bold text-slate-500 uppercase mb-2">Campaign Name</h3>
                            <p className="text-xl font-bold text-white">{strategy.campaign_name}</p>
                        </div>
                        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
                            <h3 className="text-sm font-bold text-slate-500 uppercase mb-2">Timeline</h3>
                            <div className="flex items-center gap-2">
                                <Calendar className="w-5 h-5 text-emerald-400" />
                                <span className="text-xl font-bold text-white">{strategy.timeline_days} Days</span>
                            </div>
                        </div>
                        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
                            <h3 className="text-sm font-bold text-slate-500 uppercase mb-2">Target Audience</h3>
                            <p className="text-sm text-slate-300">{strategy.target_audience}</p>
                        </div>
                    </div>

                    {/* Execution Timeline */}
                    <div className="space-y-6">
                        <h3 className="text-2xl font-bold text-white flex items-center gap-3">
                            <Play className="w-6 h-6 text-emerald-400" /> Execution Pipeline
                        </h3>

                        {strategy.weekly_tasks?.map((week: any, wIndex: number) => (
                            <div key={wIndex} className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
                                <div className="bg-slate-950 px-6 py-3 border-b border-slate-800 flex justify-between items-center">
                                    <span className="font-bold text-emerald-400">Week {week.week}</span>
                                    <span className="text-xs text-slate-500">{week.tasks.length} Tasks</span>
                                </div>
                                <div className="divide-y divide-slate-800">
                                    {week.tasks.map((task: any, tIndex: number) => (
                                        <div key={tIndex} className="p-4 flex items-center gap-4 hover:bg-slate-800/30 transition-colors">
                                            <div className="w-10 h-10 rounded-lg bg-slate-800 flex items-center justify-center shrink-0">
                                                {task.automation_possible ? (
                                                    <CheckCircle className="w-5 h-5 text-emerald-500" />
                                                ) : (
                                                    <AlertTriangle className="w-5 h-5 text-amber-500" />
                                                )}
                                            </div>
                                            <div className="flex-1">
                                                <div className="flex items-center gap-2 mb-1">
                                                    <span className="font-bold text-slate-200">{task.title}</span>
                                                    <span className="bg-slate-800 text-slate-400 text-[10px] px-2 py-0.5 rounded uppercase font-bold tracking-wider">
                                                        {task.platform}
                                                    </span>
                                                    <span className="bg-indigo-900/30 text-indigo-400 text-[10px] px-2 py-0.5 rounded uppercase font-bold tracking-wider">
                                                        {task.agent}
                                                    </span>
                                                </div>
                                                <p className="text-sm text-slate-500">{task.description}</p>
                                            </div>
                                            <button
                                                onClick={() => handleExecuteTask(task.id)} // We now have the real ID mapped from the API response
                                                className="bg-slate-800 hover:bg-emerald-600 hover:text-white px-4 py-2 rounded-lg text-sm font-bold text-slate-300 transition-all flex items-center gap-2"
                                            >
                                                Execute <ArrowRight className="w-4 h-4" />
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default GTMExecAgent;
