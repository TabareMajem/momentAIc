
import React, { useState, useEffect, useRef } from 'react';
import { useWorkflowStore } from '../stores/workflow-store';
import { useAuthStore } from '../stores/auth-store';
import { analyzeTaskAndGenerateGraph } from '../lib/agent-forge';
import { WorkflowNode, WorkflowEdge } from '../types';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Play, Square, Save, RotateCcw, Box, Eye, Terminal as TerminalIcon, Cpu, Globe, MessageSquare, AlertTriangle, Zap, CheckCircle2, Network, Trash2 } from 'lucide-react';
import { cn } from '../lib/utils';
import { useToast } from '../components/ui/Toast';

// --- VISUAL GRAPH ENGINE COMPONENTS ---

const NODE_WIDTH = 220;
const NODE_HEIGHT = 100;

interface GraphNodeProps {
  node: WorkflowNode;
  selected: boolean;
  onClick: () => void;
}

const GraphNode: React.FC<GraphNodeProps> = ({ node, selected, onClick }) => {
  const getIcon = () => {
    switch (node.type) {
      case 'start': return <Play className="w-5 h-5 text-green-400" />;
      case 'end': return <Square className="w-5 h-5 text-red-400" />;
      case 'browser': return <Globe className="w-5 h-5 text-blue-400" />;
      case 'supervisor': return <Cpu className="w-5 h-5 text-purple-400" />;
      case 'mcp': return <Box className="w-5 h-5 text-orange-400" />;
      case 'human': return <AlertTriangle className="w-5 h-5 text-yellow-400" />;
      default: return <Zap className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = () => {
    if (node.data.status === 'running') return 'border-[#00f0ff] shadow-[0_0_20px_rgba(0,240,255,0.4)]';
    if (node.data.status === 'completed') return 'border-green-500 shadow-[0_0_10px_rgba(16,185,129,0.2)]';
    if (node.data.status === 'failed') return 'border-red-500';
    if (selected) return 'border-white';
    return 'border-white/10 hover:border-white/30';
  };

  return (
    <div
      className={cn(
        "absolute flex flex-col p-4 rounded-xl bg-[#0a0a0a]/90 backdrop-blur-md border transition-all duration-300 cursor-pointer group",
        getStatusColor()
      )}
      style={{
        left: node.position.x,
        top: node.position.y,
        width: NODE_WIDTH,
        height: NODE_HEIGHT
      }}
      onClick={onClick}
    >
      <div className="flex items-center gap-3 mb-2">
        <div className="p-2 rounded-lg bg-white/5 border border-white/5 group-hover:bg-white/10 transition-colors">
          {getIcon()}
        </div>
        <div className="overflow-hidden">
          <div className="font-mono text-xs font-bold text-white truncate">{node.data.label}</div>
          <div className="text-[10px] text-gray-500 uppercase truncate">{node.type}</div>
        </div>
      </div>
      <div className="text-[10px] text-gray-400 line-clamp-2 leading-tight">
        {node.data.description}
      </div>

      {/* Connector Dots */}
      <div className="absolute top-1/2 -left-1.5 w-3 h-3 bg-[#111] border border-gray-600 rounded-full"></div>
      <div className="absolute top-1/2 -right-1.5 w-3 h-3 bg-[#111] border border-gray-600 rounded-full"></div>

      {node.data.status === 'running' && (
        <div className="absolute inset-0 border border-[#00f0ff] rounded-xl animate-pulse"></div>
      )}
    </div>
  );
};

const EdgesLayer: React.FC<{ nodes: WorkflowNode[], edges: WorkflowEdge[] }> = ({ nodes, edges }) => {
  return (
    <svg className="absolute inset-0 pointer-events-none w-full h-full overflow-visible">
      <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
          <polygon points="0 0, 10 3.5, 0 7" fill="#4b5563" />
        </marker>
        <marker id="arrowhead-active" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
          <polygon points="0 0, 10 3.5, 0 7" fill="#00f0ff" />
        </marker>
      </defs>
      {edges.map(edge => {
        const source = nodes.find(n => n.id === edge.source);
        const target = nodes.find(n => n.id === edge.target);
        if (!source || !target) return null;

        const x1 = source.position.x + NODE_WIDTH;
        const y1 = source.position.y + NODE_HEIGHT / 2;
        const x2 = target.position.x;
        const y2 = target.position.y + NODE_HEIGHT / 2;

        const controlPointOffset = Math.abs(x2 - x1) / 2;
        const pathData = `M ${x1} ${y1} C ${x1 + controlPointOffset} ${y1}, ${x2 - controlPointOffset} ${y2}, ${x2} ${y2}`;

        return (
          <g key={edge.id}>
            <path
              d={pathData}
              stroke="#374151"
              strokeWidth="2"
              fill="none"
              markerEnd="url(#arrowhead)"
            />
            {edge.animated && (
              <path
                d={pathData}
                stroke="#00f0ff"
                strokeWidth="2"
                fill="none"
                strokeDasharray="10,10"
                className="animate-dash-draw opacity-60"
                markerEnd="url(#arrowhead-active)"
              />
            )}
          </g>
        );
      })}
    </svg>
  );
};

const FORGE_COST = 10;

export default function AgentForge() {
  const {
    nodes, edges, logs, isRunning, selectedNodeId,
    setNodes, setEdges, selectNode, addLog, setRunning, updateNodeStatus, clearLogs, resetWorkflow, removeNode
  } = useWorkflowStore();

  const { deductCredits, user } = useAuthStore();
  const { toast } = useToast();

  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll logs
  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [logs]);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    // Credit Logic
    if (!deductCredits(FORGE_COST)) {
      toast({ type: 'error', title: 'Insufficient Credits', message: `Blueprint generation requires ${FORGE_COST} credits.` });
      return;
    }

    setIsGenerating(true);
    resetWorkflow();
    addLog('system', `Analyzing request: "${prompt}"...`);
    addLog('info', `Credits deducted: ${FORGE_COST}. Remaining: ${user?.credits}`);

    try {
      const graph = await analyzeTaskAndGenerateGraph(prompt);
      setNodes(graph.nodes);
      setEdges(graph.edges);
      addLog('success', `Blueprint generated: ${graph.nodes.length} agents deployed.`);
    } catch (error) {
      addLog('error', 'Failed to generate workflow architecture.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleRunSimulation = async () => {
    if (nodes.length === 0) return;
    setRunning(true);
    addLog('system', 'Initializing workflow execution...');

    // Sequential simulation of nodes
    for (const node of nodes) {
      updateNodeStatus(node.id, 'running');
      selectNode(node.id);

      let delay = 1000;
      if (node.type === 'browser') delay = 2000;
      if (node.type === 'supervisor') delay = 2500;

      addLog('info', `Executing ${node.data.label}...`, node.id);
      await new Promise(r => setTimeout(r, delay));

      updateNodeStatus(node.id, 'completed');
      addLog('success', `Task completed: ${node.data.label}`, node.id);
    }

    addLog('system', 'Workflow execution finished successfully.');
    setRunning(false);
    selectNode(null);
  };

  const selectedNode = nodes.find(n => n.id === selectedNodeId);

  return (
    <div className="h-[calc(100vh-6rem)] flex flex-col gap-4 overflow-hidden">
      {/* AgentForge.ai Platform Access Banner */}
      <div className="bg-gradient-to-r from-purple-900/30 via-blue-900/30 to-cyan-900/30 border border-white/10 rounded-xl p-6 relative overflow-hidden">
        {/* Background decoration */}
        <div className="absolute inset-0 bg-cyber-grid bg-[length:30px_30px] opacity-5 pointer-events-none"></div>
        <div className="absolute -top-10 -right-10 w-40 h-40 bg-purple-500/10 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-10 -left-10 w-40 h-40 bg-cyan-500/10 rounded-full blur-3xl"></div>

        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 bg-gradient-to-br from-purple-500 to-cyan-500 rounded-lg">
                <Network className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-black text-white tracking-tight font-mono">
                  AGENTFORGE<span className="text-cyan-400">.AI</span>
                </h2>
                <p className="text-xs text-gray-400 font-mono">ENTERPRISE AI AGENT PLATFORM</p>
              </div>
              {(user?.subscription_tier === 'god_mode' || user?.subscription_tier === 'growth') && (
                <Badge variant="secondary" className="bg-gradient-to-r from-purple-500/20 to-cyan-500/20 border-purple-500/30 text-cyan-400 ml-2">
                  PREMIUM ACCESS
                </Badge>
              )}
            </div>
            <p className="text-sm text-gray-300 max-w-2xl leading-relaxed">
              Access the full <span className="text-white font-bold">AgentForge.ai</span> platform with your MomentAIc {user?.subscription_tier === 'god_mode' ? 'GOD_MODE' : user?.subscription_tier === 'growth' ? 'GROWTH' : 'premium'} subscription.
              Build, deploy, and orchestrate advanced AI agents with enterprise-grade infrastructure.
            </p>

            {/* Feature pills */}
            <div className="flex flex-wrap gap-2 mt-4">
              {['Advanced Templates', 'Multi-Agent Orchestration', 'Priority Compute', 'API Access', 'Enterprise Support'].map((feature, i) => (
                <span key={i} className="px-2 py-1 bg-white/5 border border-white/10 rounded text-[10px] font-mono text-gray-400">
                  {feature}
                </span>
              ))}
            </div>
          </div>

          <div className="flex flex-col gap-2 items-center">
            {(user?.subscription_tier === 'god_mode' || user?.subscription_tier === 'growth') ? (
              <Button
                variant="cyber"
                size="lg"
                className="bg-gradient-to-r from-purple-600 to-cyan-500 hover:from-purple-500 hover:to-cyan-400 border-0 text-white shadow-[0_0_30px_rgba(139,92,246,0.4)] min-w-[200px]"
                onClick={() => window.open('https://agentforgeai.com/sso?source=momentaic&tier=' + user?.subscription_tier, '_blank')}
              >
                <Globe className="w-5 h-5 mr-2" />
                Launch AgentForge.ai
              </Button>
            ) : (
              <Button
                variant="outline"
                size="lg"
                className="border-purple-500/50 text-purple-400 hover:bg-purple-500/10 min-w-[200px]"
                onClick={() => toast({ type: 'info', title: 'Upgrade Required', message: 'Upgrade to GROWTH or GOD_MODE to unlock AgentForge.ai premium access.' })}
              >
                <Zap className="w-5 h-5 mr-2" />
                Upgrade to Unlock
              </Button>
            )}
            <span className="text-[10px] text-gray-500 font-mono">
              {user?.subscription_tier === 'god_mode' ? 'ENTERPRISE ACCESS' :
                user?.subscription_tier === 'growth' ? 'PRO ACCESS' :
                  'STARTER TIER'}
            </span>
          </div>
        </div>
      </div>

      {/* Original Toolbar - Workflow Studio */}
      <div className="flex flex-col md:flex-row gap-4 justify-between items-start md:items-center bg-[#0a0a0a] border border-white/10 p-4 rounded-xl">
        <div>
          <h1 className="text-xl font-bold font-mono text-white flex items-center gap-2">
            <Network className="text-[#00f0ff]" /> AGENT_FORGE <span className="text-xs text-gray-500 bg-white/5 px-2 py-0.5 rounded ml-2">STUDIO V1.0</span>
          </h1>
          <p className="text-xs text-gray-500 font-mono mt-1">Build & simulate AI agent workflows locally</p>
        </div>
        <div className="flex gap-2 w-full md:w-auto">
          <Button variant="outline" size="sm" onClick={resetWorkflow} disabled={isRunning}><RotateCcw className="w-4 h-4 mr-2" /> Reset</Button>
          <Button variant="cyber" size="sm" onClick={handleRunSimulation} disabled={isRunning || nodes.length === 0}>
            {isRunning ? 'EXECUTING...' : 'RUN SIMULATION'}
            {!isRunning && <Play className="w-4 h-4 ml-2 fill-current" />}
          </Button>
        </div>
      </div>


      <div className="flex-1 flex gap-4 overflow-hidden relative">
        {/* Main Canvas Area */}
        <div className="flex-1 flex flex-col gap-4 min-w-0">
          {/* AI Input */}
          <div className="bg-[#0a0a0a] border border-white/10 p-1 rounded-xl flex gap-2">
            <form onSubmit={handleGenerate} className="flex-1 flex gap-2">
              <Input
                value={prompt}
                onChange={e => setPrompt(e.target.value)}
                placeholder={`Describe a workflow (Cost: ${FORGE_COST} Credits)...`}
                className="bg-transparent border-none text-white focus:ring-0 placeholder:text-gray-600 font-mono"
                disabled={isRunning || isGenerating}
              />
              <Button type="submit" variant="ghost" disabled={isRunning || isGenerating} className="text-[#00f0ff] hover:bg-[#00f0ff]/10">
                {isGenerating ? <Zap className="w-4 h-4 animate-pulse" /> : <MessageSquare className="w-4 h-4" />}
              </Button>
            </form>
          </div>

          {/* Graph Canvas */}
          <div className="flex-1 bg-[#050505] rounded-xl border border-white/10 relative overflow-hidden shadow-inner group">
            {/* Grid Background */}
            <div className="absolute inset-0 bg-cyber-grid bg-[length:40px_40px] opacity-10 pointer-events-none"></div>

            <div className="w-full h-full overflow-auto relative p-10 min-w-[1000px] min-h-[600px]">
              <EdgesLayer nodes={nodes} edges={edges} />
              {nodes.map(node => (
                <GraphNode
                  key={node.id}
                  node={node}
                  selected={selectedNodeId === node.id}
                  onClick={() => selectNode(node.id)}
                />
              ))}

              {nodes.length === 0 && !isGenerating && (
                <div className="absolute inset-0 flex items-center justify-center text-gray-600 font-mono text-sm pointer-events-none">
                  WAITING_FOR_INPUT...
                </div>
              )}
              {isGenerating && (
                <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/50 backdrop-blur-sm z-10">
                  <div className="w-12 h-12 border-4 border-[#00f0ff] border-t-transparent rounded-full animate-spin mb-4"></div>
                  <div className="font-mono text-[#00f0ff] animate-pulse">GENERATING_BLUEPRINT...</div>
                </div>
              )}
            </div>
          </div>

          {/* Terminal Log */}
          <div className="h-48 bg-[#020202] border border-white/10 rounded-xl p-4 font-mono text-xs overflow-hidden flex flex-col">
            <div className="flex justify-between items-center mb-2 pb-2 border-b border-white/10">
              <div className="flex items-center gap-2 text-gray-400">
                <TerminalIcon className="w-4 h-4" /> TERMINAL_OUTPUT
              </div>
              <button onClick={clearLogs} className="text-gray-600 hover:text-white">CLEAR</button>
            </div>
            <div className="flex-1 overflow-y-auto space-y-1" ref={scrollRef}>
              {logs.map(log => (
                <div key={log.id} className="flex gap-3">
                  <span className="text-gray-600 shrink-0">[{log.timestamp}]</span>
                  <span className={cn(
                    "break-all",
                    log.level === 'error' ? 'text-red-500' :
                      log.level === 'success' ? 'text-green-500' :
                        log.level === 'system' ? 'text-[#00f0ff]' : 'text-gray-300'
                  )}>
                    {log.level === 'info' && <span className="text-blue-500 mr-2">ℹ</span>}
                    {log.message}
                  </span>
                </div>
              ))}
              {logs.length === 0 && <span className="text-gray-700 italic">System idle. Ready for execution.</span>}
            </div>
          </div>
        </div>

        {/* Inspector Panel (Right Sidebar) */}
        <div className="w-80 flex flex-col gap-4 bg-[#0a0a0a] border border-white/10 rounded-xl p-4 overflow-y-auto">
          <h2 className="font-bold text-white font-mono border-b border-white/10 pb-2 mb-2">INSPECTOR</h2>

          {selectedNode ? (
            <div className="space-y-6 animate-fade-in">
              <div>
                <label className="text-[10px] uppercase text-gray-500 font-bold">Node Type</label>
                <Badge variant="outline" className="mt-1">{selectedNode.type}</Badge>
              </div>
              <div>
                <label className="text-[10px] uppercase text-gray-500 font-bold">Label</label>
                <div className="text-white font-mono text-sm mt-1">{selectedNode.data.label}</div>
              </div>
              <div>
                <label className="text-[10px] uppercase text-gray-500 font-bold">Status</label>
                <div className={cn(
                  "mt-1 inline-flex items-center px-2 py-1 rounded text-xs font-bold uppercase",
                  selectedNode.data.status === 'completed' ? 'bg-green-500/10 text-green-500' :
                    selectedNode.data.status === 'running' ? 'bg-[#00f0ff]/10 text-[#00f0ff]' :
                      selectedNode.data.status === 'failed' ? 'bg-red-500/10 text-red-500' :
                        'bg-white/5 text-gray-400'
                )}>
                  {selectedNode.data.status}
                </div>
              </div>

              {selectedNode.data.systemInstruction && (
                <div>
                  <label className="text-[10px] uppercase text-gray-500 font-bold">System Prompt</label>
                  <div className="mt-1 p-2 bg-black/50 border border-white/10 rounded text-xs text-gray-300 font-mono h-24 overflow-y-auto">
                    {selectedNode.data.systemInstruction}
                  </div>
                </div>
              )}

              {selectedNode.data.config && (
                <div>
                  <label className="text-[10px] uppercase text-gray-500 font-bold">Configuration</label>
                  <pre className="mt-1 p-2 bg-black/50 border border-white/10 rounded text-[10px] text-green-400 font-mono overflow-x-auto">
                    {JSON.stringify(selectedNode.data.config, null, 2)}
                  </pre>
                </div>
              )}

              <div className="pt-4 border-t border-white/10">
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full text-red-400 hover:text-red-500 hover:border-red-500/50 hover:bg-red-500/10"
                  onClick={() => removeNode(selectedNode.id)}
                  disabled={isRunning}
                >
                  <Trash2 className="w-4 h-4 mr-2" /> Delete Node
                </Button>
              </div>
            </div>
          ) : (
            <div className="text-gray-500 text-sm text-center mt-10">
              Select a node to view details.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
