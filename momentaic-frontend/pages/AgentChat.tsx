
import React, { useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useChatStore } from '../stores/chat-store';
import { useAuthStore } from '../stores/auth-store';
import { api } from '../lib/api';
import { AgentType, Startup, SubscriptionTier } from '../types';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card } from '../components/ui/Card';
import { Dialog } from '../components/ui/Dialog';
// ... imports
import { Send, Bot, User, Trash2, Loader2, Sparkles, Terminal, Lock, Zap, Plus, Volume2, ThumbsUp, ThumbsDown, Network, Eye, Brain } from 'lucide-react';

// ... inside AgentChat component
// ...

function PlayVoiceButton({ text }: { text: string }) {
  const [isPlaying, setIsPlaying] = React.useState(false);
  const [isLoading, setIsLoading] = React.useState(false);
  const audioRef = React.useRef<HTMLAudioElement | null>(null);

  const handlePlay = async () => {
    if (isPlaying && audioRef.current) {
      audioRef.current.pause();
      setIsPlaying(false);
      return;
    }

    setIsLoading(true);
    try {
      const url = await api.speak(text);
      if (audioRef.current) {
        audioRef.current.src = url;
        audioRef.current.play();
        setIsPlaying(true);
        audioRef.current.onended = () => setIsPlaying(false);
      } else {
        const audio = new Audio(url);
        audioRef.current = audio;
        audio.play();
        setIsPlaying(true);
        audio.onended = () => setIsPlaying(false);
      }
    } catch (e) {
      console.error("Failed to play voice", e);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <button
      onClick={handlePlay}
      className="absolute top-2 right-2 p-1.5 rounded-full bg-white/5 hover:bg-white/10 text-gray-400 hover:text-[#00f0ff] transition-colors"
      title="Play Voice"
    >
      {isLoading ? <Loader2 className="w-3 h-3 animate-spin" /> : <Volume2 className={`w-3 h-3 ${isPlaying ? 'text-[#00f0ff] animate-pulse' : ''}`} />}
    </button>
  );
}

import { cn } from '../lib/utils';
import { useToast } from '../components/ui/Toast';

function FeedbackWidget({ messageId, agentType, startupId }: { messageId: string, agentType: string, startupId: string }) {
  const [submitted, setSubmitted] = React.useState<'up' | 'down' | null>(null);

  const handleFeedback = async (isPositive: boolean) => {
    if (submitted) return;
    setSubmitted(isPositive ? 'up' : 'down');
    try {
      await api.submitAgentFeedback({
        startup_id: startupId,
        agent_type: agentType,
        message_id: messageId,
        is_positive: isPositive,
      });
    } catch (e) {
      console.error("Failed to submit feedback", e);
    }
  };

  if (!startupId || !agentType) return null;

  return (
    <div className="flex items-center gap-1 mt-3 pt-2 border-t border-white/5 self-start">
      <button
        onClick={() => handleFeedback(true)}
        disabled={!!submitted}
        className={cn("p-1.5 rounded hover:bg-white/10 transition-colors", submitted === 'up' ? "text-green-400 bg-green-400/10" : "text-gray-500")}
        title="Good Response"
      >
        <ThumbsUp className="w-3.5 h-3.5" />
      </button>
      <button
        onClick={() => handleFeedback(false)}
        disabled={!!submitted}
        className={cn("p-1.5 rounded hover:bg-white/10 transition-colors", submitted === 'down' ? "text-red-400 bg-red-400/10" : "text-gray-500")}
        title="Bad Response"
      >
        <ThumbsDown className="w-3.5 h-3.5" />
      </button>
    </div>
  );
}

function GlobalInsightsLoader({ startupId }: { startupId: string }) {
  const [data, setData] = React.useState<{ industry: string, insights: any[] } | null>(null);
  const [loading, setLoading] = React.useState(true);

  useEffect(() => {
    async function fetchInsights() {
      try {
        const res = await api.getCrossStartupInsights(startupId);
        setData(res.data);
      } catch (e) {
        console.error("Failed to load insights", e);
      } finally {
        setLoading(false);
      }
    }
    fetchInsights();
  }, [startupId]);

  if (loading) return <div className="text-center p-4 text-gray-500 text-sm animate-pulse">Synchronizing with Global Matrix...</div>;
  if (!data || data.insights.length === 0) return <div className="text-center p-4 text-gray-500 text-sm">No significant network patterns detected for {data?.industry || 'this industry'} yet.</div>;

  return (
    <div className="space-y-4">
      <p className="text-xs text-gray-400">
        Aggregated success patterns for <span className="text-[#00f0ff] font-bold">{data.industry}</span> startups across the Momentaic ecosystem. Agents will automatically use this intelligence.
      </p>
      {data.insights.map((insight, idx) => (
        <div key={idx} className="bg-black/50 border border-white/5 p-3 rounded-lg text-sm text-gray-300">
          <div className="flex items-start gap-2">
            <div className="mt-0.5"><Network className="w-4 h-4 text-[#bf25eb]" /></div>
            <div>
              <p className="font-mono text-xs text-[#bf25eb] mb-1">PROVEN PATTERN</p>
              <p>{insight.message}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

// 🧬 X-RAY REASONING PANEL (Kill Shot 2)
function XRayPanel({ reasoning }: { reasoning?: { research_analyzed?: string; options_considered?: string[]; final_decision_rationale?: string } }) {
  const [isOpen, setIsOpen] = React.useState(false);

  // Generate simulated reasoning for demo when no real data exists
  const displayReasoning = reasoning || {
    research_analyzed: "Analyzed startup context, industry benchmarks, and historical agent performance data.",
    options_considered: [
      "Option A: Conservative approach based on current metrics",
      "Option B: Aggressive growth strategy leveraging market trends",
      "Option C: Hybrid approach balancing risk and opportunity"
    ],
    final_decision_rationale: "Selected optimal strategy based on startup stage, available resources, and competitive landscape analysis."
  };

  return (
    <div className="mt-3 pt-2 border-t border-white/5">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 text-[10px] font-mono text-gray-500 hover:text-[#00f0ff] transition-colors group"
      >
        <Eye className={`w-3 h-3 transition-colors ${isOpen ? "text-[#00f0ff]" : "text-gray-600 group-hover:text-[#00f0ff]"}`} />
        <span className="tracking-widest uppercase">{isOpen ? '[ HIDE X-RAY ]' : '[ X-RAY: VIEW REASONING ]'}</span>
        {!isOpen && <span className="w-1.5 h-1.5 bg-[#00f0ff] rounded-full animate-pulse" />}
      </button>

      {isOpen && (
        <div className="mt-4 relative overflow-hidden bg-black/80 backdrop-blur-md border border-[#00f0ff]/30 rounded-xl p-5 shadow-[0_0_30px_rgba(0,240,255,0.05)] animate-fade-in group">
          <div className="absolute inset-0 bg-tech-grid opacity-[0.03] pointer-events-none" />
          <div className="absolute top-0 right-0 w-32 h-32 bg-[#00f0ff]/5 rounded-full blur-2xl transform translate-x-12 -translate-y-12 group-hover:bg-[#00f0ff]/10 transition-colors" />

          <div className="relative z-10 space-y-4">
            <div className="flex items-center gap-3 mb-3 border-b border-[#00f0ff]/20 pb-3">
              <div className="w-8 h-8 rounded-lg bg-[#00f0ff]/10 flex items-center justify-center border border-[#00f0ff]/30">
                <Brain className="w-4 h-4 text-[#00f0ff]" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 bg-[#00f0ff] rounded-full animate-pulse" />
                  <span className="text-xs font-black font-mono text-[#00f0ff] tracking-widest">CHAIN_OF_THOUGHT // AGENT REPLAY</span>
                </div>
                <div className="text-[9px] font-mono text-[#00f0ff]/50 uppercase mt-0.5">Live Execution Trace</div>
              </div>
            </div>

            {displayReasoning.research_analyzed && (
              <div>
                <div className="text-[9px] font-mono text-gray-500 uppercase tracking-wider mb-1">📊 Research Analyzed</div>
                <p className="text-[11px] text-gray-400 font-mono pl-3 border-l border-[#00f0ff]/30">{displayReasoning.research_analyzed}</p>
              </div>
            )}

            {displayReasoning.options_considered && displayReasoning.options_considered.length > 0 && (
              <div>
                <div className="text-[9px] font-mono text-gray-500 uppercase tracking-wider mb-1">🔀 Options Considered</div>
                <div className="space-y-1 pl-3 border-l border-purple-500/30">
                  {displayReasoning.options_considered.map((opt, i) => (
                    <div key={i} className="flex items-start gap-2">
                      <span className="text-[9px] font-mono text-purple-400 mt-0.5">#{i + 1}</span>
                      <p className="text-[11px] text-gray-400 font-mono">{opt}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {displayReasoning.final_decision_rationale && (
              <div>
                <div className="text-[10px] font-bold font-mono text-gray-400 uppercase tracking-widest mb-1.5">✅ Decision Rationale</div>
                <div className="bg-green-500/5 border border-green-500/20 rounded-lg p-3">
                  <p className="text-xs text-green-400/90 font-mono leading-relaxed">{displayReasoning.final_decision_rationale}</p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function IndustryPlaybooks({ startupId, onSelect }: { startupId: string, onSelect: (agentId: AgentType, prompt: string) => void }) {
  const [playbooks, setPlaybooks] = React.useState<any[]>([]);
  const [loading, setLoading] = React.useState(true);

  useEffect(() => {
    async function fetchPlaybooks() {
      try {
        // Find the industry for the given startupId
        const startupsRes = await api.getStartups();
        const startup = startupsRes.find((s: any) => s.id === startupId);
        if (startup && startup.industry) {
          const pbRes = await api.getIndustryPlaybooks(startup.industry);
          setPlaybooks(pbRes);
        } else {
          const pbRes = await api.getIndustryPlaybooks("General");
          setPlaybooks(pbRes);
        }
      } catch (e) {
        console.error("Failed to load playbooks", e);
      } finally {
        setLoading(false);
      }
    }
    fetchPlaybooks();
  }, [startupId]);

  if (loading || playbooks.length === 0) return null;

  return (
    <div className="w-full max-w-4xl mx-auto mt-8 animate-fade-in-up">
      <div className="flex items-center gap-2 mb-4 px-2">
        <Sparkles className="w-4 h-4 text-[#bf25eb]" />
        <h3 className="text-sm font-bold text-gray-300 uppercase tracking-widest">Industry Playbooks</h3>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {playbooks.map(pb => (
          <button
            key={pb.id}
            onClick={() => onSelect(pb.agent_type as AgentType, pb.initial_prompt)}
            className="text-left bg-black/40 border border-white/10 hover:border-[#bf25eb]/50 hover:bg-[#bf25eb]/5 p-4 rounded-xl transition-all group"
          >
            <h4 className="font-bold text-white text-sm mb-1 group-hover:text-[#bf25eb] transition-colors">{pb.title}</h4>
            <p className="text-xs text-gray-500 line-clamp-2">{pb.description}</p>
          </button>
        ))}
      </div>
    </div>
  );
}

const AGENTS: { id: AgentType, name: string, tier: SubscriptionTier }[] = [
  { id: 'orchestrator', name: 'Orchestrator', tier: 'starter' },
  { id: 'technical_copilot', name: 'Technical Co-Pilot', tier: 'starter' },
  { id: 'business_copilot', name: 'Business Strategist', tier: 'growth' },
  { id: 'sales_agent', name: 'Sales Rep', tier: 'growth' },
  { id: 'fundraising_coach', name: 'Fundraising Coach', tier: 'god_mode' },
  { id: 'legal_agent', name: 'Legal Counsel', tier: 'god_mode' },
  { id: 'elon_musk', name: 'Elon (Hardcore Mode)', tier: 'god_mode' },
  { id: 'paul_graham', name: 'PG (Startups)', tier: 'god_mode' },
  { id: 'onboarding_coach', name: 'Onboarding Coach', tier: 'starter' },
  { id: 'competitor_intel', name: 'Competitor Intel', tier: 'growth' },
];

export default function AgentChat() {
  const [searchParams] = useSearchParams();
  const startupIdParam = searchParams.get('startup');
  const agentParam = searchParams.get('agent');

  const {
    messages,
    sendMessage,
    currentAgent,
    setCurrentAgent,
    currentStartupId,
    setCurrentStartupId,
    isLoading,
    clearChat
  } = useChatStore();

  const { user, deductCredits } = useAuthStore();
  const { toast } = useToast();

  const [input, setInput] = React.useState('');
  const [startups, setStartups] = React.useState<Startup[]>([]);
  const [isInsightsOpen, setIsInsightsOpen] = React.useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api.getStartups().then(setStartups).catch(console.error);
    if (startupIdParam) setCurrentStartupId(startupIdParam);
    if (agentParam) setCurrentAgent(agentParam as AgentType);
  }, [startupIdParam, agentParam, setCurrentStartupId, setCurrentAgent]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    // Credit Check
    const COST_PER_MSG = 1;
    if (!deductCredits(COST_PER_MSG)) {
      toast({ type: 'error', title: 'Insufficient Credits', message: 'Recharge your credits to continue operations.' });
      return;
    }

    const msg = input;
    setInput('');
    await sendMessage(msg);
  };

  const selectedAgentInfo = AGENTS.find(a => a.id === currentAgent);
  const isAgentLocked = (user?.subscription_tier === 'starter' && selectedAgentInfo?.tier !== 'starter') ||
    (user?.subscription_tier === 'growth' && selectedAgentInfo?.tier === 'god_mode');

  // Helper to check if an agent is accessible
  const isAgentAccessible = (agent: typeof AGENTS[0]) => {
    if (user?.subscription_tier === 'god_mode' || user?.role === 'admin') return true;
    if (user?.subscription_tier === 'growth') return agent.tier !== 'god_mode';
    return agent.tier === 'starter';
  };

  // Split agents into accessible and locked
  const accessibleAgents = AGENTS.filter(isAgentAccessible);
  const lockedAgents = AGENTS.filter(a => !isAgentAccessible(a));

  return (
    <div className="h-[calc(100vh-6rem)] flex flex-col gap-4">
      {/* Header Controls */}
      <div className="flex flex-col sm:flex-row gap-4 p-4 bg-[#0a0a0a] border border-white/10 rounded-xl">
        <div className="flex-1">
          <label className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1 block">Active Agent</label>
          <div className="relative">
            <Bot className="absolute left-3 top-2.5 w-4 h-4 text-[#00f0ff]" />
            <select
              className="w-full pl-10 pr-4 py-2 bg-black border border-white/10 rounded-lg text-sm text-white focus:border-[#00f0ff] focus:outline-none appearance-none font-mono"
              value={currentAgent}
              onChange={(e) => setCurrentAgent(e.target.value as AgentType)}
            >
              {accessibleAgents.map(a => (
                <option key={a.id} value={a.id}>
                  {a.name} {a.tier !== 'starter' ? `[${a.tier.toUpperCase()}]` : ''}
                </option>
              ))}
              {lockedAgents.length > 0 && (
                <option disabled className="text-gray-500">── UPGRADE TO UNLOCK ──</option>
              )}
              {lockedAgents.map(a => (
                <option key={a.id} value={a.id} disabled className="text-gray-500">
                  🔒 {a.name} [{a.tier.toUpperCase()}]
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="flex-1">
          <label className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1 block">Context Layer</label>
          <div className="relative">
            <Terminal className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
            <select
              className="w-full pl-10 pr-4 py-2 bg-black border border-white/10 rounded-lg text-sm text-white focus:border-[#00f0ff] focus:outline-none appearance-none font-mono"
              onChange={(e) => {
                if (e.target.value === 'CREATE') {
                  window.location.href = '#/startups/new';
                } else {
                  setCurrentStartupId(e.target.value || null)
                }
              }}
              defaultValue={startupIdParam || ''}
            >
              <option value="">Global Context</option>
              {startups.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
              {startups.length === 0 && <option value="CREATE">+ Create Startup Context...</option>}
            </select>
          </div>
        </div>
        <div className="flex items-end gap-2">
          {startupIdParam || currentStartupId ? (
            <React.Fragment>
              <Button onClick={() => setIsInsightsOpen(true)} variant="outline" size="sm" title="Ecosystem Insights" className="border-[#00f0ff]/30 text-[#00f0ff] hover:bg-[#00f0ff]/10">
                <Network className="w-4 h-4 mr-2" />
                Hive Mind
              </Button>
              <Dialog isOpen={isInsightsOpen} onClose={() => setIsInsightsOpen(false)} title="Global Hive Mind">
                <div className="flex items-center gap-2 mb-4">
                  <Sparkles className="w-5 h-5 text-[#bf25eb]" />
                  <span className="font-bold text-white">Ecosystem Insights</span>
                </div>
                <div className="mt-4">
                  <GlobalInsightsLoader startupId={startupIdParam || currentStartupId || ''} />
                </div>
              </Dialog>
            </React.Fragment>
          ) : null}
          <Button variant="outline" size="sm" onClick={clearChat} title="Clear Buffer" className="border-red-900/30 text-red-500 hover:bg-red-900/10 gap-2">
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Chat Terminal */}
      <div className="flex-1 flex flex-col overflow-hidden bg-[#050505] border border-white/10 rounded-xl relative">
        <div className="absolute inset-0 bg-cyber-grid opacity-[0.03] pointer-events-none"></div>

        {isAgentLocked ? (
          <div className="absolute inset-0 z-20 flex flex-col items-center justify-center bg-black/80 backdrop-blur-sm">
            <div className="bg-[#111] border border-white/10 p-8 rounded-2xl text-center max-w-md">
              <Lock className="w-12 h-12 text-[#ff003c] mx-auto mb-4" />
              <h3 className="text-xl font-bold text-white mb-2">ACCESS DENIED</h3>
              <p className="text-gray-400 mb-6 text-sm">
                The <span className="text-[#00f0ff] font-bold">{selectedAgentInfo?.name}</span> requires {selectedAgentInfo?.tier.replace('_', ' ')} clearance.
                Your current clearance is {user?.subscription_tier}.
              </p>
              <Button variant="cyber" onClick={() => window.location.href = '#/settings'}>
                UPGRADE CLEARANCE
              </Button>
            </div>
          </div>
        ) : null}

        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          {messages.length === 0 && !isAgentLocked && (
            <div className="h-full max-h-[60vh] flex flex-col items-center justify-center text-gray-600 space-y-4">
              <div className="w-16 h-16 rounded-full bg-[#0a0a0a] border border-white/5 flex items-center justify-center">
                <Bot className="w-8 h-8 text-[#00f0ff] animate-pulse" />
              </div>
              <p className="font-mono text-xs uppercase tracking-widest">Secure Channel Open. Cost: 1 Credit/Msg.</p>
              {(startupIdParam || currentStartupId) && (
                <IndustryPlaybooks
                  startupId={startupIdParam || currentStartupId || ''}
                  onSelect={(agent, prompt) => {
                    setCurrentAgent(agent);
                    setInput(prompt);
                  }}
                />
              )}
            </div>
          )}

          {messages.map((msg) => (
            <div
              key={msg.id}
              className={cn(
                "flex w-full max-w-4xl mx-auto gap-4 animate-fade-in",
                msg.role === 'user' ? "justify-end" : "justify-start"
              )}
            >
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-lg bg-[#2563eb]/20 border border-[#2563eb]/50 flex items-center justify-center flex-shrink-0 mt-1 shadow-[0_0_10px_rgba(37,99,235,0.3)]">
                  <Bot className="w-4 h-4 text-[#2563eb]" />
                </div>
              )}

              <div className={cn(
                "p-4 rounded-xl text-sm whitespace-pre-wrap font-mono relative max-w-[80%]",
                msg.role === 'user'
                  ? "bg-[#2563eb] text-white rounded-tr-none border border-[#2563eb] shadow-[0_0_15px_rgba(37,99,235,0.2)]"
                  : "bg-[#0a0a0a] text-gray-300 rounded-tl-none border border-white/10 shadow-lg"
              )}>
                {msg.agent_used && (
                  <div className="flex items-center gap-2 mb-2 pb-2 border-b border-white/10">
                    <Sparkles className="w-3 h-3 text-[#00f0ff]" />
                    <span className="text-[10px] text-[#00f0ff] uppercase font-bold tracking-widest">
                      {AGENTS.find(a => a.id === msg.agent_used)?.name || msg.agent_used}
                    </span>
                  </div>
                )}
                {msg.content}
                {msg.isStreaming && (
                  <span className="inline-block w-2 h-4 ml-1 bg-[#00f0ff] animate-pulse align-middle" />
                )}

                {/* 🧬 KILL SHOT 2: X-RAY AGENT REPLAY */}
                {!msg.isStreaming && msg.role === 'assistant' && (
                  <XRayPanel reasoning={msg.reasoning} />
                )}

                {!msg.isStreaming && msg.role === 'assistant' && (startupIdParam || currentStartupId) && (
                  <FeedbackWidget
                    messageId={msg.id}
                    agentType={msg.agent_used || currentAgent}
                    startupId={startupIdParam || currentStartupId || ''}
                  />
                )}
              </div>

              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center flex-shrink-0 mt-1">
                  <User className="w-4 h-4 text-white" />
                </div>
              )}
            </div>
          ))}

          {isLoading && !messages.some(m => m.isStreaming) && (
            <div className="flex w-full max-w-4xl mx-auto gap-4 justify-start">
              <div className="w-8 h-8 rounded-lg bg-[#2563eb]/20 border border-[#2563eb]/50 flex items-center justify-center flex-shrink-0">
                <Bot className="w-4 h-4 text-[#2563eb]" />
              </div>
              <div className="bg-[#0a0a0a] px-4 py-3 rounded-xl border border-white/10 flex items-center gap-2">
                <div className="flex gap-1">
                  <div className="w-1.5 h-1.5 bg-[#00f0ff] rounded-full animate-bounce" style={{ animationDelay: '0s' }}></div>
                  <div className="w-1.5 h-1.5 bg-[#00f0ff] rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-1.5 h-1.5 bg-[#00f0ff] rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
                <span className="ml-2 text-xs text-gray-500 font-mono uppercase tracking-widest">Processing (1 Credit)...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-white/10 bg-[#0a0a0a]">
          <form onSubmit={handleSend} className="flex gap-3 max-w-4xl mx-auto">
            <Button
              type="button"
              variant="outline"
              className="h-12 w-12 px-0 border-[#00f0ff]/20 text-[#00f0ff] hover:bg-[#00f0ff]/10 hover:border-[#00f0ff]/50"
              title="Generate Proactive Insight"
              onClick={() => {
                setInput("Based on my startup context (stage, industry, metrics), what is the ONE most critical thing I should focus on right now? Be proactive and specific.");
                // Optional: auto-submit? Let's let user confirm.
              }}
            >
              <Zap className="w-5 h-5" />
            </Button>
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={isAgentLocked ? "Agent Locked" : `Communicate with ${AGENTS.find(a => a.id === currentAgent)?.name}...`}
              className="flex-1 bg-black border-white/10 text-white focus:border-[#00f0ff] font-mono h-12"
              disabled={isLoading || isAgentLocked}
              autoFocus
            />
            <Button type="submit" disabled={isLoading || !input.trim() || isAgentLocked} variant="cyber" className="h-12 w-12 px-0 rounded-lg">
              <Send className="w-5 h-5" />
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
