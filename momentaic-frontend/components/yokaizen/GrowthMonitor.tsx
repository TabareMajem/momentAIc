import React, { useEffect, useState } from 'react';
import { Terminal, Activity, Calendar, Target, Globe } from 'lucide-react';
import api from '../../services/api';

interface GrowthData {
    strategies: any[];
    campaigns: any[];
    queueStats: any;
    recentContent: any[];
}

export const GrowthMonitor: React.FC = () => {
    const [data, setData] = useState<GrowthData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await api.get('/growth/monitor');
                setData(response.data);
            } catch (error) {
                console.error('Failed to load growth data', error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 5000); // Live poll
        return () => clearInterval(interval);
    }, []);

    if (loading) return <div className="p-8 text-white">Initializing Neural Link...</div>;

    return (
        <div className="min-h-screen bg-black text-green-400 p-6 font-mono">
            <header className="mb-8 border-b border-green-800 pb-4 flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold flex items-center gap-2">
                        <Globe className="w-8 h-8" />
                        GTM MONITOR <span className="text-xs bg-red-900 text-red-100 px-2 py-1 rounded">GOD MODE ACTIVE</span>
                    </h1>
                    <p className="text-gray-500 mt-1">Global Strategy Execution & Content Loop</p>
                </div>
                <div className="flex gap-4 text-sm">
                    <div className="flex items-center gap-2">
                        <Activity className="w-4 h-4 animate-pulse" />
                        <span>VIRAL WORKER: ACTIVE</span>
                    </div>
                </div>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                {/* Active Strategies */}
                <div className="col-span-1 lg:col-span-2 space-y-6">
                    <h2 className="text-xl font-bold flex items-center gap-2 border-l-4 border-green-500 pl-4">
                        <Target className="w-5 h-5" /> ACTIVE STRATEGIES
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {data?.strategies.map((strategy: any) => (
                            <div key={strategy.id} className="bg-gray-900 border border-green-800 p-4 rounded hover:border-green-500 transition-colors">
                                <h3 className="text-lg font-bold text-white mb-2">{strategy.targetUrl}</h3>
                                <div className="text-xs text-gray-400 mb-4 font-mono">
                                    {JSON.parse(strategy.strategyJson as string).campaign_overview?.product_analysis?.substring(0, 100)}...
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-xs bg-blue-900 text-blue-200 px-2 py-1 rounded">
                                        {strategy.budget}
                                    </span>
                                    <span className="text-xs text-green-500">Executing...</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Queue Stats */}
                <div className="bg-gray-900 border border-gray-800 p-6 rounded">
                    <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                        <Activity className="w-5 h-5" /> SYSTEM LOAD
                    </h2>
                    <div className="space-y-4">
                        <div className="flex justify-between border-b border-gray-800 pb-2">
                            <span>Viral Jobs</span>
                            <span className="text-white font-bold">{data?.queueStats?.viral?.active || 0}</span>
                        </div>
                        <div className="flex justify-between border-b border-gray-800 pb-2">
                            <span>Video Jobs</span>
                            <span className="text-white font-bold">{data?.queueStats?.video?.active || 0}</span>
                        </div>
                        <div className="flex justify-between border-b border-gray-800 pb-2">
                            <span>Completed Today</span>
                            <span className="text-green-400 font-bold">{data?.queueStats?.viral?.completed || 0}</span>
                        </div>
                    </div>
                </div>

                {/* Live Content Calendar */}
                <div className="col-span-1 lg:col-span-3 mt-8">
                    <h2 className="text-xl font-bold mb-6 flex items-center gap-2 border-l-4 border-purple-500 pl-4">
                        <Calendar className="w-5 h-5" /> LIVE CONTENT LOOP
                    </h2>
                    <div className="bg-gray-900 rounded border border-gray-800 overflow-hidden">
                        <table className="w-full text-left">
                            <thead className="bg-gray-800 text-gray-400">
                                <tr>
                                    <th className="p-4">Platform</th>
                                    <th className="p-4">Content Preview</th>
                                    <th className="p-4">Status</th>
                                    <th className="p-4">Ambassador/Hook</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-800">
                                {data?.recentContent.length === 0 && (
                                    <tr>
                                        <td colSpan={4} className="p-8 text-center text-gray-500">
                                            Waiting for Agent Output...
                                        </td>
                                    </tr>
                                )}
                                {data?.recentContent.map((content: any) => (
                                    <tr key={content.id} className="hover:bg-gray-800 transition-colors">
                                        <td className="p-4 font-bold text-white">{content.platform}</td>
                                        <td className="p-4 text-gray-400 text-sm max-w-md truncate">{content.content}</td>
                                        <td className="p-4">
                                            <span className={`px-2 py-1 rounded text-xs ${content.status === 'PUBLISHED' ? 'bg-green-900 text-green-200' : 'bg-yellow-900 text-yellow-200'}`}>
                                                {content.status}
                                            </span>
                                        </td>
                                        <td className="p-4 text-gray-500 text-xs">Authored by AI</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

            </div>
        </div>
    );
};
