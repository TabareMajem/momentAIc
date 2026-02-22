import { useState, useEffect } from 'react';
import {
    Zap, CheckCircle, Clock, Loader, Play, Pause,
    MessageSquare, FileText, Users, TrendingUp, Send
} from 'lucide-react';
import { Button } from '../components/ui/Button';
import { useToast } from '../components/ui/Toast';

// ============ TYPES ============

interface ExecutorTask {
    id: string;
    title: string;
    status: 'completed' | 'in_progress' | 'pending' | 'paused';
    type: 'content' | 'leads' | 'research' | 'outreach';
    completedAt?: Date;
    result?: string;
}

// ============ TASK ITEM ============

function TaskItem({ task }: { task: ExecutorTask }) {
    const getIcon = () => {
        switch (task.type) {
            case 'content': return FileText;
            case 'leads': return Users;
            case 'research': return TrendingUp;
            case 'outreach': return Send;
            default: return Zap;
        }
    };

    const getStatusIcon = () => {
        switch (task.status) {
            case 'completed': return <CheckCircle className="w-5 h-5 text-emerald-400" />;
            case 'in_progress': return <Loader className="w-5 h-5 text-blue-400 animate-spin" />;
            case 'pending': return <Clock className="w-5 h-5 text-slate-400" />;
            case 'paused': return <Pause className="w-5 h-5 text-yellow-400" />;
        }
    };

    const getStatusColor = () => {
        switch (task.status) {
            case 'completed': return 'border-emerald-500/30 bg-emerald-500/5';
            case 'in_progress': return 'border-blue-500/30 bg-blue-500/5';
            case 'pending': return 'border-slate-500/30 bg-slate-500/5';
            case 'paused': return 'border-yellow-500/30 bg-yellow-500/5';
        }
    };

    const Icon = getIcon();

    return (
        <div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className={`flex items-center gap-4 p-4 rounded-xl border ${getStatusColor()} transition-all`}
        >
            <div className="p-2 rounded-lg bg-white/5">
                <Icon className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1">
                <p className="text-white font-medium">{task.title}</p>
                {task.result && (
                    <p className="text-sm text-slate-400 mt-1">{task.result}</p>
                )}
            </div>
            {getStatusIcon()}
        </div>
    );
}

// ============ MAIN EXECUTOR PAGE ============

export default function ExecutorPage() {
    const { toast } = useToast();
    const [focusInput, setFocusInput] = useState('');
    const [tasks, setTasks] = useState<ExecutorTask[]>([]);
    const [isExecuting, setIsExecuting] = useState(true);

    // Simulate AI working
    useEffect(() => {
        // Demo tasks showing what AI has done and is doing
        setTasks([
            {
                id: '1',
                title: 'Posted to LinkedIn',
                status: 'completed',
                type: 'content',
                result: '"5 lessons from our first 100 users..."'
            },
            {
                id: '2',
                title: 'Generated 10 qualified leads',
                status: 'completed',
                type: 'leads',
                result: 'Tech founders in California'
            },
            {
                id: '3',
                title: 'Writing blog post about product updates',
                status: 'in_progress',
                type: 'content',
            },
            {
                id: '4',
                title: 'Competitor analysis',
                status: 'pending',
                type: 'research',
            },
        ]);
    }, []);

    const handleFocusSubmit = async () => {
        if (!focusInput.trim()) return;

        toast({
            type: 'success',
            title: '🎯 Focus Updated',
            message: `AI will now prioritize: "${focusInput}"`
        });

        // Add new task based on focus
        setTasks(prev => [{
            id: Date.now().toString(),
            title: focusInput,
            status: 'in_progress',
            type: 'research',
        }, ...prev]);

        setFocusInput('');
    };

    const completedCount = tasks.filter(t => t.status === 'completed').length;
    const inProgressCount = tasks.filter(t => t.status === 'in_progress').length;

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
            {/* Header */}
            <div className="max-w-3xl mx-auto pt-12 px-6">
                <div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center mb-12"
                >
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/20 mb-6">
                        {isExecuting ? (
                            <>
                                <Loader className="w-4 h-4 text-emerald-400 animate-spin" />
                                <span className="text-sm text-emerald-400">AI is working...</span>
                            </>
                        ) : (
                            <>
                                <Pause className="w-4 h-4 text-yellow-400" />
                                <span className="text-sm text-yellow-400">Paused</span>
                            </>
                        )}
                    </div>

                    <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
                        Your AI CEO
                    </h1>
                    <p className="text-slate-400 text-lg">
                        {completedCount} tasks completed today · {inProgressCount} in progress
                    </p>
                </div>

                {/* Focus Input */}
                <div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-12"
                >
                    <div className="relative">
                        <input
                            type="text"
                            value={focusInput}
                            onChange={(e) => setFocusInput(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleFocusSubmit()}
                            placeholder="What should I focus on?"
                            className="w-full px-6 py-4 rounded-2xl bg-white/5 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500/50 text-lg"
                        />
                        <button
                            onClick={handleFocusSubmit}
                            className="absolute right-2 top-1/2 -translate-y-1/2 p-3 rounded-xl bg-emerald-500 hover:bg-emerald-400 transition-colors"
                        >
                            <Play className="w-5 h-5 text-white" />
                        </button>
                    </div>
                    <p className="text-center text-sm text-slate-500 mt-3">
                        Or let me decide what's most important
                    </p>
                </div>

                {/* Task List */}
                <div className="space-y-4 pb-12">
                    
                        {tasks.map((task, idx) => (
                            <div
                                key={task.id}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: idx * 0.1 }}
                            >
                                <TaskItem task={task} />
                            </div>
                        ))}
                    
                </div>
            </div>
        </div>
    );
}
