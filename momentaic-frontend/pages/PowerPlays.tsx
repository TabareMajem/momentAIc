import { useState } from 'react';
import {
    Rocket, Zap, Users, Target, TrendingUp, Play, Loader, CheckCircle,
    FileText, Mail, Brain, Sparkles, ChevronRight, Clock
} from 'lucide-react';
import { Button } from '../components/ui/Button';
import { useToast } from '../components/ui/Toast';

// ============ POWER PLAY DEFINITIONS ============

interface PowerPlay {
    id: string;
    name: string;
    description: string;
    icon: React.ElementType;
    gradient: string;
    estimatedTime: string;
    agentChain: string[];
    outputs: string[];
}

const POWER_PLAYS: PowerPlay[] = [
    {
        id: 'product_hunt_launch',
        name: 'Product Hunt Launch',
        description: 'Complete 7-day launch strategy with content, community outreach, and maker network activation.',
        icon: Rocket,
        gradient: 'from-orange-500 to-red-600',
        estimatedTime: '~3 min',
        agentChain: ['launch_strategist', 'content', 'community', 'sdr'],
        outputs: ['Launch Strategy PDF', 'Content Calendar', 'Maker Hit List', 'Outreach Templates']
    },
    {
        id: 'lead_gen_machine',
        name: 'Lead Gen Machine',
        description: 'Scrape, research, and draft personalized outreach for 50 high-quality leads.',
        icon: Target,
        gradient: 'from-blue-500 to-cyan-500',
        estimatedTime: '~5 min',
        agentChain: ['lead_scraper', 'lead_researcher', 'sdr'],
        outputs: ['Enriched Lead List (CSV)', 'Research Profiles', 'Draft Emails']
    },
    {
        id: 'content_blitz',
        name: 'Content Blitz',
        description: 'Month-long content calendar plus 10 ready-to-post pieces for LinkedIn and Twitter.',
        icon: Sparkles,
        gradient: 'from-purple-500 to-pink-500',
        estimatedTime: '~4 min',
        agentChain: ['strategy', 'content', 'marketing'],
        outputs: ['Content Calendar', '10 Social Posts', 'Hashtag Strategy', 'Posting Schedule']
    },
    {
        id: 'competitor_roast',
        name: 'Competitor Roast',
        description: 'Deep competitive analysis with battle cards and counter-positioning content.',
        icon: TrendingUp,
        gradient: 'from-green-500 to-emerald-600',
        estimatedTime: '~3 min',
        agentChain: ['competitor_intel', 'growth_hacker', 'content'],
        outputs: ['Battle Card PDF', 'Competitive Matrix', 'Counter-Positioning Posts']
    },
];

// ============ POWER PLAY CARD ============

function PowerPlayCard({
    play,
    onExecute,
    isExecuting
}: {
    play: PowerPlay;
    onExecute: () => void;
    isExecuting: boolean;
}) {
    const Icon = play.icon;

    return (
        <div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="relative overflow-hidden rounded-2xl border border-white/10 bg-slate-900/50 backdrop-blur-xl"
        >
            {/* Gradient Header */}
            <div className={`h-2 bg-gradient-to-r ${play.gradient}`} />

            <div className="p-6">
                {/* Icon & Title */}
                <div className="flex items-start gap-4 mb-4">
                    <div className={`p-3 rounded-xl bg-gradient-to-br ${play.gradient} bg-opacity-20`}>
                        <Icon className="w-6 h-6 text-white" />
                    </div>
                    <div className="flex-1">
                        <h3 className="text-lg font-semibold text-white">{play.name}</h3>
                        <p className="text-sm text-slate-400 mt-1">{play.description}</p>
                    </div>
                </div>

                {/* Agent Chain Visualization */}
                <div className="mb-4">
                    <div className="text-xs text-slate-500 uppercase tracking-wide mb-2">Agent Chain</div>
                    <div className="flex items-center gap-1 flex-wrap">
                        {play.agentChain.map((agent, idx) => (
                            <div key={agent} className="flex items-center">
                                <span className="px-2 py-1 rounded-md bg-slate-800 text-xs text-slate-300 capitalize">
                                    {agent.replace('_', ' ')}
                                </span>
                                {idx < play.agentChain.length - 1 && (
                                    <ChevronRight className="w-3 h-3 text-slate-600 mx-1" />
                                )}
                            </div>
                        ))}
                    </div>
                </div>

                {/* Outputs */}
                <div className="mb-4">
                    <div className="text-xs text-slate-500 uppercase tracking-wide mb-2">You'll Get</div>
                    <div className="flex flex-wrap gap-2">
                        {play.outputs.map(output => (
                            <span key={output} className="flex items-center gap-1 px-2 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs">
                                <FileText className="w-3 h-3" />
                                {output}
                            </span>
                        ))}
                    </div>
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between pt-4 border-t border-white/5">
                    <div className="flex items-center gap-2 text-slate-400 text-sm">
                        <Clock className="w-4 h-4" />
                        {play.estimatedTime}
                    </div>
                    <Button
                        variant="cyber"
                        size="sm"
                        onClick={onExecute}
                        disabled={isExecuting}
                        className={`bg-gradient-to-r ${play.gradient}`}
                    >
                        {isExecuting ? (
                            <>
                                <Loader className="w-4 h-4 mr-2 animate-spin" />
                                Executing...
                            </>
                        ) : (
                            <>
                                <Play className="w-4 h-4 mr-2" />
                                Execute
                            </>
                        )}
                    </Button>
                </div>
            </div>
        </div>
    );
}

// ============ MAIN PAGE ============

export default function PowerPlays() {
    const { toast } = useToast();
    const [executingId, setExecutingId] = useState<string | null>(null);
    const [results, setResults] = useState<Record<string, any>>({});

    const handleExecute = async (play: PowerPlay) => {
        setExecutingId(play.id);
        toast({
            type: 'info',
            title: `🚀 ${play.name} Started`,
            message: `Chaining ${play.agentChain.length} agents... This may take a few minutes.`
        });

        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch('/api/v1/forge/execute-chain', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    chain: play.agentChain,
                    context: {
                        power_play: play.id,
                        task_name: play.name,
                        task_description: play.description
                    }
                })
            });

            if (!response.ok) throw new Error('Execution failed');

            const result = await response.json();
            setResults(prev => ({ ...prev, [play.id]: result }));

            toast({
                type: 'success',
                title: '✅ Power Play Complete!',
                message: `${play.name} finished. Check The Vault for your deliverables.`
            });
        } catch (error) {
            console.error(error);
            toast({
                type: 'error',
                title: 'Execution Failed',
                message: 'Something went wrong. Please try again.'
            });
        } finally {
            setExecutingId(null);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-8">
            {/* Header */}
            <div className="max-w-7xl mx-auto mb-12">
                <div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center"
                >
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-purple-500/20 to-cyan-500/20 border border-purple-500/30 mb-6">
                        <Zap className="w-4 h-4 text-yellow-400" />
                        <span className="text-sm text-purple-300">One-Click Marketing Campaigns</span>
                    </div>
                    <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
                        Power Plays
                    </h1>
                    <p className="text-slate-400 text-lg max-w-2xl mx-auto">
                        Execute complete marketing campaigns with a single click.
                        Each Power Play chains multiple AI agents together to deliver real results.
                    </p>
                </div>
            </div>

            {/* Power Play Grid */}
            <div className="max-w-7xl mx-auto">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {POWER_PLAYS.map((play, idx) => (
                        <div
                            key={play.id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: idx * 0.1 }}
                        >
                            <PowerPlayCard
                                play={play}
                                onExecute={() => handleExecute(play)}
                                isExecuting={executingId === play.id}
                            />
                        </div>
                    ))}
                </div>
            </div>

            {/* Results Section */}
            {Object.keys(results).length > 0 && (
                <div className="max-w-7xl mx-auto mt-12">
                    <h2 className="text-2xl font-semibold text-white mb-6">Recent Results</h2>
                    <div className="bg-slate-900/50 rounded-xl border border-white/10 p-6">
                        <pre className="text-sm text-slate-300 overflow-auto">
                            {JSON.stringify(results, null, 2)}
                        </pre>
                    </div>
                </div>
            )}
        </div>
    );
}
