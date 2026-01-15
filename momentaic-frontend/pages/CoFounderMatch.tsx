import React, { useState } from 'react';
import { Users, Briefcase, Globe, Heart, Zap, Award, CheckCircle } from 'lucide-react';
import api from '../lib/api';

interface Match {
    id: string;
    name: string;
    role: string;
    match_score: number;
    match_reason: string;
    skills: string[];
    bio: string;
}

export default function CoFounderMatch() {
    const [matches, setMatches] = useState<Match[]>([]);
    const [loading, setLoading] = useState(false);
    const [profile, setProfile] = useState({
        skills: '',
        looking_for: '',
        timezone: '',
        bio: '',
        industry: ''
    });

    const handleMatch = async () => {
        setLoading(true);
        try {
            const response = await api.post('/community/cofounder-match', {
                skills: profile.skills.split(',').map(s => s.trim()),
                looking_for: profile.looking_for.split(',').map(s => s.trim()),
                timezone: profile.timezone,
                bio: profile.bio,
                industry: profile.industry
            });
            setMatches(response.data.suggested_matches || []);
        } catch (error) {
            console.error("Match failed", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900/10 to-gray-900 p-6">
            <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8">

                {/* Left: Profile Form */}
                <div className="space-y-6">
                    <div>
                        <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
                            <Users className="w-8 h-8 text-blue-400" />
                            Co-Founder Match
                        </h1>
                        <p className="text-gray-400">
                            Stop swiping. Start building. AI matches you with complementary partners.
                        </p>
                    </div>

                    <div className="bg-gray-800/40 border border-gray-700 rounded-2xl p-6 space-y-4">
                        <div>
                            <label className="block text-gray-300 text-sm mb-1">Your Skills (comma separated)</label>
                            <input
                                type="text"
                                placeholder="e.g. React, Python, Growth Hacking"
                                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                value={profile.skills}
                                onChange={(e) => setProfile({ ...profile, skills: e.target.value })}
                            />
                        </div>
                        <div>
                            <label className="block text-gray-300 text-sm mb-1">Looking For (comma separated)</label>
                            <input
                                type="text"
                                placeholder="e.g. Technical CTO, Sales Lead, Designer"
                                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                value={profile.looking_for}
                                onChange={(e) => setProfile({ ...profile, looking_for: e.target.value })}
                            />
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-gray-300 text-sm mb-1">Timezone</label>
                                <input
                                    type="text"
                                    placeholder="e.g. EST, UTC+1"
                                    className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white outline-none"
                                    value={profile.timezone}
                                    onChange={(e) => setProfile({ ...profile, timezone: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="block text-gray-300 text-sm mb-1">Industry</label>
                                <input
                                    type="text"
                                    placeholder="e.g. Fintech, AI"
                                    className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white outline-none"
                                    value={profile.industry}
                                    onChange={(e) => setProfile({ ...profile, industry: e.target.value })}
                                />
                            </div>
                        </div>
                        <div>
                            <label className="block text-gray-300 text-sm mb-1">Short Bio</label>
                            <textarea
                                placeholder="What have you built? What drives you?"
                                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white outline-none h-24"
                                value={profile.bio}
                                onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
                            />
                        </div>

                        <button
                            onClick={handleMatch}
                            disabled={loading}
                            className={`w-full py-3 rounded-xl font-bold text-white transition flex items-center justify-center gap-2 ${loading ? 'bg-blue-600/50 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-500 shadow-lg shadow-blue-900/20'
                                }`}
                        >
                            {loading ? (
                                <>
                                    <Zap className="w-5 h-5 animate-spin" /> Analyzing 5M+ Profiles...
                                </>
                            ) : (
                                <>
                                    <Zap className="w-5 h-5" /> Find My Co-Founder
                                </>
                            )}
                        </button>
                    </div>
                </div>

                {/* Right: Matches */}
                <div className="space-y-6">
                    <h2 className="text-xl font-bold text-white flex items-center gap-2">
                        <Heart className="w-5 h-5 text-red-500" />
                        Top AI Matches
                    </h2>

                    {matches.length === 0 && !loading && (
                        <div className="h-full flex flex-col items-center justify-center text-gray-500 border-2 border-dashed border-gray-800 rounded-2xl p-8 min-h-[400px]">
                            <Users className="w-16 h-16 mb-4 opacity-20" />
                            <p>Fill out your profile to find matches.</p>
                        </div>
                    )}

                    <div className="space-y-4">
                        {matches.map((match) => (
                            <div key={match.id} className="bg-gray-800/60 border border-gray-700/50 hover:border-blue-500/50 transition rounded-xl p-5 group relative overflow-hidden">
                                <div className="absolute top-0 right-0 p-4 opacity-50 text-6xl font-bold text-gray-700 pointer-events-none group-hover:text-blue-900/20 transition">
                                    {match.match_score}%
                                </div>

                                <div className="relative z-10">
                                    <div className="flex items-start justify-between mb-2">
                                        <div>
                                            <h3 className="text-lg font-bold text-white">{match.name}</h3>
                                            <p className="text-blue-400 font-medium text-sm">{match.role}</p>
                                        </div>
                                        <div className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-xs font-bold ring-1 ring-green-500/30">
                                            {match.match_score}% Match
                                        </div>
                                    </div>

                                    <p className="text-gray-300 text-sm mb-4 leading-relaxed">
                                        {match.match_reason}
                                    </p>

                                    <p className="text-gray-500 italic text-xs mb-3">"{match.bio}"</p>

                                    <div className="flex flex-wrap gap-2 mb-4">
                                        {match.skills.map(skill => (
                                            <span key={skill} className="px-2 py-1 bg-gray-700 rounded text-xs text-gray-300">
                                                {skill}
                                            </span>
                                        ))}
                                    </div>

                                    <button className="w-full py-2 bg-white/5 hover:bg-white/10 text-white text-sm font-semibold rounded-lg border border-white/10 transition flex items-center justify-center gap-2 group-hover:bg-blue-600 group-hover:border-blue-500">
                                        <Briefcase className="w-4 h-4" /> Connect & Build
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

            </div>
        </div>
    );
}
