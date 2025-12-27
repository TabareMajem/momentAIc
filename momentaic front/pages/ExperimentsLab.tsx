import React, { useState } from 'react';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Input } from '../components/ui/Input';
import { Textarea } from '../components/ui/Textarea';
import { useToast } from '../components/ui/Toast';
import { cn } from '../lib/utils';
import {
    FlaskConical, Target, TrendingUp, CheckCircle, Clock, Play,
    Pause, BarChart2, Users, Zap, Sparkles, ChevronRight,
    Copy, BookOpen, Rocket, Mail, MessageSquare, Globe,
    PenTool, Share2, ArrowRight, AlertCircle
} from 'lucide-react';

// ============ TYPES ============

interface Experiment {
    id: string;
    name: string;
    hypothesis: string;
    status: 'draft' | 'running' | 'paused' | 'completed';
    metric: string;
    baseline: number;
    target: number;
    current?: number;
    startDate?: string;
    endDate?: string;
    winner?: 'A' | 'B' | 'inconclusive';
}

interface ExperimentTemplate {
    id: string;
    category: string;
    name: string;
    icon: string;
    description: string;
    hypothesis: string;
    metric: string;
    duration: string;
    difficulty: 'Easy' | 'Medium' | 'Hard';
    steps: string[];
}

// ============ EXPERIMENT TEMPLATES ============

const EXPERIMENT_TEMPLATES: ExperimentTemplate[] = [
    {
        id: 'first-100-users',
        category: 'Acquisition',
        name: 'First 100 Users Playbook',
        icon: '🚀',
        description: 'Systematic approach to get your first 100 users through multiple channels',
        hypothesis: 'By systematically testing 5 acquisition channels, we can find one that converts at >5%',
        metric: 'Signups',
        duration: '2 weeks',
        difficulty: 'Medium',
        steps: [
            'Define your ideal customer profile (ICP)',
            'Create a simple landing page with clear value prop',
            'Set up 5 acquisition experiments: LinkedIn outreach, Reddit posts, Twitter threads, Product Hunt comment strategy, cold email',
            'Run each for 3 days, track conversions',
            'Double down on top 2 performers',
            'Aim for 20 users per winning channel',
        ],
    },
    {
        id: 'product-hunt-launch',
        category: 'Launch',
        name: 'Product Hunt Launch Checklist',
        icon: '🎯',
        description: 'Step-by-step guide to a successful Product Hunt launch',
        hypothesis: 'A well-prepared PH launch can generate 500+ signups in 24 hours',
        metric: 'Upvotes & Signups',
        duration: '3 weeks prep + 1 day launch',
        difficulty: 'Hard',
        steps: [
            'Week 1: Build a hunter network (10+ connections)',
            'Week 2: Prepare assets (GIF, screenshots, video)',
            'Week 3: Pre-launch outreach to supporters',
            'Launch day: Post at 12:01 AM PST',
            'Engage with every comment within 30 minutes',
            'Share on all social channels immediately',
            'Send email blast to existing users',
            'Post-launch: Follow up with every upvoter',
        ],
    },
    {
        id: 'viral-linkedin-post',
        category: 'Content',
        name: 'LinkedIn Viral Post Formula',
        icon: '📈',
        description: 'Structure for creating high-engagement LinkedIn posts',
        hypothesis: 'Posts following the hook-story-lesson format get 3x more engagement',
        metric: 'Impressions & Engagement',
        duration: '1 week',
        difficulty: 'Easy',
        steps: [
            'Write a pattern-interrupt hook (first line)',
            'Share a personal story with vulnerability',
            'Include specific numbers and results',
            'End with a thought-provoking question',
            'Post between 8-10 AM local time',
            'Engage with first 20 comments within 1 hour',
            'Repost as Twitter thread with modifications',
        ],
    },
    {
        id: 'cold-email-sequence',
        category: 'Outreach',
        name: 'Cold Email Sequence Builder',
        icon: '📧',
        description: '5-email sequence template for B2B outreach',
        hypothesis: 'A personalized 5-email sequence achieves >15% reply rate',
        metric: 'Reply Rate',
        duration: '2 weeks',
        difficulty: 'Medium',
        steps: [
            'Research 100 ideal prospects on LinkedIn',
            'Find emails using Hunter.io or Apollo',
            'Email 1: Problem acknowledgment (Day 1)',
            'Email 2: Social proof case study (Day 3)',
            'Email 3: Value-add with free resource (Day 5)',
            'Email 4: Breakup email with urgency (Day 8)',
            'Email 5: Final follow-up with different angle (Day 14)',
            'Track opens, clicks, and replies',
        ],
    },
    {
        id: 'landing-page-ab',
        category: 'Conversion',
        name: 'Landing Page A/B Test',
        icon: '🧪',
        description: 'Test variations to optimize conversion rate',
        hypothesis: 'Testing headline and CTA can improve conversion by 20%+',
        metric: 'Conversion Rate',
        duration: '1-2 weeks',
        difficulty: 'Easy',
        steps: [
            'Define your current conversion rate baseline',
            'Create 2-3 headline variations',
            'Create 2-3 CTA button variations',
            'Use tool like Google Optimize or Vercel Edge',
            'Run until 100+ conversions per variant',
            'Calculate statistical significance',
            'Implement winner and move to next test',
        ],
    },
    {
        id: 'referral-program',
        category: 'Viral',
        name: 'Referral Program Launch',
        icon: '🎁',
        description: 'Design and launch a high-converting referral program',
        hypothesis: 'A well-designed referral program can achieve K-factor >0.3',
        metric: 'K-Factor (Viral Coefficient)',
        duration: '1 week setup + ongoing',
        difficulty: 'Medium',
        steps: [
            'Define referral reward (both sides)',
            'Create unique referral links for users',
            'Design referral dashboard in-app',
            'Write share templates (email, social)',
            'Add referral prompt at key moments',
            'Track: invites sent, signups, K-factor',
            'Optimize based on drop-off points',
        ],
    },
    {
        id: 'twitter-thread',
        category: 'Content',
        name: 'Twitter Thread Strategy',
        icon: '🐦',
        description: 'Create viral Twitter threads that drive traffic',
        hypothesis: 'Educational threads with strong hooks get 10x engagement vs regular tweets',
        metric: 'Impressions & Link Clicks',
        duration: '1 week',
        difficulty: 'Easy',
        steps: [
            'Find trending topics in your niche',
            'Write a hook that creates curiosity',
            'Structure: 1 insight per tweet, 8-12 tweets',
            'Include visuals every 3rd tweet',
            'End with CTA and link',
            'Post between 8-11 AM EST or 4-6 PM EST',
            'Engage with replies for first 2 hours',
            'Quote tweet yourself to extend reach',
        ],
    },
    {
        id: 'pricing-experiment',
        category: 'Monetization',
        name: 'Pricing Page Optimization',
        icon: '💰',
        description: 'Test pricing tiers and presentation',
        hypothesis: 'Changing pricing structure can increase ARPU by 25%',
        metric: 'ARPU & Conversion',
        duration: '2-4 weeks',
        difficulty: 'Hard',
        steps: [
            'Analyze current pricing conversion funnel',
            'Test 3-tier vs 2-tier pricing',
            'Test annual vs monthly default',
            'Test price anchoring (enterprise tier)',
            'Test adding/removing features per tier',
            'Run with significant traffic (500+ pageviews per variant)',
            'Calculate LTV impact, not just conversion',
        ],
    },
];

// ============ CATEGORY CONFIG ============

const CATEGORIES = [
    { id: 'all', name: 'All', icon: '🔥' },
    { id: 'Acquisition', name: 'Acquisition', icon: '🎯' },
    { id: 'Launch', name: 'Launch', icon: '🚀' },
    { id: 'Content', name: 'Content', icon: '📝' },
    { id: 'Outreach', name: 'Outreach', icon: '📧' },
    { id: 'Conversion', name: 'Conversion', icon: '📈' },
    { id: 'Viral', name: 'Viral', icon: '🔄' },
    { id: 'Monetization', name: 'Monetization', icon: '💰' },
];

// ============ EXPERIMENT CARD COMPONENT ============

function ExperimentCard({ template, onStart }: { template: ExperimentTemplate; onStart: () => void }) {
    const [expanded, setExpanded] = useState(false);

    return (
        <Card className="p-5 bg-black/50 border-white/10 hover:border-[#00f0ff]/30 transition-all">
            <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                    <span className="text-2xl">{template.icon}</span>
                    <div>
                        <h3 className="font-bold text-white">{template.name}</h3>
                        <div className="flex items-center gap-2 mt-1">
                            <Badge variant="outline" className="text-xs">{template.category}</Badge>
                            <Badge
                                variant={template.difficulty === 'Easy' ? 'success' : template.difficulty === 'Medium' ? 'warning' : 'destructive'}
                                className="text-xs"
                            >
                                {template.difficulty}
                            </Badge>
                        </div>
                    </div>
                </div>
                <div className="text-right">
                    <div className="text-xs text-gray-500">{template.duration}</div>
                </div>
            </div>

            <p className="text-sm text-gray-400 mb-4">{template.description}</p>

            <div className="bg-[#00f0ff]/5 border border-[#00f0ff]/20 rounded-lg p-3 mb-4">
                <div className="text-xs text-[#00f0ff] uppercase tracking-wider mb-1">Hypothesis</div>
                <p className="text-sm text-gray-300">{template.hypothesis}</p>
            </div>

            <button
                onClick={() => setExpanded(!expanded)}
                className="text-sm text-[#00f0ff] flex items-center gap-1 hover:underline mb-3"
            >
                {expanded ? 'Hide' : 'Show'} Steps ({template.steps.length})
                <ChevronRight className={cn("w-4 h-4 transition-transform", expanded && "rotate-90")} />
            </button>

            {expanded && (
                <div className="space-y-2 mb-4 animate-fade-in">
                    {template.steps.map((step, i) => (
                        <div key={i} className="flex items-start gap-2 text-sm text-gray-400">
                            <span className="text-[#00f0ff] font-mono text-xs mt-0.5">{String(i + 1).padStart(2, '0')}</span>
                            <span>{step}</span>
                        </div>
                    ))}
                </div>
            )}

            <div className="flex gap-2">
                <Button onClick={onStart} variant="cyber" size="sm" className="flex-1">
                    <Play className="w-3 h-3 mr-2" />
                    Start Experiment
                </Button>
                <Button variant="outline" size="sm">
                    <Copy className="w-3 h-3 mr-2" />
                    Copy
                </Button>
            </div>
        </Card>
    );
}

// ============ ACTIVE EXPERIMENTS COMPONENT ============

function ActiveExperiments() {
    const [experiments] = useState<Experiment[]>([
        {
            id: '1',
            name: 'LinkedIn Viral Post Test',
            hypothesis: 'Posts with personal stories get more engagement',
            status: 'running',
            metric: 'Engagement Rate',
            baseline: 2.5,
            target: 7.5,
            current: 5.2,
            startDate: '2024-12-20',
        },
        {
            id: '2',
            name: 'Cold Email Subject Line A/B',
            hypothesis: 'Question-based subjects get higher open rates',
            status: 'completed',
            metric: 'Open Rate',
            baseline: 22,
            target: 35,
            current: 41,
            startDate: '2024-12-10',
            endDate: '2024-12-20',
            winner: 'B',
        },
    ]);

    if (experiments.length === 0) {
        return (
            <Card className="p-8 bg-black/30 border-white/10 text-center">
                <FlaskConical className="w-12 h-12 text-gray-600 mx-auto mb-3" />
                <h3 className="text-gray-400 font-medium">No active experiments</h3>
                <p className="text-gray-600 text-sm mt-1">Start an experiment from the templates below</p>
            </Card>
        );
    }

    return (
        <div className="space-y-4">
            {experiments.map((exp) => {
                const progress = exp.current ? ((exp.current - exp.baseline) / (exp.target - exp.baseline)) * 100 : 0;
                const isWon = exp.current && exp.current >= exp.target;

                return (
                    <Card key={exp.id} className={cn(
                        "p-4 border transition-all",
                        exp.status === 'running' ? "bg-[#00f0ff]/5 border-[#00f0ff]/20" :
                            exp.status === 'completed' && isWon ? "bg-green-500/5 border-green-500/20" :
                                "bg-black/50 border-white/10"
                    )}>
                        <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center gap-3">
                                {exp.status === 'running' && <div className="w-2 h-2 rounded-full bg-[#00f0ff] animate-pulse" />}
                                {exp.status === 'completed' && <CheckCircle className={cn("w-4 h-4", isWon ? "text-green-500" : "text-yellow-500")} />}
                                <h4 className="font-bold text-white">{exp.name}</h4>
                            </div>
                            <Badge variant={exp.status === 'running' ? 'cyber' : 'success'} className="uppercase text-xs">
                                {exp.status}
                            </Badge>
                        </div>

                        <p className="text-sm text-gray-400 mb-3">{exp.hypothesis}</p>

                        <div className="grid grid-cols-3 gap-4 mb-3">
                            <div>
                                <div className="text-xs text-gray-500 uppercase">Baseline</div>
                                <div className="text-lg font-mono text-gray-400">{exp.baseline}%</div>
                            </div>
                            <div>
                                <div className="text-xs text-gray-500 uppercase">Current</div>
                                <div className={cn("text-lg font-mono", isWon ? "text-green-500" : "text-[#00f0ff]")}>
                                    {exp.current}%
                                </div>
                            </div>
                            <div>
                                <div className="text-xs text-gray-500 uppercase">Target</div>
                                <div className="text-lg font-mono text-white">{exp.target}%</div>
                            </div>
                        </div>

                        <div className="h-2 bg-black rounded-full overflow-hidden">
                            <div
                                className={cn(
                                    "h-full transition-all duration-500",
                                    isWon ? "bg-green-500" : "bg-[#00f0ff]"
                                )}
                                style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
                            />
                        </div>

                        {exp.winner && (
                            <div className="mt-3 p-2 bg-green-500/10 border border-green-500/20 rounded text-sm text-center">
                                🏆 Variant {exp.winner} wins! {exp.current}% vs {exp.baseline}% baseline
                            </div>
                        )}
                    </Card>
                );
            })}
        </div>
    );
}

// ============ EXPERIMENT BUILDER COMPONENT ============

function ExperimentBuilder({ onClose }: { onClose: () => void }) {
    const [formData, setFormData] = useState({
        name: '',
        hypothesis: '',
        metric: '',
        baseline: '',
        target: '',
    });
    const { toast } = useToast();

    const handleSubmit = () => {
        if (!formData.name || !formData.hypothesis) {
            toast({ type: 'error', title: 'Required Fields', message: 'Please fill in name and hypothesis' });
            return;
        }
        toast({ type: 'success', title: 'Experiment Created!', message: 'Your experiment is now running' });
        onClose();
    };

    return (
        <Card className="p-6 bg-black/50 border-[#00f0ff]/20">
            <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <FlaskConical className="w-5 h-5 text-[#00f0ff]" />
                    Create New Experiment
                </h3>
                <Button variant="ghost" size="sm" onClick={onClose}>Cancel</Button>
            </div>

            <div className="space-y-4">
                <Input
                    label="Experiment Name"
                    placeholder="e.g., Homepage Headline Test"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
                <Textarea
                    label="Hypothesis"
                    placeholder="If we [change], then [metric] will [improve] because [reason]"
                    value={formData.hypothesis}
                    onChange={(e) => setFormData({ ...formData, hypothesis: e.target.value })}
                    className="h-20"
                />
                <div className="grid grid-cols-3 gap-4">
                    <Input
                        label="Metric"
                        placeholder="e.g., Conversion Rate"
                        value={formData.metric}
                        onChange={(e) => setFormData({ ...formData, metric: e.target.value })}
                    />
                    <Input
                        label="Baseline"
                        placeholder="e.g., 2.5%"
                        value={formData.baseline}
                        onChange={(e) => setFormData({ ...formData, baseline: e.target.value })}
                    />
                    <Input
                        label="Target"
                        placeholder="e.g., 5%"
                        value={formData.target}
                        onChange={(e) => setFormData({ ...formData, target: e.target.value })}
                    />
                </div>
                <Button onClick={handleSubmit} variant="cyber" className="w-full">
                    <Play className="w-4 h-4 mr-2" />
                    Start Experiment
                </Button>
            </div>
        </Card>
    );
}

// ============ MAIN COMPONENT ============

export default function ExperimentsLab() {
    const [selectedCategory, setSelectedCategory] = useState('all');
    const [showBuilder, setShowBuilder] = useState(false);
    const { toast } = useToast();

    const filteredTemplates = selectedCategory === 'all'
        ? EXPERIMENT_TEMPLATES
        : EXPERIMENT_TEMPLATES.filter(t => t.category === selectedCategory);

    const handleStartExperiment = (template: ExperimentTemplate) => {
        toast({
            type: 'success',
            title: 'Experiment Started!',
            message: `${template.name} is now active. Track your progress in the dashboard.`
        });
    };

    return (
        <div className="space-y-8 pb-12">
            {/* Header */}
            <div className="border-b border-white/10 pb-6">
                <h1 className="text-3xl font-black text-white tracking-tighter flex items-center gap-3">
                    <FlaskConical className="w-8 h-8 text-[#00f0ff]" />
                    EXPERIMENTS_LAB
                    <Badge variant="cyber" className="text-xs">TEST & ITERATE</Badge>
                </h1>
                <p className="text-gray-500 font-mono text-sm mt-2">
                    Pre-built growth experiments. Launch, measure, iterate.
                </p>
            </div>

            {/* Active Experiments Section */}
            <section>
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-bold text-white flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-[#00f0ff]" />
                        Active Experiments
                    </h2>
                    <Button variant="outline" size="sm" onClick={() => setShowBuilder(true)}>
                        <Sparkles className="w-4 h-4 mr-2" />
                        Create Custom
                    </Button>
                </div>
                {showBuilder ? (
                    <ExperimentBuilder onClose={() => setShowBuilder(false)} />
                ) : (
                    <ActiveExperiments />
                )}
            </section>

            {/* Category Filter */}
            <div className="flex flex-wrap gap-2">
                {CATEGORIES.map((cat) => (
                    <button
                        key={cat.id}
                        onClick={() => setSelectedCategory(cat.id)}
                        className={cn(
                            "px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2",
                            selectedCategory === cat.id
                                ? "bg-[#00f0ff] text-black"
                                : "bg-black/50 text-gray-400 border border-white/10 hover:border-white/30"
                        )}
                    >
                        <span>{cat.icon}</span>
                        {cat.name}
                    </button>
                ))}
            </div>

            {/* Template Grid */}
            <section>
                <h2 className="text-lg font-bold text-white flex items-center gap-2 mb-4">
                    <BookOpen className="w-5 h-5 text-[#00f0ff]" />
                    Experiment Playbooks
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {filteredTemplates.map((template) => (
                        <ExperimentCard
                            key={template.id}
                            template={template}
                            onStart={() => handleStartExperiment(template)}
                        />
                    ))}
                </div>
            </section>
        </div>
    );
}
