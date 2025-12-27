import React, { useState } from 'react';
import { Heart, Code, Globe, Users, Zap, DollarSign, Github, Star, GitPullRequest, Gift, Rocket, ArrowRight } from 'lucide-react';

export default function MissionPage() {
    const [activeTab, setActiveTab] = useState<'founders' | 'contributors' | 'investors'>('founders');

    const pricingTiers = [
        {
            name: 'Starter',
            price: 9,
            description: 'For solo founders testing the waters',
            features: [
                'All 16 AI agents',
                '5 integrations',
                'Basic triggers',
                'Community support',
                'Traction score',
            ],
            cta: 'Start Building',
            popular: false,
        },
        {
            name: 'Pro',
            price: 19,
            description: 'For serious builders ready to scale',
            features: [
                'Everything in Starter',
                'All 42+ integrations',
                'Unlimited triggers',
                'Browser agent',
                'Deep Research',
                'Priority AI models',
                'Leaderboard featured',
            ],
            cta: 'Go Pro',
            popular: true,
        },
        {
            name: 'Scale',
            price: 99,
            description: 'For funded startups going big',
            features: [
                'Everything in Pro',
                'Custom agents',
                'API access',
                'White-label option',
                'Dedicated support',
                'Team seats (5)',
                'Investment memo generator',
            ],
            cta: 'Scale Up',
            popular: false,
        },
        {
            name: 'Accelerator',
            price: 0,
            priceLabel: 'Revenue Share',
            description: 'Anti-YC: Performance-based, not equity grab',
            features: [
                'Everything in Scale',
                'Human mentor network',
                'Investor introductions',
                'Featured showcase',
                '1% equity OR 5% revenue for 12mo',
                'No predatory terms',
            ],
            cta: 'Apply Now',
            popular: false,
            special: true,
        },
    ];

    const contributionRewards = [
        { type: 'Major Feature', reward: 'Free Pro for life', icon: '🚀' },
        { type: 'New Integration', reward: '$500 + Pro for 1 year', icon: '🔌' },
        { type: 'Bug Fix', reward: 'Pro for 3 months', icon: '🐛' },
        { type: 'Documentation', reward: 'Pro for 1 month', icon: '📚' },
    ];

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900/20 to-gray-900">
            {/* Hero */}
            <div className="relative px-6 py-20 text-center">
                <div className="absolute inset-0 overflow-hidden">
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-purple-500/20 rounded-full blur-[120px]"></div>
                </div>

                <div className="relative z-10 max-w-4xl mx-auto">
                    <h1 className="text-5xl md:text-7xl font-black text-white mb-6">
                        The YC Monopoly<br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-500 to-cyan-400">
                            Ends Here.
                        </span>
                    </h1>
                    <p className="text-xl text-gray-300 max-w-2xl mx-auto mb-8">
                        Open source AI co-founders for every entrepreneur. From Manila to Lima to Lagos.
                        Build billion-dollar companies from your sofa.
                    </p>

                    {/* Dual CTA */}
                    <div className="flex flex-wrap justify-center gap-4 mb-12">
                        <button
                            onClick={() => setActiveTab('founders')}
                            className={`px-6 py-3 rounded-xl font-bold transition ${activeTab === 'founders'
                                    ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                                    : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                                }`}
                        >
                            🚀 I'm a Founder
                        </button>
                        <button
                            onClick={() => setActiveTab('contributors')}
                            className={`px-6 py-3 rounded-xl font-bold transition ${activeTab === 'contributors'
                                    ? 'bg-gradient-to-r from-green-600 to-emerald-600 text-white'
                                    : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                                }`}
                        >
                            💻 I Want to Contribute
                        </button>
                        <button
                            onClick={() => setActiveTab('investors')}
                            className={`px-6 py-3 rounded-xl font-bold transition ${activeTab === 'investors'
                                    ? 'bg-gradient-to-r from-yellow-600 to-orange-600 text-white'
                                    : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                                }`}
                        >
                            💰 I'm an Investor
                        </button>
                    </div>
                </div>
            </div>

            {/* Founders Tab */}
            {activeTab === 'founders' && (
                <div className="px-6 pb-20 max-w-7xl mx-auto">
                    <h2 className="text-3xl font-bold text-white text-center mb-12">
                        Pricing for Builders 🔨
                    </h2>

                    <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                        {pricingTiers.map((tier) => (
                            <div
                                key={tier.name}
                                className={`relative rounded-2xl p-6 ${tier.special
                                        ? 'bg-gradient-to-br from-purple-900/50 to-pink-900/50 border-2 border-purple-500'
                                        : tier.popular
                                            ? 'bg-gradient-to-br from-blue-900/50 to-cyan-900/50 border-2 border-cyan-500'
                                            : 'bg-gray-800/50 border border-gray-700'
                                    }`}
                            >
                                {tier.popular && (
                                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-cyan-500 text-black text-xs font-bold rounded-full">
                                        MOST POPULAR
                                    </div>
                                )}
                                {tier.special && (
                                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-purple-500 text-white text-xs font-bold rounded-full">
                                        ANTI-YC
                                    </div>
                                )}

                                <h3 className="text-xl font-bold text-white mb-2">{tier.name}</h3>
                                <p className="text-gray-400 text-sm mb-4">{tier.description}</p>

                                <div className="mb-6">
                                    {tier.priceLabel ? (
                                        <span className="text-2xl font-bold text-purple-400">{tier.priceLabel}</span>
                                    ) : (
                                        <>
                                            <span className="text-4xl font-bold text-white">${tier.price}</span>
                                            <span className="text-gray-500">/mo</span>
                                        </>
                                    )}
                                </div>

                                <ul className="space-y-3 mb-6">
                                    {tier.features.map((feature, i) => (
                                        <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                                            <span className="text-green-400 mt-0.5">✓</span>
                                            {feature}
                                        </li>
                                    ))}
                                </ul>

                                <button className={`w-full py-3 rounded-xl font-bold transition ${tier.special
                                        ? 'bg-purple-600 hover:bg-purple-700 text-white'
                                        : tier.popular
                                            ? 'bg-cyan-600 hover:bg-cyan-700 text-white'
                                            : 'bg-gray-700 hover:bg-gray-600 text-white'
                                    }`}>
                                    {tier.cta} <ArrowRight className="inline w-4 h-4 ml-1" />
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Contributors Tab */}
            {activeTab === 'contributors' && (
                <div className="px-6 pb-20 max-w-5xl mx-auto">
                    <div className="text-center mb-12">
                        <h2 className="text-3xl font-bold text-white mb-4">
                            Open Source + Rewards 🎁
                        </h2>
                        <p className="text-gray-400 max-w-2xl mx-auto">
                            MomentAIc is open source. Contribute code, integrations, or docs and get rewarded.
                        </p>
                    </div>

                    {/* Contribution Rewards */}
                    <div className="grid md:grid-cols-2 gap-6 mb-12">
                        {contributionRewards.map((item) => (
                            <div key={item.type} className="bg-gray-800/50 border border-gray-700 rounded-xl p-6 flex items-center gap-4">
                                <span className="text-4xl">{item.icon}</span>
                                <div>
                                    <h3 className="text-white font-semibold">{item.type}</h3>
                                    <p className="text-green-400 text-sm">{item.reward}</p>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Self-Host Guide Preview */}
                    <div className="bg-gray-800/30 border border-gray-700 rounded-2xl p-8">
                        <div className="flex items-center gap-3 mb-4">
                            <Github className="w-6 h-6 text-white" />
                            <h3 className="text-xl font-bold text-white">Self-Host MomentAIc</h3>
                        </div>

                        <pre className="bg-black/50 rounded-xl p-4 text-sm text-gray-300 overflow-x-auto mb-6">
                            {`# Clone and run
git clone https://github.com/momentaic/momentaic.git
cd momentaic
docker-compose up -d

# That's it! Visit http://localhost:8000`}
                        </pre>

                        <div className="flex flex-wrap gap-4">
                            <a href="https://github.com/momentaic/momentaic" className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition">
                                <Github className="w-4 h-4" /> View on GitHub
                            </a>
                            <a href="#" className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition">
                                <Star className="w-4 h-4" /> Star the Repo
                            </a>
                            <a href="#" className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition">
                                <GitPullRequest className="w-4 h-4" /> Contribute
                            </a>
                        </div>
                    </div>
                </div>
            )}

            {/* Investors Tab */}
            {activeTab === 'investors' && (
                <div className="px-6 pb-20 max-w-5xl mx-auto">
                    <div className="text-center mb-12">
                        <h2 className="text-3xl font-bold text-white mb-4">
                            Invest in Real Traction 📈
                        </h2>
                        <p className="text-gray-400 max-w-2xl mx-auto">
                            Discover startups ranked by verified metrics. No pedigree filters. Pure performance.
                        </p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-6 mb-12">
                        <div className="bg-gradient-to-br from-blue-900/30 to-cyan-900/30 border border-blue-500/30 rounded-xl p-6 text-center">
                            <div className="text-4xl mb-3">🏆</div>
                            <h3 className="text-white font-semibold mb-2">Public Leaderboard</h3>
                            <p className="text-gray-400 text-sm">Browse startups ranked by real MRR, growth, and retention</p>
                        </div>
                        <div className="bg-gradient-to-br from-green-900/30 to-emerald-900/30 border border-green-500/30 rounded-xl p-6 text-center">
                            <div className="text-4xl mb-3">✅</div>
                            <h3 className="text-white font-semibold mb-2">Verified Metrics</h3>
                            <p className="text-gray-400 text-sm">Metrics pulled directly from connected integrations</p>
                        </div>
                        <div className="bg-gradient-to-br from-purple-900/30 to-pink-900/30 border border-purple-500/30 rounded-xl p-6 text-center">
                            <div className="text-4xl mb-3">📄</div>
                            <h3 className="text-white font-semibold mb-2">AI Investment Memos</h3>
                            <p className="text-gray-400 text-sm">Auto-generated VC-quality memos for top startups</p>
                        </div>
                    </div>

                    <div className="bg-gray-800/30 border border-gray-700 rounded-2xl p-8 text-center">
                        <h3 className="text-2xl font-bold text-white mb-4">Ready to Discover?</h3>
                        <p className="text-gray-400 mb-6 max-w-xl mx-auto">
                            Join MomentAIc as an investor to browse the leaderboard, filter by category,
                            and connect directly with high-traction founders.
                        </p>
                        <button className="px-8 py-4 bg-gradient-to-r from-yellow-600 to-orange-600 text-white font-bold rounded-xl hover:opacity-90 transition">
                            Apply for Investor Access <ArrowRight className="inline w-5 h-5 ml-2" />
                        </button>
                    </div>
                </div>
            )}

            {/* Global Mission Banner */}
            <div className="px-6 pb-20">
                <div className="max-w-5xl mx-auto bg-gradient-to-r from-purple-900/30 via-blue-900/30 to-cyan-900/30 border border-purple-500/20 rounded-3xl p-12 text-center">
                    <div className="flex justify-center gap-4 mb-6 text-4xl">
                        <span>🇵🇭</span>
                        <span>🇵🇪</span>
                        <span>🇳🇬</span>
                        <span>🇮🇳</span>
                        <span>🇧🇷</span>
                        <span>🇮🇩</span>
                        <span>🌍</span>
                    </div>
                    <h3 className="text-3xl font-bold text-white mb-4">
                        From Any Sofa, to Fortune 500
                    </h3>
                    <p className="text-gray-300 max-w-2xl mx-auto">
                        We believe the next generation of billion-dollar companies will be built by
                        founders who never got a YC interview. MomentAIc is their weapon.
                    </p>
                </div>
            </div>
        </div>
    );
}
