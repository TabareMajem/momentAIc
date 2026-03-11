import React from "react";
import { Link } from "react-router-dom";
import { ChevronRight, Calendar, ArrowLeft, BookOpen, Clock, Tag, Globe, Filter } from "lucide-react";
import { BLOG_POSTS, BlogPost } from "../lib/blogData";

export default function Blog() {
    const [expandedId, setExpandedId] = React.useState<string | null>(() => {
        const hash = window.location.hash.replace('#', '');
        return BLOG_POSTS.find(p => p.id === hash) ? hash : null;
    });
    const [activeLang, setActiveLang] = React.useState<string | null>(null);

    // Extract unique languages
    const languages = Array.from(new Set(BLOG_POSTS.map(p => p.language).filter(Boolean))) as string[];

    // Filter posts
    const filteredPosts = BLOG_POSTS.filter(p => !activeLang || p.language === activeLang);

    // Dynamic SEO Management
    React.useEffect(() => {
        // Sync URL Hash
        if (expandedId) {
            window.history.replaceState(null, '', `#${expandedId}`);
        } else {
            window.history.replaceState(null, '', window.location.pathname);
            document.title = "MomentAIc Log | B2B Autonomous AI & Venture Disruption";
        }

        // Schema.org JSON-LD & Meta Tags
        let schemaScriptContent = '';
        if (expandedId) {
            const post = BLOG_POSTS.find(p => p.id === expandedId);
            if (post) {
                document.title = `${post.title} | MomentAIc`;

                // Try to update meta description if it exists, otherwise create it
                let metaDesc = document.querySelector('meta[name="description"]');
                if (!metaDesc) {
                    metaDesc = document.createElement('meta');
                    metaDesc.setAttribute('name', 'description');
                    document.head.appendChild(metaDesc);
                }
                metaDesc.setAttribute('content', post.excerpt);

                const schemaData = {
                    "@context": "https://schema.org",
                    "@type": "Article",
                    "headline": post.title,
                    "datePublished": post.date,
                    "description": post.excerpt,
                    "inLanguage": post.language || "en",
                    "author": {
                        "@type": "Organization",
                        "name": "MomentAIc",
                        "url": "https://momentaic.com"
                    }
                };
                schemaScriptContent = JSON.stringify(schemaData);
            }
        } else {
            // Reset meta desc
            let metaDesc = document.querySelector('meta[name="description"]');
            if (metaDesc) metaDesc.setAttribute('content', 'Momentaic deploys Yokaizen\'s AI companion technology for Enterprise Brands. Empowering global founders with Swarm Intelligence.');
        }

        // Manage injected JSON-LD script tag
        let scriptTag = document.getElementById('json-ld-article-schema');
        if (schemaScriptContent) {
            if (!scriptTag) {
                scriptTag = document.createElement('script');
                scriptTag.id = 'json-ld-article-schema';
                scriptTag.setAttribute('type', 'application/ld+json');
                document.head.appendChild(scriptTag);
            }
            scriptTag.textContent = schemaScriptContent;
        } else if (scriptTag) {
            scriptTag.remove();
        }
    }, [expandedId]);
    return (
        <div className="min-h-screen bg-[#050505] text-white selection:bg-[#00e5ff] selection:text-black font-sans">
            {/* Navigation */}
            <nav className="fixed top-0 left-0 right-0 z-50 border-b border-white/5 bg-[#050505]/80 backdrop-blur-md">
                <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
                    <Link to="/" className="flex items-center gap-2 group">
                        <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center border border-white/10 group-hover:border-white/20 transition-all">
                            <ArrowLeft size={16} className="text-white/70 group-hover:text-white transition-colors" />
                        </div>
                        <span className="font-mono text-xs tracking-widest text-white/70 uppercase group-hover:text-white transition-colors">
                            Back to Home
                        </span>
                    </Link>

                    <div className="flex items-center gap-3">
                        <div className="w-2 h-2 rounded-full bg-[#00ff88] animate-pulse" />
                        <span className="font-mono text-xs tracking-[0.2em] uppercase text-white/50">MomentAIc Log</span>
                    </div>
                </div>
            </nav>

            <main className="pt-32 pb-20 max-w-3xl mx-auto px-6">
                <article className="prose prose-invert prose-lg max-w-none">
                    {/* Header */}
                    <header className="mb-16">
                        <div className="flex items-center gap-4 text-xs font-mono tracking-widest text-white/40 uppercase mb-8">
                            <span className="flex items-center gap-2">
                                <Calendar size={14} />
                                Published on: momentaic.com/blog
                            </span>
                        </div>
                        <h1 className="text-4xl md:text-5xl lg:text-6xl font-black tracking-tight leading-[1.1] mb-6 font-['Space_Grotesk'] text-transparent bg-clip-text bg-gradient-to-r from-white to-white/60">
                            How Momentaic Deploys Yokaizen's AI Companion Technology for Enterprise Brands
                        </h1>
                        <p className="text-xl text-white/50 leading-relaxed">
                            Momentaic is the enterprise arm of the Yokaizen ecosystem. While Yokaizen serves consumers and Yokaizen Campus serves universities, Momentaic brings the same AI companion technology to Fortune 500 brands.
                        </p>
                    </header>

                    <hr className="border-t border-white/10 my-16" />

                    {/* Content */}
                    <section className="space-y-12">
                        <div>
                            <h2 className="text-2xl font-bold font-['Space_Grotesk'] tracking-tight mb-8 flex items-center gap-3">
                                <div className="w-6 h-[2px] bg-[#00e5ff]" />
                                Primary Use Cases
                            </h2>

                            <div className="grid gap-6">
                                {/* Use Case 1 */}
                                <div className="p-8 rounded-2xl bg-white/[0.02] border border-white/[0.05] hover:border-white/10 transition-colors">
                                    <h3 className="text-lg font-bold text-[#00e5ff] mb-3 flex items-center gap-2">
                                        <span className="font-mono text-xs bg-[#00e5ff]/10 px-2 py-1 rounded text-[#00e5ff]">01</span>
                                        Employee Wellness
                                    </h3>
                                    <p className="text-white/70 text-sm md:text-base leading-relaxed">
                                        A custom AI companion for corporate teams, powered by AgentForge AI, that checks in daily and offers micro-quests tailored to work stress.
                                    </p>
                                </div>

                                {/* Use Case 2 */}
                                <div className="p-8 rounded-2xl bg-white/[0.02] border border-white/[0.05] hover:border-white/10 transition-colors">
                                    <h3 className="text-lg font-bold text-[#7c4dff] mb-3 flex items-center gap-2">
                                        <span className="font-mono text-xs bg-[#7c4dff]/10 px-2 py-1 rounded text-[#7c4dff]">02</span>
                                        Customer Engagement
                                    </h3>
                                    <p className="text-white/70 text-sm md:text-base leading-relaxed">
                                        Brands deploy interactive BondQuest-style loyalty quests that replace traditional points programs with highly engaging, narrative-driven experiences.
                                    </p>
                                </div>

                                {/* Use Case 3 */}
                                <div className="p-8 rounded-2xl bg-white/[0.02] border border-white/[0.05] hover:border-white/10 transition-colors">
                                    <h3 className="text-lg font-bold text-[#ff6b35] mb-3 flex items-center gap-2">
                                        <span className="font-mono text-xs bg-[#ff6b35]/10 px-2 py-1 rounded text-[#ff6b35]">03</span>
                                        Content Creation
                                    </h3>
                                    <p className="text-white/70 text-sm md:text-base leading-relaxed">
                                        Marketing teams use Symbiotask to generate branded visual content at scale, from storyboards to social media assets, orchestrating multiple AI specialists.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="p-8 rounded-2xl bg-gradient-to-br from-white/5 to-transparent border border-white/10">
                            <p className="text-white/80 leading-relaxed font-medium">
                                The technology stack is identical to what powers the consumer Yokaizen experience — zero-latency voice, biometric integration, and emotionally intelligent dialogue — but wrapped in enterprise-grade security, SSO, and compliance frameworks.
                            </p>
                        </div>

                        <div className="pt-8 border-t border-white/10">
                            <div className="text-xs font-mono tracking-widest text-white/40 uppercase mb-6">Explore our consumer products:</div>
                            <div className="flex flex-wrap gap-4">
                                {["Yokaizen", "Otaku Hub", "Mangaka Studio"].map((link, i) => (
                                    <a key={i} href="#" className="flex items-center gap-2 px-5 py-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 transition-all text-sm font-medium text-white/80 group cursor-pointer">
                                        {link}
                                        <ChevronRight size={14} className="text-white/30 group-hover:text-white transition-colors group-hover:translate-x-1" />
                                    </a>
                                ))}
                            </div>
                        </div>
                    </section>

                    <hr className="border-t border-white/10 my-20" />

                    {/* Blog Feed */}
                    <section>
                        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12">
                            <div>
                                <h2 className="text-3xl font-bold font-['Space_Grotesk'] tracking-tight mb-2">Latest Intelligence</h2>
                                <div className="text-xs font-mono text-white/40 uppercase tracking-widest">{filteredPosts.length} Articles Available</div>
                            </div>

                            {/* Filters */}
                            {languages.length > 0 && (
                                <div className="flex flex-wrap items-center gap-2">
                                    <div className="text-[10px] font-mono text-white/40 uppercase tracking-widest mr-2 flex items-center gap-1">
                                        <Globe size={12} /> Language
                                    </div>
                                    <button
                                        onClick={() => setActiveLang(null)}
                                        className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${!activeLang ? 'bg-[#00e5ff]/20 text-[#00e5ff] border border-[#00e5ff]/30' : 'bg-white/5 text-white/50 border border-white/10 hover:bg-white/10 hover:text-white'}`}
                                    >
                                        ALL
                                    </button>
                                    {languages.map(lang => (
                                        <button
                                            key={lang}
                                            onClick={() => setActiveLang(lang)}
                                            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${activeLang === lang ? 'bg-[#ff6b35]/20 text-[#ff6b35] border border-[#ff6b35]/30' : 'bg-white/5 text-white/50 border border-white/10 hover:bg-white/10 hover:text-white'}`}
                                        >
                                            {lang}
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>

                        <div className="grid gap-8">
                            {filteredPosts.map(post => (
                                <article
                                    key={post.id}
                                    className="p-8 rounded-2xl bg-white/[0.02] border border-white/[0.05] hover:border-white/10 transition-all duration-300 relative overflow-hidden group"
                                >
                                    {/* Accent gradient hover */}
                                    <div className="absolute inset-0 bg-gradient-to-br from-white/[0.03] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />

                                    <div className="relative z-10">
                                        <div className="flex flex-wrap items-center gap-4 text-xs font-mono text-white/40 uppercase tracking-widest mb-6">
                                            <span className="flex items-center gap-1.5"><Calendar size={12} className="text-white/30" /> {post.date}</span>
                                            <span className="flex items-center gap-1.5"><Clock size={12} className="text-white/30" /> {post.readTime}</span>
                                            <span className="flex items-center gap-1.5 text-[#00e5ff] px-2 py-0.5 rounded-full bg-[#00e5ff]/10 border border-[#00e5ff]/20"><Tag size={12} /> {post.category}</span>
                                            {post.language && (
                                                <span className="flex items-center gap-1.5 text-[#ff6b35] px-2 py-0.5 rounded-full bg-[#ff6b35]/10 border border-[#ff6b35]/20">
                                                    <Globe size={12} /> {post.language}
                                                </span>
                                            )}
                                        </div>

                                        <h3 className="text-2xl font-bold font-['Space_Grotesk'] tracking-tight mb-4 text-white group-hover:text-[#00e5ff] transition-colors cursor-pointer" onClick={() => setExpandedId(expandedId === post.id ? null : post.id)}>
                                            {post.title}
                                        </h3>

                                        <p className="text-white/60 leading-relaxed mb-6 text-lg">
                                            {post.excerpt}
                                        </p>

                                        {post.tags && post.tags.length > 0 && (
                                            <div className="flex flex-wrap gap-2 mb-6">
                                                {post.tags.map(tag => (
                                                    <span key={tag} className="text-[10px] uppercase tracking-widest font-bold text-white/30 bg-white/5 px-2 py-1 rounded border border-white/10">
                                                        #{tag}
                                                    </span>
                                                ))}
                                            </div>
                                        )}

                                        {expandedId === post.id ? (
                                            <div className="mt-8 pt-8 border-t border-white/10 animate-in fade-in slide-in-from-top-4 duration-500">
                                                <div className="prose prose-invert prose-lg max-w-none text-white/80 leading-[1.8]">
                                                    {post.content.split('\\n\\n').map((paragraph, idx) => {
                                                        const isHeader = paragraph.startsWith('**') && paragraph.endsWith('**');
                                                        return isHeader ? (
                                                            <h4 key={idx} className="text-xl font-bold text-white mt-8 mb-4 font-['Space_Grotesk']">
                                                                {paragraph.replace(/\\*\\*/g, '')}
                                                            </h4>
                                                        ) : (
                                                            <p key={idx} className="mb-6">{paragraph}</p>
                                                        );
                                                    })}
                                                </div>
                                                <button
                                                    onClick={() => setExpandedId(null)}
                                                    className="mt-8 flex items-center gap-2 text-sm font-bold text-white/50 hover:text-white transition-colors"
                                                >
                                                    <BookOpen size={16} /> Close Article
                                                </button>
                                            </div>
                                        ) : (
                                            <button
                                                onClick={() => setExpandedId(post.id)}
                                                className="flex items-center gap-2 text-sm font-bold text-[#00e5ff] hover:text-[#00e5ff] transition-colors"
                                            >
                                                <BookOpen size={16} /> Read Full Strategy
                                            </button>
                                        )}
                                    </div>
                                </article>
                            ))}
                        </div>
                    </section>
                </article>
            </main>
        </div>
    );
}
