import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Input } from '../components/ui/Input';
import { Textarea } from '../components/ui/Textarea';
import { useToast } from '../components/ui/Toast';
import { useAuthStore } from '../stores/auth-store';
import { api } from '../lib/api';
import { cn } from '../lib/utils';
import {
    Users, DollarSign, TrendingUp, Copy, Share2, ExternalLink,
    CreditCard, CheckCircle, Clock, AlertCircle, ArrowUpRight,
    Twitter, Linkedin, Mail, Zap, Gift, Crown, Target, BarChart2,
    Wallet, RefreshCw, ChevronRight, Image as ImageIcon, Sparkles
} from 'lucide-react';

// ============ TYPES ============

interface AmbassadorProfile {
    id: string;
    display_name: string;
    tier: 'micro' | 'mid' | 'macro';
    commission_rate: number;
    referral_code: string;
    referral_url: string;
    stripe_connected: boolean;
    stripe_payouts_enabled: boolean;
    total_clicks: number;
    total_signups: number;
    total_conversions: number;
    conversion_rate: number;
    total_earnings: number;
    pending_balance: number;
    available_balance: number;
    total_paid_out: number;
    status: string;
}

interface Conversion {
    id: string;
    referred_user_email: string;
    subscription_plan: string;
    subscription_amount: number;
    commission_amount: number;
    status: 'pending' | 'cleared' | 'paid' | 'refunded';
    created_at: string;
}

// ============ TIER CONFIG ============

const TIER_CONFIG = {
    micro: { name: 'Micro', rate: '20%', icon: '🌱', color: 'from-green-500/20 to-green-600/20', followers: '<10k' },
    mid: { name: 'Rising Star', rate: '25%', icon: '⭐', color: 'from-yellow-500/20 to-yellow-600/20', followers: '10k-100k' },
    macro: { name: 'Macro', rate: '30%', icon: '🚀', color: 'from-purple-500/20 to-purple-600/20', followers: '>100k' },
};

// ============ STAT CARD COMPONENT ============

function StatCard({ label, value, icon: Icon, color, trend }: {
    label: string;
    value: string | number;
    icon: React.ElementType;
    color: string;
    trend?: number;
}) {
    return (
        <Card className={cn("p-4 bg-gradient-to-br border", color)}>
            <div className="flex items-center justify-between mb-2">
                <Icon className="w-5 h-5 text-white/70" />
                {trend !== undefined && (
                    <div className={cn("flex items-center text-xs", trend >= 0 ? "text-green-500" : "text-red-500")}>
                        <ArrowUpRight className={cn("w-3 h-3", trend < 0 && "rotate-180")} />
                        {Math.abs(trend)}%
                    </div>
                )}
            </div>
            <div className="text-2xl font-black text-white">{value}</div>
            <div className="text-xs text-gray-400 uppercase tracking-wider mt-1">{label}</div>
        </Card>
    );
}

// ============ CONVERSION TABLE COMPONENT ============

function ConversionTable({ conversions }: { conversions: Conversion[] }) {
    const getStatusBadge = (status: string) => {
        const variants: Record<string, 'warning' | 'success' | 'cyber' | 'destructive'> = {
            pending: 'warning',
            cleared: 'success',
            paid: 'cyber',
            refunded: 'destructive',
        };
        return <Badge variant={variants[status] || 'outline'} className="text-xs uppercase">{status}</Badge>;
    };

    return (
        <div className="overflow-x-auto">
            <table className="w-full">
                <thead>
                    <tr className="border-b border-white/10">
                        <th className="text-left py-3 px-4 text-xs text-gray-500 uppercase">User</th>
                        <th className="text-left py-3 px-4 text-xs text-gray-500 uppercase">Plan</th>
                        <th className="text-right py-3 px-4 text-xs text-gray-500 uppercase">Amount</th>
                        <th className="text-right py-3 px-4 text-xs text-gray-500 uppercase">Commission</th>
                        <th className="text-center py-3 px-4 text-xs text-gray-500 uppercase">Status</th>
                        <th className="text-right py-3 px-4 text-xs text-gray-500 uppercase">Date</th>
                    </tr>
                </thead>
                <tbody>
                    {conversions.map((c) => (
                        <tr key={c.id} className="border-b border-white/5 hover:bg-white/5">
                            <td className="py-3 px-4 text-sm text-gray-300">{c.referred_user_email}</td>
                            <td className="py-3 px-4">
                                <Badge variant="outline" className="text-xs capitalize">{c.subscription_plan}</Badge>
                            </td>
                            <td className="py-3 px-4 text-right text-sm text-white">${c.subscription_amount.toFixed(2)}</td>
                            <td className="py-3 px-4 text-right text-sm text-[#00f0ff] font-mono">${c.commission_amount.toFixed(2)}</td>
                            <td className="py-3 px-4 text-center">{getStatusBadge(c.status)}</td>
                            <td className="py-3 px-4 text-right text-sm text-gray-500">
                                {new Date(c.created_at).toLocaleDateString()}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

// ============ STRIPE CONNECT SECTION ============

function StripeConnectSection({ profile, onConnect }: {
    profile: AmbassadorProfile;
    onConnect: () => void;
}) {
    if (profile.stripe_connected && profile.stripe_payouts_enabled) {
        return (
            <Card className="p-4 bg-green-500/10 border-green-500/20">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center">
                        <CheckCircle className="w-5 h-5 text-green-500" />
                    </div>
                    <div className="flex-1">
                        <div className="text-white font-medium">Stripe Connected</div>
                        <div className="text-xs text-gray-400">Payouts enabled • Funds will be deposited to your bank</div>
                    </div>
                    <Button variant="outline" size="sm">
                        <ExternalLink className="w-3 h-3 mr-2" />
                        Dashboard
                    </Button>
                </div>
            </Card>
        );
    }

    return (
        <Card className="p-6 bg-gradient-to-br from-[#00f0ff]/5 to-transparent border-[#00f0ff]/20">
            <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-xl bg-[#00f0ff]/10 flex items-center justify-center">
                    <CreditCard className="w-6 h-6 text-[#00f0ff]" />
                </div>
                <div className="flex-1">
                    <h3 className="text-lg font-bold text-white mb-1">Connect Your Bank</h3>
                    <p className="text-sm text-gray-400 mb-4">
                        Link your Stripe account to receive instant payouts. Takes less than 2 minutes.
                    </p>
                    <Button onClick={onConnect} variant="cyber">
                        <Zap className="w-4 h-4 mr-2" />
                        Connect with Stripe
                    </Button>
                </div>
            </div>
        </Card>
    );
}

// ============ SWIPE FILE GALLERY ============

function SwipeFileGallery() {
    const { toast } = useToast();

    const swipeFiles = [
        {
            title: "The Weapon Setup (TikTok Hook)",
            imageUrl: "https://images.unsplash.com/photo-1614729939124-032f0b5610ce?auto=format&fit=crop&q=80&w=800",
            prompt: "Bro is still using a browser automation tool in 2026 💀 I just deployed a live Autonomic Board of Directors on MomentAIc that runs my entire growth engine while I sleep. Link in bio to access the Arsenal. #AI #SaaS #MomentAIc"
        },
        {
            title: "50% MRR Flex (X / Twitter)",
            imageUrl: "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&q=80&w=800",
            prompt: "Open Claw gives you 10%. MomentAIc gives you 50% recurring. I made $14k this week just getting my agency clients onto the platform. Stop selling tools and start deploying weapons. 👇 [Your Link]"
        },
        {
            title: "System Override (Instagram Reel)",
            imageUrl: "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&q=80&w=800",
            prompt: "POV: You hit 'Deploy Swarm' and watch 50 AI agents completely hijack your competitor's SEO strategy in real-time. 🚨 System Override. #MomentAIc"
        }
    ];

    const copyPrompt = (text: string) => {
        navigator.clipboard.writeText(text);
        toast({ type: 'success', title: 'Copied!', message: 'Swipe file text copied to clipboard!' });
    };

    return (
        <Card className="p-6 bg-black/50 border-white/10 mt-6">
            <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <ImageIcon className="w-5 h-5 text-[#00f0ff]" />
                Viral Assets & Swipe Files
            </h2>
            <p className="text-sm text-gray-400 mb-6">
                Post these high-converting assets on your socials. We've written the hooks for you.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {swipeFiles.map((file, i) => (
                    <div key={i} className="border border-white/5 bg-white/5 rounded-lg overflow-hidden flex flex-col">
                        <div className="h-32 bg-gray-900 border-b border-white/5 relative overflow-hidden group">
                            {/* Using dynamic blurred styling for the mockup images */}
                            <div className="absolute inset-0 bg-gradient-to-br from-purple-500/20 to-cyan-500/20" />
                            <img src={file.imageUrl} alt={file.title} className="w-full h-full object-cover opacity-60 mix-blend-overlay group-hover:scale-105 transition-transform duration-500" />
                            <div className="absolute inset-0 flex items-center justify-center">
                                <Badge variant="cyber" className="opacity-0 group-hover:opacity-100 transition-opacity">Download</Badge>
                            </div>
                        </div>
                        <div className="p-4 flex-1 flex flex-col">
                            <h3 className="text-[#00f0ff] font-bold text-sm mb-2">{file.title}</h3>
                            <p className="text-xs text-gray-400 mb-4 line-clamp-3 italic flex-1">"{file.prompt}"</p>
                            <Button variant="outline" size="sm" onClick={() => copyPrompt(file.prompt)} className="w-full">
                                <Copy className="w-3 h-3 mr-2" /> Copy Caption
                            </Button>
                        </div>
                    </div>
                ))}
            </div>
        </Card>
    );
}

// ============ APPLICATION FORM ============

function ApplicationForm({ onSubmit }: { onSubmit: (data: any) => void }) {
    const [formData, setFormData] = useState({
        display_name: '',
        social_platform: 'twitter',
        social_username: '',
        social_url: '',
        follower_count: '',
        application_reason: '',
        promotion_plan: '',
    });
    const [submitting, setSubmitting] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSubmitting(true);
        try {
            const submissionData = {
                ...formData,
                follower_count: parseInt(formData.follower_count, 10) || 0
            };
            await onSubmit(submissionData);
        } finally {
            setSubmitting(false);
        }
    };

    const platforms = [
        { value: 'twitter', label: 'Twitter/X' },
        { value: 'linkedin', label: 'LinkedIn' },
        { value: 'instagram', label: 'Instagram' },
        { value: 'youtube', label: 'YouTube' },
        { value: 'tiktok', label: 'TikTok' },
    ];

    return (
        <Card className="p-6 bg-black/50 border-white/10">
            <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                <Users className="w-5 h-5 text-[#00f0ff]" />
                Apply to Become an Ambassador
            </h2>

            <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Input
                        label="Display Name"
                        placeholder="How should we call you?"
                        value={formData.display_name}
                        onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
                        required
                    />
                    <div>
                        <label className="block text-sm font-medium text-gray-400 mb-2">Platform</label>
                        <select
                            value={formData.social_platform}
                            onChange={(e) => setFormData({ ...formData, social_platform: e.target.value })}
                            className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-2 text-white"
                        >
                            {platforms.map(p => (
                                <option key={p.value} value={p.value}>{p.label}</option>
                            ))}
                        </select>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Input
                        label="Username"
                        placeholder="@yourhandle"
                        value={formData.social_username}
                        onChange={(e) => setFormData({ ...formData, social_username: e.target.value })}
                        required
                    />
                    <Input
                        label="Follower Count"
                        type="number"
                        placeholder="e.g., 5000"
                        value={formData.follower_count}
                        onChange={(e) => setFormData({ ...formData, follower_count: e.target.value })}
                        required
                    />
                </div>

                <Input
                    label="Profile URL"
                    placeholder="https://twitter.com/yourhandle"
                    value={formData.social_url}
                    onChange={(e) => setFormData({ ...formData, social_url: e.target.value })}
                />

                <Textarea
                    label="Why do you want to be an ambassador?"
                    placeholder="Tell us about yourself and your audience..."
                    value={formData.application_reason}
                    onChange={(e) => setFormData({ ...formData, application_reason: e.target.value })}
                    className="h-24"
                    required
                />

                <Textarea
                    label="How will you promote MomentAIc?"
                    placeholder="Your promotion strategy..."
                    value={formData.promotion_plan}
                    onChange={(e) => setFormData({ ...formData, promotion_plan: e.target.value })}
                    className="h-20"
                />

                <Button type="submit" variant="cyber" className="w-full" isLoading={submitting}>
                    <Gift className="w-4 h-4 mr-2" />
                    Submit Application
                </Button>
            </form>
        </Card>
    );
}

// ============ MAIN COMPONENT ============

import { CampaignControlModal } from '../components/ui/CampaignControlModal';

export default function AmbassadorDashboard() {
    const { user } = useAuthStore();
    const [profile, setProfile] = useState<AmbassadorProfile | null>(null);
    const [conversions, setConversions] = useState<Conversion[]>([]);
    const [loading, setLoading] = useState(true);
    const [copied, setCopied] = useState(false);
    const [requestingPayout, setRequestingPayout] = useState(false);
    const [isCampaignModalOpen, setIsCampaignModalOpen] = useState(false);
    const { toast } = useToast();

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const [profileData, conversionsData] = await Promise.all([
                api.getAmbassadorProfile(),
                api.getAmbassadorConversions(),
            ]);

            setProfile(profileData as any); // Cast for tier string/enum compatibility
            setConversions(conversionsData.conversions);
        } catch (error: any) {
            // If 404, it means user is not an ambassador yet - strict check needed
            if (error.response?.status === 404) {
                setProfile(null);
            } else {
                console.error('Failed to load ambassador data', error);
                toast({ type: 'error', title: 'Error', message: 'Failed to load ambassador data' });
            }
        } finally {
            setLoading(false);
        }
    };

    const copyLink = () => {
        if (profile) {
            navigator.clipboard.writeText(profile.referral_url);
            setCopied(true);
            toast({ type: 'success', title: 'Copied!', message: 'Referral link copied to clipboard' });
            setTimeout(() => setCopied(false), 2000);
        }
    };

    const handlePayout = async () => {
        if (!profile || profile.available_balance < 25) {
            toast({ type: 'error', title: 'Minimum $25', message: 'Minimum payout is $25' });
            return;
        }
        setRequestingPayout(true);
        try {
            const result = await api.requestPayout();
            toast({ type: 'success', title: 'Payout Sent!', message: `$${result.amount.toFixed(2)} sent to your bank.` });
            // Reload data to update balance
            loadData();
        } catch (error: any) {
            toast({ type: 'error', title: 'Payout Failed', message: error.response?.data?.detail || 'Failed to process payout' });
        } finally {
            setRequestingPayout(false);
        }
    };

    const handleStripeConnect = async () => {
        try {
            const { onboarding_url, dashboard_url } = await api.stripeOnboard();
            // API returns onboarding_url or dashboard_url depending on state
            if (onboarding_url) {
                window.location.href = onboarding_url;
            } else if (dashboard_url) {
                window.open(dashboard_url, '_blank');
            }
        } catch (error) {
            toast({ type: 'error', title: 'Error', message: 'Failed to initiate Stripe Connect' });
        }
    };

    const handleApplication = async (data: any) => {
        try {
            await api.applyAmbassador(data);
            toast({ type: 'success', title: 'Application Submitted!', message: 'We\'ll review and get back to you within 24 hours.' });
            // Reload to show pending status
            loadData();
        } catch (error: any) {
            toast({ type: 'error', title: 'Error', message: error.response?.data?.detail || 'Application failed' });
        }
    };

    const isSuperAdmin = user?.email === 'tabaremajem@gmail.com';

    if (loading) {
        return (
            <div className="flex items-center justify-center h-[60vh]">
                <div className="text-[#00f0ff] font-mono animate-pulse">LOADING_AMBASSADOR_DATA...</div>
            </div>
        );
    }

    // If not an ambassador yet, show application form
    if (!profile) {
        return (
            <div className="space-y-8 pb-12 max-w-2xl mx-auto">
                <div className="border-b border-white/10 pb-6 flex justify-between items-start">
                    <div>
                        <h1 className="text-3xl font-black text-white tracking-tighter flex items-center gap-3">
                            <Crown className="w-8 h-8 text-[#00f0ff]" />
                            AMBASSADOR_PROGRAM
                            <Badge variant="cyber" className="text-xs">EARN 20-30%</Badge>
                        </h1>
                        <p className="text-gray-500 font-mono text-sm mt-2">
                            Share MomentAIc with your audience. Earn commissions on every conversion.
                        </p>
                    </div>
                    {isSuperAdmin && (
                        <Button variant="cyber" onClick={() => setIsCampaignModalOpen(true)}>
                            <Sparkles className="w-4 h-4 mr-2" />
                            Launch Matrix Console
                        </Button>
                    )}
                </div>
                <ApplicationForm onSubmit={handleApplication} />
                <CampaignControlModal isOpen={isCampaignModalOpen} onClose={() => setIsCampaignModalOpen(false)} />
            </div>
        );
    }

    const tierConfig = TIER_CONFIG[profile.tier];

    return (
        <div className="space-y-8 pb-12">
            {/* Header */}
            <div className="border-b border-white/10 pb-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-black text-white tracking-tighter flex items-center gap-3">
                            <Crown className="w-8 h-8 text-[#00f0ff]" />
                            AMBASSADOR_HQ
                            <Badge variant="cyber" className="text-xs">{tierConfig.icon} {tierConfig.name.toUpperCase()}</Badge>
                        </h1>
                        <p className="text-gray-500 font-mono text-sm mt-2">
                            Welcome back, {profile.display_name}! You're earning <span className="text-[#00f0ff]">{tierConfig.rate}</span> commission.
                        </p>
                    </div>
                    <div className="flex items-center gap-4">
                        {isSuperAdmin && (
                            <Button variant="cyber" onClick={() => setIsCampaignModalOpen(true)} className="glow glow-purple shadow-none">
                                <Sparkles className="w-4 h-4 mr-2" />
                                Launch Matrix Console
                            </Button>
                        )}
                        <Badge
                            variant={profile.status === 'active' ? 'success' : 'warning'}
                            className="uppercase text-xs"
                        >
                            {profile.status}
                        </Badge>
                    </div>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard
                    label="Total Earnings"
                    value={`$${profile.total_earnings.toFixed(2)}`}
                    icon={DollarSign}
                    color="from-green-500/20 to-green-600/10 border-green-500/20"
                    trend={15}
                />
                <StatCard
                    label="Available"
                    value={`$${profile.available_balance.toFixed(2)}`}
                    icon={Wallet}
                    color="from-[#00f0ff]/20 to-[#00f0ff]/5 border-[#00f0ff]/20"
                />
                <StatCard
                    label="Conversions"
                    value={profile.total_conversions}
                    icon={Target}
                    color="from-purple-500/20 to-purple-600/10 border-purple-500/20"
                />
                <StatCard
                    label="Conversion Rate"
                    value={`${profile.conversion_rate}%`}
                    icon={BarChart2}
                    color="from-orange-500/20 to-orange-600/10 border-orange-500/20"
                />
            </div>

            {/* Main Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left Column */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Referral Link */}
                    <Card className="p-6 bg-gradient-to-br from-[#00f0ff]/5 to-transparent border-[#00f0ff]/20">
                        <div className="flex items-center gap-2 mb-4">
                            <Share2 className="w-5 h-5 text-[#00f0ff]" />
                            <h2 className="text-lg font-bold text-white">Your Referral Link</h2>
                        </div>

                        <div className="flex gap-2 mb-4">
                            <div className="flex-1 bg-black/50 border border-white/10 rounded-lg px-4 py-3 font-mono text-sm text-[#00f0ff] truncate">
                                {profile.referral_url}
                            </div>
                            <Button onClick={copyLink} variant={copied ? 'cyber' : 'outline'}>
                                <Copy className="w-4 h-4 mr-2" />
                                {copied ? 'Copied!' : 'Copy'}
                            </Button>
                        </div>

                        <div className="grid grid-cols-4 gap-2">
                            <Button variant="outline" size="sm" className="flex-col h-auto py-3">
                                <Twitter className="w-4 h-4 mb-1" />
                                <span className="text-xs">Twitter</span>
                            </Button>
                            <Button variant="outline" size="sm" className="flex-col h-auto py-3">
                                <Linkedin className="w-4 h-4 mb-1" />
                                <span className="text-xs">LinkedIn</span>
                            </Button>
                            <Button variant="outline" size="sm" className="flex-col h-auto py-3">
                                <Mail className="w-4 h-4 mb-1" />
                                <span className="text-xs">Email</span>
                            </Button>
                            <Button variant="outline" size="sm" className="flex-col h-auto py-3">
                                <ExternalLink className="w-4 h-4 mb-1" />
                                <span className="text-xs">More</span>
                            </Button>
                        </div>
                    </Card>

                    {/* Stripe Connect */}
                    <StripeConnectSection profile={profile} onConnect={handleStripeConnect} />

                    {/* Conversions Table */}
                    <Card className="p-6 bg-black/50 border-white/10">
                        <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                            <TrendingUp className="w-5 h-5 text-[#00f0ff]" />
                            Recent Conversions
                        </h2>
                        <ConversionTable conversions={conversions} />
                    </Card>

                    {/* Viral Assets Hub */}
                    <SwipeFileGallery />
                </div>

                {/* Right Column */}
                <div className="space-y-6">
                    {/* Earnings Breakdown */}
                    <Card className="p-6 bg-black/50 border-white/10">
                        <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                            <DollarSign className="w-5 h-5 text-[#00f0ff]" />
                            Earnings
                        </h2>

                        <div className="space-y-4">
                            <div className="flex items-center justify-between py-2 border-b border-white/5">
                                <span className="text-gray-400">Total Earned</span>
                                <span className="text-white font-mono">${profile.total_earnings.toFixed(2)}</span>
                            </div>
                            <div className="flex items-center justify-between py-2 border-b border-white/5">
                                <div className="flex items-center gap-2">
                                    <span className="text-gray-400">Available</span>
                                    <Badge variant="success" className="text-xs">70%</Badge>
                                </div>
                                <span className="text-green-500 font-mono">${profile.available_balance.toFixed(2)}</span>
                            </div>
                            <div className="flex items-center justify-between py-2 border-b border-white/5">
                                <div className="flex items-center gap-2">
                                    <span className="text-gray-400">Pending</span>
                                    <Badge variant="warning" className="text-xs">30-day hold</Badge>
                                </div>
                                <span className="text-yellow-500 font-mono">${profile.pending_balance.toFixed(2)}</span>
                            </div>
                            <div className="flex items-center justify-between py-2">
                                <span className="text-gray-400">Paid Out</span>
                                <span className="text-[#00f0ff] font-mono">${profile.total_paid_out.toFixed(2)}</span>
                            </div>
                        </div>

                        <Button
                            onClick={handlePayout}
                            variant="cyber"
                            className="w-full mt-4"
                            disabled={profile.available_balance < 25}
                            isLoading={requestingPayout}
                        >
                            <Wallet className="w-4 h-4 mr-2" />
                            Request Payout
                        </Button>
                        {profile.available_balance < 25 && (
                            <p className="text-xs text-gray-500 text-center mt-2">
                                Minimum payout: $25
                            </p>
                        )}
                    </Card>

                    {/* Traffic Stats */}
                    <Card className="p-6 bg-black/50 border-white/10">
                        <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                            <BarChart2 className="w-5 h-5 text-[#00f0ff]" />
                            Traffic
                        </h2>

                        <div className="space-y-4">
                            <div className="flex items-center justify-between">
                                <span className="text-gray-400">Link Clicks</span>
                                <span className="text-white font-mono">{profile.total_clicks}</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="text-gray-400">Signups</span>
                                <span className="text-white font-mono">{profile.total_signups}</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="text-gray-400">Paid Conversions</span>
                                <span className="text-[#00f0ff] font-mono">{profile.total_conversions}</span>
                            </div>
                        </div>
                    </Card>

                    {/* Tier Progress */}
                    <Card className={cn("p-6 border bg-gradient-to-br", tierConfig.color)}>
                        <div className="flex items-center gap-3 mb-3">
                            <span className="text-3xl">{tierConfig.icon}</span>
                            <div>
                                <div className="text-white font-bold">{tierConfig.name} Tier</div>
                                <div className="text-xs text-gray-400">{tierConfig.followers} followers</div>
                            </div>
                        </div>
                        <div className="flex items-center justify-between">
                            <span className="text-gray-400 text-sm">Commission Rate</span>
                            <span className="text-2xl font-black text-white">{tierConfig.rate}</span>
                        </div>
                    </Card>
                </div>
            </div>

            <CampaignControlModal isOpen={isCampaignModalOpen} onClose={() => setIsCampaignModalOpen(false)} />
        </div>
    );
}
