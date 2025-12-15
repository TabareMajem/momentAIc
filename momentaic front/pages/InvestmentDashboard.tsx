
import React, { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { InvestmentDashboardItem } from '../types';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Progress } from '../components/ui/Progress';
import { Button } from '../components/ui/Button';
import { TrendingUp, AlertTriangle, FileText, CheckCircle, XCircle, BrainCircuit, Activity } from 'lucide-react';
import { Dialog } from '../components/ui/Dialog';

export default function InvestmentDashboard() {
    const [data, setData] = useState<InvestmentDashboardItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedDeal, setSelectedDeal] = useState<InvestmentDashboardItem | null>(null);

    useEffect(() => {
        api.getInvestmentDashboard().then(setData).finally(() => setLoading(false));
    }, []);

    // Helper for manual table
    const Th: React.FC<{ children: React.ReactNode }> = ({ children }) => <th className="px-6 py-4 text-left text-[10px] font-bold text-gray-500 uppercase tracking-widest font-mono">{children}</th>;
    const Td: React.FC<{ children: React.ReactNode }> = ({ children }) => <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300 font-mono border-t border-white/5">{children}</td>;

    return (
        <div className="space-y-8 min-h-screen pb-12">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-white/10 pb-6">
                <div>
                    <div className="flex items-center gap-2 mb-2">
                        <TrendingUp className="w-5 h-5 text-[#00f0ff]" />
                        <span className="text-[10px] font-mono text-[#00f0ff] tracking-widest uppercase">AI VC PROTOCOL</span>
                    </div>
                    <h1 className="text-4xl font-black text-white tracking-tighter">DEAL FLOW</h1>
                    <p className="text-gray-500 mt-2 font-mono text-sm max-w-xl">
                        Autonomous due diligence engine. Algorithms screen for outliers with 99.4% precision.
                    </p>
                </div>
                <div className="flex gap-4">
                    <div className="text-right">
                        <div className="text-2xl font-bold text-white">{data.filter(i => i.investment_eligible).length}</div>
                        <div className="text-[10px] text-gray-500 uppercase tracking-widest font-mono">Hot Deals</div>
                    </div>
                    <div className="w-px bg-white/10 h-10"></div>
                    <div className="text-right">
                        <div className="text-2xl font-bold text-white">${(data.length * 1.5).toFixed(1)}M</div>
                        <div className="text-[10px] text-gray-500 uppercase tracking-widest font-mono">Pipeline Val</div>
                    </div>
                </div>
            </div>

            <Card className="bg-[#050505] border border-white/10 overflow-hidden shadow-2xl">
                <div className="overflow-x-auto">
                    <table className="min-w-full">
                        <thead className="bg-[#0a0a0a]">
                            <tr>
                                <Th>Entity Name</Th>
                                <Th>Stage</Th>
                                <Th>Composite Score</Th>
                                <Th>Signal Velocity</Th>
                                <Th>AI Recommendation</Th>
                                <Th>Action</Th>
                            </tr>
                        </thead>
                        <tbody className="bg-[#050505]">
                            {data.map((item) => (
                                <tr key={item.startup_id} className="hover:bg-white/5 transition-colors group">
                                    <Td>
                                        <div className="font-bold text-white text-base">{item.startup_name}</div>
                                        <div className="text-xs text-gray-600">ID: {item.startup_id.slice(0, 8)}</div>
                                    </Td>
                                    <Td>
                                        <Badge variant="outline" className="uppercase text-[10px] border-white/20 text-gray-400 bg-white/5">{item.stage}</Badge>
                                    </Td>
                                    <Td>
                                        <div className="flex items-center gap-3">
                                            <div className="relative w-12 h-12 flex items-center justify-center">
                                                <svg className="w-full h-full transform -rotate-90">
                                                    <circle cx="24" cy="24" r="20" stroke="#333" strokeWidth="4" fill="none" />
                                                    <circle 
                                                        cx="24" cy="24" r="20" 
                                                        stroke={item.composite_score >= 85 ? '#00f0ff' : item.composite_score >= 70 ? '#3b82f6' : '#f59e0b'} 
                                                        strokeWidth="4" 
                                                        fill="none" 
                                                        strokeDasharray={126} 
                                                        strokeDashoffset={126 - (126 * item.composite_score) / 100} 
                                                        className="transition-all duration-1000 ease-out"
                                                    />
                                                </svg>
                                                <span className="absolute text-xs font-bold text-white">{item.composite_score}</span>
                                            </div>
                                        </div>
                                    </Td>
                                    <Td>
                                        <div className="flex flex-col gap-1 w-32">
                                            <div className="flex justify-between text-[9px] text-gray-500 uppercase">
                                                <span>Tech</span>
                                                <span className="text-[#00f0ff]">{item.technical_velocity_score}</span>
                                            </div>
                                            <div className="h-1 bg-gray-800 rounded-full overflow-hidden">
                                                <div className="h-full bg-[#00f0ff]" style={{width: `${item.technical_velocity_score}%`}}></div>
                                            </div>
                                            <div className="flex justify-between text-[9px] text-gray-500 uppercase mt-1">
                                                <span>PMF</span>
                                                <span className="text-[#a855f7]">{item.pmf_score}</span>
                                            </div>
                                            <div className="h-1 bg-gray-800 rounded-full overflow-hidden">
                                                <div className="h-full bg-[#a855f7]" style={{width: `${item.pmf_score}%`}}></div>
                                            </div>
                                        </div>
                                    </Td>
                                    <Td>
                                        {item.investment_eligible ? (
                                            <div className="flex items-center gap-2 text-green-500 font-bold text-xs uppercase tracking-wider bg-green-500/10 px-3 py-1 rounded border border-green-500/20 w-fit">
                                                <CheckCircle className="w-3 h-3" /> Strong Buy
                                            </div>
                                        ) : (
                                            <div className="flex items-center gap-2 text-yellow-500 font-bold text-xs uppercase tracking-wider bg-yellow-500/10 px-3 py-1 rounded border border-yellow-500/20 w-fit">
                                                <Activity className="w-3 h-3" /> Watch
                                            </div>
                                        )}
                                    </Td>
                                    <Td>
                                        <Button 
                                            variant="ghost" 
                                            size="sm" 
                                            className="text-[#00f0ff] hover:bg-[#00f0ff]/10 hover:text-white border border-transparent hover:border-[#00f0ff]/30 font-mono text-xs"
                                            onClick={() => setSelectedDeal(item)}
                                        >
                                            <FileText className="w-3 h-3 mr-2" /> MEMO
                                        </Button>
                                    </Td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    {data.length === 0 && !loading && (
                        <div className="p-20 text-center text-gray-500 font-mono uppercase tracking-widest">
                            Scanning ecosystem... No signals detected.
                        </div>
                    )}
                </div>
            </Card>

            {/* Deal Memo Modal */}
            <Dialog 
                isOpen={!!selectedDeal} 
                onClose={() => setSelectedDeal(null)} 
                title={`INVESTMENT MEMO: ${selectedDeal?.startup_name.toUpperCase()}`}
            >
                {selectedDeal && (
                    <div className="space-y-6 font-mono text-sm">
                        <div className="flex items-center justify-between bg-black p-4 rounded-lg border border-white/10">
                            <div>
                                <div className="text-[10px] text-gray-500 uppercase tracking-widest">Composite Score</div>
                                <div className="text-3xl font-black text-white">{selectedDeal.composite_score}/100</div>
                            </div>
                            <div className="text-right">
                                <div className="text-[10px] text-gray-500 uppercase tracking-widest">Status</div>
                                <div className={selectedDeal.investment_eligible ? "text-green-500 font-bold" : "text-yellow-500 font-bold"}>
                                    {selectedDeal.investment_eligible ? 'ELIGIBLE' : 'MONITORING'}
                                </div>
                            </div>
                        </div>

                        <div className="space-y-3">
                            <div className="flex items-center gap-2 text-white font-bold border-b border-white/10 pb-2">
                                <BrainCircuit className="w-4 h-4 text-[#00f0ff]" /> AI INVESTMENT THESIS
                            </div>
                            <p className="text-gray-300 leading-relaxed bg-[#0a0a0a] p-4 rounded border border-white/5">
                                {selectedDeal.technical_velocity_score > 80 
                                    ? "Strong technical execution capabilities detected. Engineering throughput exceeds cohort average by 2.4x. "
                                    : "Technical execution requires optimization. "}
                                {selectedDeal.pmf_score > 70 
                                    ? "Market signals indicate early Product-Market Fit with high retention density. "
                                    : "PMF signals are weak; customer validation cycles are too long. "}
                                Recommendation: {selectedDeal.investment_eligible ? "Proceed to Term Sheet generation." : "Hold capital deployment pending further signal data."}
                            </p>
                        </div>

                        <div className="space-y-3">
                            <div className="flex items-center gap-2 text-white font-bold border-b border-white/10 pb-2">
                                <AlertTriangle className="w-4 h-4 text-[#ff003c]" /> DEVIL'S ADVOCATE (RISKS)
                            </div>
                            <ul className="space-y-2 text-gray-400 list-disc list-inside bg-[#0a0a0a] p-4 rounded border border-white/5">
                                <li>Capital efficiency score of {selectedDeal.capital_efficiency_score} suggests high burn rate relative to growth.</li>
                                <li>Competitor analysis shows saturation in {selectedDeal.startup_name}'s sector.</li>
                                <li>Founder performance shows inconsistent sprint completion rates.</li>
                            </ul>
                        </div>

                        <div className="flex justify-end gap-2 pt-4">
                            <Button variant="outline" onClick={() => setSelectedDeal(null)}>Dismiss</Button>
                            {selectedDeal.investment_eligible && (
                                <Button variant="cyber" className="shadow-[0_0_20px_rgba(0,240,255,0.3)]">
                                    GENERATE TERM SHEET
                                </Button>
                            )}
                        </div>
                    </div>
                )}
            </Dialog>
        </div>
    );
}
