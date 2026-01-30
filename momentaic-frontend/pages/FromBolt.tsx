import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Rocket, Sparkles, ArrowRight, Zap, Check, Terminal } from 'lucide-react';
import { Button } from '../components/ui/Button';

export default function FromBolt() {
    const navigate = useNavigate();
    const [url, setUrl] = useState('');

    const handleLaunch = () => {
        if (url.trim()) {
            sessionStorage.setItem('onboarding_url', url);
            navigate('/signup?ref=bolt');
        }
    };

    return (
        <div className="min-h-screen bg-[#050505] text-white overflow-hidden">
            {/* Animated Background */}
            <div className="fixed inset-0 bg-gradient-to-br from-yellow-900/20 via-transparent to-cyan-900/20 pointer-events-none" />
            <div className="fixed inset-0 bg-[url('/grid.svg')] opacity-5 pointer-events-none" />

            {/* Hero */}
            <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-6">
                {/* Badge */}
                <div className="mb-8 flex items-center gap-2 px-4 py-2 bg-yellow-500/10 border border-yellow-500/30 rounded-full text-yellow-400 text-sm font-mono animate-pulse">
                    <Terminal className="w-4 h-4" />
                    FOR BOLT.NEW BUILDERS
                </div>

                {/* Main Headline */}
                <h1 className="text-4xl md:text-7xl font-black text-center max-w-4xl leading-tight mb-6">
                    Your app shipped
                    <span className="bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent"> instantly</span>.
                    <br />
                    Your growth should too.
                </h1>

                <p className="text-gray-400 text-lg md:text-xl text-center max-w-2xl mb-12">
                    Bolt built your app in seconds. Now let AI find your first customers.
                    <strong className="text-white"> Same speed. Same magic.</strong>
                </p>

                {/* URL Input */}
                <div className="w-full max-w-xl mb-8">
                    <div className="relative group">
                        <input
                            type="url"
                            value={url}
                            onChange={(e) => setUrl(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleLaunch()}
                            placeholder="Paste your bolt.new app URL..."
                            className="w-full bg-black/50 border-2 border-yellow-500/30 rounded-2xl px-6 py-5 pr-16 text-white text-lg placeholder-gray-600 focus:outline-none focus:border-[#00f0ff] focus:ring-2 focus:ring-[#00f0ff]/20 transition-all font-mono"
                        />
                        <button
                            onClick={handleLaunch}
                            disabled={!url.trim()}
                            className="absolute right-3 top-3 p-3 bg-gradient-to-tr from-yellow-400 to-orange-500 rounded-xl text-black hover:opacity-90 disabled:opacity-50 transition-all shadow-lg shadow-yellow-500/20"
                        >
                            <ArrowRight className="w-5 h-5" />
                        </button>
                    </div>
                </div>

                {/* CTA Button */}
                <Button
                    onClick={handleLaunch}
                    className="bg-gradient-to-r from-yellow-400 to-orange-500 text-black font-black text-lg px-12 py-6 rounded-2xl shadow-[0_0_40px_rgba(234,179,8,0.3)] hover:shadow-[0_0_60px_rgba(234,179,8,0.5)] transition-all"
                >
                    <Zap className="w-5 h-5 mr-2" />
                    LAUNCH MY GROWTH
                </Button>

                {/* Social Proof */}
                <div className="mt-12 flex items-center gap-8 text-sm text-gray-500">
                    <div className="flex items-center gap-2">
                        <Check className="w-4 h-4 text-green-500" />
                        No credit card required
                    </div>
                    <div className="flex items-center gap-2">
                        <Sparkles className="w-4 h-4 text-[#00f0ff]" />
                        First post in 60 seconds
                    </div>
                </div>

                {/* What You Get */}
                <div className="mt-20 grid md:grid-cols-3 gap-6 max-w-4xl">
                    <div className="p-6 bg-white/5 border border-white/10 rounded-2xl text-center">
                        <div className="w-12 h-12 mx-auto mb-4 rounded-xl bg-yellow-500/10 flex items-center justify-center">
                            <Terminal className="w-6 h-6 text-yellow-400" />
                        </div>
                        <h3 className="font-bold mb-2">We Read Your App</h3>
                        <p className="text-sm text-gray-400">AI scrapes and understands what you built.</p>
                    </div>
                    <div className="p-6 bg-white/5 border border-white/10 rounded-2xl text-center">
                        <div className="w-12 h-12 mx-auto mb-4 rounded-xl bg-orange-500/10 flex items-center justify-center">
                            <Sparkles className="w-6 h-6 text-orange-400" />
                        </div>
                        <h3 className="font-bold mb-2">Generate Growth Plan</h3>
                        <p className="text-sm text-gray-400">Posts, leads, experiments—all in one click.</p>
                    </div>
                    <div className="p-6 bg-white/5 border border-white/10 rounded-2xl text-center">
                        <div className="w-12 h-12 mx-auto mb-4 rounded-xl bg-[#00f0ff]/10 flex items-center justify-center">
                            <Rocket className="w-6 h-6 text-[#00f0ff]" />
                        </div>
                        <h3 className="font-bold mb-2">Execute Instantly</h3>
                        <p className="text-sm text-gray-400">AI schedules posts and finds customers.</p>
                    </div>
                </div>

                {/* Comparison */}
                <div className="mt-16 p-6 bg-white/5 border border-white/10 rounded-2xl max-w-2xl w-full">
                    <h3 className="text-center font-bold mb-6 text-gray-400 uppercase text-xs tracking-widest">The 2026 Builder Stack</h3>
                    <div className="grid grid-cols-2 gap-4 text-center">
                        <div className="p-4 bg-yellow-500/10 rounded-xl border border-yellow-500/20">
                            <div className="font-bold text-yellow-400 text-lg mb-1">bolt.new</div>
                            <div className="text-xs text-gray-400">Builds the Product</div>
                        </div>
                        <div className="p-4 bg-[#00f0ff]/10 rounded-xl border border-[#00f0ff]/20">
                            <div className="font-bold text-[#00f0ff] text-lg mb-1">MomentAIc</div>
                            <div className="text-xs text-gray-400">Grows the Users</div>
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="mt-20 text-center text-gray-600 text-xs font-mono">
                    MOMENTAIC • YOUR AI CO-FOUNDER FOR GROWTH
                </div>
            </div>
        </div>
    );
}
