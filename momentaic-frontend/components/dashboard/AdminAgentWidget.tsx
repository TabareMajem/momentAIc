import { useState, useEffect } from 'react';
import { Shield, CheckCircle, Film, Image as ImageIcon, Loader, Play } from 'lucide-react';
import { Button } from '../ui/Button';

export function AdminAgentWidget() {
    const [connections, setConnections] = useState<any>({});
    const [loading, setLoading] = useState(true);
    const [showConnect, setShowConnect] = useState<string | null>(null);
    const [connectEmail, setConnectEmail] = useState('');
    const [loopLoading, setLoopLoading] = useState<string | null>(null);
    const [activeRuns, setActiveRuns] = useState<any[]>([]);

    useEffect(() => {
        fetchConnections();
        const interval = setInterval(fetchActiveRuns, 5000);
        return () => clearInterval(interval);
    }, []);

    const fetchActiveRuns = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch('/api/v1/integrations/agentforge/active', {
                headers: { Authorization: `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                setActiveRuns(data.runs || []);
            }
        } catch (e) {
            console.error('Failed to poll runs', e);
        }
    };

    const fetchConnections = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch('/api/v1/integrations/ecosystem/status', {
                headers: { Authorization: `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                setConnections(data.connections || {});
            }
        } catch (e) {
            console.error('Failed to fetch connections', e);
        } finally {
            setLoading(false);
        }
    };

    const handleConnect = async (platform: string) => {
        setLoading(true);
        try {
            const token = localStorage.getItem('token');
            const res = await fetch('/api/v1/integrations/ecosystem/connect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({ platform, email: connectEmail })
            });

            if (res.ok) {
                await fetchConnections();
                setShowConnect(null);
                setConnectEmail('');
                alert(`Connected to ${platform} successfully!`);
            } else {
                const err = await res.json();
                alert(`Failed: ${err.detail}`);
            }
        } catch (e) {
            alert('Connection failed');
        } finally {
            setLoading(false);
        }
    };

    const triggerLoop = async (agent: 'nolan' | 'manga') => {
        setLoopLoading(agent);
        try {
            const token = localStorage.getItem('token');
            const endpoint = agent === 'nolan'
                ? '/api/v1/admin/loops/nolan/daily'
                : '/api/v1/admin/loops/manga/react';

            const res = await fetch(endpoint, {
                method: 'POST',
                headers: { Authorization: `Bearer ${token}` }
            });

            const data = await res.json();
            if (res.ok) {
                alert(`${agent === 'nolan' ? 'Video' : 'Manga'} generation queued!`);
            } else {
                if (data.detail && data.detail.includes("not connected")) {
                    alert("Account not connected. Please connect first.");
                    setShowConnect(agent);
                } else {
                    alert(`Error: ${data.detail || 'Unknown error'}`);
                }
            }
        } catch (e) {
            console.error(e);
            alert('Failed to trigger loop');
        } finally {
            setLoopLoading(null);
        }
    };

    if (loading && Object.keys(connections).length === 0) return <div>Loading integrations...</div>;

    return (
        <div className="bg-[#111111] border border-[#222222] rounded-xl p-6 mb-8">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Shield className="w-5 h-5 text-emerald-400" />
                Admin Ecosystem Controls
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-slate-950 p-4 rounded-lg border border-[#222222] hover:border-blue-500/50 transition-colors">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-blue-500/10 rounded-lg">
                            <Film className="w-5 h-5 text-blue-400" />
                        </div>
                        <div>
                            <span className="font-semibold block">Nolan Pro (Video)</span>
                            <span className="text-xs text-slate-500">Symbiotask Integration</span>
                        </div>
                    </div>

                    <div className="mb-4">
                        <div className="text-xs text-slate-400 mb-1">Status</div>
                        {connections.symbiotask?.connected ? (
                            <div className="flex items-center gap-2 text-emerald-400 text-sm">
                                <CheckCircle className="w-4 h-4" />
                                Verified: {connections.symbiotask.email}
                            </div>
                        ) : (
                            <div className="flex items-center gap-2 text-slate-500 text-sm">
                                <div className="w-2 h-2 rounded-full bg-slate-600" />
                                Not Connected
                            </div>
                        )}
                    </div>

                    {showConnect === 'nolan' ? (
                        <div className="space-y-3 p-3 bg-[#111111] rounded-lg">
                            <label className="text-xs text-slate-400">Verify Pro Membership Email</label>
                            <input
                                type="email"
                                placeholder="name@symbiotask.com"
                                className="w-full bg-slate-950 px-3 py-2 text-sm border border-[#222222] rounded focus:border-blue-500 outline-none"
                                value={connectEmail}
                                onChange={e => setConnectEmail(e.target.value)}
                            />
                            <div className="flex gap-2">
                                <Button size="sm" variant="ghost" onClick={() => setShowConnect(null)}>Cancel</Button>
                                <Button size="sm" variant="cyber" onClick={() => handleConnect('symbiotask')}>
                                    Verify & Connect
                                </Button>
                            </div>
                        </div>
                    ) : (
                        <div className="flex gap-2">
                            {!connections.symbiotask?.connected && (
                                <Button
                                    size="sm"
                                    variant="outline"
                                    className="flex-1"
                                    onClick={() => setShowConnect('nolan')}
                                >
                                    Connect Account
                                </Button>
                            )}

                            <Button
                                size="sm"
                                variant={connections.symbiotask?.connected ? "cyber" : "secondary"}
                                className="flex-1"
                                onClick={() => triggerLoop('nolan')}
                                disabled={loopLoading === 'nolan' || !connections.symbiotask?.connected}
                            >
                                {loopLoading === 'nolan' ? <Loader className="w-3 h-3 animate-spin mr-1" /> : <Play className="w-3 h-3 mr-1" />}
                                Trigger Daily Cycle
                            </Button>
                        </div>
                    )}
                </div>

                <div className="bg-slate-950 p-4 rounded-lg border border-[#222222] hover:border-pink-500/50 transition-colors">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-pink-500/10 rounded-lg">
                            <ImageIcon className="w-5 h-5 text-pink-400" />
                        </div>
                        <div>
                            <span className="font-semibold block">Manga Magic (Image)</span>
                            <span className="text-xs text-slate-500">Mangaka Integration</span>
                        </div>
                    </div>

                    <div className="mb-4">
                        <div className="text-xs text-slate-400 mb-1">Status</div>
                        {connections.mangaka?.connected ? (
                            <div className="flex items-center gap-2 text-emerald-400 text-sm">
                                <CheckCircle className="w-4 h-4" />
                                Verified: {connections.mangaka.email}
                            </div>
                        ) : (
                            <div className="flex items-center gap-2 text-slate-500 text-sm">
                                <div className="w-2 h-2 rounded-full bg-slate-600" />
                                Not Connected
                            </div>
                        )}
                    </div>

                    {showConnect === 'manga' ? (
                        <div className="space-y-3 p-3 bg-[#111111] rounded-lg">
                            <label className="text-xs text-slate-400">Verify Pro Membership Email</label>
                            <input
                                type="email"
                                placeholder="name@mangaka.com"
                                className="w-full bg-slate-950 px-3 py-2 text-sm border border-[#222222] rounded focus:border-pink-500 outline-none"
                                value={connectEmail}
                                onChange={e => setConnectEmail(e.target.value)}
                            />
                            <div className="flex gap-2">
                                <Button size="sm" variant="ghost" onClick={() => setShowConnect(null)}>Cancel</Button>
                                <Button size="sm" variant="cyber" onClick={() => handleConnect('mangaka')}>
                                    Verify & Connect
                                </Button>
                            </div>
                        </div>
                    ) : (
                        <div className="flex gap-2">
                            {!connections.mangaka?.connected && (
                                <Button
                                    size="sm"
                                    variant="outline"
                                    className="flex-1"
                                    onClick={() => setShowConnect('manga')}
                                >
                                    Connect Account
                                </Button>
                            )}

                            <Button
                                size="sm"
                                variant={connections.mangaka?.connected ? "cyber" : "secondary"}
                                className="flex-1"
                                onClick={() => triggerLoop('manga')}
                                disabled={loopLoading === 'manga' || !connections.mangaka?.connected}
                            >
                                {loopLoading === 'manga' ? <Loader className="w-3 h-3 animate-spin mr-1" /> : <Play className="w-3 h-3 mr-1" />}
                                Generate Meme
                            </Button>
                        </div>
                    )}
                </div>
            </div>

            {activeRuns.length > 0 && (
                <div className="mt-6 space-y-3">
                    <div className="text-xs text-slate-500 font-bold uppercase tracking-widest">Live Agent Activity</div>
                    {activeRuns.map(run => (
                        <div key={run.run_id} className="bg-slate-950 border border-[#222222] p-3 rounded-lg flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                                <div>
                                    <div className="text-sm font-bold text-white uppercase">{run.workflow_id}</div>
                                    <div className="text-xs text-slate-400 font-mono">NODE: {run.current_node}</div>
                                </div>
                            </div>
                            <div className="text-xs text-emerald-400 font-mono animate-pulse">EXECUTING...</div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
