import React from 'react';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { ArrowLeft, BookOpen, Share2, Sparkles, TrendingUp, Zap } from 'lucide-react';
import { Button } from '../ui/Button';

export function ResearchWhitepaper({ onBack }: { onBack: () => void }) {
    return (
        <div className="max-w-4xl mx-auto py-12 px-4 sm:px-6 lg:px-8 animate-in fade-in duration-500">
            <button
                onClick={onBack}
                className="flex items-center text-gray-400 hover:text-white transition-colors mb-8 group"
            >
                <ArrowLeft className="w-4 h-4 mr-2 group-hover:-translate-x-1 transition-transform" />
                Back to Dashboard
            </button>

            <div className="mb-12 text-center">
                <Badge variant="cyber" className="mb-6 animate-pulse">
                    <Sparkles className="w-3 h-3 mr-1 inline" />
                    MOMENTAIC RESEARCH LABS
                </Badge>
                <h1 className="text-4xl md:text-6xl font-black text-white tracking-tighter mb-6 leading-tight">
                    The Algorithm of Alpha
                </h1>
                <h2 className="text-xl md:text-2xl text-purple-400 font-serif italic mb-8">
                    Deconstructing the Pedigree Paradox and the Rise of Quantitative Venture Capital
                </h2>

                <div className="flex items-center justify-center gap-6 text-sm font-mono text-gray-500 border-t border-b border-white/10 py-4 mb-12">
                    <span className="flex items-center gap-2"><BookOpen className="w-4 h-4" /> 12 Min Read</span>
                    <span className="flex items-center gap-2"><TrendingUp className="w-4 h-4" /> Market Thesis</span>
                    <span className="flex items-center gap-2"><Zap className="w-4 h-4" /> Vol. 1.0.4</span>
                </div>
            </div>

            <article className="prose prose-invert prose-lg max-w-none prose-headings:font-black prose-headings:tracking-tighter prose-a:text-[#00f0ff] prose-a:no-underline hover:prose-a:underline prose-strong:text-purple-300">
                <h3>I. Introduction: The Efficiency Crisis in Private Capital Markets</h3>
                <p>
                    The global venture capital (VC) industry, widely celebrated as the engine of modern innovation, operates on a fundamental contradiction: it funds the automation of traditional industries while stubbornly resisting its own evolution. Capital allocation remains an intensely manual, intuition-driven artisanal craft, constrained by the cognitive biases and network limitations of human partners.
                </p>
                <p>
                    This reliance on heuristic matchmaking has birthed the <strong>Pedigree Paradox</strong>: a systemic inefficiency where capital flows disproportionately toward founders matching rigid historical archetypes rather than objective indicators of future utility or product-market fit.
                </p>

                <Card className="my-10 p-8 bg-black/40 border-purple-500/30 shadow-[0_0_30px_rgba(168,85,247,0.1)]">
                    <h4 className="flex items-center gap-2 text-xl font-bold text-white mb-4 mt-0">
                        <Sparkles className="w-5 h-5 text-purple-400" />
                        The Inevitable Shift
                    </h4>
                    <p className="mb-0 text-gray-300 text-base leading-relaxed">
                        We are entering the era of Quantitative Venture Capital (QVC). Just as algorithmic trading devoured the intuition-based stock pickers of the 1980s, autonomous signal processing and multi-agent operations—the core of an Autonomous Business OS—are poised to rewrite the rules of early-stage software funding.
                    </p>
                </Card>

                <h3>II. The Artisan Bottleneck</h3>
                <p>
                    Traditional early-stage investing relies on a "warm intro" network graph to source deals, followed by subjective evaluations of founder "grit" and "vision." This artisan approach cannot scale efficiently in a world where AI foundation models drive the marginal cost of software creation toward zero. When 100,000 new software startups can launch in a year, a 10-person partner meeting reviewing 100 deals per quarter is a severe systemic bottleneck.
                </p>

                <h3>III. Quantitative Venture Capital & The Autonomous OS</h3>
                <p>
                    The antidote to the artisan bottleneck is the mechanization of growth. MomentAIc's architecture does not merely observe; it operates. By deploying a swarm of specialized AI agents—from SDRs executing outbound pipelines to PMs defining engineering specs—the system establishes an empirical baseline of traction unpolluted by human subjectivity.
                </p>
                <p>
                    <strong>The formula changes:</strong> You no longer invest in a team; you invest in an Autonomous Business OS governed by a founder's vision. Growth becomes a deterministic function of inputs (compute, capital) multiplying through optimized algorithmic loops. This is the bedrock of Quantitative Venture Capital.
                </p>

                <h3>IV. The Death of the Pedigree Paradox</h3>
                <p>
                    In the traditional paradigm, an ex-Stripe PM from Stanford receives $3M on a slide deck, while a self-taught engineer in Indonesia must bootstrap to $10k MRR to secure a meeting.
                </p>
                <p>
                    When an Autonomous Business OS drives the entire operational stack—marketing, sales, support, and engineering scaffolding—the "pedigree" of the founder ceases to be the primary risk variable. The execution risk is offloaded to the AI Swarm. The remaining delta is pure market opportunity and founder vision. This democratization of execution collapses the Pedigree Paradox entirely.
                </p>

                <h3>V. Conclusion: The Algorithmic Enterprise</h3>
                <p>
                    MomentAIc is not building SaaS. We are building the substrate for the Algorithmic Enterprise. Startups governed by an autonomous OS will outcompete artisan teams not through brilliance, but through sheer, relentless, 24/7 volumetric execution. The future of venture capital belongs to those who fund the algorithm.
                </p>
            </article>

            <div className="mt-16 pt-8 border-t border-white/10 flex items-center justify-between">
                <div className="text-gray-500 font-mono text-sm">
                    © 2026 MomentAIc Research Labs. All rights reserved.
                </div>
                <Button variant="outline" className="gap-2">
                    <Share2 className="w-4 h-4" /> Share Research
                </Button>
            </div>
        </div>
    );
}
