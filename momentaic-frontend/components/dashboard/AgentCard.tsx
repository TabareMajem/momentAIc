import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp, CheckCircle, Clock, Pause, FileText, Send, TrendingUp, Eye, Users, BarChart2, Bot, Loader } from 'lucide-react';
import { Button } from '../ui/Button';

export interface AgentActivity {
    id: string;
    agent: string;
    task: string;
    status: 'pending' | 'running' | 'complete' | 'error';
    progress: number;
    message: string;
    result?: any;
    started_at: string;
}

const AGENT_ICONS: Record<string, any> = {
    ContentAgent: FileText,
    SDRAgent: Send,
    GrowthHackerAgent: TrendingUp,
    CompetitorIntelAgent: Eye,
    LeadResearcherAgent: Users,
    MarketingAgent: BarChart2,
    default: Bot,
};

const AGENT_COLORS: Record<string, string> = {
    ContentAgent: 'from-purple-500',
    SDRAgent: 'from-blue-500',
    GrowthHackerAgent: 'from-green-500',
    CompetitorIntelAgent: 'from-orange-500',
    LeadResearcherAgent: 'from-yellow-500',
    MarketingAgent: 'from-indigo-500',
    default: 'from-slate-500',
};

export function AgentCard({ activity }: { activity: AgentActivity }) {
    const [expanded, setExpanded] = useState(false);
    const Icon = AGENT_ICONS[activity.agent] || AGENT_ICONS.default;
    const color = AGENT_COLORS[activity.agent] || AGENT_COLORS.default;

    const getStatusIndicator = () => {
        switch (activity.status) {
            case 'running':
                return <Loader className="w-4 h-4 text-blue-400 animate-spin" />;
            case 'complete':
                return <CheckCircle className="w-4 h-4 text-emerald-400" />;
            case 'error':
                return <span className="w-2 h-2 rounded-full bg-red-500" />;
            case 'pending':
                return <Clock className="w-4 h-4 text-slate-400" />;
        }
    };

    return (
        <motion.div 
            layout
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-[#111111]/50 rounded-xl border border-white/5 overflow-hidden hover:border-white/10 transition-colors"
        >
            <motion.div
                layout
                className="p-4 cursor-pointer"
                onClick={() => setExpanded(!expanded)}
            >
                <motion.div layout className="flex items-center gap-4">
                    <div className={`p-2 rounded-lg bg-[#111111] ${color}`}>
                        <Icon className="w-5 h-5 text-white" />
                    </div>

                    <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                            <span className="font-medium text-white">{activity.agent}</span>
                            {getStatusIndicator()}
                        </div>
                        <p className="text-sm text-slate-400 truncate">{activity.task}</p>
                    </div>

                    {activity.status === 'running' && (
                        <div className="text-right">
                            <span className="text-sm font-medium text-blue-400">{activity.progress}%</span>
                        </div>
                    )}

                    <motion.div
                        animate={{ rotate: expanded ? 180 : 0 }}
                        transition={{ duration: 0.2 }}
                    >
                        <ChevronDown className="w-4 h-4 text-slate-400" />
                    </motion.div>
                </motion.div>

                {activity.status === 'running' && (
                    <motion.div layout className="mt-3 h-1 bg-[#1A1A1A] rounded-full overflow-hidden">
                        <motion.div
                            className="h-full bg-blue-500"
                            initial={{ width: 0 }}
                            animate={{ width: `${activity.progress}%` }}
                            transition={{ ease: "linear", duration: 0.5 }}
                        />
                    </motion.div>
                )}
            </motion.div>

            <AnimatePresence>
                {expanded && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ type: "spring", bounce: 0, duration: 0.3 }}
                        className="overflow-hidden border-t border-white/5"
                    >
                        <div className="p-4 space-y-3">
                            <div className="bg-[#1A1A1A]/50 rounded-lg p-3">
                                <p className="text-xs text-slate-500 mb-1">Current Status</p>
                                <p className="text-sm text-slate-300 font-mono">
                                    {activity.message || 'Processing...'}
                                </p>
                            </div>

                            {activity.result && (
                                <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-3">
                                    <p className="text-xs text-emerald-400 mb-1">Result</p>
                                    <p className="text-sm text-emerald-300">
                                        {typeof activity.result === 'string'
                                            ? activity.result.slice(0, 200)
                                            : JSON.stringify(activity.result).slice(0, 200)}
                                    </p>
                                </div>
                            )}

                            <div className="flex gap-2">
                                {activity.status === 'running' && (
                                    <Button size="sm" variant="outline">
                                        <Pause className="w-3 h-3 mr-1" />
                                        Pause
                                    </Button>
                                )}
                                {activity.status === 'complete' && (
                                    <Button size="sm" variant="cyber">
                                        View Full Result
                                    </Button>
                                )}
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
}
