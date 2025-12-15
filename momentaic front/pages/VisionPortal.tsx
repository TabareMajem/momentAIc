
import React, { useState, useEffect } from 'react';
import { useWorkflowStore } from '../stores/workflow-store';
import { useAuthStore } from '../stores/auth-store';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card } from '../components/ui/Card';
import { Bot, ArrowRight, CheckCircle, Terminal, Layers, Code, Sparkles, Loader2, Globe, Zap } from 'lucide-react';
import { cn } from '../lib/utils';
import { analyzeTaskAndGenerateGraph } from '../lib/agent-forge';
import { useToast } from '../components/ui/Toast';

const INDUSTRIES = [
    { id: 'healthcare', label: 'Healthcare', icon: '🏥' },
    { id: 'legal', label: 'Legal Tech', icon: '⚖️' },
    { id: 'ecommerce', label: 'E-Commerce', icon: '🛍️' },
    { id: 'finance', label: 'FinTech', icon: '💸' },
];

const GENERATION_COST = 20;

export default function VisionPortal() {
    const [step, setStep] = useState(0);
    const [industry, setIndustry] = useState('');
    const [appName, setAppName] = useState('');
    const [description, setDescription] = useState('');
    const [logs, setLogs] = useState<string[]>([]);
    const [isGenerating, setIsGenerating] = useState(false);
    
    const { deductCredits, user } = useAuthStore();
    const { toast } = useToast();

    const addLog = (msg: string) => setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`]);

    const handleGenerate = async () => {
        if (!deductCredits(GENERATION_COST)) {
            toast({ type: 'error', title: 'Insufficient Credits', message: `Vision Portal requires ${GENERATION_COST} credits.` });
            return;
        }

        setIsGenerating(true);
        addLog(`Initializing ${appName}...`);
        await new Promise(r => setTimeout(r, 800));
        addLog(`Setting context: ${industry.toUpperCase()}...`);
        await new Promise(r => setTimeout(r, 800));
        
        // Simulate backend generation
        addLog('Analyzing requirements with Gemini 2.5 Flash...');
        await analyzeTaskAndGenerateGraph(description); 
        
        addLog('Blueprint created. Configuring nodes...');
        await new Promise(r => setTimeout(r, 1000));
        
        addLog('Compiling Frontend Assets...');
        await new Promise(r => setTimeout(r, 1200));
        
        addLog('DEPLOYMENT SUCCESSFUL.');
        setIsGenerating(false);
        setStep(3); // Result step
    };

    const handleLaunch = () => {
        toast({ type: 'success', title: 'Sandbox Environment', message: `Initializing ${appName} in isolation container...` });
        setTimeout(() => {
            window.open('/#/agent-forge', '_blank'); // Simulate opening app for now
        }, 1500);
    };

    return (
        <div className="min-h-[calc(100vh-6rem)] relative flex items-center justify-center overflow-hidden">
            {/* Background Effects */}
            <div className="absolute inset-0 bg-[#000] z-0">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-purple-900/20 blur-[120px] rounded-full pointer-events-none"></div>
                <div className="absolute bottom-0 right-0 w-[600px] h-[600px] bg-blue-900/10 blur-[100px] rounded-full pointer-events-none"></div>
                <div className="absolute inset-0 bg-cyber-grid bg-[length:50px_50px] opacity-[0.05]"></div>
            </div>

            <div className="relative z-10 w-full max-w-4xl p-6">
                
                {/* Header */}
                <div className="text-center mb-12">
                    <div className="inline-flex items-center gap-2 border border-white/10 bg-white/5 px-4 py-1 rounded-full text-xs font-mono text-gray-400 mb-6">
                        <Sparkles className="w-3 h-3 text-[#00f0ff]" /> VISION PORTAL BETA
                    </div>
                    <h1 className="text-4xl md:text-6xl font-black text-white tracking-tighter mb-4">
                        BUILD YOUR <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#00f0ff] to-purple-600">UNICORN</span>
                    </h1>
                    <p className="text-gray-400 max-w-lg mx-auto font-mono text-sm">
                        Describe your dream SaaS. Our agents will architect, code, and deploy the MVP in seconds.
                    </p>
                </div>

                {/* Wizard Container */}
                <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl overflow-hidden shadow-2xl relative min-h-[500px] flex flex-col">
                    {/* Progress Bar */}
                    <div className="h-1 bg-gray-800 w-full">
                        <div 
                            className="h-full bg-gradient-to-r from-[#00f0ff] to-purple-600 transition-all duration-500" 
                            style={{ width: `${((step + 1) / 4) * 100}%` }}
                        ></div>
                    </div>

                    <div className="flex-1 p-8 md:p-12 flex flex-col">
                        
                        {/* STEP 0: INDUSTRY */}
                        {step === 0 && (
                            <div className="flex-1 flex flex-col items-center justify-center animate-fade-in">
                                <h2 className="text-2xl font-bold text-white mb-8">Select Your Sector</h2>
                                <div className="grid grid-cols-2 gap-4 w-full max-w-lg">
                                    {INDUSTRIES.map(ind => (
                                        <button 
                                            key={ind.id}
                                            onClick={() => { setIndustry(ind.id); setStep(1); }}
                                            className="group relative p-6 bg-[#111] border border-white/5 rounded-xl hover:border-[#00f0ff] transition-all hover:bg-[#151515] text-left"
                                        >
                                            <div className="text-3xl mb-3 group-hover:scale-110 transition-transform">{ind.icon}</div>
                                            <div className="font-bold text-white group-hover:text-[#00f0ff]">{ind.label}</div>
                                            <div className="text-xs text-gray-500 mt-1">Deploy {ind.label} Agents</div>
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* STEP 1: CONCEPT */}
                        {step === 1 && (
                            <div className="flex-1 flex flex-col justify-center animate-fade-in max-w-lg mx-auto w-full space-y-6">
                                <div>
                                    <h2 className="text-2xl font-bold text-white mb-2">Define The Mission</h2>
                                    <p className="text-gray-400 text-sm">Give your entity a name and a purpose.</p>
                                </div>
                                <div className="space-y-4">
                                    <Input 
                                        placeholder="Project Name (e.g. LegalMind OS)" 
                                        value={appName}
                                        onChange={e => setAppName(e.target.value)}
                                        className="h-12 bg-[#111] border-white/10 text-lg"
                                        autoFocus
                                    />
                                    <textarea 
                                        placeholder="Describe what the system should do. E.g., 'A dashboard that scrapes court records and uses AI to summarize cases for lawyers.'"
                                        value={description}
                                        onChange={e => setDescription(e.target.value)}
                                        className="w-full h-32 bg-[#111] border border-white/10 rounded-lg p-4 text-white placeholder:text-gray-600 focus:outline-none focus:border-[#00f0ff] resize-none"
                                    ></textarea>
                                </div>
                                <div className="flex justify-between pt-4">
                                    <Button variant="ghost" onClick={() => setStep(0)}>Back</Button>
                                    <Button 
                                        variant="cyber" 
                                        onClick={() => setStep(2)} 
                                        disabled={!appName || !description}
                                    >
                                        INITIALIZE ARCHITECT <ArrowRight className="ml-2 w-4 h-4"/>
                                    </Button>
                                </div>
                            </div>
                        )}

                        {/* STEP 2: GENERATION (TERMINAL) */}
                        {step === 2 && (
                            <div className="flex-1 flex flex-col animate-fade-in relative">
                                <div className="absolute inset-0 flex flex-col items-center justify-center z-10 pointer-events-none">
                                    {!isGenerating ? (
                                        <div className="pointer-events-auto text-center space-y-2">
                                            <Button variant="cyber" size="lg" className="animate-pulse shadow-[0_0_30px_#00f0ff]" onClick={handleGenerate}>
                                                START GENERATION SEQUENCE
                                            </Button>
                                            <div className="text-[10px] text-gray-500 font-mono uppercase">Cost: {GENERATION_COST} Credits</div>
                                        </div>
                                    ) : (
                                        <div className="text-center space-y-4 bg-black/80 p-6 rounded-xl backdrop-blur-md border border-white/10">
                                            <Loader2 className="w-12 h-12 text-[#00f0ff] animate-spin mx-auto" />
                                            <div className="text-xl font-bold text-white tracking-widest">BUILDING...</div>
                                        </div>
                                    )}
                                </div>
                                
                                <div className="flex-1 bg-black border border-gray-800 rounded-lg p-4 font-mono text-sm text-green-500 overflow-hidden flex flex-col opacity-50">
                                    <div className="flex items-center gap-2 text-gray-500 border-b border-gray-800 pb-2 mb-2">
                                        <Terminal className="w-4 h-4" /> SYSTEM_LOG
                                    </div>
                                    <div className="flex-1 overflow-y-auto space-y-1">
                                        {logs.map((log, i) => <div key={i}>{log}</div>)}
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* STEP 3: RESULT */}
                        {step === 3 && (
                            <div className="flex-1 flex flex-col items-center justify-center animate-fade-in text-center space-y-8">
                                <div className="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center border border-green-500 text-green-500 mb-4 shadow-[0_0_30px_rgba(34,197,94,0.3)]">
                                    <CheckCircle className="w-10 h-10" />
                                </div>
                                
                                <div>
                                    <h2 className="text-3xl font-black text-white mb-2">SYSTEM READY</h2>
                                    <p className="text-gray-400">{appName} has been deployed to the edge.</p>
                                </div>

                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full max-w-lg">
                                    <Button variant="secondary" className="h-14" onClick={() => window.open('/#/agent-forge', '_blank')}>
                                        <Layers className="mr-2 w-4 h-4" /> View Architecture
                                    </Button>
                                    <Button variant="cyber" className="h-14" onClick={handleLaunch}>
                                        <Globe className="mr-2 w-4 h-4" /> Launch App
                                    </Button>
                                </div>
                                
                                <Button variant="ghost" size="sm" onClick={() => { setStep(0); setLogs([]); }} className="text-gray-500">
                                    Build Another
                                </Button>
                            </div>
                        )}

                    </div>
                </div>
            </div>
        </div>
    );
}
