import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, PlayCircle, Sparkles, ExternalLink, Zap } from 'lucide-react';
import { Button } from './Button';

interface SymbioTaskVideoModalProps {
    isOpen: boolean;
    onClose: () => void;
    imageUri?: string;
    prompt?: string;
}

export function SymbioTaskVideoModal({ isOpen, onClose, imageUri, prompt }: SymbioTaskVideoModalProps) {
    if (!isOpen) return null;

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6">
                {/* Backdrop */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    onClick={onClose}
                    className="absolute inset-0 bg-black/80 backdrop-blur-md"
                />

                {/* Modal */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.95, y: 20 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95, y: 20 }}
                    className="relative w-full max-w-2xl bg-[#0a0a0f] border border-purple-500/30 rounded-2xl shadow-2xl shadow-purple-900/40 overflow-hidden"
                >
                    {/* Header */}
                    <div className="p-6 border-b border-white/5 flex justify-between items-center bg-gradient-to-r from-purple-900/20 to-transparent">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg shadow-lg">
                                <PlayCircle className="w-5 h-5 text-white" />
                            </div>
                            <div>
                                <h2 className="text-xl font-bold text-white tracking-tight">AI Video & Ad Generation</h2>
                                <p className="text-xs text-purple-300/80 font-mono tracking-wider uppercase mt-1">Powered by Symbiotask.com</p>
                            </div>
                        </div>
                        <button onClick={onClose} className="p-2 text-gray-500 hover:text-white bg-white/5 hover:bg-white/10 rounded-full transition-colors">
                            <X className="w-5 h-5" />
                        </button>
                    </div>

                    <div className="p-6 sm:p-8 space-y-6">
                        {/* Hero Text */}
                        <div className="text-center space-y-4">
                            <div className="inline-flex items-center gap-2 px-3 py-1 bg-yellow-500/10 border border-yellow-500/20 rounded-full text-yellow-500 text-[10px] font-bold tracking-widest uppercase">
                                <Sparkles className="w-3 h-3" />
                                Premium Partner Offer
                            </div>
                            <h3 className="text-2xl sm:text-3xl font-black text-white px-4">
                                Bring your assets to life with{' '}
                                <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-500">
                                    Cinematic AI Video
                                </span>
                            </h3>
                            <p className="text-gray-400 text-sm max-w-lg mx-auto leading-relaxed">
                                Instantly convert your generated ad campaigns into high-converting 4K video ads
                                for TikTok, Reels, and YouTube Shorts using our partner integration with Symbiotask.
                            </p>
                        </div>

                        {/* Asset Preview (if an image was just generated) */}
                        {imageUri && (
                            <div className="bg-black/40 border border-white/5 rounded-xl p-4 flex gap-4 items-center">
                                <img src={imageUri} alt="Asset preview" className="w-24 h-24 object-cover rounded-lg border border-white/10" />
                                <div className="flex-1 min-w-0">
                                    <h4 className="text-xs font-bold text-gray-300 uppercase tracking-widest mb-1">Target Asset Detected</h4>
                                    <p className="text-xs text-gray-500 font-mono line-clamp-2">&quot;{prompt}&quot;</p>
                                </div>
                                <Zap className="w-5 h-5 text-purple-500 animate-pulse hidden sm:block flex-shrink-0" />
                            </div>
                        )}

                        {/* CTA Card */}
                        <div className="bg-gradient-to-br from-purple-900/40 to-black border border-purple-500/30 rounded-xl p-6 text-center shadow-[inset_0_0_20px_rgba(168,85,247,0.15)] relative overflow-hidden">
                            <div className="absolute -top-10 -right-10 w-32 h-32 bg-pink-500/20 blur-3xl rounded-full pointer-events-none" />

                            <h4 className="text-lg font-bold text-white mb-2 relative">Claim Your MomentAIc Partner Discount</h4>
                            <p className="text-sm text-gray-300 mb-6 font-mono relative">
                                Use code{' '}
                                <span className="text-white bg-purple-600 px-2 py-0.5 rounded font-bold">MOMENTAIC10</span>{' '}
                                to get{' '}
                                <span className="text-pink-400 font-bold">10% OFF</span>{' '}
                                premium video generation on Symbiotask.com.
                            </p>

                            <a href="https://symbiotask.com" target="_blank" rel="noopener noreferrer" className="inline-block">
                                <Button className="px-8 h-12 text-sm bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-400 hover:to-pink-400 text-white font-bold rounded-xl shadow-[0_0_20px_rgba(168,85,247,0.4)] hover:shadow-[0_0_30px_rgba(168,85,247,0.6)] transition-all flex items-center gap-2">
                                    Launch Symbiotask Studio
                                    <ExternalLink className="w-4 h-4" />
                                </Button>
                            </a>
                        </div>
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    );
}
