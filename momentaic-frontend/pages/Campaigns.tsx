
import React, { useState } from 'react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Rocket, Upload, Link as LinkIcon, FileText, Check, Loader2 } from 'lucide-react';
import { useToast } from '../components/ui/Toast';

const PROJECTS = [
    "BondQuests.com",
    "Agentforgeai.com",
    "Symbiotask.com",
    "Yokaizen.com",
    "otaku.yokaizen.com",
    "MomentAic.com"
];

export default function Campaigns() {
    const { toast } = useToast();
    const [selectedProject, setSelectedProject] = useState(PROJECTS[0]);
    const [strategyLink, setStrategyLink] = useState('');
    const [isUploading, setIsUploading] = useState(false);

    const handleExecute = async () => {
        if (!strategyLink) return;

        setIsUploading(true);

        // Simulate API call for now (until backend is ready)
        try {
            await new Promise(resolve => setTimeout(resolve, 2000));

            toast({
                type: 'success',
                title: 'Campaign Initiated',
                message: `Analyzing strategy for ${selectedProject}... check your dashboard shortly.`
            });

            setStrategyLink('');
        } catch (e) {
            toast({ type: 'error', title: 'Error', message: 'Failed to launch campaign' });
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto py-8 px-4">
            <div className="flex items-center gap-3 mb-8">
                <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-brand-purple to-brand-cyan flex items-center justify-center">
                    <Rocket className="w-6 h-6 text-white" />
                </div>
                <div>
                    <h1 className="text-3xl font-bold text-white">Campaign Executor</h1>
                    <p className="text-gray-400">Manage multiple projects from one central command</p>
                </div>
            </div>

            <div className="grid gap-6">
                <Card className="p-8 bg-[#0a0a0a] border-white/10">
                    <h2 className="text-xl font-bold text-white mb-6">Launch New Campaign</h2>

                    {/* Project Selector */}
                    <div className="mb-6">
                        <label className="block text-sm font-medium text-gray-400 mb-2">Target Project</label>
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                            {PROJECTS.map(p => (
                                <button
                                    key={p}
                                    onClick={() => setSelectedProject(p)}
                                    className={`p-3 rounded-lg border text-sm font-mono transition-all text-left ${selectedProject === p
                                            ? 'bg-brand-purple/20 border-brand-purple text-white shadow-[0_0_15px_rgba(124,58,237,0.3)]'
                                            : 'bg-white/5 border-white/10 text-gray-400 hover:bg-white/10'
                                        }`}
                                >
                                    {p}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Strategy Input */}
                    <div className="mb-8">
                        <label className="block text-sm font-medium text-gray-400 mb-2">Strategy Document</label>
                        <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                            <div className="flex flex-col items-center justify-center border-2 border-dashed border-white/10 rounded-lg p-8 mb-4 hover:border-brand-cyan/50 transition-colors">
                                <Upload className="w-8 h-8 text-gray-500 mb-3" />
                                <p className="text-gray-400 text-sm mb-2">Drag and drop your strategy file (Word/PDF)</p>
                                <span className="text-xs text-gray-500 uppercase">OR</span>
                                <div className="flex w-full max-w-md mt-3 gap-2">
                                    <input
                                        type="text"
                                        value={strategyLink}
                                        onChange={(e) => setStrategyLink(e.target.value)}
                                        placeholder="Paste Google Drive / Notion Link..."
                                        className="flex-1 bg-black border border-white/20 rounded-lg px-3 py-2 text-white text-sm focus:border-brand-cyan outline-none"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>

                    <Button
                        variant="cyber"
                        className="w-full py-6 text-lg tracking-widest uppercase font-bold"
                        onClick={handleExecute}
                        disabled={isUploading}
                    >
                        {isUploading ? (
                            <>
                                <Loader2 className="w-5 h-5 mr-3 animate-spin" /> Processing Strategy...
                            </>
                        ) : (
                            <>
                                <Rocket className="w-5 h-5 mr-3" /> Execute Campaign
                            </>
                        )}
                    </Button>
                </Card>
            </div>
        </div>
    );
}
