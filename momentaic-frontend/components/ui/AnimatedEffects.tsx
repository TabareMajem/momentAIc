import React, { useState, useEffect, useRef } from 'react';
import { cn } from '../../lib/utils';

interface AnimatedCounterProps {
    value: number;
    duration?: number;
    prefix?: string;
    suffix?: string;
    label?: string;
    className?: string;
}

export const AnimatedCounter: React.FC<AnimatedCounterProps> = ({
    value,
    duration = 2000,
    prefix = '',
    suffix = '',
    label,
    className,
}) => {
    const [count, setCount] = useState(0);
    const [hasAnimated, setHasAnimated] = useState(false);
    const ref = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting && !hasAnimated) {
                    setHasAnimated(true);
                    animateValue(0, value, duration);
                }
            },
            { threshold: 0.3 }
        );

        if (ref.current) {
            observer.observe(ref.current);
        }

        return () => observer.disconnect();
    }, [value, duration, hasAnimated]);

    const animateValue = (start: number, end: number, dur: number) => {
        const startTime = performance.now();

        const step = (currentTime: number) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / dur, 1);

            // Easing function for smooth deceleration
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const current = Math.floor(start + (end - start) * easeOut);

            setCount(current);

            if (progress < 1) {
                requestAnimationFrame(step);
            }
        };

        requestAnimationFrame(step);
    };

    const formatNumber = (num: number): string => {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        }
        if (num >= 1000) {
            return (num / 1000).toFixed(num >= 10000 ? 0 : 1) + 'K';
        }
        return num.toLocaleString();
    };

    return (
        <div ref={ref} className={cn("text-center", className)}>
            <div className="text-4xl md:text-5xl font-black text-white tracking-tight">
                {prefix}{formatNumber(count)}{suffix}
            </div>
            {label && (
                <div className="text-xs font-mono text-gray-500 uppercase tracking-widest mt-2">
                    {label}
                </div>
            )}
        </div>
    );
};

// Live Activity Feed Component
interface ActivityItem {
    emoji: string;
    text: string;
    location?: string;
    time: string;
}

export const LiveActivityFeed: React.FC<{ className?: string }> = ({ className }) => {
    const [currentIndex, setCurrentIndex] = useState(0);
    const [isVisible, setIsVisible] = useState(true);

    const activities: ActivityItem[] = [
        { emoji: "🚀", text: "Sarah launched her SaaS", location: "Lagos", time: "2m ago" },
        { emoji: "💰", text: "Ahmed closed a $10K deal", location: "Dubai", time: "5m ago" },
        { emoji: "📈", text: "Maria hit 1K users", location: "São Paulo", time: "8m ago" },
        { emoji: "🎯", text: "Dev generated 50 leads", location: "Manila", time: "12m ago" },
        { emoji: "✨", text: "Alex shipped MVP in 3 days", location: "Berlin", time: "15m ago" },
        { emoji: "🔥", text: "Priya's post went viral", location: "Mumbai", time: "18m ago" },
    ];

    useEffect(() => {
        const interval = setInterval(() => {
            setIsVisible(false);
            setTimeout(() => {
                setCurrentIndex((prev) => (prev + 1) % activities.length);
                setIsVisible(true);
            }, 300);
        }, 4000);

        return () => clearInterval(interval);
    }, []);

    const current = activities[currentIndex];

    return (
        <div className={cn(
            "inline-flex items-center gap-3 bg-green-500/10 border border-green-500/20 rounded-full px-4 py-2 transition-all duration-300",
            isVisible ? "opacity-100 translate-y-0" : "opacity-0 -translate-y-2",
            className
        )}>
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
            <span className="text-sm font-medium text-green-400">
                {current.emoji} {current.text}
            </span>
            {current.location && (
                <span className="text-xs text-gray-500 font-mono">
                    from {current.location}
                </span>
            )}
        </div>
    );
};

// Typing Effect for AI responses
export const TypingText: React.FC<{
    text: string;
    speed?: number;
    onComplete?: () => void;
    className?: string;
}> = ({ text, speed = 30, onComplete, className }) => {
    const [displayedText, setDisplayedText] = useState('');
    const [isComplete, setIsComplete] = useState(false);

    useEffect(() => {
        let index = 0;
        setDisplayedText('');
        setIsComplete(false);

        const interval = setInterval(() => {
            if (index < text.length) {
                setDisplayedText(text.slice(0, index + 1));
                index++;
            } else {
                clearInterval(interval);
                setIsComplete(true);
                onComplete?.();
            }
        }, speed);

        return () => clearInterval(interval);
    }, [text, speed, onComplete]);

    return (
        <span className={className}>
            {displayedText}
            {!isComplete && <span className="animate-pulse">▊</span>}
        </span>
    );
};

// Confetti burst effect
export const ConfettiBurst: React.FC<{ trigger: boolean }> = ({ trigger }) => {
    const [particles, setParticles] = useState<Array<{
        id: number;
        x: number;
        y: number;
        color: string;
        delay: number;
    }>>([]);

    useEffect(() => {
        if (trigger) {
            const colors = ['#00f0ff', '#a855f7', '#3b82f6', '#10b981', '#f59e0b'];
            const newParticles = Array.from({ length: 50 }, (_, i) => ({
                id: i,
                x: Math.random() * 100,
                y: Math.random() * 100,
                color: colors[Math.floor(Math.random() * colors.length)],
                delay: Math.random() * 0.5,
            }));
            setParticles(newParticles);

            setTimeout(() => setParticles([]), 2000);
        }
    }, [trigger]);

    if (particles.length === 0) return null;

    return (
        <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
            {particles.map((p) => (
                <div
                    key={p.id}
                    className="absolute w-3 h-3 rounded-full animate-confetti"
                    style={{
                        left: `${p.x}%`,
                        top: `${p.y}%`,
                        backgroundColor: p.color,
                        animationDelay: `${p.delay}s`,
                    }}
                />
            ))}
        </div>
    );
};

export default AnimatedCounter;
