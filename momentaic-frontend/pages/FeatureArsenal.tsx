import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    LayoutDashboard, Shield, Settings, Zap, Activity, TrendingUp, Network,
    Sparkles, BookOpen, BarChart2, Phone, Target, Globe, Plug, Bell,
    FlaskConical, Terminal, DollarSign, Check, Lock, ArrowRight
} from 'lucide-react';
import { FEATURE_REGISTRY, useFeatureStore, type FeatureDefinition } from '../stores/feature-store';
import { cn } from '../lib/utils';

const ICON_MAP: Record<string, any> = {
    LayoutDashboard, Shield, Settings, Zap, Activity, TrendingUp, Network,
    Sparkles, BookOpen, BarChart2, Phone, Target, Globe, Plug, Bell,
    FlaskConical, Terminal, DollarSign,
};

const TIER_CONFIG = {
    essential: { label: 'ESSENTIAL', color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/30', glow: 'shadow-emerald-500/10' },
    growth: { label: 'GROWTH', color: 'text-blue-400', bg: 'bg-blue-500/10', border: 'border-blue-500/30', glow: 'shadow-blue-500/10' },
    godmode: { label: 'GOD MODE', color: 'text-purple-400', bg: 'bg-purple-500/10', border: 'border-purple-500/30', glow: 'shadow-purple-500/10' },
};

const CATEGORY_CONFIG: Record<string, { label: string; emoji: string }> = {
    core: { label: 'Core', emoji: '⚡' },
    marketing: { label: 'Marketing', emoji: '📣' },
    operations: { label: 'Operations', emoji: '⚙️' },
    intelligence: { label: 'Intelligence', emoji: '🧠' },
    agents: { label: 'AI Agents', emoji: '🤖' },
};

function FeatureCard({ feature }: { feature: FeatureDefinition }) {
    const { isEnabled, toggleFeature } = useFeatureStore();
    const enabled = isEnabled(feature.id);
    const isEssential = feature.tier === 'essential';
    const tier = TIER_CONFIG[feature.tier];
    const Icon = ICON_MAP[feature.icon] || Shield;
    const navigate = useNavigate();

    return (
        <div
            className={cn(
                "relative group rounded-xl border p-5 transition-all duration-300",
                enabled
                    ? `bg-white/[0.03] ${tier.border} shadow-lg ${tier.glow}`
                    : "bg-white/[0.01] border-white/5 hover:border-white/15 hover:bg-white/[0.02]"
            )}
        >
            {/* Tier Badge */}
            <div className={cn(
                "absolute top-3 right-3 text-[8px] font-mono font-bold tracking-[0.2em] uppercase px-2 py-0.5 rounded",
                tier.bg, tier.color
            )}>
                {tier.label}
            </div>

            {/* Icon */}
            <div className={cn(
                "w-10 h-10 rounded-lg flex items-center justify-center mb-4 transition-colors",
                enabled ? tier.bg : "bg-white/5"
            )}>
                <Icon className={cn("w-5 h-5", enabled ? tier.color : "text-gray-600")} />
            </div>

            {/* Info */}
            <h3 className={cn(
                "text-sm font-bold mb-1 transition-colors",
                enabled ? "text-white" : "text-gray-400"
            )}>
                {feature.name}
            </h3>
            <p className="text-xs text-gray-600 mb-4 leading-relaxed line-clamp-2">
                {feature.description}
            </p>

            {/* Action */}
            <div className="flex items-center justify-between">
                {isEssential ? (
                    <span className="text-[9px] font-mono text-emerald-500/60 uppercase tracking-widest flex items-center gap-1">
                        <Check className="w-3 h-3" /> Always Active
                    </span>
                ) : (
                    <button
                        onClick={() => toggleFeature(feature.id)}
                        className={cn(
                            "text-[10px] font-mono font-bold uppercase tracking-widest px-3 py-1.5 rounded-lg border transition-all",
                            enabled
                                ? "text-red-400 border-red-500/30 hover:bg-red-500/10"
                                : `${tier.color} ${tier.border} hover:${tier.bg}`
                        )}
                    >
                        {enabled ? 'Deactivate' : 'Activate'}
                    </button>
                )}

                {enabled && (
                    <button
                        onClick={() => navigate(feature.href)}
                        className="text-[10px] font-mono text-white/40 hover:text-white flex items-center gap-1 transition-colors"
                    >
                        Open <ArrowRight className="w-3 h-3" />
                    </button>
                )}
            </div>
        </div>
    );
}

export default function FeatureArsenal() {
    const { enabledFeatures, enableAll, resetToEssentials } = useFeatureStore();
    const [activeCategory, setActiveCategory] = useState<string>('all');

    const categories = ['all', ...Object.keys(CATEGORY_CONFIG)];
    const filteredFeatures = activeCategory === 'all'
        ? FEATURE_REGISTRY
        : FEATURE_REGISTRY.filter(f => f.category === activeCategory);

    const activeCount = enabledFeatures.length;
    const totalCount = FEATURE_REGISTRY.length;

    return (
        <div className="min-h-screen bg-[#020202] text-white pb-20">
            {/* Header */}
            <div className="mb-10">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <div className="text-[10px] font-mono text-purple-400 tracking-[0.3em] uppercase mb-2">
                            ✦ YOUR ARSENAL
                        </div>
                        <h1 className="text-3xl md:text-4xl font-black tracking-tight">
                            Feature Control Center
                        </h1>
                        <p className="text-sm text-gray-500 mt-2 max-w-lg">
                            Activate the capabilities your startup needs right now. Your sidebar adapts instantly.
                        </p>
                    </div>

                    <div className="flex gap-2">
                        <button
                            onClick={resetToEssentials}
                            className="px-4 py-2 text-[10px] font-mono font-bold uppercase tracking-widest border border-white/10 text-gray-400 hover:text-white hover:border-white/30 rounded-lg transition-all"
                        >
                            Reset
                        </button>
                        <button
                            onClick={enableAll}
                            className="px-4 py-2 text-[10px] font-mono font-bold uppercase tracking-widest bg-purple-500/10 border border-purple-500/30 text-purple-400 hover:bg-purple-500/20 rounded-lg transition-all"
                        >
                            Unlock All
                        </button>
                    </div>
                </div>

                {/* Stats Bar */}
                <div className="flex items-center gap-6 py-3 px-4 bg-white/[0.02] border border-white/5 rounded-lg">
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                        <span className="text-xs font-mono text-gray-400">
                            <span className="text-white font-bold">{activeCount}</span> / {totalCount} Active
                        </span>
                    </div>
                    <div className="h-4 w-px bg-white/10" />
                    <div className="flex-1 h-1.5 bg-white/5 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-gradient-to-r from-emerald-500 via-blue-500 to-purple-500 rounded-full transition-all duration-500"
                            style={{ width: `${(activeCount / totalCount) * 100}%` }}
                        />
                    </div>
                </div>
            </div>

            {/* Category Filter */}
            <div className="flex gap-2 mb-8 overflow-x-auto pb-2 scrollbar-hide">
                {categories.map(cat => (
                    <button
                        key={cat}
                        onClick={() => setActiveCategory(cat)}
                        className={cn(
                            "px-4 py-2 text-[10px] font-mono font-bold uppercase tracking-widest rounded-lg border whitespace-nowrap transition-all",
                            activeCategory === cat
                                ? "bg-white/10 border-white/20 text-white"
                                : "bg-transparent border-white/5 text-gray-600 hover:text-gray-400 hover:border-white/10"
                        )}
                    >
                        {cat === 'all' ? '🌐 All' : `${CATEGORY_CONFIG[cat].emoji} ${CATEGORY_CONFIG[cat].label}`}
                    </button>
                ))}
            </div>

            {/* Feature Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredFeatures.map(feature => (
                    <FeatureCard key={feature.id} feature={feature} />
                ))}
            </div>
        </div>
    );
}
