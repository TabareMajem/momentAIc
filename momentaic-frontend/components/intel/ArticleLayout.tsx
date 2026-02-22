import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { ArrowLeft, Share2, Eye, Shield, Terminal } from 'lucide-react';
import { Logo } from '../../components/ui/Logo';

export const ArticleLayout = ({ title, category, date, children }: { title: string, category: string, date: string, children: React.ReactNode }) => {
    const [readMode, setReadMode] = useState(false);

    return (
        <div className={`min-h-screen bg-[#020202] text-white selection:bg-purple-500 font-sans ${readMode ? 'tracking-normal' : 'tracking-tight'}`}>
            {/* Navbar */}
            <nav className="fixed top-0 w-full z-40 bg-[#020202]/90 backdrop-blur-md border-b border-white/5">
                <div className="max-w-4xl mx-auto px-6 h-16 flex items-center justify-between">
                    <Link to="/intel">
                        <Button variant="ghost" className="text-gray-400 hover:text-white font-mono text-xs">
                            <ArrowLeft className="w-4 h-4 mr-2" />
                            BACK_TO_INTEL
                        </Button>
                    </Link>
                    <Logo collapsed={true} />
                    <div className="flex gap-2">
                        <button
                            onClick={() => setReadMode(!readMode)}
                            className={`p-2 rounded border ${readMode ? 'bg-white text-black border-white' : 'bg-transparent text-gray-400 border-white/10'}`}
                        >
                            <Eye className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </nav>

            <main className="pt-32 pb-24 px-6">
                <article className="max-w-3xl mx-auto">
                    {/* Header */}
                    <div className="mb-12 text-center">
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-purple-500/30 bg-purple-500/10 text-purple-400 font-mono text-xs mb-6">
                            <Shield className="w-3 h-3" />
                            INTEL_CLASSIFIED // {category.toUpperCase()}
                        </div>
                        <h1 className="text-4xl md:text-6xl font-black mb-6 leading-tight glitch-text tracking-tighter">{title}</h1>
                        <div className="flex items-center justify-center gap-6 text-sm text-gray-500 font-mono">
                            <span>AUTHOR: MOMENTAIC_CORE</span>
                            <span>DATE: {date}</span>
                            <span>READ_TIME: 4 MIN</span>
                        </div>
                    </div>

                    {/* Content */}
                    <div className={`prose prose-invert prose-lg max-w-none ${readMode ? 'font-serif' : 'font-sans'}`}>
                        {children}
                    </div>

                    {/* Footer CTA */}
                    <div className="mt-16 p-8 border border-white/10 rounded-xl bg-white/[0.02] text-center clip-corner-4">
                        <h3 className="text-2xl font-bold mb-4">Deploy This Strategy</h3>
                        <p className="text-gray-400 mb-8 max-w-md mx-auto">
                            The protocols described in this dossier are available on the Founder Tier.
                        </p>
                        <Link to="/signup">
                            <Button className="btn-brand px-8 py-3 font-bold text-white">
                                Initialize Agent Swarm
                            </Button>
                        </Link>
                    </div>
                </article>
            </main>
        </div>
    );
};
