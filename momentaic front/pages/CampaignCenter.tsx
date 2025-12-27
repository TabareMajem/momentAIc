import React, { useState } from 'react';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Input } from '../components/ui/Input';
import { Textarea } from '../components/ui/Textarea';
import { useToast } from '../components/ui/Toast';
import { cn } from '../lib/utils';
import {
    Megaphone, Calendar, CheckCircle, Clock, Play, Pause,
    Copy, ChevronRight, Rocket, Mail, MessageSquare, Twitter,
    Linkedin, Globe, PenTool, Share2, Target, Zap, Sparkles,
    ExternalLink, Edit, Trash2, Plus
} from 'lucide-react';

// ============ TYPES ============

interface CampaignTemplate {
    id: string;
    name: string;
    icon: string;
    description: string;
    channel: string;
    duration: string;
    tasks: CampaignTask[];
}

interface CampaignTask {
    day: number;
    title: string;
    description: string;
    template?: string;
    completed?: boolean;
}

interface ActiveCampaign {
    id: string;
    name: string;
    template: string;
    startDate: string;
    progress: number;
    status: 'active' | 'paused' | 'completed';
}

// ============ CAMPAIGN TEMPLATES ============

const CAMPAIGN_TEMPLATES: CampaignTemplate[] = [
    {
        id: 'product-hunt',
        name: 'Product Hunt Launch',
        icon: '🚀',
        description: '7-day campaign to maximize your Product Hunt launch success',
        channel: 'Product Hunt',
        duration: '7 days',
        tasks: [
            { day: -7, title: 'Build Hunter Network', description: 'Connect with 10+ hunters, engage with their posts', template: 'Hey [Name], loved your recent hunt of [Product]. I\'m launching [Your Product] next week and would love your support!' },
            { day: -5, title: 'Prepare Assets', description: 'Create logo, screenshots, GIF walkthrough, and tagline' },
            { day: -3, title: 'Set Up Page', description: 'Create PH listing with compelling copy, add team members' },
            { day: -2, title: 'Tease on Social', description: 'Post teaser on Twitter/LinkedIn about upcoming launch', template: '🚀 Big news dropping in 48 hours...\n\nAfter months of building in stealth, we\'re finally ready to share [Product] with the world.\n\nHint: It\'s going to change how you [benefit].\n\nSet your alarms for [date]. 🎯' },
            { day: -1, title: 'Email Supporters', description: 'Send personal emails to 50+ supporters asking for Day 1 upvotes', template: 'Hey [Name]!\n\nQuick favor - I\'m launching [Product] on Product Hunt tomorrow at 12:01 AM PST.\n\nWould mean the world if you could:\n1. Upvote (link coming at launch)\n2. Leave a comment with your thoughts\n\nWill send you the link first thing tomorrow!\n\nThanks 🙏' },
            { day: 0, title: 'Launch Day AM', description: 'Post at 12:01 AM PST, share on all channels, engage with every comment' },
            { day: 0, title: 'Launch Day PM', description: 'Post updates, thank supporters, respond to all comments within 30 min' },
            { day: 1, title: 'Follow-Up', description: 'Thank everyone who upvoted, share results on social' },
        ],
    },
    {
        id: 'linkedin-launch',
        name: 'LinkedIn Launch Series',
        icon: '💼',
        description: '5-post series to announce your product on LinkedIn',
        channel: 'LinkedIn',
        duration: '5 days',
        tasks: [
            { day: 1, title: 'Founder Story', description: 'Share your journey and why you built this', template: 'I quit my job at [Company] 6 months ago.\n\nEveryone thought I was crazy.\n\nBut I couldn\'t stop thinking about [problem].\n\nToday, I\'m launching [Product].\n\nHere\'s what I learned building it 🧵' },
            { day: 2, title: 'Problem Post', description: 'Deep dive into the problem you\'re solving', template: 'Most [audience] spend [X hours] doing [task].\n\nI know because I was one of them.\n\nHere\'s what nobody tells you about [problem]:\n\n[5 insights]\n\nThat\'s why we built [Product].' },
            { day: 3, title: 'Solution Reveal', description: 'Show your product in action', template: 'Yesterday I showed you the problem.\n\nToday, let me show you the solution.\n\n[Product] helps you [benefit] in [time].\n\nHere\'s how it works:\n\n[3-step breakdown with screenshots]' },
            { day: 4, title: 'Social Proof', description: 'Share early wins and testimonials', template: 'We launched [Product] 3 days ago.\n\nIn those 3 days:\n\n✅ [X] signups\n✅ [X] active users\n✅ [X] [key action]\n\nBut the best part? The feedback:\n\n[3 testimonial quotes]\n\nThis is just the beginning.' },
            { day: 5, title: 'CTA & Offer', description: 'Direct call to action with special offer', template: 'If you made it this far, thank you.\n\nI\'ve shared my journey, the problem, and the solution.\n\nNow it\'s your turn.\n\nFor the next 48 hours, get [offer].\n\nLink in comments. 👇' },
        ],
    },
    {
        id: 'twitter-launch',
        name: 'Twitter Thread Blitz',
        icon: '🐦',
        description: 'Viral Twitter thread campaign for maximum reach',
        channel: 'Twitter',
        duration: '3 days',
        tasks: [
            { day: 1, title: 'Launch Thread', description: 'The big announcement thread', template: 'I spent 6 months building [Product].\n\nToday, it\'s live.\n\nHere\'s everything I learned (and why you should try it) 🧵\n\n[10-12 tweet thread]' },
            { day: 1, title: 'Engage', description: 'Reply to every comment for 2 hours, quote tweet yourself' },
            { day: 2, title: 'Behind the Scenes', description: 'Share the building journey', template: '24 hours since launch:\n\n📊 [X] signups\n💬 [X] comments\n🔥 [X] retweets\n\nBut honestly? The imposter syndrome hit hard.\n\n[Story thread about the journey]' },
            { day: 2, title: 'DM Outreach', description: 'DM 20 relevant accounts asking to try the product' },
            { day: 3, title: 'Results Thread', description: 'Share launch metrics and learnings', template: 'We launched [Product] 72 hours ago.\n\nHere\'s what happened:\n\n📈 Stats that surprised us\n😅 Things that broke\n🎯 What we\'d do differently\n\nFull breakdown 🧵' },
        ],
    },
    {
        id: 'email-sequence',
        name: 'Email Launch Sequence',
        icon: '📧',
        description: '5-email sequence to announce to your list',
        channel: 'Email',
        duration: '14 days',
        tasks: [
            { day: -3, title: 'Teaser Email', description: 'Build anticipation', template: 'Subject: Something big is coming...\n\nHey [Name],\n\nI\'ve been working on something special for the past few months.\n\nCan\'t share all the details yet, but here\'s a hint:\n\n[One sentence teaser]\n\nStay tuned - announcement coming in 3 days.\n\n[Your name]' },
            { day: 0, title: 'Launch Email', description: 'The main announcement', template: 'Subject: It\'s here: [Product] is live 🚀\n\nHey [Name],\n\nThe wait is over.\n\n[Product] is officially live.\n\n[One-liner description]\n\nAs a thank you for being an early supporter, here\'s [special offer].\n\n[CTA Button]\n\nLet me know what you think!\n\n[Your name]' },
            { day: 2, title: 'Social Proof Email', description: 'Share early feedback', template: 'Subject: People are loving [Product]...\n\nHey [Name],\n\n48 hours since launch and the response has been incredible:\n\n[3 testimonial quotes]\n\nIf you haven\'t tried it yet, here\'s what you\'re missing:\n\n[3 key benefits]\n\n[CTA Button]' },
            { day: 5, title: 'Feature Deep-Dive', description: 'Showcase a key feature', template: 'Subject: The feature everyone\'s asking about\n\nHey [Name],\n\nWanted to show you [Feature] - it\'s been the #1 thing people love about [Product].\n\n[Feature explanation with visual]\n\nHere\'s how [specific user] used it to [result].\n\nWant to try it yourself?\n\n[CTA Button]' },
            { day: 10, title: 'Last Chance Email', description: 'Urgency for special offer', template: 'Subject: [Offer] ends tomorrow\n\nHey [Name],\n\nQuick heads up - the [launch offer] expires tomorrow at midnight.\n\nAfter that, [Product] goes back to regular pricing.\n\nIf you\'ve been on the fence, now\'s the time.\n\n[CTA Button]\n\nNo hard feelings if it\'s not for you - but didn\'t want you to miss out.\n\n[Your name]' },
        ],
    },
    {
        id: 'community-launch',
        name: 'Community Launch',
        icon: '👥',
        description: 'Launch through communities (Reddit, Discord, Slack)',
        channel: 'Communities',
        duration: '7 days',
        tasks: [
            { day: -7, title: 'Join Communities', description: 'Find and join 10 relevant communities (Reddit, Discord, Slack)' },
            { day: -5, title: 'Add Value First', description: 'Make 20+ helpful comments/posts without promoting' },
            { day: -2, title: 'Build Relationships', description: 'Connect with community leaders, offer to help' },
            { day: 0, title: 'Soft Launch', description: 'Share in 2-3 communities with genuine ask for feedback', template: 'Hey everyone! 👋\n\nI\'ve been lurking here for a while and learned so much from this community.\n\nI just launched [Product] to help [audience] with [problem].\n\nWould love honest feedback from this group - what do you think?\n\n[Link]\n\nHappy to answer any questions!' },
            { day: 1, title: 'Engage Deeply', description: 'Respond to every comment, thank people, implement feedback' },
            { day: 3, title: 'Case Study Post', description: 'Share results and what you learned from community feedback' },
            { day: 7, title: 'Give Back', description: 'Create valuable resource for community as thank you' },
        ],
    },
];

// ============ CAMPAIGN CARD COMPONENT ============

function CampaignCard({ template, onStart }: { template: CampaignTemplate; onStart: () => void }) {
    const [expanded, setExpanded] = useState(false);
    const { toast } = useToast();

    const copyTemplate = (text: string) => {
        navigator.clipboard.writeText(text);
        toast({ type: 'success', title: 'Copied!', message: 'Template copied to clipboard' });
    };

    return (
        <Card className="p-5 bg-black/50 border-white/10 hover:border-[#00f0ff]/30 transition-all">
            <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                    <span className="text-3xl">{template.icon}</span>
                    <div>
                        <h3 className="font-bold text-white text-lg">{template.name}</h3>
                        <div className="flex items-center gap-2 mt-1">
                            <Badge variant="outline" className="text-xs">{template.channel}</Badge>
                            <span className="text-xs text-gray-500">{template.duration}</span>
                        </div>
                    </div>
                </div>
            </div>

            <p className="text-sm text-gray-400 mb-4">{template.description}</p>

            <button
                onClick={() => setExpanded(!expanded)}
                className="text-sm text-[#00f0ff] flex items-center gap-1 hover:underline mb-3"
            >
                {expanded ? 'Hide' : 'Show'} Campaign Tasks ({template.tasks.length})
                <ChevronRight className={cn("w-4 h-4 transition-transform", expanded && "rotate-90")} />
            </button>

            {expanded && (
                <div className="space-y-3 mb-4 animate-fade-in max-h-[400px] overflow-y-auto">
                    {template.tasks.map((task, i) => (
                        <div key={i} className="bg-black/30 rounded-lg p-3 border border-white/5">
                            <div className="flex items-center justify-between mb-2">
                                <div className="flex items-center gap-2">
                                    <Badge variant={task.day < 0 ? 'warning' : task.day === 0 ? 'cyber' : 'outline'} className="text-xs">
                                        {task.day < 0 ? `D${task.day}` : task.day === 0 ? 'LAUNCH' : `D+${task.day}`}
                                    </Badge>
                                    <span className="font-medium text-white text-sm">{task.title}</span>
                                </div>
                            </div>
                            <p className="text-xs text-gray-400 mb-2">{task.description}</p>
                            {task.template && (
                                <div className="mt-2">
                                    <div className="bg-[#00f0ff]/5 border border-[#00f0ff]/10 rounded p-2 text-xs text-gray-400 max-h-24 overflow-y-auto">
                                        {task.template.substring(0, 150)}...
                                    </div>
                                    <Button
                                        size="sm"
                                        variant="ghost"
                                        className="mt-1 text-xs"
                                        onClick={() => copyTemplate(task.template!)}
                                    >
                                        <Copy className="w-3 h-3 mr-1" />
                                        Copy Template
                                    </Button>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}

            <div className="flex gap-2">
                <Button onClick={onStart} variant="cyber" size="sm" className="flex-1">
                    <Play className="w-3 h-3 mr-2" />
                    Start Campaign
                </Button>
                <Button variant="outline" size="sm">
                    <Calendar className="w-3 h-3 mr-2" />
                    Schedule
                </Button>
            </div>
        </Card>
    );
}

// ============ ACTIVE CAMPAIGNS COMPONENT ============

function ActiveCampaigns() {
    const [campaigns] = useState<ActiveCampaign[]>([
        {
            id: '1',
            name: 'Product Hunt Launch',
            template: 'product-hunt',
            startDate: '2024-12-20',
            progress: 62,
            status: 'active',
        },
    ]);

    if (campaigns.length === 0) {
        return (
            <Card className="p-8 bg-black/30 border-white/10 text-center">
                <Calendar className="w-12 h-12 text-gray-600 mx-auto mb-3" />
                <h3 className="text-gray-400 font-medium">No active campaigns</h3>
                <p className="text-gray-600 text-sm mt-1">Start a campaign from the templates below</p>
            </Card>
        );
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {campaigns.map((campaign) => (
                <Card key={campaign.id} className="p-4 bg-[#00f0ff]/5 border-[#00f0ff]/20">
                    <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full bg-[#00f0ff] animate-pulse" />
                            <h4 className="font-bold text-white">{campaign.name}</h4>
                        </div>
                        <Badge variant="cyber" className="uppercase text-xs">
                            {campaign.status}
                        </Badge>
                    </div>

                    <div className="mb-3">
                        <div className="flex items-center justify-between text-xs mb-1">
                            <span className="text-gray-400">Progress</span>
                            <span className="text-[#00f0ff]">{campaign.progress}%</span>
                        </div>
                        <div className="h-2 bg-black rounded-full overflow-hidden">
                            <div
                                className="h-full bg-[#00f0ff] transition-all duration-500"
                                style={{ width: `${campaign.progress}%` }}
                            />
                        </div>
                    </div>

                    <div className="flex gap-2">
                        <Button variant="outline" size="sm" className="flex-1">
                            <Pause className="w-3 h-3 mr-1" />
                            Pause
                        </Button>
                        <Button variant="outline" size="sm" className="flex-1">
                            View Details
                        </Button>
                    </div>
                </Card>
            ))}
        </div>
    );
}

// ============ QUICK COPY TEMPLATES COMPONENT ============

function QuickCopyTemplates() {
    const { toast } = useToast();

    const quickTemplates = [
        {
            name: 'Launch Tweet',
            icon: '🐦',
            text: "🚀 It's finally here!\n\nAfter [X months] of building, I'm excited to announce [Product].\n\n[One-liner description]\n\nCheck it out: [Link]\n\nWould love your feedback! 🙏",
        },
        {
            name: 'LinkedIn Announcement',
            icon: '💼',
            text: "I have some exciting news to share!\n\nToday, I'm launching [Product].\n\nFor the past [X months], I've been obsessed with solving [problem].\n\nHere's why this matters:\n\n• [Benefit 1]\n• [Benefit 2]\n• [Benefit 3]\n\nIf you're a [target audience], I'd love for you to try it.\n\nLink in comments 👇",
        },
        {
            name: 'Email Subject Lines',
            icon: '📧',
            text: "Option 1: It's here! [Product] is live 🚀\nOption 2: Something new for you...\nOption 3: I made this for you\nOption 4: [X hours] to launch\nOption 5: You asked, I built it",
        },
        {
            name: 'Press Pitch',
            icon: '📰',
            text: "Subject: [Startup Name] launches [Product] to help [audience] [achieve outcome]\n\nHi [Name],\n\n[One sentence hook]\n\n[Startup Name] is launching [Product], a [category] that helps [target audience] [key benefit].\n\nKey facts:\n• [Unique angle]\n• [Impressive stat or traction]\n• [Team credibility]\n\nWould love to share more details for a potential story.\n\nBest,\n[Your name]",
        },
    ];

    const copyText = (text: string, name: string) => {
        navigator.clipboard.writeText(text);
        toast({ type: 'success', title: 'Copied!', message: `${name} template copied` });
    };

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {quickTemplates.map((template) => (
                <Card key={template.name} className="p-4 bg-black/50 border-white/10">
                    <div className="flex items-center gap-2 mb-3">
                        <span className="text-xl">{template.icon}</span>
                        <h4 className="font-bold text-white text-sm">{template.name}</h4>
                    </div>
                    <p className="text-xs text-gray-500 line-clamp-3 mb-3">{template.text}</p>
                    <Button
                        onClick={() => copyText(template.text, template.name)}
                        variant="outline"
                        size="sm"
                        className="w-full"
                    >
                        <Copy className="w-3 h-3 mr-2" />
                        Copy
                    </Button>
                </Card>
            ))}
        </div>
    );
}

// ============ MAIN COMPONENT ============

export default function CampaignCenter() {
    const { toast } = useToast();

    const handleStartCampaign = (template: CampaignTemplate) => {
        toast({
            type: 'success',
            title: 'Campaign Started!',
            message: `${template.name} is now active. Check your dashboard for daily tasks.`
        });
    };

    return (
        <div className="space-y-8 pb-12">
            {/* Header */}
            <div className="border-b border-white/10 pb-6">
                <h1 className="text-3xl font-black text-white tracking-tighter flex items-center gap-3">
                    <Megaphone className="w-8 h-8 text-[#00f0ff]" />
                    CAMPAIGN_CENTER
                    <Badge variant="cyber" className="text-xs">LAUNCH PLAYBOOKS</Badge>
                </h1>
                <p className="text-gray-500 font-mono text-sm mt-2">
                    Ready-to-launch campaign templates. Copy, customize, execute.
                </p>
            </div>

            {/* Active Campaigns */}
            <section>
                <h2 className="text-lg font-bold text-white flex items-center gap-2 mb-4">
                    <Zap className="w-5 h-5 text-[#00f0ff]" />
                    Active Campaigns
                </h2>
                <ActiveCampaigns />
            </section>

            {/* Quick Copy Templates */}
            <section>
                <h2 className="text-lg font-bold text-white flex items-center gap-2 mb-4">
                    <Copy className="w-5 h-5 text-[#00f0ff]" />
                    Quick Copy Templates
                </h2>
                <QuickCopyTemplates />
            </section>

            {/* Campaign Templates */}
            <section>
                <h2 className="text-lg font-bold text-white flex items-center gap-2 mb-4">
                    <Target className="w-5 h-5 text-[#00f0ff]" />
                    Launch Playbooks
                </h2>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {CAMPAIGN_TEMPLATES.map((template) => (
                        <CampaignCard
                            key={template.id}
                            template={template}
                            onStart={() => handleStartCampaign(template)}
                        />
                    ))}
                </div>
            </section>
        </div>
    );
}
