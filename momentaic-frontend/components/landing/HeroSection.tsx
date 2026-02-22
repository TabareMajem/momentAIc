import React, { useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Play, BadgeCheck } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { cn } from '../../lib/utils';
import { AgentCommandCenter } from './AgentCommandCenter';

export const HeroSection = () => {
    const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
    const heroRef = useRef<HTMLDivElement>(null);

    const handleMouseMove = (e: React.MouseEvent) => {
        if (!heroRef.current) return;
        const { left, top, width, height } = heroRef.current.getBoundingClientRect();
        const x = (e.clientX - left) / width - 0.5;
        const y = (e.clientY - top) / height - 0.5;
        setMousePos({ x, y });
    };

    return (
        <section
            ref={heroRef}
            onMouseMove={handleMouseMove}
            className="relative min-h-screen flex flex-col items-center justify-center pt-32 pb-20 overflow-hidden bg-neural"
        >
            {/* Background Effects */}
            <div className="absolute inset-0 bg-noise opacity-[0.03]" />
            <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808008_1px,transparent_1px),linear-gradient(to_bottom,#80808008_1px,transparent_1px)] bg-[size:32px_32px]" />

            {/* Content Container */}
            <div className="relative z-10 max-w-7xl mx-auto px-6 w-full text-center">

                {/* Version Badge */}
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 backdrop-blur-md mb-8 animate-fade-in-up">
                    <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                    </span>
                    <span className="text-xs font-mono text-gray-400 uppercase tracking-widest">System Online v2.4</span>
                </div>

                {/* Main Headline with Parallax */}
                <h1
                    className="text-6xl md:text-7xl lg:text-9xl font-black tracking-tighter leading-[0.9] text-white animate-slide-up"
                    style={{
                        transform: `translate(${mousePos.x * -20}px, ${mousePos.y * -20}px)`,
                        textShadow: '0 0 40px rgba(168, 85, 247, 0.2)'
                    }}
                >
                    Scale <br />
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-white to-blue-400 animate-gradient bg-[length:200%_auto]">
                        Infinite.
                    </span>
                </h1>

                <p className="mt-8 text-xl text-gray-400 max-w-2xl mx-auto leading-relaxed animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
                    Deploy <span className="text-white font-bold border-b border-purple-500">16 Autonomous Agents</span> in seconds.
                    <br className="hidden md:block" />
                    Your 24/7 AI workforce that builds, sells, and optimizes while you sleep.
                </p>

                {/* CTAs */}
                <div className="flex flex-col sm:flex-row gap-4 items-center justify-center mt-12 animate-fade-in-up" style={{ animationDelay: '0.4s' }}>
                    <Link to="/signup">
                        <Button className="h-14 px-8 text-lg bg-white text-black hover:bg-gray-200 font-bold rounded-xl shadow-[0_0_30px_-5px_rgba(255,255,255,0.4)] transition-all hover:scale-105 btn-brand text-white border-0">
                            Start Free Trial <ArrowRight className="ml-2 w-5 h-5" />
                        </Button>
                    </Link>
                    <button className="h-14 px-8 text-lg text-gray-400 hover:text-white border border-white/10 rounded-xl hover:bg-white/5 transition-all flex items-center gap-2">
                        <Play className="w-5 h-5 fill-current" /> Watch Demo
                    </button>
                </div>

                {/* Trust Badges */}
                <div className="mt-12 flex items-center justify-center gap-6 text-sm text-gray-500 font-mono animate-fade-in-up" style={{ animationDelay: '0.6s' }}>
                    <span className="flex items-center gap-1"><BadgeCheck className="w-4 h-4 text-purple-500" /> SOC2 Compliant</span>
                    <span className="flex items-center gap-1"><BadgeCheck className="w-4 h-4 text-purple-500" /> Stripe Validated</span>
                </div>

                {/* Command Center Preview (The "Show" part) */}
                <div
                    className="mt-24 transform transition-all duration-1000 ease-out perspective-1000"
                    style={{
                        transform: `rotateX(${mousePos.y * 10}deg) rotateY(${mousePos.x * 10}deg)`,
                    }}
                >
                    <div className="relative group">
                        <div className="absolute -inset-1 bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl blur opacity-25 group-hover:opacity-50 transition duration-1000"></div>
                        <AgentCommandCenter />
                    </div>
                </div>

            </div>
        </section>
    );
};
