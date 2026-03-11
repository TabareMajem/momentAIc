import { Rocket, Sparkles, Zap } from 'lucide-react';
import { Button } from '../ui/Button';

export function ZeroStateWidget({ pendingStrategy, onCreateStartup }: { pendingStrategy: any; onCreateStartup: () => void }) {
    return (
        <div className="min-h-[60vh] flex flex-col items-center justify-center text-center px-4">
            <div className="max-w-lg space-y-8">
                {/* Icon */}
                <div className="relative mx-auto w-24 h-24">
                    <div className="absolute inset-0 bg-[#111111] from-purple-500/20 rounded-full animate-pulse" />
                    <div className="relative w-full h-full rounded-full bg-[#111] border border-white/10 flex items-center justify-center">
                        <Rocket className="w-10 h-10 text-[#00f0ff]" />
                    </div>
                </div>

                {/* Title */}
                <div>
                    <h2 className="text-3xl font-bold text-white mb-3">Launch Your Empire</h2>
                    <p className="text-gray-400 text-sm">
                        {pendingStrategy
                            ? "You have a strategy ready! Create your first startup to activate it."
                            : "Create your first startup to unlock the full power of your AI team."
                        }
                    </p>
                </div>

                {/* Pending Strategy Preview */}
                {pendingStrategy && (
                    <div className="bg-[#0a0a0a] border border-[#00f0ff]/20 rounded-xl p-4 text-left">
                        <div className="flex items-center gap-2 mb-2 text-[#00f0ff]">
                            <Sparkles className="w-4 h-4" />
                            <span className="text-xs font-bold uppercase tracking-widest">Saved Strategy</span>
                        </div>
                        <p className="text-sm text-gray-300 line-clamp-2">
                            {pendingStrategy.strategy?.target_audience || pendingStrategy.plan?.summary || "Your AI-generated growth strategy is ready"}
                        </p>
                    </div>
                )}

                {/* CTA Button */}
                <Button
                    variant="cyber"
                    size="lg"
                    onClick={onCreateStartup}
                    className="w-full max-w-xs mx-auto"
                >
                    <Zap className="w-5 h-5 mr-2" />
                    CREATE YOUR FIRST STARTUP
                </Button>

                {/* Secondary Action */}
                <p className="text-xs text-gray-600">
                    Takes less than 60 seconds • No credit card required
                </p>
            </div>
        </div>
    );
}
