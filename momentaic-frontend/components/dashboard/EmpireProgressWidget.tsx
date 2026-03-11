import { useState, useEffect } from 'react';
import { Rocket, Zap, ArrowRight } from 'lucide-react';
import { api } from '../../lib/api';
import { useNavigate } from 'react-router-dom';
import { Button } from '../ui/Button';

export function EmpireProgressWidget() {
    const [status, setStatus] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchStatus = async () => {
            try {
                const res = await api.getEmpireStatus();
                setStatus(res);
            } catch (e) {
                console.error('Failed to fetch empire status:', e);
            } finally {
                setLoading(false);
            }
        };
        fetchStatus();
    }, []);

    if (loading) return <div className="animate-pulse bg-[#111111] h-24 rounded-xl border border-white/5 mb-8" />;
    if (!status || status.completed_at) return null;

    const stepsCount = 5;
    const percent = Math.min(((status.current_step) / stepsCount) * 100, 100);

    return (
        <div className="bg-[#111111] border border-purple-500/20 rounded-xl p-5 mb-8 relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-2 opacity-10 group-hover:opacity-20 transition-opacity">
                <Rocket className="w-16 h-16 rotate-12" />
            </div>

            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
                <div className="flex items-center gap-4">
                    <div className="p-3 bg-purple-500/20 rounded-full">
                        <Zap className="w-6 h-6 text-purple-400" />
                    </div>
                    <div>
                        <h3 className="text-lg font-bold text-white flex items-center gap-2">
                            <span className="text-[#00f0ff] uppercase tracking-tighter">Unfinished Business</span>
                            <span className="text-[10px] px-2 py-0.5 bg-white/10 text-white rounded-full font-mono uppercase">Step {status.current_step + 1} of 5</span>
                        </h3>
                        <p className="text-sm text-slate-300 mt-1">
                            Your Empire is {percent}% complete. Finish the protocol to unlock God Mode.
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    <div className="w-32 h-1.5 bg-black/40 rounded-full overflow-hidden border border-white/10 hidden sm:block">
                        <div
                            className="h-full bg-[#111111] from-purple-500 transition-all duration-500"
                            style={{ width: `${percent}%` }}
                        />
                    </div>
                    <Button variant="cyber" size="sm" onClick={() => navigate('/empire-builder')}>
                        RESUME PROTOCOL <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                </div>
            </div>
        </div>
    );
}
