import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Logo } from '../../components/ui/Logo';
import { Button } from '../../components/ui/Button';
import { Lock, Zap, ChevronRight, Tag, Clock } from 'lucide-react';
import { getAllArticles } from '../../src/data/articles';
import { PageMeta } from '../../components/ui/PageMeta';

const IntelCard = ({ article }: { article: any }) => (
    <Link to={`/intel/${article.slug}`} className="group block border border-white/10 bg-[#0a0a0f] hover:border-purple-500/50 transition-all clip-corner-4 relative overflow-hidden flex flex-col h-full">
        {article.featuredImage && (
            <div className="w-full h-48 overflow-hidden relative">
                <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a0f] to-transparent z-10" />
                <img
                    src={article.featuredImage}
                    alt={article.title}
                    className="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-700 opacity-80"
                />
            </div>
        )}

        <div className="absolute top-4 right-4 z-20 opacity-0 group-hover:opacity-100 transition-opacity">
            <Zap className="w-5 h-5 text-purple-400" />
        </div>

        <div className="p-6 flex flex-col flex-1 relative z-20 -mt-10">
            <div className="inline-flex items-center gap-2 px-2 py-1 bg-[#0a0a0f]/90 border border-white/10 rounded text-[10px] font-mono text-purple-400 mb-4 backdrop-blur-sm self-start">
                <Tag className="w-3 h-3" />
                {article.category}
            </div>

            <h3 className="text-xl font-bold mb-3 group-hover:text-purple-300 transition-colors leading-tight">
                {article.title}
            </h3>

            <p className="text-sm text-gray-400 mb-6 flex-1 line-clamp-3">
                {article.subtitle}
            </p>

            <div className="mt-auto border-t border-white/5 pt-4 flex items-center justify-between text-xs font-mono text-gray-500">
                <span className="flex items-center gap-2"><Clock className="w-3 h-3 text-gray-600" /> {article.readTime}</span>
                <span className="group-hover:text-purple-400 transition-colors flex items-center gap-1">
                    READ <ChevronRight className="w-3 h-3" />
                </span>
            </div>
        </div>
    </Link>
);

const LockedCard = ({ title, category }: { title: string, category: string }) => (
    <div className="group block border border-white/5 bg-[#050508] p-6 clip-corner-4 relative overflow-hidden opacity-50 cursor-not-allowed h-full min-h-[300px] flex flex-col">
        <div className="font-mono text-xs text-gray-600 mb-3 flex items-center gap-2">
            <Tag className="w-3 h-3" /> {category}
        </div>
        <h3 className="text-xl font-bold mb-3 text-gray-500 line-clamp-2">{title}</h3>

        <div className="absolute inset-0 bg-black/60 flex items-center justify-center">
            <div className="bg-black border border-white/10 px-3 py-2 rounded font-mono text-xs text-gray-400 flex items-center gap-2 shadow-xl shadow-black">
                <Lock className="w-4 h-4 text-red-500/70" />
                CLEARANCE_REQUIRED
            </div>
        </div>
    </div>
);

export default function IntelHub() {
    const articles = getAllArticles();
    const categories = ['All', ...new Set(articles.map(a => a.category))];
    const [activeFilter, setActiveFilter] = useState('All');

    const filteredArticles = activeFilter === 'All'
        ? articles
        : articles.filter(a => a.category === activeFilter);

    return (
        <div className="min-h-screen bg-[#020202] text-white selection:bg-purple-500 font-sans">
            <PageMeta
                title="Intel Hub | Mission Intelligence for Autonomous Startups"
                description="Declassified playbooks, architecture patterns, and growth strategies for operating an Autonomous Startup using MomentAIc agents."
            />
            <nav className="fixed top-0 w-full z-40 bg-[#020202]/90 backdrop-blur-md border-b border-white/5">
                <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
                    <Link to="/">
                        <Logo collapsed={false} />
                    </Link>
                    <div className="flex gap-4">
                        <Link to="/signup">
                            <Button className="h-8 px-4 text-xs font-mono bg-white text-black hover:bg-purple-500 hover:text-white transition-colors font-bold clip-corner-4">
                                ACCESS_TERMINAL
                            </Button>
                        </Link>
                    </div>
                </div>
            </nav>

            <main className="pt-32 pb-24 px-6 max-w-7xl mx-auto relative z-10">
                <div className="text-center mb-16">
                    <div className="inline-block px-3 py-1 border border-white/10 text-purple-400/70 font-mono text-xs rounded mb-6 bg-purple-900/10">
                        PUBLIC_ACCESS_TERMINAL // INTEL
                    </div>
                    <h1 className="text-5xl md:text-7xl font-black mb-6 tracking-tighter bg-clip-text text-transparent bg-gradient-to-br from-white to-gray-500">
                        Mission Intelligence
                    </h1>
                    <p className="text-gray-400 max-w-2xl mx-auto text-lg leading-relaxed">
                        Declassified playbooks, architecture patterns, and growth strategies for operating an Autonomous Startup.
                    </p>
                </div>

                {/* Filters */}
                <div className="flex flex-wrap items-center justify-center gap-3 mb-12">
                    {categories.map(cat => (
                        <button
                            key={cat}
                            onClick={() => setActiveFilter(cat)}
                            className={`px-4 py-2 text-xs font-mono rounded-full border transition-all ${activeFilter === cat
                                ? 'bg-purple-600 border-purple-500 text-white shadow-lg shadow-purple-900/50'
                                : 'bg-white/5 border-white/10 text-gray-400 hover:bg-white/10 hover:text-white'
                                }`}
                        >
                            {cat}
                        </button>
                    ))}
                </div>

                {/* Article Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {filteredArticles.map(article => (
                        <IntelCard key={article.slug} article={article} />
                    ))}

                    {/* Placeholder Locked Intel for Vibe */}
                    {activeFilter === 'All' && (
                        <>
                            <LockedCard title="Zero-Touch DevOps Architecture" category="INFRASTRUCTURE" />
                            <LockedCard title="Automated Legal Compliance" category="LEGAL_OPS" />
                        </>
                    )}
                </div>
            </main>
        </div>
    );
}
