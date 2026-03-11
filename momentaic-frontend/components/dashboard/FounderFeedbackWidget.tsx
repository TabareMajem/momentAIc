import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '../ui/Card';
import { Button } from '../ui/Button';
import { CheckCircle2, ChevronDown, Heart, Sparkles, X } from 'lucide-react';
import { useAuthStore } from '../../stores/auth-store';
import { api } from '../../lib/api';

export function FounderFeedbackWidget() {
    const { user } = useAuthStore();
    const [isVisible, setIsVisible] = useState(false);
    const [isSubmitted, setIsSubmitted] = useState(false);
    const [selectedScore, setSelectedScore] = useState<number | null>(null);
    const [feedbackText, setFeedbackText] = useState('');
    const [isExpanded, setIsExpanded] = useState(true);

    // Only show to founders after some time has passed to accumulate usage
    useEffect(() => {
        // Check if they've already submitted feedback recently
        const lastSubmitted = localStorage.getItem('pmf_feedback_timestamp');
        if (lastSubmitted) {
            const daysSince = (Date.now() - parseInt(lastSubmitted)) / (1000 * 60 * 60 * 24);
            if (daysSince < 30) {
                return; // Don't show if they answered in the last 30 days
            }
        }

        // Delay showing the widget so it doesn't overwhelm them on immediate load
        const timer = setTimeout(() => {
            setIsVisible(true);
        }, 5000);

        return () => clearTimeout(timer);
    }, []);

    const handleSubmit = async () => {
        if (!selectedScore) return;
        
        try {
            // Mock API call for the PMF score submission
            // await api.submitPMFFeedback({ score: selectedScore, comment: feedbackText });
            localStorage.setItem('pmf_feedback_timestamp', Date.now().toString());
            setIsSubmitted(true);
            setTimeout(() => setIsVisible(false), 5000); // Hide completely after 5s
        } catch (error) {
            console.error("Failed to submit PMF feedback:", error);
        }
    };

    if (!isVisible) return null;

    if (!isExpanded && !isSubmitted) {
        return (
            <button 
                onClick={() => setIsExpanded(true)}
                className="fixed bottom-6 right-6 z-50 bg-[#111111] border border-brand-purple/30 p-3 rounded-full shadow-2xl hover:border-brand-purple/60 hover:scale-110 transition-all group"
            >
                <Heart className="w-5 h-5 text-brand-purple animate-pulse" />
            </button>
        );
    }

    return (
        <div className="fixed bottom-6 right-6 z-50 w-full max-w-sm animate-in slide-in-from-bottom-5 fade-in duration-500">
            <Card variant="neon" className="shadow-[0_0_50px_rgba(0,0,0,0.5)] overflow-hidden">
                {!isSubmitted && (
                    <button 
                        onClick={() => setIsExpanded(false)}
                        className="absolute top-3 right-3 text-gray-500 hover:text-white transition-colors"
                    >
                        <ChevronDown className="w-4 h-4" />
                    </button>
                )}
                
                <CardContent className="p-5">
                    {isSubmitted ? (
                        <div className="text-center py-4 space-y-3">
                            <div className="w-12 h-12 bg-emerald-500/10 rounded-full flex items-center justify-center mx-auto mb-3">
                                <CheckCircle2 className="w-6 h-6 text-emerald-400" />
                            </div>
                            <h3 className="font-bold text-white text-lg tracking-tight">Data Transmitted</h3>
                            <p className="text-sm text-gray-400 font-mono">
                                Your intelligence has been routed directly to the founding team. We build what you need.
                            </p>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            <div className="flex items-center gap-2 mb-2">
                                <Sparkles className="w-4 h-4 text-brand-purple" />
                                <h3 className="font-bold text-sm tracking-widest uppercase text-gray-300">Telemetry Pulse</h3>
                            </div>
                            
                            <p className="text-sm text-white font-medium leading-relaxed">
                                How disappointed would you be if you could no longer use MomentAIc?
                            </p>
                            
                            <div className="space-y-2">
                                {[
                                    { score: 3, label: 'Very disappointed', color: 'hover:border-emerald-500 hover:bg-emerald-500/10', active: 'border-emerald-500 bg-emerald-500/20 text-emerald-300' },
                                    { score: 2, label: 'Somewhat disappointed', color: 'hover:border-blue-500 hover:bg-blue-500/10', active: 'border-blue-500 bg-blue-500/20 text-blue-300' },
                                    { score: 1, label: 'Not disappointed', color: 'hover:border-red-500 hover:bg-red-500/10', active: 'border-red-500 bg-red-500/20 text-red-300' }
                                ].map((option) => (
                                    <button
                                        key={option.score}
                                        onClick={() => setSelectedScore(option.score)}
                                        className={`w-full text-left px-4 py-3 rounded-xl border transition-all text-sm font-medium ${
                                            selectedScore === option.score 
                                                ? option.active 
                                                : `border-white/10 bg-[#0A0A0A] text-gray-400 ${option.color}`
                                        }`}
                                    >
                                        {option.label}
                                    </button>
                                ))}
                            </div>

                            {selectedScore && (
                                <div className="space-y-3 pt-2 animate-in fade-in slide-in-from-top-2">
                                    <textarea
                                        value={feedbackText}
                                        onChange={(e) => setFeedbackText(e.target.value)}
                                        placeholder="What is the main benefit you receive from it?"
                                        className="w-full h-24 px-3 py-2 bg-[#0A0A0A] border border-white/10 rounded-lg text-sm text-white placeholder-gray-600 focus:outline-none focus:border-brand-purple/50 resize-none font-mono"
                                    />
                                    <div className="flex gap-2">
                                        <Button 
                                            variant="ghost" 
                                            onClick={() => setIsExpanded(false)}
                                            className="flex-1 text-xs font-mono uppercase tracking-widest"
                                        >
                                            Dismiss
                                        </Button>
                                        <Button 
                                            onClick={handleSubmit}
                                            className="flex-1 text-xs font-mono uppercase tracking-widest bg-brand-purple hover:bg-brand-purple/80 text-white"
                                        >
                                            Transmit
                                        </Button>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
