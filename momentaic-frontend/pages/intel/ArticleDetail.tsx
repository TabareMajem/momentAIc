import React, { useEffect, useState } from 'react';
import { useParams, Navigate, Link } from 'react-router-dom';
import { ArrowLeft, Clock, Calendar, Share2, Tag, ChevronRight } from 'lucide-react';
import { getArticleBySlug } from '../../src/data/articles';
import { Logo } from '../../components/ui/Logo';

// Add marked for markdown processing. (Needs `npm i marked` if not installed, falling back to simple render otherwise)
// For this environment, we'll use a basic pre-rendered HTML injection since content is static inside articles.ts 
// with simple tags, or we assume the content is safe HTML.

export default function ArticleDetail() {
    const { slug } = useParams<{ slug: string }>();
    const article = getArticleBySlug(slug || '');

    useEffect(() => {
        if (article) {
            document.title = `${article.title} | MomentAIc Intel Hub`;

            // Basic meta tag injection for SEO
            let metaDesc = document.querySelector('meta[name="description"]');
            if (!metaDesc) {
                metaDesc = document.createElement('meta');
                metaDesc.setAttribute('name', 'description');
                document.head.appendChild(metaDesc);
            }
            metaDesc.setAttribute('content', article.metaDescription);
        }
    }, [article]);

    if (!article) {
        return <Navigate to="/intel" replace />;
    }

    // A very simple markdown to HTML converter for basic tags
    const renderContent = (content: string) => {
        let html = content
            .replace(/^# (.*$)/gim, '<h1 class="text-3xl md:text-5xl font-bold mt-12 mb-6 text-white glitched-text">$1</h1>')
            .replace(/^## (.*$)/gim, '<h2 class="text-2xl md:text-3xl font-bold mt-10 mb-5 text-gray-100">$1</h2>')
            .replace(/^### (.*$)/gim, '<h3 class="text-xl md:text-2xl font-bold mt-8 mb-4 text-purple-400">$1</h3>')
            .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
            .replace(/\*(.*)\*/gim, '<em>$1</em>')
            .replace(/^\- (.*$)/gim, '<li class="ml-6 mb-2 list-disc marker:text-purple-500">$1</li>')
            .replace(/`(.*?)`/gim, '<code class="bg-purple-900/30 text-purple-300 px-1.5 py-0.5 rounded text-sm font-mono border border-purple-500/20">$1</code>')
            .replace(/^\d+\.\s+(.*$)/gim, '<li class="ml-6 mb-2 list-decimal marker:text-purple-500 font-bold text-white"><span class="font-normal text-gray-300">$1</span></li>')
            .split('\\n\\n').join('</p><p class="mb-6 text-gray-300 leading-relaxed text-lg">');

        return <div className="prose prose-invert prose-purple max-w-none" dangerouslySetInnerHTML={{ __html: `<p class="mb-6 text-gray-300 leading-relaxed text-lg">${html}</p>` }} />;
    };

    return (
        <div className="min-h-screen bg-[#020202] text-white selection:bg-purple-500/30 font-sans">
            {/* Global Background */}
            <div className="fixed inset-0 pointer-events-none z-0 bg-transparent opacity-[0.03] mix-blend-overlay" />
            <div className="fixed top-0 left-0 w-full h-1 bg-gradient-to-r from-purple-600 via-pink-500 to-purple-600 z-50 animate-pulse-slow" />

            {/* Navigation */}
            <nav className="fixed top-0 w-full z-40 bg-[#020202]/80 backdrop-blur-md border-b border-white/5">
                <div className="max-w-4xl mx-auto px-6 h-16 flex items-center justify-between">
                    <Link to="/" className="flex items-center gap-4 hover:opacity-80 transition-opacity">
                        <Logo collapsed={false} />
                    </Link>
                    <div className="flex items-center gap-4 text-sm font-mono tracking-widest">
                        <Link to="/intel" className="text-gray-400 hover:text-purple-400 transition-colors flex items-center gap-2">
                            <ArrowLeft className="w-4 h-4" /> REAR VIEW
                        </Link>
                    </div>
                </div>
            </nav>

            {/* Main Content Area */}
            <main className="relative z-10 pt-32 pb-24 px-6">
                <article className="max-w-3xl mx-auto">

                    {/* Breadcrumbs */}
                    <div className="flex items-center gap-2 text-xs font-mono tracking-wider text-gray-500 mb-8 overflow-x-auto whitespace-nowrap hide-scrollbar">
                        <Link to="/" className="hover:text-purple-400">HOME</Link>
                        <ChevronRight className="w-3 h-3" />
                        <Link to="/intel" className="hover:text-purple-400">INTEL HUB</Link>
                        <ChevronRight className="w-3 h-3" />
                        <span className="text-purple-400 uppercase">{article.category}</span>
                    </div>

                    {/* Header */}
                    <header className="mb-12">
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-400 text-xs font-mono mb-6">
                            <Tag className="w-3 h-3" />
                            {article.category}
                        </div>

                        <h1 className="text-4xl md:text-6xl font-black tracking-tight mb-6 bg-clip-text text-transparent bg-gradient-to-br from-white to-gray-400">
                            {article.title}
                        </h1>

                        <p className="text-xl md:text-2xl text-gray-400 font-light leading-relaxed mb-8 border-l-4 border-purple-500 pl-6">
                            {article.subtitle}
                        </p>

                        <div className="flex flex-wrap items-center gap-6 text-sm text-gray-500 font-mono border-t border-b border-white/10 py-6">
                            <div className="flex items-center gap-2 text-gray-300">
                                <div className="w-8 h-8 rounded-full border border-purple-500/30 overflow-hidden bg-purple-900/20 flex items-center justify-center text-purple-400">
                                    {article.author.charAt(0)}
                                </div>
                                <span>{article.author}</span>
                            </div>
                            <div className="w-1 h-1 rounded-full bg-gray-600 hidden md:block" />
                            <div className="flex items-center gap-2">
                                <Calendar className="w-4 h-4" />
                                {article.date}
                            </div>
                            <div className="w-1 h-1 rounded-full bg-gray-600 hidden md:block" />
                            <div className="flex items-center gap-2">
                                <Clock className="w-4 h-4 text-purple-400" />
                                <span className="text-purple-400">{article.readTime}</span>
                            </div>
                        </div>
                    </header>

                    {/* Featured Image */}
                    {article.featuredImage && (
                        <div className="relative w-full aspect-video rounded-2xl overflow-hidden mb-16 border border-white/10 shadow-2xl shadow-purple-900/20 group">
                            <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent z-10" />
                            <img
                                src={article.featuredImage}
                                alt={article.title}
                                className="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-700"
                            />
                            <div className="absolute bottom-6 left-6 z-20 font-mono text-xs text-white/50 tracking-widest uppercase">
                                FIG 1.0 — {article.category} MODULE
                            </div>
                        </div>
                    )}

                    {/* Article Body */}
                    <div className="article-body">
                        {renderContent(article.content)}
                    </div>

                    {/* Footer Actions */}
                    <footer className="mt-20 pt-10 border-t border-white/10">
                        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
                            <div className="flex gap-2 flex-wrap">
                                {article.keywords.map((kw, i) => (
                                    <span key={i} className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-xs font-mono text-gray-400 hover:text-white hover:border-white/30 transition-colors cursor-pointer">
                                        #{kw}
                                    </span>
                                ))}
                            </div>
                            <button className="flex items-center gap-2 px-6 py-3 bg-purple-600/20 border border-purple-500/50 hover:bg-purple-600 text-purple-400 hover:text-white rounded-lg transition-all font-mono text-sm tracking-widest shrink-0">
                                <Share2 className="w-4 h-4" />
                                SHARE_INTEL
                            </button>
                        </div>
                    </footer>
                </article>
            </main>
        </div>
    );
}
