
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Check, X, Bell, Zap } from 'lucide-react';
import { api } from '@/lib/api';
import toast from 'react-hot-toast';

interface ActionItem {
    id: string;
    source: string;
    title: string;
    description: string;
    priority: 'low' | 'medium' | 'high' | 'urgent';
    payload: any;
    created_at: string;
}

export const MorningBriefWidget = () => {
    const [items, setItems] = useState<ActionItem[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchItems();
    }, []);

    const fetchItems = async () => {
        try {
            const res = await api.get('/actions/pending');
            setItems(res.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleAction = async (id: string, action: 'approve' | 'reject') => {
        try {
            await api.post(`/actions/${id}/${action}`);
            toast.success(action === 'approve' ? 'Action Approved & Executed' : 'Action Rejected');
            // Remove from list immediately (optimistic)
            setItems(prev => prev.filter(i => i.id !== id));
        } catch (err) {
            toast.error('Failed to process action');
        }
    };

    if (loading || items.length === 0) return null;

    return (
        <div className="mb-8">
            <div className="flex items-center gap-2 mb-4">
                <div className="bg-yellow-500/10 border border-yellow-500/20 px-3 py-1 rounded text-xs font-mono text-yellow-500 uppercase tracking-widest flex items-center gap-2">
                    <Zap className="w-3 h-3" /> Morning Brief
                </div>
                <span className="text-gray-500 text-xs">{items.length} pending decisions</span>
            </div>

            {/* Mobile: Horizontal Scroll | Desktop: Grid */}
            <div className="flex overflow-x-auto pb-4 gap-4 md:grid md:grid-cols-2 lg:grid-cols-3 snap-x snap-mandatory md:snap-none hide-scrollbar">
                <AnimatePresence>
                    {items.map((item) => (
                        <motion.div
                            key={item.id}
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.9, height: 0 }}
                            className="bg-[#111] border border-white/10 rounded-xl p-5 hover:border-white/20 transition-colors relative overflow-hidden group min-w-[85vw] md:min-w-0 snap-center touch-manipulation"
                        >
                            <div className="absolute top-0 right-0 p-3 opacity-0 group-hover:opacity-100 transition-opacity">
                                <span className={`text-[10px] uppercase tracking-wider px-2 py-1 rounded bg-white/5 
                  ${item.priority === 'urgent' ? 'text-red-400' :
                                        item.priority === 'high' ? 'text-orange-400' : 'text-gray-400'}`}>
                                    {item.priority}
                                </span>
                            </div>

                            <div className="flex items-start gap-4 mb-4">
                                <div className={`p-2 rounded-lg ${item.source === 'SalesHunter' ? 'bg-blue-500/10 text-blue-400' : 'bg-purple-500/10 text-purple-400'}`}>
                                    {item.source === 'SalesHunter' ? '🎯' : '🚀'}
                                </div>
                                <div>
                                    <h3 className="text-sm font-bold text-white leading-tight mb-1">{item.title}</h3>
                                    <p className="text-xs text-xs text-gray-500 uppercase tracking-wider">{item.source}</p>
                                </div>
                            </div>

                            <p className="text-xs text-gray-400 mb-6 leading-relaxed">
                                {item.description}
                            </p>

                            <div className="flex items-center gap-2">
                                <button
                                    onClick={() => handleAction(item.id, 'reject')}
                                    className="flex-1 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-gray-400 text-xs font-medium transition-colors border border-transparent hover:border-white/5 flex items-center justify-center gap-2 group/reject"
                                >
                                    <X className="w-3 h-3 group-hover/reject:text-red-400" />
                                    Reject
                                </button>
                                <button
                                    onClick={() => handleAction(item.id, 'approve')}
                                    className="flex-1 py-2 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 text-xs font-bold transition-colors border border-emerald-500/20 hover:border-emerald-500/30 flex items-center justify-center gap-2 shadow-[0_0_15px_rgba(16,185,129,0.1)] hover:shadow-[0_0_20px_rgba(16,185,129,0.2)]"
                                >
                                    <Check className="w-3 h-3" />
                                    Approve & Execute
                                </button>
                            </div>

                        </motion.div>
                    ))}
                </AnimatePresence>
            </div>
        </div>
    );
};
