import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, Timer, ArrowRight, AlertTriangle, CheckCircle, Zap } from 'lucide-react';

// Region configurations with quotas and styling
const REGIONS = {
    US: {
        name: 'United States',
        flag: '🇺🇸',
        quota: 500,
        initialRemaining: 127,
        headline: 'America, Meet Your AI Co-Founder',
        subhead: 'Join 373 US entrepreneurs building faster with MomentAIc',
        gradient: 'from-blue-900 to-indigo-900',
        accent: 'text-blue-400',
        timezone: 'PST/EST'
    },
    LATAM: {
        name: 'Latin America',
        flag: '🌎',
        quota: 500,
        initialRemaining: 234,
        headline: 'LatAm: Tu Momento Es Ahora',
        subhead: 'Únete a 266 emprendedores latinoamericanos',
        gradient: 'from-emerald-900 to-teal-900',
        accent: 'text-emerald-400',
        timezone: 'CDMX/São Paulo'
    },
    EUROPE: {
        name: 'Europe',
        flag: '🇪🇺',
        quota: 500,
        initialRemaining: 89,
        headline: 'Europe: AI That Respects Your Data',
        subhead: 'Join 411 European founders building GDPR-compliant startups',
        gradient: 'from-slate-900 to-blue-950',
        accent: 'text-sky-400',
        timezone: 'CET/GMT'
    },
    ASIA: {
        name: 'Asia Pacific',
        flag: '🌏',
        quota: 500,
        initialRemaining: 156,
        headline: 'Asia: Build Faster, Scale Smarter',
        subhead: 'Join 344 APAC entrepreneurs leveraging AI automation',
        gradient: 'from-red-900 to-orange-950',
        accent: 'text-red-400',
        timezone: 'JST/SGT'
    }
};

// Recent locations for the live ticker
const LIVE_LOCATIONS = [
    'Austin, TX', 'San Francisco, CA', 'New York, NY', 'Miami, FL',
    'London, UK', 'Berlin, DE', 'Mexico City, MX', 'São Paulo, BR',
    'Tokyo, JP', 'Singapore, SG', 'Toronto, CA', 'Sydney, AU'
];

// Countdown timer component
function CountdownTimer({ endDate }: { endDate: Date }) {
    const [timeLeft, setTimeLeft] = useState({ days: 0, hours: 0, minutes: 0, seconds: 0, ms: 0 });

    useEffect(() => {
        const timer = setInterval(() => {
            const now = new Date().getTime();
            const distance = endDate.getTime() - now;

            if (distance < 0) {
                clearInterval(timer);
                return;
            }

            setTimeLeft({
                days: Math.floor(distance / (1000 * 60 * 60 * 24)),
                hours: Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
                minutes: Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60)),
                seconds: Math.floor((distance % (1000 * 60)) / 1000),
                ms: Math.floor((distance % 1000) / 10)
            });
        }, 37); // Update frequently for ms effect

        return () => clearInterval(timer);
    }, [endDate]);

    return (
        <div className="flex gap-2 md:gap-4 justify-center">
            {Object.entries(timeLeft).filter(([k]) => k !== 'ms').map(([unit, value]) => (
                <div key={unit} className="text-center">
                    <div className="text-3xl md:text-5xl font-mono font-bold bg-white/5 backdrop-blur-md rounded-lg px-3 py-2 border border-white/10 shadow-lg text-white">
                        {String(value).padStart(2, '0')}
                    </div>
                    <div className="text-[10px] md:text-xs uppercase tracking-widest mt-2 text-white/50">{unit}</div>
                </div>
            ))}
        </div>
    );
}

export default function RegionFomoPage() {
    const navigate = useNavigate();
    const [selectedRegion, setSelectedRegion] = useState<string | null>(null);
    const [regionKey, setRegionKey] = useState<string>('US');
    const [email, setEmail] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Live mechanic states
    const [remainingSpots, setRemainingSpots] = useState(127);
    const [recentSignup, setRecentSignup] = useState<string | null>(null);

    // Auto-detect region
    useEffect(() => {
        const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
        let rKey = 'US';
        if (tz.includes('New_York') || tz.includes('Los_Angeles') || tz.includes('Chicago')) rKey = 'US';
        else if (tz.includes('Mexico') || tz.includes('Sao_Paulo') || tz.includes('Buenos_Aires')) rKey = 'LATAM';
        else if (tz.includes('Europe') || tz.includes('London') || tz.includes('Berlin') || tz.includes('Paris')) rKey = 'EUROPE';
        else if (tz.includes('Asia') || tz.includes('Tokyo') || tz.includes('Singapore')) rKey = 'ASIA';

        setSelectedRegion(rKey);
        setRegionKey(rKey);
        // Set initial spots based on region, with some random variation for realism
        setRemainingSpots(REGIONS[rKey as keyof typeof REGIONS].initialRemaining);
    }, []);

    const region = selectedRegion ? REGIONS[selectedRegion as keyof typeof REGIONS] : REGIONS['US'];

    // 1. Live spot decrement simulation
    useEffect(() => {
        // Randomly decrement a spot every 10-40 seconds
        const spotInterval = setInterval(() => {
            if (Math.random() > 0.5) {
                setRemainingSpots(prev => Math.max(3, prev - 1));
                // Show a fake signup notification when spot drops
                triggerSignupNotification();
            }
        }, 15000 + Math.random() * 20000);

        return () => clearInterval(spotInterval);
    }, []);

    // 2. Fake signup ticker
    const triggerSignupNotification = () => {
        const location = LIVE_LOCATIONS[Math.floor(Math.random() * LIVE_LOCATIONS.length)];
        const names = ['Alex', 'Sarah', 'Jorge', 'Mike', 'Emma', 'David', 'Maria', 'Chen'];
        const name = names[Math.floor(Math.random() * names.length)];
        setRecentSignup(`${name} from ${location} just joined!`);

        setTimeout(() => setRecentSignup(null), 4000);
    };

    // Initial random signups
    useEffect(() => {
        const initialTimer = setTimeout(triggerSignupNotification, 3000);
        return () => clearTimeout(initialTimer);
    }, []);

    // End date: 48 hours from now (Aggressive)
    const endDate = new Date();
    endDate.setHours(endDate.getHours() + 48);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);
        try {
            const response = await fetch('/api/v1/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, region: selectedRegion, source: 'region_fomo' })
            });

            if (response.ok) {
                navigate('/dashboard?welcome=true');
            }
        } catch (error) {
            console.error('Signup failed:', error);
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className={`min-h-screen bg-gradient-to-br ${region.gradient} text-white relative overflow-hidden font-sans selection:bg-white/30`}>

            {/* Background Grid Pattern */}
            <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] pointer-events-none" />

            {/* Floating Live Notification */}
            {recentSignup && (
                <div className="fixed top-24 right-6 z-50 animate-slide-in-right">
                    <div className="bg-white/10 backdrop-blur-md border border-white/20 px-4 py-3 rounded-lg shadow-2xl flex items-center gap-3">
                        <div className="bg-green-500 rounded-full p-1">
                            <CheckCircle className="w-3 h-3 text-white" />
                        </div>
                        <span className="text-sm font-medium">{recentSignup}</span>
                    </div>
                </div>
            )}

            {/* Top Bar */}
            <div className="absolute top-0 w-full p-6 flex justify-between items-center z-10">
                <div className="bg-white/10 backdrop-blur-sm px-3 py-1 rounded-full text-xs font-mono border border-white/10 flex items-center gap-2">
                    <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                    LIVE DEMAND: HIGH
                </div>
                <div className="text-xs text-white/50 font-mono">
                    DETECTED REGION: <span className="text-white font-bold">{regionKey}</span>
                </div>
            </div>

            <main className="relative z-10 container mx-auto px-4 min-h-screen flex flex-col items-center justify-center py-20">

                {/* Visual Anchor */}
                <div className="mb-8 inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-red-500/20 text-red-300 font-medium text-sm border border-red-500/30 animate-pulse">
                    <AlertTriangle className="w-4 h-4" />
                    Warning: High Traffic Detected
                </div>

                {/* Hero */}
                <h1 className="text-5xl md:text-7xl font-bold text-center mb-6 leading-tight tracking-tight">
                    {region.headline}
                </h1>

                <p className="text-xl md:text-2xl text-white/60 text-center mb-12 max-w-2xl mx-auto leading-relaxed">
                    {region.subhead}
                </p>

                {/* The "Hook" - Countdown */}
                <div className="mb-16 transform hover:scale-105 transition-transform duration-500">
                    <div className="text-center text-sm font-bold tracking-widest text-white/40 mb-4 uppercase">
                        Access Window Closes In
                    </div>
                    <CountdownTimer endDate={endDate} />
                </div>

                {/* Main Interaction Card */}
                <div className="w-full max-w-lg bg-black/40 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-2xl ring-1 ring-white/5 relative overflow-hidden group">

                    {/* Progress Bar */}
                    <div className="mb-8">
                        <div className="flex justify-between items-end mb-2">
                            <span className="text-3xl font-bold font-mono text-white flex items-center gap-2">
                                {remainingSpots}
                                <span className="text-sm font-sans font-normal text-white/40 mb-1">spots left</span>
                            </span>
                            <span className="text-xs text-white/40 mb-1">
                                {Math.round(((region.quota - remainingSpots) / region.quota) * 100)}% Claimed
                            </span>
                        </div>
                        <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-gradient-to-r from-red-500 to-orange-500 transition-all duration-1000 ease-out"
                                style={{ width: `${((region.quota - remainingSpots) / region.quota) * 100}%` }}
                            />
                        </div>
                        <div className="mt-2 text-xs text-red-400 flex items-center gap-1">
                            <Zap className="w-3 h-3" />
                            Selling out fast - 4 people viewing this page
                        </div>
                    </div>

                    {/* Form */}
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="space-y-1">
                            <label className="text-xs font-bold text-white/60 uppercase ml-1">Email Access</label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="name@company.com"
                                required
                                className="w-full px-6 py-4 rounded-xl bg-white/5 border border-white/10 text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-white/30 focus:bg-white/10 transition-all font-medium text-lg"
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={isSubmitting}
                            className="w-full py-4 rounded-xl bg-white text-black font-bold text-lg hover:bg-white/90 transform hover:translate-y-[-2px] transition-all shadow-[0_0_40px_-10px_rgba(255,255,255,0.3)] disabled:opacity-50 disabled:hover:translate-y-0 flex items-center justify-center gap-2 group-hover:shadow-[0_0_60px_-15px_rgba(255,255,255,0.4)]"
                        >
                            {isSubmitting ? (
                                'Securing Spot...'
                            ) : (
                                <>
                                    Claim Spot Now <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                                </>
                            )}
                        </button>
                    </form>

                    <div className="mt-6 text-center">
                        <p className="text-xs text-white/30">
                            By joining, you agree to our Terms. Zero spam, automated unsubscribe.
                        </p>
                    </div>
                </div>

                {/* Region Selector (Footer) */}
                <div className="mt-16 flex flex-wrap justify-center gap-3 opacity-60 hover:opacity-100 transition-opacity">
                    {Object.entries(REGIONS).map(([key, r]) => (
                        <button
                            key={key}
                            onClick={() => {
                                setSelectedRegion(key);
                                setRegionKey(key);
                                setRemainingSpots(r.initialRemaining);
                            }}
                            className={`px-3 py-1 rounded-full text-xs font-medium border transition-all ${selectedRegion === key
                                    ? 'bg-white text-black border-white'
                                    : 'bg-transparent text-white/60 border-white/10 hover:border-white/30'
                                }`}
                        >
                            {r.flag} {r.name}
                        </button>
                    ))}
                </div>

            </main>
        </div>
    );
}
