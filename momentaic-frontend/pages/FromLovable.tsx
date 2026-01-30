import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Rocket, Sparkles, ArrowRight, Zap, Check } from 'lucide-react';
import { Button } from '../components/ui/Button';

export default function FromLovable() {
    const navigate = useNavigate();
    const [url, setUrl] = useState('');

    const handleLaunch = () => {
        if (url.trim()) {
            // Store URL for genius session and redirect
            sessionStorage.setItem('onboarding_url', url);
            navigate('/signup?ref=lovable');
        }
    };

    return (
        <div className="min-h-screen bg-[#050505] text-white overflow-hidden">
            {/* Animated Background */}
            <div className="fixed inset-0 bg-gradient-to-br from-purple-900/20 via-transparent to-cyan-900/20 pointer-events-none" />
            <div className="fixed inset-0 bg-[url('/grid.svg')] opacity-5 pointer-events-none" />

            {/* Hero */}
            <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-6">
                {/* Badge */}
                <div className="mb-8 flex items-center gap-2 px-4 py-2 bg-purple-500/10 border border-purple-500/30 rounded-full text-purple-400 text-sm font-mono animate-pulse">
                    <Sparkles className="w-4 h-4" />
                    FOR LOVABLE BUILDERS
                </div>

                {/* Main Headline */}
                <h1 className="text-4xl md:text-7xl font-black text-center max-w-4xl leading-tight mb-6">
                    You built it in
                    <span className="bg-gradient-to-r from-[#00f0ff] to-purple-500 bg-clip-text text-transparent"> 10 minutes</span>.
                    <br />
                    Now get your first
                    <span className="bg-gradient-to-r from-purple-500 to-pink-500 bg-clip-text text-transparent"> 10 users</span>.
                </h1>

                <p className="text-gray-400 text-lg md:text-xl text-center max-w-2xl mb-12">
                    Your Lovable app is live. Nobody knows it exists.
                    <strong className="text-white"> We fix that in 60 seconds.</strong>
                </p>

                {/* URL Input */}
                <div className="w-full max-w-xl mb-8">
                    <div className="relative group">
                        <input
                            type="url"
                            value={url}
                            onChange={(e) => setUrl(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleLaunch()}
                            placeholder="Paste your Lovable app URL..."
                            className="w-full bg-black/50 border-2 border-purple-500/30 rounded-2xl px-6 py-5 pr-16 text-white text-lg placeholder-gray-600 focus:outline-none focus:border-[#00f0ff] focus:ring-2 focus:ring-[#00f0ff]/20 transition-all font-mono"
                        />
                        <button
                            onClick={handleLaunch}
                            disabled={!url.trim()}
                            className="absolute right-3 top-3 p-3 bg-gradient-to-tr from-[#00f0ff] to-purple-500 rounded-xl text-black hover:opacity-90 disabled:opacity-50 transition-all shadow-lg shadow-purple-500/20"
                        >
                            <ArrowRight className="w-5 h-5" />
                        </button>
                    </div>
                </div>

                {/* CTA Button */}
                <Button
                    onClick={handleLaunch}
                    className="bg-gradient-to-r from-[#00f0ff] to-purple-500 text-black font-black text-lg px-12 py-6 rounded-2xl shadow-[0_0_40px_rgba(168,85,247,0.3)] hover:shadow-[0_0_60px_rgba(168,85,247,0.5)] transition-all"
                >
                    <Rocket className="w-5 h-5 mr-2" />
                    LAUNCH MY GROWTH
                </Button>

                {/* Social Proof */}
                <div className="mt-12 flex items-center gap-8 text-sm text-gray-500">
                    <div className="flex items-center gap-2">
                        <Check className="w-4 h-4 text-green-500" />
                        No credit card required
                    </div>
                    <div className="flex items-center gap-2">
                        <Zap className="w-4 h-4 text-yellow-500" />
                        AI-generated in 60 seconds
                    </div>
                </div>

                {/* What You Get */}
                <div className="mt-20 grid md:grid-cols-3 gap-6 max-w-4xl">
                    <div className="p-6 bg-white/5 border border-white/10 rounded-2xl text-center">
                        <div className="w-12 h-12 mx-auto mb-4 rounded-xl bg-[#00f0ff]/10 flex items-center justify-center">
                            <Sparkles className="w-6 h-6 text-[#00f0ff]" />
                        </div>
                        <h3 className="font-bold mb-2">AI Analyzes Your App</h3>
                        <p className="text-sm text-gray-400">We scrape your landing page and understand what you built.</p>
                    </div>
                    <div className="p-6 bg-white/5 border border-white/10 rounded-2xl text-center">
                        <div className="w-12 h-12 mx-auto mb-4 rounded-xl bg-purple-500/10 flex items-center justify-center">
                            <Zap className="w-6 h-6 text-purple-400" />
                        </div>
                        <h3 className="font-bold mb-2">Instant Growth Plan</h3>
                        <p className="text-sm text-gray-400">Target audience, viral hooks, and your first week of posts.</p>
                    </div>
                    <div className="p-6 bg-white/5 border border-white/10 rounded-2xl text-center">
                        <div className="w-12 h-12 mx-auto mb-4 rounded-xl bg-pink-500/10 flex items-center justify-center">
                            <Rocket className="w-6 h-6 text-pink-400" />
                        </div>
                        <h3 className="font-bold mb-2">One-Click Execute</h3>
                        <p className="text-sm text-gray-400">We schedule posts and find leads. You sit back.</p>
                    </div>
                </div>

                {/* Footer */}
                <div className="mt-20 text-center text-gray-600 text-xs font-mono">
                    MOMENTAIC • THE AI CO-FOUNDER FOR POST-MVP BUILDERS
                </div>
            </div>
        </div>
    );
}
