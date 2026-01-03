import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../lib/api';
import { Startup, SignalScores, WeeklySprint } from '../types';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Plus, Target, TrendingUp, Rocket, Bot, Activity, ArrowUpRight, Code, Shield, AlertTriangle, Zap } from 'lucide-react';
import { Cell, Pie, PieChart, ResponsiveContainer } from 'recharts';
import { cn } from '../lib/utils';
import { LiveMatrixWidget } from '../components/LiveMatrixWidget';
import { SharedBrainWidget } from '../components/SharedBrainWidget';

// --- COMPONENTS ---

const SystemTicker = () => (
  <div className="w-full bg-[#050505] border-b border-white/5 overflow-hidden py-1.5 mb-0 z-50 relative">
    <div className="whitespace-nowrap animate-[scanline_40s_linear_infinite] font-mono text-[9px] text-gray-600 tracking-widest flex gap-12 select-none">
      <span className="flex items-center gap-2"><div className="w-1 h-1 bg-green-500 rounded-full animate-pulse"></div> SYSTEM STATUS: ONLINE</span>
      <span>ENCRYPTION: AES-256 [SECURE]</span>
      <span>NODE_NETWORK: 42 CONNECTIONS</span>
      <span>API_LATENCY: 12ms</span>
      <span>MEMORY_LOAD: 34%</span>
      <span>THREAT_LEVEL: LOW</span>
      <span>AI_AGENTS: STANDBY</span>
    </div>
  </div>
);

export default function Dashboard() {
  const [startups, setStartups] = useState<Startup[]>([]);
  const [selectedStartupId, setSelectedStartupId] = useState<string | null>(null);
  const [signals, setSignals] = useState<SignalScores | null>(null);
  const [currentSprint, setCurrentSprint] = useState<WeeklySprint | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const startupsData = await api.getStartups();
        setStartups(startupsData);

        if (startupsData.length > 0) {
          const id = startupsData[0].id;
          setSelectedStartupId(id);
          const [signalsData, sprintData] = await Promise.allSettled([
            api.getSignalScores(id),
            api.getCurrentSprint(id)
          ]);

          if (signalsData.status === 'fulfilled') setSignals(signalsData.value);
          if (sprintData.status === 'fulfilled') setCurrentSprint(sprintData.value);
        }
      } catch (error) {
        console.error("Failed to load dashboard data", error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-[#020202]">
      <div className="relative">
        <div className="w-24 h-24 border-t-2 border-b-2 border-[#00f0ff] rounded-full animate-spin"></div>
        <div className="absolute inset-0 flex items-center justify-center font-mono text-[#00f0ff] text-xs font-bold animate-pulse">LOADING</div>
      </div>
    </div>
  );

  if (startups.length === 0) {
    return (
      <div className="h-[80vh] flex flex-col items-center justify-center text-center p-6 bg-[#020202] text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-cyber-grid opacity-5 pointer-events-none"></div>
        <div className="p-8 border border-dashed border-[#2563eb]/30 bg-[#2563eb]/5 mb-6 rounded-full animate-float relative group">
          <div className="absolute inset-0 bg-[#2563eb] opacity-10 blur-2xl rounded-full group-hover:opacity-20 transition-opacity"></div>
          <Rocket className="w-12 h-12 text-[#2563eb] relative z-10" />
        </div>
        <h1 className="text-4xl font-black font-mono mb-3 tracking-tight text-white uppercase">System Empty</h1>
        <p className="text-gray-500 max-w-md mb-8 font-mono text-sm">
          Initialize your first startup entity to begin operations.
        </p>
        <Link to="/startups/new">
          <Button size="lg" variant="cyber" className="shadow-[0_0_20px_rgba(37,99,235,0.2)]">
            INIT_STARTUP_SEQUENCE
          </Button>
        </Link>
      </div>
    );
  }

  const selectedStartup = startups.find(s => s.id === selectedStartupId) || startups[0];
  const score = signals?.composite_score || 0;

  const gaugeData = [
    { name: 'Score', value: score },
    { name: 'Remaining', value: 100 - score },
  ];
  const COLORS = ['#00f0ff', '#1a1a1a'];

  return (
    <div className="bg-[#020202] min-h-screen text-gray-200 font-sans pb-24 md:pb-10 overflow-x-hidden relative">

      {/* Background Ambience */}
      <div className="fixed top-0 right-0 w-[500px] h-[500px] bg-[#2563eb] opacity-[0.02] blur-[150px] pointer-events-none rounded-full"></div>
      <div className="fixed bottom-0 left-0 w-[500px] h-[500px] bg-[#00f0ff] opacity-[0.01] blur-[150px] pointer-events-none rounded-full"></div>

      <SystemTicker />

      {/* HUD Header */}
      <div className="flex flex-col gap-6 mb-8 relative z-10 pt-4">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 border-b border-white/5 pb-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className="h-1.5 w-1.5 bg-[#00ff9d] rounded-full animate-pulse shadow-[0_0_10px_#00ff9d]"></div>
              <span className="font-mono text-[9px] text-[#00ff9d] tracking-[0.2em] uppercase opacity-80">COMMAND_CENTER // {selectedStartup.stage}</span>
            </div>
            <h1 className="text-4xl md:text-5xl font-black text-white tracking-tighter font-mono uppercase leading-none">
              MISSION<span className="text-[#2563eb]">_</span>CTRL
            </h1>
          </div>

          <div className="flex flex-col items-end gap-2">
            <span className="text-[9px] text-gray-600 font-mono uppercase tracking-widest">Target Entity</span>
            <div className="flex items-center gap-3">
              <span className="text-lg font-bold text-white bg-white/5 px-4 py-1.5 rounded-lg border border-white/5 shadow-inner">{selectedStartup.name}</span>
              <Link to="/startups/new">
                <Button variant="outline" size="sm" className="h-10 w-10 p-0 rounded-full border-dashed border-white/20 hover:border-white/50"><Plus className="w-4 h-4" /></Button>
              </Link>
            </div>
          </div>
        </div>

        {/* Quick Actions - Scrollable on Mobile */}
        <div className="overflow-x-auto pb-4 -mx-6 px-6 md:mx-0 md:px-0 no-scrollbar">
          <div className="flex md:grid md:grid-cols-4 gap-4 min-w-[max-content] md:min-w-0">
            <QuickAction href={`/agents/chat?startup=${selectedStartup.id}`} icon={<Bot />} title="AI_ADVISOR" desc="Ready" color="text-[#00f0ff]" />
            <QuickAction href={`/startups/${selectedStartup.id}/signals`} icon={<Activity />} title="VELOCITY" desc="94.2%" color="text-[#00ff9d]" />
            <QuickAction href={`/startups/${selectedStartup.id}/sprints`} icon={<Target />} title="SPRINT" desc="Active" color="text-[#ffee00]" />
            <QuickAction href="/investment" icon={<TrendingUp />} title="FUNDING" desc="Watching" color="text-[#ff003c]" />
          </div>
        </div>
      </div>

      {/* Main HUD Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Signal Core Card */}
        <div className="lg:col-span-2 relative group">
          <div className="tech-panel h-full transition-all rounded-xl overflow-hidden bg-[#050505] border border-white/10">
            <div className="h-full p-6 md:p-8 relative">
              {/* Background Glow */}
              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-[#2563eb] opacity-[0.03] blur-[80px] rounded-full pointer-events-none"></div>

              <div className="flex justify-between items-center mb-8 relative z-10 border-b border-white/5 pb-4">
                <h3 className="font-mono font-bold text-white uppercase text-lg tracking-tight flex items-center gap-2">
                  <Code className="w-5 h-5 text-[#2563eb]" /> Signal Core
                </h3>
                <div className="font-mono text-[9px] text-[#00f0ff] bg-[#00f0ff]/5 border border-[#00f0ff]/20 px-2 py-0.5 rounded animate-pulse">LIVE FEED</div>
              </div>

              <div className="flex flex-col md:flex-row items-center gap-8 md:gap-12 relative z-10">
                {/* Radial Gauge */}
                <div className="relative w-48 h-48 md:w-56 md:h-56 flex-shrink-0">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={gaugeData}
                        cx="50%" cy="50%"
                        innerRadius="70%" outerRadius="90%"
                        startAngle={220} endAngle={-40}
                        paddingAngle={5}
                        dataKey="value"
                        stroke="none"
                        cornerRadius={2}
                      >
                        {gaugeData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index]} className="outline-none" />
                        ))}
                      </Pie>
                    </PieChart>
                  </ResponsiveContainer>

                  {/* Inner Circle Content */}
                  <div className="absolute inset-0 flex flex-col items-center justify-center pt-6 pointer-events-none">
                    <div className="text-[9px] font-mono text-gray-500 uppercase tracking-widest mb-1">COMPOSITE</div>
                    <span className="text-6xl md:text-7xl font-black text-white tracking-tighter drop-shadow-[0_0_15px_rgba(0,240,255,0.2)]">{score}</span>
                    <div className="flex items-center gap-1 mt-1 text-[#00ff9d]">
                      <TrendingUp className="w-3 h-3" />
                      <span className="text-[10px] font-bold">+2.4%</span>
                    </div>
                  </div>
                </div>

                {/* Data Bars */}
                <div className="flex-1 w-full space-y-6">
                  <ScoreBar label="Tech Velocity" value={signals?.technical_velocity_score || 0} color="bg-[#00f0ff]" />
                  <ScoreBar label="Product Market Fit" value={signals?.pmf_score || 0} color="bg-[#2563eb]" />
                  <ScoreBar label="Capital Efficiency" value={signals?.capital_efficiency_score || 0} color="bg-[#00ff9d]" />
                  <ScoreBar label="Founder Performance" value={signals?.founder_performance_score || 0} color="bg-[#ff003c]" />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Active Sprint Terminal */}
        <div className="bg-[#050505] border border-white/10 flex flex-col relative group overflow-hidden rounded-xl">
          <div className="h-full p-6 md:p-8 flex flex-col relative z-10">
            <div className="flex justify-between items-center mb-8 border-b border-white/5 pb-4">
              <h3 className="font-mono font-bold text-white uppercase tracking-tight flex items-center gap-2 text-lg">
                <Target className="w-5 h-5 text-[#ffee00]" /> Active Sprint
              </h3>
              <div className="flex items-center gap-2 bg-[#ffee00]/5 px-2 py-1 rounded border border-[#ffee00]/10">
                <div className="w-1.5 h-1.5 bg-[#ffee00] animate-pulse"></div>
                <span className="text-[#ffee00] font-mono text-[9px] tracking-widest font-bold">RUNNING</span>
              </div>
            </div>

            <div className="flex-1 flex flex-col justify-between gap-6">
              <div>
                <div className="text-[9px] text-gray-500 font-mono mb-2 uppercase tracking-widest flex items-center gap-2">
                  <Shield className="w-3 h-3" /> Primary Objective
                </div>
                <div className="text-xl font-bold text-white leading-tight border-l-2 border-[#ffee00] pl-4 py-2 bg-gradient-to-r from-[#ffee00]/5 to-transparent">
                  {currentSprint ? currentSprint.weekly_goal : "NO_OBJECTIVE_SET"}
                </div>
              </div>

              {currentSprint?.key_metric_name && (
                <div className="bg-[#111] border border-white/5 p-4 relative overflow-hidden group/metric rounded-lg transition-colors hover:border-white/20">
                  <div className="absolute right-0 top-0 p-2 text-gray-600 opacity-20 group-hover/metric:opacity-50 transition-opacity transform group-hover/metric:translate-x-1 group-hover/metric:-translate-y-1"><ArrowUpRight size={32} /></div>
                  <div className="text-[9px] text-gray-400 mb-1 uppercase tracking-widest">
                    {currentSprint.key_metric_name}
                  </div>
                  <div className="text-4xl font-black text-white tracking-tighter">{currentSprint.key_metric_start}</div>
                </div>
              )}

              <Link to={`/startups/${selectedStartup.id}/sprints`} className="mt-auto">
                <Button className="w-full bg-[#ffee00] text-black hover:bg-white hover:text-black font-black font-mono rounded-lg uppercase tracking-[0.2em] h-12 shadow-[0_0_15px_rgba(255,238,0,0.1)] hover:shadow-[0_0_25px_rgba(255,238,0,0.3)] border-none">
                  ACCESS_TERMINAL
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function QuickAction({ href, icon, title, desc, color }: any) {
  return (
    <Link to={href} className="group w-40 md:w-auto flex-shrink-0">
      <div className={`h-full border border-white/10 bg-[#0a0a0a]/50 p-5 hover:bg-[#111] transition-all duration-300 cursor-pointer relative overflow-hidden flex flex-col justify-between rounded-xl hover:border-white/20 backdrop-blur-sm`}>
        <div className={`mb-4 ${color} transform group-hover:scale-110 transition-transform duration-300 opacity-80 group-hover:opacity-100`}>
          {React.cloneElement(icon, { size: 28, strokeWidth: 1.5 })}
        </div>
        <div className="relative z-10">
          <h3 className="font-bold text-white font-mono uppercase tracking-tight text-xs group-hover:translate-x-1 transition-transform">{title}</h3>
          <p className="text-[10px] text-gray-500 mt-1 font-mono uppercase tracking-widest group-hover:text-gray-300 transition-colors truncate">{desc}</p>
        </div>

        {/* Subtle Glow on Hover */}
        <div className={`absolute -inset-px bg-gradient-to-br ${color.replace('text-', 'from-')}/0 to-transparent opacity-0 group-hover:opacity-10 transition-opacity`}></div>
      </div>
    </Link>
  )
}

function ScoreBar({ label, value, color }: any) {
  return (
    <div className="group">
      <div className="flex justify-between mb-1.5 items-end">
        <span className="text-[9px] font-mono text-gray-500 uppercase tracking-widest group-hover:text-white transition-colors">{label}</span>
        <span className="text-xs font-mono font-bold text-white">{value}%</span>
      </div>
      <div className="w-full bg-[#111] h-1.5 rounded-full overflow-hidden border border-white/5 relative">
        <div className={`h-full rounded-full ${color} opacity-80 group-hover:opacity-100 transform origin-left scale-x-0 animate-[float_1s_ease-out_forwards] transition-all duration-1000 shadow-[0_0_10px_currentColor]`} style={{ width: `${value}%`, animationDelay: '0.2s' }}></div>
      </div>
    </div>
  );
}