
import React from 'react';
import { AgentType } from '../../types';
import { Target, ShieldAlert, Sparkles, Film, Workflow, Key, Zap, Database, Users, Scale, LifeBuoy, DollarSign, BrainCircuit, Play, ArrowRight, Clock, Star } from 'lucide-react';

interface AgentHubProps {
    onSelectAgent: (agent: AgentType) => void;
}

const AGENTS_CATALOG = [
    {
        id: AgentType.SNIPER,
        name: "Sniper Agent",
        description: "Autonomous lead generation and outreach at scale.",
        icon: Target,
        color: "text-emerald-400",
        bg: "bg-emerald-500/10",
        border: "border-emerald-500/20",
        status: "Online"
    },
    {
        id: AgentType.CONTENT_CLAY,
        name: "Marketing Clay",
        description: "AI-driven content strategy and social optimization.",
        icon: Sparkles,
        color: "text-fuchsia-400",
        bg: "bg-fuchsia-500/10",
        border: "border-fuchsia-500/20",
        status: "Active"
    },
    {
        id: AgentType.VIRAL,
        name: "Viral Growth",
        description: "Predict trends and generate viral video scripts.",
        icon: Zap,
        color: "text-amber-400",
        bg: "bg-amber-500/10",
        border: "border-amber-500/20",
        status: "New"
    },
    {
        id: AgentType.MOBY_DTC,
        name: "Moby DTC",
        description: "Ecommerce revenue optimization and leak detection.",
        icon: DollarSign,
        color: "text-cyan-400",
        bg: "bg-cyan-500/10",
        border: "border-cyan-500/20",
        status: "Standby"
    },
    {
        id: AgentType.GATEKEEPER,
        name: "Gatekeeper",
        description: "Automated call screening and priority routing.",
        icon: ShieldAlert,
        color: "text-rose-400",
        bg: "bg-rose-500/10",
        border: "border-rose-500/20",
        status: "Online"
    },
    {
        id: AgentType.MEDIA,
        name: "Media Agent",
        description: "Asset management and creative generation.",
        icon: Film,
        color: "text-indigo-400",
        bg: "bg-indigo-500/10",
        border: "border-indigo-500/20",
        status: "Idle"
    },
    {
        id: AgentType.WORKFLOW,
        name: "Workflow",
        description: "Process automation and task orchestration.",
        icon: Workflow,
        color: "text-slate-400",
        bg: "bg-slate-500/10",
        border: "border-slate-500/20",
        status: "Idle"
    },
    {
        id: AgentType.RECRUITING,
        name: "Recruiting",
        description: "Talent acquisition and candidate screening.",
        icon: Users,
        color: "text-blue-400",
        bg: "bg-blue-500/10",
        border: "border-blue-500/20",
        status: "Idle"
    },
    {
        id: AgentType.LEGAL,
        name: "Legal",
        description: "Contract analysis and compliance monitoring.",
        icon: Scale,
        color: "text-red-400",
        bg: "bg-red-500/10",
        border: "border-red-500/20",
        status: "Idle"
    },
    {
        id: AgentType.SUPPORT,
        name: "Support",
        description: "Customer service and ticket resolution.",
        icon: LifeBuoy,
        color: "text-orange-400",
        bg: "bg-orange-500/10",
        border: "border-orange-500/20",
        status: "Idle"
    },
    {
        id: AgentType.PROCUREMENT,
        name: "Procurement",
        description: "Vendor management and cost optimization.",
        icon: Database,
        color: "text-green-400",
        bg: "bg-green-500/10",
        border: "border-green-500/20",
        status: "Idle"
    }
];

const AgentHub: React.FC<AgentHubProps> = ({ onSelectAgent }) => {
    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex flex-col md:flex-row justify-between md:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-white tracking-tight">Neuronal Hub</h1>
                    <p className="text-slate-400 mt-1">Deploy autonomous agents to execute complex business tasks.</p>
                </div>
                <div className="flex items-center gap-2 px-4 py-2 bg-slate-900 rounded-full border border-slate-800">
                    <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                    <span className="text-sm font-medium text-slate-300">System Nominal</span>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {AGENTS_CATALOG.map((agent) => (
                    <button
                        key={agent.id}
                        onClick={() => onSelectAgent(agent.id)}
                        className={`group relative overflow-hidden rounded-2xl border ${agent.border} bg-slate-900/40 hover:bg-slate-900/80 p-6 text-left transition-all duration-300 hover:scale-[1.02] hover:shadow-2xl`}
                    >
                        <div className={`absolute inset-0 bg-gradient-to-br from-transparent to-${agent.color.split('-')[1]}-500/5 opacity-0 group-hover:opacity-100 transition-opacity`}></div>

                        <div className="flex justify-between items-start mb-4">
                            <div className={`w-12 h-12 rounded-xl ${agent.bg} flex items-center justify-center border ${agent.border} group-hover:scale-110 transition-transform duration-300`}>
                                <agent.icon className={`w-6 h-6 ${agent.color}`} />
                            </div>
                            {agent.status === "New" && (
                                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-500 text-white uppercase tracking-wider">New</span>
                            )}
                        </div>

                        <h3 className="text-lg font-bold text-white mb-2 group-hover:text-indigo-300 transition-colors">{agent.name}</h3>
                        <p className="text-sm text-slate-400 mb-6 min-h-[40px] leading-relaxed">{agent.description}</p>

                        <div className="flex items-center text-xs font-medium text-slate-500 group-hover:text-white transition-colors">
                            <Play className="w-3 h-3 mr-1" /> Deploy Agent
                            <ArrowRight className="w-3 h-3 ml-auto opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
                        </div>
                    </button>
                ))}

                {/* Coming Soon Card */}
                <div className="rounded-2xl border border-slate-800/50 bg-slate-900/20 p-6 flex flex-col items-center justify-center text-center opacity-60">
                    <BrainCircuit className="w-10 h-10 text-slate-700 mb-4" />
                    <h3 className="text-base font-bold text-slate-500 mb-1">More Coming Soon</h3>
                    <p className="text-xs text-slate-600">Our neural network is expanding.</p>
                </div>
            </div>
        </div>
    );
};

export default AgentHub;
