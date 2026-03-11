import React, { useState } from 'react';
import { Lock, Bell, BellOff, Sparkles, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Button } from './Button';

interface ComingSoonOverlayProps {
    featureName: string;
    description?: string;
    eta?: string;
    children: React.ReactNode;
}

/**
 * Wraps an existing page with a blurred "Coming Soon" overlay.
 * The original page content is preserved underneath and visible through the blur.
 * This is NON-DESTRUCTIVE — no code is deleted.
 */
export function ComingSoonOverlay({ featureName, description, eta, children }: ComingSoonOverlayProps) {
    const navigate = useNavigate();
    const storageKey = `coming_soon_notify_${featureName.toLowerCase().replace(/\s+/g, '_')}`;
    const [notifyMe, setNotifyMe] = useState(() => localStorage.getItem(storageKey) === 'true');

    const handleNotify = () => {
        const next = !notifyMe;
        setNotifyMe(next);
        localStorage.setItem(storageKey, String(next));
    };

    return (
        <div className="relative min-h-[80vh]">
            {/* Original page content — blurred but visible */}
            <div className="pointer-events-none select-none filter blur-[6px] opacity-40">
                {children}
            </div>

            {/* Overlay */}
            <div className="absolute inset-0 z-50 flex items-center justify-center">
                {/* Background dim */}
                <div className="absolute inset-0 bg-[#020202]/60 backdrop-blur-sm" />

                <div className="relative z-10 max-w-lg w-full text-center px-6">
                    {/* Lock Icon */}
                    <div className="w-20 h-20 bg-[#111111] border border-white/10 rounded-2xl flex items-center justify-center mx-auto mb-8 shadow-2xl relative">
                        <Lock className="w-8 h-8 text-gray-500" />
                        <div className="absolute -top-1 -right-1 w-4 h-4 bg-purple-500 rounded-full flex items-center justify-center">
                            <Sparkles className="w-2.5 h-2.5 text-white" />
                        </div>
                    </div>

                    {/* Feature Name */}
                    <h1 className="text-3xl md:text-4xl font-black uppercase tracking-tighter text-white mb-3">
                        {featureName}
                    </h1>

                    {/* Status Badge */}
                    <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-purple-500/10 border border-purple-500/30 rounded-full mb-6">
                        <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse" />
                        <span className="text-xs font-bold font-mono text-purple-400 uppercase tracking-widest">
                            Coming Soon
                        </span>
                    </div>

                    {/* Description */}
                    <p className="text-gray-400 text-sm leading-relaxed max-w-md mx-auto mb-2">
                        {description || `This module is being engineered by the DeerFlow team and will deploy in an upcoming platform update.`}
                    </p>

                    {eta && (
                        <p className="text-[10px] font-mono text-gray-600 uppercase tracking-widest mb-8">
                            Estimated Deploy: {eta}
                        </p>
                    )}

                    {!eta && <div className="mb-8" />}

                    {/* Action Buttons */}
                    <div className="flex flex-col sm:flex-row gap-3 justify-center">
                        <Button
                            onClick={handleNotify}
                            variant="outline"
                            className={`h-11 px-6 font-mono text-xs uppercase tracking-widest transition-all ${
                                notifyMe
                                    ? 'bg-purple-500/10 border-purple-500/50 text-purple-400'
                                    : 'border-white/10 text-gray-400 hover:border-purple-500/30'
                            }`}
                        >
                            {notifyMe ? (
                                <><BellOff className="w-4 h-4 mr-2" /> Notification Set</>
                            ) : (
                                <><Bell className="w-4 h-4 mr-2" /> Notify Me at Launch</>
                            )}
                        </Button>

                        <Button
                            onClick={() => navigate('/dashboard')}
                            variant="ghost"
                            className="h-11 px-6 font-mono text-xs uppercase tracking-widest text-gray-500 hover:text-white"
                        >
                            <ArrowLeft className="w-4 h-4 mr-2" /> Back to Command Center
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
}
