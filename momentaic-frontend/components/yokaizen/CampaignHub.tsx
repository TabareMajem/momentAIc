import React, { useState, useEffect } from 'react';
import { FolderKanban, Plus, PlayCircle, Pause, CheckCircle, FileText, Upload, Zap, Globe, ArrowRight, RefreshCw, ExternalLink } from 'lucide-react';
import { BackendService } from '../../services/backendService';
import { useToast } from './Toast';

interface Project {
    id: string;
    name: string;
    domain: string;
    description?: string;
    logoUrl?: string;
    campaigns: Campaign[];
}

interface Campaign {
    id: string;
    name: string;
    status: 'DRAFT' | 'ACTIVE' | 'PAUSED' | 'COMPLETED';
    strategyDocUrl?: string;
    tasks?: CampaignTask[];
}

interface CampaignTask {
    id: string;
    title: string;
    description?: string;
    agent: string;
    status: 'PENDING' | 'IN_PROGRESS' | 'DONE' | 'FAILED';
}

// Initial Workspace
const DEFAULT_WORKSPACE = {
    name: 'My GTM Workspace',
    domain: 'yourdomain.com',
    description: 'Central Hub for Growth'
};

const CampaignHub: React.FC = () => {
    const [projects, setProjects] = useState<Project[]>([]);
    const [selectedProject, setSelectedProject] = useState<Project | null>(null);
    const [selectedCampaign, setSelectedCampaign] = useState<Campaign | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [showNewCampaignModal, setShowNewCampaignModal] = useState(false);
    const [newCampaignName, setNewCampaignName] = useState('');
    const [newCampaignDoc, setNewCampaignDoc] = useState('');
    const [strategyText, setStrategyText] = useState('');
    const [isParsing, setIsParsing] = useState(false);
    const { addToast } = useToast();

    useEffect(() => {
        loadProjects();
    }, []);

    const loadProjects = async () => {
        setIsLoading(true);
        try {
            const data = await BackendService.getCampaignProjects();
            setProjects(data);
            if (data.length > 0) setSelectedProject(data[0]);
        } catch (e) {
            console.error('Failed to load projects:', e);
            try {
                // Initialize with single workspace if none exist to enable UI functionality
                await BackendService.createCampaignProject(DEFAULT_WORKSPACE);
                const data = await BackendService.getCampaignProjects();
                setProjects(data);
                if (data.length > 0) setSelectedProject(data[0]);
            } catch (err) {
                console.error('Could not create default workspace', err);
                setProjects([]);
            }
        }
        setIsLoading(false);
    };

    const handleCreateCampaign = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedProject) return;

        try {
            await BackendService.createCampaign(selectedProject.id, {
                name: newCampaignName,
                strategyDocUrl: newCampaignDoc,
            });
            setShowNewCampaignModal(false);
            setNewCampaignName('');
            setNewCampaignDoc('');
            loadProjects();
            addToast('Campaign created!', 'success');
        } catch (e) {
            addToast('Failed to create campaign', 'error');
        }
    };

    const handleParseStrategy = async () => {
        if (!selectedCampaign || !strategyText) return;
        setIsParsing(true);

        try {
            await BackendService.parseCampaignStrategy(selectedCampaign.id, strategyText);
            addToast('Strategy parsed into tasks!', 'success');
            loadProjects();
        } catch (e) {
            addToast('Failed to parse strategy', 'error');
        }
        setIsParsing(false);
    };

    const handleExecuteTask = async (taskId: string) => {
        try {
            await BackendService.executeCampaignTask(taskId);
            addToast('Task executed!', 'success');
            loadProjects();
        } catch (e) {
            addToast('Task execution failed', 'error');
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'ACTIVE': case 'IN_PROGRESS': return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
            case 'DONE': case 'COMPLETED': return 'text-blue-400 bg-blue-500/10 border-blue-500/20';
            case 'PAUSED': return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
            case 'FAILED': return 'text-rose-400 bg-rose-500/10 border-rose-500/20';
            default: return 'text-slate-400 bg-slate-500/10 border-slate-500/20';
        }
    };

    if (isLoading) {
        return (
            <div className="p-6 max-w-6xl mx-auto flex items-center justify-center h-96">
                <RefreshCw className="w-8 h-8 text-indigo-500 animate-spin" />
            </div>
        );
    }

    return (
        <div className="p-6 max-w-7xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between md:items-center gap-4 mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
                        <FolderKanban className="w-8 h-8 text-fuchsia-500" />
                        Campaign Master
                    </h1>
                    <p className="text-slate-400 mt-1">Execute growth strategies across all your projects</p>
                </div>
                <div className="flex items-center gap-2 px-4 py-2 bg-slate-900 rounded-full border border-slate-800">
                    <Zap className="w-4 h-4 text-amber-400" />
                    <span className="text-sm font-medium text-slate-300">{projects.length} Projects</span>
                </div>
            </div>

            {/* Project Tabs */}
            <div className="flex gap-2 overflow-x-auto pb-2 mb-6">
                {projects.map((project) => (
                    <button
                        key={project.id}
                        onClick={() => { setSelectedProject(project); setSelectedCampaign(null); }}
                        className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all whitespace-nowrap ${selectedProject?.id === project.id
                            ? 'bg-indigo-600 text-white'
                            : 'bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700'
                            }`}
                    >
                        <Globe className="w-4 h-4" />
                        {project.name}
                    </button>
                ))}
            </div>

            {/* Main Content */}
            <div className="grid lg:grid-cols-3 gap-6">
                {/* Campaigns List */}
                <div className="lg:col-span-1 bg-slate-900 rounded-2xl border border-slate-800 p-4">
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-lg font-bold text-white">Campaigns</h2>
                        <button
                            onClick={() => setShowNewCampaignModal(true)}
                            className="p-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors"
                        >
                            <Plus className="w-4 h-4" />
                        </button>
                    </div>

                    <div className="space-y-2">
                        {selectedProject?.campaigns.length === 0 && (
                            <div className="text-center py-8 text-slate-500">
                                <FileText className="w-10 h-10 mx-auto mb-2 opacity-50" />
                                <p>No campaigns yet</p>
                            </div>
                        )}
                        {selectedProject?.campaigns.map((campaign) => (
                            <button
                                key={campaign.id}
                                onClick={() => setSelectedCampaign(campaign)}
                                className={`w-full p-3 rounded-xl text-left transition-all ${selectedCampaign?.id === campaign.id
                                    ? 'bg-indigo-600/20 border border-indigo-500/30'
                                    : 'bg-slate-800/50 border border-transparent hover:border-slate-700'
                                    }`}
                            >
                                <div className="flex justify-between items-start">
                                    <h3 className="font-medium text-white">{campaign.name}</h3>
                                    <span className={`text-xs px-2 py-0.5 rounded border ${getStatusColor(campaign.status)}`}>
                                        {campaign.status}
                                    </span>
                                </div>
                                {campaign.strategyDocUrl && (
                                    <a href={campaign.strategyDocUrl} target="_blank" rel="noreferrer" className="text-xs text-indigo-400 flex items-center gap-1 mt-1 hover:underline">
                                        <ExternalLink className="w-3 h-3" /> Strategy Doc
                                    </a>
                                )}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Campaign Detail / Tasks */}
                <div className="lg:col-span-2 bg-slate-900 rounded-2xl border border-slate-800 p-6">
                    {!selectedCampaign ? (
                        <div className="text-center py-16 text-slate-500">
                            <FolderKanban className="w-16 h-16 mx-auto mb-4 opacity-30" />
                            <h3 className="text-lg font-medium text-slate-400">Select a campaign</h3>
                            <p className="text-sm">Or create a new one to get started</p>
                        </div>
                    ) : (
                        <div className="space-y-6">
                            <div className="flex justify-between items-start">
                                <div>
                                    <h2 className="text-2xl font-bold text-white">{selectedCampaign.name}</h2>
                                    <p className="text-slate-500 text-sm">{selectedProject?.domain}</p>
                                </div>
                                <span className={`text-sm px-3 py-1 rounded-full border ${getStatusColor(selectedCampaign.status)}`}>
                                    {selectedCampaign.status}
                                </span>
                            </div>

                            {/* Strategy Parser */}
                            <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700">
                                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                                    <Upload className="w-4 h-4" /> Paste Strategy Document
                                </h3>
                                <textarea
                                    value={strategyText}
                                    onChange={(e) => setStrategyText(e.target.value)}
                                    placeholder="Paste your marketing strategy, campaign brief, or Google Doc content here. AI will parse it into actionable tasks..."
                                    className="w-full h-32 bg-slate-900 border border-slate-700 rounded-lg p-3 text-white text-sm resize-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none"
                                />
                                <button
                                    onClick={handleParseStrategy}
                                    disabled={isParsing || !strategyText}
                                    className="mt-3 bg-gradient-to-r from-indigo-600 to-fuchsia-600 hover:from-indigo-700 hover:to-fuchsia-700 text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {isParsing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
                                    {isParsing ? 'Parsing...' : 'Parse & Create Tasks'}
                                </button>
                            </div>

                            {/* Tasks List */}
                            <div>
                                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-3">Tasks ({selectedCampaign.tasks?.length || 0})</h3>
                                <div className="space-y-2">
                                    {selectedCampaign.tasks?.map((task) => (
                                        <div key={task.id} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                                            <div className="flex items-center gap-3">
                                                <span className={`px-2 py-0.5 text-xs rounded font-mono ${getStatusColor(task.status)}`}>
                                                    {task.agent}
                                                </span>
                                                <div>
                                                    <h4 className="text-white font-medium">{task.title}</h4>
                                                    {task.description && <p className="text-slate-500 text-xs">{task.description}</p>}
                                                </div>
                                            </div>
                                            <div className="flex items-center gap-2">
                                                <span className={`text-xs px-2 py-0.5 rounded border ${getStatusColor(task.status)}`}>
                                                    {task.status}
                                                </span>
                                                {task.status === 'PENDING' && (
                                                    <button
                                                        onClick={() => handleExecuteTask(task.id)}
                                                        className="p-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded transition-colors"
                                                        title="Execute Task"
                                                    >
                                                        <PlayCircle className="w-4 h-4" />
                                                    </button>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                    {(!selectedCampaign.tasks || selectedCampaign.tasks.length === 0) && (
                                        <div className="text-center py-8 text-slate-500">
                                            <p>No tasks yet. Paste a strategy above to generate tasks.</p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* New Campaign Modal */}
            {showNewCampaignModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
                    <div className="bg-slate-900 w-full max-w-md rounded-2xl border border-slate-700 shadow-2xl p-6">
                        <h2 className="text-xl font-bold text-white mb-4">New Campaign</h2>
                        <form onSubmit={handleCreateCampaign} className="space-y-4">
                            <div>
                                <label className="text-xs font-bold text-slate-500 uppercase mb-1 block">Campaign Name</label>
                                <input
                                    type="text"
                                    value={newCampaignName}
                                    onChange={(e) => setNewCampaignName(e.target.value)}
                                    className="w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-white focus:border-indigo-500 outline-none"
                                    placeholder="e.g., Product Hunt Launch"
                                    required
                                />
                            </div>
                            <div>
                                <label className="text-xs font-bold text-slate-500 uppercase mb-1 block">Strategy Doc URL (Optional)</label>
                                <input
                                    type="url"
                                    value={newCampaignDoc}
                                    onChange={(e) => setNewCampaignDoc(e.target.value)}
                                    className="w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-white focus:border-indigo-500 outline-none"
                                    placeholder="https://docs.google.com/..."
                                />
                            </div>
                            <div className="flex gap-3 pt-2">
                                <button type="button" onClick={() => setShowNewCampaignModal(false)} className="flex-1 bg-slate-800 hover:bg-slate-700 text-white py-2 rounded-lg font-medium">
                                    Cancel
                                </button>
                                <button type="submit" className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white py-2 rounded-lg font-medium flex items-center justify-center gap-2">
                                    <Plus className="w-4 h-4" /> Create
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default CampaignHub;
