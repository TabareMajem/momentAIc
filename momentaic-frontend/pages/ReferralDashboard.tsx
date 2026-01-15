import React, { useState, useEffect } from 'react';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { useToast } from '../components/ui/Toast';
import { useAuthStore } from '../stores/auth-store';
import { api } from '../lib/api';
import { cn } from '../lib/utils';
import {
    Gift, Users, Trophy, Copy, Share2, Twitter, Linkedin,
    Mail, MessageCircle, Zap, Target, TrendingUp, Award,
    ChevronRight, Sparkles, Crown
} from 'lucide-react';

// ============ TYPES ============

interface ReferralStats {
    total_referrals: number;
    successful_signups: number;
    converted_users: number;
    total_credits_earned: number;
    current_streak: number;
    rank: number;
    next_milestone: {
        name: string;
        required: number;
        current: number;
        reward_credits: number;
        progress_percent: number;
    };
    milestones_achieved: string[];
}

interface ReferralLink {
    referral_code: string;
    referral_url: string;
    share_message: string;
    share_templates: {
        twitter: string;
        linkedin: string;
        email_subject: string;
        email_body: string;
        whatsapp: string;
    };
}

interface LeaderboardEntry {
    rank: number;
    username: string;
    referral_count: number;
    avatar_url?: string;
}

// ============ MILESTONES CONFIG ============

const MILESTONES = [
    { count: 5, name: 'Starter', reward: 250, badge: '🌱', color: 'from-green-500/20 to-green-600/20' },
    { count: 10, name: 'Rising Star', reward: 500, badge: '⭐', color: 'from-yellow-500/20 to-yellow-600/20' },
    { count: 25, name: 'Growth Master', reward: 1000, badge: '🚀', color: 'from-blue-500/20 to-blue-600/20' },
    { count: 50, name: 'Viral Legend', reward: 2500, badge: '🔥', color: 'from-orange-500/20 to-orange-600/20' },
    { count: 100, name: 'Unicorn Hunter', reward: 5000, badge: '🦄', color: 'from-purple-500/20 to-purple-600/20' },
];

// ============ SHARE BUTTON COMPONENT ============

function ShareButton({
    icon: Icon,
    label,
    onClick,
    color
}: {
    icon: React.ElementType;
    label: string;
    onClick: () => void;
    color: string;
}) {
    return (
        <button
            onClick={onClick}
            className={cn(
                "flex flex-col items-center gap-2 p-4 rounded-xl border border-white/10",
                "hover:scale-105 transition-all duration-200",
                "bg-gradient-to-br", color
            )}
        >
            <Icon className="w-6 h-6" />
            <span className="text-xs font-mono uppercase tracking-wider">{label}</span>
        </button>
    );
}

// ============ MILESTONE CARD COMPONENT ============

function MilestoneCard({
    milestone,
    achieved,
    current
}: {
    milestone: typeof MILESTONES[0];
    achieved: boolean;
    current: number;
}) {
    const progress = Math.min(100, (current / milestone.count) * 100);

    return (
        <div className={cn(
            "relative p-4 rounded-xl border transition-all",
            achieved
                ? "border-[#00f0ff]/50 bg-[#00f0ff]/5"
                : "border-white/10 bg-black/50"
        )}>
            {achieved && (
                <div className="absolute -top-2 -right-2 bg-[#00f0ff] text-black text-xs px-2 py-0.5 rounded-full font-bold">
                    UNLOCKED
                </div>
            )}

            <div className="flex items-center gap-3 mb-3">
                <span className="text-2xl">{milestone.badge}</span>
                <div>
                    <div className="font-bold text-white">{milestone.name}</div>
                    <div className="text-xs text-gray-500">{milestone.count} referrals</div>
                </div>
            </div>

            <div className="flex items-center justify-between text-xs mb-2">
                <span className="text-gray-400">Progress</span>
                <span className="text-[#00f0ff] font-mono">{current}/{milestone.count}</span>
            </div>

            <div className="h-2 bg-black rounded-full overflow-hidden">
                <div
                    className="h-full bg-gradient-to-r from-[#00f0ff] to-[#00f0ff]/50 transition-all duration-500"
                    style={{ width: `${progress}%` }}
                />
            </div>

            <div className="mt-3 flex items-center justify-between">
                <div className="flex items-center gap-1 text-xs text-gray-400">
                    <Gift className="w-3 h-3" />
                    <span>{milestone.reward} credits</span>
                </div>
                {achieved && (
                    <Badge variant="success" className="text-xs">Claimed</Badge>
                )}
            </div>
        </div>
    );
}

// ============ LEADERBOARD COMPONENT ============

function Leaderboard({ entries }: { entries: LeaderboardEntry[] }) {
    return (
        <div className="space-y-2">
            {entries.map((entry, idx) => (
                <div
                    key={entry.rank}
                    className={cn(
                        "flex items-center gap-3 p-3 rounded-lg",
                        idx < 3 ? "bg-gradient-to-r from-[#00f0ff]/10 to-transparent border border-[#00f0ff]/20" : "bg-black/30"
                    )}
                >
                    <div className={cn(
                        "w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm",
                        idx === 0 ? "bg-yellow-500/20 text-yellow-500" :
                            idx === 1 ? "bg-gray-400/20 text-gray-400" :
                                idx === 2 ? "bg-orange-600/20 text-orange-500" :
                                    "bg-white/5 text-gray-500"
                    )}>
                        {idx === 0 ? <Crown className="w-4 h-4" /> : entry.rank}
                    </div>

                    <div className="flex-1">
                        <div className="text-sm font-medium text-white">{entry.username}</div>
                    </div>

                    <div className="text-right">
                        <div className="text-sm font-mono text-[#00f0ff]">{entry.referral_count}</div>
                        <div className="text-xs text-gray-500">referrals</div>
                    </div>
                </div>
            ))}
        </div>
    );
}

// ============ MAIN COMPONENT ============

export default function ReferralDashboard() {
    const [stats, setStats] = useState<ReferralStats | null>(null);
    const [referralLink, setReferralLink] = useState<ReferralLink | null>(null);
    const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
    const [loading, setLoading] = useState(true);
    const [copied, setCopied] = useState(false);
    const { toast } = useToast();

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const [statsData, linkData, leaderboardData] = await Promise.all([
                api.getReferralStats(),
                api.generateReferralLink(),
                api.getReferralLeaderboard(),
            ]);

            setStats(statsData);

            // Transform API response to match UI interface if needed
            setReferralLink({
                referral_code: linkData.referral_code,
                referral_url: linkData.referral_url,
                share_message: linkData.share_message,
                share_templates: {
                    twitter: linkData.share_templates.twitter,
                    linkedin: linkData.share_templates.linkedin,
                    email_subject: linkData.share_templates.email_subject,
                    email_body: linkData.share_templates.email_body,
                    whatsapp: linkData.share_templates.whatsapp,
                }
            });

            setLeaderboard(leaderboardData);
        } catch (error) {
            console.error('Failed to load referral data:', error);
            // Fallback for safety or show error toast
            toast({ type: 'error', title: 'Error', message: 'Failed to load referral data' });
        } finally {
            setLoading(false);
        }
    };

    const copyLink = () => {
        if (referralLink) {
            navigator.clipboard.writeText(referralLink.referral_url);
            setCopied(true);
            toast({ type: 'success', title: 'Copied!', message: 'Referral link copied to clipboard' });
            setTimeout(() => setCopied(false), 2000);
        }
    };

    const shareTwitter = () => {
        if (referralLink) {
            window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(referralLink.share_templates.twitter)}`, '_blank');
        }
    };

    const shareLinkedIn = () => {
        if (referralLink) {
            window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(referralLink.referral_url)}`, '_blank');
        }
    };

    const shareEmail = () => {
        if (referralLink) {
            window.open(`mailto:?subject=${encodeURIComponent(referralLink.share_templates.email_subject)}&body=${encodeURIComponent(referralLink.share_templates.email_body)}`, '_blank');
        }
    };

    const shareWhatsApp = () => {
        if (referralLink) {
            window.open(`https://wa.me/?text=${encodeURIComponent(referralLink.share_templates.whatsapp)}`, '_blank');
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-[60vh]">
                <div className="text-[#00f0ff] font-mono animate-pulse">LOADING_REFERRAL_DATA...</div>
            </div>
        );
    }

    return (
        <div className="space-y-8 pb-12">
            {/* Header */}
            <div className="border-b border-white/10 pb-6">
                <h1 className="text-3xl font-black text-white tracking-tighter flex items-center gap-3">
                    <Gift className="w-8 h-8 text-[#00f0ff]" />
                    REFERRAL_ENGINE
                    <Badge variant="cyber" className="text-xs">VIRAL GROWTH</Badge>
                </h1>
                <p className="text-gray-500 font-mono text-sm mt-2">
                    Invite founders. Earn credits. Climb the leaderboard.
                </p>
            </div>

            {/* Stats Row */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Card className="p-4 bg-gradient-to-br from-[#00f0ff]/10 to-transparent border-[#00f0ff]/20">
                    <div className="flex items-center gap-2 text-[#00f0ff] mb-2">
                        <Users className="w-4 h-4" />
                        <span className="text-xs uppercase tracking-wider">Signups</span>
                    </div>
                    <div className="text-3xl font-black text-white">{stats?.successful_signups || 0}</div>
                </Card>

                <Card className="p-4 bg-gradient-to-br from-green-500/10 to-transparent border-green-500/20">
                    <div className="flex items-center gap-2 text-green-500 mb-2">
                        <Zap className="w-4 h-4" />
                        <span className="text-xs uppercase tracking-wider">Credits Earned</span>
                    </div>
                    <div className="text-3xl font-black text-white">{stats?.total_credits_earned || 0}</div>
                </Card>

                <Card className="p-4 bg-gradient-to-br from-purple-500/10 to-transparent border-purple-500/20">
                    <div className="flex items-center gap-2 text-purple-500 mb-2">
                        <Trophy className="w-4 h-4" />
                        <span className="text-xs uppercase tracking-wider">Your Rank</span>
                    </div>
                    <div className="text-3xl font-black text-white">#{stats?.rank || '-'}</div>
                </Card>

                <Card className="p-4 bg-gradient-to-br from-orange-500/10 to-transparent border-orange-500/20">
                    <div className="flex items-center gap-2 text-orange-500 mb-2">
                        <TrendingUp className="w-4 h-4" />
                        <span className="text-xs uppercase tracking-wider">Streak</span>
                    </div>
                    <div className="text-3xl font-black text-white">{stats?.current_streak || 0} days</div>
                </Card>
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left Column - Share */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Referral Link Card */}
                    <Card className="p-6 bg-gradient-to-br from-[#00f0ff]/5 to-transparent border-[#00f0ff]/20">
                        <div className="flex items-center gap-2 mb-4">
                            <Share2 className="w-5 h-5 text-[#00f0ff]" />
                            <h2 className="text-lg font-bold text-white">Your Referral Link</h2>
                        </div>

                        <div className="flex gap-2 mb-6">
                            <div className="flex-1 bg-black/50 border border-white/10 rounded-lg px-4 py-3 font-mono text-sm text-[#00f0ff] truncate">
                                {referralLink?.referral_url}
                            </div>
                            <Button
                                onClick={copyLink}
                                variant={copied ? "cyber" : "outline"}
                                className="shrink-0"
                            >
                                <Copy className="w-4 h-4 mr-2" />
                                {copied ? 'Copied!' : 'Copy'}
                            </Button>
                        </div>

                        {/* Share Buttons */}
                        <div className="grid grid-cols-4 gap-3">
                            <ShareButton
                                icon={Twitter}
                                label="Twitter"
                                onClick={shareTwitter}
                                color="from-blue-400/20 to-blue-500/10"
                            />
                            <ShareButton
                                icon={Linkedin}
                                label="LinkedIn"
                                onClick={shareLinkedIn}
                                color="from-blue-600/20 to-blue-700/10"
                            />
                            <ShareButton
                                icon={Mail}
                                label="Email"
                                onClick={shareEmail}
                                color="from-gray-500/20 to-gray-600/10"
                            />
                            <ShareButton
                                icon={MessageCircle}
                                label="WhatsApp"
                                onClick={shareWhatsApp}
                                color="from-green-500/20 to-green-600/10"
                            />
                        </div>
                    </Card>

                    {/* Next Milestone Progress */}
                    {stats?.next_milestone && (
                        <Card className="p-6 bg-black/50 border-white/10">
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center gap-2">
                                    <Target className="w-5 h-5 text-[#00f0ff]" />
                                    <h2 className="text-lg font-bold text-white">Next Milestone</h2>
                                </div>
                                <Badge variant="outline" className="text-[#00f0ff] border-[#00f0ff]/30">
                                    {stats.next_milestone.name}
                                </Badge>
                            </div>

                            <div className="mb-4">
                                <div className="flex justify-between text-sm mb-2">
                                    <span className="text-gray-400">Progress</span>
                                    <span className="text-[#00f0ff] font-mono">
                                        {stats.next_milestone.current}/{stats.next_milestone.required}
                                    </span>
                                </div>
                                <div className="h-4 bg-black rounded-full overflow-hidden border border-white/10">
                                    <div
                                        className="h-full bg-gradient-to-r from-[#00f0ff] to-[#00f0ff]/50 transition-all duration-500 relative"
                                        style={{ width: `${stats.next_milestone.progress_percent}%` }}
                                    >
                                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer" />
                                    </div>
                                </div>
                            </div>

                            <div className="flex items-center justify-between p-3 bg-[#00f0ff]/5 rounded-lg border border-[#00f0ff]/20">
                                <div className="flex items-center gap-2">
                                    <Sparkles className="w-4 h-4 text-[#00f0ff]" />
                                    <span className="text-sm text-gray-300">Reward</span>
                                </div>
                                <span className="text-lg font-bold text-[#00f0ff]">
                                    +{stats.next_milestone.reward_credits} credits
                                </span>
                            </div>
                        </Card>
                    )}

                    {/* Milestones Grid */}
                    <div>
                        <div className="flex items-center gap-2 mb-4">
                            <Award className="w-5 h-5 text-[#00f0ff]" />
                            <h2 className="text-lg font-bold text-white">Milestone Rewards</h2>
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                            {MILESTONES.map((milestone) => (
                                <MilestoneCard
                                    key={milestone.count}
                                    milestone={milestone}
                                    achieved={(stats?.successful_signups || 0) >= milestone.count}
                                    current={stats?.successful_signups || 0}
                                />
                            ))}
                        </div>
                    </div>
                </div>

                {/* Right Column - Leaderboard */}
                <div>
                    <Card className="p-6 bg-black/50 border-white/10 sticky top-6">
                        <div className="flex items-center gap-2 mb-4">
                            <Trophy className="w-5 h-5 text-yellow-500" />
                            <h2 className="text-lg font-bold text-white">Top Referrers</h2>
                        </div>
                        <Leaderboard entries={leaderboard} />

                        <div className="mt-4 p-3 bg-[#00f0ff]/5 rounded-lg border border-[#00f0ff]/20 text-center">
                            <div className="text-xs text-gray-400 mb-1">Your Position</div>
                            <div className="text-2xl font-black text-[#00f0ff]">#{stats?.rank}</div>
                        </div>
                    </Card>
                </div>
            </div>
        </div>
    );
}
