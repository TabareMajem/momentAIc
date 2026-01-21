import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, Zap, Sparkles, Box, CircuitBoard, Globe, Code, Brain, Cpu, RefreshCw, Copy, Check, Crosshair, Network } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { WarRoomWidget } from './WarRoomWidget';
import { SynergyLabWidget } from './SynergyLabWidget';

// ============ TYPES ============

interface Product {
    name: string;
    desc: string;
}

// ============ ADMIN ECOSYSTEM WIDGET ============

export function AdminEcosystemWidget() {
    const [products, setProducts] = useState<Product[]>([]);
    const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
    const [showWarRoom, setShowWarRoom] = useState(false);
    const [showSynergy, setShowSynergy] = useState(false);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);
    const [strategyLoading, setStrategyLoading] = useState(false);
    const [generatedContent, setGeneratedContent] = useState<any>(null);
    const [strategyContent, setStrategyContent] = useState<any>(null);
    const [copied, setCopied] = useState<string | null>(null);

    useEffect(() => {
        fetchProducts();
    }, []);

    const fetchProducts = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch('/api/v1/admin/god-mode/products', {
                headers: { Authorization: `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                setProducts(data.products || []);
            }
        } catch (e) {
            console.error('Failed to fetch empire products', e);
        } finally {
            setLoading(false);
        }
    };

    const handleNanoBananas = async (productName: string) => {
        setGenerating(true);
        setGeneratedContent(null);
        try {
            const token = localStorage.getItem('token');
            const res = await fetch('/api/v1/admin/god-mode/nano-bananas', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({ product_name: productName })
            });
            const data = await res.json();
            setGeneratedContent(data);
        } catch (e) {
            alert("Failed to generate reality distortion field.");
        } finally {
            setGenerating(false);
        }
    };

    const handleSurpriseMe = async () => {
        setStrategyLoading(true);
        setStrategyContent(null);
        try {
            const token = localStorage.getItem('token');
            const res = await fetch('/api/v1/admin/god-mode/surprise-me', {
                method: 'POST',
                headers: { Authorization: `Bearer ${token}` }
            });
            const data = await res.json();
            setStrategyContent(data);
        } catch (e) {
            alert("Strategist is offline.");
        } finally {
            setStrategyLoading(false);
        }
    };

    const copyToClipboard = (text: string, key: string) => {
        navigator.clipboard.writeText(text);
        setCopied(key);
        setTimeout(() => setCopied(null), 2000);
    };

    const glitchVariants = {
        hidden: { x: 0, opacity: 1 },
        hover: {
            x: [-2, 2, -2, 0],
            textShadow: [
                "2px 0 #00fff9, -2px 0 #ff00c1",
                "-2px 0 #00fff9, 2px 0 #ff00c1",
                "0px 0 transparent, 0px 0 transparent"
            ],
            transition: { repeat: Infinity, duration: 0.2 }
        }
    };

    if (loading) return null;

    return (
        <div className="bg-[#050510] border border-cyan-500/10 rounded-3xl p-8 mb-12 relative overflow-hidden shadow-2xl">
            {/* Background Decor */}
            <div className="absolute top-0 right-0 w-96 h-96 bg-purple-600/5 rounded-full blur-[100px] pointer-events-none" />
            <div className="absolute bottom-0 left-0 w-96 h-96 bg-cyan-600/5 rounded-full blur-[100px] pointer-events-none" />
            <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.02] pointer-events-none" />

            <div className="relative z-10">
                <div className="flex items-center justify-between mb-10">
                    <div>
                        <h3 className="text-3xl font-black flex items-center gap-3 text-white tracking-tighter mb-1">
                            <div className="p-2 bg-gradient-to-br from-cyan-900/50 to-purple-900/50 rounded-lg border border-white/10">
                                <Shield className="w-8 h-8 text-white" />
                            </div>
                            <span className="bg-clip-text text-transparent bg-gradient-to-r from-white via-cyan-100 to-purple-200">
                                EMPIRE CONSOLE
                            </span>
                        </h3>
                        <div className="flex items-center gap-2 pl-16">
                            <span className="text-[10px] px-2 py-0.5 bg-cyan-500/10 text-cyan-400 rounded border border-cyan-500/20 uppercase tracking-[0.2em] font-bold">
                                GOD MODE ACTIVE
                            </span>
                            <span className="text-[10px] text-slate-500 tracking-widest font-mono">/// SYSTEM ONLINE</span>
                        </div>
                    </div>

                    <div className="flex gap-3">
                        <Button
                            variant="outline"
                            size="lg"
                            onClick={() => setShowSynergy(true)}
                            className="border-purple-500/30 text-purple-400 hover:bg-purple-500/10 hover:border-purple-500/60 hover:text-white transition-all h-12 px-6"
                        >
                            <Network className="w-5 h-5 mr-2" />
                            THE NEXUS
                        </Button>
                        <Button
                            variant="outline"
                            size="lg"
                            onClick={handleSurpriseMe}
                            disabled={strategyLoading}
                            className="border-yellow-500/30 text-yellow-500 hover:bg-yellow-500/10 hover:border-yellow-500/60 transition-all h-12 px-6"
                        >
                            {strategyLoading ? <RefreshCw className="w-5 h-5 animate-spin mr-2" /> : <Sparkles className="w-5 h-5 mr-2" />}
                            SURPRISE ME
                        </Button>
                    </div>
                </div>

                {/* Global Strategy Result */}
                <AnimatePresence>
                    {strategyContent && (
                        <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: "auto", opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            className="mb-10 overflow-hidden"
                        >
                            <div className="bg-gradient-to-r from-yellow-500/5 via-yellow-900/5 to-transparent border-l-4 border-yellow-500 rounded-r-xl p-6 relative">
                                <Zap className="absolute top-4 right-4 w-24 h-24 text-yellow-500/5 rotate-12" />
                                <h4 className="text-yellow-400 font-black text-2xl mb-2 flex items-center gap-3 tracking-tight">
                                    <Zap className="w-6 h-6 animate-pulse" />
                                    STRATEGY DETECTED: {strategyContent.campaign_name}
                                </h4>
                                <p className="text-yellow-100/60 italic mb-6 text-lg font-light border-b border-yellow-500/10 pb-4">"{strategyContent.tagline}"</p>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                    <div>
                                        <div className="text-xs text-yellow-500 uppercase font-bold mb-3 tracking-widest">Strategy Brief</div>
                                        <p className="text-sm text-slate-300 whitespace-pre-wrap leading-relaxed bg-black/20 p-4 rounded-lg border border-yellow-500/10">
                                            {strategyContent.strategy_brief}
                                        </p>
                                    </div>
                                    <div>
                                        <div className="text-xs text-yellow-500 uppercase font-bold mb-3 tracking-widest">Execution Steps</div>
                                        <ul className="space-y-3">
                                            {strategyContent.steps?.map((step: string, i: number) => (
                                                <li key={i} className="text-sm text-slate-300 flex items-start gap-4 p-3 rounded-lg bg-black/20 border border-transparent hover:border-yellow-500/20 transition-colors">
                                                    <span className="text-yellow-500 font-mono font-bold bg-yellow-500/10 px-2 rounded">0{i + 1}</span>
                                                    {step}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Product Hive Grid */}
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-7 gap-4 mb-8">
                    {products.map((p) => (
                        <motion.button
                            key={p.name}
                            initial="hidden"
                            whileHover="hover"
                            onClick={() => setSelectedProduct(p)}
                            className={`
                                group relative p-5 rounded-2xl text-left transition-all duration-300 h-32 flex flex-col justify-between
                                ${selectedProduct?.name === p.name
                                    ? 'bg-gradient-to-b from-cyan-900/40 to-cyan-950/40 border-cyan-400 shadow-[0_0_30px_rgba(6,182,212,0.15)] scale-105 z-10'
                                    : 'bg-[#0a0a12] border-white/5 hover:border-white/20 hover:bg-[#151520]'}
                                border
                            `}
                        >
                            <div className="flex justify-between items-start">
                                <motion.div variants={glitchVariants}>
                                    {p.name.includes('Yokaizen') ? <Brain className="w-6 h-6 text-pink-500" /> :
                                        p.name.includes('Agent') ? <Cpu className="w-6 h-6 text-cyan-500" /> :
                                            <Globe className="w-6 h-6 text-emerald-500" />}
                                </motion.div>
                                {selectedProduct?.name === p.name && (
                                    <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse shadow-[0_0_10px_rgba(6,182,212,0.8)]" />
                                )}
                            </div>

                            <div>
                                <div className={`font-bold text-sm truncate mb-1 ${selectedProduct?.name === p.name ? 'text-white' : 'text-slate-400 group-hover:text-slate-200'}`}>
                                    {p.name}
                                </div>
                                <div className="text-[9px] text-slate-500 uppercase tracking-wider truncate opacity-0 group-hover:opacity-100 transition-opacity">
                                    ACTIVE
                                </div>
                            </div>
                        </motion.button>
                    ))}
                </div>

                {/* Selected Product Command Center */}
                <AnimatePresence mode='wait'>
                    {selectedProduct && (
                        <motion.div
                            key={selectedProduct.name}
                            initial={{ opacity: 0, scale: 0.98, y: 10 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.98, y: -10 }}
                            className="bg-[#080810] border border-cyan-500/20 rounded-2xl p-8 relative overflow-hidden"
                        >
                            {/* Circuit Pattern Overlay */}
                            <div className="absolute top-0 right-0 p-8 opacity-5">
                                <CircuitBoard className="w-64 h-64 text-cyan-400" />
                            </div>

                            <div className="flex items-center justify-between mb-8 relative z-10">
                                <div>
                                    <h4 className="text-3xl font-black text-white mb-2 tracking-tight">{selectedProduct.name}</h4>
                                    <p className="text-slate-400 text-sm max-w-xl">{selectedProduct.desc}</p>
                                </div>
                                <div className="flex gap-4">
                                    <Button
                                        size="lg"
                                        className="bg-black border border-cyan-500/50 text-cyan-400 hover:bg-cyan-500/10 hover:text-white transition-all font-bold tracking-wider"
                                        onClick={() => handleNanoBananas(selectedProduct.name)}
                                        disabled={generating}
                                    >
                                        {generating ? <RefreshCw className="w-5 h-5 animate-spin mr-2" /> : <Sparkles className="w-5 h-5 mr-2" />}
                                        INITIATE NANO BANANAS
                                    </Button>
                                    <Button
                                        size="lg"
                                        className="bg-red-600 hover:bg-red-700 text-white border-0 shadow-[0_0_30px_rgba(220,38,38,0.4)] hover:shadow-[0_0_50px_rgba(220,38,38,0.6)] font-bold tracking-wider"
                                        onClick={() => setShowWarRoom(true)}
                                    >
                                        <Crosshair className="w-5 h-5 mr-2" />
                                        OPEN WAR ROOM
                                    </Button>
                                </div>
                            </div>

                            {/* Generated Content Display */}
                            {generatedContent && (
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    className="grid grid-cols-1 md:grid-cols-3 gap-6 relative z-10"
                                >
                                    {[
                                        { title: 'Viral Tweet', icon: '🐦', content: generatedContent.tweet, color: 'text-blue-400', key: 'tweet' },
                                        { title: 'LinkedIn Post', icon: '💼', content: generatedContent.linkedin, color: 'text-blue-600', key: 'li' },
                                        { title: 'Midjourney Prompt', icon: '🎨', content: generatedContent.art_prompt, color: 'text-pink-500', key: 'art' }
                                    ].map((item) => (
                                        <div key={item.key} className="bg-black/40 p-6 rounded-xl border border-white/5 hover:border-white/10 transition-colors group">
                                            <div className="flex items-center justify-between mb-4">
                                                <div className={`text-xs font-black uppercase tracking-widest ${item.color} flex items-center gap-2`}>
                                                    <span className="text-lg">{item.icon}</span> {item.title}
                                                </div>
                                                <button
                                                    onClick={() => copyToClipboard(item.content, item.key)}
                                                    className="p-2 rounded-lg hover:bg-white/10 text-slate-500 hover:text-white transition-colors"
                                                >
                                                    {copied === item.key ? <Check className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4" />}
                                                </button>
                                            </div>
                                            <div className="relative">
                                                <p className="text-sm text-slate-300/80 whitespace-pre-wrap leading-relaxed font-mono text-xs max-h-48 overflow-y-auto custom-scrollbar">
                                                    {item.content}
                                                </p>
                                                <div className="absolute bottom-0 left-0 w-full h-8 bg-gradient-to-t from-black/0 to-transparent pointer-events-none" />
                                            </div>
                                        </div>
                                    ))}
                                </motion.div>
                            )}
                        </motion.div>
                    )}
                </AnimatePresence>

            </div>

            {showWarRoom && selectedProduct && (
                <WarRoomWidget product={selectedProduct} onClose={() => setShowWarRoom(false)} />
            )}

            {showSynergy && (
                <SynergyLabWidget products={products} onClose={() => setShowSynergy(false)} />
            )}
        </div>
    );
}
