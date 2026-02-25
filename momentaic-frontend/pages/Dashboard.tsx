import { useState, useEffect } from 'react';
import {
  FileText, Users, TrendingUp, Send, Bot, Eye, Rocket, ArrowRight,
  BarChart2, Shield, ChevronDown, ChevronUp, Film, Image as ImageIcon, PlayCircle,
  Zap, Loader, CheckCircle, Clock, Pause, Play, Sparkles
} from 'lucide-react';
import { api } from '../lib/api';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import ActivityFeed from '../components/ActivityFeed';
import { AdminEcosystemWidget } from '../components/dashboard/AdminEcosystemWidget';
import { AstroTurfWidget } from '../components/ui/AstroTurfWidget';
import { LiveAgentDashboard } from '../components/LiveAgentDashboard';
import { BenchmarkWidget } from '../components/dashboard/BenchmarkWidget';
import { useAuthStore } from '../stores/auth-store';
import { useStartupStore } from '../stores/startup-store';

// ============ TYPES ============

interface AgentActivity {
  id: string;
  agent: string;
  task: string;
  status: 'pending' | 'running' | 'complete' | 'error';
  progress: number;
  message: string;
  result?: any;
  started_at: string;
}

// ============ AGENT ICONS ============

const AGENT_ICONS: Record<string, any> = {
  ContentAgent: FileText,
  SDRAgent: Send,
  GrowthHackerAgent: TrendingUp,
  CompetitorIntelAgent: Eye,
  LeadResearcherAgent: Users,
  MarketingAgent: BarChart2,
  default: Bot,
};

const AGENT_COLORS: Record<string, string> = {
  ContentAgent: 'from-purple-500 to-pink-500',
  SDRAgent: 'from-blue-500 to-cyan-500',
  GrowthHackerAgent: 'from-green-500 to-emerald-500',
  CompetitorIntelAgent: 'from-orange-500 to-red-500',
  LeadResearcherAgent: 'from-yellow-500 to-orange-500',
  MarketingAgent: 'from-indigo-500 to-purple-500',
  default: 'from-slate-500 to-slate-600',
};

// ============ AGENT CARD ============

function AgentCard({ activity }: { activity: AgentActivity }) {
  const [expanded, setExpanded] = useState(false);
  const Icon = AGENT_ICONS[activity.agent] || AGENT_ICONS.default;
  const color = AGENT_COLORS[activity.agent] || AGENT_COLORS.default;

  const getStatusIndicator = () => {
    switch (activity.status) {
      case 'running':
        return <Loader className="w-4 h-4 text-blue-400 animate-spin" />;
      case 'complete':
        return <CheckCircle className="w-4 h-4 text-emerald-400" />;
      case 'error':
        return <span className="w-2 h-2 rounded-full bg-red-500" />;
      case 'pending':
        return <Clock className="w-4 h-4 text-slate-400" />;
    }
  };

  return (
    <div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-slate-900/50 rounded-xl border border-white/5 overflow-hidden hover:border-white/10 transition-colors"
    >
      <div
        className="p-4 cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-4">
          {/* Agent Icon */}
          <div className={`p-2 rounded-lg bg-gradient-to-br ${color}`}>
            <Icon className="w-5 h-5 text-white" />
          </div>

          {/* Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="font-medium text-white">{activity.agent}</span>
              {getStatusIndicator()}
            </div>
            <p className="text-sm text-slate-400 truncate">{activity.task}</p>
          </div>

          {/* Progress */}
          {activity.status === 'running' && (
            <div className="text-right">
              <span className="text-sm font-medium text-blue-400">{activity.progress}%</span>
            </div>
          )}

          {/* Expand */}
          {expanded ? (
            <ChevronUp className="w-4 h-4 text-slate-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-slate-400" />
          )}
        </div>

        {/* Progress Bar */}
        {activity.status === 'running' && (
          <div className="mt-3 h-1 bg-slate-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-blue-500 to-cyan-500"
              initial={{ width: 0 }}
              animate={{ width: `${activity.progress}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        )}
      </div>

      {/* Expanded Content */}

      {expanded && (
        <div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          className="border-t border-white/5"
        >
          <div className="p-4 space-y-3">
            {/* Live Message */}
            <div className="bg-slate-800/50 rounded-lg p-3">
              <p className="text-xs text-slate-500 mb-1">Current Status</p>
              <p className="text-sm text-slate-300 font-mono">
                {activity.message || 'Processing...'}
              </p>
            </div>

            {/* Result Preview */}
            {activity.result && (
              <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-3">
                <p className="text-xs text-emerald-400 mb-1">Result</p>
                <p className="text-sm text-emerald-300">
                  {typeof activity.result === 'string'
                    ? activity.result.slice(0, 200)
                    : JSON.stringify(activity.result).slice(0, 200)}
                </p>
              </div>
            )}



            {/* Actions */}
            <div className="flex gap-2">
              {activity.status === 'running' && (
                <Button size="sm" variant="outline">
                  <Pause className="w-3 h-3 mr-1" />
                  Pause
                </Button>
              )}
              {activity.status === 'complete' && (
                <Button size="sm" variant="cyber">
                  View Full Result
                </Button>
              )}
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

// ============ ADMIN AGENT WIDGET ============

function AdminAgentWidget() {
  const [connections, setConnections] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [showConnect, setShowConnect] = useState<string | null>(null);
  const [connectEmail, setConnectEmail] = useState('');
  const [loopLoading, setLoopLoading] = useState<string | null>(null);
  const [activeRuns, setActiveRuns] = useState<any[]>([]);

  useEffect(() => {
    fetchConnections();
    // Poll for active runs every 5 seconds
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
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 mb-8">
      <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
        <Shield className="w-5 h-5 text-emerald-400" />
        Admin Ecosystem Controls
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Nolan Trigger */}
        <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 hover:border-blue-500/50 transition-colors">
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
            <div className="space-y-3 p-3 bg-slate-900 rounded-lg">
              <label className="text-xs text-slate-400">Verify Pro Membership Email</label>
              <input
                type="email"
                placeholder="name@symbiotask.com"
                className="w-full bg-slate-950 px-3 py-2 text-sm border border-slate-700 rounded focus:border-blue-500 outline-none"
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

        {/* Manga Trigger */}
        <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 hover:border-pink-500/50 transition-colors">
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
            <div className="space-y-3 p-3 bg-slate-900 rounded-lg">
              <label className="text-xs text-slate-400">Verify Pro Membership Email</label>
              <input
                type="email"
                placeholder="name@mangaka.com"
                className="w-full bg-slate-950 px-3 py-2 text-sm border border-slate-700 rounded focus:border-pink-500 outline-none"
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

      {/* Active Runs Display */}
      {activeRuns.length > 0 && (
        <div className="mt-6 space-y-3">
          <div className="text-xs text-slate-500 font-bold uppercase tracking-widest">Live Agent Activity</div>
          {activeRuns.map(run => (
            <div key={run.run_id} className="bg-slate-950 border border-slate-800 p-3 rounded-lg flex items-center justify-between">
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

function EmpireProgressWidget() {
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

  if (loading) return <div className="animate-pulse bg-slate-900 h-24 rounded-xl border border-white/5 mb-8" />;
  if (!status || status.completed_at) return null;

  const stepsCount = 5;
  const percent = Math.min(((status.current_step) / stepsCount) * 100, 100);

  return (
    <div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gradient-to-r from-purple-900/30 to-blue-900/30 border border-purple-500/20 rounded-xl p-5 mb-8 relative overflow-hidden group"
    >
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
              className="h-full bg-gradient-to-r from-purple-500 to-cyan-500"
              initial={{ width: 0 }}
              animate={{ width: `${percent}%` }}
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

// ============ ZERO STATE WIDGET ============

function ZeroStateWidget({ pendingStrategy, onCreateStartup }: { pendingStrategy: any; onCreateStartup: () => void }) {
  return (
    <div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="min-h-[60vh] flex flex-col items-center justify-center text-center px-4"
    >
      <div className="max-w-lg space-y-8">
        {/* Icon */}
        <div className="relative mx-auto w-24 h-24">
          <div className="absolute inset-0 bg-gradient-to-br from-purple-500/20 to-cyan-500/20 rounded-full animate-pulse" />
          <div className="relative w-full h-full rounded-full bg-[#111] border border-white/10 flex items-center justify-center">
            <Rocket className="w-10 h-10 text-[#00f0ff]" />
          </div>
        </div>

        {/* Title */}
        <div>
          <h2 className="text-3xl font-bold text-white mb-3">Launch Your Empire</h2>
          <p className="text-gray-400 text-sm">
            {pendingStrategy
              ? "You have a strategy ready! Create your first startup to activate it."
              : "Create your first startup to unlock the full power of your AI team."
            }
          </p>
        </div>

        {/* Pending Strategy Preview */}
        {pendingStrategy && (
          <div className="bg-[#0a0a0a] border border-[#00f0ff]/20 rounded-xl p-4 text-left">
            <div className="flex items-center gap-2 mb-2 text-[#00f0ff]">
              <Sparkles className="w-4 h-4" />
              <span className="text-xs font-bold uppercase tracking-widest">Saved Strategy</span>
            </div>
            <p className="text-sm text-gray-300 line-clamp-2">
              {pendingStrategy.strategy?.target_audience || pendingStrategy.plan?.summary || "Your AI-generated growth strategy is ready"}
            </p>
          </div>
        )}

        {/* CTA Button */}
        <Button
          variant="cyber"
          size="lg"
          onClick={onCreateStartup}
          className="w-full max-w-xs mx-auto"
        >
          <Zap className="w-5 h-5 mr-2" />
          CREATE YOUR FIRST STARTUP
        </Button>

        {/* Secondary Action */}
        <p className="text-xs text-gray-600">
          Takes less than 60 seconds • No credit card required
        </p>
      </div>
    </div>
  );
}

// ============ MAIN DASHBOARD ============


export default function Dashboard() {
  const user = useAuthStore((state) => state.user);
  const navigate = useNavigate();
  const { startups, activeStartupId, fetchStartups } = useStartupStore();
  const [activities, setActivities] = useState<AgentActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [pendingStrategy, setPendingStrategy] = useState<any>(null);

  const hasStartups = startups.length > 0;

  // Hydrate startup store if needed
  useEffect(() => {
    if (user && startups.length === 0) {
      fetchStartups();
    }
  }, [user]);

  // Load dashboard data whenever the active startup changes
  useEffect(() => {
    if (!user || !activeStartupId) {
      setLoading(false);
      return;
    }

    const loadRealData = async () => {
      setLoading(true);
      try {
        // Check for pending strategies from onboarding
        const pendingStrategyData = localStorage.getItem('pendingStrategy');
        const pendingGeniusPlan = localStorage.getItem('pendingGeniusPlan');
        if (pendingStrategyData) {
          setPendingStrategy(JSON.parse(pendingStrategyData));
        } else if (pendingGeniusPlan) {
          setPendingStrategy(JSON.parse(pendingGeniusPlan));
        }

        // Get Dashboard Data scoped to active startup
        const dashboard = await api.getDashboard(activeStartupId);

        // Map to Frontend Model
        const realActivities: AgentActivity[] = dashboard.recent_activity.map((a: any, idx: number) => ({
          id: `act-${idx}`,
          agent: a.agent || 'System',
          task: a.type === 'content_drafted' ? 'Drafting Content' :
            a.type === 'lead_acquired' ? 'Hunting Leads' :
              a.message.split(':')[0] || 'Processing',
          status: 'complete',
          progress: 100,
          message: a.message,
          started_at: a.timestamp
        }));

        setActivities(realActivities);
      } catch (e) {
        console.error("Failed to load dashboard:", e);
      } finally {
        setLoading(false);
      }
    };

    loadRealData();
  }, [user, activeStartupId]);

  const activeCount = activities.filter(a => a.status === 'running').length;
  const pendingCount = activities.filter(a => a.status === 'pending').length;
  const completedTodayCount = activities.filter(a => a.status === 'complete').length;

  return (
    <div className="min-h-screen bg-[#020202] text-white">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-gradient-to-br from-purple-500/20 to-cyan-500/20">
              <Zap className="w-6 h-6 text-purple-400" />
            </div>
            <div>
              <h1 className="text-3xl font-bold">Command Center</h1>
              <p className="text-sm text-slate-400">Your AI team working in real-time</p>
            </div>
          </div>

          {/* Admin Badge */}
          {user?.is_superuser && (
            <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/20 rounded-full">
              <Shield className="w-4 h-4 text-emerald-400" />
              <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">
                System Verified v2.0
              </span>
            </div>
          )}
        </div>

        {/* Stats Bar */}
        <div className="flex gap-6 mt-6">
          <div className="flex items-center gap-2">
            <Loader className="w-4 h-4 text-blue-400 animate-spin" />
            <span className="text-sm text-slate-300">{activeCount} Active</span>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-slate-400" />
            <span className="text-sm text-slate-300">{pendingCount} Pending</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-emerald-400" />
            <span className="text-sm text-slate-300">{completedTodayCount} Completed Today</span>
          </div>
        </div>
      </div>



      {/* Show Zero State if no startups */}
      {hasStartups === false ? (
        <ZeroStateWidget
          pendingStrategy={pendingStrategy}
          onCreateStartup={() => navigate('/onboarding/genius')}
        />
      ) : (
        <>
          {/* Admin Specialized Agents */}
          {user?.is_superuser && (
            <div className="space-y-8">
              <AdminEcosystemWidget />
              <AdminAgentWidget />
            </div>
          )}

          {/* Empire Progress Widget */}
          <EmpireProgressWidget />

          {/* Morning Brief & AstroTurf Row */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <div className="lg:col-span-2">
              <MorningBriefWidget />
            </div>
            <div className="lg:col-span-1">
              <AstroTurfWidget />
            </div>
          </div>

          {/* Main Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Active Agents */}
            <div className="lg:col-span-2 space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
                  Active Agents
                </h2>
                <Button size="sm" variant="outline">
                  <Pause className="w-3 h-3 mr-1" />
                  Pause All
                </Button>
              </div>

              {loading ? (
                <div className="flex items-center justify-center py-12">
                  <Loader className="w-6 h-6 text-slate-400 animate-spin" />
                </div>
              ) : (
                <div className="space-y-3">
                  {activities
                    .filter(a => a.status === 'running')
                    .map(activity => (
                      <AgentCard key={activity.id} activity={activity} />
                    ))}
                </div>
              )}

              {/* Pending */}
              <div className="mt-8">
                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Clock className="w-4 h-4 text-slate-400" />
                  Pending Queue
                </h2>
                <div className="space-y-3">
                  {activities
                    .filter(a => a.status === 'pending')
                    .map(activity => (
                      <AgentCard key={activity.id} activity={activity} />
                    ))}
                </div>
              </div>

              {/* Completed */}
              <div className="mt-8">
                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-emerald-400" />
                  Completed Today
                </h2>
                <div className="space-y-3">
                  {activities
                    .filter(a => a.status === 'complete')
                    .map(activity => (
                      <AgentCard key={activity.id} activity={activity} />
                    ))}
                </div>
              </div>
            </div>

            {/* Sidebar: Quick Actions + Activity Feed */}
            <div className="space-y-6">
              {/* Quick Focus */}
              <div className="bg-slate-900/50 rounded-xl border border-white/5 p-4">
                <h3 className="font-medium mb-3">Quick Focus</h3>
                <input
                  type="text"
                  placeholder="What should AI focus on?"
                  className="w-full px-4 py-3 rounded-lg bg-slate-800/50 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-purple-500/50"
                />
                <Button className="w-full mt-3" variant="cyber">
                  <Play className="w-4 h-4 mr-2" />
                  Start Task
                </Button>
              </div>

              {/* Benchmark Widget Insights */}
              <BenchmarkWidget />

              {/* Live WebSocket Swarm Feed */}
              <LiveAgentDashboard />

              {/* Activity Feed */}
              <ActivityFeed />
            </div>
          </div>
        </>
      )}
    </div>
  );
}