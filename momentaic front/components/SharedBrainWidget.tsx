import React, { useEffect, useState } from 'react';
import { Brain, Cpu, Database, ChevronRight, RefreshCw } from 'lucide-react';
import { api } from '../lib/api';
import { useChatStore } from '../stores/chat-store';

interface MemoryItem {
    id: string;
    content: string;
    importance: number;
    created_at: string;
}

export const SharedBrainWidget = () => {
    const { currentStartupId } = useChatStore();
    const [memories, setMemories] = useState<MemoryItem[]>([]);
    const [loading, setLoading] = useState(false);

    const fetchMemories = async () => {
        if (!currentStartupId) return;

        try {
            setLoading(true);
            // Assuming we added getSharedBrainMemory to api.ts, or verify if we need to add it:
            // Actually I haven't added it to api.ts yet. I should add it or use raw fetch. 
            // For now, raw fetch to keep velocity high, assuming standard bearer token
            const token = api.getToken();
            const res = await fetch(`${import.meta.env.VITE_API_URL || ''}/api/v1/agents/memory/shared-brain?startup_id=${currentStartupId}&limit=5`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                setMemories(data); // Expecting array of memories
            }
        } catch (e) {
            console.error("SharedBrain fetch error", e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchMemories();
        const interval = setInterval(fetchMemories, 10000); // Poll every 10s
        return () => clearInterval(interval);
    }, [currentStartupId]);

    if (!currentStartupId) return null;

    return (
        <div className="bg-[#050505] border border-white/10 rounded-xl p-4 flex flex-col gap-3">
            <div className="flex justify-between items-center pb-2 border-b border-white/5">
                <div className="flex items-center gap-2">
                    <Brain className="w-4 h-4 text-[#bf25eb]" />
                    <span className="text-xs font-mono uppercase tracking-widest text-[#bf25eb]">Shared Brain</span>
                </div>
                <button onClick={fetchMemories} className="text-gray-500 hover:text-white transition-colors">
                    <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
                </button>
            </div>

            <div className="space-y-3">
                {memories.length === 0 && !loading && (
                    <p className="text-gray-600 text-xs italic">No high-importance memories yet.</p>
                )}

                {memories.map(mem => (
                    <div key={mem.id} className="relative pl-3 border-l border-white/10 group hover:border-[#bf25eb] transition-colors">
                        <div className="absolute -left-[3px] top-1.5 w-1.5 h-1.5 bg-[#0a0a0a] border border-white/20 rounded-full group-hover:border-[#bf25eb] group-hover:bg-[#bf25eb]" />
                        <p className="text-[11px] text-gray-300 font-light leading-relaxed mb-1">
                            {mem.content}
                        </p>
                        <div className="flex justify-between items-center text-[9px] text-gray-600">
                            <span className="flex items-center gap-1">
                                <Database className="w-2 h-2" />
                                {new Date(mem.created_at).toLocaleDateString()}
                            </span>
                            <span className={mem.importance > 8 ? "text-[#bf25eb]" : ""}>
                                Imp: {mem.importance}
                            </span>
                        </div>
                    </div>
                ))}

                <div className="pt-2 flex justify-end">
                    <span className="text-[9px] text-gray-500 uppercase tracking-widest flex items-center gap-1">
                        <Cpu className="w-2 h-2" /> Memory Active
                    </span>
                </div>
            </div>
        </div>
    );
};
